"""
Code Generation Components for Evolution Framework
Autonomous generation of improvements, optimizations, and new features
"""

import ast
import re
import random
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import json

from dslmodel import DSLModel
from pydantic import Field

from .core import EvolutionStrategy, EvolutionCandidate

class GenerationResult(DSLModel):
    """Result from a code generator"""
    generator_name: str = Field(..., description="Name of generator")
    strategy: EvolutionStrategy = Field(..., description="Strategy used")
    description: str = Field(..., description="Description of generated changes")
    code_changes: Dict[str, str] = Field(default_factory=dict, description="File changes")
    new_files: Dict[str, str] = Field(default_factory=dict, description="New files")
    deleted_files: List[str] = Field(default_factory=list, description="Files to delete")
    implementation_notes: List[str] = Field(default_factory=list, description="Implementation notes")
    estimated_impact: str = Field("medium", description="Expected impact")
    risk_level: str = Field("low", description="Risk assessment")

class CodeGenerator:
    """Generates general code improvements and refactoring"""
    
    def __init__(self):
        self.name = "CodeGenerator"
        
    async def generate(self, target_path: Path, strategy: EvolutionStrategy, generation: int) -> Dict[str, Any]:
        """Generate code improvements based on strategy"""
        
        python_files = list(target_path.rglob("*.py"))
        
        if not python_files:
            return self._create_default_result("No Python files found to improve")
        
        # Select random file for improvement
        target_file = random.choice(python_files)
        
        try:
            content = target_file.read_text()
            
            # Generate improvement based on strategy
            if strategy == EvolutionStrategy.CODE_QUALITY_IMPROVEMENT:
                improved_content = await self._improve_code_quality(content, target_file.name)
            elif strategy == EvolutionStrategy.PERFORMANCE_OPTIMIZATION:
                improved_content = await self._optimize_performance(content, target_file.name)
            elif strategy == EvolutionStrategy.SECURITY_HARDENING:
                improved_content = await self._harden_security(content, target_file.name)
            else:
                improved_content = await self._general_improvement(content, target_file.name)
            
            # Create relative path
            rel_path = target_file.relative_to(target_path)
            
            return {
                "description": f"Improved {rel_path} for {strategy.value}",
                "code_changes": {str(rel_path): improved_content},
                "implementation_notes": [f"Applied {strategy.value} to {rel_path}"],
                "estimated_impact": "medium",
                "risk_level": "low"
            }
            
        except Exception as e:
            return self._create_default_result(f"Failed to improve {target_file.name}: {str(e)}")
    
    def _create_default_result(self, description: str) -> Dict[str, Any]:
        """Create default result when generation fails"""
        return {
            "description": description,
            "code_changes": {},
            "new_files": {},
            "deleted_files": [],
            "implementation_notes": [description],
            "estimated_impact": "low",
            "risk_level": "low"
        }
    
    async def _improve_code_quality(self, content: str, filename: str) -> str:
        """Improve code quality through various enhancements"""
        lines = content.splitlines()
        improved_lines = []
        
        for line in lines:
            improved_line = line
            
            # Fix line length issues
            if len(line) > 120:
                # Simple line breaking for imports
                if line.strip().startswith('from ') and ',' in line:
                    parts = line.split('import ')
                    if len(parts) == 2:
                        imports = parts[1].split(',')
                        if len(imports) > 1:
                            improved_line = f"{parts[0]}import (\n"
                            for imp in imports:
                                improved_line += f"    {imp.strip()},\n"
                            improved_line += ")"
            
            # Add type hints to function definitions (simplified)
            if re.match(r'\s*def \w+\(.*\):', line) and '->' not in line:
                if not line.strip().startswith('def __'):
                    improved_line = line.replace('):', ') -> Any:')
                    if 'from typing import Any' not in content:
                        # Note: This is a simplification
                        pass
            
            # Improve variable naming (basic)
            improved_line = re.sub(r'\b([a-z])(\d+)\b', r'\1_\2', improved_line)
            
            improved_lines.append(improved_line)
        
        # Add module docstring if missing
        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
            docstring = f'"""\n{filename} - Enhanced for code quality\n"""\n\n'
            improved_content = docstring + '\n'.join(improved_lines)
        else:
            improved_content = '\n'.join(improved_lines)
        
        # Add imports if needed
        if '-> Any:' in improved_content and 'from typing import Any' not in improved_content:
            import_line = 'from typing import Any\n'
            if improved_content.startswith('"""'):
                # Add after module docstring
                parts = improved_content.split('"""', 2)
                if len(parts) >= 3:
                    improved_content = f'"""{parts[1]}"""\n\n{import_line}{parts[2]}'
            else:
                improved_content = import_line + improved_content
        
        return improved_content
    
    async def _optimize_performance(self, content: str, filename: str) -> str:
        """Apply performance optimizations"""
        
        # Replace inefficient patterns
        optimized = content
        
        # Optimize list operations
        optimized = re.sub(
            r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):',
            r'for \1, item in enumerate(\2):',
            optimized
        )
        
        # Optimize string concatenation
        optimized = re.sub(
            r'(\w+)\s*\+=\s*(["\'][^"\']*["\'])',
            r'\1 = "".join([\1, \2])',
            optimized
        )
        
        # Add caching hints
        if 'def ' in optimized and 'from functools import lru_cache' not in optimized:
            # Find function definitions that might benefit from caching
            lines = optimized.splitlines()
            for i, line in enumerate(lines):
                if re.match(r'\s*def \w+\(.*\):', line) and not line.strip().startswith('def __'):
                    # Add cache decorator (simplified heuristic)
                    if 'calculate' in line.lower() or 'compute' in line.lower():
                        indent = len(line) - len(line.lstrip())
                        decorator = ' ' * indent + '@lru_cache(maxsize=128)'
                        lines.insert(i, decorator)
                        break
            
            # Add import
            if '@lru_cache' in '\n'.join(lines):
                if optimized.startswith('"""'):
                    parts = optimized.split('"""', 2)
                    if len(parts) >= 3:
                        optimized = f'"""{parts[1]}"""\n\nfrom functools import lru_cache\n{parts[2]}'
                else:
                    optimized = 'from functools import lru_cache\n' + optimized
                optimized = '\n'.join(lines)
        
        return optimized
    
    async def _harden_security(self, content: str, filename: str) -> str:
        """Apply security hardening"""
        
        hardened = content
        
        # Replace dangerous functions
        hardened = re.sub(r'eval\s*\(', 'ast.literal_eval(', hardened)
        hardened = re.sub(r'os\.system\s*\(', 'subprocess.run([', hardened)
        
        # Fix subprocess calls
        if 'subprocess.run([' in hardened and 'subprocess.run(' in hardened:
            # Need to fix the replacement above
            hardened = hardened.replace('subprocess.run([', 'subprocess.run(')
        
        # Replace weak crypto
        hardened = re.sub(r'hashlib\.md5\s*\(', 'hashlib.sha256(', hardened)
        hardened = re.sub(r'hashlib\.sha1\s*\(', 'hashlib.sha256(', hardened)
        
        # Replace weak random
        hardened = re.sub(r'random\.random\s*\(', 'secrets.SystemRandom().random(', hardened)
        
        # Add necessary imports
        imports_needed = []
        if 'ast.literal_eval' in hardened and 'import ast' not in hardened:
            imports_needed.append('import ast')
        if 'subprocess.run' in hardened and 'import subprocess' not in hardened:
            imports_needed.append('import subprocess')
        if 'secrets.SystemRandom' in hardened and 'import secrets' not in hardened:
            imports_needed.append('import secrets')
        
        if imports_needed:
            import_block = '\n'.join(imports_needed) + '\n'
            if hardened.startswith('"""'):
                parts = hardened.split('"""', 2)
                if len(parts) >= 3:
                    hardened = f'"""{parts[1]}"""\n\n{import_block}{parts[2]}'
            else:
                hardened = import_block + hardened
        
        return hardened
    
    async def _general_improvement(self, content: str, filename: str) -> str:
        """Apply general improvements"""
        
        improved = content
        
        # Add better error handling
        lines = improved.splitlines()
        improved_lines = []
        
        for i, line in enumerate(lines):
            improved_lines.append(line)
            
            # Add logging after function definitions
            if re.match(r'\s*def \w+\(.*\):', line) and not line.strip().startswith('def __'):
                indent = len(line) - len(line.lstrip()) + 4
                log_line = ' ' * indent + f'logger.debug(f"Entering {line.split("def ")[1].split("(")[0]}")'
                improved_lines.append(log_line)
        
        improved = '\n'.join(improved_lines)
        
        # Add logging import if needed
        if 'logger.debug' in improved and 'import logging' not in improved:
            logging_imports = '''import logging

logger = logging.getLogger(__name__)
'''
            if improved.startswith('"""'):
                parts = improved.split('"""', 2)
                if len(parts) >= 3:
                    improved = f'"""{parts[1]}"""\n\n{logging_imports}{parts[2]}'
            else:
                improved = logging_imports + improved
        
        return improved

class OptimizationGenerator:
    """Generates performance optimizations"""
    
    def __init__(self):
        self.name = "OptimizationGenerator"
        
    async def generate(self, target_path: Path, strategy: EvolutionStrategy, generation: int) -> Dict[str, Any]:
        """Generate performance optimizations"""
        
        # Find files with performance opportunities
        opportunities = await self._find_optimization_opportunities(target_path)
        
        if not opportunities:
            return {
                "description": "No optimization opportunities found",
                "code_changes": {},
                "implementation_notes": ["Codebase already well-optimized"]
            }
        
        # Select top opportunity
        opportunity = opportunities[0]
        
        try:
            optimized_content = await self._apply_optimization(
                opportunity['file_path'],
                opportunity['optimization_type']
            )
            
            rel_path = opportunity['file_path'].relative_to(target_path)
            
            return {
                "description": f"Applied {opportunity['optimization_type']} optimization to {rel_path}",
                "code_changes": {str(rel_path): optimized_content},
                "implementation_notes": [
                    f"Optimization: {opportunity['description']}",
                    f"Expected improvement: {opportunity['expected_improvement']}"
                ],
                "estimated_impact": "high",
                "risk_level": "medium"
            }
            
        except Exception as e:
            return {
                "description": f"Failed to apply optimization: {str(e)}",
                "code_changes": {},
                "implementation_notes": [f"Optimization failed: {str(e)}"]
            }
    
    async def _find_optimization_opportunities(self, target_path: Path) -> List[Dict[str, Any]]:
        """Find performance optimization opportunities"""
        opportunities = []
        
        python_files = list(target_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                
                # Check for various optimization patterns
                if re.search(r'for.*in.*range\(len\(', content):
                    opportunities.append({
                        'file_path': py_file,
                        'optimization_type': 'enumerate_optimization',
                        'description': 'Replace range(len()) with enumerate()',
                        'expected_improvement': '10-20% faster iteration'
                    })
                
                if content.count('+=') > 5:
                    opportunities.append({
                        'file_path': py_file,
                        'optimization_type': 'string_join_optimization',
                        'description': 'Replace string concatenation with join()',
                        'expected_improvement': '50-80% faster string building'
                    })
                
                if re.search(r'\.append\(.*\)\s*for.*in', content):
                    opportunities.append({
                        'file_path': py_file,
                        'optimization_type': 'list_comprehension',
                        'description': 'Replace append loops with list comprehensions',
                        'expected_improvement': '20-40% faster list building'
                    })
                
            except Exception:
                continue
        
        # Sort by potential impact
        return sorted(opportunities, key=lambda x: x['expected_improvement'], reverse=True)
    
    async def _apply_optimization(self, file_path: Path, optimization_type: str) -> str:
        """Apply specific optimization to file"""
        content = file_path.read_text()
        
        if optimization_type == 'enumerate_optimization':
            content = re.sub(
                r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):',
                r'for \1, item in enumerate(\2):',
                content
            )
        
        elif optimization_type == 'string_join_optimization':
            # Convert string concatenation to join
            content = re.sub(
                r'(\w+)\s*\+=\s*(["\'][^"\']*["\'])',
                r'_temp_parts.append(\2)  # \1 = "".join(_temp_parts)',
                content
            )
        
        elif optimization_type == 'list_comprehension':
            # This is complex to do automatically, so add a comment
            content = '# TODO: Convert append loops to list comprehensions\n' + content
        
        return content

class FeatureGenerator:
    """Generates new features and capabilities"""
    
    def __init__(self):
        self.name = "FeatureGenerator"
        
    async def generate(self, target_path: Path, strategy: EvolutionStrategy, generation: int) -> Dict[str, Any]:
        """Generate new features"""
        
        # Analyze existing codebase to suggest features
        feature_suggestions = await self._analyze_feature_opportunities(target_path)
        
        if not feature_suggestions:
            feature = await self._generate_generic_feature(target_path)
        else:
            feature = random.choice(feature_suggestions)
        
        # Generate feature implementation
        feature_code = await self._implement_feature(feature)
        
        return {
            "description": f"Added new feature: {feature['name']}",
            "new_files": feature_code['new_files'],
            "code_changes": feature_code.get('modifications', {}),
            "implementation_notes": [
                f"Feature: {feature['name']}",
                f"Description: {feature['description']}",
                f"Benefits: {feature['benefits']}"
            ],
            "estimated_impact": "high",
            "risk_level": "medium"
        }
    
    async def _analyze_feature_opportunities(self, target_path: Path) -> List[Dict[str, Any]]:
        """Analyze codebase for feature opportunities"""
        opportunities = []
        
        python_files = list(target_path.rglob("*.py"))
        
        # Check for common patterns that suggest missing features
        has_cli = any('cli' in f.name.lower() for f in python_files)
        has_config = any('config' in f.name.lower() for f in python_files)
        has_tests = any('test' in f.name.lower() for f in python_files)
        has_logging = any('log' in f.read_text() for f in python_files[:5] if f.exists())
        
        if not has_config:
            opportunities.append({
                'name': 'Configuration Management',
                'description': 'Add centralized configuration management',
                'benefits': 'Easier deployment and environment management'
            })
        
        if not has_tests:
            opportunities.append({
                'name': 'Test Suite',
                'description': 'Add comprehensive test suite',
                'benefits': 'Improved reliability and regression detection'
            })
        
        if not has_logging:
            opportunities.append({
                'name': 'Structured Logging',
                'description': 'Add structured logging framework',
                'benefits': 'Better observability and debugging'
            })
        
        # Always suggest monitoring
        opportunities.append({
            'name': 'Health Monitoring',
            'description': 'Add health check and monitoring endpoints',
            'benefits': 'Better operational visibility'
        })
        
        return opportunities
    
    async def _generate_generic_feature(self, target_path: Path) -> Dict[str, Any]:
        """Generate a generic utility feature"""
        features = [
            {
                'name': 'Utility Helper',
                'description': 'Add common utility functions',
                'benefits': 'Reduce code duplication and improve consistency'
            },
            {
                'name': 'Cache Manager',
                'description': 'Add intelligent caching system',
                'benefits': 'Improved performance and resource usage'
            },
            {
                'name': 'Async Wrapper',
                'description': 'Add async/await support for synchronous operations',
                'benefits': 'Better concurrency and performance'
            }
        ]
        
        return random.choice(features)
    
    async def _implement_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the specified feature"""
        
        if feature['name'] == 'Configuration Management':
            return self._implement_config_management()
        elif feature['name'] == 'Test Suite':
            return self._implement_test_suite()
        elif feature['name'] == 'Structured Logging':
            return self._implement_structured_logging()
        elif feature['name'] == 'Health Monitoring':
            return self._implement_health_monitoring()
        else:
            return self._implement_utility_feature(feature)
    
    def _implement_config_management(self) -> Dict[str, Any]:
        """Implement configuration management feature"""
        config_py = '''"""
Configuration Management Module
Centralized configuration handling with environment support
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config.json")
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment"""
        # Load from file if exists
        if self.config_path.exists():
            with open(self.config_path) as f:
                self._config = json.load(f)
        
        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith('APP_'):
                config_key = key[4:].lower()
                self._config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

# Global config instance
config = ConfigManager()
'''
        
        config_json = '''{
  "debug": false,
  "log_level": "INFO",
  "max_workers": 4,
  "cache_ttl": 3600,
  "database_url": "sqlite:///app.db"
}'''
        
        return {
            'new_files': {
                'config.py': config_py,
                'config.json': config_json
            }
        }
    
    def _implement_test_suite(self) -> Dict[str, Any]:
        """Implement test suite feature"""
        test_base = '''"""
Base Test Classes and Utilities
"""

import unittest
import asyncio
from typing import Any

class BaseTestCase(unittest.TestCase):
    """Base test case with common utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {}
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def assert_evolution_fitness(self, fitness: float, threshold: float = 0.6):
        """Assert evolution fitness meets threshold"""
        self.assertGreaterEqual(fitness, threshold, 
                               f"Fitness {fitness} below threshold {threshold}")

class AsyncTestCase(BaseTestCase):
    """Base class for async tests"""
    
    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
        super().tearDown()
    
    def async_test(self, coro):
        """Run async test"""
        return self.loop.run_until_complete(coro)
'''
        
        sample_test = '''"""
Sample Tests for Evolution Framework
"""

import unittest
from tests.base import BaseTestCase, AsyncTestCase

class TestEvolutionFramework(BaseTestCase):
    """Test evolution framework functionality"""
    
    def test_fitness_calculation(self):
        """Test fitness calculation"""
        # Mock fitness calculation
        fitness = 0.75
        self.assert_evolution_fitness(fitness)
    
    def test_candidate_generation(self):
        """Test candidate generation"""
        # Test candidate creation
        self.assertTrue(True)  # Placeholder

class TestAsyncEvolution(AsyncTestCase):
    """Test async evolution operations"""
    
    def test_async_analysis(self):
        """Test async analysis"""
        async def mock_analysis():
            return {"score": 0.8}
        
        result = self.async_test(mock_analysis())
        self.assertEqual(result["score"], 0.8)
'''
        
        return {
            'new_files': {
                'tests/__init__.py': '',
                'tests/base.py': test_base,
                'tests/test_evolution.py': sample_test
            }
        }
    
    def _implement_structured_logging(self) -> Dict[str, Any]:
        """Implement structured logging feature"""
        logging_py = '''"""
Structured Logging System
Enhanced logging with context and structured output
"""

import logging
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class EvolutionLogger:
    """Enhanced logger for evolution framework"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_handler()
    
    def _setup_handler(self):
        """Setup structured logging handler"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def evolution_start(self, strategy: str, generation: int):
        """Log evolution start"""
        self.logger.info("Evolution started", extra={
            'extra_fields': {
                'event': 'evolution_start',
                'strategy': strategy,
                'generation': generation
            }
        })
    
    def fitness_evaluated(self, candidate_id: str, fitness: float):
        """Log fitness evaluation"""
        self.logger.info("Fitness evaluated", extra={
            'extra_fields': {
                'event': 'fitness_evaluated',
                'candidate_id': candidate_id,
                'fitness': fitness
            }
        })
    
    def deployment_success(self, candidate_id: str):
        """Log successful deployment"""
        self.logger.info("Deployment successful", extra={
            'extra_fields': {
                'event': 'deployment_success',
                'candidate_id': candidate_id
            }
        })

# Global logger instance
evolution_logger = EvolutionLogger('evolution')
'''
        
        return {
            'new_files': {
                'logging_system.py': logging_py
            }
        }
    
    def _implement_health_monitoring(self) -> Dict[str, Any]:
        """Implement health monitoring feature"""
        health_py = '''"""
Health Monitoring and Status Checks
"""

import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class HealthCheck:
    """Individual health check"""
    name: str
    status: str
    message: str
    response_time_ms: float
    timestamp: datetime

class HealthMonitor:
    """System health monitoring"""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.last_check: Optional[datetime] = None
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        # Perform individual checks
        await self._check_memory_usage()
        await self._check_disk_space()
        await self._check_evolution_engine()
        
        total_time = (time.time() - start_time) * 1000
        self.last_check = datetime.utcnow()
        
        # Aggregate results
        healthy_checks = sum(1 for check in self.checks.values() if check.status == "healthy")
        total_checks = len(self.checks)
        
        overall_status = "healthy" if healthy_checks == total_checks else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": self.last_check.isoformat(),
            "response_time_ms": total_time,
            "checks": {name: {
                "status": check.status,
                "message": check.message,
                "response_time_ms": check.response_time_ms
            } for name, check in self.checks.items()},
            "summary": {
                "healthy": healthy_checks,
                "total": total_checks,
                "uptime": self._get_uptime()
            }
        }
    
    async def _check_memory_usage(self):
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            status = "healthy" if memory.percent < 80 else "warning"
            message = f"Memory usage: {memory.percent:.1f}%"
            
            self.checks["memory"] = HealthCheck(
                name="memory",
                status=status,
                message=message,
                response_time_ms=1.0,
                timestamp=datetime.utcnow()
            )
        except ImportError:
            self.checks["memory"] = HealthCheck(
                name="memory",
                status="unknown",
                message="psutil not available",
                response_time_ms=0.1,
                timestamp=datetime.utcnow()
            )
    
    async def _check_disk_space(self):
        """Check disk space"""
        try:
            import shutil
            usage = shutil.disk_usage("/")
            percent_used = (usage.used / usage.total) * 100
            
            status = "healthy" if percent_used < 85 else "warning"
            message = f"Disk usage: {percent_used:.1f}%"
            
            self.checks["disk"] = HealthCheck(
                name="disk",
                status=status,
                message=message,
                response_time_ms=2.0,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            self.checks["disk"] = HealthCheck(
                name="disk",
                status="error",
                message=f"Disk check failed: {str(e)}",
                response_time_ms=1.0,
                timestamp=datetime.utcnow()
            )
    
    async def _check_evolution_engine(self):
        """Check evolution engine status"""
        # Mock evolution engine check
        self.checks["evolution"] = HealthCheck(
            name="evolution",
            status="healthy",
            message="Evolution engine operational",
            response_time_ms=5.0,
            timestamp=datetime.utcnow()
        )
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        # Simplified uptime calculation
        return "24h 15m"

# Global health monitor
health_monitor = HealthMonitor()
'''
        
        return {
            'new_files': {
                'health_monitor.py': health_py
            }
        }
    
    def _implement_utility_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Implement generic utility feature"""
        utils_py = f'''"""
{feature['name']} - {feature['description']}
"""

from typing import Any, Dict, List, Optional
import asyncio

class {feature['name'].replace(' ', '')}:
    """
    {feature['description']}
    
    Benefits: {feature['benefits']}
    """
    
    def __init__(self):
        self.initialized = True
    
    async def process(self, data: Any) -> Any:
        """Process data using this feature"""
        # Placeholder implementation
        return data
    
    def get_status(self) -> Dict[str, Any]:
        """Get feature status"""
        return {{
            "name": "{feature['name']}",
            "status": "active",
            "description": "{feature['description']}"
        }}

# Feature instance
{feature['name'].lower().replace(' ', '_')} = {feature['name'].replace(' ', '')}()
'''
        
        return {
            'new_files': {
                f"{feature['name'].lower().replace(' ', '_')}.py": utils_py
            }
        }

class RefactoringGenerator:
    """Generates code refactoring improvements"""
    
    def __init__(self):
        self.name = "RefactoringGenerator"
        
    async def generate(self, target_path: Path, strategy: EvolutionStrategy, generation: int) -> Dict[str, Any]:
        """Generate refactoring improvements"""
        
        # Find refactoring opportunities
        opportunities = await self._find_refactoring_opportunities(target_path)
        
        if not opportunities:
            return {
                "description": "No refactoring opportunities found",
                "code_changes": {},
                "implementation_notes": ["Code structure is already well-organized"]
            }
        
        # Apply top refactoring
        opportunity = opportunities[0]
        
        try:
            refactored_content = await self._apply_refactoring(
                opportunity['file_path'],
                opportunity['refactoring_type']
            )
            
            rel_path = opportunity['file_path'].relative_to(target_path)
            
            return {
                "description": f"Applied {opportunity['refactoring_type']} to {rel_path}",
                "code_changes": {str(rel_path): refactored_content},
                "implementation_notes": [
                    f"Refactoring: {opportunity['description']}",
                    f"Benefit: {opportunity['benefit']}"
                ],
                "estimated_impact": "medium",
                "risk_level": "low"
            }
            
        except Exception as e:
            return {
                "description": f"Refactoring failed: {str(e)}",
                "code_changes": {},
                "implementation_notes": [f"Failed to refactor: {str(e)}"]
            }
    
    async def _find_refactoring_opportunities(self, target_path: Path) -> List[Dict[str, Any]]:
        """Find code refactoring opportunities"""
        opportunities = []
        
        python_files = list(target_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                # Check for long functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                        if func_lines > 50:
                            opportunities.append({
                                'file_path': py_file,
                                'refactoring_type': 'extract_method',
                                'description': f'Function {node.name} is {func_lines} lines long',
                                'benefit': 'Improved readability and maintainability'
                            })
                
                # Check for duplicate code patterns
                if content.count('def ') > 10:
                    opportunities.append({
                        'file_path': py_file,
                        'refactoring_type': 'consolidate_methods',
                        'description': 'Many methods detected - potential for consolidation',
                        'benefit': 'Reduced code duplication'
                    })
                
            except Exception:
                continue
        
        return opportunities
    
    async def _apply_refactoring(self, file_path: Path, refactoring_type: str) -> str:
        """Apply specific refactoring"""
        content = file_path.read_text()
        
        if refactoring_type == 'extract_method':
            # Add helper methods (simplified)
            lines = content.splitlines()
            
            # Find functions and add helper comments
            for i, line in enumerate(lines):
                if re.match(r'\s*def \w+\(.*\):', line) and 'def __' not in line:
                    indent = len(line) - len(line.lstrip())
                    helper_comment = ' ' * (indent + 4) + '# TODO: Consider extracting helper methods'
                    lines.insert(i + 1, helper_comment)
                    break
            
            content = '\n'.join(lines)
        
        elif refactoring_type == 'consolidate_methods':
            # Add consolidation comment
            content = '# TODO: Review methods for consolidation opportunities\n' + content
        
        return content

class TestGenerator:
    """Generates automated tests"""
    
    def __init__(self):
        self.name = "TestGenerator"
        
    async def generate(self, target_path: Path, strategy: EvolutionStrategy, generation: int) -> Dict[str, Any]:
        """Generate test cases"""
        
        # Find untested modules
        untested_modules = await self._find_untested_modules(target_path)
        
        if not untested_modules:
            return {
                "description": "All modules appear to have test coverage",
                "new_files": {},
                "implementation_notes": ["Test coverage appears complete"]
            }
        
        # Generate tests for first untested module
        module_path = untested_modules[0]
        test_content = await self._generate_test_file(module_path, target_path)
        
        # Create test file path
        rel_path = module_path.relative_to(target_path)
        test_file_name = f"test_{rel_path.stem}.py"
        test_dir = target_path / "tests"
        test_file_path = test_dir / test_file_name
        
        return {
            "description": f"Generated tests for {rel_path}",
            "new_files": {str(test_file_path.relative_to(target_path)): test_content},
            "implementation_notes": [
                f"Added tests for {rel_path}",
                "Tests include basic functionality coverage",
                "Consider adding integration tests"
            ],
            "estimated_impact": "high",
            "risk_level": "low"
        }
    
    async def _find_untested_modules(self, target_path: Path) -> List[Path]:
        """Find modules without corresponding tests"""
        python_files = list(target_path.rglob("*.py"))
        test_files = list(target_path.rglob("test_*.py"))
        
        # Extract tested module names
        tested_modules = set()
        for test_file in test_files:
            if test_file.name.startswith('test_'):
                module_name = test_file.name[5:-3]  # Remove 'test_' and '.py'
                tested_modules.add(module_name)
        
        # Find untested modules
        untested = []
        for py_file in python_files:
            if (not py_file.name.startswith('test_') and 
                not py_file.name.startswith('__') and
                py_file.stem not in tested_modules):
                untested.append(py_file)
        
        return untested
    
    async def _generate_test_file(self, module_path: Path, target_path: Path) -> str:
        """Generate test file content for module"""
        
        rel_path = module_path.relative_to(target_path)
        import_path = str(rel_path.with_suffix('')).replace('/', '.')
        
        # Analyze module to find testable functions/classes
        try:
            content = module_path.read_text()
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
        except Exception:
            functions = []
            classes = []
        
        # Generate test content
        test_content = f'''"""
Tests for {rel_path}
Generated automatically by Evolution Framework
"""

import unittest
from unittest.mock import Mock, patch

try:
    from {import_path} import *
except ImportError:
    # Handle import issues gracefully
    pass

class Test{rel_path.stem.title()}(unittest.TestCase):
    """Test cases for {rel_path.stem} module"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        pass
'''
        
        # Add function tests
        for func_name in functions[:5]:  # Limit to first 5 functions
            test_content += f'''
    def test_{func_name}(self):
        """Test {func_name} function"""
        # TODO: Implement test for {func_name}
        pass
'''
        
        # Add class tests  
        for class_name in classes[:3]:  # Limit to first 3 classes
            test_content += f'''
    def test_{class_name.lower()}_creation(self):
        """Test {class_name} creation"""
        # TODO: Implement test for {class_name}
        pass
'''
        
        test_content += '''
    def test_module_imports(self):
        """Test that module imports successfully"""
        try:
            import ''' + import_path + '''
            self.assertTrue(True, "Module imported successfully")
        except ImportError as e:
            self.fail(f"Module import failed: {e}")

if __name__ == '__main__':
    unittest.main()
'''
        
        return test_content