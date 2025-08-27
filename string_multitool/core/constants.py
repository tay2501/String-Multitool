"""
Constants module for String_Multitool.

This module provides centralized constant management using modern Python best practices:
- frozen=True dataclasses for immutable constant groups
- Enum for related categorical constants
- typing.Final for type safety and documentation

Following PEP 526 (Variable Annotations) and 2024 best practices.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Final


@dataclass(frozen=True)
class TransformationConstants:
    """Core transformation constants with immutable guarantees.
    
    Uses frozen=True to prevent modification after instantiation,
    ensuring true immutability and hashability for dictionary keys.
    """
    
    # File and encoding constants
    DEFAULT_ENCODING: Final[str] = "utf-8"
    TSV_FILE_EXTENSION: Final[str] = ".tsv"
    JSON_FILE_EXTENSION: Final[str] = ".json"
    
    # Directory structure constants
    CONFIG_DIR_NAME: Final[str] = "config"
    TSV_RULES_DIR: Final[str] = "tsv_rules"
    RSA_KEYS_DIR: Final[str] = "rsa"
    
    # Format constants
    DEFAULT_JSON_INDENT: Final[int] = 2
    DEFAULT_TSV_SEPARATOR: Final[str] = "\t"
    DEFAULT_SLUG_SEPARATOR: Final[str] = "-"
    
    # Text processing constants
    FULL_WIDTH_ASCII_START: Final[int] = 0xFF01
    FULL_WIDTH_ASCII_END: Final[int] = 0xFF5E
    FULL_WIDTH_SPACE: Final[int] = 0x3000
    HALF_WIDTH_ASCII_START: Final[int] = 0x21
    HALF_WIDTH_ASCII_END: Final[int] = 0x7E
    UNICODE_OFFSET: Final[int] = 0xFEE0
    
    # SQL formatting constants
    SQL_IN_QUOTE: Final[str] = "'"
    SQL_IN_SEPARATOR: Final[str] = ",\r\n"
    
    # Line break constants
    CRLF: Final[str] = "\r\n"
    LF: Final[str] = "\n"
    CR: Final[str] = "\r"


@dataclass(frozen=True)
class CryptoConstants:
    """Cryptographic operation constants.
    
    Centralized security-related constants for RSA/AES operations.
    """
    
    # RSA constants
    RSA_KEY_SIZE: Final[int] = 4096
    RSA_PUBLIC_KEY_FILENAME: Final[str] = "public_key.pem"
    RSA_PRIVATE_KEY_FILENAME: Final[str] = "private_key.pem"
    
    # AES constants
    AES_MODE: Final[str] = "AES-256-CBC"
    AES_KEY_SIZE: Final[int] = 32  # 256 bits
    
    # Hash constants
    HASH_ALGORITHM: Final[str] = "SHA-256"
    
    # Encoding constants
    BASE64_ENCODING: Final[str] = "ascii"


@dataclass(frozen=True)
class ValidationConstants:
    """Input validation and error handling constants."""
    
    # Error message templates
    INVALID_INPUT_TYPE_MSG: Final[str] = "Text must be a string, got {type_name}"
    INVALID_RULE_TYPE_MSG: Final[str] = "Rule string must be a string, got {type_name}"
    EMPTY_RULE_MSG: Final[str] = "Rule string cannot be empty"
    RULE_PREFIX_MSG: Final[str] = "Rules must start with '/'"
    UNKNOWN_RULE_MSG: Final[str] = "Unknown rule: {rule_name}"
    
    # Rule validation constants
    RULE_PREFIX: Final[str] = "/"
    MIN_REPLACE_ARGS: Final[int] = 1
    MAX_TEXT_PREVIEW_LENGTH: Final[int] = 50
    MAX_JSON_PREVIEW_LENGTH: Final[int] = 100


@unique
class RuleNames(Enum):
    """Enumeration of transformation rule names.
    
    Uses @unique decorator to ensure no duplicate values.
    Provides type-safe access to rule names with IDE completion.
    """
    
    # Core transformation rule (updated from convertbytsv)
    USE_TSV_RULES = "usetsvr"
    
    # Basic transformations
    UNDERBAR_TO_HYPHEN = "uh"
    HYPHEN_TO_UNDERBAR = "hu"
    FULL_TO_HALF_WIDTH = "fh"
    HALF_TO_FULL_WIDTH = "hf"
    
    # Case transformations
    LOWERCASE = "l"
    UPPERCASE = "u"
    PASCAL_CASE = "p"
    CAMEL_CASE = "c"
    SNAKE_CASE = "s"
    CAPITALIZE = "a"
    
    # String operations
    TRIM = "t"
    REVERSE = "R"
    SQL_IN_CLAUSE = "si"
    DELETE_LINE_BREAKS = "dlb"
    
    # Advanced operations with arguments
    REPLACE = "r"
    SLUGIFY = "S"
    
    # Encryption operations
    ENCRYPT = "enc"
    DECRYPT = "dec"
    
    # Hash operations
    SHA256_HASH = "hash"
    
    # Encoding operations
    BASE64_ENCODE = "base64enc"
    BASE64_DECODE = "base64dec"
    
    # Format operations
    FORMAT_JSON = "formatjson"


@unique
class TSVOptionNames(Enum):
    """TSV conversion option names for argument parsing."""
    
    CASE_INSENSITIVE_LONG = "--case-insensitive"
    CASE_INSENSITIVE_ALT = "--caseinsensitive"
    CASE_INSENSITIVE_SHORT = "-i"
    NO_PRESERVE_CASE = "--no-preserve-case"
    NO_PRESERVE_CASE_ALT = "--no-preserve-original-case"
    PRESERVE_CASE = "--preserve-case"
    PRESERVE_CASE_ALT = "--preserve-original-case"


@dataclass(frozen=True)
class ErrorContextKeys:
    """Standard keys for error context dictionaries.
    
    Provides consistent naming for error context information
    across the application.
    """
    
    # General error context
    ERROR_TYPE: Final[str] = "error_type"
    TEXT_LENGTH: Final[str] = "text_length"
    TEXT_PREVIEW: Final[str] = "text_preview"
    
    # Rule-specific context
    RULE_NAME: Final[str] = "rule_name"
    RULE_STRING: Final[str] = "rule_string"
    ARGS: Final[str] = "args"
    ARGS_COUNT: Final[str] = "args_count"
    AVAILABLE_RULES: Final[str] = "available_rules"
    
    # File-specific context
    FILE_PATH: Final[str] = "file_path"
    TSV_FILE: Final[str] = "tsv_file"
    RULES_COUNT: Final[str] = "rules_count"
    
    # Encoding/decoding context
    ENCODING_ERROR: Final[str] = "encoding_error"
    UNICODE_ERROR: Final[str] = "unicode_error"
    DECODE_ERROR: Final[str] = "decode_error"
    
    # JSON-specific context
    JSON_ERROR: Final[str] = "json_error"
    ERROR_LINE: Final[str] = "error_line"
    ERROR_POS: Final[str] = "error_pos"
    
    # Configuration context
    CONFIG_KEYS: Final[str] = "config_keys"
    CONFIG_TYPE: Final[str] = "config_type"


# Module-level singleton instances for convenient access
TRANSFORM_CONSTANTS = TransformationConstants()
CRYPTO_CONSTANTS = CryptoConstants()
VALIDATION_CONSTANTS = ValidationConstants()
ERROR_CONTEXT_KEYS = ErrorContextKeys()

# Type aliases for better code documentation
RuleName = RuleNames
TSVOption = TSVOptionNames