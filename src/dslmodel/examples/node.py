from jinja2 import Template
from pathlib import Path

from dslmodel.examples.gherkin_models import Feature

# Define the Jinja template as a string
pytest_bdd_template = '''
# feature_{{ feature.name | lower | replace(' ', '_') }}.py

"""
Generated
pytest - bdd
tests
for the feature: {{feature.name}}
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Scenarios
{% for scenario in feature.scenarios %}
scenarios("{{ scenario.name }}")
{% endfor %}

# Steps
{% for scenario in feature.scenarios %}
# {{ scenario.name }}
{% for step in scenario.steps %}
@{{ step.keyword | lower }}('{{ step.text }}')
{% if step.argument and step.argument.__class__.__name__ == "DataTable" %}
def step_impl_{{ loop.index }}(data_table):
    """
    DataTable
    Implementation:
    - Headers: {{step.argument.headers}}
    - Rows: {{step.argument.rows}}
    """
    pass
{% elif step.argument and step.argument.__class__.__name__ == "DocString" %}
def step_impl_{{ loop.index }}():
    """
    DocString
    Implementation:
    Content - Type: {{step.argument.content_type}}
    Content: {{step.argument.content}}
    """
    pass
{% else %}
def step_impl_{{ loop.index }}():
    pass
{% endif %}
{% endfor %}
{% endfor %}
'''


# Generate the pytest-bdd test file dynamically
def render_pytest_bdd(feature):
    # Load Jinja template
    template = Template(pytest_bdd_template)

    # Render template with feature data
    rendered_output = template.render(feature=feature)

    # Save to file
    output_path = Path(f"feature_{feature.name.lower().replace(' ', '_')}.py")
    with open(output_path, "w") as file:
        file.write(rendered_output)

    print(f"Test file generated: {output_path}")


def main():
    """Main function"""
    # Example usage with the Feature model
    from dslmodel.utils.dspy_tools import init_instant

    init_instant()

    # Dynamically generate feature from prompt or DSLModel
    feature = Feature.from_prompt("Write me a test for the login feature with two scenarios: success and failure.")
    render_pytest_bdd(feature)



if __name__ == '__main__':
    main()
