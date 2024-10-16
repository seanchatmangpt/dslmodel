from pydantic import Field
from typing import List
from dslmodel import DSLModel

# Task Model in BPMN
class Task(DSLModel):
    task_id: str = Field(..., description="Unique identifier for the task")
    task_name: str = Field(..., description="Name of the task")
    task_description: str = Field(..., description="Detailed description of the task")
    task_type: str = Field(..., description="Type of the task, e.g., user task, service task")

# Event Model in BPMN
class Event(DSLModel):
    event_id: str = Field(..., description="Unique identifier for the event")
    event_name: str = Field(..., description="Name of the event")
    event_type: str = Field(..., description="Type of the event, e.g., start event, end event")
    event_description: str = Field(..., description="Detailed description of the event")

# Gateway Model in BPMN
class Gateway(DSLModel):
    gateway_id: str = Field(..., description="Unique identifier for the gateway")
    gateway_name: str = Field(..., description="Name of the gateway")
    gateway_type: str = Field(..., description="Type of the gateway, e.g., exclusive, inclusive")

# Sequence Flow Model in BPMN
class SequenceFlow(DSLModel):
    flow_id: str = Field(..., description="Unique identifier for the sequence flow")
    source_ref: str = Field(..., description="Reference to the source element")
    target_ref: str = Field(..., description="Reference to the target element")
    condition: str | None = Field(None, description="Condition for flow execution (optional)")

# Camunda-Specific DSL Integration (used for service tasks, execution listeners, etc.)
class CamundaTask(Task):
    camunda_assignee: str = Field(..., description="Camunda-specific field for task assignment")
    camunda_form_key: str = Field(None, description="Camunda form key for user tasks")
    camunda_listener: str = Field(None, description="Execution listener for the task in Camunda BPM")

class CamundaServiceTask(CamundaTask):
    class_name: str = Field(..., description="Name of the Java class to be invoked for the service task")
    method_name: str = Field(..., description="Method to invoke in the class")

# Camunda-Specific Process Model with execution listeners, delegates, etc.
class CamundaProcess(DSLModel):
    process_id: str = Field(..., description="Unique identifier for the BPMN process")
    process_name: str = Field(..., description="Name of the BPMN process")
    tasks: List[Task] = Field(..., description="List of tasks in the process")
    events: List[Event] = Field(..., description="List of events in the process")
    gateways: List[Gateway] = Field(..., description="List of gateways in the process")
    sequence_flows: List[SequenceFlow] = Field(..., description="List of sequence flows connecting tasks, events, and gateways")
    execution_listener: str = Field(None, description="Camunda-specific execution listener for the process")
    start_event_listener: str = Field(None, description="Listener attached to the start event of the process")
    end_event_listener: str = Field(None, description="Listener attached to the end event of the process")

# Example of a Complete BPMN Process for Camunda House
class CamundaHouseBPMN(DSLModel):
    house_id: str = Field(..., description="Unique identifier for the Camunda House BPMN")
    bpmn_process: CamundaProcess = Field(..., description="The BPMN process model representing Camunda's workflow automation in the house")
    model_description: str = Field(..., description="Description of how this model represents the Camunda House architecture")

