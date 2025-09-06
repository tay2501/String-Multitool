"""
Unified logging system using structlog for String_Multitool.

This module provides a single, simple interface for all logging needs,
replacing the complex multiple logging implementations with structlog.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, List, Union

import structlog
from structlog import stdlib
from structlog.processors import JSONRenderer, TimeStamper
from structlog.types import Processor


def configure_logging(level: str = "INFO", json_output: bool = False) -> None:
    """Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_output: Whether to output JSON format logs
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure stdlib logging to work with structlog
    import logging
    import logging.handlers

    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "string_multitool.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )

    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout), file_handler],
    )

    # Configure structlog processors
    processors: List[Processor] = [
        stdlib.filter_by_level,
        stdlib.add_logger_name,
        stdlib.add_log_level,
        stdlib.PositionalArgumentsFormatter(),
        TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
    ]

    if json_output:
        processors.append(JSONRenderer())
    else:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(colors=True),
                stdlib.ProcessorFormatter.wrap_for_formatter,
            ]
        )

    structlog.configure(
        processors=processors,
        logger_factory=stdlib.LoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)  # type: ignore[no-any-return]


def log_with_context(
    logger: structlog.stdlib.BoundLogger,
    level: str,
    message: str,
    **context: Any,
) -> None:
    """Log a message with structured context.

    Args:
        logger: Structured logger instance
        level: Log level (info, warning, error, debug)
        message: Log message
        **context: Additional context fields
    """
    try:
        log_method = getattr(logger, level.lower())
        log_method(message, **context)
    except AttributeError:
        logger.error(f"Invalid log level: {level}", message=message, **context)


# Convenience functions for backward compatibility
def log_debug(logger: structlog.stdlib.BoundLogger, message: str, **kwargs: Any) -> None:
    """Log debug message with context."""
    log_with_context(logger, "debug", message, **kwargs)


def log_info(logger: structlog.stdlib.BoundLogger, message: str, **kwargs: Any) -> None:
    """Log info message with context."""
    log_with_context(logger, "info", message, **kwargs)


def log_warning(logger: structlog.stdlib.BoundLogger, message: str, **kwargs: Any) -> None:
    """Log warning message with context."""
    log_with_context(logger, "warning", message, **kwargs)


def log_error(logger: structlog.stdlib.BoundLogger, message: str, **kwargs: Any) -> None:
    """Log error message with context."""
    log_with_context(logger, "error", message, **kwargs)


# Initialize logging on module import
try:
    configure_logging()
except Exception:
    # Fallback configuration
    import logging

    logging.basicConfig(level=logging.INFO)
