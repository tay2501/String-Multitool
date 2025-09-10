#!/usr/bin/env python3
"""Entry point script for TSV converter CLI.

Educational example of a clean entry point script that
delegates to the main CLI implementation.
"""

import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tsv_translate.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
