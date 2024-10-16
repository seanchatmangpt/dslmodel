from datetime import datetime, timedelta
from unittest.mock import patch

import pytz

from dslmodel.workflow import *
from tests.factories.workflow_factory import WorkflowFactory


def test_workflow_imports_with_mocked_prompt(scheduler, mock_clock, captured_output):
    # Create a mock workflow using the factory
    imported_workflow = WorkflowFactory(name="ImportedWorkflow")

    # Mock the from_prompt method to return our imported workflow
    with patch.object(Workflow, 'from_prompt', return_value=imported_workflow):
        workflow = WorkflowFactory(name="MainWorkflow", imports=["imported_workflow.yaml"])

        # Schedule and start the workflow
        schedule_workflow(workflow, scheduler)
        scheduler.start()

        # Simulate time passing
        while mock_clock.current < datetime(2023, 1, 3, tzinfo=pytz.UTC):
            mock_clock.advance(timedelta(hours=1))
            scheduler.wakeup()

        scheduler.shutdown()

        # Validate that both the main and imported jobs executed
        output = captured_output.getvalue()
        assert "Main job executed" in output, "Main job did not execute"
        assert "ImportedWorkflow" in output, "Imported workflow did not execute"
