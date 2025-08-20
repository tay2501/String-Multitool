"""Exception hierarchy for TSV converter.

Clean exception design following Python best practices
with specific error types for different failure scenarios.
"""


class TSVConverterError(Exception):
    """Base exception for all TSV converter errors.
    
    Provides a foundation for hierarchical exception handling
    following the principle of specific error types.
    """
    pass


class ValidationError(TSVConverterError):
    """Raised when data validation fails.
    
    Examples:
    - Invalid TSV file format
    - Missing required columns
    - Data type mismatches
    """
    pass


class SyncError(TSVConverterError):
    """Raised when file-database synchronization fails.
    
    Examples:
    - Database transaction failures
    - File system access errors
    - Hash mismatch during integrity checks
    """
    pass


class ConversionError(TSVConverterError):
    """Raised when text conversion operations fail.
    
    Examples:
    - Rule not found for given input
    - Multiple conflicting rules
    - Conversion result validation failures
    """
    pass