"""Base service class with common functionality.

Abstract base class demonstrating clean architecture patterns
and dependency injection principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

try:
    from sqlalchemy.orm import Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    if TYPE_CHECKING:
        from sqlalchemy.orm import Session  # type: ignore[import]

from ..core.exceptions import TSVTranslateError


class BaseService(ABC):
    """Abstract base class for all services.
    
    Implements common patterns:
    - Dependency injection through constructor
    - Resource management with context managers
    - Consistent error handling
    - Logging interface (extendable)
    """
    
    def __init__(self, db_session: Session) -> None:
        """Initialize with database session dependency.
        
        Args:
            db_session: SQLAlchemy session for database operations
        """
        self._db_session = db_session
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """Validate required dependencies are properly injected."""
        if not self._db_session:
            raise TSVTranslateError("Database session is required")
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verify service is operational.
        
        Returns:
            True if service is healthy, False otherwise
        """
        pass
    
    def _log_operation(
        self,
        operation: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Log service operations for debugging and monitoring.
        
        Placeholder for structured logging implementation.
        In production, this would integrate with logging framework.
        
        Args:
            operation: Description of the operation
            details: Additional operation details
        """
        # TODO: Integrate with application logging system
        pass
    
    def __enter__(self) -> "BaseService":
        """Context manager entry for resource management."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Base implementation - subclasses can override
        pass