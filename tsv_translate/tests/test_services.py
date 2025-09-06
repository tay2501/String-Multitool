"""Test cases for service layer.

Comprehensive testing of business logic with proper
mocking, error handling, and integration scenarios.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ..services import SyncService, ConversionService
from ..models import RuleSet, ConversionRule
from ..models.types import OperationStatus
from ..models.exceptions import ValidationError


class TestSyncService:
    """Test cases for TSV synchronization service."""
    
    def test_sync_new_file(self, sync_service, sample_tsv_file):
        """Test synchronizing a new TSV file."""
        result = sync_service.sync_file(sample_tsv_file)
        
        assert result.is_successful
        assert result.operation == "create"
        assert result.rules_processed == 3
        assert result.rule_set_name == "test_rules"
    
    def test_sync_existing_file_no_changes(self, sync_service, sample_tsv_file):
        """Test sync when file hasn't changed."""
        # First sync
        sync_service.sync_file(sample_tsv_file)
        
        # Second sync should skip
        result = sync_service.sync_file(sample_tsv_file)
        
        assert result.is_successful
        assert result.operation == "skip"
    
    def test_sync_existing_file_with_changes(
        self, sync_service, sample_tsv_file, sample_tsv_content
    ):
        """Test sync when file content has changed."""
        # First sync
        sync_service.sync_file(sample_tsv_file)
        
        # Modify file
        new_content = sample_tsv_content + "\nnew	新しい"
        sample_tsv_file.write_text(new_content, encoding='utf-8')
        
        # Second sync should update
        result = sync_service.sync_file(sample_tsv_file)
        
        assert result.is_successful
        assert result.operation == "update"
        assert result.rules_processed == 4
    
    def test_sync_invalid_tsv_format(self, sync_service, temp_directory):
        """Test sync with invalid TSV format."""
        invalid_file = temp_directory / "invalid.tsv"
        invalid_file.write_text("single_column_only\n", encoding='utf-8')
        
        result = sync_service.sync_file(invalid_file)
        
        assert not result.is_successful
        assert "Expected 2 columns" in result.error_message
    
    def test_sync_directory(self, sync_service, temp_directory, sample_tsv_content):
        """Test synchronizing entire directory."""
        # Create multiple TSV files
        for i in range(3):
            tsv_file = temp_directory / f"rules_{i}.tsv"
            tsv_file.write_text(sample_tsv_content, encoding='utf-8')
        
        results = sync_service.sync_directory(temp_directory)
        
        assert len(results) == 3
        assert all(r.is_successful for r in results)
        assert all(r.operation == "create" for r in results)
    
    def test_remove_rule_set(self, sync_service, sample_tsv_file):
        """Test removing rule set from database."""
        # First sync the file
        sync_service.sync_file(sample_tsv_file)
        
        # Remove rule set
        result = sync_service.remove_rule_set("test_rules")
        
        assert result.is_successful
        assert result.operation == "delete"
        assert result.rules_deleted == 3
    
    def test_remove_nonexistent_rule_set(self, sync_service):
        """Test removing rule set that doesn't exist."""
        result = sync_service.remove_rule_set("nonexistent")
        
        assert result.status == OperationStatus.WARNING
        assert "not found" in result.error_message
    
    def test_health_check(self, sync_service):
        """Test service health check."""
        assert sync_service.health_check() is True


class TestConversionService:
    """Test cases for text conversion service."""
    
    def test_convert_text_success(self, conversion_service, test_database):
        """Test successful text conversion."""
        # Setup test data
        rule_set = RuleSet(
            name="test_conversion",
            file_path="/test.tsv",
            file_hash="hash"
        )
        test_database.add(rule_set)
        test_database.flush()
        
        rule = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="hello",
            target_text="こんにちは"
        )
        test_database.add(rule)
        test_database.commit()
        
        # Test conversion
        result = conversion_service.convert_text("hello", "test_conversion")
        
        assert result.is_successful
        assert result.converted_text == "こんにちは"
        assert result.rules_applied == 1
    
    def test_convert_text_no_match(self, conversion_service, test_database):
        """Test conversion when no matching rule exists."""
        rule_set = RuleSet(
            name="empty_set",
            file_path="/empty.tsv",
            file_hash="hash"
        )
        test_database.add(rule_set)
        test_database.commit()
        
        result = conversion_service.convert_text("nomatch", "empty_set")
        
        assert result.is_successful
        assert result.converted_text == "nomatch"  # Unchanged
        assert result.rules_applied == 0
    
    def test_convert_nonexistent_rule_set(self, conversion_service):
        """Test conversion with nonexistent rule set."""
        result = conversion_service.convert_text("test", "nonexistent")
        
        assert not result.is_successful
        assert "not found" in result.error_message
    
    def test_convert_empty_text(self, conversion_service, test_database):
        """Test conversion with empty input text."""
        rule_set = RuleSet(
            name="test_empty",
            file_path="/test.tsv",
            file_hash="hash"
        )
        test_database.add(rule_set)
        test_database.commit()
        
        result = conversion_service.convert_text("", "test_empty")
        
        assert result.status == OperationStatus.WARNING
        assert "Empty input" in result.error_message
    
    def test_list_rule_sets(self, conversion_service, test_database):
        """Test listing available rule sets."""
        # Add test rule sets
        rule_sets = ["set_a", "set_b", "set_c"]
        for name in rule_sets:
            rs = RuleSet(
                name=name,
                file_path=f"/{name}.tsv",
                file_hash=f"hash_{name}"
            )
            test_database.add(rs)
        
        test_database.commit()
        
        result = conversion_service.list_rule_sets()
        
        assert len(result) == 3
        assert result == sorted(rule_sets)  # Should be sorted
    
    def test_get_rule_set_info(self, conversion_service, test_database):
        """Test getting detailed rule set information."""
        rule_set = RuleSet(
            name="info_test",
            file_path="/info.tsv",
            file_hash="info_hash",
            rule_count=5,
            description="Test rule set"
        )
        test_database.add(rule_set)
        test_database.commit()
        
        info = conversion_service.get_rule_set_info("info_test")
        
        assert info is not None
        assert info["name"] == "info_test"
        assert info["rule_count"] == 5
        assert info["description"] == "Test rule set"
        assert "created_at" in info
        assert "updated_at" in info
    
    def test_get_nonexistent_rule_set_info(self, conversion_service):
        """Test getting info for nonexistent rule set."""
        info = conversion_service.get_rule_set_info("nonexistent")
        assert info is None
    
    def test_usage_statistics_tracking(self, conversion_service, test_database):
        """Test that usage statistics are properly tracked."""
        # Setup test data
        rule_set = RuleSet(
            name="usage_test",
            file_path="/usage.tsv",
            file_hash="usage_hash"
        )
        test_database.add(rule_set)
        test_database.flush()
        
        rule = ConversionRule(
            rule_set_id=rule_set.id,
            source_text="tracked",
            target_text="追跡",
            usage_count=0
        )
        test_database.add(rule)
        test_database.commit()
        
        # Perform conversion
        conversion_service.convert_text("tracked", "usage_test")
        
        # Check that usage count was incremented
        test_database.refresh(rule)
        assert rule.usage_count == 1
    
    def test_health_check(self, conversion_service):
        """Test service health check."""
        assert conversion_service.health_check() is True