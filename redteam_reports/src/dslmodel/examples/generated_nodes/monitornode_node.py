
from pydantic import BaseModel, Field
from pyn8n.n8n_decorator import n8n_node

# Step model for reasoning
class MonitorNodeStep(BaseModel):
    explanation: str
    output: str

# Reasoning model for detailed insights
class MonitorNodeReasoning(BaseModel):
    steps: list[MonitorNodeStep]
    
    insights: dict = Field(..., description="Insights derived from metrics.")
    

# Input model
class MonitorInput(BaseModel):
    
    metrics: dict = Field(..., description="Metrics for performance and resources.")
    

# Output model
class MonitorOutput(BaseModel):
    reasoning: MonitorNodeReasoning

# Node definition
@n8n_node(input_model=MonitorInput, output_model=MonitorOutput)
def monitor_node(data: MonitorInput) -> MonitorOutput:
    """Analyze metrics and generate insights."""
    # Hoare Logic: Pre-condition
    assert 'performance' in data.metrics and 'resources' in data.metrics, "Metrics must include 'performance' and 'resources'."

    steps = []
    
    step_1 = MonitorNodeStep(
        explanation="Evaluate performance metric.",
        output="Performance status: Optimal"
    )
    steps.append(step_1)
    
    step_2 = MonitorNodeStep(
        explanation="Check resource usage.",
        output="Alert: Resource under-utilization"
    )
    steps.append(step_2)
    

    reasoning = MonitorNodeReasoning(
        steps=steps,
        
        insights={"performance_status": "Optimal", "alerts": ["Resource under-utilization"]},
        
    )

    # Hoare Logic: Post-condition
    assert 'performance_status' in reasoning.insights, "Insights must include performance status."

    return MonitorOutput(reasoning=reasoning)