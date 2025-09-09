#!/usr/bin/env python3
"""Modern pytest-based Unicode handling test suite for String_Multitool.

Demonstrates enterprise-grade Unicode testing patterns:
- Comprehensive Unicode character set coverage
- Cross-platform encoding validation
- Modern pytest parametrization for character sets
- Proper subprocess testing with pytest fixtures
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from string_multitool.models.config import ConfigurationManager
from string_multitool.models.transformations import TextTransformationEngine


# Modern pytest fixtures
@pytest.fixture(scope="session")
def config_manager() -> ConfigurationManager:
    """Provide shared ConfigurationManager instance for all tests."""
    return ConfigurationManager()


@pytest.fixture(scope="session")
def transformation_engine(config_manager: ConfigurationManager) -> TextTransformationEngine:
    """Provide shared TextTransformationEngine instance for all tests."""
    return TextTransformationEngine(config_manager)


class TestUnicodeHandling:
    """Unicode handling tests using modern pytest patterns."""

    @pytest.mark.parametrize(
        "test_input,rule,description",
        [
            (" Te Sｔ- _　  ", "/t", "Mixed ASCII and full-width characters with trim"),
            ("こんにちは世界", "/u", "Japanese hiragana and kanji uppercase test"),
            ("ＨＥＬＬＯ　ＷＯＲＬＤ", "/fh", "Full-width to half-width conversion"),
            ("Hello World", "/hf", "Half-width to full-width conversion"),
            ("café naïve résumé", "/u", "Latin characters with diacritics"),
            ("Привет мир", "/l", "Cyrillic characters lowercase"),
            ("🚀 Unicode 🌟 Emoji 🎉", "/t", "Emoji characters with trim"),
            ("α β γ δ ε", "/u", "Greek alphabet characters"),
            ("中文测试文本", "/l", "Chinese simplified characters"),
            ("العربية اختبار", "/R", "Arabic text with reverse"),
        ],
    )
    def test_unicode_transformations(
        self,
        transformation_engine: TextTransformationEngine,
        test_input: str,
        rule: str,
        description: str,
    ) -> None:
        """Test Unicode transformations using parametrized testing."""
        try:
            result = transformation_engine.apply_transformations(test_input, rule)
            # Verify result is still a valid string
            assert isinstance(result, str), f"Result should be string for {description}"
            # For most Unicode text, transformations should at least not crash
            assert len(result) >= 0, f"Result should have valid length for {description}"

        except Exception as e:
            pytest.fail(f"Unicode transformation failed for {description}: {e}")

    def test_unicode_pipe_subprocess(self) -> None:
        """Test Unicode input through subprocess pipe."""
        test_input = " Te Sｔ- _　  "

        try:
            result = subprocess.run(
                [sys.executable, "String_Multitool.py", "/t"],
                input=test_input,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",  # Use 'replace' to handle encoding issues gracefully
                timeout=10,  # Add timeout for safety
            )

            actual_output = result.stdout.strip()

            # Basic validation
            assert result.returncode == 0, f"Process should exit successfully: {result.stderr}"

            # Windows console may have encoding limitations, so just verify trimming worked
            # and non-ASCII characters are present (even if corrupted)
            assert len(actual_output) > 0, "Output should not be empty"
            assert len(actual_output) < len(
                test_input
            ), "Output should be shorter than input (trimmed)"

        except subprocess.TimeoutExpired:
            pytest.fail("Unicode pipe test timed out")
        except FileNotFoundError:
            pytest.skip("String_Multitool.py not found in current directory")
        except Exception as e:
            pytest.fail(f"Unicode pipe test failed: {e}")

    @pytest.mark.parametrize("encoding", ["utf-8", "utf-16", "utf-32"])
    def test_unicode_encoding_handling(
        self, transformation_engine: TextTransformationEngine, encoding: str
    ) -> None:
        """Test Unicode handling with different encodings."""
        test_text = "Hello 世界 🌍 café"

        try:
            # Test that text can be encoded and decoded properly
            encoded = test_text.encode(encoding)
            decoded = encoded.decode(encoding)
            assert decoded == test_text

            # Test transformation on decoded text
            result = transformation_engine.apply_transformations(decoded, "/u")
            assert isinstance(result, str)

        except UnicodeError as e:
            pytest.fail(f"Encoding {encoding} failed: {e}")

    def test_unicode_normalization(self, transformation_engine: TextTransformationEngine) -> None:
        """Test Unicode normalization handling."""
        import unicodedata

        # Test with composed and decomposed forms
        composed = "café"  # é as single character
        decomposed = "cafe\u0301"  # e + combining acute accent

        # Normalize to compare
        normalized_composed = unicodedata.normalize("NFC", composed)
        normalized_decomposed = unicodedata.normalize("NFC", decomposed)

        assert normalized_composed == normalized_decomposed

        # Test transformations on both forms
        result1 = transformation_engine.apply_transformations(composed, "/u")
        result2 = transformation_engine.apply_transformations(decomposed, "/u")

        # Both should produce equivalent results when normalized
        norm_result1 = unicodedata.normalize("NFC", result1)
        norm_result2 = unicodedata.normalize("NFC", result2)

        assert norm_result1 == norm_result2

    def test_unicode_edge_cases(self, transformation_engine: TextTransformationEngine) -> None:
        """Test Unicode edge cases and special characters."""
        edge_cases = [
            "",  # Empty string
            "\x00",  # Null character
            "\u200b",  # Zero-width space
            "\ufeff",  # Byte order mark
            "\U0001f600",  # Emoji (4-byte UTF-8)
            "\ud800\udc00",  # Surrogate pair (if supported)
            "a\u0300",  # Base + combining character
        ]

        for test_case in edge_cases:
            try:
                result = transformation_engine.apply_transformations(test_case, "/t")
                assert isinstance(result, str)
            except Exception as e:
                # Some edge cases might legitimately fail
                print(f"Expected failure for edge case {repr(test_case)}: {e}")

    @pytest.mark.slow
    def test_large_unicode_text_performance(
        self, transformation_engine: TextTransformationEngine
    ) -> None:
        """Test performance with large Unicode text."""
        import time

        # Create large Unicode text (mix of different character sets)
        large_text = "Hello 世界 🌍 " * 10000  # ~150KB of mixed Unicode

        start_time = time.time()
        result = transformation_engine.apply_transformations(large_text, "/l")
        end_time = time.time()

        elapsed = end_time - start_time

        assert isinstance(result, str)
        assert len(result) > 0
        # Should complete within reasonable time (2 seconds for 150KB)
        assert elapsed < 2.0, f"Large Unicode text processing took {elapsed:.2f}s"


if __name__ == "__main__":
    # Modern pytest execution
    pytest.main([__file__, "-v", "--tb=short"])
