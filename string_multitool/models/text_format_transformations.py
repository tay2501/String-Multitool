"""
Text format transformation operations for String_Multitool.

This module provides dedicated text formatting transformation functionality
following the single responsibility principle and EAFP error handling pattern.
"""

from __future__ import annotations

import re
from typing import Any

from ..exceptions import TransformationError
from .constants import ERROR_CONTEXT_KEYS
from .transformation_base import TransformationBase


class TextFormatTransformations(TransformationBase):
    """Dedicated text format transformation operations handler.

    This class handles all text format operations including case conversion,
    width conversion, trimming, and string formatting with proper error handling.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize text format transformations.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config or {})
        self._input_text: str = ""
        self._output_text: str = ""
        self._transformation_rule: str = ""

    def transform(self, text: str, operation: str = "trim") -> str:
        """Apply text format transformation to text.

        Args:
            text: Input text to transform
            operation: Type of operation (trim, pascal, camel, snake, etc.)

        Returns:
            Transformed text

        Raises:
            TransformationError: If transformation fails
        """
        operation_map = {
            "trim": self.trim_text,
            "pascal": self.to_pascal_case,
            "camel": self.to_camel_case,
            "snake": self.to_snake_case,
            "full_to_half": self.full_to_half_width,
            "half_to_full": self.half_to_full_width,
            "sql_in": self.to_sql_in_clause,
        }

        try:
            self._input_text = text
            self._transformation_rule = operation

            if operation not in operation_map:
                raise TransformationError(
                    f"Unknown text format operation: {operation}",
                    {
                        ERROR_CONTEXT_KEYS.OPERATION: operation,
                        "available_operations": list(operation_map.keys()),
                    },
                )

            # EAFP: Try transformation directly
            result = operation_map[operation](text)
            self._output_text = result
            return result

        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(
                f"Text format transformation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: operation,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                },
            ) from e

    def trim_text(self, text: str) -> str:
        """Remove leading and trailing whitespace from text.

        Args:
            text: Input text to trim

        Returns:
            Trimmed text

        Raises:
            TransformationError: If trimming fails
        """
        try:
            # EAFP: Try trimming directly
            result = text.strip()

            # Additional whitespace normalization
            result = re.sub(r"\\s+", " ", result)

            return result

        except Exception as e:
            raise TransformationError(
                f"Text trimming failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "trim",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase.

        Args:
            text: Input text to convert

        Returns:
            PascalCase formatted text

        Raises:
            TransformationError: If conversion fails
        """
        try:
            # EAFP: Try conversion directly
            words = re.split(r"[\\s_-]+", text.strip())
            return "".join(word.capitalize() for word in words if word)

        except Exception as e:
            raise TransformationError(
                f"PascalCase conversion failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "pascal_case",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def to_camel_case(self, text: str) -> str:
        """Convert text to camelCase.

        Args:
            text: Input text to convert

        Returns:
            camelCase formatted text

        Raises:
            TransformationError: If conversion fails
        """
        try:
            # EAFP: Try conversion directly
            pascal_case = self.to_pascal_case(text)
            if not pascal_case:
                return ""
            return pascal_case[0].lower() + pascal_case[1:]

        except Exception as e:
            raise TransformationError(
                f"camelCase conversion failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "camel_case",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def to_snake_case(self, text: str) -> str:
        """Convert text to snake_case.

        Args:
            text: Input text to convert

        Returns:
            snake_case formatted text

        Raises:
            TransformationError: If conversion fails
        """
        try:
            # EAFP: Try conversion directly
            text = text.strip()

            # Handle camelCase and PascalCase
            text = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", text)
            text = re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", text)

            # Replace spaces and hyphens with underscores
            text = re.sub(r"[\\s-]+", "_", text)

            return text.lower()

        except Exception as e:
            raise TransformationError(
                f"snake_case conversion failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "snake_case",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def full_to_half_width(self, text: str) -> str:
        """Convert full-width characters to half-width.

        Args:
            text: Input text with full-width characters

        Returns:
            Text with half-width characters

        Raises:
            TransformationError: If conversion fails
        """
        try:
            # EAFP: Try conversion directly
            result = ""
            for char in text:
                # Convert full-width ASCII to half-width
                if "\\uff01" <= char <= "\\uff5e":  # Full-width ASCII range
                    result += chr(ord(char) - 0xFEE0)
                # Convert full-width space to half-width space
                elif char == "\\u3000":  # Full-width space
                    result += " "
                else:
                    result += char

            return result

        except Exception as e:
            raise TransformationError(
                f"Full-width to half-width conversion failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "full_to_half_width",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def half_to_full_width(self, text: str) -> str:
        """Convert half-width characters to full-width.

        Args:
            text: Input text with half-width characters

        Returns:
            Text with full-width characters

        Raises:
            TransformationError: If conversion fails
        """
        try:
            # EAFP: Try conversion directly
            result = ""
            for char in text:
                # Convert half-width ASCII to full-width
                if "!" <= char <= "~":  # Half-width ASCII range
                    result += chr(ord(char) + 0xFEE0)
                # Convert half-width space to full-width space
                elif char == " ":
                    result += "\\u3000"  # Full-width space
                else:
                    result += char

            return result

        except Exception as e:
            raise TransformationError(
                f"Half-width to full-width conversion failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "half_to_full_width",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def to_sql_in_clause(self, text: str) -> str:
        """Convert comma-separated values to SQL IN clause format.

        Args:
            text: Input text with comma-separated values

        Returns:
            SQL IN clause formatted text

        Raises:
            TransformationError: If conversion fails
        """
        try:
            # EAFP: Try conversion directly
            items = [item.strip() for item in text.split(",") if item.strip()]

            if not items:
                return "()"

            # Quote each item and join with commas
            quoted_items = [f"'{item.replace(chr(39), chr(39) + chr(39))}'" for item in items]
            return f"({', '.join(quoted_items)})"

        except Exception as e:
            raise TransformationError(
                f"SQL IN clause conversion failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "sql_in_clause",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def replace_text(self, text: str, old_value: str, new_value: str) -> str:
        """Replace all occurrences of old_value with new_value.

        Args:
            text: Input text
            old_value: Text to replace
            new_value: Replacement text

        Returns:
            Text with replacements made

        Raises:
            TransformationError: If replacement fails
        """
        try:
            # EAFP: Try replacement directly
            return text.replace(old_value, new_value)

        except Exception as e:
            raise TransformationError(
                f"Text replacement failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "replace",
                    "old_value": old_value,
                    "new_value": new_value,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def regex_replace(self, text: str, pattern: str, replacement: str) -> str:
        """Replace text using regular expression pattern.

        Args:
            text: Input text
            pattern: Regular expression pattern
            replacement: Replacement text (can include regex groups)

        Returns:
            Text with regex replacements made

        Raises:
            TransformationError: If regex replacement fails
        """
        try:
            # EAFP: Try regex replacement directly
            return re.sub(pattern, replacement, text)

        except re.error as e:
            raise TransformationError(
                f"Invalid regular expression pattern: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "regex_replace",
                    "pattern": pattern,
                    "replacement": replacement,
                },
            ) from e
        except Exception as e:
            raise TransformationError(
                f"Regex replacement failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "regex_replace",
                    "pattern": pattern,
                    "replacement": replacement,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def get_input_text(self) -> str:
        """Get the input text used in the transformation.

        Returns:
            Input text string
        """
        return self._input_text

    def get_output_text(self) -> str:
        """Get the output text from the transformation.

        Returns:
            Output text string
        """
        return self._output_text

    def get_transformation_rule(self) -> str:
        """Get the transformation rule that was applied.

        Returns:
            Transformation rule string
        """
        return self._transformation_rule
