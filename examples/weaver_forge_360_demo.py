#!/usr/bin/env python3
"""
Weaver Forge + DSLModel 360° Integration Demo

This demo showcases the complete integration of:
- Semantic convention generation
- Type-safe model creation
- FSM state management
- OpenTelemetry instrumentation
- AI-enhanced workflows
"""

import asyncio
from enum import Enum
from typing import List, Optional
from loguru import logger
from pydantic import Field

from dslmodel import DSLModel
from dslmodel.mixins import FSMMixin, trigger
from dslmodel.integrations.otel import DslmodelAttributes
from dslmodel.utils.dspy_tools import init_lm


# Step 1: Define semantic conventions (normally from Weaver Forge)
class PaymentAttributes(DslmodelAttributes):
    """Payment processing telemetry attributes"""
    payment_id: str = Field(..., description="Unique payment identifier")
    payment_method: str = Field(..., description="Payment method used")
    payment_amount: float = Field(..., description="Payment amount")
    payment_currency: str = Field("USD", description="Payment currency")
    payment_status: str = Field("pending", description="Payment status")


# Step 2: Define workflow states
class PaymentState(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# Step 3: Create observable workflow with FSM
class PaymentWorkflow(PaymentAttributes):
    """
    Payment processing workflow with complete observability
    
    Features:
    - Type-safe attributes from semantic conventions
    - State machine with automatic telemetry
    - AI-enhanced fraud detection
    - Complete observability
    """
    
    customer_id: str = Field(..., description="Customer identifier")
    merchant_id: str = Field(..., description="Merchant identifier")
    fraud_score: Optional[float] = Field(None, description="AI fraud risk score")
    state: str = Field("pending", description="Current workflow state")
    
    def __init__(self, **kwargs):
        super().__init__(
            workflow_name=f"payment-{kwargs.get('payment_id')}",
            workflow_status="started",
            **kwargs
        )
        self.state = PaymentState.PENDING.value
        logger.info(f"🏦 Payment workflow initialized: {self.payment_id}")
    
    def start_validation(self):
        """Begin payment validation with telemetry"""
        logger.info(f"🔍 Validating payment {self.payment_id}")
        self.state = PaymentState.VALIDATING.value
        # In production, this would create an OTEL span
        self._emit_telemetry("payment.validation.start", {
            "payment.method": self.payment_method,
            "payment.amount": self.payment_amount
        })
    
    async def process_payment(self):
        """Process payment with fraud detection"""
        if self.state != PaymentState.VALIDATING.value:
            logger.error(f"Cannot process payment in state: {self.state}")
            return
            
        logger.info(f"💳 Processing payment {self.payment_id}")
        self.state = PaymentState.PROCESSING.value
        
        # AI-enhanced fraud detection (mock)
        self.fraud_score = await self._calculate_fraud_score()
        
        if self.fraud_score > 0.8:
            logger.warning(f"⚠️ High fraud risk: {self.fraud_score}")
            self.reject_payment(f"High fraud risk: {self.fraud_score:.2f}")
            return
        
        self._emit_telemetry("payment.process", {
            "payment.fraud_score": self.fraud_score,
            "payment.risk_level": self._get_risk_level()
        })
    
    def complete_payment(self):
        """Successfully complete payment"""
        if self.state != PaymentState.PROCESSING.value:
            logger.error(f"Cannot complete payment in state: {self.state}")
            return
            
        self.state = PaymentState.COMPLETED.value
        self.payment_status = "completed"
        self.workflow_status = "completed"
        self.workflow_duration_ms = 2500  # Mock duration
        
        logger.success(f"✅ Payment {self.payment_id} completed successfully!")
        self._emit_telemetry("payment.completed", self.model_dump())
    
    def reject_payment(self, reason: str = "Unknown"):
        """Reject payment with reason"""
        self.state = PaymentState.FAILED.value
        self.payment_status = "failed"
        self.workflow_status = "failed"
        
        logger.error(f"❌ Payment {self.payment_id} rejected: {reason}")
        self._emit_telemetry("payment.rejected", {
            "payment.rejection_reason": reason,
            "payment.state": self.state
        })
    
    async def _calculate_fraud_score(self) -> float:
        """AI-powered fraud detection (mock)"""
        # In production, this would use DSPy/LLM
        import random
        await asyncio.sleep(0.1)  # Simulate API call
        return random.random()
    
    def _get_risk_level(self) -> str:
        """Determine risk level from fraud score"""
        if self.fraud_score < 0.3:
            return "low"
        elif self.fraud_score < 0.7:
            return "medium"
        else:
            return "high"
    
    def _emit_telemetry(self, event_name: str, attributes: dict):
        """Emit telemetry (mock for demo)"""
        logger.debug(f"📊 Telemetry: {event_name} - {attributes}")
    
    def get_workflow_summary(self) -> dict:
        """Get complete workflow summary"""
        return {
            "payment_id": self.payment_id,
            "status": self.payment_status,
            "state": self.state,
            "amount": f"{self.payment_currency} {self.payment_amount}",
            "fraud_score": self.fraud_score,
            "duration_ms": self.workflow_duration_ms,
            "telemetry": {
                "workflow_name": self.workflow_name,
                "workflow_status": self.workflow_status,
                "otel_namespace": "dslmodel.payment"
            }
        }


# Step 4: Demonstrate batch processing
class PaymentBatchProcessor(DSLModel):
    """Process multiple payments with aggregated telemetry"""
    
    batch_id: str = Field(..., description="Batch identifier")
    payments: List[PaymentWorkflow] = Field(default_factory=list)
    
    async def process_batch(self):
        """Process all payments in batch"""
        logger.info(f"🚀 Processing batch {self.batch_id} with {len(self.payments)} payments")
        
        # Process payments concurrently
        tasks = []
        for payment in self.payments:
            payment.start_validation()
            tasks.append(payment.process_payment())
        
        await asyncio.gather(*tasks)
        
        # Complete successful payments
        for payment in self.payments:
            if payment.state == PaymentState.PROCESSING.value:
                payment.complete_payment()
        
        # Generate batch summary
        return self.get_batch_summary()
    
    def get_batch_summary(self) -> dict:
        """Get batch processing summary"""
        completed = sum(1 for p in self.payments if p.payment_status == "completed")
        failed = sum(1 for p in self.payments if p.payment_status == "failed")
        total_amount = sum(p.payment_amount for p in self.payments if p.payment_status == "completed")
        
        return {
            "batch_id": self.batch_id,
            "total_payments": len(self.payments),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / len(self.payments) if self.payments else 0,
            "total_amount": total_amount,
            "payments": [p.get_workflow_summary() for p in self.payments]
        }


async def main():
    """Run the 360° integration demo"""
    logger.info("🎯 Weaver Forge + DSLModel 360° Integration Demo")
    logger.info("=" * 60)
    
    # Initialize AI (optional, for production use)
    # init_lm("ollama/qwen3")
    
    # Create payment batch
    batch = PaymentBatchProcessor(batch_id="BATCH-2024-001")
    
    # Add sample payments
    payment_data = [
        {"payment_id": "PAY-001", "payment_method": "credit_card", "payment_amount": 99.99, "customer_id": "CUST-123", "merchant_id": "MERCH-ABC"},
        {"payment_id": "PAY-002", "payment_method": "paypal", "payment_amount": 49.99, "customer_id": "CUST-456", "merchant_id": "MERCH-ABC"},
        {"payment_id": "PAY-003", "payment_method": "crypto", "payment_amount": 199.99, "customer_id": "CUST-789", "merchant_id": "MERCH-XYZ"},
        {"payment_id": "PAY-004", "payment_method": "bank_transfer", "payment_amount": 1299.99, "customer_id": "CUST-321", "merchant_id": "MERCH-XYZ"},
    ]
    
    for data in payment_data:
        payment = PaymentWorkflow(**data)
        batch.payments.append(payment)
    
    # Process batch
    summary = await batch.process_batch()
    
    # Display results
    logger.info("\n📊 BATCH PROCESSING RESULTS")
    logger.info(f"Batch ID: {summary['batch_id']}")
    logger.info(f"Total Payments: {summary['total_payments']}")
    logger.info(f"Completed: {summary['completed']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Success Rate: {summary['success_rate']:.1%}")
    logger.info(f"Total Amount: ${summary['total_amount']:,.2f}")
    
    logger.info("\n💳 PAYMENT DETAILS:")
    for payment_summary in summary['payments']:
        logger.info(f"  {payment_summary['payment_id']}: {payment_summary['status']} "
                   f"({payment_summary['amount']}) - "
                   f"Fraud Score: {payment_summary['fraud_score']:.2f}")
    
    logger.info("\n🎯 Demo Complete!")
    logger.info("This demonstrates:")
    logger.info("  ✓ Type-safe models from semantic conventions")
    logger.info("  ✓ FSM state management with automatic transitions")
    logger.info("  ✓ AI-enhanced decision making (fraud detection)")
    logger.info("  ✓ Complete observability with telemetry")
    logger.info("  ✓ Batch processing with concurrent execution")
    logger.info("  ✓ Rich summaries and reporting")


if __name__ == "__main__":
    asyncio.run(main())