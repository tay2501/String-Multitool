"""
Modern pytest-based code quality test suite that mirrors GitHub Actions CI/CD pipeline.

This comprehensive module integrates all code quality checks (type checking, formatting, 
import sorting, and YAML validation) into pytest using modern patterns including:
- Session-scoped fixtures for performance
- Parametrized testing for workflow validation
- Modern type annotations with generic types
- Comprehensive error reporting and actionable feedback

Makes all quality checks executable via `pytest test_code_quality.py`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Generator

import pytest
import yaml


class TestCodeQuality:
    """Test class for comprehensive code quality validation."""

    @pytest.fixture(scope="session")
    def source_files(self) -> Generator[list[Path], None, None]:
        """Fixture providing all Python source files in the project."""
        source_dir = Path("string_multitool")
        if source_dir.exists():
            files = list(source_dir.rglob("*.py"))
            yield files
        else:
            yield []

    @pytest.fixture(scope="session")  
    def workflow_files(self) -> Generator[list[Path], None, None]:
        """Fixture providing all GitHub Actions workflow files."""
        workflow_dir = Path(".github/workflows")
        if workflow_dir.exists():
            files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
            yield files
        else:
            yield []

    @pytest.mark.quality
    def test_mypy_type_checking(self, source_files: list[Path]) -> None:
        """Test that all source files pass mypy type checking."""
        if not source_files:
            pytest.skip("No source files found")
        
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "string_multitool/"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode != 0:
            pytest.fail(
                f"mypy type checking failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    @pytest.mark.quality
    def test_black_code_formatting(self, source_files: list[Path]) -> None:
        """Test that all source files conform to black formatting."""
        if not source_files:
            pytest.skip("No source files found")
            
        result = subprocess.run(
            [sys.executable, "-m", "black", "--check", "string_multitool/"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode != 0:
            pytest.fail(
                f"black formatting check failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}\n"
                f"Run 'black string_multitool/' to fix formatting issues"
            )

    @pytest.mark.quality
    def test_isort_import_sorting(self, source_files: list[Path]) -> None:
        """Test that all source files have correctly sorted imports."""
        if not source_files:
            pytest.skip("No source files found")
            
        result = subprocess.run(
            [sys.executable, "-m", "isort", "--check-only", "string_multitool/"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode != 0:
            pytest.fail(
                f"isort import sorting check failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}\n"
                f"Run 'isort string_multitool/' to fix import sorting issues"
            )

    @pytest.mark.parametrize("workflow_file", [
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml", 
        ".github/workflows/release.yml",
        ".github/workflows/security.yml",
        ".github/workflows/dependency-review.yml",
        ".github/workflows/dependabot-auto-merge.yml"
    ])
    @pytest.mark.yaml
    def test_yaml_workflow_syntax(self, workflow_file: str) -> None:
        """Test that GitHub Actions workflow files have valid YAML syntax."""
        workflow_path = Path(workflow_file)
        
        if not workflow_path.exists():
            pytest.skip(f"Workflow file {workflow_file} not found")
            
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"YAML syntax error in {workflow_file}: {e}")
        except Exception as e:
            pytest.fail(f"Error reading {workflow_file}: {e}")

    def test_pyproject_toml_syntax(self) -> None:
        """Test that pyproject.toml has valid syntax and required sections."""
        pyproject_path = Path("pyproject.toml")
        
        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")
            
        try:
            import tomllib
        except ImportError:
            # Fallback for Python < 3.11
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("tomllib/tomli not available for TOML parsing")
        
        try:
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
                
            # Verify essential sections exist
            required_sections = ['build-system', 'project', 'tool.pytest.ini_options']
            for section in required_sections:
                keys = section.split('.')
                current = config
                for key in keys:
                    if key not in current:
                        pytest.fail(f"Required section [{section}] missing from pyproject.toml")
                    current = current[key]
                    
        except Exception as e:
            pytest.fail(f"Error parsing pyproject.toml: {e}")

    def test_test_file_discovery(self) -> None:
        """Test that pytest can discover all test files properly."""
        test_files = [
            "test_transform.py",
            "test_tsv_case_insensitive.py", 
            "test_system_integration.py",
            "test_tsv_operations.py",
            "test_readme_examples.py",
            "test_unicode.py",
            "test_code_quality.py",  # This file
            "test_signal_handler.py",
            "test_modern_comprehensive.py"
        ]
        
        missing_files = []
        tests_dir = Path(__file__).parent
        for test_file in test_files:
            if not (tests_dir / test_file).exists():
                missing_files.append(test_file)
        
        if missing_files:
            pytest.fail(f"Test files missing: {missing_files}")

    @pytest.mark.slow
    def test_comprehensive_test_execution(self) -> None:
        """Test that the main test suite executes successfully."""
        # Run core transformation tests with correct path
        tests_dir = Path(__file__).parent
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest", 
                str(tests_dir / "test_transform.py"), 
                str(tests_dir / "test_tsv_case_insensitive.py"),
                "-v", "--tb=short"
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode != 0:
            pytest.fail(
                f"Core test suite execution failed:\n"
                f"STDOUT: {result.stdout}\n"  
                f"STDERR: {result.stderr}"
            )

    def test_coverage_configuration(self) -> None:
        """Test that coverage configuration is properly set up."""
        pyproject_path = Path("pyproject.toml")
        
        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")
            
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for coverage configuration sections
        required_coverage_sections = [
            '[tool.coverage.run]',
            '[tool.coverage.report]'
        ]
        
        for section in required_coverage_sections:
            if section not in content:
                pytest.fail(f"Coverage configuration section {section} missing from pyproject.toml")

    @pytest.mark.integration
    @pytest.mark.cicd
    def test_github_actions_workflow_integrity(self, workflow_files: list[Path]) -> None:
        """Test that GitHub Actions workflows reference existing files and commands."""
        if not workflow_files:
            pytest.skip("No workflow files found")
            
        critical_commands = [
            "uv sync --all-extras --dev --locked",
            "uv run pytest"
        ]
        
        for workflow_file in workflow_files:
            if "ci.yml" in workflow_file.name:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                missing_commands = []
                for cmd in critical_commands:
                    if cmd not in content:
                        missing_commands.append(cmd)
                        
                if missing_commands:
                    pytest.fail(
                        f"Critical commands missing from {workflow_file.name}: {missing_commands}"
                    )