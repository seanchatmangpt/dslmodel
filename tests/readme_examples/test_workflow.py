from dslmodel.workflow import execute_workflow, initialize_context
from dslmodel.workflow.workflow_models import Workflow, Job, Action, Condition, CronSchedule

def test_workflow_execution():
    context = {"participants": []}
    condition = Condition(expr="len(participants) > 3")
    action1 = Action(
        name="Generate Participants",
        code="participants.extend([1, 2, 3, 4])"
    )
    action2 = Action(
        name="Notify Organizer",
        code="context['notified'] = True",
        cond=condition
    )
    job = Job(
        name="Setup Meeting",
        steps=[action1, action2]
    )
    schedule = CronSchedule(cron="0 9 * * MON")
    workflow = Workflow(
        name="Weekly Meeting Setup",
        schedules=[schedule],
        jobs=[job],
        context=context
    )
    
    # Initialize and execute the workflow
    context = initialize_context(context)
    context = execute_workflow(workflow, context)
    
    assert "notified" in context
    assert context["notified"] is True 