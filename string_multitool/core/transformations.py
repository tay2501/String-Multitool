"""
Text transformation engine for String_Multitool.

This module provides the core text transformation functionality with
configurable rules and comprehensive error handling.
"""

from __future__ import annotations

import re
import json
import base64
import hashlib
from typing import Any

from ..exceptions import TransformationError, ValidationError
from .types import (
    TransformationRule, TransformationRuleType, ConfigurableComponent,
    TransformationEngineProtocol, ConfigManagerProtocol, CryptoManagerProtocol
)


class TextTransformationEngine(ConfigurableComponent[dict[str, Any]]):
    """Advanced text transformation engine with configurable rules.
    
    This class provides a comprehensive set of text transformation operations
    with support for sequential rule application and custom rule definitions.
    """
    
    def __init__(self, config_manager: ConfigManagerProtocol) -> None:
        """Initialize transformation engine.
        
        Args:
            config_manager: Configuration manager instance
            
        Raises:
            TransformationError: If initialization fails
        """
        try:
            transformation_config = config_manager.load_transformation_rules()
            super().__init__(transformation_config)
            
            # Instance variable annotations following PEP 526
            self.config_manager: ConfigManagerProtocol = config_manager
            self.crypto_manager: CryptoManagerProtocol | None = None
            self._available_rules: dict[str, TransformationRule] | None = None
            
        except Exception as e:
            raise TransformationError(
                f"Failed to initialize transformation engine: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set the cryptography manager for encryption/decryption operations.
        
        Args:
            crypto_manager: Cryptography manager instance
        """
        self.crypto_manager = crypto_manager
    
    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text.
        
        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')
            
        Returns:
            Transformed text
            
        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        if not isinstance(text, str):
            raise ValidationError(
                f"Text must be a string, got {type(text).__name__}",
                {"text_type": type(text).__name__}
            )
        
        if not isinstance(rule_string, str):
            raise ValidationError(
                f"Rule string must be a string, got {type(rule_string).__name__}",
                {"rule_type": type(rule_string).__name__}
            )
        
        if not rule_string.strip():
            raise ValidationError("Rule string cannot be empty")
        
        if not rule_string.startswith('/'):
            raise ValidationError(
                "Rules must start with '/'",
                {"rule_string": rule_string}
            )
        
        try:
            # Parse and apply rules sequentially
            parsed_rules = self.parse_rule_string(rule_string)
            result = text
            
            for rule_name, args in parsed_rules:
                result = self._apply_single_rule(result, rule_name, args)
            
            return result
            
        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            raise TransformationError(
                f"Unexpected error during transformation: {e}",
                {"rule_string": rule_string, "text_length": len(text), "error_type": type(e).__name__}
            ) from e
    
    def parse_rule_string(self, rule_string: str) -> list[tuple[str, list[str]]]:
        """Parse rule string into list of (rule, arguments) tuples.
        
        Args:
            rule_string: Rule string to parse (e.g., '/t/l/r "old" "new"')
            
        Returns:
            List of (rule_name, arguments) tuples
            
        Raises:
            ValidationError: If rule string format is invalid
        """
        try:
            if not rule_string.startswith('/'):
                raise ValidationError(
                    "Rule string must start with '/'",
                    {"rule_string": rule_string}
                )
            
            # Remove leading slash and split by slash
            rules_part: str = rule_string[1:]
            if not rules_part:
                raise ValidationError("Empty rule string after '/'")
            
            # Handle quoted arguments
            parts: list[str] = self._parse_with_quotes(rules_part)
            parsed_rules: list[tuple[str, list[str]]] = []
            current_rule: str | None = None
            current_args: list[str] = []
            
            for part in parts:
                if part.startswith('/'):
                    # New rule found, save previous if exists
                    if current_rule is not None:
                        parsed_rules.append((current_rule, current_args))
                    current_rule = part[1:]  # Remove leading slash
                    current_args = []
                elif current_rule is not None:
                    # Argument for current rule
                    current_args.append(part)
                else:
                    # First part should be a rule
                    current_rule = part
                    current_args = []
            
            # Add the last rule
            if current_rule is not None:
                parsed_rules.append((current_rule, current_args))
            
            if not parsed_rules:
                raise ValidationError("No valid rules found in rule string")
            
            return parsed_rules
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Failed to parse rule string: {e}",
                {"rule_string": rule_string, "error_type": type(e).__name__}
            ) from e
    
    def get_available_rules(self) -> dict[str, TransformationRule]:
        """Get all available transformation rules.
        
        Returns:
            Dictionary mapping rule names to TransformationRule objects
        """
        if self._available_rules is None:
            self._available_rules = self._build_available_rules()
        
        return self._available_rules
    
    def _apply_single_rule(self, text: str, rule_name: str, args: list[str]) -> str:
        """Apply a single transformation rule to text.
        
        Args:
            text: Input text
            rule_name: Name of the rule to apply
            args: Arguments for the rule
            
        Returns:
            Transformed text
            
        Raises:
            TransformationError: If rule application fails
        """
        try:
            available_rules = self.get_available_rules()
            
            if rule_name not in available_rules:
                raise TransformationError(
                    f"Unknown rule: {rule_name}",
                    {"rule_name": rule_name, "available_rules": list(available_rules.keys())}
                )
            
            rule = available_rules[rule_name]
            
            # Handle rules that require arguments
            if rule.requires_args:
                if not args and rule.default_args:
                    args = rule.default_args
                elif not args:
                    raise TransformationError(
                        f"Rule '{rule_name}' requires arguments",
                        {"rule_name": rule_name, "required_args": True}
                    )
            
            # Apply the transformation
            if rule_name in ['enc', 'dec']:
                return self._apply_crypto_rule(text, rule_name)
            elif args:
                return self._apply_rule_with_args(text, rule_name, args)
            else:
                return rule.function(text)
                
        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(
                f"Failed to apply rule '{rule_name}': {e}",
                {"rule_name": rule_name, "args": args, "text_length": len(text), "error_type": type(e).__name__}
            ) from e
    
    def _apply_crypto_rule(self, text: str, rule_name: str) -> str:
        """Apply encryption or decryption rule.
        
        Args:
            text: Input text
            rule_name: 'enc' or 'dec'
            
        Returns:
            Encrypted or decrypted text
            
        Raises:
            TransformationError: If crypto operation fails
        """
        if self.crypto_manager is None:
            raise TransformationError(
                "Cryptography manager not available for encryption/decryption",
                {"rule_name": rule_name}
            )
        
        try:
            if rule_name == 'enc':
                print("Using existing RSA key pair")
                result = self.crypto_manager.encrypt_text(text)
                print(f"Text encrypted successfully (AES-256+RSA-4096, {len(text)} bytes)")
                return result
            elif rule_name == 'dec':
                print("Using existing RSA key pair")
                result = self.crypto_manager.decrypt_text(text)
                print(f"Text decrypted successfully (AES-256+RSA-4096, {len(result)} chars)")
                return result
            else:
                raise TransformationError(f"Unknown crypto rule: {rule_name}")
                
        except Exception as e:
            raise TransformationError(
                f"Cryptography operation failed: {e}",
                {"rule_name": rule_name, "error_type": type(e).__name__}
            ) from e
    
    def _apply_rule_with_args(self, text: str, rule_name: str, args: list[str]) -> str:
        """Apply transformation rule that requires arguments.
        
        Args:
            text: Input text
            rule_name: Name of the rule
            args: Arguments for the rule
            
        Returns:
            Transformed text
        """
        if rule_name == 'r':  # Replace
            if len(args) >= 2:
                return text.replace(args[0], args[1])
            elif len(args) == 1:
                return text.replace(args[0], '')
            else:
                raise TransformationError("Replace rule requires at least 1 argument")
        
        elif rule_name == 'S':  # Slugify
            separator = args[0] if args else '-'
            # Convert to lowercase, replace non-alphanumeric with separator
            result = re.sub(r'[^a-zA-Z0-9]+', separator, text.lower())
            return result.strip(separator)
        
        else:
            raise TransformationError(f"Unknown rule with arguments: {rule_name}")
    
    def _parse_with_quotes(self, text: str) -> list[str]:
        """Parse text respecting quoted strings.
        
        Args:
            text: Text to parse
            
        Returns:
            List of parsed parts
        """
        parts: list[str] = []
        current_part: str = ""
        in_quotes: bool = False
        quote_char: str | None = None
        i: int = 0
        
        while i < len(text):
            char: str = text[i]
            
            if not in_quotes:
                if char in ['"', "'"]:
                    in_quotes = True
                    quote_char = char
                elif char == '/':
                    if current_part:
                        parts.append(current_part)
                        current_part = ""
                    current_part = "/"
                elif char == ' ':
                    if current_part:
                        parts.append(current_part)
                        current_part = ""
                else:
                    current_part += char
            else:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_part += char
            
            i += 1
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    def _build_available_rules(self) -> dict[str, TransformationRule]:
        """Build dictionary of available transformation rules."""
        rules = {}
        
        # Basic transformations
        rules.update({
            'uh': TransformationRule(
                name='Underbar to Hyphen',
                description='Convert underscores to hyphens',
                example='TBL_CHA1 → TBL-CHA1',
                function=lambda text: text.replace('_', '-'),
                rule_type=TransformationRuleType.BASIC
            ),
            'hu': TransformationRule(
                name='Hyphen to Underbar',
                description='Convert hyphens to underscores',
                example='TBL-CHA1 → TBL_CHA1',
                function=lambda text: text.replace('-', '_'),
                rule_type=TransformationRuleType.BASIC
            ),
            'fh': TransformationRule(
                name='Full-width to Half-width',
                description='Convert full-width characters to half-width',
                example='ＴＢＬ－ＣＨＡ１ → TBL-CHA1',
                function=self._full_to_half_width,
                rule_type=TransformationRuleType.BASIC
            ),
            'hf': TransformationRule(
                name='Half-width to Full-width',
                description='Convert half-width characters to full-width',
                example='TBL-CHA1 → ＴＢＬ－ＣＨＡ１',
                function=self._half_to_full_width,
                rule_type=TransformationRuleType.BASIC
            ),
        })
        
        # Case transformations
        rules.update({
            'l': TransformationRule(
                name='Lowercase',
                description='Convert to lowercase',
                example='HELLO WORLD → hello world',
                function=str.lower,
                rule_type=TransformationRuleType.CASE
            ),
            'u': TransformationRule(
                name='Uppercase',
                description='Convert to uppercase',
                example='hello world → HELLO WORLD',
                function=str.upper,
                rule_type=TransformationRuleType.CASE
            ),
            'p': TransformationRule(
                name='PascalCase',
                description='Convert to PascalCase',
                example='the quick brown fox → TheQuickBrownFox',
                function=self._to_pascal_case,
                rule_type=TransformationRuleType.CASE
            ),
            'c': TransformationRule(
                name='camelCase',
                description='Convert to camelCase',
                example='is error state → isErrorState',
                function=self._to_camel_case,
                rule_type=TransformationRuleType.CASE
            ),
            's': TransformationRule(
                name='snake_case',
                description='Convert to snake_case',
                example='is error state → is_error_state',
                function=self._to_snake_case,
                rule_type=TransformationRuleType.CASE
            ),
            'a': TransformationRule(
                name='Capitalize',
                description='Capitalize first letter of each word',
                example='hello world → Hello World',
                function=str.title,
                rule_type=TransformationRuleType.CASE
            ),
        })
        
        # String operations
        rules.update({
            't': TransformationRule(
                name='Trim',
                description='Remove leading and trailing whitespace',
                example='  hello world   → hello world',
                function=str.strip,
                rule_type=TransformationRuleType.STRING_OPS
            ),
            'R': TransformationRule(
                name='Reverse',
                description='Reverse the string',
                example='hello → olleh',
                function=lambda text: text[::-1],
                rule_type=TransformationRuleType.STRING_OPS
            ),
            'si': TransformationRule(
                name='SQL IN Clause',
                description='Format as SQL IN clause',
                example="A0001\\r\\nA0002\\r\\nA0003 → 'A0001',\\r\\n'A0002',\\r\\n'A0003'",
                function=self._to_sql_in_clause,
                rule_type=TransformationRuleType.STRING_OPS
            ),
            'dlb': TransformationRule(
                name='Delete Line Breaks',
                description='Remove all line breaks',
                example='A0001\\r\\nA0002\\r\\nA0003 → A0001A0002A0003',
                function=lambda text: text.replace('\r\n', '').replace('\n', '').replace('\r', ''),
                rule_type=TransformationRuleType.STRING_OPS
            ),
        })
        
        # Encryption operations
        rules.update({
            'enc': TransformationRule(
                name='RSA Encrypt',
                description='Encrypt text using RSA',
                example='Secret message → Base64 encrypted text',
                function=lambda text: text,  # Handled specially
                rule_type=TransformationRuleType.ENCRYPTION
            ),
            'dec': TransformationRule(
                name='RSA Decrypt',
                description='Decrypt text using RSA',
                example='Base64 encrypted text → Secret message',
                function=lambda text: text,  # Handled specially
                rule_type=TransformationRuleType.ENCRYPTION
            ),
        })
        
        # Hash operations
        rules.update({
            'hash': TransformationRule(
                name='SHA-256 Hash',
                description='Generate SHA-256 hash of input text',
                example='password → 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
                function=self._sha256_hash,
                rule_type=TransformationRuleType.ADVANCED
            ),
        })
        
        # Encoding operations
        rules.update({
            'base64enc': TransformationRule(
                name='Base64 Encode',
                description='Encode text to Base64',
                example='hello → aGVsbG8=',
                function=self._base64_encode,
                rule_type=TransformationRuleType.ADVANCED
            ),
            'base64dec': TransformationRule(
                name='Base64 Decode',
                description='Decode Base64 to text',
                example='aGVsbG8= → hello',
                function=self._base64_decode,
                rule_type=TransformationRuleType.ADVANCED
            ),
        })
        
        # Formatting operations
        rules.update({
            'formatjson': TransformationRule(
                name='Format JSON',
                description='Format JSON with proper indentation',
                example='{"a":1,"b":2} → formatted JSON',
                function=self._format_json,
                rule_type=TransformationRuleType.ADVANCED
            ),
        })
        
        # Advanced rules with arguments
        rules.update({
            'r': TransformationRule(
                name='Replace',
                description='Replace text',
                example="/r 'old' 'new' → old text → new text",
                function=lambda text: text,  # Handled specially
                requires_args=True,
                rule_type=TransformationRuleType.ADVANCED
            ),
            'S': TransformationRule(
                name='Slugify',
                description='Convert to URL-friendly slug',
                example="/S '+' → http://foo.bar → http+foo+bar",
                function=lambda text: text,  # Handled specially
                requires_args=True,
                default_args=['-'],
                rule_type=TransformationRuleType.ADVANCED
            ),
        })
        
        return rules
    
    # Helper methods for transformations
    def _full_to_half_width(self, text: str) -> str:
        """Convert full-width characters to half-width."""
        result = ""
        for char in text:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:  # Full-width ASCII range
                result += chr(code - 0xFEE0)
            elif code == 0x3000:  # Full-width space
                result += ' '
            else:
                result += char
        return result
    
    def _half_to_full_width(self, text: str) -> str:
        """Convert half-width characters to full-width."""
        result = ""
        for char in text:
            code = ord(char)
            if 0x21 <= code <= 0x7E:  # Half-width ASCII range
                result += chr(code + 0xFEE0)
            elif char == ' ':  # Half-width space
                result += '　'
            else:
                result += char
        return result
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        words = re.findall(r'\w+', text)
        return ''.join(word.capitalize() for word in words)
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = re.findall(r'\w+', text)
        if not words:
            return text
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        words = re.findall(r'\w+', text)
        return '_'.join(word.lower() for word in words)
    
    def _to_sql_in_clause(self, text: str) -> str:
        """Convert text to SQL IN clause format."""
        lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        quoted_lines = [f"'{line.strip()}'" for line in lines if line.strip()]
        return ',\r\n'.join(quoted_lines)
    
    def _sha256_hash(self, text: str) -> str:
        """Generate SHA-256 hash of input text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _base64_encode(self, text: str) -> str:
        """Encode text to Base64."""
        try:
            encoded_bytes = base64.b64encode(text.encode('utf-8'))
            return encoded_bytes.decode('ascii')
        except Exception as e:
            raise TransformationError(f"Base64 encoding failed: {e}")
    
    def _base64_decode(self, text: str) -> str:
        """Decode Base64 to text."""
        try:
            # Remove whitespace and padding if needed
            clean_text = text.strip()
            decoded_bytes = base64.b64decode(clean_text)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            raise TransformationError(f"Base64 decoding failed: {e}")
    
    def _format_json(self, text: str) -> str:
        """Format JSON with proper indentation."""
        try:
            # Parse JSON
            parsed = json.loads(text)
            # Format with 2-space indentation
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise TransformationError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise TransformationError(f"JSON formatting failed: {e}")
    
    def validate_rule_string(self, rule_string: str) -> tuple[bool, str | None]:
        """Validate rule string format.
        
        Args:
            rule_string: Rule string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not isinstance(rule_string, str):
                return False, f"Rule string must be a string, got {type(rule_string).__name__}"
            
            if not rule_string.strip():
                return False, "Rule string cannot be empty"
            
            if not rule_string.startswith('/'):
                return False, "Rules must start with '/'"
            
            # Try to parse the rule string
            self.parse_rule_string(rule_string)
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_rule_help(self, rule_name: str | None = None) -> str:
        """Get help information for rules.
        
        Args:
            rule_name: Specific rule name or None for all rules
            
        Returns:
            Help text for the rule(s)
        """
        if rule_name is None:
            # Return help for all rules
            help_text = "Available transformation rules:\n"
            rules = self.get_available_rules()
            for name, rule in rules.items():
                help_text += f"  /{name} - {rule.name}\n"
                if rule.example:
                    help_text += f"    Example: {rule.example}\n"
            return help_text
        else:
            # Return help for specific rule
            rules = self.get_available_rules()
            if rule_name in rules:
                rule = rules[rule_name]
                return f"/{rule_name} - {rule.name}\n{rule.description}\nExample: {rule.example}"
            else:
                return f"Unknown rule: {rule_name}"