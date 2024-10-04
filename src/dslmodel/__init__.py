# """dslmodel."""
import warnings
from .models import DSLModel
from .utils.dspy_tools import init_lm, init_text, init_instant

#
# # Ignore all DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
#

#
# # from confz import BaseConfig, TomlSource
# from typing import Optional
#
# class LMConfig(BaseConfig):
#     model: str = "openai/gpt-4o-mini"
#     api_key: Optional[str] = None
#     api_base: Optional[str] = None
#     temperature: float = 0.0
#     max_tokens: int = 1000
#     cache: bool = True
#     model_type: Optional[str] = "text"
#     stop: Optional[list] = None
#     experimental: bool = True
#
#     # Load configuration from pyproject.toml, specifically from the [tool.lmconfig] section
#     CONFIG_SOURCES = TomlSource(file="pyproject.toml", section="tool.lmconfig")
#
# # Global config instance
# lm_config: Optional[LMConfig] = None
#
# def load_lm_config():
#     global lm_config
#     if lm_config is None:
#         lm_config = LMConfig()  # This will load the config from pyproject.toml
