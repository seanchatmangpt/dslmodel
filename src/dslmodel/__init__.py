# """dslmodel."""
import warnings

# from .generators.dsl_class_generator import DSLClassGenerator
from .dsl_models import DSLModel
from .template import render
from .utils.log_tools import init_log, log_warning, log_info, log_debug, log_error, log_critical, log_exception, logger
from .readers.data_reader import DataReader
from .utils.dspy_tools import init_instant, init_lm, init_text
from .writers.data_writer import DataWriter
from pydantic import Field
from .utils.model_tools import run_dsls, from_prompt_chain

init_text()

#
# # Ignore all DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
