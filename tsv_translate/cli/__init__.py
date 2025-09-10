"""Command-line interface for TSV converter.

Clean CLI implementation with argparse and tab completion support.
"""

from .completion import setup_completion
from .main import create_parser, main

__all__ = ["main", "create_parser", "setup_completion"]
