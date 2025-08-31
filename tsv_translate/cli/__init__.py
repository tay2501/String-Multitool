"""Command-line interface for TSV converter.

Clean CLI implementation with argparse and tab completion support.
"""

from .main import main, create_parser
from .completion import setup_completion

__all__ = ["main", "create_parser", "setup_completion"]