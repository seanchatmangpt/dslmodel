from dslmodel.workflow import *
from dslmodel.workflow.workflow_executor import execute_action, execute_job
from dslmodel.workflow.workflow_models import Workflow, CronSchedule, Job, Action


def test_workflow_creation():
    workflow = Workflow(
        name="TestWorkflow",
        schedules=[CronSchedule(cron="0 0 * * *")],
        jobs=[
            Job(
                name="TestJob",
                runner="python",
                steps=[Action(name="TestAction", code="print('Hello, World!')")],
            )
        ],
    )
    assert workflow.name == "TestWorkflow"
    assert len(workflow.schedules) == 1
    assert isinstance(workflow.schedules[0], CronSchedule)
    assert workflow.schedules[0].cron == "0 0 * * *"
    assert len(workflow.jobs) == 1


def test_execute_action(capsys):
    action = Action(name="TestAction", code="print('Hello, World!')")
    context = {}
    new_context = execute_action(action, context)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"
    assert new_context == {}


def test_execute_agent_model(capsys):
    action = Action(name="TestAction", code="print('Hello, World!')")
    context = {}
    new_context = execute_action(action, context)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"
    assert new_context == {}


def test_execute_job(capsys):
    job = Job(
        name="TestJob",
        runner="python",
        steps=[
            Action(name="TestAction1", code="print('Action 1')"),
            Action(name="TestAction2", code="print('Action 2')"),
        ],
    )
    context = {}
    new_context = execute_job(job, context)
    captured = capsys.readouterr()
    assert "Action 1" in captured.out
    assert "Action 2" in captured.out
    assert new_context == {}


def test_execute_workflow(capsys):
    workflow = Workflow(
        name="TestWorkflow",
        schedules=[CronSchedule(cron="0 0 * * *")],
        jobs=[
            Job(
                name="TestJob1",
                runner="python",
                steps=[Action(name="TestAction1", code="print('Job 1, Action 1')")],
            ),
            Job(
                name="TestJob2",
                runner="python",
                steps=[Action(name="TestAction2", code="print('Job 2, Action 1')")],
            ),
        ],
    )
    execute_workflow(workflow)
    captured = capsys.readouterr()
    assert "Job 1, Action 1" in captured.out
    assert "Job 2, Action 1" in captured.out
