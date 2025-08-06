# Contributing to Clipboard Transformer

Thank you for your interest in contributing to Clipboard Transformer! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Windows 10/11 (for testing)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/clipboard-transformer.git
   cd clipboard-transformer
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run tests to ensure everything works:
   ```bash
   pytest
   ```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards
3. Add or update tests as needed
4. Run the test suite:
   ```bash
   pytest
   pytest --cov=src  # With coverage
   ```

5. Update documentation if needed
6. Commit your changes with clear messages

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for custom hotkey modifiers

- Allow combinations like ctrl+shift+alt+key
- Update configuration validation
- Add tests for new hotkey formats
```

## Code Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Include docstrings for all public functions and classes
- Maximum line length: 100 characters

### Code Quality

- Write unit tests for new functionality
- Maintain test coverage above 90%
- Use meaningful variable and function names
- Add comments for complex logic

### Example Code Style

```python
def transform_text(text: str, pattern: str, replacement: str) -> str:
    """
    Transform text using regex pattern and replacement.
    
    Args:
        text: Input text to transform
        pattern: Regex pattern to match
        replacement: Replacement string
        
    Returns:
        Transformed text
        
    Raises:
        ValueError: If pattern is invalid
    """
    try:
        import re
        return re.sub(pattern, replacement, text)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_transformer.py

# Run with coverage report
pytest --cov=src --cov-report=html

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies

Example test:

```python
def test_hyphen_to_underscore_transformation():
    """Test basic hyphen to underscore transformation."""
    transformer = TransformationEngine("test_config.json")
    result = transformer.apply_transformation("test-string", "hyphen_to_underscore")
    assert result == "test_string"

def test_transformation_with_invalid_pattern():
    """Test transformation with invalid regex pattern."""
    transformer = TransformationEngine("test_config.json")
    with pytest.raises(ValueError):
        transformer.apply_transformation("test", "invalid_pattern")
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type information and examples where helpful

### User Documentation

- Update README.md for user-facing changes
- Add configuration examples for new features
- Update troubleshooting section for known issues

## Submitting Changes

### Pull Request Process

1. Ensure all tests pass
2. Update documentation as needed
3. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## Issue Reporting

### Bug Reports

Include:
- Operating system and version
- Python version (if applicable)
- Steps to reproduce
- Expected vs actual behavior
- Log files if available
- Configuration file (remove sensitive data)

### Feature Requests

Include:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Examples of similar features

## Release Process

### Version Numbers

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test executable
5. Create GitHub release
6. Update documentation

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain professional communication

### Getting Help

- Check existing issues and documentation first
- Ask questions in GitHub discussions
- Provide context and details when asking for help
- Be patient and respectful

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor statistics

Thank you for contributing to Clipboard Transformer!