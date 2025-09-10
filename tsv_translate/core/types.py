"""Type definitions and data classes.

Modern Python type system usage with dataclasses
for clear, self-documenting data structures.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


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
    converted_text: str | None = None
    rule_set_name: str | None = None
    rules_applied: int = 0
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

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
    file_hash: str | None = None
    error_message: str | None = None
    execution_time_ms: float | None = None

    @property
    def is_successful(self) -> bool:
        """Convenience property for success checking."""
        return self.status == OperationStatus.SUCCESS
