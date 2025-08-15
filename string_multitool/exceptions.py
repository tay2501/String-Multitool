"""
Custom exceptions for String_Multitool.

This module defines the exception hierarchy for the application,
providing specific error types for different failure scenarios.
"""

from __future__ import annotations

from typing import Any


class StringMultitoolError(Exception):
    """Base exception for String_Multitool.

    All custom exceptions in the application should inherit from this class.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details: dict[str, Any] = details or {}


class ConfigurationError(StringMultitoolError):
    """Configuration related errors.

    Raised when there are issues with loading or parsing configuration files.
    """

    pass


class TransformationError(StringMultitoolError):
    """Transformation related errors.

    Raised when text transformation operations fail.
    """

    pass


class CryptographyError(StringMultitoolError):
    """Cryptography related errors.

    Raised when encryption/decryption operations fail.
    """

    pass


class ClipboardError(StringMultitoolError):
    """Clipboard related errors.

    Raised when clipboard operations fail.
    """

    pass


class ValidationError(StringMultitoolError):
    """Input validation errors.

    Raised when input data fails validation checks.
    """

    pass
