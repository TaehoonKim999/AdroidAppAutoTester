"""
Logging utilities for Android App Auto Tester.

Provides standardized logging setup with console and file handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# Log format with timestamp, level, module, and message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log level
DEFAULT_LEVEL = logging.INFO


def setup_logger(
    name: str,
    level: int = DEFAULT_LEVEL,
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (typically module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        console: Whether to also log to console

    Returns:
        Configured logger instance

    Example:
        logger = setup_logger(__name__)
        logger.info("Starting test")
        logger.error("Test failed", exc_info=True)
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str, level: int = DEFAULT_LEVEL) -> logging.Logger:
    """
    Get or create a logger with standard configuration.

    This is a convenience function that creates a logger with console output only.
    For file logging, use setup_logger() directly.

    Args:
        name: Logger name (typically __name__)
        level: Logging level

    Returns:
        Logger instance
    """
    return setup_logger(name, level=level, console=True)


def get_session_logger(
    name: str,
    session_id: Optional[str] = None,
    level: int = DEFAULT_LEVEL
) -> logging.Logger:
    """
    Get logger with automatic file output for test sessions.

    Creates a log file in logs/ directory with timestamp and session ID.

    Args:
        name: Logger name
        session_id: Optional session identifier
        level: Logging level

    Returns:
        Logger instance with file handler
    """
    # Import here to avoid circular dependency
    from ..platform_utils import get_platform_utils

    platform_utils = get_platform_utils()
    logs_dir = platform_utils.get_path("logs")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if session_id:
        log_file = logs_dir / f"{session_id}_{timestamp}.log"
    else:
        log_file = logs_dir / f"session_{timestamp}.log"

    return setup_logger(name, level=level, log_file=log_file, console=True)


def set_log_level(logger: logging.Logger, level: int):
    """
    Update log level for logger and all its handlers.

    Args:
        logger: Logger instance
        level: New logging level
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def debug_mode(logger: logging.Logger):
    """Enable DEBUG level logging for a logger."""
    set_log_level(logger, logging.DEBUG)


def quiet_mode(logger: logging.Logger):
    """Enable ERROR level logging only for a logger."""
    set_log_level(logger, logging.ERROR)
