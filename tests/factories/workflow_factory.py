# tests/factories/workflow_factory.py
import factory
from src.dslmodel.workflow import Workflow, Job, Action, DateSchedule

class ActionFactory(factory.Factory):
    class Meta:
        model = Action

    name = factory.Faker('word')
    code = factory.Faker('sentence')

class JobFactory(factory.Factory):
    class Meta:
        model = Job

    name = factory.Faker('word')
    runner = "python"
    steps = factory.List([factory.SubFactory(ActionFactory)])

class WorkflowFactory(factory.Factory):
    class Meta:
        model = Workflow

    name = factory.Faker('word')
    triggers = factory.List([DateSchedule(run_date="2023-01-02 09:00:00")])
    jobs = factory.List([factory.SubFactory(JobFactory)])

    @classmethod
    def from_prompt(cls, prompt, **kwargs):
        """Mockable from_prompt method."""
        return cls(**kwargs)
