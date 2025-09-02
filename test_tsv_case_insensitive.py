"""
Modern pytest-based test suite for TSV case-insensitive conversion functionality.

This comprehensive test suite demonstrates enterprise-grade testing patterns using pytest
with modern fixtures, parametrization, and best practices for maintainable tests.

Test coverage:
- Basic case-insensitive conversion functionality
- Original case pattern preservation
- Option parsing and validation
- Error handling scenarios  
- Performance testing with realistic thresholds
- End-to-end integration testing
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

# Import modules to test
from string_multitool.core.transformations import TSVTransformation, TextTransformationEngine
from string_multitool.core.tsv_conversion_strategies import (
    CaseInsensitiveConversionStrategy,
    CaseSensitiveConversionStrategy,
    TSVConversionStrategyFactory,
)
from string_multitool.core.types import TSVConversionOptions
from string_multitool.exceptions import TransformationError, ValidationError


# Modern pytest fixtures for shared test data
@pytest.fixture
def default_conversion_dict() -> dict[str, str]:
    """Provide standard conversion dictionary for testing."""
    return {
        "API": "Application Programming Interface",
        "SQL": "Structured Query Language", 
        "HTTP": "HyperText Transfer Protocol"
    }


class TestTSVConversionOptions:
    """Test TSV conversion options dataclass with modern pytest patterns."""
    
    def test_default_options(self) -> None:
        """Test that default options are correctly set."""
        options = TSVConversionOptions()
        
        assert not options.case_insensitive
        assert options.preserve_original_case
        assert not options.match_whole_words_only
        assert not options.enable_regex_patterns
    
    @pytest.mark.parametrize("case_insensitive,preserve_original_case", [
        (True, False),
        (True, True),
        (False, False),
        (False, True),
    ])
    def test_custom_options(self, case_insensitive: bool, preserve_original_case: bool) -> None:
        """Test custom options using parametrized testing."""
        options = TSVConversionOptions(
            case_insensitive=case_insensitive,
            preserve_original_case=preserve_original_case
        )
        
        assert options.case_insensitive == case_insensitive
        assert options.preserve_original_case == preserve_original_case
    
    def test_immutability(self) -> None:
        """Test that options object is immutable (dataclass frozen behavior)."""
        options = TSVConversionOptions()
        
        with pytest.raises(AttributeError):
            options.case_insensitive = True  # type: ignore


class TestCaseSensitiveConversionStrategy:
    """Test case-sensitive conversion strategy with modern pytest patterns."""
    
    @pytest.fixture
    def strategy(self) -> CaseSensitiveConversionStrategy:
        """Provide case-sensitive strategy instance."""
        return CaseSensitiveConversionStrategy()
    
    @pytest.fixture
    def case_sensitive_options(self) -> TSVConversionOptions:
        """Provide case-sensitive options."""
        return TSVConversionOptions(case_insensitive=False)
    
    def test_exact_match_conversion(
        self, 
        strategy: CaseSensitiveConversionStrategy, 
        default_conversion_dict: dict[str, str],
        case_sensitive_options: TSVConversionOptions
    ) -> None:
        """Test exact match conversion functionality."""
        text = "Use API and SQL for development"
        result = strategy.convert_text(text, default_conversion_dict, case_sensitive_options)
        expected = "Use Application Programming Interface and Structured Query Language for development"
        assert result == expected
    
    def test_case_sensitive_behavior(
        self,
        strategy: CaseSensitiveConversionStrategy,
        default_conversion_dict: dict[str, str], 
        case_sensitive_options: TSVConversionOptions
    ) -> None:
        """Test case-sensitive behavior distinguishes different cases."""
        text = "Use api and API for development"
        result = strategy.convert_text(text, default_conversion_dict, case_sensitive_options)
        expected = "Use api and Application Programming Interface for development"
        assert result == expected
    
    @pytest.mark.parametrize("test_text", [
        "Use REST and GraphQL",
        "Use NoMatch and Unknown", 
        "This has no replacements at all"
    ])
    def test_no_match_unchanged(
        self,
        strategy: CaseSensitiveConversionStrategy,
        default_conversion_dict: dict[str, str],
        case_sensitive_options: TSVConversionOptions,
        test_text: str
    ) -> None:
        """Test that text without matches remains unchanged."""
        result = strategy.convert_text(test_text, default_conversion_dict, case_sensitive_options)
        assert result == test_text
    
    def test_longest_match_priority(
        self,
        strategy: CaseSensitiveConversionStrategy,
        case_sensitive_options: TSVConversionOptions
    ) -> None:
        """Test that longest matches take priority over shorter ones."""
        conversion_dict = {
            "API": "Application Programming Interface",
            "API key": "Application Programming Interface key"
        }
        text = "Generate API key for authentication"
        result = strategy.convert_text(text, conversion_dict, case_sensitive_options)
        expected = "Generate Application Programming Interface key for authentication"
        assert result == expected


class TestCaseInsensitiveConversionStrategy:
    """Test case-insensitive conversion strategy with modern pytest patterns."""
    
    @pytest.fixture
    def strategy(self) -> CaseInsensitiveConversionStrategy:
        """Provide case-insensitive strategy instance."""
        return CaseInsensitiveConversionStrategy()
    
    @pytest.fixture
    def case_insensitive_options(self) -> TSVConversionOptions:
        """Provide case-insensitive options."""
        return TSVConversionOptions(case_insensitive=True)
    
    @pytest.mark.parametrize("input_text,expected", [
        ("Use API for development", "Use APPLICATION PROGRAMMING INTERFACE for development"),
        ("Use api for development", "Use application programming interface for development"),
        ("Use Api for development", "Use Application Programming Interface for development"),
        ("Use aPI for development", "Use application programming interface for development"),
    ])
    def test_case_insensitive_match(
        self,
        strategy: CaseInsensitiveConversionStrategy,
        default_conversion_dict: dict[str, str],
        case_insensitive_options: TSVConversionOptions,
        input_text: str,
        expected: str
    ) -> None:
        """Test case-insensitive matching behavior using parametrized testing."""
        result = strategy.convert_text(input_text, default_conversion_dict, case_insensitive_options)
        assert result == expected
    
    @pytest.mark.parametrize("input_text,expected", [
        ("Use API", "Use APPLICATION PROGRAMMING INTERFACE"),
        ("Use api", "Use application programming interface"),
        ("Use Api", "Use Application Programming Interface"),
        ("Use aPI", "Use application programming interface"),
    ])
    def test_preserve_original_case_enabled(
        self,
        strategy: CaseInsensitiveConversionStrategy,
        default_conversion_dict: dict[str, str],
        input_text: str,
        expected: str
    ) -> None:
        """Test preservation of original case patterns using parametrized testing."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=True
        )
        result = strategy.convert_text(input_text, default_conversion_dict, options)
        assert result == expected
    
    @pytest.mark.parametrize("input_text,expected", [
        ("Use API", "Use Application Programming Interface"),
        ("Use api", "Use Application Programming Interface"),
        ("Use Api", "Use Application Programming Interface"),
        ("Use aPI", "Use Application Programming Interface"),
    ])
    def test_preserve_original_case_disabled(
        self,
        strategy: CaseInsensitiveConversionStrategy,
        default_conversion_dict: dict[str, str],
        input_text: str,
        expected: str
    ) -> None:
        """Test preservation of original case disabled using parametrized testing."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=False
        )
        result = strategy.convert_text(input_text, default_conversion_dict, options)
        assert result == expected
    
    
    def test_mixed_content_conversion(
        self,
        strategy: CaseInsensitiveConversionStrategy,
        default_conversion_dict: dict[str, str]
    ) -> None:
        """Test mixed content conversion with case preservation."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=True
        )
        
        text = "Use API and sql with HTTP protocol"
        result = strategy.convert_text(text, default_conversion_dict, options)
        expected = "Use APPLICATION PROGRAMMING INTERFACE and structured query language with HYPERTEXT TRANSFER PROTOCOL protocol"
        assert result == expected


class TestTSVConversionStrategyFactory:
    """Test TSV conversion strategy factory."""
    
    @pytest.mark.parametrize("case_insensitive,expected_type", [
        (False, CaseSensitiveConversionStrategy),
        (True, CaseInsensitiveConversionStrategy),
    ])
    def test_create_strategy(
        self, 
        case_insensitive: bool, 
        expected_type: type
    ) -> None:
        """Test strategy creation using parametrized testing."""
        options = TSVConversionOptions(case_insensitive=case_insensitive)
        strategy = TSVConversionStrategyFactory.create_strategy(options)
        assert isinstance(strategy, expected_type)
    
    def test_validate_options(self) -> None:
        """Test option validation functionality."""
        valid_options = TSVConversionOptions()
        assert TSVConversionStrategyFactory.validate_options(valid_options)
        
        # Invalid options (wrong type)
        assert not TSVConversionStrategyFactory.validate_options("invalid")  # type: ignore
    
    def test_get_available_strategies(self) -> None:
        """Test getting list of available strategies."""
        strategies = TSVConversionStrategyFactory.get_available_strategies()
        expected = [
            "CaseSensitiveConversionStrategy",
            "CaseInsensitiveConversionStrategy"
        ]
        assert strategies == expected


class TestTSVTransformationIntegration:
    """TSV Transformation integration tests with modern pytest patterns."""
    
    @pytest.fixture
    def tsv_test_file(self) -> Path:
        """Create temporary TSV file for testing."""
        temp_dir = tempfile.mkdtemp()
        tsv_file = Path(temp_dir) / "test.tsv"
        
        # Test TSV data
        tsv_content = """API\tApplication Programming Interface
SQL\tStructured Query Language  
HTTP\tHyperText Transfer Protocol
JSON\tJavaScript Object Notation"""
        
        tsv_file.write_text(tsv_content, encoding="utf-8")
        
        yield tsv_file
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_default_case_sensitive_behavior(self, tsv_test_file: Path) -> None:
        """Test default case-sensitive behavior."""
        transformer = TSVTransformation(str(tsv_test_file))
        
        text = "Use API and api for development"
        result = transformer.transform(text)
        expected = "Use Application Programming Interface and api for development"
        assert result == expected
    
    def test_case_insensitive_option(self, tsv_test_file: Path) -> None:
        """Test case-insensitive option."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(tsv_test_file), options)
        
        text = "Use api and Api for development"
        result = transformer.transform(text)
        expected = "Use application programming interface and Application Programming Interface for development"
        assert result == expected
    
    def test_update_options_runtime(self, tsv_test_file: Path) -> None:
        """Test runtime option updates."""
        transformer = TSVTransformation(str(tsv_test_file))
        
        # Initial state (case-sensitive)
        text = "Use api"
        result1 = transformer.transform(text)
        assert result1 == "Use api"  # No conversion
        
        # Update options (case-insensitive)
        new_options = TSVConversionOptions(case_insensitive=True)
        transformer.update_options(new_options)
        
        result2 = transformer.transform(text)
        assert result2 == "Use application programming interface"
    
    def test_get_current_options(self, tsv_test_file: Path) -> None:
        """Test getting current options."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(tsv_test_file), options)
        
        current_options = transformer.get_current_options()
        assert current_options == options
    
    def test_transformation_rule_string(self, tsv_test_file: Path) -> None:
        """Test transformation rule string generation."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=False
        )
        transformer = TSVTransformation(str(tsv_test_file), options)
        
        rule = transformer.get_transformation_rule()
        assert "convertbytsv" in rule
        assert "--case-insensitive" in rule
        assert "--no-preserve-case" in rule


class TestTextTransformationEngineIntegration:
    """Test text transformation engine TSV conversion integration."""
    
    @pytest.fixture
    def engine_test_file(self) -> Path:
        """Create temporary TSV file for engine testing."""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / "config" / "tsv_rules"
        config_dir.mkdir(parents=True)
        
        tsv_file = config_dir / "test_terms.tsv"
        
        # Test TSV data
        tsv_content = """API\tApplication Programming Interface
REST\tRepresentational State Transfer"""
        
        tsv_file.write_text(tsv_content, encoding="utf-8")
        
        yield tsv_file
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_parse_tsv_conversion_args(self) -> None:
        """TSV変換引数解析をテスト（POSIX準拠：オプション優先パターン）."""
        # テスト用のエンジンインスタンスを作成
        from string_multitool.core.config import ConfigurationManager
        config_manager = ConfigurationManager()
        engine = TextTransformationEngine(config_manager)
        
        # 基本的な引数（オプションなし）
        args1 = ["test_terms.tsv"]
        result1 = engine._parse_tsv_conversion_args(args1)
        assert result1["file_path"] == "test_terms.tsv"
        assert not result1["options"].case_insensitive
        
        # POSIX準拠：オプション優先パターン
        args2 = ["--case-insensitive", "test_terms.tsv"]
        result2 = engine._parse_tsv_conversion_args(args2)
        assert result2["file_path"] == "test_terms.tsv"
        assert result2["options"].case_insensitive
        
        # 複数オプション（POSIX準拠）
        args3 = ["--case-insensitive", "--no-preserve-case", "test_terms.tsv"]
        result3 = engine._parse_tsv_conversion_args(args3)
        assert result3["file_path"] == "test_terms.tsv"
        assert result3["options"].case_insensitive
        assert not result3["options"].preserve_original_case
        
        # 短縮オプション（POSIX準拠）
        args4 = ["-i", "test_terms.tsv"]
        result4 = engine._parse_tsv_conversion_args(args4)
        assert result4["file_path"] == "test_terms.tsv"
        assert result4["options"].case_insensitive
        
        # 代替オプション名
        args5 = ["--caseinsensitive", "test_terms.tsv"]
        result5 = engine._parse_tsv_conversion_args(args5)
        assert result5["file_path"] == "test_terms.tsv"
        assert result5["options"].case_insensitive
        
        # ファイルパスなしエラー
        args6 = ["--case-insensitive"]
        with pytest.raises(ValidationError):
            engine._parse_tsv_conversion_args(args6)


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases."""
    
    @pytest.fixture
    def performance_tsv_file(self) -> Path:
        """Create large TSV file for performance testing."""
        temp_dir = tempfile.mkdtemp()
        tsv_file = Path(temp_dir) / "performance_test.tsv"
        
        # Create large TSV file
        large_content = []
        for i in range(1000):
            large_content.append(f"TERM{i:04d}\tDefinition for term {i:04d}")
        
        tsv_file.write_text("\n".join(large_content), encoding="utf-8")
        
        yield tsv_file
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_large_tsv_file_performance(self, performance_tsv_file: Path) -> None:
        """Test large TSV file performance."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(performance_tsv_file), options)
        
        text = "Use TERM0001 and term0500 in your code"
        
        start_time = time.time()
        result = transformer.transform(text)
        end_time = time.time()
        
        # Performance verification (should complete within 1 second)
        assert end_time - start_time < 1.0
        # TERM0001 is all caps, so replacement should be all caps too
        assert "DEFINITION FOR TERM 0001" in result
        # term0500 is lowercase, so replacement should be lowercase too
        assert "definition for term 0500" in result
    
    def test_empty_tsv_file(self, performance_tsv_file: Path) -> None:
        """Test empty TSV file."""
        empty_file = performance_tsv_file.parent / "empty.tsv"
        empty_file.write_text("", encoding="utf-8")
        
        transformer = TSVTransformation(str(empty_file))
        text = "No conversion should happen"
        result = transformer.transform(text)
        assert result == text
    
    def test_malformed_tsv_lines(self, performance_tsv_file: Path) -> None:
        """Test malformed TSV lines."""
        malformed_file = performance_tsv_file.parent / "malformed.tsv"
        content = """API\tApplication Programming Interface
\tMissing key
Value without key
SQL\tStructured Query Language\tExtra column"""
        
        malformed_file.write_text(content, encoding="utf-8")
        
        transformer = TSVTransformation(str(malformed_file))
        text = "Use API and SQL"
        result = transformer.transform(text)
        expected = "Use Application Programming Interface and Structured Query Language"
        assert result == expected
    
    def test_unicode_content(self, performance_tsv_file: Path) -> None:
        """Test Unicode content."""
        unicode_file = performance_tsv_file.parent / "unicode.tsv"
        content = """API\tアプリケーション プログラミング インターフェース
データベース\tDatabase
🚀\tRocket Emoji"""
        
        unicode_file.write_text(content, encoding="utf-8")
        
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(unicode_file), options)
        
        text = "Use api and データベース and 🚀"
        result = transformer.transform(text)
        expected = "Use アプリケーション プログラミング インターフェース and database and rocket emoji"
        assert result == expected


class TestErrorHandling:
    """Test error handling."""
    
    def test_nonexistent_file(self) -> None:
        """Test error handling for nonexistent file."""
        with pytest.raises(ValidationError):
            TSVTransformation("/nonexistent/path.tsv")
    
    def test_invalid_options_type(self) -> None:
        """Test error handling for invalid options type."""
        temp_dir = tempfile.mkdtemp()
        tsv_file = Path(temp_dir) / "test.tsv"
        tsv_file.write_text("API\tApplication Programming Interface", encoding="utf-8")
        
        try:
            with pytest.raises((TypeError, ValidationError)):
                TSVTransformation(str(tsv_file), "invalid_options")  # type: ignore
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_strategy_error_handling(self) -> None:
        """Test strategy error handling."""
        strategy = CaseInsensitiveConversionStrategy()
        options = TSVConversionOptions()
        
        # Invalid input type
        with pytest.raises(ValidationError):
            strategy.convert_text(123, {}, options)  # type: ignore
        
        # Invalid conversion dictionary type
        with pytest.raises(ValidationError):
            strategy.convert_text("text", "invalid_dict", options)  # type: ignore


if __name__ == "__main__":
    # Run tests with modern pytest
    pytest.main([__file__, "-v"])