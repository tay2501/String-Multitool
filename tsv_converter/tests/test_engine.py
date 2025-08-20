"""Test cases for the main conversion engine.

Integration testing demonstrating complete workflows
and system behavior under various conditions.
"""

import pytest
from pathlib import Path

from ..core.engine import TSVConverterEngine
from ..core.exceptions import TSVConverterError


class TestTSVConverterEngine:
    """Test cases for the main conversion engine."""
    
    def test_engine_initialization(self, test_config):
        """Test proper engine initialization."""
        with TSVConverterEngine(test_config) as engine:
            assert engine._is_initialized is True
            
            # Test health check
            health = engine.health_check()
            assert health["engine"] is True
            assert health["database"] is True
    
    def test_engine_context_manager(self, test_config):
        """Test proper resource cleanup with context manager."""
        engine = TSVConverterEngine(test_config)
        
        with engine:
            assert engine._is_initialized is True
        
        assert engine._is_initialized is False
    
    def test_complete_workflow(self, converter_engine, sample_tsv_file):
        """Test complete workflow from sync to conversion."""
        # 1. Sync TSV file
        sync_result = converter_engine.sync_file(sample_tsv_file)
        assert sync_result.is_successful
        
        # 2. List rule sets
        rule_sets = converter_engine.list_rule_sets()
        assert "test_rules" in rule_sets
        
        # 3. Convert text
        conversion_result = converter_engine.convert_text("hello", "test_rules")
        assert conversion_result.is_successful
        assert conversion_result.converted_text == "こんにちは"
        
        # 4. Get rule set info
        info = converter_engine.get_rule_set_info("test_rules")
        assert info is not None
        assert info["rule_count"] == 3
        
        # 5. Remove rule set
        remove_result = converter_engine.remove_rule_set("test_rules")
        assert remove_result.is_successful
    
    def test_directory_sync_workflow(self, converter_engine, temp_directory):
        """Test directory synchronization workflow."""
        # Create multiple TSV files
        sample_content = "test\tテスト\nhello\tこんにちは"
        
        files = []
        for i in range(3):
            tsv_file = temp_directory / f"rules_{i}.tsv"
            tsv_file.write_text(sample_content, encoding='utf-8')
            files.append(tsv_file)
        
        # Sync directory
        results = converter_engine.sync_directory(temp_directory)
        assert len(results) == 3
        assert all(r.is_successful for r in results)
        
        # Verify all rule sets are available
        rule_sets = converter_engine.list_rule_sets()
        assert len(rule_sets) == 3
        
        # Test conversion with each rule set
        for i in range(3):
            result = converter_engine.convert_text("hello", f"rules_{i}")
            assert result.is_successful
            assert result.converted_text == "こんにちは"
    
    def test_error_handling_invalid_file(self, converter_engine, temp_directory):
        """Test error handling with invalid TSV file."""
        invalid_file = temp_directory / "invalid.tsv"
        invalid_file.write_text("invalid\ttsv\tformat\twith\ttoo\tmany\tcolumns")
        
        result = converter_engine.sync_file(invalid_file)
        assert not result.is_successful
        assert "Expected 2 columns" in result.error_message
    
    def test_error_handling_missing_rule_set(self, converter_engine):
        """Test error handling with missing rule set."""
        result = converter_engine.convert_text("test", "nonexistent")
        assert not result.is_successful
        assert "not found" in result.error_message
    
    def test_uninitialized_engine_error(self, test_config):
        """Test error when using uninitialized engine."""
        engine = TSVConverterEngine(test_config)
        
        with pytest.raises(TSVConverterError, match="not initialized"):
            engine.convert_text("test", "rule_set")
    
    def test_configuration_override(self, test_config, temp_directory):
        """Test configuration parameter usage."""
        # Modify config
        test_config["tsv_directory"] = str(temp_directory)
        test_config["debug"] = True
        
        with TSVConverterEngine(test_config) as engine:
            # Create TSV file in configured directory
            tsv_file = temp_directory / "config_test.tsv"
            tsv_file.write_text("config\t設定", encoding='utf-8')
            
            # Sync should work with configured directory
            result = engine.sync_file(tsv_file)
            assert result.is_successful
    
    def test_concurrent_operations(self, converter_engine, temp_directory):
        """Test handling multiple operations."""
        # Create test files
        files = []
        for i in range(5):
            tsv_file = temp_directory / f"concurrent_{i}.tsv"
            tsv_file.write_text(f"key_{i}\tvalue_{i}", encoding='utf-8')
            files.append(tsv_file)
        
        # Sync all files
        results = []
        for file in files:
            result = converter_engine.sync_file(file)
            results.append(result)
        
        # All should succeed
        assert all(r.is_successful for r in results)
        
        # Test conversions work
        for i in range(5):
            result = converter_engine.convert_text(f"key_{i}", f"concurrent_{i}")
            assert result.is_successful
            assert result.converted_text == f"value_{i}"
    
    def test_performance_large_rule_set(self, converter_engine, temp_directory):
        """Test performance with large rule set."""
        # Create large TSV file
        large_content = []
        for i in range(1000):
            large_content.append(f"key_{i:04d}\tvalue_{i:04d}")
        
        large_file = temp_directory / "large_rules.tsv"
        large_file.write_text("\n".join(large_content), encoding='utf-8')
        
        # Sync should handle large file
        result = converter_engine.sync_file(large_file)
        assert result.is_successful
        assert result.rules_processed == 1000
        
        # Conversion should be fast
        conversion_result = converter_engine.convert_text("key_0500", "large_rules")
        assert conversion_result.is_successful
        assert conversion_result.converted_text == "value_0500"