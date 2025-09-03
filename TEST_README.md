# CLI Functionality Tests

## Overview

`test_cli_functionality.py` provides comprehensive pytest-based testing for the String_Multitool CLI functionality, including pipe chaining and parameterized rules.

## Test Structure

### Test Classes

1. **TestBasicTransformations**
   - Basic transformation rules (`/t/u`, `/l`, `/p`)
   - Single-stage transformations

2. **TestParameterizedRules** 
   - Rules requiring parameters (`/S '+'`, `/r 'old' 'new'`)
   - Argument handling validation

3. **TestPipeChaining**
   - Multi-stage pipe operations
   - Complex transformation chains
   - Real subprocess pipe testing

4. **TestSilentMode**
   - Silent mode output validation
   - Comparison with normal mode
   - Pipe compatibility in silent mode

5. **TestErrorHandling**
   - Invalid rule handling
   - Empty input processing
   - Error code validation

## Running Tests

### Basic Execution
```bash
# Run all CLI tests
python -m pytest test_cli_functionality.py -v

# Run specific test class
python -m pytest test_cli_functionality.py::TestPipeChaining -v

# Run with coverage
python -m pytest test_cli_functionality.py --cov=string_multitool
```

### Parametrized Tests
The test suite includes parametrized tests for comprehensive rule coverage:
```python
@pytest.mark.parametrize("rule,input_text,expected", [
    ("//u", "hello", "HELLO"),
    ("//l", "WORLD", "world"),  
    ("//t", "  spaced  ", "spaced"),
    ("//S", "Test Case", "test-case"),
])
```

## Key Test Features

### 1. Real Subprocess Testing
- Uses `subprocess.run()` and `subprocess.Popen()` for authentic CLI testing
- Tests actual pipe chaining between multiple process instances
- Validates real-world usage scenarios

### 2. Comprehensive Coverage
- **18 test cases** covering all major functionality
- Basic transformations, parameterized rules, pipe chaining
- Silent mode, error handling, help functionality

### 3. Windows Compatibility  
- Uses `//` rule format to avoid Windows CMD path interpretation
- Handles quoted parameters correctly
- Tests timeout handling (10s limit)

## Test Examples

### Pipe Chaining Test
```python
def test_trim_uppercase_to_slug(self, cli_script):
    stdout, stderr, code = run_pipe_chain(
        cli_script,
        [["//t//u"], ["//S", "+"]],
        "  test a  "
    )
    assert code == 0
    assert stdout == "test+a"
```

### Parameterized Rule Test  
```python
def test_slug_with_plus(self, cli_script):
    stdout, stderr, code = run_cli(cli_script, ["-s", "//S", "+"], "Test A")
    assert code == 0
    assert stdout == "test+a"
```

## Test Results

```
18 passed, 1 warning in 4.52s
```

All tests pass successfully, validating:
- ✅ Basic transformations
- ✅ Parameterized rules  
- ✅ Pipe chaining functionality
- ✅ Silent mode operation
- ✅ Error handling
- ✅ Help functionality

## Pytest Best Practices Applied

1. **Fixtures**: `cli_script` fixture for DRY principle
2. **Helper Functions**: `run_cli()` and `run_pipe_chain()` for reusability
3. **Clear Assertions**: Specific assertions for stdout, stderr, and return codes
4. **Timeout Handling**: 10-second timeout prevents hanging tests
5. **Parametrization**: Efficient testing of multiple input/output combinations
6. **Class Organization**: Logical grouping of related test cases

## Integration with Existing Tests

This test suite complements existing tests:
- `test_transform.py` - Unit tests for transformation engine
- `test_tsv_case_insensitive.py` - TSV-specific functionality  
- `test_cli_functionality.py` - **NEW** CLI integration tests

Together they provide comprehensive coverage of the String_Multitool functionality.