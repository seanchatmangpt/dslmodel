"""
WeaverPrompt - Jinja → DSPy template engine
"""

import dspy
from jinja2 import Template
import pathlib

class WeaverPrompt:
    """Bridge between Weaver templates and DSPy"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.template_path = pathlib.Path(__file__).parent.parent / "weaver" / "templates" / f"{template_name}.weaver.j2"
        
    def forward(self, **kwargs) -> str:
        """Render template with context and return result"""
        if self.template_path.exists():
            template_content = self.template_path.read_text()
        else:
            # Fallback inline template
            template_content = self._get_fallback_template()
            
        template = Template(template_content)
        prompt = template.render(**kwargs)
        
        # Use DSPy to get LLM response
        lm = dspy.OpenAI(model="gpt-3.5-turbo")  # or whatever model is configured
        with dspy.context(lm=lm):
            response = lm(prompt)
            
        return response
    
    def _get_fallback_template(self) -> str:
        """Fallback templates for common operations"""
        if self.template_name == "git_planner":
            return """You are GitCoach, an expert in advanced Git.

Available commands (must use exactly these op names):
{{ commands }}

The user wants: "{{ goal }}"

Return **ONLY** valid JSON like:
[
  {"op":"clone","args":{"repo_url":"https://…","target_path":"tmp"}},
  {"op":"worktree","args":{"path":"wt-42","sha":"HEAD~3"}}
]

• op must match regex ^({{ strict_cmds }})$
• args keys must match the placeholders in git_registry.yaml row."""
        return "Template not found: {{ template_name }}"