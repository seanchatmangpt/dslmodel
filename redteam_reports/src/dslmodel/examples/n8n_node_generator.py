import os
from jinja2 import Template
from pydantic import BaseModel, Field, ValidationError
from typing import List

# Template for n8n Node
NODE_TEMPLATE = '''
from pydantic import BaseModel, Field
from pyn8n.n8n_decorator import n8n_node

# Step model for reasoning
class {{ node_name }}Step(BaseModel):
    explanation: str
    output: str

# Reasoning model for detailed insights
class {{ node_name }}Reasoning(BaseModel):
    steps: list[{{ node_name }}Step]
    {% for field in reasoning_output_fields %}
    {{ field.name }}: {{ field.type }} = Field(..., description="{{ field.description }}")
    {% endfor %}

# Input model
class {{ input_model.name }}(BaseModel):
    {% for field in input_model.fields %}
    {{ field.name }}: {{ field.type }} = Field(..., description="{{ field.description }}")
    {% endfor %}

# Output model
class {{ output_model.name }}(BaseModel):
    reasoning: {{ node_name }}Reasoning

# Node definition
@n8n_node(input_model={{ input_model.name }}, output_model={{ output_model.name }})
def {{ function_name }}(data: {{ input_model.name }}) -> {{ output_model.name }}:
    """{{ function_description }}"""
    # Hoare Logic: Pre-condition
    assert {{ pre_condition }}, "{{ pre_condition_message }}"

    steps = []
    {% for step in reasoning_steps %}
    step_{{ loop.index }} = {{ node_name }}Step(
        explanation="{{ step.explanation }}",
        output="{{ step.output }}"
    )
    steps.append(step_{{ loop.index }})
    {% endfor %}

    reasoning = {{ node_name }}Reasoning(
        steps=steps,
        {% for field in reasoning_output_fields %}
        {{ field.name }}={{ field.value }},
        {% endfor %}
    )

    # Hoare Logic: Post-condition
    assert {{ post_condition }}, "{{ post_condition_message }}"

    return {{ output_model.name }}(reasoning=reasoning)
'''

# Field Specification
class FieldSpec(BaseModel):
    name: str
    type: str
    description: str
    value: str | None = None  # Optional default value


# Node Specification
class NodeSpec(BaseModel):
    node_name: str
    function_name: str
    function_description: str
    input_model: dict  # Dictionary containing name and fields
    output_model: dict  # Dictionary containing name and fields
    reasoning_output_fields: List[FieldSpec]
    reasoning_steps: List[dict]
    pre_condition: str
    pre_condition_message: str
    post_condition: str
    post_condition_message: str


# Code Generator Function
def generate_node_code(spec: NodeSpec) -> str:
    """
    Generates Python code for a pyn8n node based on the provided specification.
    """
    template = Template(NODE_TEMPLATE)
    return template.render(
        node_name=spec.node_name,
        function_name=spec.function_name,
        function_description=spec.function_description,
        input_model=spec.input_model,
        output_model=spec.output_model,
        reasoning_output_fields=spec.reasoning_output_fields,
        reasoning_steps=spec.reasoning_steps,
        pre_condition=spec.pre_condition,
        pre_condition_message=spec.pre_condition_message,
        post_condition=spec.post_condition,
        post_condition_message=spec.post_condition_message,
    )


# File Writer Function
def write_node_to_disk(node_code: str, output_dir: str, node_name: str) -> None:
    """
    Writes the generated Python node code to a file.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{node_name.lower()}_node.py")
    with open(file_path, "w") as file:
        file.write(node_code)
    print(f"Node written to {file_path}")


# Main Function
def main():
    """Main function to demonstrate node generation and saving to disk."""
    template_data = {
        "node_name": "MonitorNode",
        "function_name": "monitor_node",
        "function_description": "Analyze metrics and generate insights.",
        "input_model": {
            "name": "MonitorInput",
            "fields": [
                {"name": "metrics", "type": "dict", "description": "Metrics for performance and resources."}
            ]
        },
        "output_model": {
            "name": "MonitorOutput",
            "fields": []
        },
        "reasoning_output_fields": [
            {"name": "insights", "type": "dict", "description": "Insights derived from metrics.",
             "value": '{"performance_status": "Optimal", "alerts": ["Resource under-utilization"]}'}
        ],
        "reasoning_steps": [
            {"explanation": "Evaluate performance metric.", "output": "Performance status: Optimal"},
            {"explanation": "Check resource usage.", "output": "Alert: Resource under-utilization"}
        ],
        "pre_condition": "'performance' in data.metrics and 'resources' in data.metrics",
        "pre_condition_message": "Metrics must include 'performance' and 'resources'.",
        "post_condition": "'performance_status' in reasoning.insights",
        "post_condition_message": "Insights must include performance status."
    }

    try:
        # Generate and validate specification
        spec = NodeSpec.model_validate(template_data)

        # Generate code
        node_code = generate_node_code(spec)

        # Write to disk
        write_node_to_disk(node_code, "./generated_nodes", spec.node_name)
    except ValidationError as e:
        print("Validation Error:", e)


if __name__ == "__main__":
    main()
