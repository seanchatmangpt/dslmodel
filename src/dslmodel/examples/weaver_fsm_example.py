"""
Example: Weaver + FSM Integration for Observable Workflows

This example demonstrates how to combine:
1. Weaver Forge for generating type-safe OTEL models
2. FSMMixin for state machine capabilities
3. DSLModel for base model functionality
4. OpenTelemetry for observability
5. Ollama/Qwen3 for AI-powered state transitions

The result is a fully observable, type-safe workflow with automatic
instrumentation of state transitions and AI decision-making.
"""
import asyncio
from enum import Enum
from typing import Optional
from loguru import logger

# Initialize LLM first
from dslmodel.utils.llm_init import init_qwen3
logger.info("Initializing Qwen3 for AI-powered workflows...")
lm = init_qwen3(temperature=0.2)  # Slightly higher temp for creativity

# OpenTelemetry setup
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

from pydantic import Field

from dslmodel.otel.fsm_weaver_integration import (
    WeaverFSMModel, 
    observable_trigger,
    WorkflowStateGenerator
)


# Setup OpenTelemetry
resource = Resource.create({"service.name": "weaver-fsm-demo"})

# Tracing
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)
trace.set_tracer_provider(tracer_provider)

# Metrics  
metric_reader = PeriodicExportingMetricReader(
    exporter=ConsoleMetricExporter(),
    export_interval_millis=5000
)
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader]
)
metrics.set_meter_provider(meter_provider)


# Define workflow states
class OrderState(str, Enum):
    """States for order processing workflow."""
    PENDING = "pending"
    VALIDATED = "validated"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_COMPLETE = "payment_complete"
    FULFILLMENT = "fulfillment"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderWorkflow(WeaverFSMModel):
    """
    Order processing workflow with observable state transitions.
    
    This model combines:
    - Type-safe fields from DSLModel
    - State machine from FSMMixin
    - OpenTelemetry instrumentation
    """
    
    # Order attributes
    order_id: str = Field(description="Unique order identifier")
    customer_id: str = Field(description="Customer placing the order")
    total_amount: float = Field(description="Total order amount in USD")
    items_count: int = Field(description="Number of items in order")
    
    # Workflow attributes
    state: OrderState = Field(default=OrderState.PENDING, description="Current order state")
    transition_count: int = Field(default=0, description="Number of state transitions")
    error_message: Optional[str] = Field(default=None, description="Error details if failed")
    
    # Business logic attributes
    is_validated: bool = Field(default=False)
    payment_verified: bool = Field(default=False)
    inventory_reserved: bool = Field(default=False)
    
    def model_post_init(self, __context) -> None:
        """Initialize the FSM after model creation."""
        super().model_post_init(__context)
        
        # Setup FSM with order states
        self.setup_fsm(OrderState, initial=OrderState.PENDING)
        
        # Setup observability with custom service name
        self.setup_observability(service_name="order-workflow")
        
    # State transition methods with business logic
    
    @observable_trigger(source=OrderState.PENDING, dest=OrderState.VALIDATED)
    def validate_order(self) -> bool:
        """Validate order details and inventory."""
        logger.info(f"Validating order {self.order_id}")
        
        # Simulate validation logic
        if self.total_amount <= 0:
            raise ValueError("Invalid order amount")
            
        if self.items_count <= 0:
            raise ValueError("Order has no items")
            
        # Mark as validated
        self.is_validated = True
        self.transition_count += 1
        
        logger.success(f"Order {self.order_id} validated")
        return True
        
    @observable_trigger(source=OrderState.VALIDATED, dest=OrderState.PAYMENT_PROCESSING)
    def start_payment(self) -> bool:
        """Initiate payment processing."""
        logger.info(f"Starting payment for order {self.order_id}")
        
        if not self.is_validated:
            raise ValueError("Cannot process payment for unvalidated order")
            
        self.transition_count += 1
        return True
        
    @observable_trigger(source=OrderState.PAYMENT_PROCESSING, dest=OrderState.PAYMENT_COMPLETE)
    def complete_payment(self, payment_id: str) -> bool:
        """Complete payment processing."""
        logger.info(f"Completing payment {payment_id} for order {self.order_id}")
        
        # Simulate payment verification
        self.payment_verified = True
        self.transition_count += 1
        
        logger.success(f"Payment completed for order {self.order_id}")
        return True
        
    @observable_trigger(source=OrderState.PAYMENT_COMPLETE, dest=OrderState.FULFILLMENT)
    def start_fulfillment(self) -> bool:
        """Start order fulfillment process."""
        logger.info(f"Starting fulfillment for order {self.order_id}")
        
        if not self.payment_verified:
            raise ValueError("Cannot fulfill order without payment")
            
        # Reserve inventory
        self.inventory_reserved = True
        self.transition_count += 1
        
        return True
        
    @observable_trigger(source=OrderState.FULFILLMENT, dest=OrderState.SHIPPED) 
    def ship_order(self, tracking_number: str) -> bool:
        """Ship the order."""
        logger.info(f"Shipping order {self.order_id} with tracking {tracking_number}")
        
        self.transition_count += 1
        return True
        
    @observable_trigger(source=OrderState.SHIPPED, dest=OrderState.DELIVERED)
    def deliver_order(self) -> bool:
        """Mark order as delivered."""
        logger.info(f"Order {self.order_id} delivered")
        
        self.transition_count += 1
        return True
        
    @observable_trigger(
        source=[OrderState.PENDING, OrderState.VALIDATED, OrderState.PAYMENT_PROCESSING],
        dest=OrderState.CANCELLED
    )
    def cancel_order(self, reason: str) -> bool:
        """Cancel the order."""
        logger.warning(f"Cancelling order {self.order_id}: {reason}")
        
        self.error_message = f"Cancelled: {reason}"
        self.transition_count += 1
        
        return True
        
    def ai_risk_assessment(self, context: str) -> str:
        """Use AI to assess order risk and recommend actions."""
        prompt = f"""
        Order Risk Assessment:
        
        Order ID: {self.order_id}
        Customer: {self.customer_id}
        Amount: ${self.total_amount}
        Items: {self.items_count}
        Current State: {self.state}
        
        Context: {context}
        
        Assess the risk level (LOW/MEDIUM/HIGH) and recommend next action.
        Respond with format: "RISK: [level] - ACTION: [recommendation]"
        """
        
        try:
            response = self.forward(prompt)
            logger.info(f"AI Risk Assessment: {response}")
            return str(response)
        except Exception as e:
            logger.error(f"AI assessment failed: {e}")
            return "RISK: UNKNOWN - ACTION: Manual review required"
        
    @observable_trigger(
        source="*",  # Can fail from any state
        dest=OrderState.FAILED
    )
    def fail_order(self, error: str) -> bool:
        """Mark order as failed."""
        logger.error(f"Order {self.order_id} failed: {error}")
        
        self.error_message = error
        self.transition_count += 1
        
        return True


async def process_order_example():
    """Example of processing an order through the workflow."""
    
    # Create an order
    order = OrderWorkflow(
        order_id="ORD-2024-001",
        customer_id="CUST-123", 
        total_amount=150.00,
        items_count=3
    )
    
    logger.info(f"Created order in state: {order.state}")
    
    try:
        # Progress through workflow
        order.validate_order()
        logger.info(f"Order state: {order.state}, transitions: {order.transition_count}")
        
        # AI Risk Assessment before payment
        risk_context = f"Large order from customer {order.customer_id} with ${order.total_amount} total"
        ai_assessment = order.ai_risk_assessment(risk_context)
        logger.info(f"AI Assessment: {ai_assessment}")
        
        order.start_payment()
        logger.info(f"Order state: {order.state}, transitions: {order.transition_count}")
        
        # Simulate async payment processing
        await asyncio.sleep(0.5)
        order.complete_payment("PAY-ABC-123")
        logger.info(f"Order state: {order.state}, transitions: {order.transition_count}")
        
        order.start_fulfillment()
        logger.info(f"Order state: {order.state}, transitions: {order.transition_count}")
        
        # Simulate fulfillment time
        await asyncio.sleep(0.3)
        order.ship_order("TRACK-12345")
        logger.info(f"Order state: {order.state}, transitions: {order.transition_count}")
        
        # Simulate delivery
        await asyncio.sleep(0.2) 
        order.deliver_order()
        logger.info(f"Order completed! Final state: {order.state}, total transitions: {order.transition_count}")
        
    except Exception as e:
        order.fail_order(str(e))
        logger.error(f"Order failed: {order.error_message}")
        
    # Show final model state
    logger.info(f"\nFinal order model:\n{order.model_dump_json(indent=2)}")
    
    return order


def generate_custom_workflow_example():
    """Example of generating a custom workflow with Weaver."""
    
    generator = WorkflowStateGenerator()
    
    # Define a custom approval workflow
    success = generator.generate_fsm_model(
        workflow_name="approval",
        states=["draft", "submitted", "reviewing", "approved", "rejected"],
        transitions=[
            {"trigger": "submit", "source": "draft", "dest": "submitted"},
            {"trigger": "start_review", "source": "submitted", "dest": "reviewing"},
            {"trigger": "approve", "source": "reviewing", "dest": "approved"},
            {"trigger": "reject", "source": "reviewing", "dest": "rejected"},
            {"trigger": "redraft", "source": "rejected", "dest": "draft"}
        ],
        attributes={
            "approver_id": {
                "type": "string",
                "requirement_level": "optional",
                "brief": "ID of the approver"
            },
            "comments": {
                "type": "string", 
                "requirement_level": "optional",
                "brief": "Review comments"
            }
        }
    )
    
    if success:
        logger.success("Generated custom approval workflow model!")
    else:
        logger.error("Failed to generate workflow model")
        
    return success


async def main():
    """Run the examples."""
    logger.info("=== Weaver + FSM Integration Demo ===\n")
    
    # Run order workflow example
    logger.info("1. Running order workflow example...")
    await process_order_example()
    
    # Generate custom workflow
    logger.info("\n2. Generating custom approval workflow...")
    generate_custom_workflow_example()
    
    # Let metrics export
    await asyncio.sleep(6)
    
    logger.info("\nDemo complete! Check console output for OpenTelemetry spans and metrics.")


if __name__ == "__main__":
    asyncio.run(main())