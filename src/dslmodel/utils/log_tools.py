import logging
import sys
from pathlib import Path
from contextlib import contextmanager
from loguru import logger
from typing import Optional, Any

from dslmodel.utils.file_tools import data_dir

# Define log formats
LOG_FORMAT_DETAILED = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

LOG_FORMAT_JSON = (
    "{{"
    '"timestamp": "{time:YYYY-MM-DDTHH:mm:ss.SSSZ}", '
    '"level": "{level}", '
    '"module": "{name}", '
    '"function": "{function}", '
    '"line": "{line}", '
    '"message": "{message}"'
    "}}"
)

LOG_FORMAT_SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>"

# Singleton pattern for logger initialization
_is_logger_initialized = False


def init_log(
        log_level: str = "INFO",
        log_format: str = LOG_FORMAT_DETAILED,
        log_file: str = "application.log",
        rotation: str = "1 week",
        retention: str = "1 month",
        serialize: bool = False,
):
    """
    Initialize the logger with specific configurations for file and console logging.
    :param log_level: Logging level (e.g., "DEBUG", "INFO", "ERROR").
    :param log_format: Format for the log messages.
    :param log_file: File name for saving logs.
    :param rotation: File rotation policy.
    :param retention: Log retention policy.
    :param serialize: If True, logs are serialized as JSON.
    """
    global _is_logger_initialized

    if _is_logger_initialized:
        return logger  # Avoid re-initializing

    logger.remove()  # Clear any existing handlers

    # Log to console
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        serialize=serialize,
    )

    # Log to file
    log_file_path = data_dir() / log_file
    logger.add(
        log_file_path,
        format=log_format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        serialize=serialize,
    )

    _is_logger_initialized = True
    return logger


# Helper functions for logging different levels
def log_info(message: str, **kwargs: Any):
    init_log()
    logger.info(message, **kwargs)


def log_debug(message: str, **kwargs: Any):
    init_log(log_level="DEBUG")
    logger.debug(message, **kwargs)


def log_warning(message: str, **kwargs: Any):
    init_log(log_level="WARNING")
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs: Any):
    init_log(log_level="ERROR")
    logger.error(message, **kwargs)


def log_critical(message: str, **kwargs: Any):
    init_log(log_level="CRITICAL")
    logger.critical(message, **kwargs)


def log_exception(message: str, **kwargs: Any):
    """
    Log an exception with a traceback.
    Should be called inside an `except` block.
    """
    init_log(log_level="ERROR")
    logger.exception(message, **kwargs)
