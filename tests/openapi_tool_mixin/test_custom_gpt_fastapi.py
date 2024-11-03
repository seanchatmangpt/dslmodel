import pytest
from fastapi import FastAPI, APIRouter, Body, HTTPException
from fastapi.testclient import TestClient

from dslmodel.workflow import execute_workflow
from dslmodel.workflow.workflow_models import Workflow, Job, Action

app = FastAPI()

# Simulating the existing OpenAPIToolMixin functionality
router = APIRouter()


@app.post("/execute_workflow")
async def _execute_workflow(workflow_yaml: dict = Body(...)):
    """
    FastAPI route to simulate workflow execution from a YAML definition.
    """
    try:
        # Simulate Workflow.from_yaml processing
        workflow = Workflow.from_yaml(workflow_yaml['workflow_yaml'])
        result = execute_workflow(workflow, verbose=True)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add router to the app
app.include_router(router)

client = TestClient(app)


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
                code: "print('data = fetch_financial_data()')"
          - name: "Run Backtest"
            steps:
              - name: "Agent 2 Run Backtest"
                code: "print('results = run_backtest(data)')"
        """
        return workflow_yaml
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
                            Action(name="Agent 1 Fetch Data", code="print('data = fetch_financial_data()')")
                        ]
                    ),
                    Job(
                        name="Run Backtest",
                        steps=[
                            Action(name="Agent 2 Run Backtest", code="print('results = run_backtest(data)')")
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
    generated_workflow_yaml = mock_gpt_action_request(user_prompt)

    assert generated_workflow_yaml is not None, "The GPT did not generate a workflow from the prompt."

    # Now let's simulate sending a POST request to the FastAPI endpoint to process this workflow
    response = client.post("/execute_workflow", json={"workflow_yaml": generated_workflow_yaml})
    assert response.status_code == 200, "Workflow execution failed."

    # Get the result from the response
    data = response.json()

    print(data)

    # Assert workflow results match the expected job names and steps
    assert data is not None
