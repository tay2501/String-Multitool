# GitHub Actions Artifact Migration Guide

## Overview

This document explains the migration from `actions/upload-artifact@v3` to `actions/upload-artifact@v4` and `actions/download-artifact@v4` in our CI/CD pipeline.

## Migration Background

### Deprecation Notice
- **Effective Date**: January 30th, 2025
- **Official Source**: [GitHub Changelog - Deprecation notice: v3 of the artifact actions](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/)
- **Impact**: Workflows using v3 will fail after the deprecation date

### Performance Improvements
- **Upload Speed**: Up to 90% improvement in upload performance
- **Download Speed**: Up to 98% improvement in download performance  
- **Availability**: Artifacts are immediately available in UI and REST API
- **Reliability**: Artifacts are now "immutable" and cannot be modified

## Changes Made

### 1. Upload Artifact Updates

**Before (v3)**:
```yaml
- name: Upload security reports
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: security-reports
    path: |
      bandit-report.json
      safety-report.json
```

**After (v4)**:
```yaml
- name: Upload security reports
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: security-reports
    path: |
      bandit-report.json
      safety-report.json
```

**Changes**: Only version number update required for basic usage.

### 2. Build Artifacts Updates

**Before (v3)**:
```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v3
  with:
    name: executables-${{ runner.os }}
    path: dist/String_Multitool_*
```

**After (v4)**:
```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v4
  with:
    name: executables-${{ runner.os }}
    path: dist/String_Multitool_*
```

**Changes**: Only version number update required.

### 3. Download Artifact Updates

**Before (v3)**:
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@v3
```

**After (v4)**:
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@v4
  with:
    merge-multiple: true
```

**Changes**: Added `merge-multiple: true` parameter to merge multiple artifacts into a single directory.

## Key Breaking Changes in v4

### 1. Immutable Artifacts
- **v3**: Artifacts could be overwritten by multiple uploads to same name
- **v4**: Artifacts are immutable; attempting to upload to same name fails
- **Impact**: Ensures data integrity and prevents corruption

### 2. Multiple Artifacts Handling
- **v3**: Multiple artifacts automatically merged during download
- **v4**: Requires explicit `merge-multiple: true` parameter
- **Benefit**: More control over artifact organization

### 3. Job Limitations
- **New Limit**: Maximum 500 artifacts per job
- **Rationale**: Performance optimization
- **Mitigation**: Our project uploads 4-6 artifacts per job (well within limit)

### 4. Hidden Files
- **v4.4+**: Hidden files excluded by default
- **Override**: Use `include-hidden-files: true` if needed
- **Project Impact**: No impact as we don't rely on hidden files

## Compatibility Notes

### Cross-Version Compatibility
- **Important**: v4 artifacts cannot be downloaded by v3 actions
- **Migration Strategy**: Update all upload/download actions together
- **Rollback**: Ensure all workflow steps use same version

### GitHub Enterprise Server
- **Status**: v4 not yet supported on GHES
- **Timeline**: Will be available in future GHES releases
- **Current Project**: Uses GitHub.com, fully supported

## Validation and Testing

### Pre-Migration Testing
1. **Syntax Validation**: YAML syntax remained valid ✅
2. **Workflow Execution**: Test runs on feature branch ✅
3. **Artifact Integrity**: Confirmed all artifacts upload/download correctly ✅

### Post-Migration Benefits
1. **Performance**: Faster artifact operations
2. **Reliability**: Immutable artifacts prevent corruption
3. **Future-Proof**: Compliant with GitHub's roadmap

## Best Practices Applied

### 1. Proactive Migration
- Migrated before enforcement date (January 30, 2025)
- Avoided brownout periods and workflow failures
- Maintained development velocity

### 2. Documentation
- Documented all changes with rationale
- Included performance and reliability benefits
- Created maintenance guide for future updates

### 3. Version Pinning
- Used specific version (`@v4`) rather than `@latest`
- Ensures reproducible builds
- Prevents unexpected breaking changes

## Future Maintenance

### 1. Monitor New Versions
- Watch [actions/upload-artifact repository](https://github.com/actions/upload-artifact) for updates
- Review release notes for breaking changes
- Plan migration timeline for major version updates

### 2. Performance Monitoring
- Monitor artifact upload/download times
- Compare against baseline metrics
- Report performance improvements to team

### 3. Feature Adoption
- Evaluate new features in future v4.x releases:
  - Compression level configuration
  - Pattern-based downloads
  - Custom artifact retention

## References

### Official Documentation
- [GitHub Actions Artifacts v4 Documentation](https://github.com/actions/upload-artifact)
- [Migration Guide](https://github.com/actions/upload-artifact/blob/main/MIGRATION.md)
- [GitHub Blog: Get started with v4](https://github.blog/news-insights/product-news/get-started-with-v4-of-github-actions-artifacts/)

### Project-Specific
- **Modified Files**: `.github/workflows/ci.yml`
- **Validation Date**: 2025-01-24
- **Migration Status**: ✅ Complete

## Troubleshooting

### Common Issues
1. **Artifact Name Conflicts**: Use unique names per job/run
2. **Download Failures**: Ensure `merge-multiple: true` for multiple artifacts
3. **Missing Artifacts**: Check artifact retention policy (90 days default)

### Support
- **GitHub Actions Support**: [GitHub Community](https://github.com/orgs/community/discussions)
- **Project Issues**: Create GitHub issue with `ci/cd` label
- **Emergency**: Contact development team lead