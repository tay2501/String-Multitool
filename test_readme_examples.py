#!/usr/bin/env python3
"""
Test README.md command examples.

This test suite validates that all command examples shown in README.md
work correctly and produce the expected results.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from string_multitool.core.config import ConfigurationManager
from string_multitool.core.transformations import TextTransformationEngine


def test_readme_examples():
    """Test command examples from README.md."""
    try:
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)

        # Test cases from README
        test_cases = [
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
        ]

        passed = 0
        failed = 0

        for i, (input_text, rule, expected, description) in enumerate(test_cases, 1):
            try:
                result = transformation_engine.apply_transformations(input_text, rule)
                if result == expected:
                    print(f"PASS Test {i}: {description}")
                    print(f'  Input:    "{input_text}"')
                    print(f"  Rule:     {rule}")
                    print(f'  Result:   "{result}"')
                    passed += 1
                else:
                    print(f"FAIL Test {i}: {description}")
                    print(f'  Input:    "{input_text}"')
                    print(f"  Rule:     {rule}")
                    print(f'  Expected: "{expected}"')
                    print(f'  Actual:   "{result}"')
                    failed += 1
                print()

            except Exception as e:
                print(f"ERROR Test {i}: {description}")
                print(f'  Input:    "{input_text}"')
                print(f"  Rule:     {rule}")
                print(f"  Error:    {e}")
                failed += 1
                print()

        print(f"Results: {passed} passed, {failed} failed")
        return failed == 0

    except Exception as e:
        print(f"Setup error: {e}")
        return False


if __name__ == "__main__":
    success = test_readme_examples()
    sys.exit(0 if success else 1)
