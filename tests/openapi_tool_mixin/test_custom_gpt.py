import pytest
from dslmodel.workflow import Workflow, Job, Action  # Replace with the correct import path
from dslmodel.workflow import Condition  # If you use conditions in your workflow

def mock_gpt_action_request(user_prompt):
    """
    Mock function that simulates how the GPT converts a user prompt into a workflow action request.
    """
    if "multi-agent system" in user_prompt and "backtests" in user_prompt:
        # Simulated GPT action request
        workflow_yaml = """
        name: "Multi-Agent Financial Backtest"
        context:
          agents: []
        jobs:
          - name: "Fetch Financial Data"
            steps:
              - name: "Agent 1 Fetch Data"
                code: "data = fetch_financial_data()"
          - name: "Run Backtest"
            steps:
              - name: "Agent 2 Run Backtest"
                code: "results = run_backtest(data)"
        """
        return Workflow.from_yaml(workflow_yaml)
    return None


@pytest.mark.parametrize("user_prompt, expected_workflow", [
    (
        "A multi-agent system that can run backtests on financial data",
        Workflow(
            name="Multi-Agent Financial Backtest",
            context={"agents": []},
            jobs=[
                Job(
                    name="Fetch Financial Data",
                    steps=[
                        Action(name="Agent 1 Fetch Data", code="data = fetch_financial_data()")
                    ]
                ),
                Job(
                    name="Run Backtest",
                    steps=[
                        Action(name="Agent 2 Run Backtest", code="results = run_backtest(data)")
                    ]
                )
            ]
        )
    ),
])
def test_custom_gpt_multi_agent_backtest(user_prompt, expected_workflow):
    """
    Test case to simulate how a user prompt is converted into a workflow and ensure it matches
    the expected structure of the workflow model.
    """

    # Simulate the GPT action request conversion
    generated_workflow = mock_gpt_action_request(user_prompt)

    # Assert that the generated workflow matches the expected workflow structure
    assert generated_workflow is not None, "The GPT did not generate a workflow from the prompt."
    assert generated_workflow.name == expected_workflow.name
    assert generated_workflow.jobs[0].name == expected_workflow.jobs[0].name
    assert generated_workflow.jobs[0].steps[0].name == expected_workflow.jobs[0].steps[0].name
    assert generated_workflow.jobs[0].steps[0].code == expected_workflow.jobs[0].steps[0].code
    assert generated_workflow.jobs[1].name == expected_workflow.jobs[1].name
    assert generated_workflow.jobs[1].steps[0].name == expected_workflow.jobs[1].steps[0].name
    assert generated_workflow.jobs[1].steps[0].code == expected_workflow.jobs[1].steps[0].code
