"""DSLModel admitted public API.

Historical framework exports were previously lazy-loaded from modules that are
not part of the production dependency closure. The package root now exposes
only executable, dependency-closed capabilities; legacy source remains in Git
history and the repository audit, not as ambient import authority.
"""

from __future__ import annotations

from pydantic import Field

from .capabilities import (
    CapabilityReceipt,
    CapabilityRegistry,
    CapabilitySpec,
    CapabilityStanding,
    artifact_receipt,
    verify_artifact_receipt,
)
from .generators.openapi_models import (
    OpenAPIGenerationError,
    OpenAPIModelGenerator,
    generate_openapi_models,
    load_openapi,
)

__all__ = [
    "Field",
    "CapabilityStanding",
    "CapabilitySpec",
    "CapabilityReceipt",
    "CapabilityRegistry",
    "artifact_receipt",
    "verify_artifact_receipt",
    "OpenAPIGenerationError",
    "OpenAPIModelGenerator",
    "load_openapi",
    "generate_openapi_models",
]
