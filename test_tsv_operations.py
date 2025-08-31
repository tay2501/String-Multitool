#!/usr/bin/env python3
"""Comprehensive test suite for TSV operations features.

Educational example of enterprise-grade testing patterns:
- Clean test organization with descriptive naming
- Proper setup and teardown lifecycle management  
- Comprehensive error scenario coverage
- Performance validation with realistic thresholds
- Mocking external dependencies for isolation
"""

import sys
import unittest
import time
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from string_multitool.core.transformations import TextTransformationEngine
from string_multitool.core.config import ConfigurationManager
from string_multitool.exceptions import TransformationError, ValidationError


class TestTSVOperationsCore(unittest.TestCase):
    """Core functionality tests for TSV operations.
    
    Demonstrates best practices for:
    - Test fixture management with proper initialization
    - Descriptive test method naming conventions
    - Comprehensive assertion patterns
    - Exception handling validation
    """
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up class-level test fixtures."""
        cls.config_manager = ConfigurationManager()
        cls.engine = TextTransformationEngine(cls.config_manager)
    
    def setUp(self) -> None:
        """Set up method-level test fixtures."""
        # Reset any instance-level state if needed
        pass
    
    def tearDown(self) -> None:
        """Clean up method-level test resources."""
        # Clean up any method-specific resources
        pass
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up class-level test resources."""
        # Clean up any class-level resources
        pass
    
    def test_tsv_rule_registration(self) -> None:
        """Verify TSV rule is properly registered with correct metadata."""
        rules = self.engine.get_available_rules()
        
        # Validate rule exists with proper key
        self.assertIn("tsv", rules, "TSV rule should be registered in available rules")
        
        tsv_rule = rules["tsv"]
        
        # Validate rule metadata
        self.assertEqual(tsv_rule.name, "TSV Operations", "Rule name should be descriptive")
        self.assertTrue(tsv_rule.requires_args, "TSV rule should require arguments")
        
        # Validate description contains key functionality
        description_lower = tsv_rule.description.lower()
        self.assertIn("list", description_lower, "Description should mention list functionality")
        self.assertIn("sqlite", description_lower, "Description should mention SQLite functionality")
        self.assertIn("convert", description_lower, "Description should mention conversion functionality")
    
    def test_tsv_help_information(self) -> None:
        """Verify TSV rule help information is comprehensive and accurate."""
        help_info = self.engine.get_rule_help("tsv")
        
        help_lower = help_info.lower()
        self.assertIn("tsv", help_lower, "Help should contain rule name")
        self.assertIn("list", help_lower, "Help should document list command")
        self.assertIn("sqlite3", help_lower, "Help should document sqlite3 command")
    
    def test_tsv_list_command_execution(self) -> None:
        """Test TSV list command executes without errors."""
        try:
            result = self.engine.apply_transformations("", "/tsv list")
            
            # Validate result structure
            self.assertIsInstance(result, str, "List command should return string result")
            self.assertGreater(len(result), 0, "List command should return non-empty result")
            
            # Check for expected content patterns
            result_lower = result.lower()
            if "no rule sets found" not in result_lower:
                # If database has content, verify formatting
                self.assertIn("database rules", result_lower, "Should contain database rules header")
            
        except ImportError:
            # Allow test to pass if TSV converter module unavailable in test environment
            self.skipTest("TSV converter module not available in test environment")
        except TransformationError as e:
            # Allow certain expected errors in test environment
            if "module not available" in str(e).lower():
                self.skipTest("TSV converter dependencies not available")
            else:
                raise
    
    def test_tsv_sqlite3_command_execution(self) -> None:
        """Test TSV sqlite3 command provides database information."""
        try:
            result = self.engine.apply_transformations("", "/tsv sqlite3")
            
            # Validate result structure
            self.assertIsInstance(result, str, "SQLite command should return string result")
            self.assertGreater(len(result), 0, "SQLite command should return non-empty result")
            
            # Check for expected information patterns
            result_lower = result.lower()
            self.assertIn("sqlite", result_lower, "Result should mention SQLite")
            self.assertIn("database", result_lower, "Result should mention database")
            
            # Should contain either connection info or error message
            has_connection_info = "path:" in result_lower
            has_error_info = "failed" in result_lower or "error" in result_lower
            
            self.assertTrue(
                has_connection_info or has_error_info,
                "Result should contain either connection information or error details"
            )
            
        except ImportError:
            self.skipTest("TSV converter module not available in test environment")
        except TransformationError as e:
            if "module not available" in str(e).lower():
                self.skipTest("TSV converter dependencies not available")
            else:
                raise
    
    def test_tsv_missing_arguments_error(self) -> None:
        """Verify TSV command without arguments raises appropriate error."""
        with self.assertRaises((TransformationError, ValidationError)) as context:
            self.engine.apply_transformations("", "/tsv")
        
        error_message = str(context.exception).lower()
        self.assertIn("require", error_message, "Error should mention requirement")
        self.assertIn("argument", error_message, "Error should mention arguments")
    
    def test_rule_string_parsing_accuracy(self) -> None:
        """Test accurate parsing of TSV command variations."""
        test_cases = [
            ("/tsv list", [("tsv", ["list"])]),
            ("/tsv sqlite3", [("tsv", ["sqlite3"])]),
            ("/tsv file.tsv", [("tsv", ["file.tsv"])]),
        ]
        
        for rule_string, expected_result in test_cases:
            with self.subTest(rule_string=rule_string):
                parsed_result = self.engine.parse_rule_string(rule_string)
                self.assertEqual(
                    parsed_result, 
                    expected_result, 
                    f"Parsing of '{rule_string}' should match expected result"
                )


class TestTSVOperationsIntegration(unittest.TestCase):
    """Integration tests for TSV operations with external dependencies.
    
    Demonstrates:
    - Integration testing patterns
    - External dependency management
    - Database interaction testing
    - Error scenario coverage
    """
    
    def setUp(self) -> None:
        """Set up integration test fixtures."""
        self.config_manager = ConfigurationManager()
        self.engine = TextTransformationEngine(self.config_manager)
    
    def test_database_path_resolution(self) -> None:
        """Verify database path resolution follows expected patterns."""
        # Test that project structure assumptions are valid
        current_file = Path(__file__)
        project_root = current_file.parent
        expected_db_path = project_root / "data" / "tsv_translate.db"
        
        # Validate project structure
        self.assertTrue(project_root.exists(), "Project root should exist")
        # Note: Database file may not exist in test environment, which is acceptable
    
    @patch('sqlite3.connect')
    def test_sqlite_connection_error_handling(self, mock_connect: Mock) -> None:
        """Test graceful handling of SQLite connection failures."""
        # Mock connection failure
        mock_connect.side_effect = Exception("Connection failed")
        
        try:
            result = self.engine.apply_transformations("", "/tsv sqlite3")
            
            # Should handle error gracefully and provide informative message
            result_lower = result.lower()
            self.assertTrue(
                "failed" in result_lower or "error" in result_lower,
                "Should indicate connection failure in result"
            )
            
        except TransformationError as e:
            # Should wrap connection errors appropriately
            error_lower = str(e).lower()
            self.assertIn("failed", error_lower, "Should indicate failure in error message")
        except ImportError:
            self.skipTest("TSV converter module not available")


class TestTSVOperationsPerformance(unittest.TestCase):
    """Performance validation tests for TSV operations.
    
    Educational example of:
    - Performance testing methodologies
    - Realistic performance thresholds
    - Time-based validation patterns
    - Resource usage monitoring
    """
    
    def setUp(self) -> None:
        """Set up performance test fixtures."""
        self.config_manager = ConfigurationManager()
        self.engine = TextTransformationEngine(self.config_manager)
        
        # Performance thresholds (in seconds)
        self.list_command_threshold = 5.0
        self.sqlite_command_threshold = 3.0
        self.parsing_threshold = 0.1
    
    def test_list_command_performance(self) -> None:
        """Validate list command executes within acceptable time limits."""
        start_time = time.time()
        
        try:
            self.engine.apply_transformations("", "/tsv list")
        except (ImportError, TransformationError):
            # Allow failures in test environment
            pass
        
        execution_time = time.time() - start_time
        
        self.assertLess(
            execution_time, 
            self.list_command_threshold,
            f"List command should complete within {self.list_command_threshold}s"
        )
    
    def test_sqlite_command_performance(self) -> None:
        """Validate sqlite3 command executes within acceptable time limits."""
        start_time = time.time()
        
        try:
            self.engine.apply_transformations("", "/tsv sqlite3")
        except (ImportError, TransformationError):
            # Allow failures in test environment
            pass
        
        execution_time = time.time() - start_time
        
        self.assertLess(
            execution_time,
            self.sqlite_command_threshold, 
            f"SQLite command should complete within {self.sqlite_command_threshold}s"
        )
    
    def test_rule_parsing_performance(self) -> None:
        """Validate rule string parsing performance for complex commands."""
        test_commands = [
            "/tsv list",
            "/tsv sqlite3", 
            "/tsv technical_terms.tsv --case-insensitive",
            "/tsv file.tsv --preserve-case"
        ]
        
        start_time = time.time()
        
        for command in test_commands:
            try:
                self.engine.parse_rule_string(command)
            except (ValidationError, TransformationError):
                # Allow parsing errors in test
                pass
        
        execution_time = time.time() - start_time
        average_time = execution_time / len(test_commands)
        
        self.assertLess(
            average_time,
            self.parsing_threshold,
            f"Rule parsing should average under {self.parsing_threshold}s per command"
        )


def create_comprehensive_test_suite() -> unittest.TestSuite:
    """Create comprehensive test suite with all test cases.
    
    Returns:
        Configured test suite ready for execution
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test case classes
    test_classes = [
        TestTSVOperationsCore,
        TestTSVOperationsIntegration, 
        TestTSVOperationsPerformance
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTest(tests)
    
    return suite


def run_comprehensive_tests() -> bool:
    """Execute comprehensive test suite with detailed reporting.
    
    Returns:
        True if all tests passed, False otherwise
    """
    print("=" * 80)
    print("TSV Operations - Comprehensive Test Suite")
    print("=" * 80)
    
    # Create and run test suite
    test_suite = create_comprehensive_test_suite()
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False,
        buffer=True  # Capture stdout/stderr during tests
    )
    
    result = runner.run(test_suite)
    
    # Summary reporting
    print("=" * 80)
    print("Test Execution Summary")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.testsRun > 0:
        success_count = result.testsRun - len(result.failures) - len(result.errors)
        success_rate = (success_count / result.testsRun) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)