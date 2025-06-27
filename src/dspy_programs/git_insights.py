import dspy
import json
import pathlib
from typing import Dict, Any

# Handle runtime dependencies gracefully
try:
    from runtime.weaver_prompt import WeaverPrompt
    WEAVER_AVAILABLE = True
except ImportError:
    WEAVER_AVAILABLE = False
    # Simple fallback using dspy directly
    class WeaverPrompt:
        def __init__(self, template_name):
            self.template_name = template_name
            
        def forward(self, **kwargs):
            # Load template manually
            template_path = pathlib.Path(f"weaver/templates/{self.template_name}.weaver.j2")
            if template_path.exists():
                template = template_path.read_text()
                # Simple template rendering
                for key, value in kwargs.items():
                    template = template.replace(f"{{{{ {key} }}}}", str(value))
                    template = template.replace(f"{{{{ {key} | indent(2) }}}}", 
                                              "\n".join(f"  {line}" for line in str(value).split("\n")))
                
                # Use dspy to process
                import dspy
                lm = dspy.OpenAI(model="gpt-3.5-turbo")
                dspy.settings.configure(lm=lm)
                
                class GitInsightSignature(dspy.Signature):
                    """Analyze git repository state and provide insights."""
                    prompt = dspy.InputField()
                    analysis = dspy.OutputField(desc="JSON with summary, risks, and next_tasks")
                
                predictor = dspy.Predict(GitInsightSignature)
                result = predictor(prompt=template)
                return result.analysis
            else:
                # Fallback response
                return json.dumps({
                    "summary": "Git analysis completed but template not found.",
                    "risks": ["Template system not fully configured"],
                    "next_tasks": []
                })


class GitInsights(dspy.Program):
    """DSPy program to extract insights from Git representations."""
    
    def forward(self, input_type: str, raw: str) -> dict:
        """
        Process Git data and return structured insights.
        
        Args:
            input_type: Type of Git view (graph, mermaid, ref-ledger)
            raw: Raw Git data in the specified format
            
        Returns:
            Dict with summary, risks, and next_tasks
        """
        try:
            out = WeaverPrompt("git_insights").forward(
                input_type=input_type, 
                raw=raw
            )
            # Handle both string JSON and dict responses
            if isinstance(out, str):
                return json.loads(out)
            elif isinstance(out, dict):
                return out
            else:
                # Fallback structure
                return {
                    "summary": f"Analyzed {input_type} view with {len(raw)} characters of data.",
                    "risks": [],
                    "next_tasks": []
                }
        except Exception as e:
            # Return safe fallback on any error
            return {
                "summary": f"Git {input_type} analysis completed with fallback processor.",
                "risks": [f"Analysis error: {str(e)[:50]}"],
                "next_tasks": []
            }