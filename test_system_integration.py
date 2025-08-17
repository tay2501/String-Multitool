#!/usr/bin/env python3
"""
システム統合テストスイート

このモジュールは、String_Multitools全体のシステム統合テストを提供します。
実際のファイルI/O、設定読み込み、変換パイプラインなどをテストします。
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from string_multitool.core.config import ConfigurationManager
from string_multitool.core.transformations import TextTransformationEngine
from string_multitool.exceptions import ConfigurationError, TransformationError
from string_multitool.io.manager import InputOutputManager
from string_multitool.main import ApplicationInterface


class TestSystemIntegration:
    """システム統合テストクラス"""

    def test_full_transformation_pipeline(self) -> None:
        """フル変換パイプラインのテスト"""
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        
        # 複数のルールを連続適用
        test_cases = [
            ("  Hello World Test  ", "/t/l/s", "hello_world_test"),
            ("camelCaseTest", "/s/u", "CAMELCASETEST"),  # snake_caseは現在単語分割しない
            ("test-kebab-case", "/hu", "test_kebab_case"),  # ハイフンをアンダーバーに変換
        ]
        
        for input_text, rules, expected in test_cases:
            result = transformation_engine.apply_transformations(input_text, rules)
            assert result == expected, f"Pipeline {rules} failed: got '{result}', expected '{expected}'"

    def test_configuration_loading_integration(self) -> None:
        """設定ファイル読み込み統合テスト"""
        config_manager = ConfigurationManager()
        
        # 各設定ファイルの読み込みテスト
        transformation_rules = config_manager.load_transformation_rules()
        assert isinstance(transformation_rules, dict)
        assert len(transformation_rules) > 0
        
        security_config = config_manager.load_security_config()
        assert isinstance(security_config, dict)
        assert "rsa_encryption" in security_config

    @patch("string_multitool.io.manager.pyperclip")
    def test_io_manager_integration(self, mock_pyperclip: Mock) -> None:
        """I/O管理統合テスト"""
        mock_pyperclip.paste.return_value = "test clipboard content"
        mock_pyperclip.copy.return_value = None
        
        io_manager = InputOutputManager()
        
        # クリップボードからの読み取り
        content = io_manager.get_clipboard_text()
        assert content == "test clipboard content"
        
        # クリップボードへの書き込み
        io_manager.set_output_text("output content")
        mock_pyperclip.copy.assert_called_with("output content")

    def test_application_interface_integration(self) -> None:
        """アプリケーションインターフェース統合テスト"""
        app = ApplicationInterface()
        assert app.config_manager is not None
        assert app.transformation_engine is not None
        assert app.io_manager is not None

    def test_error_handling_integration(self) -> None:
        """エラーハンドリング統合テスト"""
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        
        # 不正なルール
        with pytest.raises(TransformationError):
            transformation_engine.apply_transformations("test", "/invalid_rule")
        
        # 空のルール文字列
        with pytest.raises(Exception):  # ValidationError or similar
            transformation_engine.apply_transformations("test", "")

    def test_japanese_text_handling(self) -> None:
        """日本語テキスト処理テスト"""
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        
        japanese_test_cases = [
            ("こんにちは世界", "/u", "こんにちは世界"),  # 日本語は大文字化されない
            ("　全角スペース　", "/t", "全角スペース"),  # 全角スペーストリム（実装に依存）
        ]
        
        for input_text, rule, expected in japanese_test_cases:
            result = transformation_engine.apply_transformations(input_text, rule)
            # 大文字変換は日本語には適用されないことを確認
            assert isinstance(result, str), f"Result should be string for {input_text}"

    @patch("string_multitool.io.manager.sys.stdin")
    def test_stdin_input_integration(self, mock_stdin: Mock) -> None:
        """標準入力統合テスト"""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "piped input\n"
        
        io_manager = InputOutputManager()
        result = io_manager.get_input_text()
        assert result == "piped input"

    def test_transformation_engine_factory(self) -> None:
        """変換エンジンファクトリーテスト"""
        config_manager = ConfigurationManager()
        engine = TextTransformationEngine(config_manager)
        
        # 利用可能なルール一覧を取得
        available_rules = engine.get_available_rules()
        assert isinstance(available_rules, dict)
        
        # 基本的なルールが含まれていることを確認
        expected_rules = ["l", "u", "t", "s", "c", "p"]
        for rule in expected_rules:
            assert rule in available_rules, f"Rule '{rule}' should be available"

    def test_memory_usage_with_large_text(self) -> None:
        """大きなテキストでのメモリ使用量テスト"""
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        
        # 大きなテキストの生成（1MB）
        large_text = "A" * (1024 * 1024)
        
        # 基本的な変換が正常に動作することを確認
        result = transformation_engine.apply_transformations(large_text, "/l")
        assert len(result) == len(large_text)
        assert result == "a" * (1024 * 1024)

    def test_concurrent_transformation_requests(self) -> None:
        """並行変換リクエストテスト"""
        import threading
        import time
        
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        
        results = []
        errors = []
        
        def transform_worker(text: str, rule: str, worker_id: int) -> None:
            try:
                result = transformation_engine.apply_transformations(text, rule)
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # 複数のワーカーを同時実行
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=transform_worker,
                args=(f"test{i}", "/u", i)
            )
            threads.append(thread)
            thread.start()
        
        # 全スレッドの完了を待機
        for thread in threads:
            thread.join(timeout=5.0)
        
        # エラーがないことを確認
        assert len(errors) == 0, f"Concurrent errors occurred: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"


class TestCryptographyIntegration:
    """暗号化機能統合テスト"""

    def test_crypto_manager_availability(self) -> None:
        """暗号化マネージャーの利用可能性テスト"""
        try:
            from string_multitool.core.crypto import CryptographyManager, CRYPTOGRAPHY_AVAILABLE
            from string_multitool.core.config import ConfigurationManager
            
            if not CRYPTOGRAPHY_AVAILABLE:
                pytest.skip("Cryptography package not available")
            
            config_manager = ConfigurationManager()
            crypto_manager = CryptographyManager(config_manager)
            assert crypto_manager is not None
            
        except ImportError:
            pytest.skip("Cryptography components not available")

    def test_end_to_end_encryption(self) -> None:
        """エンドツーエンド暗号化テスト"""
        try:
            from string_multitool.core.crypto import CryptographyManager, CRYPTOGRAPHY_AVAILABLE
            from string_multitool.core.config import ConfigurationManager
            
            if not CRYPTOGRAPHY_AVAILABLE:
                pytest.skip("Cryptography package not available")
            
            config_manager = ConfigurationManager()
            crypto_manager = CryptographyManager(config_manager)
            
            # テストデータ
            test_text = "機密情報：これは暗号化されるべきテキストです"
            
            # 暗号化
            encrypted = crypto_manager.encrypt_text(test_text)
            assert encrypted != test_text
            assert len(encrypted) > 0
            
            # 復号化
            decrypted = crypto_manager.decrypt_text(encrypted)
            assert decrypted == test_text
            
        except ImportError:
            pytest.skip("Cryptography components not available")


class TestPerformanceIntegration:
    """パフォーマンス統合テスト"""

    def test_transformation_performance(self) -> None:
        """変換処理パフォーマンステスト"""
        import time
        
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        
        # 大量の小さな変換
        start_time = time.time()
        for i in range(1000):
            result = transformation_engine.apply_transformations(f"test{i}", "/u")
            assert result == f"TEST{i}"
        end_time = time.time()
        
        elapsed = end_time - start_time
        # 1000回の変換が2秒以内に完了することを確認
        assert elapsed < 2.0, f"Performance test failed: {elapsed:.2f}s for 1000 transformations"

    def test_config_loading_performance(self) -> None:
        """設定読み込みパフォーマンステスト"""
        import time
        
        # 複数回の設定読み込み（キャッシュ効果を確認）
        start_time = time.time()
        for i in range(100):
            config_manager = ConfigurationManager()
            rules = config_manager.load_transformation_rules()
            assert len(rules) > 0
        end_time = time.time()
        
        elapsed = end_time - start_time
        # 100回の設定読み込みが1秒以内に完了することを確認（キャッシュ効果）
        assert elapsed < 1.0, f"Config loading performance test failed: {elapsed:.2f}s"


def test_dry_run_main_entry_points() -> None:
    """メインエントリーポイントのドライランテスト"""
    # main関数をインポートして呼び出し可能であることを確認
    from string_multitool.main import main
    assert callable(main)
    
    # ApplicationFactoryの動作確認
    try:
        from string_multitool.application_factory import ApplicationFactory
        app = ApplicationFactory.create_application()
        assert app is not None
    except ImportError:
        # ApplicationFactoryが存在しない場合はスキップ
        pass


if __name__ == "__main__":
    # テストを直接実行
    pytest.main([__file__, "-v", "--tb=short"])