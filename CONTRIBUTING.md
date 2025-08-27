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

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Code Style

We use automated tools to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting  
- **mypy**: Type checking

Before submitting a PR, run:
```bash
python -m black string_multitool/
python -m isort string_multitool/
python -m mypy string_multitool/
```

## Testing

Run the test suite:
```bash
python -m pytest test_transform.py test_tsv_case_insensitive.py -v
```

For coverage reports:
```bash
python -m pytest --cov=string_multitool
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