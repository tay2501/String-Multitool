#!/usr/bin/env python3
"""
Modern pytest-based test suite for README.md command examples.

This comprehensive test suite validates that all command examples shown in README.md
work correctly using modern pytest patterns including parametrization and fixtures.

Demonstrates:
- README.md example validation
- Documentation-driven testing
- Modern pytest parametrization
- Comprehensive example coverage
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add project root to path
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


class TestReadmeExamples:
    """Test README.md command examples using modern pytest patterns."""

    @pytest.mark.parametrize(
        "input_text,rule,expected,description",
        [
            # Basic transformations
            ("  HELLO WORLD  ", "/t/l", "hello world", "Trim + lowercase"),
            (
                "The Quick Brown Fox",
                "/s/u",
                "THE_QUICK_BROWN_FOX",
                "snake_case + uppercase",
            ),
            ("  hello world test  ", "/t/S", "hello-world-test", "Trim + slugify"),
            # Advanced transformations
            (
                "http://foo.bar/baz",
                "/S '+'",
                "http+foo+bar+baz",
                "Slugify with custom replacement",
            ),
            (
                "I'm Will, Will's son",
                "/r 'Will' 'Bill'",
                "I'm Bill, Bill's son",
                "Replace text",
            ),
            ("remove this text", "/r 'this'", "remove  text", "Remove substring"),
        ],
    )
    def test_readme_command_examples(
        self,
        transformation_engine: TextTransformationEngine,
        input_text: str,
        rule: str,
        expected: str,
        description: str,
    ) -> None:
        """Test individual README command examples using parametrized testing."""
        result = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, (
            f"{description} failed: expected '{expected}', got '{result}' "
            f"for input '{input_text}' with rule '{rule}'"
        )

    @pytest.mark.parametrize(
        "category,examples",
        [
            (
                "Basic Case Transformations",
                [
                    ("Hello World", "/l", "hello world", "Lowercase transformation"),
                    ("hello world", "/u", "HELLO WORLD", "Uppercase transformation"),
                    ("hello world", "/c", "helloWorld", "camelCase transformation"),
                    ("hello world", "/p", "HelloWorld", "PascalCase transformation"),
                    ("hello world", "/s", "hello_world", "snake_case transformation"),
                    ("hello world", "/a", "Hello World", "Title Case transformation"),
                ],
            ),
            (
                "String Operations",
                [
                    ("  padded text  ", "/t", "padded text", "Trim whitespace"),
                    ("reverse me", "/R", "em esrever", "Reverse string"),
                    (
                        "line1\nline2\nline3",
                        "/si",
                        "'line1',\r\n'line2',\r\n'line3'",
                        "Single quotes insertion",
                    ),
                    ("line1\r\nline2\r\nline3", "/dlb", "line1line2line3", "Delete line breaks"),
                ],
            ),
            (
                "Character Width Conversions",
                [
                    ("ＴＢＬ－ＣＨＡ１", "/fh", "TBL-CHA1", "Full-width to half-width"),
                    ("TBL-CHA1", "/hf", "ＴＢＬ－ＣＨＡ１", "Half-width to full-width"),
                    ("TBL_CHA1", "/uh", "TBL-CHA1", "Underscore to hyphen"),
                    ("TBL-CHA1", "/hu", "TBL_CHA1", "Hyphen to underscore"),
                ],
            ),
        ],
    )
    def test_readme_examples_by_category(
        self,
        transformation_engine: TextTransformationEngine,
        category: str,
        examples: list[tuple[str, str, str, str]],
    ) -> None:
        """Test README examples organized by functionality category."""
        for input_text, rule, expected, description in examples:
            result = transformation_engine.apply_transformations(input_text, rule)
            assert result == expected, (
                f"{category} - {description} failed: "
                f"expected '{expected}', got '{result}' "
                f"for input '{input_text}' with rule '{rule}'"
            )

    def test_complex_rule_chains(self, transformation_engine: TextTransformationEngine) -> None:
        """Test complex rule chains from README examples."""
        complex_examples = [
            ("  Mixed Case Example  ", "/t/l/s/u", "MIXED_CASE_EXAMPLE", "Trim→Lower→Snake→Upper"),
            ("CamelCaseString", "/s/l/a", "Camel_Case_String", "Snake→Lower→Title"),
            ("  UPPER TEXT  ", "/t/l/p", "UpperText", "Trim→Lower→Pascal"),
            ("kebab-case-text", "/hu/c", "kebabCaseText", "Hyphen→Underscore→camelCase"),
        ]

        for input_text, rule, expected, description in complex_examples:
            result = transformation_engine.apply_transformations(input_text, rule)
            assert result == expected, (
                f"Complex chain {description} failed: "
                f"expected '{expected}', got '{result}' "
                f"for input '{input_text}' with rule '{rule}'"
            )

    def test_argument_based_examples(
        self, transformation_engine: TextTransformationEngine
    ) -> None:
        """Test README examples with arguments."""
        argument_examples = [
            ("hello world test", "/S", "hello-world-test", "Default slugify"),
            ("hello world test", "/S '_'", "hello_world_test", "Slugify with underscore"),
            ("hello world test", "/S '+'", "hello+world+test", "Slugify with plus"),
            ("find and replace", "/r 'and' '&'", "find & replace", "Simple replacement"),
            ("remove this word", "/r 'this '", "remove word", "Remove with space"),
        ]

        for input_text, rule, expected, description in argument_examples:
            result = transformation_engine.apply_transformations(input_text, rule)
            assert result == expected, (
                f"Argument example {description} failed: "
                f"expected '{expected}', got '{result}' "
                f"for input '{input_text}' with rule '{rule}'"
            )

    def test_edge_case_examples(self, transformation_engine: TextTransformationEngine) -> None:
        """Test edge cases that might appear in README."""
        edge_cases = [
            ("", "/l", "", "Empty string"),
            (" ", "/t", "", "Whitespace only"),
            ("a", "/u", "A", "Single character"),
            ("123", "/l", "123", "Numbers only"),
            ("!@#$%", "/u", "!@#$%", "Special characters only"),
        ]

        for input_text, rule, expected, description in edge_cases:
            result = transformation_engine.apply_transformations(input_text, rule)
            assert result == expected, (
                f"Edge case {description} failed: "
                f"expected '{expected}', got '{result}' "
                f"for input '{input_text}' with rule '{rule}'"
            )


if __name__ == "__main__":
    # Modern pytest execution
    pytest.main([__file__, "-v", "--tb=short"])
