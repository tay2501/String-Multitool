"""Text conversion service using synchronized rules.

Clean implementation of string conversion operations with
performance optimizations and comprehensive result tracking.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

try:
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy.orm import Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    if TYPE_CHECKING:
        pass

from ..models import ConversionRule, RuleSet
from ..models.types import ConversionResult, OperationStatus
from .base import BaseService


class ConversionServiceInterface(ABC):
    """Interface for text conversion operations."""

    @abstractmethod
    def convert_text(self, text: str, rule_set_name: str) -> ConversionResult:
        """Convert text using specified rule set."""
        pass

    @abstractmethod
    def list_rule_sets(self) -> list[str]:
        """Get list of available rule set names."""
        pass

    @abstractmethod
    def get_rule_set_info(self, rule_set_name: str) -> dict | None:
        """Get information about a specific rule set."""
        pass


class ConversionService(BaseService, ConversionServiceInterface):
    """Text conversion implementation with performance optimization.
    
    Educational features:
    - Efficient database queries with proper indexing usage
    - Usage statistics tracking for monitoring
    - Comprehensive error handling and logging
    - Clean separation of concerns
    """

    def health_check(self) -> bool:
        """Verify conversion service is operational."""
        try:
            # Test basic query operation
            count = self._db_session.query(RuleSet).count()
            return True
        except Exception:
            # Handle both SQLAlchemyError and import errors gracefully
            if not SQLALCHEMY_AVAILABLE:
                return False
            return False

    def convert_text(self, text: str, rule_set_name: str) -> ConversionResult:
        """Convert text using specified rule set.
        
        Optimized for performance with single query lookup
        using the composite index on (rule_set_id, source_text).
        """
        if not text.strip():
            return ConversionResult(
                status=OperationStatus.WARNING,
                original_text=text,
                converted_text=text,
                rule_set_name=rule_set_name,
                error_message="Empty input text"
            )

        try:
            # Get rule set with validation
            rule_set = self._get_rule_set(rule_set_name)
            if not rule_set:
                return ConversionResult(
                    status=OperationStatus.ERROR,
                    original_text=text,
                    rule_set_name=rule_set_name,
                    error_message=f"Rule set '{rule_set_name}' not found"
                )

            # Perform conversion using optimized query
            converted_text = self._apply_conversion_rules(text, rule_set.id)

            # Track usage statistics
            if converted_text != text:
                self._update_usage_statistics(rule_set.id, text)

            return ConversionResult(
                status=OperationStatus.SUCCESS,
                original_text=text,
                converted_text=converted_text,
                rule_set_name=rule_set_name,
                rules_applied=1 if converted_text != text else 0
            )

        except Exception as e:
            # Handle both SQLAlchemyError and import errors gracefully
            if not SQLALCHEMY_AVAILABLE:
                raise ValueError("SQLAlchemy not available") from e
            return ConversionResult(
                status=OperationStatus.ERROR,
                original_text=text,
                rule_set_name=rule_set_name,
                error_message=f"Database error: {str(e)}"
            )

    def list_rule_sets(self) -> list[str]:
        """Get sorted list of available rule set names."""
        try:
            rule_sets = (
                self._db_session.query(RuleSet.name)
                .order_by(RuleSet.name)
                .all()
            )
            return [rs.name for rs in rule_sets]

        except Exception:
            # Handle both SQLAlchemyError and import errors gracefully
            if not SQLALCHEMY_AVAILABLE:
                return []
            return []

    def get_rule_set_info(self, rule_set_name: str) -> dict | None:
        """Get comprehensive information about a rule set."""
        try:
            rule_set = self._get_rule_set(rule_set_name)
            if not rule_set:
                return None

            # Calculate additional statistics
            total_usage = (
                self._db_session.query(ConversionRule.usage_count)
                .filter(ConversionRule.rule_set_id == rule_set.id)
                .all()
            )

            return {
                "name": rule_set.name,
                "file_path": rule_set.file_path,
                "rule_count": rule_set.rule_count,
                "total_usage": sum(usage.usage_count for usage in total_usage),
                "created_at": rule_set.created_at.isoformat(),
                "updated_at": rule_set.updated_at.isoformat(),
                "description": rule_set.description
            }

        except Exception:
            # Handle both SQLAlchemyError and import errors gracefully
            if not SQLALCHEMY_AVAILABLE:
                return None
            return None

    def _get_rule_set(self, name: str) -> RuleSet | None:
        """Get rule set by name with error handling."""
        return cast(
            RuleSet | None,
            self._db_session.query(RuleSet)
            .filter(RuleSet.name == name)
            .first()
        )

    def _apply_conversion_rules(self, text: str, rule_set_id: int) -> str:
        """Apply conversion rules efficiently.
        
        Uses the optimized composite index for fast lookup.
        Returns original text if no matching rule found.
        """
        conversion_rule = (
            self._db_session.query(ConversionRule)
            .filter(
                ConversionRule.rule_set_id == rule_set_id,
                ConversionRule.source_text == text
            )
            .first()
        )

        return conversion_rule.target_text if conversion_rule else text

    def _update_usage_statistics(self, rule_set_id: int, source_text: str) -> None:
        """Update usage statistics for monitoring and optimization.
        
        Separate transaction to avoid affecting main conversion operation.
        """
        try:
            rule = (
                self._db_session.query(ConversionRule)
                .filter(
                    ConversionRule.rule_set_id == rule_set_id,
                    ConversionRule.source_text == source_text
                )
                .first()
            )

            if rule:
                rule.usage_count += 1
                self._db_session.commit()

        except Exception:
            # Handle both SQLAlchemyError and import errors gracefully
            if not SQLALCHEMY_AVAILABLE:
                return
            # Statistics update failure shouldn't affect main operation
            self._db_session.rollback()
            self._log_operation("usage_stats_update_failed", {
                "rule_set_id": rule_set_id,
                "source_text": source_text[:50]  # Truncate for logging
            })
