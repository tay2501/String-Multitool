"""
Transformation coordinator for String_Multitool.

This module provides a centralized coordinator that manages different
transformation components following the single responsibility principle
and loose coupling patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types import ConfigManagerProtocol, CryptoManagerProtocol

from ..exceptions import TransformationError, ValidationError
from .constants import ERROR_CONTEXT_KEYS, VALIDATION_CONSTANTS
from .crypto_transformations import CryptoTransformations
from .hash_transformations import HashTransformations
from .text_format_transformations import TextFormatTransformations
from .transformation_base import TransformationBase
from .types import ConfigurableComponent


class TransformationCoordinator(ConfigurableComponent[dict[str, Any]], TransformationBase):
    """Central coordinator for all transformation operations.

    This class coordinates between different transformation components
    while maintaining loose coupling and single responsibility principles.
    It acts as a facade pattern implementation for transformation operations.
    """

    def __init__(self, config_manager: ConfigManagerProtocol) -> None:
        """Initialize transformation coordinator with dependency injection.

        Args:
            config_manager: Configuration manager for loading rules and settings

        Raises:
            ValidationError: If configuration manager is invalid
            TransformationError: If initialization fails
        """
        try:
            # EAFP: Try to load configuration
            transformation_config = config_manager.load_transformation_rules()

            # Initialize parent classes
            ConfigurableComponent.__init__(self, transformation_config)
            TransformationBase.__init__(self, transformation_config)

            # Initialize transformation components with dependency injection
            self.crypto_transformations = CryptoTransformations()
            self.hash_transformations = HashTransformations(transformation_config)
            self.text_format_transformations = TextFormatTransformations(transformation_config)

            # Store config manager for future use
            self.config_manager = config_manager

        except (ValidationError, TransformationError):
            # Re-raise expected exceptions
            raise
        except Exception as e:
            raise TransformationError(
                f"Failed to initialize transformation coordinator: {e}",
                {
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                    "config_manager_type": type(config_manager).__name__,
                },
            ) from e

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set cryptography manager for encryption/decryption operations.

        Args:
            crypto_manager: Cryptography manager instance
        """
        self.crypto_transformations.set_crypto_manager(crypto_manager)

    def transform(self, text: str) -> str:
        """Base transformation method (identity transformation).

        Args:
            text: Input text

        Returns:
            Unchanged text (for base class compatibility)
        """
        return text

    def apply_crypto_transformation(self, text: str, operation: str) -> str:
        """Apply cryptographic transformation.

        Args:
            text: Input text
            operation: Crypto operation (encrypt, decrypt, encode, decode)

        Returns:
            Transformed text

        Raises:
            TransformationError: If transformation fails
        """
        try:
            return self.crypto_transformations.transform(text, operation)
        except Exception as e:
            raise TransformationError(
                f"Crypto transformation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: operation,
                    ERROR_CONTEXT_KEYS.COMPONENT: "crypto_transformations",
                },
            ) from e

    def apply_hash_transformation(self, text: str, algorithm: str = "sha256") -> str:
        """Apply hash transformation.

        Args:
            text: Input text
            algorithm: Hash algorithm to use

        Returns:
            Hash string

        Raises:
            TransformationError: If transformation fails
        """
        try:
            return self.hash_transformations.transform(text, algorithm)
        except Exception as e:
            raise TransformationError(
                f"Hash transformation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.ALGORITHM: algorithm,
                    ERROR_CONTEXT_KEYS.COMPONENT: "hash_transformations",
                },
            ) from e

    def apply_text_format_transformation(self, text: str, operation: str) -> str:
        """Apply text format transformation.

        Args:
            text: Input text
            operation: Format operation (trim, pascal, camel, snake, etc.)

        Returns:
            Formatted text

        Raises:
            TransformationError: If transformation fails
        """
        try:
            return self.text_format_transformations.transform(text, operation)
        except Exception as e:
            raise TransformationError(
                f"Text format transformation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: operation,
                    ERROR_CONTEXT_KEYS.COMPONENT: "text_format_transformations",
                },
            ) from e

    def apply_transformations_by_rule(
        self, text: str, rule_name: str, args: list[str] | None = None
    ) -> str:
        """Apply transformation based on rule name and arguments.

        This method provides a unified interface for applying transformations
        while delegating to appropriate specialized components.

        Args:
            text: Input text to transform
            rule_name: Name of the transformation rule
            args: Optional arguments for the transformation

        Returns:
            Transformed text

        Raises:
            ValidationError: If inputs are invalid
            TransformationError: If transformation fails
        """
        try:
            # Input validation using EAFP
            if not self.validate_input(text):
                raise ValidationError(
                    VALIDATION_CONSTANTS.INVALID_INPUT_TYPE_MSG.format(
                        type_name=type(text).__name__
                    ),
                    {ERROR_CONTEXT_KEYS.TEXT_TYPE: type(text).__name__},
                )

            if not isinstance(rule_name, str) or not rule_name.strip():
                raise ValidationError(
                    "Rule name must be a non-empty string",
                    {"rule_name": rule_name, "rule_type": type(rule_name).__name__},
                )

            args = args or []

            # Route to appropriate transformation component
            if rule_name in {"encrypt", "decrypt"} or rule_name in {"encode", "decode"}:
                return self.apply_crypto_transformation(text, rule_name)
            elif rule_name in {"sha256", "sha1", "sha512", "md5"}:
                return self.apply_hash_transformation(text, rule_name)
            elif rule_name in {
                "trim",
                "pascal",
                "camel",
                "snake",
                "full_to_half",
                "half_to_full",
                "sql_in",
            }:
                return self.apply_text_format_transformation(text, rule_name)
            elif rule_name == "replace" and len(args) >= 2:
                return self.text_format_transformations.replace_text(text, args[0], args[1])
            elif rule_name == "regex_replace" and len(args) >= 2:
                return self.text_format_transformations.regex_replace(text, args[0], args[1])
            else:
                # Fallback to basic string operations
                return self._apply_basic_transformation(text, rule_name, args)

        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            raise TransformationError(
                f"Rule-based transformation failed: {e}",
                {
                    "rule_name": rule_name,
                    "args_count": len(args) if args else 0,
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                },
            ) from e

    def _apply_basic_transformation(self, text: str, rule_name: str, args: list[str]) -> str:
        """Apply basic string transformations.

        Args:
            text: Input text
            rule_name: Rule name
            args: Rule arguments

        Returns:
            Transformed text

        Raises:
            TransformationError: If transformation fails
        """
        try:
            # Basic case transformations
            if rule_name == "lower" or rule_name == "l":
                return text.lower()
            elif rule_name == "upper" or rule_name == "u":
                return text.upper()
            elif rule_name == "title":
                return text.title()
            elif rule_name == "capitalize":
                return text.capitalize()
            elif rule_name == "swapcase":
                return text.swapcase()
            elif rule_name == "reverse":
                return text[::-1]
            else:
                raise TransformationError(
                    f"Unknown transformation rule: {rule_name}",
                    {"rule_name": rule_name, "available_rules": self.get_available_basic_rules()},
                )

        except Exception as e:
            raise TransformationError(
                f"Basic transformation failed: {e}",
                {
                    "rule_name": rule_name,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def get_available_basic_rules(self) -> list[str]:
        """Get list of available basic transformation rules.

        Returns:
            List of rule names
        """
        return [
            "lower",
            "l",
            "upper",
            "u",
            "title",
            "capitalize",
            "swapcase",
            "reverse",
            "trim",
            "pascal",
            "camel",
            "snake",
            "replace",
            "regex_replace",
            "encode",
            "decode",
            "encrypt",
            "decrypt",
            "sha256",
            "sha1",
            "sha512",
            "md5",
            "full_to_half",
            "half_to_full",
            "sql_in",
        ]

    def get_component_status(self) -> dict[str, bool]:
        """Get status of transformation components.

        Returns:
            Dictionary with component names and their availability status
        """
        return {
            "crypto_transformations": self.crypto_transformations is not None,
            "hash_transformations": self.hash_transformations is not None,
            "text_format_transformations": self.text_format_transformations is not None,
            "crypto_manager_available": (
                self.crypto_transformations.crypto_manager is not None
                if self.crypto_transformations
                else False
            ),
        }
