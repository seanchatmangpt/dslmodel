# """dslmodel."""
import warnings
from .models import DSLModel
from .utils.dspy_tools import init_lm, init_text, init_instant
from .generators.dsl_class_generator import DSLClassGenerator

#
# # Ignore all DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
#

