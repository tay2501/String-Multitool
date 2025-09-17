"""
Cryptographic transformation operations for String_Multitool.

This module provides dedicated cryptographic transformation functionality
following the single responsibility principle and EAFP error handling pattern.
"""

from __future__ import annotations

import base64
import binascii
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import CryptoManagerProtocol

from ..exceptions import TransformationError
from .constants import CRYPTO_CONSTANTS, ERROR_CONTEXT_KEYS
from .transformation_base import TransformationBase


class CryptoTransformations(TransformationBase):
    """Dedicated cryptographic transformation operations handler.

    This class handles all cryptographic operations including encryption,
    decryption, and Base64 encoding/decoding with proper error handling.
    """

    def __init__(self, crypto_manager: CryptoManagerProtocol | None = None) -> None:
        """Initialize crypto transformations with dependency injection.

        Args:
            crypto_manager: Optional cryptography manager instance
        """
        super().__init__({})  # No configuration needed for crypto operations
        self.crypto_manager = crypto_manager
        self._input_text: str = ""
        self._output_text: str = ""
        self._transformation_rule: str = ""

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set the cryptography manager for encryption/decryption operations.

        Args:
            crypto_manager: Cryptography manager instance
        """
        self.crypto_manager = crypto_manager

    def transform(self, text: str, operation: str = "encode") -> str:
        """Apply cryptographic transformation to text.

        Args:
            text: Input text to transform
            operation: Type of operation (encrypt, decrypt, encode, decode)

        Returns:
            Transformed text

        Raises:
            TransformationError: If transformation fails
        """
        try:
            if operation == "encrypt":
                return self.encrypt_text(text)
            elif operation == "decrypt":
                return self.decrypt_text(text)
            elif operation == "encode":
                return self.base64_encode(text)
            elif operation == "decode":
                return self.base64_decode(text)
            else:
                raise TransformationError(
                    f"Unknown crypto operation: {operation}",
                    {ERROR_CONTEXT_KEYS.OPERATION: operation},
                )
        except Exception as e:
            raise TransformationError(
                f"Cryptographic transformation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: operation,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                },
            ) from e

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using configured crypto manager.

        Args:
            text: Plain text to encrypt

        Returns:
            Encrypted text (Base64 encoded)

        Raises:
            TransformationError: If encryption fails or crypto manager not set
        """
        try:
            self._input_text = text
            self._transformation_rule = "encrypt"

            if not self.crypto_manager:
                raise TransformationError(
                    CRYPTO_CONSTANTS.NO_CRYPTO_MANAGER_ERROR,
                    {ERROR_CONTEXT_KEYS.OPERATION: "encrypt"},
                )

            # EAFP: Try encryption directly
            encrypted_bytes = self.crypto_manager.encrypt(text.encode("utf-8"))
            result = base64.b64encode(encrypted_bytes).decode("ascii")
            self._output_text = result
            return result

        except AttributeError as e:
            raise TransformationError(
                "Invalid crypto manager interface",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "encrypt",
                    ERROR_CONTEXT_KEYS.MANAGER_TYPE: type(self.crypto_manager).__name__,
                },
            ) from e
        except Exception as e:
            raise TransformationError(
                f"Encryption failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "encrypt",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt Base64 encoded encrypted text.

        Args:
            encrypted_text: Base64 encoded encrypted text

        Returns:
            Decrypted plain text

        Raises:
            TransformationError: If decryption fails or crypto manager not set
        """
        try:
            self._input_text = encrypted_text
            self._transformation_rule = "decrypt"

            if not self.crypto_manager:
                raise TransformationError(
                    CRYPTO_CONSTANTS.NO_CRYPTO_MANAGER_ERROR,
                    {ERROR_CONTEXT_KEYS.OPERATION: "decrypt"},
                )

            # EAFP: Try decryption directly
            encrypted_bytes = base64.b64decode(encrypted_text.encode("ascii"))
            decrypted_bytes = self.crypto_manager.decrypt(encrypted_bytes)
            result = decrypted_bytes.decode("utf-8")
            self._output_text = result
            return result

        except (ValueError, binascii.Error) as e:
            raise TransformationError(
                "Invalid Base64 encoded data for decryption",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "decrypt",
                    ERROR_CONTEXT_KEYS.DATA_FORMAT: "base64",
                },
            ) from e
        except AttributeError as e:
            raise TransformationError(
                "Invalid crypto manager interface",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "decrypt",
                    ERROR_CONTEXT_KEYS.MANAGER_TYPE: type(self.crypto_manager).__name__,
                },
            ) from e
        except Exception as e:
            raise TransformationError(
                f"Decryption failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "decrypt",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(encrypted_text),
                },
            ) from e

    def base64_encode(self, text: str) -> str:
        """Encode text to Base64.

        Args:
            text: Plain text to encode

        Returns:
            Base64 encoded text

        Raises:
            TransformationError: If encoding fails
        """
        try:
            # EAFP: Try encoding directly
            return base64.b64encode(text.encode("utf-8")).decode("ascii")
        except Exception as e:
            raise TransformationError(
                f"Base64 encoding failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "base64_encode",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e

    def base64_decode(self, encoded_text: str) -> str:
        """Decode Base64 encoded text.

        Args:
            encoded_text: Base64 encoded text

        Returns:
            Decoded plain text

        Raises:
            TransformationError: If decoding fails
        """
        try:
            # EAFP: Try decoding directly
            return base64.b64decode(encoded_text.encode("ascii")).decode("utf-8")
        except (ValueError, binascii.Error) as e:
            raise TransformationError(
                "Invalid Base64 encoded data",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "base64_decode",
                    ERROR_CONTEXT_KEYS.DATA_FORMAT: "base64",
                },
            ) from e
        except UnicodeDecodeError as e:
            raise TransformationError(
                "Base64 decoded data is not valid UTF-8",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "base64_decode",
                    ERROR_CONTEXT_KEYS.ENCODING: "utf-8",
                },
            ) from e
        except Exception as e:
            raise TransformationError(
                f"Base64 decoding failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.OPERATION: "base64_decode",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(encoded_text),
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
