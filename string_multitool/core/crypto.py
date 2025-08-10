"""
Cryptography management for String_Multitool.

This module handles RSA encryption and decryption operations with
enhanced security features and proper error handling.
"""

from __future__ import annotations

import base64
import secrets
from pathlib import Path
from typing import Any, TYPE_CHECKING

# Import logging utilities
from ..utils.logger import get_logger, log_info, log_error, log_warning, log_debug

from ..exceptions import CryptographyError, ConfigurationError
from .types import ConfigurableComponent, CryptoManagerProtocol, ConfigManagerProtocol

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
else:
    RSAPrivateKey = Any
    RSAPublicKey = Any


class CryptographyManager(ConfigurableComponent[dict[str, Any]]):
    """Manages RSA encryption and decryption operations with enhanced security.
    
    This class provides hybrid encryption using AES for data and RSA for key exchange,
    following cryptographic best practices.
    """
    
    def __init__(self, config_manager: ConfigManagerProtocol) -> None:
        """Initialize cryptography manager.
        
        Args:
            config_manager: Configuration manager instance
            
        Raises:
            CryptographyError: If cryptography library is not available
            ConfigurationError: If security configuration is invalid
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptographyError(
                "Cryptography library not available. Install with: pip install cryptography"
            )
        
        try:
            security_config = config_manager.load_security_config()
            super().__init__(security_config)
            
            # Instance variable annotations following PEP 526
            self.config_manager: ConfigManagerProtocol = config_manager
            self.rsa_config: dict[str, Any] = security_config["rsa_encryption"]
            self.key_directory: Path = Path(self.rsa_config["key_directory"])
            self.private_key_path: Path = self.key_directory / self.rsa_config["private_key_file"]
            self.public_key_path: Path = self.key_directory / f"{self.rsa_config['private_key_file']}.pub"
            
        except KeyError as e:
            raise ConfigurationError(
                f"Missing required security configuration: {e}",
                {"missing_key": str(e)}
            ) from e
        except Exception as e:
            raise CryptographyError(
                f"Failed to initialize cryptography manager: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def encrypt_text(self, text: str) -> str:
        """Encrypt text using hybrid AES+RSA encryption.
        
        Args:
            text: Text to encrypt
            
        Returns:
            Base64 encoded encrypted data
            
        Raises:
            CryptographyError: If encryption fails
        """
        try:
            if not text:
                raise CryptographyError("Cannot encrypt empty text")
            
            # Generate AES key and IV
            aes_key = secrets.token_bytes(self.rsa_config["aes_key_size"])
            aes_iv = secrets.token_bytes(self.rsa_config["aes_iv_size"])
            
            # Encrypt data with AES
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Pad text to AES block size
            text_bytes = text.encode('utf-8')
            padding_length = 16 - (len(text_bytes) % 16)
            padded_text = text_bytes + bytes([padding_length] * padding_length)
            
            encrypted_data = encryptor.update(padded_text) + encryptor.finalize()
            
            # Encrypt AES key with RSA
            _, public_key = self.ensure_key_pair()
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted key, IV, and data
            combined_data = encrypted_aes_key + aes_iv + encrypted_data
            return base64.b64encode(combined_data).decode('ascii')
            
        except Exception as e:
            raise CryptographyError(
                f"Encryption failed: {e}",
                {"text_length": len(text), "error_type": type(e).__name__}
            ) from e
    
    def decrypt_text(self, text: str) -> str:
        """Decrypt text using hybrid AES+RSA decryption.
        
        Args:
            text: Base64 encoded encrypted data
            
        Returns:
            Decrypted text
            
        Raises:
            CryptographyError: If decryption fails
        """
        try:
            if not text:
                raise CryptographyError("Cannot decrypt empty text")
            
            # Decode base64
            combined_data = base64.b64decode(text.encode('ascii'))
            
            # Extract components
            key_size = self.rsa_config["key_size"] // 8  # Convert bits to bytes
            encrypted_aes_key = combined_data[:key_size]
            aes_iv = combined_data[key_size:key_size + self.rsa_config["aes_iv_size"]]
            encrypted_data = combined_data[key_size + self.rsa_config["aes_iv_size"]:]
            
            # Decrypt AES key with RSA
            private_key, _ = self.ensure_key_pair()
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data with AES
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_text = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            padding_length = padded_text[-1]
            text_bytes = padded_text[:-padding_length]
            
            return text_bytes.decode('utf-8')
            
        except Exception as e:
            raise CryptographyError(
                f"Decryption failed: {e}",
                {"encrypted_length": len(text), "error_type": type(e).__name__}
            ) from e
    
    def ensure_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Ensure RSA key pair exists, create if not found.
        
        Returns:
            Tuple of (private_key, public_key)
            
        Raises:
            CryptographyError: If key operations fail
        """
        try:
            self._ensure_key_directory()
            
            # Check if keys exist and are valid
            if self.private_key_path.exists() and self.public_key_path.exists():
                try:
                    return self._load_key_pair()
                except Exception:
                    # Keys are corrupted, regenerate
                    pass
            
            # Generate new key pair
            logger = get_logger(__name__)
            log_info(logger, "Generating new RSA key pair...")
            return self._generate_key_pair()
            
        except Exception as e:
            raise CryptographyError(
                f"Key pair management failed: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def _ensure_key_directory(self) -> None:
        """Ensure key directory exists with proper permissions."""
        try:
            self.key_directory.mkdir(mode=0o700, exist_ok=True)
        except Exception as e:
            raise CryptographyError(
                f"Failed to create key directory: {e}",
                {"directory": str(self.key_directory)}
            ) from e
    
    def _generate_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate a new RSA key pair with enhanced security settings."""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=self.rsa_config["public_exponent"],
                key_size=self.rsa_config["key_size"],
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Save keys
            self._save_key_pair(private_key, public_key)
            
            return private_key, public_key
            
        except Exception as e:
            raise CryptographyError(
                f"Key generation failed: {e}",
                {"key_size": self.rsa_config["key_size"]}
            ) from e
    
    def _save_key_pair(self, private_key: RSAPrivateKey, public_key: RSAPublicKey) -> None:
        """Save key pair to files with secure permissions."""
        try:
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Write keys to files
            with open(self.private_key_path, 'wb') as file:
                file.write(private_pem)
            
            with open(self.public_key_path, 'wb') as file:
                file.write(public_pem)
            
            # Set secure file permissions using pathlib
            try:
                self.private_key_path.chmod(int(self.rsa_config["private_key_permissions"], 8))
                self.public_key_path.chmod(int(self.rsa_config["public_key_permissions"], 8))
            except OSError:
                # Windows doesn't support chmod the same way
                pass
            
            logger = get_logger(__name__)
            log_info(logger, f"RSA key pair saved securely:")
            log_info(logger, f"   Private key: {self.private_key_path}")
            log_info(logger, f"   Public key:  {self.public_key_path}")
            
        except Exception as e:
            raise CryptographyError(
                f"Failed to save key pair: {e}",
                {"private_path": str(self.private_key_path), "public_path": str(self.public_key_path)}
            ) from e
    
    def _load_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Load existing key pair from files."""
        try:
            with open(self.private_key_path, 'rb') as file:
                private_key = serialization.load_pem_private_key(
                    file.read(),
                    password=None,
                    backend=default_backend()
                )
            
            with open(self.public_key_path, 'rb') as file:
                public_key_data = serialization.load_pem_public_key(
                    file.read(),
                    backend=default_backend()
                )
            
            # Ensure we have RSA keys
            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise CryptographyError("Private key is not an RSA key")
            if not isinstance(public_key_data, rsa.RSAPublicKey):
                raise CryptographyError("Public key is not an RSA key")
            
            return private_key, public_key_data
            
        except Exception as e:
            raise CryptographyError(
                f"Failed to load key pair: {e}",
                {"private_path": str(self.private_key_path), "public_path": str(self.public_key_path)}
            ) from e
    
    def generate_key_pair(self) -> None:
        """Generate new RSA key pair.
        
        Raises:
            CryptographyError: If key generation fails
        """
        try:
            self._generate_key_pair()
        except Exception as e:
            raise CryptographyError(
                f"Key pair generation failed: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def load_keys(self) -> bool:
        """Load existing RSA key pair.
        
        Returns:
            True if keys loaded successfully, False otherwise
        """
        try:
            if self.private_key_path.exists() and self.public_key_path.exists():
                self._load_key_pair()
                return True
            return False
        except Exception:
            return False