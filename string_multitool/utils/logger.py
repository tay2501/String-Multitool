"""
Logging configuration module for String_Multitool.

This module provides centralized logging configuration based on PEP 282
and Python's official logging documentation.

Reference:
- PEP 282: A Logging System
- Python Official Documentation: logging module
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, TextIO


class LoggerManager:
    """Centralized logger management for String_Multitool.
    
    This class provides a standardized logging configuration system
    that follows Python's logging best practices.
    """
    
    _instance: LoggerManager | None = None
    _initialized: bool = False
    
    def __new__(cls) -> LoggerManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not self._initialized:
            self._configure_logging()
            LoggerManager._initialized = True
    
    def _configure_logging(self) -> None:
        """Configure logging system with default settings."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler for user-facing messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(message)s'  # Simple format for console output
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for detailed logging
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "string_multitool.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a configured logger instance.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Configured logger instance
        """
        # Ensure LoggerManager is initialized
        LoggerManager()
        return logging.getLogger(name)
    
    @staticmethod
    def set_log_level(level: str | int) -> None:
        """Set the logging level for all loggers.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Update all handlers
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and getattr(handler, 'stream', None) == sys.stdout:
                # Keep console handler at INFO or higher
                handler.setLevel(max(level, logging.INFO))
            else:
                handler.setLevel(level)
    
    @staticmethod
    def add_file_handler(file_path: str | Path, level: str | int = logging.DEBUG) -> None:
        """Add an additional file handler.
        
        Args:
            file_path: Path to log file
            level: Logging level for this handler
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    @staticmethod
    def configure_from_config(config: dict[str, Any]) -> None:
        """Configure logging from configuration dictionary.
        
        Args:
            config: Logging configuration dictionary
        """
        log_config = config.get('logging', {})
        
        # Set log level
        if 'level' in log_config:
            LoggerManager.set_log_level(log_config['level'])
        
        # Add additional file handlers
        if 'additional_files' in log_config:
            for file_config in log_config['additional_files']:
                LoggerManager.add_file_handler(
                    file_config['path'],
                    file_config.get('level', logging.DEBUG)
                )


# Convenience functions for common logging operations
def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return LoggerManager.get_logger(name)


def log_info(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    """Log an info message with optional extra context.
    
    Args:
        logger: Logger instance
        message: Log message
        **kwargs: Additional context data
    """
    if kwargs:
        logger.info(f"{message} - Context: {kwargs}")
    else:
        logger.info(message)


def log_error(logger: logging.Logger, message: str, exc_info: bool = True, **kwargs: Any) -> None:
    """Log an error message with optional exception info.
    
    Args:
        logger: Logger instance
        message: Error message
        exc_info: Include exception traceback
        **kwargs: Additional context data
    """
    if kwargs:
        logger.error(f"{message} - Context: {kwargs}", exc_info=exc_info)
    else:
        logger.error(message, exc_info=exc_info)


def log_warning(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    """Log a warning message with optional extra context.
    
    Args:
        logger: Logger instance
        message: Warning message
        **kwargs: Additional context data
    """
    if kwargs:
        logger.warning(f"{message} - Context: {kwargs}")
    else:
        logger.warning(message)


def log_debug(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    """Log a debug message with optional extra context.
    
    Args:
        logger: Logger instance
        message: Debug message
        **kwargs: Additional context data
    """
    if kwargs:
        logger.debug(f"{message} - Context: {kwargs}")
    else:
        logger.debug(message)