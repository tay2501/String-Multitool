# Security Policy

## Supported Versions

We actively support the following versions of String Multitool with security updates:

| Version | Supported          | Support End Date |
| ------- | ------------------ | ---------------- |
| 2.6.x   | ✅ Fully supported | TBD              |
| 2.x.x   | ✅ Security fixes only | 2025-12-31   |
| 1.x.x   | ❌ Not supported    | 2024-12-31       |
| 0.x.x   | ❌ Not supported    | 2024-06-30       |

## Security Features

String Multitool implements several security measures:

### Cryptographic Security
- **RSA-4096**: Industry-standard RSA encryption with 4096-bit keys
- **AES-256-CBC**: Advanced Encryption Standard with 256-bit keys
- **Hybrid Encryption**: Combines RSA + AES for optimal security and performance
- **Secure Key Generation**: Cryptographically secure random key generation
- **Proper Key Storage**: Private keys stored with restricted permissions (0o600)

### Input Security
- **Input Validation**: All user inputs are validated and sanitized
- **Buffer Protection**: Protection against buffer overflow attacks
- **Safe File Handling**: Secure file operations with proper error handling

### Configuration Security
- **Secure Defaults**: All security configurations use safe default values
- **JSON Validation**: Configuration files are validated against schemas
- **Sensitive Data Protection**: No sensitive data logged or exposed

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly:

### For Critical Vulnerabilities (CVE Score 7.0+)
**DO NOT** create a public GitHub issue. Instead:

1. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting
   - Go to the Security tab in the repository
   - Click "Report a vulnerability"
   - This creates a private advisory for coordinated disclosure
2. **Alternative Contact**: Email `tay2501@users.noreply.github.com`
3. **Subject**: `[SECURITY] String Multitool Critical Vulnerability Report`
4. **Encryption**: Use our PGP key if possible (see below)

### For Non-Critical Issues
You can create a private security advisory through GitHub:
1. Go to the Security tab in the repository
2. Click "Report a vulnerability" 
3. Fill out the advisory form

### What to Include
Please provide:
- **Description**: Clear description of the vulnerability
- **Impact**: Potential security impact and attack scenarios  
- **Reproduction**: Steps to reproduce (if safe to share)
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have ideas for mitigation

### Response Timeline (Updated 2025)
- **Acknowledgment**: Within 24 hours (business days)
- **Initial Assessment**: Within 72 hours
- **CVE Assignment**: Within 1 week (if applicable)
- **Fix Timeline**: Varies by CVSS severity
  - Critical (9.0-10.0): 1-3 days
  - High (7.0-8.9): 3-7 days
  - Medium (4.0-6.9): 1-4 weeks
  - Low (0.1-3.9): Next regular release
- **Public Disclosure**: 90 days after initial report (coordinated)

## Security Best Practices for Users

### Key Management
- **Protect Private Keys**: Never share your RSA private keys
- **Backup Safely**: Store key backups in secure locations
- **Key Rotation**: Consider rotating keys periodically

### Configuration
- **Review Settings**: Regularly review your security configurations
- **Update Dependencies**: Keep Python and dependencies updated
- **Monitor Logs**: Check logs for suspicious activity

### Usage Guidelines
- **Trusted Sources**: Only process data from trusted sources
- **Validate Outputs**: Verify encrypted/decrypted content integrity
- **Secure Environment**: Use String Multitool in secure environments

## Security Contacts

- **Primary Security Contact**: [@tay2501](https://github.com/tay2501)
- **GitHub Security Advisory**: [Report via GitHub](https://github.com/tay2501/String-Multitool/security/advisories/new)
- **Alternative Email**: `tay2501@users.noreply.github.com`
- **Emergency Contact**: Available via GitHub Issues for coordinated disclosure

## PGP Key for Encrypted Communications

For highly sensitive vulnerability reports, you can use our PGP public key:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBGXXXXXXBCADXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
(PGP Key will be provided when setting up actual security infrastructure)
-----END PGP PUBLIC KEY BLOCK-----
```

**Key Details:**
- Key ID: (To be provided)
- Fingerprint: (To be provided)
- Expires: (To be provided)

## Security Updates

Security updates are released as:
- **Patch Releases**: For backward-compatible fixes
- **Security Advisories**: Published through GitHub Security Advisories
- **Release Notes**: Security fixes documented in release notes

**Stay Informed:**
- Subscribe to [GitHub Security Advisories](https://github.com/tay2501/String-Multitool/security/advisories)
- Watch the repository for security-related releases
- Enable notifications for critical updates
- Follow our security-related discussions in GitHub Discussions

## Scope

This security policy covers:
- String Multitool core application
- Configuration files and dependencies
- Build and distribution processes
- Documentation and examples

**Out of Scope**:
- Third-party integrations not officially supported
- User-modified code or configurations
- Issues in underlying OS or Python interpreter

## Bug Bounty Program

Currently, String Multitool does not offer a formal bug bounty program. However, we deeply appreciate security research and will:

- Acknowledge security researchers in our security advisories
- Provide detailed credit in release notes
- Consider recognition rewards for significant security improvements

## Compliance and Standards

String Multitool follows these security standards:

- **OWASP Top 10**: Regular assessment against OWASP security risks
- **CWE/SANS Top 25**: Mitigation of most dangerous software errors  
- **NIST Cybersecurity Framework**: Alignment with CSF guidelines
- **ISO 27001 Principles**: Information security management best practices

## Automated Security Monitoring

Our repository includes automated security measures:

- **Dependabot**: Automatic dependency vulnerability scanning
- **CodeQL**: Static code analysis for security issues
- **Bandit**: Python-specific security linter
- **Safety**: Python dependency security scanner
- **pip-audit**: Python package vulnerability scanner

## Acknowledgments

We appreciate security researchers and users who report vulnerabilities responsibly. Contributors will be acknowledged in:
- Security advisories (with permission)
- Release notes
- This security policy

---

**Last Updated**: January 2025  
**Next Review**: July 2025  
**Version**: 2.1  
**Contact for Policy Questions**: [@tay2501](https://github.com/tay2501)