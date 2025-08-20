"""Type definitions and data classes.

Modern Python type system usage with dataclasses
for clear, self-documenting data structures.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class OperationStatus(Enum):
    """Standard operation result statuses."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ConversionResult:
    """Result of a text conversion operation.
    
    Immutable data class following functional programming principles
    with comprehensive result information for debugging and monitoring.
    """
    status: OperationStatus
    original_text: str
    converted_text: Optional[str] = None
    rule_set_name: Optional[str] = None
    rules_applied: int = 0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def is_successful(self) -> bool:
        """Convenience property for success checking."""
        return self.status == OperationStatus.SUCCESS


@dataclass(frozen=True)
class SyncResult:
    """Result of a file-database synchronization operation.
    
    Comprehensive sync result tracking for audit trails
    and operational monitoring.
    """
    status: OperationStatus
    rule_set_name: str
    operation: str  # 'create', 'update', 'delete'
    rules_processed: int = 0
    rules_added: int = 0
    rules_updated: int = 0
    rules_deleted: int = 0
    file_hash: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    
    @property
    def is_successful(self) -> bool:
        """Convenience property for success checking."""
        return self.status == OperationStatus.SUCCESS