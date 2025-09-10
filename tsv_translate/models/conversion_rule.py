"""Conversion rule model for key-value pairs.

Optimized for high-performance lookups with composite indexing
following database design best practices.
"""

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ConversionRule(Base):
    """Individual conversion rule within a rule set.
    
    Design optimizations:
    - Composite index on (rule_set_id, source_text) for fast lookups
    - Foreign key constraints for referential integrity
    - String length limits based on practical usage patterns
    - Usage statistics for monitoring and optimization
    """

    __tablename__ = "conversion_rules"

    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique conversion rule identifier"
    )

    # Foreign key relationship
    rule_set_id: Mapped[int] = mapped_column(
        ForeignKey("rule_sets.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to parent rule set"
    )

    # Conversion pair with practical length limits
    source_text: Mapped[str] = mapped_column(
        String(1000),  # Reasonable limit for performance
        nullable=False,
        comment="Text to be replaced (search key)"
    )

    target_text: Mapped[str] = mapped_column(
        String(2000),  # Allow longer replacement text
        nullable=False,
        comment="Replacement text (conversion result)"
    )

    # Usage tracking for optimization insights
    usage_count: Mapped[int] = mapped_column(
        default=0,
        server_default=text("0"),
        nullable=False,
        comment="Number of times this rule has been applied"
    )

    # TSV file name for traceability and debugging
    tsv_file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original TSV filename this rule originated from"
    )

    # Relationship back to rule set
    rule_set: Mapped["RuleSet"] = relationship(
        "RuleSet",
        back_populates="conversion_rules"
    )

    # Performance-optimized indexing strategy
    __table_args__ = (
        # Primary lookup index for conversion operations
        Index(
            "ix_conversion_rules_lookup",
            "rule_set_id", "source_text",
            unique=True  # Prevent duplicate rules within same set
        ),
        # Secondary index for analytics and management
        Index("ix_conversion_rules_usage", "usage_count"),
    )

    def __repr__(self) -> str:
        """Readable representation for debugging."""
        return (
            f"<ConversionRule(id={self.id}, "
            f"'{self.source_text[:20]}...' -> '{self.target_text[:20]}...', "
            f"used={self.usage_count})>"
        )
