"""DSLModel command modules."""

# Import all command modules to make them available
# from . import asyncapi  # Commented out to avoid OpenAI API key requirement
# from . import coordination_cli  # Commented out to avoid dependency issues
from . import forge
from . import autonomous
from . import slidev
from . import swarm
from . import thesis_cli
from . import demo
from . import transformation_cli
from . import git_auto_cli

# Import OTEL coordination if available
try:
    from . import otel_coordination_cli
    OTEL_AVAILABLE = True
except ImportError:
    # OTEL dependencies not available
    OTEL_AVAILABLE = False

__all__ = [
    # "asyncapi",
    "coordination_cli", 
    "forge",
    "autonomous",
    "slidev",
    "swarm",
    "thesis_cli",
    "demo",
    "transformation_cli",
    "git_auto_cli"
]

# Add OTEL coordination if available
if OTEL_AVAILABLE:
    __all__.append("otel_coordination_cli")
