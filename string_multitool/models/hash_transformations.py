"""
Hash transformation operations for String_Multitool.

This module provides dedicated hash transformation functionality
following the single responsibility principle and EAFP error handling pattern.
"""

from __future__ import annotations

import hashlib
from typing import Any

from ..exceptions import TransformationError
from .constants import ERROR_CONTEXT_KEYS
from .transformation_base import TransformationBase


class HashTransformations(TransformationBase):
    """Dedicated hash transformation operations handler.

    This class handles all hash operations including SHA-256, MD5,
    and other cryptographic hash functions with proper error handling.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize hash transformations.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config or {})
        self._supported_algorithms = {"sha256", "sha1", "sha512", "md5", "sha224", "sha384"}

    def transform(self, text: str, algorithm: str = "sha256") -> str:
        """Apply hash transformation to text.

        Args:
            text: Input text to hash
            algorithm: Hash algorithm to use

        Returns:
            Hexadecimal hash string

        Raises:
            TransformationError: If hashing fails
        """
        try:
            if algorithm not in self._supported_algorithms:
                raise TransformationError(
                    f"Unsupported hash algorithm: {algorithm}",
                    {
                        ERROR_CONTEXT_KEYS.ALGORITHM: algorithm,
                        "supported_algorithms": list(self._supported_algorithms),
                    },
                )

            # EAFP: Try hashing directly
            return self._compute_hash(text, algorithm)

        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(
                f"Hash transformation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.ALGORITHM: algorithm,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                },
            ) from e

    def sha256_hash(self, text: str) -> str:
        """Generate SHA-256 hash of text.

        Args:
            text: Input text to hash

        Returns:
            SHA-256 hash as hexadecimal string

        Raises:
            TransformationError: If hashing fails
        """
        return self._compute_hash(text, "sha256")

    def sha1_hash(self, text: str) -> str:
        """Generate SHA-1 hash of text.

        Args:
            text: Input text to hash

        Returns:
            SHA-1 hash as hexadecimal string

        Raises:
            TransformationError: If hashing fails
        """
        return self._compute_hash(text, "sha1")

    def sha512_hash(self, text: str) -> str:
        """Generate SHA-512 hash of text.

        Args:
            text: Input text to hash

        Returns:
            SHA-512 hash as hexadecimal string

        Raises:
            TransformationError: If hashing fails
        """
        return self._compute_hash(text, "sha512")

    def md5_hash(self, text: str) -> str:
        """Generate MD5 hash of text.

        Note:
            MD5 is not cryptographically secure and should only be used
            for non-security applications like checksums.

        Args:
            text: Input text to hash

        Returns:
            MD5 hash as hexadecimal string

        Raises:
            TransformationError: If hashing fails
        """
        return self._compute_hash(text, "md5")

    def _compute_hash(self, text: str, algorithm: str) -> str:
        """Compute hash using specified algorithm.

        Args:
            text: Input text to hash
            algorithm: Hash algorithm name

        Returns:
            Hash as hexadecimal string

        Raises:
            TransformationError: If hashing fails
        """
        try:
            # EAFP: Try to create hash object and compute
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(text.encode("utf-8"))
            return hash_obj.hexdigest()

        except ValueError as e:
            raise TransformationError(
                f"Invalid hash algorithm: {algorithm}",
                {
                    ERROR_CONTEXT_KEYS.ALGORITHM: algorithm,
                    "available_algorithms": list(hashlib.algorithms_available),
                },
            ) from e
        except UnicodeEncodeError as e:
            raise TransformationError(
                "Text encoding failed during hash computation",
                {
                    ERROR_CONTEXT_KEYS.ALGORITHM: algorithm,
                    ERROR_CONTEXT_KEYS.ENCODING: "utf-8",
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                },
            ) from e
        except Exception as e:
            raise TransformationError(
                f"Hash computation failed: {e}",
                {
                    ERROR_CONTEXT_KEYS.ALGORITHM: algorithm,
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: len(text),
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                },
            ) from e

    def get_supported_algorithms(self) -> set[str]:
        """Get list of supported hash algorithms.

        Returns:
            Set of supported algorithm names
        """
        return self._supported_algorithms.copy()

    def is_algorithm_supported(self, algorithm: str) -> bool:
        """Check if hash algorithm is supported.

        Args:
            algorithm: Algorithm name to check

        Returns:
            True if algorithm is supported, False otherwise
        """
        return algorithm.lower() in self._supported_algorithms
