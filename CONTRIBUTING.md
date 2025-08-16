# Contributing to String_Multitool

Thank you for your interest in contributing to String_Multitool! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Windows 10/11 (for testing)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/String-Multitool.git
   cd String-Multitool
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Run tests to ensure everything works:
   ```bash
   python -m pytest test_transform.py -v
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
   python -m pytest test_transform.py -v
   python -m pytest test_transform.py --cov=string_multitool
   ```

5. Update documentation if needed
6. Commit your changes with clear messages

### Commit Messages

Use clear, descriptive commit messages:

```
Add new text transformation rule

- Implement transformation logic in TextTransformationEngine
- Update config/transformation_rules.json
- Add comprehensive test cases
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
def apply_transformation(self, text: str, rule_string: str) -> str:
    """
    Apply transformation rules to input text.
    
    Args:
        text: Input text to transform
        rule_string: Rule string (e.g., '/t/l/u')
        
    Returns:
        Transformed text
        
    Raises:
        StringMultitoolError: If rule is invalid
    """
    try:
        rules = self.parse_rule_string(rule_string)
        result = text
        for rule in rules:
            result = rule.function(result)
        return result
    except Exception as e:
        raise StringMultitoolError(f"Transformation failed: {e}")
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest test_transform.py -v

# Run specific test categories
python test_transform.py

# Run with coverage report
python -m pytest test_transform.py --cov=string_multitool

# Run integration tests
python -m pytest test_readme_examples.py -v
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
    engine = TextTransformationEngine()
    result = engine.apply_transformations("test-string", "/h")
    assert result == "test_string"

def test_sequential_transformations():
    """Test chaining multiple transformations."""
    engine = TextTransformationEngine()
    result = engine.apply_transformations("Hello-World", "/h/l")
    assert result == "hello_world"
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type information and examples where helpful

### User Documentation

- Update README.md for user-facing changes
- Add transformation examples to config/transformation_rules.json
- Update CLAUDE.md for development workflow changes

## Submitting Changes

### Pull Request Process

1. Ensure all tests pass
2. Update documentation as needed
3. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Test results for all transformation rules
   - Updated documentation if needed

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
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Log files from logs/ directory
- Configuration files from config/ directory (remove RSA keys)

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

1. Update version in pyproject.toml
2. Run full test suite with all transformation rules
3. Build executable with .\build.ps1
4. Test interactive and daemon modes
5. Update README.md examples
6. Create GitHub release

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
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributor statistics

Thank you for contributing to String_Multitool!