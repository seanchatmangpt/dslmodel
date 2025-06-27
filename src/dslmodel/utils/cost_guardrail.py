#!/usr/bin/env python3
"""
Cost Guardrail for DSPy Language Models
Tracks token usage and enforces budget limits
"""

import os
import csv
import json
import functools
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional
import warnings

from loguru import logger


class CostTracker:
    """Track LM costs and enforce budget limits"""
    
    def __init__(self, csv_path: Optional[Path] = None):
        self.csv_path = csv_path or Path.cwd() / "swarmsh_costs.csv"
        self.max_daily_cost = float(os.getenv('SWARMSH_MAX_COST_PER_DAY', '50.00'))
        self.warn_threshold = float(os.getenv('SWARMSH_TOKEN_BUDGET_WARN', '0.8'))
        
        # Token cost estimates (USD per 1K tokens)
        self.cost_per_1k_tokens = {
            'gpt-4o': 0.005,
            'gpt-4o-mini': 0.0015,
            'gpt-4-turbo': 0.01,
            'groq/llama-3.1-8b-instant': 0.0,  # Free tier
            'groq/llama-3.3-70b-versatile': 0.0,
            'ollama/qwen3': 0.0,  # Local
        }
        
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'date', 'model', 'prompt_tokens', 
                    'completion_tokens', 'total_tokens', 'estimated_cost_usd',
                    'operation', 'session_id'
                ])
    
    def log_usage(self, model: str, prompt_tokens: int, completion_tokens: int, 
                  operation: str = 'unknown', session_id: str = 'default') -> float:
        """Log token usage and return estimated cost"""
        total_tokens = prompt_tokens + completion_tokens
        
        # Estimate cost
        base_model = model.split('/')[-1] if '/' in model else model
        cost_rate = self.cost_per_1k_tokens.get(base_model, 0.002)  # Default fallback
        estimated_cost = (total_tokens / 1000) * cost_rate
        
        # Log to CSV
        timestamp = datetime.now().isoformat()
        today = date.today().isoformat()
        
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, today, model, prompt_tokens, completion_tokens,
                total_tokens, estimated_cost, operation, session_id
            ])
        
        # Check budget
        daily_cost = self._get_daily_cost(today)
        if daily_cost >= self.max_daily_cost:
            raise RuntimeError(
                f"Daily cost limit exceeded: ${daily_cost:.2f} >= ${self.max_daily_cost:.2f}"
            )
        elif daily_cost >= self.max_daily_cost * self.warn_threshold:
            warnings.warn(
                f"Approaching daily cost limit: ${daily_cost:.2f}/{self.max_daily_cost:.2f}"
            )
        
        logger.info(f"💰 Token usage: {total_tokens} tokens, ${estimated_cost:.4f}")
        return estimated_cost
    
    def _get_daily_cost(self, date_str: str) -> float:
        """Get total cost for a specific date"""
        total_cost = 0.0
        
        try:
            with open(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['date'] == date_str:
                        total_cost += float(row['estimated_cost_usd'])
        except FileNotFoundError:
            pass
        
        return total_cost
    
    def get_usage_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate usage report for last N days"""
        report = {
            'total_cost': 0.0,
            'total_tokens': 0,
            'by_model': {},
            'by_operation': {},
            'daily_breakdown': {}
        }
        
        try:
            with open(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cost = float(row['estimated_cost_usd'])
                    tokens = int(row['total_tokens'])
                    model = row['model']
                    operation = row['operation']
                    date_str = row['date']
                    
                    report['total_cost'] += cost
                    report['total_tokens'] += tokens
                    
                    # By model
                    if model not in report['by_model']:
                        report['by_model'][model] = {'cost': 0.0, 'tokens': 0}
                    report['by_model'][model]['cost'] += cost
                    report['by_model'][model]['tokens'] += tokens
                    
                    # By operation
                    if operation not in report['by_operation']:
                        report['by_operation'][operation] = {'cost': 0.0, 'tokens': 0}
                    report['by_operation'][operation]['cost'] += cost
                    report['by_operation'][operation]['tokens'] += tokens
                    
                    # Daily breakdown
                    if date_str not in report['daily_breakdown']:
                        report['daily_breakdown'][date_str] = {'cost': 0.0, 'tokens': 0}
                    report['daily_breakdown'][date_str]['cost'] += cost
                    report['daily_breakdown'][date_str]['tokens'] += tokens
                    
        except FileNotFoundError:
            pass
        
        return report


# Global tracker instance
_cost_tracker = CostTracker()


def cost_guardrail(operation: str = 'dspy_call', session_id: str = 'default'):
    """Decorator to track DSPy token usage and enforce cost limits"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the function
            result = func(*args, **kwargs)
            
            # Try to extract token usage from result
            # This depends on DSPy's response format
            prompt_tokens = 0
            completion_tokens = 0
            model = 'unknown'
            
            # Check if result has usage information
            if hasattr(result, 'response') and hasattr(result.response, 'usage'):
                usage = result.response.usage
                prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                completion_tokens = getattr(usage, 'completion_tokens', 0)
            
            # Try to get model from DSPy settings
            try:
                import dspy
                if hasattr(dspy.settings, 'lm') and hasattr(dspy.settings.lm, 'model'):
                    model = dspy.settings.lm.model
            except:
                pass
            
            # Log usage if we have token counts
            if prompt_tokens > 0 or completion_tokens > 0:
                _cost_tracker.log_usage(
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    operation=operation,
                    session_id=session_id
                )
            
            return result
        
        return wrapper
    return decorator


def get_cost_report(days: int = 7) -> Dict[str, Any]:
    """Get cost usage report"""
    return _cost_tracker.get_usage_report(days)


def check_budget_status() -> Dict[str, Any]:
    """Check current budget status"""
    today = date.today().isoformat()
    daily_cost = _cost_tracker._get_daily_cost(today)
    
    return {
        'daily_cost': daily_cost,
        'daily_limit': _cost_tracker.max_daily_cost,
        'percentage_used': (daily_cost / _cost_tracker.max_daily_cost) * 100,
        'remaining_budget': _cost_tracker.max_daily_cost - daily_cost,
        'warn_threshold': _cost_tracker.max_daily_cost * _cost_tracker.warn_threshold
    }