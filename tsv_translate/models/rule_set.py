"""Rule set model representing TSV files.

Demonstrates SQLAlchemy 2.0 best practices with proper indexing,
constraints, and relationships.
"""


from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RuleSet(Base):
    """Represents a TSV file containing conversion rules.
    
    Design principles:
    - Normalized data model following 3NF
    - Proper indexing for performance
    - Clear constraint definitions
    - Descriptive column comments
    """

    __tablename__ = "rule_sets"

    # Primary key following best practices
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique rule set identifier"
    )

    # Business key with unique constraint
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Rule set name derived from TSV filename"
    )

    # File integrity tracking
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Absolute path to the TSV file"
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash for change detection"
    )

    # Optional metadata
    description: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Optional rule set description"
    )

    # Performance statistics
    rule_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Number of conversion rules in this set"
    )

    # Relationships following SQLAlchemy 2.0 patterns
    conversion_rules: Mapped[list["ConversionRule"]] = relationship(
        "ConversionRule",
        back_populates="rule_set",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Database constraints for data integrity
    __table_args__ = (
        UniqueConstraint("name", name="uq_rule_sets_name"),
        UniqueConstraint("file_path", name="uq_rule_sets_file_path"),
        Index("ix_rule_sets_name_hash", "name", "file_hash"),
    )

    def __repr__(self) -> str:
        """Clean string representation for debugging."""
        return f"<RuleSet(id={self.id}, name='{self.name}', rules={self.rule_count})>"
