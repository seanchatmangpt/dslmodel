"""
Weaver Prompt Runtime
=====================

Provides runtime support for Weaver-generated prompts and templates.
Integrates with DSPy programs and validation systems.
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

try:
    from ..utils.span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from ..utils.log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

class WeaverPromptEngine:
    """Engine for processing Weaver-generated prompts."""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self.conventions: Dict[str, Any] = {}
        self.semantic_cache: Dict[str, Any] = {}
        self._load_templates()
        self._load_conventions()
    
    def _load_templates(self):
        """Load Weaver templates from the templates directory."""
        templates_dir = Path(__file__).parent.parent.parent / "weaver_templates"
        
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.yaml"):
                try:
                    with open(template_file) as f:
                        template_data = yaml.safe_load(f)
                        if template_data and "prompt" in template_data:
                            self.templates[template_file.stem] = template_data["prompt"]
                except Exception as e:
                    logger.warning(f"Failed to load template {template_file}: {e}")
        
        # Add default templates if none found
        if not self.templates:
            self.templates.update({
                "git_analysis": """
                Analyze the following Git repository state and provide insights:
                
                Repository: {repo_name}
                Branch: {branch}
                Recent commits: {commits}
                
                Focus on:
                1. Code quality patterns
                2. Development velocity
                3. Potential issues
                4. Recommendations
                
                Provide structured analysis with specific examples.
                """,
                
                "validation_improvement": """
                Based on validation results, suggest improvements:
                
                Validation failures: {failures}
                Success rate: {success_rate}
                Performance metrics: {metrics}
                
                Recommend:
                1. Schema adjustments
                2. Rule refinements  
                3. Performance optimizations
                4. Coverage gaps to address
                """,
                
                "scrum_insights": """
                Analyze Scrum workflow data and provide insights:
                
                Sprint: {sprint_id}
                Backlog items: {backlog_count}
                Burndown data: {burndown}
                Standup notes: {standups}
                
                Analyze:
                1. Sprint progress and velocity
                2. Potential blockers or risks
                3. Team coordination patterns
                4. Process improvement suggestions
                """
            })
    
    def _load_conventions(self):
        """Load semantic conventions for prompts."""
        conventions_file = Path(__file__).parent.parent.parent / "weaver.yaml"
        
        if conventions_file.exists():
            try:
                with open(conventions_file) as f:
                    self.conventions = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to load conventions: {e}")
        
        # Default conventions
        if not self.conventions:
            self.conventions = {
                "git_analysis": {
                    "max_commits": 10,
                    "focus_areas": ["quality", "velocity", "patterns"],
                    "output_format": "structured"
                },
                "validation": {
                    "improvement_threshold": 0.8,
                    "max_suggestions": 5,
                    "priority_levels": ["critical", "important", "optional"]
                },
                "scrum": {
                    "burndown_analysis_days": 7,
                    "velocity_calculation": "story_points",
                    "risk_indicators": ["behind_schedule", "blocked_items", "low_velocity"]
                }
            }
    
    @span("weaver_prompt_generate")
    def generate_prompt(
        self,
        template_name: str,
        context: Dict[str, Any],
        conventions_override: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a prompt from a template with given context."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        # Apply conventions
        active_conventions = self.conventions.get(template_name, {})
        if conventions_override:
            active_conventions.update(conventions_override)
        
        # Merge conventions into context
        full_context = {**context, **active_conventions}
        
        try:
            # Format template with context
            formatted_prompt = template.format(**full_context)
            
            # Cache for reuse
            cache_key = f"{template_name}:{hash(json.dumps(sorted(context.items())))}"
            self.semantic_cache[cache_key] = formatted_prompt
            
            return formatted_prompt
            
        except KeyError as e:
            logger.error(f"Missing context variable in template {template_name}: {e}")
            # Return template with missing variables highlighted
            return template.replace("{" + str(e).strip("'") + "}", f"[MISSING: {e}]")
    
    @span("weaver_prompt_validate")
    def validate_prompt(self, prompt: str, template_name: str) -> Dict[str, Any]:
        """Validate a generated prompt against conventions."""
        conventions = self.conventions.get(template_name, {})
        
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "quality_score": 1.0
        }
        
        # Check prompt length
        if len(prompt) > conventions.get("max_length", 2000):
            validation_result["warnings"].append("Prompt exceeds recommended length")
            validation_result["quality_score"] -= 0.1
        
        # Check for missing variables
        if "[MISSING:" in prompt:
            validation_result["errors"].append("Prompt contains missing variables")
            validation_result["valid"] = False
            validation_result["quality_score"] -= 0.5
        
        # Check structure
        if template_name == "git_analysis" and "Repository:" not in prompt:
            validation_result["warnings"].append("Git analysis missing repository context")
            validation_result["quality_score"] -= 0.2
        
        return validation_result
    
    @span("weaver_prompt_optimize")
    def optimize_prompt(self, template_name: str, feedback: Dict[str, Any]) -> str:
        """Optimize a prompt template based on feedback."""
        if template_name not in self.templates:
            return ""
        
        current_template = self.templates[template_name]
        
        # Apply optimizations based on feedback
        if feedback.get("too_verbose"):
            # Make template more concise
            optimized = current_template.replace("Provide detailed", "Provide")
            optimized = optimized.replace("comprehensive", "focused")
        elif feedback.get("too_brief"):
            # Add more detail
            optimized = current_template.replace("Provide", "Provide detailed")
            optimized = optimized.replace("List", "Comprehensively list")
        else:
            optimized = current_template
        
        # Update template
        self.templates[template_name] = optimized
        
        logger.info(f"Optimized template {template_name} based on feedback")
        return optimized

# Global engine instance
_engine = None

def get_weaver_engine() -> WeaverPromptEngine:
    """Get or create the global Weaver prompt engine."""
    global _engine
    if _engine is None:
        _engine = WeaverPromptEngine()
    return _engine

# Convenience functions for DSPy integration

@span("weaver_git_analysis_prompt")
def git_analysis_prompt(repo_name: str, branch: str, commits: List[str]) -> str:
    """Generate a git analysis prompt."""
    engine = get_weaver_engine()
    return engine.generate_prompt("git_analysis", {
        "repo_name": repo_name,
        "branch": branch,
        "commits": commits[:10]  # Limit to 10 commits
    })

@span("weaver_validation_prompt")
def validation_improvement_prompt(
    failures: List[str],
    success_rate: float,
    metrics: Dict[str, Any]
) -> str:
    """Generate a validation improvement prompt."""
    engine = get_weaver_engine()
    return engine.generate_prompt("validation_improvement", {
        "failures": failures,
        "success_rate": success_rate,
        "metrics": metrics
    })

@span("weaver_scrum_analysis_prompt")
def scrum_insights_prompt(
    sprint_id: str,
    backlog_count: int,
    burndown: Dict[str, Any],
    standups: List[str]
) -> str:
    """Generate a Scrum insights prompt."""
    engine = get_weaver_engine()
    return engine.generate_prompt("scrum_insights", {
        "sprint_id": sprint_id,
        "backlog_count": backlog_count,
        "burndown": burndown,
        "standups": standups
    })

# Template management functions

@span("weaver_add_template")
def add_template(name: str, template: str, conventions: Optional[Dict[str, Any]] = None):
    """Add a new prompt template."""
    engine = get_weaver_engine()
    engine.templates[name] = template
    
    if conventions:
        engine.conventions[name] = conventions
    
    logger.info(f"Added template: {name}")

@span("weaver_list_templates")
def list_templates() -> List[str]:
    """List all available templates."""
    engine = get_weaver_engine()
    return list(engine.templates.keys())

@span("weaver_get_template")
def get_template(name: str) -> Optional[str]:
    """Get a template by name."""
    engine = get_weaver_engine()
    return engine.templates.get(name)

# Integration with feedback loop
def report_prompt_feedback(template_name: str, feedback: Dict[str, Any]):
    """Report feedback on a prompt template."""
    try:
        from ..utils.otel_feedback_loop import send_feedback_event
        
        send_feedback_event(
            source="weaver_prompt",
            event_type="prompt_feedback",
            data={
                "template_name": template_name,
                "feedback": feedback
            },
            severity="info"
        )
        
        # Auto-optimize based on feedback
        engine = get_weaver_engine()
        engine.optimize_prompt(template_name, feedback)
        
    except ImportError:
        logger.warning("Could not report prompt feedback - feedback loop not available")