import copy
import sys
from datetime import datetime
from subprocess import Popen, PIPE
from typing import Any

import pytz
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger as APSchedulerCronTrigger
from apscheduler.triggers.date import DateTrigger as APSchedulerDateTrigger
from loguru import logger

from dslmodel.template import render
from dslmodel.workflow.workflow_models import Job, Action, Workflow, CronSchedule, DateSchedule

# Configure logger with timestamp and log level
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)
logger.add(
    "workflow_executor.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="1 MB",
)


# Custom log handler to collect log messages
class LogCollector:
    def __init__(self):
        self.messages = []

    def write(self, message):
        if message.strip():  # Avoid empty messages
            self.messages.append(message.strip())

    def flush(self):
        pass  # Required for file-like objects


def initialize_context(init_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    """Initializes the workflow context."""
    logger.debug(f"Initializing context with: {init_ctx}")
    return copy.deepcopy(init_ctx) if init_ctx else {}


def update_context(context: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    """Updates the workflow context with new values."""
    new_context = {
        k: v for k, v in context.items() if isinstance(v, (int, float, str, bool, list, dict))
    }

    new_context = copy.deepcopy(new_context)

    new_context.update(updates)

    if "__builtins__" in new_context:
        del new_context["__builtins__"]  # Remove builtins from context

    rendered_context = {}
    for arg, value in new_context.items():
        if "{{" in str(value):
            rendered_context[arg] = render(value, **new_context)
            try:
                rendered_context[arg] = eval(rendered_context[arg])
            except Exception as e:
                logger.error(f"Error converting rendered value to native Python type: {e}")
        else:
            rendered_context[arg] = value
    return rendered_context


def evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
    """Evaluates a condition within the current context."""
    logger.debug(f"Evaluating condition: '{condition}' with context: {context}")
    try:
        safe_context = copy.deepcopy(context)
        result = eval(condition, {}, safe_context)
        logger.debug(f"Condition result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error evaluating condition '{condition}': {e}")
        return False


def execute_job(job: Job, context: dict[str, Any]) -> dict[str, Any]:
    """Executes all actions within a job."""
    logger.info(f"Executing job: {job.name}")
    job_context = update_context(context, {})  # Isolate context for the job

    for action in job.steps:
        logger.info(f"Executing action: {action.name}")
        try:
            job_context = execute_action(action, job_context)  # Execute each action
            logger.info(f"Finished executing action: {action.name}")
        except Exception as e:
            logger.error(f"Error executing action {action.name}: {e!s}")

    logger.debug(f"Job {job.name} completed. Updated context: {job_context}")
    return job_context


def execute_action(action: Action, context: dict[str, Any]) -> dict[str, Any]:
    """Executes a single action, updating the context accordingly."""
    logger.info(f"Executing action: {action.name}")

    if action.cond and not evaluate_condition(action.cond.expr, context):
        logger.info(f"Condition for action '{action.name}' not met, skipping.")
        return context

    action_context = update_context(context, {})

    if action.code:
        logger.debug(f"Executing code for action '{action.name}'")
        rendered_code = render(action.code, **action_context)
        logger.debug(f"Rendered code: {rendered_code}")
        try:
            exec(rendered_code, action_context, action_context)
            logger.info(f"Code execution for action '{action.name}' completed successfully")
        except Exception as e:
            logger.error(f"Error executing code for action '{action.name}': {e!s}")
        context = update_context(context, action_context)

    if action.shell:
        logger.debug(f"Executing shell command for action '{action.name}': {action.shell}")
        try:
            process = Popen(action.shell, shell=True, stdout=PIPE, stderr=PIPE, env=action.env or None)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                logger.info(f"Shell command executed successfully. Output:\n{stdout.decode().strip()}")
            else:
                logger.error(f"Shell command failed with error:\n{stderr.decode().strip()}")

            # Optionally, capture the output in the context if needed
            action_context["shell_output"] = stdout.decode().strip()
            action_context["shell_error"] = stderr.decode().strip() if stderr else None

        except Exception as e:
            logger.error(f"Error executing shell command for action '{action.name}': {e!s}")
        context = update_context(context, action_context)

    # Execute a callable function if provided
    if action.callable:
        logger.debug(f"Executing callable for action '{action.name}'")
        try:
            result = action.callable()
            logger.debug(f"Callable result for action '{action.name}': {result}")
            if isinstance(result, dict):
                action_context.update(result)  # Update context if the callable returns a dict
        except Exception as e:
            logger.error(f"Error executing callable for action '{action.name}': {e!s}")
        context = update_context(context, action_context)

    logger.debug(f"Action '{action.name}' completed. Updated context: {context}")
    return context


def execute_workflow(workflow: Workflow, init_ctx: dict[str, Any] | None = None, verbose: bool = False) -> dict[
    str, Any]:
    """Executes all jobs defined in a workflow."""
    logger.info(f"Executing workflow: {workflow.name}")
    global_context = initialize_context(init_ctx)

    workflow.process_imports()
    workflow.topological_sort()

    log_collector = LogCollector()
    logger.add(log_collector, level="DEBUG")

    for job in workflow.jobs:
        logger.info(f"Starting execution of job: {job.name}")
        try:
            global_context = execute_job(job, global_context)
            logger.info(f"Finished execution of job: {job.name}")
        except Exception as e:
            logger.error(f"Error executing job {job.name}: {e!s}")

    if "__builtins__" in global_context:
        del global_context["__builtins__"]

    logger.info(f"Workflow '{workflow.name}' completed. Final context: {global_context}")

    if verbose:
        global_context['log_messages'] = log_collector.messages

    return global_context


def schedule_workflow(workflow: Workflow, scheduler: BaseScheduler):
    """Schedules a workflow using the provided scheduler."""
    logger.info(f"Scheduling workflow: {workflow.name}")
    for trigger in workflow.schedules:
        if isinstance(trigger, CronSchedule):
            logger.debug(f"Adding cron job for trigger: {trigger.cron}")
            job = scheduler.add_job(
                execute_workflow,
                APSchedulerCronTrigger.from_crontab(trigger.cron, timezone=pytz.UTC),
                args=[workflow],
                timezone=pytz.UTC,
            )
            logger.debug(f"Job added: {job!s}")
        elif isinstance(trigger, DateSchedule):
            logger.debug(f"Adding date job for trigger: {trigger.run_date}")
            run_date = trigger.run_date if trigger.run_date != "now" else datetime.now(pytz.UTC)
            job = scheduler.add_job(
                execute_workflow,
                APSchedulerDateTrigger(run_date=run_date, timezone=pytz.UTC),
                args=[workflow],
                timezone=pytz.UTC,
            )
            logger.debug(f"Job added: {job!s}")
        else:
            logger.error(f"Unknown trigger type: {type(trigger)}")
            
    scheduler.start()

    logger.info(f"Workflow '{workflow.name}' scheduled successfully")
    logger.debug(f"All jobs: {scheduler.get_jobs()}")
    return scheduler


def default_scheduler():
    """Returns a default scheduler."""
    return BackgroundScheduler()


if __name__ == "__main__":
    from apscheduler.schedulers.background import BackgroundScheduler

    workflow = Workflow.from_yaml("path/to/your/workflow.yaml")
    scheduler = default_scheduler()
    
    schedule_workflow(workflow, scheduler)

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
