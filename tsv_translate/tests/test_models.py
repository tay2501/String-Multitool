"""Test cases for data models.

Educational testing examples demonstrating:
- Model validation and constraints
- Relationship testing
- Database integrity checks
"""

import pytest

try:
    from sqlalchemy.exc import IntegrityError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    IntegrityError = Exception  # Fallback for type checking

from ..models import ConversionRule, RuleSet


class TestRuleSet:
    """Test cases for RuleSet model."""

    def test_create_rule_set(self, test_database):
        """Test basic rule set creation."""
        rule_set = RuleSet(
            name="test_rules",
            file_path="/path/to/test.tsv",
            file_hash="abc123",
            rule_count=5
        )

        test_database.add(rule_set)
        test_database.commit()

        assert rule_set.id is not None
        assert rule_set.name == "test_rules"
        assert rule_set.rule_count == 5
        assert rule_set.created_at is not None
        assert rule_set.updated_at is not None

    def test_unique_name_constraint(self, test_database):
        """Test that rule set names must be unique."""
        rule_set1 = RuleSet(
            name="duplicate_name",
            file_path="/path1.tsv",
            file_hash="hash1"
        )
        rule_set2 = RuleSet(
            name="duplicate_name",
            file_path="/path2.tsv",
            file_hash="hash2"
        )

        test_database.add(rule_set1)
        test_database.commit()

        test_database.add(rule_set2)
        with pytest.raises(IntegrityError):
            test_database.commit()

    def test_rule_set_relationship(self, test_database):
        """Test relationship with conversion rules."""
        rule_set = RuleSet(
            name="relationship_test",
            file_path="/test.tsv",
            file_hash="hash123"
        )
        test_database.add(rule_set)
        test_database.flush()

        # Add conversion rules
        rule1 = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="hello",
            target_text="world"
        )
        rule2 = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="foo",
            target_text="bar"
        )

        test_database.add_all([rule1, rule2])
        test_database.commit()

        # Test relationship
        assert len(rule_set.conversion_rules) == 2
        assert rule1.rule_set == rule_set
        assert rule2.rule_set == rule_set


class TestConversionRule:
    """Test cases for ConversionRule model."""

    def test_create_conversion_rule(self, test_database):
        """Test basic conversion rule creation."""
        # First create rule set
        rule_set = RuleSet(
            name="test_set",
            file_path="/test.tsv",
            file_hash="hash"
        )
        test_database.add(rule_set)
        test_database.flush()

        # Create conversion rule
        rule = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="input",
            target_text="output",
            usage_count=5
        )

        test_database.add(rule)
        test_database.commit()

        assert rule.id is not None
        assert rule.source_text == "input"
        assert rule.target_text == "output"
        assert rule.usage_count == 5

    def test_unique_rule_constraint(self, test_database):
        """Test that rules must be unique within a rule set."""
        rule_set = RuleSet(
            name="unique_test",
            file_path="/test.tsv",
            file_hash="hash"
        )
        test_database.add(rule_set)
        test_database.flush()

        rule1 = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="duplicate",
            target_text="first"
        )
        rule2 = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="duplicate",
            target_text="second"
        )

        test_database.add(rule1)
        test_database.commit()

        test_database.add(rule2)
        with pytest.raises(IntegrityError):
            test_database.commit()

    def test_cascade_delete(self, test_database):
        """Test that rules are deleted when rule set is deleted."""
        rule_set = RuleSet(
            name="cascade_test",
            file_path="/test.tsv",
            file_hash="hash"
        )
        test_database.add(rule_set)
        test_database.flush()

        rule = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="test",
            target_text="result"
        )
        test_database.add(rule)
        test_database.commit()

        # Delete rule set
        test_database.delete(rule_set)
        test_database.commit()

        # Rule should be automatically deleted
        remaining_rules = test_database.query(ConversionRule).filter(
            ConversionRule.rule_set_id == rule_set.id
        ).count()
        assert remaining_rules == 0
