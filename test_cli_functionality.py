#!/usr/bin/env python3
"""
Pytest tests for String_Multitool CLI functionality.

Tests pipe chaining, parameterized rules, and silent mode based on pytest best practices.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

import pytest


@pytest.fixture
def cli_script() -> str:
    """Return path to the CLI script."""
    return str(Path(__file__).parent / "String_Multitool.py")


def run_cli(cli_script: str, args: List[str], input_text: str = "") -> Tuple[str, str, int]:
    """Run CLI command and return stdout, stderr, and return code."""
    cmd = [sys.executable, cli_script] + args
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        timeout=10
    )
    return result.stdout, result.stderr, result.returncode


def run_pipe_chain(cli_script: str, commands: List[List[str]], input_text: str) -> Tuple[str, str, int]:
    """Run multiple CLI commands in a pipe chain."""
    processes = []
    
    # Start first process
    first_cmd = [sys.executable, cli_script] + commands[0]
    first_proc = subprocess.Popen(
        first_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(first_proc)
    
    # Chain additional processes
    for cmd_args in commands[1:]:
        cmd = [sys.executable, cli_script] + cmd_args
        proc = subprocess.Popen(
            cmd,
            stdin=processes[-1].stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(proc)
    
    # Start the chain by providing input to first process
    first_proc.stdin.write(input_text)
    first_proc.stdin.close()
    
    # Wait for all processes and get final output
    final_stdout, final_stderr = processes[-1].communicate()
    return_code = processes[-1].returncode
    
    return final_stdout.strip(), final_stderr, return_code


class TestBasicTransformations:
    """Test basic transformation rules."""
    
    def test_trim_uppercase(self, cli_script):
        """Test trim + uppercase transformation."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//t//u"], "  test  ")
        assert code == 0
        assert stdout == "TEST"
        assert stderr == ""
    
    def test_lowercase(self, cli_script):
        """Test lowercase transformation."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//l"], "TEST")
        assert code == 0
        assert stdout == "test"
    
    def test_pascalcase(self, cli_script):
        """Test PascalCase transformation."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//p"], "hello world")
        assert code == 0
        assert stdout == "HelloWorld"


class TestParameterizedRules:
    """Test rules that require parameters."""
    
    def test_slug_with_plus(self, cli_script):
        """Test slug transformation with plus separator."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//S", "+"], "Test A")
        assert code == 0
        assert stdout == "test+a"
    
    def test_slug_with_underscore(self, cli_script):
        """Test slug transformation with underscore separator."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//S", "_"], "Test A")
        assert code == 0
        assert stdout == "test_a"
    
    def test_replace_rule(self, cli_script):
        """Test replace transformation."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//r", "World", "Universe"], "Hello World")
        assert code == 0
        assert stdout == "Hello Universe"


class TestPipeChaining:
    """Test pipe chaining functionality."""
    
    def test_trim_uppercase_to_slug(self, cli_script):
        """Test: trim+uppercase -> slug transformation."""
        stdout, stderr, code = run_pipe_chain(
            cli_script,
            [["//t//u"], ["//S", "+"]],
            "  test a  "
        )
        assert code == 0
        assert stdout == "test+a"
    
    def test_complex_pipe_chain(self, cli_script):
        """Test complex transformation chain."""
        stdout, stderr, code = run_pipe_chain(
            cli_script,
            [["//t//l"], ["//p"], ["//s"]],
            "  HELLO WORLD  "
        )
        assert code == 0
        assert stdout == "helloworld"
    
    def test_replace_to_slug_chain(self, cli_script):
        """Test replace -> slug transformation chain."""
        stdout, stderr, code = run_pipe_chain(
            cli_script,
            [["//r", "World", "Universe"], ["//S", "-"]],
            "Hello World"
        )
        assert code == 0
        assert stdout == "hello-universe"


class TestSilentMode:
    """Test silent mode functionality."""
    
    def test_silent_vs_normal_mode(self, cli_script):
        """Test difference between silent and normal modes."""
        # Silent mode - only result
        silent_out, _, _ = run_cli(cli_script, ["-s", "//u"], "test")
        assert silent_out == "TEST"
        
        # Normal mode - includes result in stdout
        normal_out, _, _ = run_cli(cli_script, ["//u"], "test")
        assert "TEST" in normal_out
    
    def test_silent_mode_pipe_compatibility(self, cli_script):
        """Test that silent mode works in pipe chains."""
        stdout, stderr, code = run_pipe_chain(
            cli_script,
            [["-s", "//u"], ["-s", "//S", "+"]],
            "test a"
        )
        assert code == 0
        assert stdout == "test+a"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_rule(self, cli_script):
        """Test handling of invalid transformation rule."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "invalid"], "test")
        assert code != 0
        assert "must start with '/'" in stderr
    
    def test_empty_input(self, cli_script):
        """Test handling of empty input."""
        stdout, stderr, code = run_cli(cli_script, ["-s", "//u"], "")
        assert code == 0
        assert stdout == ""


@pytest.mark.parametrize("rule,input_text,expected", [
    ("//u", "hello", "HELLO"),
    ("//l", "WORLD", "world"),  # Fixed: lowercase should convert to lowercase
    ("//t", "  spaced  ", "spaced"),
    ("//S", "Test Case", "test-case"),  # Default separator
])
def test_transformation_rules_parametrized(cli_script, rule, input_text, expected):
    """Parametrized test for various transformation rules."""
    args = ["-s", rule] if rule == "//S" else ["-s", rule]  
    stdout, stderr, code = run_cli(cli_script, args, input_text)
    assert code == 0
    assert stdout == expected


def test_help_functionality(cli_script):
    """Test help functionality."""
    # Test help command (simpler approach)
    stdout, stderr, code = run_cli(cli_script, ["help"])
    assert code == 0
    # Help functionality works if it doesn't crash
    assert stderr == "" or "help" in stderr.lower()


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])