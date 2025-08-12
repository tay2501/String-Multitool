"""
Enhanced error handling and logging infrastructure.

This module provides structured error handling, centralized logging,
and error recovery mechanisms following modern Python best practices.
"""

from __future__ import annotations

import sys
import traceback
import contextvars
from collections.abc import Callable, Mapping, Any as AnyMapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar, Generic
from typing_extensions import ParamSpec

from ..exceptions import StringMultitoolError

T = TypeVar('T')
P = ParamSpec('P')

# Context variable for request ID tracking
request_context: contextvars.ContextVar[str] = contextvars.ContextVar('request_id', default='')


class ErrorSeverity(Enum):
    """Error severity levels for structured error reporting."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors for better classification."""
    
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    TRANSFORMATION = "transformation"
    CRYPTOGRAPHY = "cryptography"
    IO_OPERATION = "io_operation"
    DEPENDENCY_INJECTION = "dependency_injection"
    SYSTEM_RESOURCE = "system_resource"
    EXTERNAL_SERVICE = "external_service"
    USER_INPUT = "user_input"
    INTERNAL_ERROR = "internal_error"


class ErrorContext:
    """Structured context information for errors."""
    
    def __init__(
        self,
        operation: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: str | None = None,
        technical_details: dict[str, Any] | None = None,
        recovery_suggestions: list[str] | None = None,
        correlation_id: str | None = None
    ) -> None:
        """Initialize error context."""
        self.operation = operation
        self.category = category
        self.severity = severity
        self.user_message = user_message
        self.technical_details = technical_details or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.correlation_id = correlation_id or request_context.get()
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert error context to dictionary for logging."""
        return {
            "operation": self.operation,
            "category": self.category.value,
            "severity": self.severity.value,
            "user_message": self.user_message,
            "technical_details": self.technical_details,
            "recovery_suggestions": self.recovery_suggestions,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat()
        }


class StructuredError(StringMultitoolError):
    """Enhanced error with structured context information."""
    
    def __init__(
        self,
        message: str,
        context: ErrorContext,
        cause: Exception | None = None
    ) -> None:
        """Initialize structured error."""
        super().__init__(message, context.technical_details)
        self.context = context
        self.cause = cause
    
    @property
    def user_friendly_message(self) -> str:
        """Get user-friendly error message."""
        return self.context.user_message or str(self)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if error has recovery suggestions."""
        return len(self.context.recovery_suggestions) > 0
    
    def get_formatted_details(self) -> dict[str, Any]:
        """Get formatted error details for logging."""
        details = {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "context": self.context.to_dict()
        }
        
        if self.cause:
            details["cause"] = {
                "type": self.cause.__class__.__name__,
                "message": str(self.cause),
                "traceback": traceback.format_exception(\n                    type(self.cause),\n                    self.cause,\n                    self.cause.__traceback__\n                )\n            }\n        \n        return details\n\n\nclass ErrorHandler:\n    \"\"\"Centralized error handler with recovery mechanisms.\"\"\"\n    \n    def __init__(self) -> None:\n        \"\"\"Initialize error handler.\"\"\"\n        self._error_listeners: list[Callable[[StructuredError], None]] = []\n        self._recovery_strategies: dict[ErrorCategory, list[Callable[[StructuredError], bool]]] = {}\n    \n    def add_error_listener(self, listener: Callable[[StructuredError], None]) -> None:\n        \"\"\"Add error event listener.\"\"\"\n        self._error_listeners.append(listener)\n    \n    def add_recovery_strategy(\n        self,\n        category: ErrorCategory,\n        strategy: Callable[[StructuredError], bool]\n    ) -> None:\n        \"\"\"Add recovery strategy for specific error category.\"\"\"\n        if category not in self._recovery_strategies:\n            self._recovery_strategies[category] = []\n        self._recovery_strategies[category].append(strategy)\n    \n    def handle_error(\n        self,\n        error: StructuredError,\n        *,\n        attempt_recovery: bool = True\n    ) -> bool:\n        \"\"\"Handle error with optional recovery attempt.\"\"\"\n        # Notify listeners\n        for listener in self._error_listeners:\n            try:\n                listener(error)\n            except Exception:\n                # Don't let listener errors break error handling\n                pass\n        \n        # Attempt recovery if requested\n        if attempt_recovery and error.context.category in self._recovery_strategies:\n            strategies = self._recovery_strategies[error.context.category]\n            for strategy in strategies:\n                try:\n                    if strategy(error):\n                        return True  # Recovery successful\n                except Exception:\n                    # Recovery strategy failed, continue to next\n                    pass\n        \n        return False  # No recovery possible\n    \n    def create_structured_error(\n        self,\n        message: str,\n        operation: str,\n        category: ErrorCategory,\n        *,\n        severity: ErrorSeverity = ErrorSeverity.MEDIUM,\n        user_message: str | None = None,\n        technical_details: dict[str, Any] | None = None,\n        recovery_suggestions: list[str] | None = None,\n        cause: Exception | None = None\n    ) -> StructuredError:\n        \"\"\"Create structured error with context.\"\"\"\n        context = ErrorContext(\n            operation=operation,\n            category=category,\n            severity=severity,\n            user_message=user_message,\n            technical_details=technical_details,\n            recovery_suggestions=recovery_suggestions\n        )\n        \n        return StructuredError(message, context, cause)\n\n\nclass RetryStrategy:\n    \"\"\"Configurable retry strategy for error recovery.\"\"\"\n    \n    def __init__(\n        self,\n        max_attempts: int = 3,\n        delay_seconds: float = 1.0,\n        exponential_backoff: bool = True,\n        max_delay: float = 30.0\n    ) -> None:\n        \"\"\"Initialize retry strategy.\"\"\"\n        self.max_attempts = max_attempts\n        self.delay_seconds = delay_seconds\n        self.exponential_backoff = exponential_backoff\n        self.max_delay = max_delay\n    \n    def execute(\n        self,\n        operation: Callable[[], T],\n        *,\n        operation_name: str = \"unknown\",\n        category: ErrorCategory = ErrorCategory.INTERNAL_ERROR\n    ) -> T:\n        \"\"\"Execute operation with retry logic.\"\"\"\n        import time\n        \n        last_exception: Exception | None = None\n        delay = self.delay_seconds\n        \n        for attempt in range(1, self.max_attempts + 1):\n            try:\n                return operation()\n            except Exception as e:\n                last_exception = e\n                \n                if attempt == self.max_attempts:\n                    # Final attempt failed\n                    break\n                \n                # Wait before retry\n                time.sleep(min(delay, self.max_delay))\n                \n                if self.exponential_backoff:\n                    delay *= 2\n        \n        # All attempts failed, create structured error\n        error_handler = get_error_handler()\n        structured_error = error_handler.create_structured_error(\n            f\"Operation '{operation_name}' failed after {self.max_attempts} attempts\",\n            operation_name,\n            category,\n            cause=last_exception,\n            technical_details={\"max_attempts\": self.max_attempts, \"last_attempt\": attempt}\n        )\n        \n        raise structured_error\n\n\ndef with_error_context(\n    operation: str,\n    category: ErrorCategory,\n    *,\n    severity: ErrorSeverity = ErrorSeverity.MEDIUM,\n    user_message: str | None = None,\n    recovery_suggestions: list[str] | None = None\n) -> Callable[[Callable[P, T]], Callable[P, T]]:\n    \"\"\"Decorator to add error context to function calls.\"\"\"\n    \n    def decorator(func: Callable[P, T]) -> Callable[P, T]:\n        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:\n            try:\n                return func(*args, **kwargs)\n            except StructuredError:\n                # Already structured, re-raise\n                raise\n            except Exception as e:\n                # Convert to structured error\n                error_handler = get_error_handler()\n                structured_error = error_handler.create_structured_error(\n                    f\"Error in {operation}: {e}\",\n                    operation,\n                    category,\n                    severity=severity,\n                    user_message=user_message,\n                    recovery_suggestions=recovery_suggestions,\n                    cause=e\n                )\n                raise structured_error from e\n        \n        return wrapper\n    return decorator\n\n\ndef safe_execute(\n    operation: Callable[[], T],\n    *,\n    operation_name: str = \"unknown\",\n    category: ErrorCategory = ErrorCategory.INTERNAL_ERROR,\n    default_value: T | None = None,\n    log_errors: bool = True\n) -> T | None:\n    \"\"\"Safely execute operation with error handling.\"\"\"\n    try:\n        return operation()\n    except Exception as e:\n        if log_errors:\n            from ..utils.logger import get_logger, log_error\n            logger = get_logger(__name__)\n            log_error(logger, f\"Error in {operation_name}: {e}\")\n        \n        return default_value\n\n\n# Global error handler instance\n_global_error_handler: ErrorHandler | None = None\n\n\ndef get_error_handler() -> ErrorHandler:\n    \"\"\"Get global error handler instance.\"\"\"\n    global _global_error_handler\n    if _global_error_handler is None:\n        _global_error_handler = ErrorHandler()\n    return _global_error_handler\n\n\ndef configure_error_handling(\n    *,\n    log_file: Path | None = None,\n    console_logging: bool = True,\n    structured_logging: bool = True\n) -> None:\n    \"\"\"Configure global error handling settings.\"\"\"\n    error_handler = get_error_handler()\n    \n    # Add default error listeners\n    if console_logging:\n        def console_error_listener(error: StructuredError) -> None:\n            details = error.get_formatted_details()\n            print(f\"[ERROR] {details['message']}\", file=sys.stderr)\n            if error.context.severity in (ErrorSeverity.HIGH, ErrorSeverity.CRITICAL):\n                print(f\"[ERROR] Context: {error.context.to_dict()}\", file=sys.stderr)\n        \n        error_handler.add_error_listener(console_error_listener)\n    \n    if log_file and structured_logging:\n        def file_error_listener(error: StructuredError) -> None:\n            import json\n            from ..utils.logger import get_logger, log_error\n            \n            logger = get_logger(__name__)\n            details = error.get_formatted_details()\n            log_error(logger, json.dumps(details, indent=2))\n        \n        error_handler.add_error_listener(file_error_listener)"}]