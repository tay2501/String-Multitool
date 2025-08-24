## Summary

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Please delete options that are not relevant -->

- [ ] = Bug fix (non-breaking change which fixes an issue)
- [ ] ( New feature (non-breaking change which adds functionality)
- [ ] =¥ Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] =Ú Documentation update
- [ ] >ù Code cleanup/refactoring
- [ ] ¡ Performance improvement
- [ ] = Security enhancement
- [ ] =' Configuration change
- [ ] >ê Test improvement

## Related Issues

<!-- Link to related issues or feature requests -->
Fixes #(issue)
Closes #(issue)
Related to #(issue)

## Changes Made

<!-- Describe the changes made in detail -->

### Core Changes
- 
- 
- 

### Additional Changes
- 
- 
- 

## Testing

<!-- Describe how you tested your changes -->

### Test Cases
- [ ] Unit tests pass (`python -m pytest test_transform.py test_tsv_case_insensitive.py -v`)
- [ ] Type checking passes (`python -m mypy string_multitool/`)
- [ ] Code formatting is correct (`python -m black --check string_multitool/`)
- [ ] Import sorting is correct (`python -m isort --check-only string_multitool/`)

### Manual Testing
- [ ] Interactive mode tested
- [ ] Command line mode tested
- [ ] Daemon mode tested (if applicable)
- [ ] Cross-platform compatibility verified (if applicable)

### Security Testing (if applicable)
- [ ] Cryptography functions tested
- [ ] Input validation tested
- [ ] No sensitive data exposed

## Screenshots/Demo

<!-- If applicable, add screenshots or demo of the changes -->

## Breaking Changes

<!-- List any breaking changes and migration steps -->

### Migration Guide
<!-- If this introduces breaking changes, provide migration instructions -->

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improvement (describe)
- [ ] Performance regression (describe and justify)

## Documentation

<!-- Documentation updates -->

- [ ] Code comments updated
- [ ] README updated (if needed)
- [ ] CHANGELOG updated (if applicable)
- [ ] API documentation updated (if applicable)

## Checklist

<!-- Please check all applicable boxes -->

### Code Quality
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors
- [ ] Any dependent changes have been merged and published

### Security
- [ ] My changes don't introduce security vulnerabilities
- [ ] I haven't committed sensitive information (keys, passwords, etc.)
- [ ] Input validation is properly implemented where needed

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested edge cases and error conditions

### Dependencies
- [ ] I have checked for dependency conflicts
- [ ] New dependencies are justified and minimal
- [ ] Dependencies are pinned to secure versions

## Additional Notes

<!-- Any additional information, context, or concerns -->

---

**Reviewer Note**: Please ensure all checks pass before merging. Pay special attention to security implications and breaking changes.