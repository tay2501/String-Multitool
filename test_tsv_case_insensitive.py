"""
TSV大文字小文字無視変換の包括的テストスイート.

Enterprise-grade設計に基づく詳細なテストケースにより、
すべての機能が期待通りに動作することを検証します。

テスト範囲:
- 基本的な大文字小文字無視変換
- 元の大文字小文字パターンの保持
- オプション解析
- エラーハンドリング
- パフォーマンステスト
- 統合テスト
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

# Import modules to test
from string_multitool.core.transformations import TSVTransformation, TextTransformationEngine
from string_multitool.core.tsv_conversion_strategies import (
    CaseInsensitiveConversionStrategy,
    CaseSensitiveConversionStrategy,
    TSVConversionStrategyFactory,
)
from string_multitool.core.types import TSVConversionOptions
from string_multitool.exceptions import TransformationError, ValidationError


class TestTSVConversionOptions(unittest.TestCase):
    """TSVConversionOptionsデータクラスのテスト."""
    
    def test_default_options(self) -> None:
        """デフォルトオプションが正しく設定されるかテスト."""
        options = TSVConversionOptions()
        
        self.assertFalse(options.case_insensitive)
        self.assertTrue(options.preserve_original_case)
        self.assertFalse(options.match_whole_words_only)
        self.assertFalse(options.enable_regex_patterns)
    
    def test_custom_options(self) -> None:
        """カスタムオプションが正しく設定されるかテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=False
        )
        
        self.assertTrue(options.case_insensitive)
        self.assertFalse(options.preserve_original_case)
    
    def test_immutability(self) -> None:
        """オプションオブジェクトが不変であることをテスト."""
        options = TSVConversionOptions()
        
        with self.assertRaises(AttributeError):
            options.case_insensitive = True  # type: ignore


class TestCaseSensitiveConversionStrategy(unittest.TestCase):
    """大文字小文字を区別する変換戦略のテスト."""
    
    def setUp(self) -> None:
        """テストセットアップ."""
        self.strategy = CaseSensitiveConversionStrategy()
        self.options = TSVConversionOptions(case_insensitive=False)
        self.conversion_dict = {
            "API": "Application Programming Interface",
            "api": "application programming interface",
            "SQL": "Structured Query Language"
        }
    
    def test_exact_match_conversion(self) -> None:
        """完全一致による変換をテスト."""
        text = "Use API and SQL for development"
        result = self.strategy.convert_text(text, self.conversion_dict, self.options)
        expected = "Use Application Programming Interface and Structured Query Language for development"
        self.assertEqual(result, expected)
    
    def test_case_sensitive_behavior(self) -> None:
        """大文字小文字を区別する動作をテスト."""
        text = "Use api and API for development"
        result = self.strategy.convert_text(text, self.conversion_dict, self.options)
        expected = "Use application programming interface and Application Programming Interface for development"
        self.assertEqual(result, expected)
    
    def test_no_match_unchanged(self) -> None:
        """マッチしない場合は変更されないことをテスト."""
        text = "Use REST and GraphQL"
        result = self.strategy.convert_text(text, self.conversion_dict, self.options)
        self.assertEqual(result, text)
    
    def test_longest_match_priority(self) -> None:
        """最長マッチ優先をテスト."""
        conversion_dict = {
            "API": "Application Programming Interface",
            "API key": "Application Programming Interface key"
        }
        text = "Generate API key for authentication"
        result = self.strategy.convert_text(text, conversion_dict, self.options)
        expected = "Generate Application Programming Interface key for authentication"
        self.assertEqual(result, expected)


class TestCaseInsensitiveConversionStrategy(unittest.TestCase):
    """大文字小文字を無視する変換戦略のテスト."""
    
    def setUp(self) -> None:
        """テストセットアップ."""
        self.strategy = CaseInsensitiveConversionStrategy()
        self.conversion_dict = {
            "API": "Application Programming Interface",
            "SQL": "Structured Query Language",
            "HTTP": "HyperText Transfer Protocol"
        }
    
    def test_case_insensitive_match(self) -> None:
        """大文字小文字を無視したマッチングをテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        
        test_cases = [
            ("Use API for development", "Use Application Programming Interface for development"),
            ("Use api for development", "Use Application Programming Interface for development"),
            ("Use Api for development", "Use Application Programming Interface for development"),
            ("Use aPI for development", "Use Application Programming Interface for development"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.strategy.convert_text(input_text, self.conversion_dict, options)
                self.assertEqual(result, expected)
    
    def test_preserve_original_case_enabled(self) -> None:
        """元の大文字小文字パターンの保持をテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=True
        )
        
        test_cases = [
            ("Use API", "Use APPLICATION PROGRAMMING INTERFACE"),
            ("Use api", "Use application programming interface"),
            ("Use Api", "Use Application Programming Interface"),
            ("Use aPI", "Use aPPlication Programming Interface"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.strategy.convert_text(input_text, self.conversion_dict, options)
                self.assertEqual(result, expected)
    
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
                self.assertEqual(result, expected)
    
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
                self.assertEqual(result, expected)
    
    def test_mixed_content_conversion(self) -> None:
        """複数の変換が混在するテキストのテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=True
        )
        
        text = "Use API and sql with HTTP protocol"
        result = self.strategy.convert_text(text, self.conversion_dict, options)
        expected = "Use APPLICATION PROGRAMMING INTERFACE and sql with HTTP PROTOCOL"
        self.assertEqual(result, expected)


class TestTSVConversionStrategyFactory(unittest.TestCase):
    """TSV変換戦略ファクトリーのテスト."""
    
    def test_create_case_sensitive_strategy(self) -> None:
        """大文字小文字区別戦略の作成をテスト."""
        options = TSVConversionOptions(case_insensitive=False)
        strategy = TSVConversionStrategyFactory.create_strategy(options)
        self.assertIsInstance(strategy, CaseSensitiveConversionStrategy)
    
    def test_create_case_insensitive_strategy(self) -> None:
        """大文字小文字無視戦略の作成をテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        strategy = TSVConversionStrategyFactory.create_strategy(options)
        self.assertIsInstance(strategy, CaseInsensitiveConversionStrategy)
    
    def test_validate_options(self) -> None:
        """オプション検証をテスト."""
        valid_options = TSVConversionOptions()
        self.assertTrue(TSVConversionStrategyFactory.validate_options(valid_options))
        
        # 無効なオプション（型が違う）
        self.assertFalse(TSVConversionStrategyFactory.validate_options("invalid"))  # type: ignore
    
    def test_get_available_strategies(self) -> None:
        """利用可能な戦略一覧の取得をテスト."""
        strategies = TSVConversionStrategyFactory.get_available_strategies()
        expected = [
            "CaseSensitiveConversionStrategy",
            "CaseInsensitiveConversionStrategy"
        ]
        self.assertEqual(strategies, expected)


class TestTSVTransformationIntegration(unittest.TestCase):
    """TSVTransformationクラスの統合テスト."""
    
    def setUp(self) -> None:
        """テストセットアップ."""
        # 一時TSVファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.tsv_file = Path(self.temp_dir) / "test.tsv"
        
        # テスト用TSVデータ
        tsv_content = """API\tApplication Programming Interface
SQL\tStructured Query Language
HTTP\tHyperText Transfer Protocol
JSON\tJavaScript Object Notation"""
        
        self.tsv_file.write_text(tsv_content, encoding="utf-8")
    
    def tearDown(self) -> None:
        """テストクリーンアップ."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_default_case_sensitive_behavior(self) -> None:
        """デフォルトの大文字小文字区別動作をテスト."""
        transformer = TSVTransformation(str(self.tsv_file))
        
        text = "Use API and api for development"
        result = transformer.transform(text)
        expected = "Use Application Programming Interface and api for development"
        self.assertEqual(result, expected)
    
    def test_case_insensitive_option(self) -> None:
        """大文字小文字無視オプションをテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        text = "Use api and Api for development"
        result = transformer.transform(text)
        expected = "Use application programming interface and Application Programming Interface for development"
        self.assertEqual(result, expected)
    
    def test_update_options_runtime(self) -> None:
        """実行時オプション更新をテスト."""
        transformer = TSVTransformation(str(self.tsv_file))
        
        # 初期状態（大文字小文字区別）
        text = "Use api"
        result1 = transformer.transform(text)
        self.assertEqual(result1, "Use api")  # 変換されない
        
        # オプション更新（大文字小文字無視）
        new_options = TSVConversionOptions(case_insensitive=True)
        transformer.update_options(new_options)
        
        result2 = transformer.transform(text)
        self.assertEqual(result2, "Use application programming interface")
    
    def test_get_current_options(self) -> None:
        """現在のオプション取得をテスト."""
        options = TSVConversionOptions(case_insensitive=True)
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        current_options = transformer.get_current_options()
        self.assertEqual(current_options, options)
    
    def test_transformation_rule_string(self) -> None:
        """変換ルール文字列の生成をテスト."""
        options = TSVConversionOptions(
            case_insensitive=True,
            preserve_original_case=False
        )
        transformer = TSVTransformation(str(self.tsv_file), options)
        
        rule = transformer.get_transformation_rule()
        self.assertIn("convertbytsv", rule)
        self.assertIn("--case-insensitive", rule)
        self.assertIn("--no-preserve-case", rule)


class TestTextTransformationEngineIntegration(unittest.TestCase):
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
        self.assertEqual(result1["file_path"], "test_terms.tsv")
        self.assertFalse(result1["options"].case_insensitive)
        
        # POSIX準拠：オプション優先パターン
        args2 = ["--case-insensitive", "test_terms.tsv"]
        result2 = engine._parse_tsv_conversion_args(args2)
        self.assertEqual(result2["file_path"], "test_terms.tsv")
        self.assertTrue(result2["options"].case_insensitive)
        
        # 複数オプション（POSIX準拠）
        args3 = ["--case-insensitive", "--no-preserve-case", "test_terms.tsv"]
        result3 = engine._parse_tsv_conversion_args(args3)
        self.assertEqual(result3["file_path"], "test_terms.tsv")
        self.assertTrue(result3["options"].case_insensitive)
        self.assertFalse(result3["options"].preserve_original_case)
        
        # 短縮オプション（POSIX準拠）
        args4 = ["-i", "test_terms.tsv"]
        result4 = engine._parse_tsv_conversion_args(args4)
        self.assertEqual(result4["file_path"], "test_terms.tsv")
        self.assertTrue(result4["options"].case_insensitive)
        
        # 代替オプション名
        args5 = ["--caseinsensitive", "test_terms.tsv"]
        result5 = engine._parse_tsv_conversion_args(args5)
        self.assertEqual(result5["file_path"], "test_terms.tsv")
        self.assertTrue(result5["options"].case_insensitive)
        
        # ファイルパスなしエラー
        args6 = ["--case-insensitive"]
        with self.assertRaises(ValidationError):
            engine._parse_tsv_conversion_args(args6)


class TestPerformanceAndEdgeCases(unittest.TestCase):
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
        self.assertLess(end_time - start_time, 1.0)
        self.assertIn("Definition for term 0001", result)
        self.assertIn("definition for term 0500", result)
    
    def test_empty_tsv_file(self) -> None:
        """空のTSVファイルのテスト."""
        empty_file = Path(self.temp_dir) / "empty.tsv"
        empty_file.write_text("", encoding="utf-8")
        
        transformer = TSVTransformation(str(empty_file))
        text = "No conversion should happen"
        result = transformer.transform(text)
        self.assertEqual(result, text)
    
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
        self.assertEqual(result, expected)
    
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
        self.assertEqual(result, expected)


class TestErrorHandling(unittest.TestCase):
    """エラーハンドリングのテスト."""
    
    def test_nonexistent_file(self) -> None:
        """存在しないファイルのエラーハンドリング."""
        with self.assertRaises(ValidationError):
            TSVTransformation("/nonexistent/path.tsv")
    
    def test_invalid_options_type(self) -> None:
        """無効なオプション型のエラーハンドリング."""
        temp_dir = tempfile.mkdtemp()
        tsv_file = Path(temp_dir) / "test.tsv"
        tsv_file.write_text("API\tApplication Programming Interface", encoding="utf-8")
        
        try:
            with self.assertRaises((TypeError, ValidationError)):
                TSVTransformation(str(tsv_file), "invalid_options")  # type: ignore
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_strategy_error_handling(self) -> None:
        """戦略エラーハンドリングのテスト."""
        strategy = CaseInsensitiveConversionStrategy()
        options = TSVConversionOptions()
        
        # 無効な入力タイプ
        with self.assertRaises(ValidationError):
            strategy.convert_text(123, {}, options)  # type: ignore
        
        # 無効な変換辞書タイプ
        with self.assertRaises(ValidationError):
            strategy.convert_text("text", "invalid_dict", options)  # type: ignore


if __name__ == "__main__":
    # テストスイートを実行
    unittest.main(verbosity=2)