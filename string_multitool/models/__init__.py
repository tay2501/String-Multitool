"""
Core components for String_Multitool.
"""

from .config import ConfigurationManager
from .crypto import CryptographyManager
from .transformations import TextTransformationEngine
from .types import (
    CommandResult,
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    SessionState,
    TextSource,
    TransformationEngineProtocol,
    TransformationRule,
    TransformationRuleType,
)

__all__ = [
    "ConfigurationManager",
    "CryptographyManager",
    "TextTransformationEngine",
    "TransformationRule",
    "SessionState",
    "CommandResult",
    "TextSource",
    "TransformationRuleType",
    "ConfigManagerProtocol",
    "TransformationEngineProtocol",
    "CryptoManagerProtocol",
]
