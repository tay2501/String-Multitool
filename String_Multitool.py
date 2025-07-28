#!/usr/bin/env python3
"""
String_Multitool - Advanced text transformation tool with pipe support and RSA encryption.

A powerful command-line text transformation tool with intuitive rule-based syntax,
pipe support, and secure RSA encryption capabilities.

Usage:
    String_Multitool.py                          # Interactive mode (clipboard input)
    String_Multitool.py /t/l                     # Apply trim + lowercase to clipboard
    echo "text" | String_Multitool.py            # Interactive mode (pipe input)
    echo "text" | String_Multitool.py /t/l       # Apply trim + lowercase to piped text
    String_Multitool.py /enc                     # Encrypt clipboard text with RSA
    String_Multitool.py /dec                     # Decrypt clipboard text with RSA

Author: String_Multitool Development Team
Version: 2.1.0
License: MIT
"""

import sys
import re
import json
import os
import base64
import secrets
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("Warning: pyperclip not available. Clipboard functionality disabled.")

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


@dataclass
class TransformationRule:
    """Data class representing a transformation rule."""
    name: str
    description: str
    example: str
    function: Callable[[str], str]
    requires_args: bool = False
    default_args: List[str] = None


class ConfigurationManager:
    """Manages application configuration from JSON files."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._transformation_rules = None
        self._security_config = None
    
    def load_transformation_rules(self) -> Dict[str, Any]:
        """Load transformation rules from configuration file."""
        if self._transformation_rules is None:
            config_file = self.config_dir / "transformation_rules.json"
            try:
                with open(config_file, 'r', encoding='utf-8') as file:
                    self._transformation_rules = json.load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        return self._transformation_rules
    
    def load_security_config(self) -> Dict[str, Any]:
        """Load security configuration from configuration file."""
        if self._security_config is None:
            config_file = self.config_dir / "security_config.json"
            try:
                with open(config_file, 'r', encoding='utf-8') as file:
                    self._security_config = json.load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Security configuration file not found: {config_file}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in security configuration file: {e}")
        
        return self._security_config


class CryptographyManager:
    """Manages RSA encryption and decryption operations with enhanced security."""
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize cryptography manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError(
                "cryptography library not installed. "
                "Install with: pip install cryptography>=41.0.0"
            )
        
        self.config_manager = config_manager
        self.security_config = config_manager.load_security_config()
        self.rsa_config = self.security_config["rsa_encryption"]
        
        # Initialize paths
        self.key_directory = Path(self.rsa_config["key_directory"])
        self.private_key_path = self.key_directory / self.rsa_config["private_key_file"]
        self.public_key_path = self.key_directory / self.rsa_config["public_key_file"]
    
    def _ensure_key_directory(self) -> None:
        """Ensure the key directory exists with proper permissions."""
        self.key_directory.mkdir(mode=0o700, exist_ok=True)
    
    def _generate_key_pair(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Generate a new RSA key pair with enhanced security settings.
        
        Returns:
            Tuple of (private_key, public_key)
        """
        print("Generating new RSA key pair with enhanced security...")
        
        private_key = rsa.generate_private_key(
            public_exponent=self.rsa_config["public_exponent"],
            key_size=self.rsa_config["key_size"],
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    def _save_key_pair(self, private_key: rsa.RSAPrivateKey, public_key: rsa.RSAPublicKey) -> None:
        """Save key pair to files with secure permissions.
        
        Args:
            private_key: RSA private key
            public_key: RSA public key
        """
        # Save private key with password protection option (currently disabled for simplicity)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # Could be enhanced with password
        )
        
        with open(self.private_key_path, 'wb') as file:
            file.write(private_pem)
        
        # Save public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(self.public_key_path, 'wb') as file:
            file.write(public_pem)
        
        # Set secure file permissions
        try:
            os.chmod(self.private_key_path, int(self.rsa_config["private_key_permissions"], 8))
            os.chmod(self.public_key_path, int(self.rsa_config["public_key_permissions"], 8))
        except OSError:
            # Windows doesn't support chmod the same way
            pass
        
        print(f"RSA key pair saved securely:")
        print(f"   Private key: {self.private_key_path}")
        print(f"   Public key:  {self.public_key_path}")
    
    def _load_key_pair(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Load existing key pair from files.
        
        Returns:
            Tuple of (private_key, public_key)
        
        Raises:
            Exception: If keys cannot be loaded
        """
        with open(self.private_key_path, 'rb') as file:
            private_key = serialization.load_pem_private_key(
                file.read(),
                password=None,
                backend=default_backend()
            )
        
        with open(self.public_key_path, 'rb') as file:
            public_key = serialization.load_pem_public_key(
                file.read(),
                backend=default_backend()
            )
        
        return private_key, public_key
    
    def ensure_key_pair(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Ensure RSA key pair exists, create if not found.
        
        Returns:
            Tuple of (private_key, public_key)
        """
        self._ensure_key_directory()
        
        # Check if keys exist and are valid
        if self.private_key_path.exists() and self.public_key_path.exists():
            try:
                private_key, public_key = self._load_key_pair()
                print("Using existing RSA key pair")
                return private_key, public_key
            except Exception as e:
                print(f"Warning: Error loading existing keys: {e}")
                print("Generating new key pair...")
        
        # Generate and save new key pair
        private_key, public_key = self._generate_key_pair()
        self._save_key_pair(private_key, public_key)
        
        return private_key, public_key
    
    def encrypt_text(self, plaintext: str) -> str:
        """Encrypt text using hybrid AES+RSA encryption with enhanced security.
        
        Args:
            plaintext: Text to encrypt
            
        Returns:
            Base64 encoded encrypted text
            
        Raises:
            RuntimeError: If encryption fails
        """
        try:
            private_key, public_key = self.ensure_key_pair()
            
            # Convert text to bytes
            plaintext_bytes = plaintext.encode('utf-8')
            
            # Generate cryptographically secure random AES key
            aes_key = secrets.token_bytes(self.rsa_config["aes_key_size"])
            
            # Generate cryptographically secure random IV
            initialization_vector = secrets.token_bytes(self.rsa_config["aes_iv_size"])
            
            # Encrypt the text with AES-CBC
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(initialization_vector),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            block_size = 16  # AES block size
            padding_length = block_size - (len(plaintext_bytes) % block_size)
            padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)
            
            # Encrypt the padded text
            encrypted_text = encryptor.update(padded_plaintext) + encryptor.finalize()
            
            # Encrypt the AES key with RSA using OAEP padding
            hash_algorithm = getattr(hashes, self.rsa_config["hash_algorithm"])()
            mgf_algorithm = getattr(padding, self.rsa_config["mgf_algorithm"])(algorithm=hash_algorithm)
            
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=mgf_algorithm,
                    algorithm=hash_algorithm,
                    label=None
                )
            )
            
            # Combine components: [key_length][encrypted_key][iv][encrypted_text]
            encrypted_key_length = len(encrypted_aes_key).to_bytes(4, byteorder='big')
            combined_data = encrypted_key_length + encrypted_aes_key + initialization_vector + encrypted_text
            
            # Encode as base64 for safe text representation
            encrypted_base64 = base64.b64encode(combined_data).decode('ascii')
            
            print(f"Text encrypted successfully (AES-{self.rsa_config['aes_key_size']*8}+RSA-{self.rsa_config['key_size']}, {len(plaintext_bytes)} bytes)")
            return encrypted_base64
            
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {e}")
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text using hybrid AES+RSA decryption.
        
        Args:
            encrypted_text: Base64 encoded encrypted text
            
        Returns:
            Decrypted plaintext
            
        Raises:
            RuntimeError: If decryption fails
        """
        try:
            private_key, public_key = self.ensure_key_pair()
            
            # Clean and validate input
            cleaned_text = ''.join(encrypted_text.split())
            
            if not cleaned_text:
                raise ValueError("Empty encrypted text")
            
            # Validate base64 characters
            base64_charset = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
            invalid_chars = [c for c in cleaned_text if c not in base64_charset]
            
            if invalid_chars:
                invalid_sample = invalid_chars[:5]
                raise ValueError(f"Invalid base64 characters found: {invalid_sample}")
            
            # Fix base64 padding if enabled
            if self.security_config["base64_encoding"]["auto_fix_padding"]:
                missing_padding = len(cleaned_text) % 4
                if missing_padding:
                    cleaned_text += '=' * (4 - missing_padding)
            
            # Decode from base64
            try:
                encrypted_bytes = base64.b64decode(
                    cleaned_text.encode('ascii'),
                    validate=self.security_config["base64_encoding"]["validate"]
                )
            except Exception as e:
                raise ValueError(f"Invalid base64 format: {e}")
            
            # Extract components
            if len(encrypted_bytes) < 4:
                raise ValueError("Invalid encrypted data format")
            
            # Extract encrypted AES key length
            encrypted_key_length = int.from_bytes(encrypted_bytes[:4], byteorder='big')
            
            if len(encrypted_bytes) < 4 + encrypted_key_length + self.rsa_config["aes_iv_size"]:
                raise ValueError("Invalid encrypted data format")
            
            # Extract components
            encrypted_aes_key = encrypted_bytes[4:4 + encrypted_key_length]
            initialization_vector = encrypted_bytes[4 + encrypted_key_length:4 + encrypted_key_length + self.rsa_config["aes_iv_size"]]
            encrypted_data = encrypted_bytes[4 + encrypted_key_length + self.rsa_config["aes_iv_size"]:]
            
            # Decrypt the AES key with RSA
            hash_algorithm = getattr(hashes, self.rsa_config["hash_algorithm"])()
            mgf_algorithm = getattr(padding, self.rsa_config["mgf_algorithm"])(algorithm=hash_algorithm)
            
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=mgf_algorithm,
                    algorithm=hash_algorithm,
                    label=None
                )
            )
            
            # Decrypt the text with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(initialization_vector),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt and remove PKCS7 padding
            padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Validate and remove padding
            padding_length = padded_plaintext[-1]
            if padding_length > 16 or padding_length == 0:
                raise ValueError("Invalid PKCS7 padding")
            
            # Verify padding bytes
            for i in range(padding_length):
                if padded_plaintext[-(i+1)] != padding_length:
                    raise ValueError("Invalid PKCS7 padding")
            
            decrypted_text = padded_plaintext[:-padding_length].decode('utf-8')
            
            print(f"Text decrypted successfully (AES-{self.rsa_config['aes_key_size']*8}+RSA-{self.rsa_config['key_size']}, {len(decrypted_text)} chars)")
            return decrypted_text
            
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {e}")


class TextTransformationEngine:
    """Advanced text transformation engine with configurable rules."""
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize transformation engine.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.crypto_manager = CryptographyManager(config_manager) if CRYPTO_AVAILABLE else None
        self.transformation_rules = {}
        self.argument_rules = {}
        
        self._initialize_rules()
    
    def _initialize_rules(self) -> None:
        """Initialize transformation rules from configuration."""
        rules_config = self.config_manager.load_transformation_rules()
        
        # Initialize basic transformation rules
        basic_rules = {
            'uh': self._underbar_to_hyphen,
            'hu': self._hyphen_to_underbar,
            'fh': self._fullwidth_to_halfwidth,
            'hf': self._halfwidth_to_fullwidth,
        }
        
        # Initialize case transformation rules
        case_rules = {
            'l': self._to_lowercase,
            'u': self._to_uppercase,
            'p': self._to_pascal_case,
            'c': self._to_camel_case,
            's': self._to_snake_case,
            'a': self._capitalize_words,
        }
        
        # Initialize string operation rules
        string_rules = {
            't': self._trim_whitespace,
            'r': self._reverse_string,
            'si': self._to_sql_in_clause,
            'dlb': self._delete_line_breaks,
        }
        
        # Initialize encryption rules if available
        encryption_rules = {}
        if self.crypto_manager:
            encryption_rules = {
                'enc': self._encrypt_text,
                'dec': self._decrypt_text,
            }
        
        # Combine all rules
        all_rules = {**basic_rules, **case_rules, **string_rules, **encryption_rules}
        
        # Create TransformationRule objects
        for category_name, category_rules in rules_config.items():
            if category_name == "advanced_rules":
                continue  # Handle separately
                
            for rule_key, rule_config in category_rules.items():
                if rule_key in all_rules:
                    self.transformation_rules[rule_key] = TransformationRule(
                        name=rule_config["name"],
                        description=rule_config["description"],
                        example=rule_config["example"],
                        function=all_rules[rule_key]
                    )
        
        # Initialize advanced rules with arguments
        advanced_rules = rules_config.get("advanced_rules", {})
        for rule_key, rule_config in advanced_rules.items():
            if rule_key == 'S':
                self.argument_rules[rule_key] = TransformationRule(
                    name=rule_config["name"],
                    description=rule_config["description"],
                    example=rule_config["example"],
                    function=self._slugify_text,
                    requires_args=True,
                    default_args=rule_config.get("default_args", ["-"])
                )
            elif rule_key == 'R':
                self.argument_rules[rule_key] = TransformationRule(
                    name=rule_config["name"],
                    description=rule_config["description"],
                    example=rule_config["example"],
                    function=self._replace_text,
                    requires_args=True,
                    default_args=rule_config.get("default_args", [""])
                )
    
    # Basic transformation methods
    def _underbar_to_hyphen(self, text: str) -> str:
        """Convert underscores to hyphens."""
        return text.replace('_', '-')
    
    def _hyphen_to_underbar(self, text: str) -> str:
        """Convert hyphens to underscores."""
        return text.replace('-', '_')
    
    def _fullwidth_to_halfwidth(self, text: str) -> str:
        """Convert full-width characters to half-width."""
        fullwidth_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚー－"
        halfwidth_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz--"
        return text.translate(str.maketrans(fullwidth_chars, halfwidth_chars))
    
    def _halfwidth_to_fullwidth(self, text: str) -> str:
        """Convert half-width characters to full-width."""
        halfwidth_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
        fullwidth_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ－"
        return text.translate(str.maketrans(halfwidth_chars, fullwidth_chars))
    
    # Case transformation methods
    def _to_lowercase(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()
    
    def _to_uppercase(self, text: str) -> str:
        """Convert text to uppercase."""
        return text.upper()
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        words = re.findall(r'[a-zA-Z0-9]+', text)
        return ''.join(word.capitalize() for word in words)
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = re.findall(r'[a-zA-Z0-9]+', text)
        if not words:
            return text
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        result = re.sub(r'[^a-zA-Z0-9]+', '_', text)
        result = re.sub(r'_+', '_', result)
        return result.strip('_').lower()
    
    def _capitalize_words(self, text: str) -> str:
        """Capitalize first character of each word."""
        return text.title()
    
    # String operation methods
    def _trim_whitespace(self, text: str) -> str:
        """Remove leading and trailing whitespace."""
        return text.strip()
    
    def _reverse_string(self, text: str) -> str:
        """Reverse the string."""
        return text[::-1]
    
    def _to_sql_in_clause(self, text: str) -> str:
        """Convert line-separated text to SQL IN clause format."""
        lines = text.replace('\r\n', '\n').split('\n')
        quoted_lines = [f"'{line.strip()}'" for line in lines if line.strip()]
        return ',\r\n'.join(quoted_lines)
    
    def _delete_line_breaks(self, text: str) -> str:
        """Remove all line breaks from text."""
        return text.replace('\r\n', '').replace('\r', '').replace('\n', '')
    
    # Advanced transformation methods
    def _slugify_text(self, text: str, replacement: str = '-') -> str:
        """Convert text to slug format with specified replacement character."""
        result = re.sub(r'[^a-zA-Z0-9]+', replacement, text)
        result = re.sub(f'{re.escape(replacement)}+', replacement, result)
        return result.strip(replacement)
    
    def _replace_text(self, text: str, find_string: str, replacement: str = '') -> str:
        """Replace all occurrences of find_string with replacement."""
        return text.replace(find_string, replacement)
    
    # Encryption methods
    def _encrypt_text(self, text: str) -> str:
        """Encrypt text using RSA encryption."""
        if not self.crypto_manager:
            raise RuntimeError("Cryptography not available")
        return self.crypto_manager.encrypt_text(text)
    
    def _decrypt_text(self, text: str) -> str:
        """Decrypt text using RSA decryption."""
        if not self.crypto_manager:
            raise RuntimeError("Cryptography not available")
        return self.crypto_manager.decrypt_text(text)
    
    def parse_rule_string(self, rule_string: str) -> List[Tuple[str, List[str]]]:
        """Parse rule string into list of (rule, arguments) tuples.
        
        Args:
            rule_string: Rule string to parse (e.g., "/t/l" or "/R 'old' 'new'")
            
        Returns:
            List of (rule_name, arguments) tuples
            
        Raises:
            ValueError: If rule string is invalid
        """
        if not rule_string.startswith('/'):
            raise ValueError("Rules must start with '/'")
        
        # Enhanced regex pattern for parsing rules and arguments
        pattern = r"/([a-zA-Z]+)(?:\s+'([^']*)'(?:\s+'([^']*)')?)?|/([a-zA-Z]+)"
        matches = re.findall(pattern, rule_string)
        
        parsed_rules = []
        for match in matches:
            if match[0]:  # Rule with potential arguments
                rule_name = match[0]
                arguments = [arg for arg in match[1:3] if arg]
            elif match[3]:  # Rule without arguments
                rule_name = match[3]
                arguments = []
            else:
                continue
            
            # Validate rule exists
            if rule_name in self.transformation_rules:
                parsed_rules.append((rule_name, []))
            elif rule_name in self.argument_rules:
                # Use provided arguments or defaults
                if not arguments and self.argument_rules[rule_name].default_args:
                    arguments = self.argument_rules[rule_name].default_args
                parsed_rules.append((rule_name, arguments))
            else:
                raise ValueError(f"Unknown rule: {rule_name}")
        
        if not parsed_rules:
            raise ValueError("No valid rules found")
        
        return parsed_rules
    
    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text.
        
        Args:
            text: Input text to transform
            rule_string: Rule string specifying transformations
            
        Returns:
            Transformed text
            
        Raises:
            ValueError: If rule string is invalid
            RuntimeError: If transformation fails
        """
        parsed_rules = self.parse_rule_string(rule_string)
        result = text
        
        for rule_name, arguments in parsed_rules:
            try:
                if rule_name in self.transformation_rules:
                    result = self.transformation_rules[rule_name].function(result)
                elif rule_name in self.argument_rules:
                    result = self.argument_rules[rule_name].function(result, *arguments)
            except Exception as e:
                raise RuntimeError(f"Error applying rule '{rule_name}': {e}")
        
        return result
    
    def get_available_rules(self) -> Dict[str, TransformationRule]:
        """Get all available transformation rules.
        
        Returns:
            Dictionary of rule_name -> TransformationRule
        """
        return {**self.transformation_rules, **self.argument_rules}


class InputOutputManager:
    """Manages input and output operations for the application."""
    
    @staticmethod
    def get_input_text() -> str:
        """Get input text from stdin or clipboard.
        
        Returns:
            Input text string
            
        Raises:
            RuntimeError: If input cannot be read
        """
        if not sys.stdin.isatty():
            # Reading from pipe
            try:
                if sys.platform.startswith('win'):
                    sys.stdin.reconfigure(encoding='utf-8')
                return sys.stdin.read().rstrip('\n\r')
            except Exception as e:
                raise RuntimeError(f"Error reading from stdin: {e}")
        else:
            # Reading from clipboard
            if not CLIPBOARD_AVAILABLE:
                raise RuntimeError("Clipboard functionality not available. Install pyperclip.")
            
            try:
                clipboard_content = pyperclip.paste()
                return clipboard_content.strip() if clipboard_content else ""
            except Exception as e:
                raise RuntimeError(f"Error reading clipboard: {e}")
    
    @staticmethod
    def set_output_text(text: str) -> None:
        """Set output text to clipboard.
        
        Args:
            text: Text to copy to clipboard
            
        Raises:
            RuntimeError: If clipboard operation fails
        """
        if not CLIPBOARD_AVAILABLE:
            print("Warning: Clipboard functionality not available")
            return
        
        try:
            pyperclip.copy(text)
            print("✅ Text copied to clipboard")
        except Exception as e:
            raise RuntimeError(f"Error copying to clipboard: {e}")


class ApplicationInterface:
    """Main application interface and user interaction handler."""
    
    def __init__(self):
        """Initialize application interface."""
        self.config_manager = ConfigurationManager()
        self.transformation_engine = TextTransformationEngine(self.config_manager)
        self.io_manager = InputOutputManager()
    
    def display_help(self) -> None:
        """Display comprehensive help information."""
        available_rules = self.transformation_engine.get_available_rules()
        rules_config = self.config_manager.load_transformation_rules()
        
        print("String_Multitool - Advanced Text Transformation Tool")
        print("=" * 55)
        print()
        print("Usage:")
        print("  String_Multitool.py                    # Interactive mode (clipboard input)")
        print("  String_Multitool.py /t/l               # Apply trim + lowercase to clipboard")
        print("  echo 'text' | String_Multitool.py      # Interactive mode (pipe input)")
        print("  echo 'text' | String_Multitool.py /t/l # Apply trim + lowercase to piped text")
        print()
        print("Available Transformation Rules:")
        print("-" * 35)
        
        # Display rules by category
        category_display_names = {
            "basic_transformations": "Basic Transformations",
            "case_transformations": "Case Transformations", 
            "string_operations": "String Operations",
            "encryption_operations": "Encryption/Decryption",
            "advanced_rules": "Advanced Rules (with arguments)"
        }
        
        for category_key, category_data in rules_config.items():
            category_name = category_display_names.get(category_key, category_key)
            print(f"\n{category_name}:")
            
            for rule_key, rule_info in category_data.items():
                if rule_key in available_rules:
                    rule = available_rules[rule_key]
                    if rule.requires_args:
                        print(f"  /{rule_key} '<args>' - {rule.name}")
                    else:
                        print(f"  /{rule_key} - {rule.name}")
                    print(f"    Example: {rule.example}")
        
        print()
        print("Usage Examples:")
        print("  /t                        # Trim whitespace")
        print("  /t/l                      # Trim then lowercase")
        print("  /enc                      # Encrypt with RSA")
        print("  /dec                      # Decrypt with RSA")
        print("  /S '-'                    # Slugify with hyphen")
        print("  /R 'old' 'new'            # Replace 'old' with 'new'")
        
        if CRYPTO_AVAILABLE:
            security_config = self.config_manager.load_security_config()
            rsa_config = security_config["rsa_encryption"]
            print()
            print("RSA Encryption Information:")
            print(f"  • Key Size: RSA-{rsa_config['key_size']}")
            print(f"  • AES Encryption: AES-{rsa_config['aes_key_size']*8}-{rsa_config['aes_mode']}")
            print(f"  • Hash Algorithm: {rsa_config['hash_algorithm']}")
            print(f"  • Keys Location: {rsa_config['key_directory']}/")
            print("  • Auto-generated on first use")
            print("  • Supports unlimited text size")
    
    def run_interactive_mode(self, input_text: str) -> None:
        """Run application in interactive mode.
        
        Args:
            input_text: Initial input text
        """
        print("String_Multitool - Interactive Mode")
        print("=" * 40)
        print(f"Input text: '{input_text[:50]}{'...' if len(input_text) > 50 else ''}'")
        print()
        print("Enter transformation rules (e.g., /t/l) or 'help' for available rules:")
        
        current_text = input_text
        
        while True:
            try:
                try:
                    user_input = input("Rules: ").strip()
                except EOFError:
                    print("\nGoodbye!")
                    break
                
                if not user_input:
                    print("Please enter a rule or 'help'")
                    continue
                
                if user_input.lower() in ['help', 'h', '?']:
                    self.display_help()
                    continue
                
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("Goodbye!")
                    break
                
                # Handle decryption with fresh clipboard content
                if user_input.strip() == '/dec':
                    current_text = self.io_manager.get_input_text()
                
                # Apply transformations
                result = self.transformation_engine.apply_transformations(current_text, user_input)
                self.io_manager.set_output_text(result)
                
                # Display result
                if user_input.strip() == '/enc':
                    print(f"Result: '{result}'")
                    print("(Full encrypted text copied to clipboard)")
                else:
                    display_result = result[:100] + ('...' if len(result) > 100 else '')
                    print(f"Result: '{display_result}'")
                
                # Update current text for next iteration
                current_text = result
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Type 'help' for available rules")
    
    def run_command_mode(self, rule_string: str) -> None:
        """Run application in command mode with specified rules.
        
        Args:
            rule_string: Rule string to apply
        """
        try:
            input_text = self.io_manager.get_input_text()
            result = self.transformation_engine.apply_transformations(input_text, rule_string)
            self.io_manager.set_output_text(result)
            
            print(f"Applied: {rule_string}")
            
            # Display appropriate result format
            if rule_string.strip() == '/enc':
                print(f"Result: '{result}'")
                print("(Full encrypted text copied to clipboard)")
            else:
                display_result = result[:100] + ('...' if len(result) > 100 else '')
                print(f"Result: '{display_result}'")
            
            print("✅ Transformation completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def run(self) -> None:
        """Main application entry point."""
        # Parse command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['-h', '--help', 'help']:
                self.display_help()
                return
            
            # Command mode - join all arguments to handle quoted strings
            rule_string = ' '.join(sys.argv[1:])
            self.run_command_mode(rule_string)
        else:
            # Interactive mode
            try:
                input_text = self.io_manager.get_input_text()
                self.run_interactive_mode(input_text)
            except Exception as e:
                print(f"❌ Error: {e}", file=sys.stderr)
                sys.exit(1)


def main():
    """Application entry point."""
    try:
        app = ApplicationInterface()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()