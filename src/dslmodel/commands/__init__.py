"""DSLModel command modules."""

# Import all command modules to make them available
# from . import asyncapi  # Commented out to avoid OpenAI API key requirement
# from . import coordination_cli  # Commented out to avoid dependency issues
from . import forge
from . import autonomous
from . import slidev
from . import swarm_simple as swarm

# Import OTEL coordination if available
try:
    from . import otel_coordination
except ImportError:
    # OTEL dependencies not available
    pass

__all__ = [
    # "asyncapi",
    "coordination_cli", 
    "forge",
    "autonomous",
    "slidev",
    "swarm",
    "otel_coordination"
]
