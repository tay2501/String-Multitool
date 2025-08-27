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
        "api": "application programming interface", 
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
        expected = "Use application programming interface and Application Programming Interface for development"
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
        ("Use API for development", "Use Application Programming Interface for development"),
        ("Use api for development", "Use Application Programming Interface for development"),
        ("Use Api for development", "Use Application Programming Interface for development"),
        ("Use aPI for development", "Use Application Programming Interface for development"),
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
        ("Use aPI", "Use aPPlication Programming Interface"),
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
    
    def test_preserve_original_case_disabled(self) -> None:
        """元の大文字小文字パターンの保持無効をテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=False
        )
        
        test_cases = [
            ("Use API", "Use Application Programming Interface"),
            ("Use api", "Use Application Programming Interface"),
            ("Use Api", "Use Application Programming Interface"),
            ("Use aPI", "Use Application Programming Interface"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.strategy.convert_text(input_text, self.conversion_dict, options)
                assert result == expected
    
    def test_case_pattern_application(self) -> None:
        """大文字小文字パターン適用の詳細テスト."""
        # プライベートメソッドのテスト（通常は推奨されないが、重要なロジックのため）
        strategy = CaseInsensitiveConversionStrategy()
        
        test_cases = [
            ("API", "Application Programming Interface", "APPLICATION PROGRAMMING INTERFACE"),
            ("api", "Application Programming Interface", "application programming interface"),
            ("Api", "Application Programming Interface", "Application Programming Interface"),
            ("aPI", "Application Programming Interface", "aPPlication Programming Interface"),
            ("A", "Application Programming Interface", "Application Programming Interface"),  # 短い場合
        ]
        
        for original, replacement, expected in test_cases:
            with self.subTest(original=original, replacement=replacement):
                result = strategy._apply_case_pattern(original, replacement)
                assert result == expected
    
    def test_mixed_content_conversion(self) -> None:
        """複数の変換が混在するテキストのテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=True
        )
        
        text = "Use API and sql with HTTP protocol"
        result = self.strategy.convert_text(text, self.conversion_dict, options)
        expected = "Use APPLICATION PROGRAMMING INTERFACE and sql with HTTP PROTOCOL"
        assert result == expected


class TestTSVConversionStrategyFactory:
    """TSV変換戦略ファクトリーのテスト."""
    
    def test_create_case_sensitive_strategy(self) -> None:
        """大文字小文字区別戦略の作成をテスト."""
        options = TSVConversionOptions(case_insensitive=False)
        strategy = TSVConversionStrategyFactory.create_strategy(options)
        assert isinstance(strategy, CaseSensitiveConversionStrategy)
    
    def test_create_case_insensitive_strategy(self) -> None:
        """大文字小文字無視戦略の作成をテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        strategy = TSVConversionStrategyFactory.create_strategy(options)
        assert isinstance(strategy, CaseInsensitiveConversionStrategy)
    
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
    
    def test_default_case_sensitive_behavior(self) -> None:
        """デフォルトの大文字小文字区別動作をテスト."""
        transformer = TSVTransformation(str(self.tsv_file))
        
        text = "Use API and api for development"
        result = transformer.transform(text)
        expected = "Use Application Programming Interface and api for development"
        assert result == expected
    
    def test_case_insensitive_option(self) -> None:
        """大文字小文字無視オプションをテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        text = "Use api and Api for development"
        result = transformer.transform(text)
        expected = "Use application programming interface and Application Programming Interface for development"
        assert result == expected
    
    def test_update_options_runtime(self) -> None:
        """実行時オプション更新をテスト."""
        transformer = TSVTransformation(str(self.tsv_file))
        
        # 初期状態（大文字小文字区別）
        text = "Use api"
        result1 = transformer.transform(text)
        assert result1 == "Use api"  # 変換されない
        
        # オプション更新（大文字小文字無視）
        new_options = TSVConversionOptions(case_insensitive=True)
        transformer.update_options(new_options)
        
        result2 = transformer.transform(text)
        assert result2 == "Use application programming interface"
    
    def test_get_current_options(self) -> None:
        """現在のオプション取得をテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        current_options = transformer.get_current_options()
        assert current_options == options
    
    def test_transformation_rule_string(self) -> None:
        """変換ルール文字列の生成をテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=False
        )
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        rule = transformer.get_transformation_rule()
        assert "convertbytsv" in rule
        assert "--case-insensitive" in rule
        assert "--no-preserve-case" in rule


class TestTextTransformationEngineIntegration():
    """TextTransformationEngineでのTSV変換統合テスト."""
    
    def setUp(self) -> None:
        """テストセットアップ."""
        # 一時TSVファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config" / "tsv_rules"
        self.config_dir.mkdir(parents=True)
        
        self.tsv_file = self.config_dir / "test_terms.tsv"
        
        # テスト用TSVデータ
        tsv_content = """API\tApplication Programming Interface
REST\tRepresentational State Transfer"""
        
        self.tsv_file.write_text(tsv_content, encoding="utf-8")
    
    def tearDown(self) -> None:
        """テストクリーンアップ."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
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


class TestPerformanceAndEdgeCases():
    """パフォーマンスとエッジケースのテスト."""
    
    def setUp(self) -> None:
        """テストセットアップ."""
        self.temp_dir = tempfile.mkdtemp()
        self.tsv_file = Path(self.temp_dir) / "performance_test.tsv"
        
        # 大きなTSVファイルを作成
        large_content = []
        for i in range(1000):
            large_content.append(f"TERM{i:04d}\tDefinition for term {i:04d}")
        
        self.tsv_file.write_text("\n".join(large_content), encoding="utf-8")
    
    def tearDown(self) -> None:
        """テストクリーンアップ."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_large_tsv_file_performance(self) -> None:
        """大きなTSVファイルのパフォーマンステスト."""
        import time
        
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        text = "Use TERM0001 and term0500 in your code"
        
        start_time = time.time()
        result = transformer.transform(text)
        end_time = time.time()
        
        # パフォーマンス検証（1秒以内で完了することを期待）
        assert end_time - start_time < 1.0
        assert "Definition for term 0001" in result
        assert "definition for term 0500" in result
    
    def test_empty_tsv_file(self) -> None:
        """空のTSVファイルのテスト."""
        empty_file = Path(self.temp_dir) / "empty.tsv"
        empty_file.write_text("", encoding="utf-8")
        
        transformer = TSVTransformation(str(empty_file))
        text = "No conversion should happen"
        result = transformer.transform(text)
        assert result == text
    
    def test_malformed_tsv_lines(self) -> None:
        """不正な形式のTSV行のテスト."""
        malformed_file = Path(self.temp_dir) / "malformed.tsv"
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
    
    def test_unicode_content(self) -> None:
        """Unicode文字のテスト."""
        unicode_file = Path(self.temp_dir) / "unicode.tsv"
        content = """API\tアプリケーション プログラミング インターフェース
データベース\tDatabase
🚀\tRocket Emoji"""
        
        unicode_file.write_text(content, encoding="utf-8")
        
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(unicode_file), options)
        
        text = "Use api and データベース and 🚀"
        result = transformer.transform(text)
        expected = "Use アプリケーション プログラミング インターフェース and Database and Rocket Emoji"
        assert result == expected


class TestErrorHandling():
    """エラーハンドリングのテスト."""
    
    def test_nonexistent_file(self) -> None:
        """存在しないファイルのエラーハンドリング."""
        with pytest.raises(ValidationError):
            TSVTransformation("/nonexistent/path.tsv")
    
    def test_invalid_options_type(self) -> None:
        """無効なオプション型のエラーハンドリング."""
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
        """戦略エラーハンドリングのテスト."""
        strategy = CaseInsensitiveConversionStrategy()
        options = TSVConversionOptions()
        
        # 無効な入力タイプ
        with pytest.raises(ValidationError):
            strategy.convert_text(123, {}, options)  # type: ignore
        
        # 無効な変換辞書タイプ
        with pytest.raises(ValidationError):
            strategy.convert_text("text", "invalid_dict", options)  # type: ignore


if __name__ == "__main__":
    # Run tests with modern pytest
    pytest.main([__file__, "-v"])