# Contributing to String Multitool

Thank you for your interest in contributing to String Multitool! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/[your-username]/String-Multitool.git
cd String-Multitool

# Install dependencies using uv (recommended)
uv sync --all-extras --dev

# Or using traditional pip
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -e .
```

## Code Style

We use automated tools to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting  
- **mypy**: Type checking

Before submitting a PR, run:
```bash
# Using uv (recommended)
uv run black string_multitool/
uv run isort string_multitool/
uv run mypy string_multitool/

# Or traditional method
python -m black string_multitool/
python -m isort string_multitool/
python -m mypy string_multitool/
```

## Testing

Run the test suite:
```bash
# Using uv (recommended)
uv run pytest test_transform.py test_tsv_case_insensitive.py -v

# For coverage reports
uv run pytest --cov=string_multitool

# Or traditional method
python -m pytest test_transform.py test_tsv_case_insensitive.py -v
python -m pytest --cov=string_multitool
```

## Architecture Overview

String_Multitool follows **Python MVC best practices**:

```
string_multitool/
├── models/          # Business Logic Layer (The "Model")
│   ├── config.py    # Configuration management
│   ├── crypto.py    # Cryptography operations
│   ├── transformations.py  # String transformation engine
│   ├── interactive.py      # Interactive session management
│   └── types.py     # Type definitions and protocols
├── io/             # View/Controller Layer (User Interface)
│   ├── manager.py  # Clipboard operations and I/O handling
│   └── clipboard.py # Clipboard monitoring
├── main.py         # Entry Point (Application flow control)
└── __init__.py     # Package initialization
```

### Development Guidelines
- Place business logic in `models/` directory
- UI operations belong in `io/` directory  
- Use `from .models.` for importing business components
- Follow MVC separation principles

## TSV Database Development

The project includes a SQLite-backed TSV conversion system:

```bash
# Test TSV functionality
python String_Multitool.py /tsvtr technical_terms.tsv

# Access database directly for debugging
python -m tsv_translate.cli.main --shell litecli
python -m tsv_translate.cli.main --shell sqlite3

# Manage TSV rule sets
python -m tsv_translate.cli.main ls                    # List rule sets
python -m tsv_translate.cli.main sync config/tsv_rules # Sync TSV files
python -m tsv_translate.cli.main info japanese_terms   # Show rule set info
```

### Database Schema
```sql
-- Main conversion rules table
CREATE TABLE conversion_rules (
    id INTEGER PRIMARY KEY,
    source_text TEXT,
    target_text TEXT, 
    rule_set_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Run code quality checks
7. Commit with descriptive messages
8. Push to your fork
9. Submit a pull request

## Pull Request Guidelines

- Fill out the PR template completely
- Include tests for new features
- Update documentation if needed
- Ensure all checks pass
- Keep PRs focused and atomic

## Issue Reporting

Use the appropriate issue template:
- Bug reports: Include version, OS, and reproduction steps
- Feature requests: Describe the use case and proposed solution

## Building Executables

To build platform-specific executables:

Windows:
```bash
./build.ps1
```

Other platforms:
```bash
python -m PyInstaller --onefile String_Multitool.py
```

## Questions?

Feel free to open an issue for questions or join discussions.