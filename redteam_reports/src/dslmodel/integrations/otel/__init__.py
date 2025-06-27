"""
OpenTelemetry integration for DSLModel

This module provides OpenTelemetry semantic convention models and utilities
generated using Weaver Forge, including workflow orchestration and FSM integration.
"""
from .weaver_integration import WeaverForgeIntegration

# Import generated models
try:
    from .models.dslmodel_attributes import DslmodelAttributes
    from .metrics.dslmodel_metrics import DslmodelMetricsMetric
    __all__ = ["WeaverForgeIntegration", "DslmodelAttributes", "DslmodelMetricsMetric"]
except ImportError:
    __all__ = ["WeaverForgeIntegration"]