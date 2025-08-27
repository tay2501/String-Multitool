"""
Argument parsing utilities for String_Multitool.

This module provides enterprise-grade argument parsing functionality
using Python's standard library `shlex` module for robust and secure
string parsing with proper escape character handling.
"""

from __future__ import annotations

import shlex
from typing import Any

from ..exceptions import ValidationError


class ArgumentParsingError(ValidationError):
    """Specialized exception for argument parsing errors."""
    
    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize with enhanced context for debugging.
        
        Args:
            message: Error message describing the parsing failure
            context: Additional context information for debugging
        """
        super().__init__(message, context or {})


class ShellStyleArgumentParser:
    """Enterprise-grade shell-style argument parser.
    
    Uses Python's standard library `shlex` module for POSIX-compliant
    argument parsing with proper handling of:
    - Quoted strings with escape sequences
    - Backslash escaping
    - Space-separated arguments
    - Special characters in arguments
    
    Design Principles:
    - Single Responsibility: Only handles argument parsing
    - Open/Closed: Extensible through inheritance
    - Dependency Inversion: Uses standard library abstractions
    - Interface Segregation: Minimal, focused interface
    
    Example:
        parser = ShellStyleArgumentParser()
        result = parser.parse_rule_string("/r 'old text' 'new text'")
        # Returns: [('r', ['old text', 'new text'])]
    """

    def __init__(self, posix: bool = False) -> None:
        """Initialize the parser with POSIX compliance setting.
        
        Args:
            posix: Whether to use POSIX-compliant parsing (default: False for Windows compatibility)
        """
        self._posix: bool = posix

    def parse_rule_string(self, rule_string: str) -> list[tuple[str, list[str]]]:
        """Parse rule string into structured format.
        
        Uses shlex for robust parsing of shell-style command syntax.
        Handles complex cases like:
        - /r '/' '\'
        - /r "path with spaces" "new path"
        - /convertbytsv --case-insensitive file.tsv
        
        Args:
            rule_string: Rule string to parse (e.g., "/r 'old' 'new'")
            
        Returns:
            List of (rule_name, arguments) tuples
            
        Raises:
            ArgumentParsingError: If parsing fails or rule format is invalid
        """
        try:
            # Validate input
            if not isinstance(rule_string, str):
                raise ArgumentParsingError(
                    f"Rule string must be a string, got {type(rule_string).__name__}",
                    {"input_type": type(rule_string).__name__}
                )

            if not rule_string.strip():
                raise ArgumentParsingError("Rule string cannot be empty")

            if not rule_string.startswith("/"):
                raise ArgumentParsingError(
                    "Rule string must start with '/'",
                    {"rule_string": rule_string}
                )

            # Remove leading slash and parse using shlex
            rules_part = rule_string[1:]
            if not rules_part:
                raise ArgumentParsingError("Empty rule string after '/'")

            # Split the entire string first
            try:
                tokens = shlex.split(rules_part, posix=self._posix)
            except ValueError as e:
                # shlex raises ValueError for unclosed quotes, etc.
                raise ArgumentParsingError(
                    f"Invalid quote or escape sequence: {e}",
                    {
                        "rule_string": rule_string,
                        "shlex_error": str(e)
                    }
                ) from e

            if not tokens:
                raise ArgumentParsingError("No valid tokens found in rule string")

            # Parse tokens into rules and arguments
            parsed_rules: list[tuple[str, list[str]]] = []
            current_rule: str | None = None
            current_args: list[str] = []

            for token in tokens:
                if token.startswith("/"):
                    # New rule found, save previous if exists
                    if current_rule is not None:
                        parsed_rules.append((current_rule, current_args))
                    
                    rule_part = token[1:]  # Remove leading slash
                    
                    # Check if this is a sequential rule chain (contains '/')
                    if '/' in rule_part:
                        # Handle sequential rules like 't/u' or 't/r'
                        sequential_rules = rule_part.split('/')
                        for i, seq_rule in enumerate(sequential_rules):
                            if seq_rule:  # Skip empty parts
                                if i == len(sequential_rules) - 1:
                                    # Last rule in sequence might have arguments coming next
                                    current_rule = seq_rule
                                    current_args = []
                                else:
                                    # Non-last rules have no arguments
                                    parsed_rules.append((seq_rule, []))
                        if len(sequential_rules) == 0 or not sequential_rules[-1]:
                            current_rule = None
                            current_args = []
                    else:
                        current_rule = rule_part
                        current_args = []
                elif current_rule is not None:
                    # Argument for current rule - remove surrounding quotes if present
                    clean_token = self._remove_surrounding_quotes(token)
                    current_args.append(clean_token)
                else:
                    # First token should be a rule (no leading slash in this context)
                    rule_part = token
                    
                    # Check if this is a sequential rule chain
                    if '/' in rule_part:
                        # Handle sequential rules
                        sequential_rules = rule_part.split('/')
                        for i, seq_rule in enumerate(sequential_rules):
                            if seq_rule:  # Skip empty parts
                                if i == len(sequential_rules) - 1:
                                    # Last rule in sequence might have arguments coming next
                                    current_rule = seq_rule
                                    current_args = []
                                else:
                                    # Non-last rules have no arguments
                                    parsed_rules.append((seq_rule, []))
                        if len(sequential_rules) == 0 or not sequential_rules[-1]:
                            current_rule = None
                            current_args = []
                    else:
                        current_rule = rule_part
                        current_args = []

            # Add the last rule if it exists and wasn't part of a sequential chain
            if current_rule is not None:
                parsed_rules.append((current_rule, current_args))

            if not parsed_rules:
                raise ArgumentParsingError("No valid rules found in rule string")

            return parsed_rules

        except ArgumentParsingError:
            raise
        except Exception as e:
            raise ArgumentParsingError(
                f"Unexpected error during argument parsing: {e}",
                {
                    "rule_string": rule_string,
                    "error_type": type(e).__name__,
                    "posix_mode": self._posix
                }
            ) from e

    def escape_argument(self, arg: str) -> str:
        """Escape argument for shell safety.
        
        Args:
            arg: Argument string to escape
            
        Returns:
            Shell-safe escaped argument
            
        Raises:
            ArgumentParsingError: If escaping fails
        """
        try:
            return shlex.quote(arg)
        except Exception as e:
            raise ArgumentParsingError(
                f"Failed to escape argument: {e}",
                {"argument": arg, "error_type": type(e).__name__}
            ) from e

    def join_arguments(self, args: list[str]) -> str:
        """Join arguments into a shell-safe command string.
        
        Args:
            args: List of arguments to join
            
        Returns:
            Shell-safe command string
            
        Raises:
            ArgumentParsingError: If joining fails
        """
        try:
            return shlex.join(args)
        except Exception as e:
            raise ArgumentParsingError(
                f"Failed to join arguments: {e}",
                {"arguments": args, "error_type": type(e).__name__}
            ) from e

    def validate_rule_format(self, rule_string: str) -> tuple[bool, str | None]:
        """Validate rule string format without full parsing.
        
        Args:
            rule_string: Rule string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.parse_rule_string(rule_string)
            return True, None
        except ArgumentParsingError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected validation error: {e}"

    def _remove_surrounding_quotes(self, text: str) -> str:
        """Remove surrounding quotes from a string if present.
        
        Args:
            text: Text that may have surrounding quotes
            
        Returns:
            Text with surrounding quotes removed if they were present
        """
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith("'") and text.endswith("'")):
                return text[1:-1]
        return text


class ArgumentParserFactory:
    """Factory for creating argument parsers with different configurations.
    
    Implements Factory pattern for flexible parser creation and configuration.
    Supports dependency injection and extensibility.
    """

    @staticmethod
    def create_shell_parser(posix: bool = False) -> ShellStyleArgumentParser:
        """Create a shell-style argument parser.
        
        Args:
            posix: Whether to use POSIX-compliant parsing (default: False for Windows compatibility)
            
        Returns:
            Configured ShellStyleArgumentParser instance
        """
        return ShellStyleArgumentParser(posix=posix)

    @staticmethod
    def create_windows_parser() -> ShellStyleArgumentParser:
        """Create a Windows-compatible argument parser.
        
        Returns:
            Parser configured for Windows command-line compatibility
        """
        return ShellStyleArgumentParser(posix=False)

    @staticmethod
    def create_strict_parser() -> ShellStyleArgumentParser:
        """Create a strict POSIX-compliant parser.
        
        Returns:
            Parser with strict POSIX compliance for maximum compatibility
        """
        return ShellStyleArgumentParser(posix=True)


# Default parser instance for convenience
default_parser = ArgumentParserFactory.create_shell_parser()