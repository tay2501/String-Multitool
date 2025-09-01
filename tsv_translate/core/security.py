"""Database security implementation using SQLCipher.

Educational implementation of database encryption with proper
key management and security best practices.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .exceptions import TSVTranslateError


class SecurityManager:
    """Database security and encryption management.
    
    Educational implementation demonstrating:
    - Proper key derivation using PBKDF2
    - Secure key storage and management
    - Database URL transformation for SQLCipher
    - Configuration-based security settings
    """
    
    def __init__(self, security_config: Dict[str, Any]) -> None:
        """Initialize security manager with configuration.
        
        Args:
            security_config: Security-related configuration options
        """
        self._config = security_config
        self._master_key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None
    
    def is_encryption_enabled(self) -> bool:
        """Check if database encryption is enabled."""
        return bool(self._config.get("enable_encryption", False))
    
    def get_secure_database_url(self, base_url: str) -> str:
        """Transform database URL for encrypted database access.
        
        For SQLite with SQLCipher integration, adds necessary
        encryption parameters to the connection string.
        
        Args:
            base_url: Original database URL
            
        Returns:
            Enhanced URL with encryption parameters
        """
        if not self.is_encryption_enabled():
            return base_url
        
        if not base_url.startswith("sqlite:"):
            raise TSVTranslateError("Encryption currently only supported for SQLite")
        
        # Get or create encryption key
        key = self._get_or_create_key()
        
        # Transform URL for SQLCipher
        # Note: This is educational - actual SQLCipher integration
        # would require pysqlcipher3 or similar SQLCipher binding
        encrypted_params = f"?cipher=aes-256-gcm&key={key.hex()}"
        
        return base_url + encrypted_params
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive string data.
        
        Used for encrypting configuration values or other
        sensitive information that needs storage protection.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Base64-encoded encrypted data
        """
        if not self.is_encryption_enabled():
            return data
        
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('ascii')
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive string data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Original plain text data
        """
        if not self.is_encryption_enabled():
            return encrypted_data
        
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('ascii'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise TSVTranslateError(f"Decryption failed: {e}")
    
    def _get_or_create_key(self) -> bytes:
        """Get existing encryption key or create new one.
        
        Demonstrates secure key management with proper file permissions
        and key derivation from password.
        """
        key_file = Path("data/.encryption_key")
        
        if key_file.exists():
            return self._load_key(key_file)
        else:
            return self._create_key(key_file)
    
    def _load_key(self, key_file: Path) -> bytes:
        """Load encryption key from secure storage."""
        try:
            with open(key_file, 'rb') as f:
                salt = f.read(32)  # First 32 bytes are salt
                key_hash = f.read(32)  # Next 32 bytes are derived key
            
            # Derive key from master password and salt
            password = self._get_master_password()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self._config.get("key_derivation_iterations", 100000),
            )
            derived_key = kdf.derive(password.encode('utf-8'))
            
            # Verify key integrity
            if derived_key != key_hash:
                raise TSVTranslateError("Key integrity check failed")
            
            return derived_key
            
        except (OSError, ValueError) as e:
            raise TSVTranslateError(f"Failed to load encryption key: {e}")
    
    def _create_key(self, key_file: Path) -> bytes:
        """Create new encryption key with secure storage."""
        try:
            # Ensure data directory exists
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate random salt
            salt = os.urandom(32)
            
            # Derive key from master password
            password = self._get_master_password()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self._config.get("key_derivation_iterations", 100000),
            )
            derived_key = kdf.derive(password.encode('utf-8'))
            
            # Store salt and key hash securely
            with open(key_file, 'wb') as f:
                f.write(salt)
                f.write(derived_key)
            
            # Set secure file permissions (owner read/write only)
            if hasattr(os, 'chmod'):
                os.chmod(key_file, 0o600)
            
            return derived_key
            
        except OSError as e:
            raise TSVTranslateError(f"Failed to create encryption key: {e}")
    
    def _get_master_password(self) -> str:
        """Get master password for key derivation.
        
        Educational implementation - in production, this might:
        - Prompt user for password
        - Use system keychain/credential manager
        - Derive from hardware security module
        - Use environment variable with proper validation
        """
        password = os.environ.get("TSV_CONVERTER_KEY")
        
        if not password:
            # Fallback to deterministic password based on system
            # This is NOT secure for production use
            system_info = f"{os.getlogin()}-{os.getcwd()}"
            password = hashlib.sha256(system_info.encode()).hexdigest()[:16]
        
        return password
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for symmetric encryption."""
        if not self._fernet:
            key = self._get_or_create_key()
            # Fernet requires base64-encoded 32-byte key
            fernet_key = base64.urlsafe_b64encode(key)
            self._fernet = Fernet(fernet_key)
        
        return self._fernet


def create_secure_database_url(config: Dict[str, Any]) -> str:
    """Create database URL with security enhancements.
    
    Factory function for creating properly configured database URLs
    with optional encryption support.
    
    Args:
        config: Application configuration including security settings
        
    Returns:
        Database URL with security enhancements applied
    """
    base_url = config.get("database_url", "sqlite:///data/tsv_converter.db")
    
    security_config = config.get("security", {})
    if not security_config.get("enable_encryption", False):
        return str(base_url)
    
    security_manager = SecurityManager(security_config)
    return security_manager.get_secure_database_url(base_url)