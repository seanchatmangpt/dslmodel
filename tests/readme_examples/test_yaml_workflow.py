import yaml
from dslmodel.workflow import execute_workflow, initialize_context
from dslmodel.workflow.workflow_models import Workflow, Job, Action, Condition, CronSchedule

def test_yaml_workflow_execution():
    yaml_str = '''
workflow:
  name: "Weekly Meeting Setup"
  schedules:
    - type: "CronSchedule"
      cron: "0 9 * * MON"
  context:
    participants: [ ]
  jobs:
    - name: "Setup Meeting"
      steps:
        - name: "Generate Participants"
          code: "participants.extend([1, 2, 3, 4])"
        - name: "Notify Organizer"
          code: "context['notified'] = True"
          condition:
            expr: "len(participants) > 3"
'''
    data = yaml.safe_load(yaml_str)["workflow"]
    context = data["context"]
    steps = [
        Action(name=step["name"], code=step["code"], cond=Condition(**step["condition"]) if "condition" in step else None)
        for step in data["jobs"][0]["steps"]
    ]
    job = Job(name=data["jobs"][0]["name"], steps=steps)
    schedule = CronSchedule(cron=data["schedules"][0]["cron"])
    workflow = Workflow(
        name=data["name"],
        schedules=[schedule],
        jobs=[job],
        context=context
    )
    
    # Initialize and execute the workflow
    context = initialize_context(workflow)
    context = execute_workflow(workflow, context)
    
    assert "notified" in context
    assert context["notified"] is True 