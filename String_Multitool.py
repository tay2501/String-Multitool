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
import time
import threading
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Ensure UTF-8 encoding for stdout/stderr on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        pass

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


@dataclass
class SessionState:
    """Represents current interactive session state."""
    current_text: str
    text_source: str  # "clipboard", "pipe", "manual"
    last_update_time: datetime
    character_count: int
    auto_detection_enabled: bool
    clipboard_monitor_active: bool


@dataclass
class CommandResult:
    """Result of command processing."""
    success: bool
    message: str
    should_continue: bool = True
    updated_text: Optional[str] = None


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
            'R': self._reverse_string,
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
            elif rule_key == 'r':
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


class ClipboardMonitor:
    """Monitors clipboard changes for auto-detection functionality."""
    
    def __init__(self, io_manager: 'InputOutputManager'):
        """Initialize clipboard monitor.
        
        Args:
            io_manager: InputOutputManager instance for clipboard operations
        """
        self.io_manager = io_manager
        self.last_content = ""
        self.last_check_time = None
        self.is_monitoring = False
        self.check_interval = 1.0  # seconds
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.change_callback = None
        self.max_content_size = 1024 * 1024  # 1MB limit
    
    def start_monitoring(self, change_callback: Optional[Callable[[str], None]] = None) -> None:
        """Start clipboard monitoring in background.
        
        Args:
            change_callback: Optional callback function called when clipboard changes
        """
        if self.is_monitoring:
            return
        
        self.change_callback = change_callback
        self.is_monitoring = True
        self.stop_event.clear()
        
        # Initialize with current clipboard content
        try:
            self.last_content = self.get_current_content()
        except Exception:
            self.last_content = ""
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop clipboard monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        self.change_callback = None
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop running in background thread."""
        while not self.stop_event.is_set():
            try:
                if self.check_for_changes() and self.change_callback:
                    self.change_callback(self.last_content)
            except Exception:
                # Silently handle monitoring errors to avoid spam
                pass
            
            # Wait for next check or stop signal
            self.stop_event.wait(self.check_interval)
    
    def check_for_changes(self) -> bool:
        """Check if clipboard content has changed.
        
        Returns:
            True if clipboard content has changed, False otherwise
        """
        try:
            current_content = self.get_current_content()
            self.last_check_time = datetime.now()
            
            if current_content != self.last_content:
                self.last_content = current_content
                return True
            
            return False
        except Exception:
            return False
    
    def get_current_content(self) -> str:
        """Get current clipboard content.
        
        Returns:
            Current clipboard content
            
        Raises:
            RuntimeError: If clipboard cannot be accessed
        """
        if not CLIPBOARD_AVAILABLE:
            raise RuntimeError("Clipboard functionality not available")
        
        try:
            content = pyperclip.paste()
            if content is None:
                return ""
            
            # Check size limit
            if len(content) > self.max_content_size:
                raise RuntimeError(f"Clipboard content too large ({len(content)} bytes, max {self.max_content_size})")
            
            return content.strip() if content else ""
        except Exception as e:
            if "too large" in str(e):
                raise
            raise RuntimeError(f"Error reading clipboard: {e}")
    
    def set_check_interval(self, interval: float) -> None:
        """Set clipboard check interval.
        
        Args:
            interval: Check interval in seconds (minimum 0.1)
        """
        self.check_interval = max(0.1, interval)
    
    def set_max_content_size(self, size: int) -> None:
        """Set maximum allowed clipboard content size.
        
        Args:
            size: Maximum size in bytes
        """
        self.max_content_size = max(1024, size)  # Minimum 1KB


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
    def get_clipboard_text() -> str:
        """Get text from clipboard only.
        
        Returns:
            Clipboard text string
            
        Raises:
            RuntimeError: If clipboard cannot be read
        """
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


class InteractiveSession:
    """Manages interactive session state and clipboard operations."""
    
    def __init__(self, io_manager: InputOutputManager, transformation_engine: 'TextTransformationEngine'):
        """Initialize interactive session.
        
        Args:
            io_manager: InputOutputManager instance
            transformation_engine: TextTransformationEngine instance
        """
        self.io_manager = io_manager
        self.transformation_engine = transformation_engine
        self.current_text = ""
        self.text_source = "clipboard"  # clipboard, pipe, manual
        self.last_update_time = datetime.now()
        self.clipboard_monitor = ClipboardMonitor(io_manager)
        self.auto_detection_enabled = False
        self.session_start_time = datetime.now()
    
    def initialize_with_text(self, text: str, source: str = "clipboard") -> None:
        """Initialize session with initial text.
        
        Args:
            text: Initial text content
            source: Source of the text (clipboard, pipe, manual)
        """
        self.update_working_text(text, source)
    
    def refresh_from_clipboard(self) -> bool:
        """Refresh working text from clipboard.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        try:
            new_content = self.io_manager.get_clipboard_text()
            
            if new_content == self.current_text:
                return False  # No change detected
            
            self.update_working_text(new_content, "clipboard")
            return True
            
        except Exception:
            return False
    
    def update_working_text(self, text: str, source: str) -> None:
        """Update current working text with source tracking.
        
        Args:
            text: New text content
            source: Source of the text (clipboard, pipe, manual)
        """
        self.current_text = text
        self.text_source = source
        self.last_update_time = datetime.now()
    
    def get_status_info(self) -> SessionState:
        """Get current session status information.
        
        Returns:
            SessionState object with current status
        """
        return SessionState(
            current_text=self.current_text,
            text_source=self.text_source,
            last_update_time=self.last_update_time,
            character_count=len(self.current_text),
            auto_detection_enabled=self.auto_detection_enabled,
            clipboard_monitor_active=self.clipboard_monitor.is_monitoring
        )
    
    def toggle_auto_detection(self, enabled: bool) -> bool:
        """Enable/disable automatic clipboard detection.
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            True if operation was successful, False otherwise
        """
        try:
            if enabled and not self.auto_detection_enabled:
                # Start monitoring
                self.clipboard_monitor.start_monitoring(self._on_clipboard_change)
                self.auto_detection_enabled = True
                return True
            elif not enabled and self.auto_detection_enabled:
                # Stop monitoring
                self.clipboard_monitor.stop_monitoring()
                self.auto_detection_enabled = False
                return True
            
            return True  # Already in desired state
            
        except Exception:
            return False
    
    def _on_clipboard_change(self, new_content: str) -> None:
        """Callback for clipboard change notifications.
        
        Args:
            new_content: New clipboard content
        """
        # This will be called from the monitoring thread
        # We'll just store the notification for the main thread to handle
        pass
    
    def check_clipboard_changes(self) -> Optional[str]:
        """Check for clipboard changes (for manual polling).
        
        Returns:
            New clipboard content if changed, None otherwise
        """
        if self.clipboard_monitor.check_for_changes():
            return self.clipboard_monitor.last_content
        return None
    
    def clear_working_text(self) -> None:
        """Clear current working text."""
        self.update_working_text("", "manual")
    
    def copy_to_clipboard(self) -> bool:
        """Copy current working text to clipboard.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.io_manager.set_output_text(self.current_text)
            return True
        except Exception:
            return False
    
    def get_display_text(self, max_length: int = 50) -> str:
        """Get truncated text for display purposes.
        
        Args:
            max_length: Maximum length for display
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(self.current_text) <= max_length:
            return self.current_text
        return self.current_text[:max_length] + "..."
    
    def get_time_since_update(self) -> str:
        """Get human-readable time since last update.
        
        Returns:
            Time string (e.g., "2 minutes ago")
        """
        delta = datetime.now() - self.last_update_time
        
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())} seconds ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() // 60)} minutes ago"
        else:
            return f"{int(delta.total_seconds() // 3600)} hours ago"
    
    def cleanup(self) -> None:
        """Clean up session resources."""
        if self.auto_detection_enabled:
            self.clipboard_monitor.stop_monitoring()


class CommandProcessor:
    """Processes interactive commands including clipboard operations."""
    
    CLIPBOARD_COMMANDS = {
        'refresh': 'Refresh input text from clipboard',
        'reload': 'Alias for refresh',
        'replace': 'Short alias for refresh',
        'auto': 'Toggle automatic clipboard detection',
        'status': 'Show current session status',
        'clear': 'Clear current working text',
        'copy': 'Copy working text to clipboard',
        'commands': 'Show all available commands',
        'cmd': 'Short alias for commands'
    }
    
    SYSTEM_COMMANDS = {
        'help': 'Show transformation rules',
        'h': 'Short alias for help',
        '?': 'Short alias for help',
        'quit': 'Exit application',
        'q': 'Short alias for quit',
        'exit': 'Exit application'
    }
    
    def __init__(self, session: InteractiveSession):
        """Initialize command processor.
        
        Args:
            session: InteractiveSession instance
        """
        self.session = session
    
    def is_command(self, input_text: str) -> bool:
        """Check if input text is a command (not a transformation rule).
        
        Args:
            input_text: User input text
            
        Returns:
            True if input is a command, False if it's a transformation rule
        """
        input_text = input_text.strip().lower()
        
        # Check system commands
        if input_text in self.SYSTEM_COMMANDS:
            return True
        
        # Check clipboard commands
        if input_text in self.CLIPBOARD_COMMANDS:
            return True
        
        # Check auto command with arguments
        if input_text.startswith('auto '):
            return True
        
        # If it starts with '/', it's a transformation rule
        if input_text.startswith('/'):
            return False
        
        # Default to command for unrecognized input
        return True
    
    def process_command(self, command: str) -> CommandResult:
        """Process interactive command and return result.
        
        Args:
            command: Command string to process
            
        Returns:
            CommandResult with operation result
        """
        command = command.strip().lower()
        
        # Handle system commands
        if command in ['help', 'h', '?']:
            return self._handle_help_command()
        
        if command in ['quit', 'q', 'exit']:
            return CommandResult(
                success=True,
                message="Goodbye!",
                should_continue=False
            )
        
        # Handle clipboard commands
        if command in ['refresh', 'reload', 'replace']:
            return self._handle_refresh_command()
        
        if command == 'status':
            return self._handle_status_command()
        
        if command == 'clear':
            return self._handle_clear_command()
        
        if command == 'copy':
            return self._handle_copy_command()
        
        if command in ['commands', 'cmd']:
            return self._handle_commands_command()
        
        if command.startswith('auto'):
            return self._handle_auto_command(command)
        
        # Unknown command
        return CommandResult(
            success=False,
            message=f"Unknown command: {command}. Type 'commands' for available commands."
        )
    
    def _handle_refresh_command(self) -> CommandResult:
        """Handle clipboard refresh command."""
        try:
            old_text = self.session.current_text
            success = self.session.refresh_from_clipboard()
            
            if not success:
                if self.session.current_text == old_text:
                    return CommandResult(
                        success=True,
                        message="No change detected - clipboard content is identical to current text."
                    )
                else:
                    return CommandResult(
                        success=False,
                        message="Failed to refresh from clipboard. Please check clipboard access."
                    )
            
            status = self.session.get_status_info()
            display_text = self.session.get_display_text()
            
            return CommandResult(
                success=True,
                message=f"✅ Refreshed from clipboard ({status.character_count} chars)\nNew text: '{display_text}'",
                updated_text=self.session.current_text
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error refreshing clipboard: {e}"
            )
    
    def _handle_status_command(self) -> CommandResult:
        """Handle status command."""
        status = self.session.get_status_info()
        display_text = self.session.get_display_text(100)
        time_since = self.session.get_time_since_update()
        
        status_lines = [
            f"📊 Session Status:",
            f"   Text: '{display_text}'",
            f"   Length: {status.character_count} characters",
            f"   Source: {status.text_source}",
            f"   Last updated: {time_since}",
            f"   Auto-detection: {'ON' if status.auto_detection_enabled else 'OFF'}",
            f"   Monitor active: {'Yes' if status.clipboard_monitor_active else 'No'}"
        ]
        
        return CommandResult(
            success=True,
            message="\n".join(status_lines)
        )
    
    def _handle_clear_command(self) -> CommandResult:
        """Handle clear command."""
        self.session.clear_working_text()
        return CommandResult(
            success=True,
            message="✅ Working text cleared. Enter new text or use 'refresh' to load from clipboard.",
            updated_text=""
        )
    
    def _handle_copy_command(self) -> CommandResult:
        """Handle copy command."""
        if not self.session.current_text:
            return CommandResult(
                success=False,
                message="No text to copy. Working text is empty."
            )
        
        success = self.session.copy_to_clipboard()
        if success:
            return CommandResult(
                success=True,
                message=f"✅ Copied {len(self.session.current_text)} characters to clipboard."
            )
        else:
            return CommandResult(
                success=False,
                message="Failed to copy text to clipboard."
            )
    
    def _handle_auto_command(self, command: str) -> CommandResult:
        """Handle auto-detection command."""
        parts = command.split()
        
        if len(parts) == 1:
            # Toggle auto-detection
            current_status = self.session.get_status_info()
            new_state = not current_status.auto_detection_enabled
        elif len(parts) == 2:
            # Explicit on/off
            arg = parts[1].lower()
            if arg in ['on', 'enable', 'true', '1']:
                new_state = True
            elif arg in ['off', 'disable', 'false', '0']:
                new_state = False
            else:
                return CommandResult(
                    success=False,
                    message="Invalid argument for 'auto'. Use 'on' or 'off'."
                )
        else:
            return CommandResult(
                success=False,
                message="Usage: 'auto' or 'auto on/off'"
            )
        
        success = self.session.toggle_auto_detection(new_state)
        if success:
            state_text = "enabled" if new_state else "disabled"
            return CommandResult(
                success=True,
                message=f"✅ Auto-detection {state_text}."
            )
        else:
            return CommandResult(
                success=False,
                message="Failed to toggle auto-detection."
            )
    
    def _handle_commands_command(self) -> CommandResult:
        """Handle commands list command."""
        lines = [
            "📋 Available Interactive Commands:",
            "",
            "Clipboard Operations:",
        ]
        
        for cmd, desc in self.CLIPBOARD_COMMANDS.items():
            lines.append(f"  {cmd:<12} - {desc}")
        
        lines.extend([
            "",
            "System Commands:",
        ])
        
        for cmd, desc in self.SYSTEM_COMMANDS.items():
            lines.append(f"  {cmd:<12} - {desc}")
        
        lines.extend([
            "",
            "Transformation Rules:",
            "  /t/l         - Trim and lowercase",
            "  /enc         - Encrypt text",
            "  /dec         - Decrypt text",
            "  /S '-'       - Slugify with hyphen",
            "  /r 'old' 'new' - Replace text",
            "  ... (type 'help' for complete list)",
        ])
        
        return CommandResult(
            success=True,
            message="\n".join(lines)
        )
    
    def _handle_help_command(self) -> CommandResult:
        """Handle help command - this will be handled by ApplicationInterface."""
        return CommandResult(
            success=True,
            message="SHOW_HELP",  # Special message to trigger help display
            should_continue=True
        )


class DaemonMode:
    """Daemon mode for continuous clipboard monitoring and transformation."""
    
    def __init__(self, config_manager: ConfigurationManager, transformation_engine: TextTransformationEngine):
        """Initialize daemon mode.
        
        Args:
            config_manager: Configuration manager instance
            transformation_engine: Text transformation engine instance
        """
        self.config_manager = config_manager
        self.transformation_engine = transformation_engine
        self.io_manager = InputOutputManager()
        
        # Load daemon configuration
        try:
            daemon_config_path = Path("config/daemon_config.json")
            if daemon_config_path.exists():
                with open(daemon_config_path, 'r', encoding='utf-8') as f:
                    self.daemon_config = json.load(f)
            else:
                self.daemon_config = self._get_default_daemon_config()
        except Exception as e:
            print(f"Warning: Could not load daemon config: {e}")
            self.daemon_config = self._get_default_daemon_config()
        
        # Initialize state
        self.is_running = False
        self.last_clipboard_content = ""
        self.active_rules = []
        self.clipboard_monitor = None
        self.stats = {
            'transformations_applied': 0,
            'start_time': None,
            'last_transformation': None
        }
    
    def _get_default_daemon_config(self) -> Dict[str, Any]:
        """Get default daemon configuration."""
        return {
            "daemon_mode": {
                "enabled": True,
                "check_interval": 0.5,
                "max_clipboard_size": 1048576
            },
            "auto_transformation": {
                "enabled": True,
                "default_rules": [],
                "active_preset": "",
                "custom_rules": []
            },
            "clipboard_monitoring": {
                "enabled": True,
                "ignore_empty": True,
                "ignore_duplicates": True,
                "min_length": 1,
                "max_length": 10000
            }
        }
    
    def set_transformation_rules(self, rules: List[str]) -> None:
        """Set active transformation rules.
        
        Args:
            rules: List of transformation rule strings
        """
        self.active_rules = rules
        print(f"[DAEMON] Active rules set: {' -> '.join(rules) if rules else 'None'}")
    
    def set_preset(self, preset_name: str) -> bool:
        """Set transformation preset.
        
        Args:
            preset_name: Name of the preset to activate
            
        Returns:
            True if preset was set successfully, False otherwise
        """
        presets = self.daemon_config.get("auto_transformation", {}).get("rule_presets", {})
        
        if preset_name in presets:
            preset_rules = presets[preset_name]
            # Handle both string and list formats
            if isinstance(preset_rules, str):
                self.active_rules = [preset_rules]
            else:
                self.active_rules = preset_rules
            
            self.daemon_config["auto_transformation"]["active_preset"] = preset_name
            print(f"[DAEMON] Preset '{preset_name}' activated: {' -> '.join(self.active_rules)}")
            return True
        else:
            print(f"[DAEMON] Preset '{preset_name}' not found. Available: {list(presets.keys())}")
            return False
    
    def start_monitoring(self) -> None:
        """Start daemon monitoring in background thread."""
        if self.is_running:
            print("[DAEMON] Already running")
            return
        
        if not CLIPBOARD_AVAILABLE:
            print("[DAEMON] Error: Clipboard functionality not available")
            return
        
        if not self.active_rules:
            print("[DAEMON] No transformation rules set. Use 'preset' or 'rules' to configure.")
            return
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        print(f"[DAEMON] Check interval: {self.daemon_config['daemon_mode']['check_interval']}s")
        print(f"[DAEMON] Active transformation: {' -> '.join(self.active_rules)}")
        
        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
    
    def start(self) -> None:
        """Start daemon mode (legacy method for compatibility)."""
        if self.is_running:
            print("[DAEMON] Already running")
            return
        
        if not CLIPBOARD_AVAILABLE:
            print("[DAEMON] Error: Clipboard functionality not available")
            return
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        print("[DAEMON] Starting clipboard monitoring...")
        print(f"[DAEMON] Check interval: {self.daemon_config['daemon_mode']['check_interval']}s")
        
        if self.active_rules:
            print(f"[DAEMON] Active transformation: {' -> '.join(self.active_rules)}")
        else:
            print("[DAEMON] No transformation rules set. Use 'set_preset' or 'set_rules' to configure.")
        
        print("[DAEMON] Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            self._monitor_clipboard()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        """Stop daemon mode."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Show statistics
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            print(f"\n[DAEMON] Stopped after {runtime}")
            print(f"[DAEMON] Transformations applied: {self.stats['transformations_applied']}")
        
        print("[DAEMON] Clipboard monitoring stopped")
    
    def _monitor_clipboard(self) -> None:
        """Main clipboard monitoring loop."""
        check_interval = self.daemon_config["daemon_mode"]["check_interval"]
        
        while self.is_running:
            try:
                current_content = self.io_manager.get_clipboard_text()
                
                if self._should_process_content(current_content):
                    self._process_clipboard_content(current_content)
                
                # Use shorter sleep intervals for better responsiveness
                for _ in range(int(check_interval * 10)):
                    if not self.is_running:
                        break
                    time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\r[DAEMON] Error monitoring clipboard: {e}", flush=True)
                time.sleep(check_interval)
    
    def _should_process_content(self, content: str) -> bool:
        """Check if clipboard content should be processed.
        
        Args:
            content: Clipboard content to check
            
        Returns:
            True if content should be processed, False otherwise
        """
        config = self.daemon_config["clipboard_monitoring"]
        
        # Check if monitoring is enabled
        if not config.get("enabled", True):
            return False
        
        # Check if we have active rules
        if not self.active_rules:
            return False
        
        # Check if content is different from last processed (both input and output)
        if config.get("ignore_duplicates", True):
            if content == self.last_clipboard_content:
                return False
            # Also check against the original content before transformation
            if hasattr(self, '_last_input_content') and content == self._last_input_content:
                return False
        
        # Check if content is empty
        if config.get("ignore_empty", True) and not content.strip():
            return False
        
        # Check content length
        min_length = config.get("min_length", 1)
        max_length = config.get("max_length", 10000)
        
        if len(content) < min_length or len(content) > max_length:
            return False
        
        # Check ignore patterns
        ignore_patterns = config.get("ignore_patterns", [])
        for pattern in ignore_patterns:
            if re.match(pattern, content):
                return False
        
        return True
    
    def _process_clipboard_content(self, content: str) -> None:
        """Process clipboard content with active transformation rules.
        
        Args:
            content: Clipboard content to process
        """
        try:
            # Apply transformation rules sequentially
            result = content
            for rule in self.active_rules:
                result = self.transformation_engine.apply_transformations(result, rule)
            
            # Skip if transformation didn't change the content
            if result == content:
                return
            
            # Update clipboard with transformed content (silently)
            try:
                import pyperclip
                pyperclip.copy(result)
            except Exception:
                pass  # Silently fail if clipboard update fails
            
            # Update statistics and state
            self.stats['transformations_applied'] += 1
            self.stats['last_transformation'] = datetime.now()
            self.last_clipboard_content = result
            
            # Show transformation result (only when content actually changed)
            display_input = content[:50] + "..." if len(content) > 50 else content
            display_output = result[:50] + "..." if len(result) > 50 else result
            
            # Use \r to overwrite current line and avoid interfering with command input
            print(f"\r[DAEMON] Transformed: '{display_input}' -> '{display_output}'", end='', flush=True)
            print()  # Add newline after transformation message
            
        except Exception as e:
            print(f"\r[DAEMON] Error processing content: {e}", flush=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get daemon status information.
        
        Returns:
            Dictionary containing status information
        """
        status = {
            'running': self.is_running,
            'active_rules': self.active_rules,
            'active_preset': self.daemon_config.get("auto_transformation", {}).get("active_preset", ""),
            'stats': self.stats.copy()
        }
        
        if self.stats['start_time']:
            status['runtime'] = str(datetime.now() - self.stats['start_time'])
        
        return status


class ApplicationInterface:
    """Main application interface and user interaction handler."""
    
    def __init__(self):
        """Initialize application interface."""
        self.config_manager = ConfigurationManager()
        self.transformation_engine = TextTransformationEngine(self.config_manager)
        self.io_manager = InputOutputManager()
        self.daemon_mode = DaemonMode(self.config_manager, self.transformation_engine)
    
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
        print("  String_Multitool.py --daemon           # Daemon mode (continuous monitoring)")
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
        
        print()
        print("Daemon Mode:")
        print("  String_Multitool.py --daemon")
        print("  • Continuous clipboard monitoring")
        print("  • Automatic transformation application")
        print("  • Configurable transformation presets")
        print("  • Background operation")
        print("  • Real-time clipboard processing")
    
    def run_interactive_mode(self, input_text: str) -> None:
        """Run application in interactive mode with enhanced clipboard functionality.
        
        Args:
            input_text: Initial input text
        """
        # Initialize interactive session
        session = InteractiveSession(self.io_manager, self.transformation_engine)
        
        # Determine initial text source
        if sys.stdin.isatty():
            session.initialize_with_text(input_text, "clipboard")
        else:
            session.initialize_with_text(input_text, "pipe")
        
        command_processor = CommandProcessor(session)
        
        # Display initial session info
        self._display_session_header(session)
        
        try:
            while True:
                try:
                    # Check for clipboard changes if auto-detection is enabled
                    if session.auto_detection_enabled:
                        new_content = session.check_clipboard_changes()
                        if new_content is not None and new_content != session.current_text:
                            print(f"\n🔔 Clipboard changed! New content available ({len(new_content)} chars)")
                            print("   Type 'refresh' to load new content or continue with current text.")
                    
                    # Get user input
                    try:
                        user_input = input("Rules: ").strip()
                    except EOFError:
                        print("\nGoodbye!")
                        break
                    
                    if not user_input:
                        print("Please enter a rule, command, or 'help'")
                        continue
                    
                    # Process command or transformation rule
                    if command_processor.is_command(user_input):
                        result = command_processor.process_command(user_input)
                        
                        if result.message == "SHOW_HELP":
                            self.display_help()
                            continue
                        
                        print(result.message)
                        
                        if result.updated_text is not None:
                            # Text was updated by command
                            pass
                        
                        if not result.should_continue:
                            break
                            
                    else:
                        # Handle transformation rules
                        try:
                            # Always get fresh clipboard content for transformation rules
                            # unless the input came from pipe initially
                            if session.text_source != "pipe":
                                try:
                                    fresh_content = self.io_manager.get_clipboard_text()
                                    # Show if clipboard content changed
                                    if fresh_content != session.current_text:
                                        old_display = session.current_text[:30] + "..." if len(session.current_text) > 30 else session.current_text
                                        new_display = fresh_content[:30] + "..." if len(fresh_content) > 30 else fresh_content
                                        print(f"[CLIPBOARD] Using fresh content: '{old_display}' -> '{new_display}'")
                                    
                                    session.update_working_text(fresh_content, "clipboard")
                                except Exception as e:
                                    print(f"Warning: Could not read clipboard: {e}")
                                    print("Using current working text instead.")
                            
                            # Apply transformations to current working text
                            result = self.transformation_engine.apply_transformations(session.current_text, user_input)
                            self.io_manager.set_output_text(result)
                            
                            # Update session with result
                            session.update_working_text(result, "transformation")
                            
                            # Display result
                            if user_input.strip() == '/enc':
                                print(f"Result: '{result}'")
                                print("(Full encrypted text copied to clipboard)")
                            else:
                                display_result = result[:100] + ('...' if len(result) > 100 else '')
                                print(f"Result: '{display_result}'")
                            
                        except Exception as e:
                            print(f"❌ Transformation error: {e}")
                    
                    print()
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print("Type 'commands' for available commands or 'help' for transformation rules")
        
        finally:
            # Clean up session resources
            session.cleanup()
    
    def _display_session_header(self, session: InteractiveSession) -> None:
        """Display interactive session header with status information.
        
        Args:
            session: InteractiveSession instance
        """
        status = session.get_status_info()
        display_text = session.get_display_text()
        
        print("String_Multitool - Interactive Mode")
        print("=" * 45)
        print(f"Input text: '{display_text}' ({status.character_count} chars, from {status.text_source})")
        print(f"Auto-detection: {'ON' if status.auto_detection_enabled else 'OFF'}")
        print()
        print("Available commands: help, refresh, auto, status, clear, copy, commands, quit")
        print("Enter transformation rules (e.g., /t/l) or command:")
        if status.text_source == "clipboard":
            print("Note: Transformation rules will use the latest clipboard content")
        print()
    
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
    
    def run_daemon_mode(self) -> None:
        """Run application in daemon mode."""
        print("String_Multitool - Daemon Mode")
        print("=" * 40)
        print("Continuous clipboard monitoring and transformation")
        print()
        
        # Show available presets
        daemon_config_path = Path("config/daemon_config.json")
        if daemon_config_path.exists():
            try:
                with open(daemon_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    presets = config.get("auto_transformation", {}).get("rule_presets", {})
                    
                    if presets:
                        print("Available presets:")
                        for name, rules in presets.items():
                            if isinstance(rules, str):
                                print(f"  {name}: {rules}")
                            else:
                                print(f"  {name}: {' -> '.join(rules)}")
                        print()
            except Exception:
                pass
        
        print("Commands:")
        print("  preset <name>     - Set transformation preset")
        print("  rules <rules>     - Set custom transformation rules (e.g., '/t/l')")
        print("  start             - Start daemon monitoring")
        print("  stop              - Stop daemon monitoring")
        print("  status            - Show daemon status")
        print("  quit              - Exit daemon mode")
        print()
        
        while True:
            try:
                try:
                    user_input = input("Daemon> ").strip()
                except EOFError:
                    print("\nGoodbye!")
                    break
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command in ['quit', 'q', 'exit']:
                    if self.daemon_mode.is_running:
                        self.daemon_mode.stop()
                    print("Goodbye!")
                    break
                
                elif command == 'preset':
                    if len(parts) < 2:
                        print("Usage: preset <name>")
                        continue
                    
                    preset_name = parts[1]
                    self.daemon_mode.set_preset(preset_name)
                
                elif command == 'rules':
                    if len(parts) < 2:
                        print("Usage: rules <rule_string>")
                        print("Example: rules /t/l")
                        continue
                    
                    rule_string = ' '.join(parts[1:])
                    try:
                        # Validate rules by parsing them
                        parsed_rules = self.transformation_engine.parse_rule_string(rule_string)
                        rule_list = [rule_string]  # Store as single rule string for sequential application
                        self.daemon_mode.set_transformation_rules(rule_list)
                    except Exception as e:
                        print(f"Error: Invalid rule string: {e}")
                
                elif command == 'start':
                    if self.daemon_mode.is_running:
                        print("[DAEMON] Already running")
                    else:
                        # Start daemon monitoring without blocking command input
                        self.daemon_mode.start_monitoring()
                        print("[DAEMON] Monitoring started in background")
                
                elif command == 'stop':
                    self.daemon_mode.stop()
                
                elif command == 'status':
                    status = self.daemon_mode.get_status()
                    print(f"Status: {'Running' if status['running'] else 'Stopped'}")
                    print(f"Active rules: {' -> '.join(status['active_rules']) if status['active_rules'] else 'None'}")
                    print(f"Active preset: {status['active_preset'] or 'None'}")
                    print(f"Transformations applied: {status['stats']['transformations_applied']}")
                    if status.get('runtime'):
                        print(f"Runtime: {status['runtime']}")
                
                elif command == 'help':
                    print("Daemon Mode Commands:")
                    print("  preset <name>     - Set transformation preset")
                    print("  rules <rules>     - Set custom transformation rules")
                    print("  start             - Start daemon monitoring")
                    print("  stop              - Stop daemon monitoring")
                    print("  status            - Show daemon status")
                    print("  quit              - Exit daemon mode")
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                if self.daemon_mode.is_running:
                    self.daemon_mode.stop()
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run(self) -> None:
        """Main application entry point."""
        # Parse command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['-h', '--help', 'help']:
                self.display_help()
                return
            
            if sys.argv[1] in ['-d', '--daemon', 'daemon']:
                self.run_daemon_mode()
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