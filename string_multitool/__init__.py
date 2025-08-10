"""
String_Multitool - Advanced text transformation tool.

A powerful command-line text transformation tool with intuitive rule-based syntax,
pipe support, and secure RSA encryption capabilities.
"""

from __future__ import annotations

from .exceptions import (
    StringMultitoolError,
    ConfigurationError,
    TransformationError,
    CryptographyError,
    ClipboardError,
    ValidationError,
)

from .core.types import (
    TransformationRule,
    SessionState,
    CommandResult,
    TextSource,
    TransformationRuleType,
    ConfigManagerProtocol,
    IOManagerProtocol,
    TransformationEngineProtocol,
    CryptoManagerProtocol,
)

from .core.config import ConfigurationManager
from .core.crypto import CryptographyManager
from .core.transformations import TextTransformationEngine

from .io.manager import InputOutputManager
from .io.clipboard import ClipboardMonitor

__version__ = "2.1.0"
__author__ = "String_Multitool Development Team"

__all__ = [
    # Exceptions
    "StringMultitoolError",
    "ConfigurationError", 
    "TransformationError",
    "CryptographyError",
    "ClipboardError",
    "ValidationError",
    
    # Types and Protocols
    "TransformationRule",
    "SessionState",
    "CommandResult",
    "TextSource",
    "TransformationRuleType",
    "ConfigManagerProtocol",
    "IOManagerProtocol", 
    "TransformationEngineProtocol",
    "CryptoManagerProtocol",
    
    # Core Components
    "ConfigurationManager",
    "CryptographyManager",
    "TextTransformationEngine",
    
    # I/O Components
    "InputOutputManager",
    "ClipboardMonitor",
]