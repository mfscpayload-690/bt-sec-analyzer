# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Ethical Use Policy

bt-sec-analyzer is designed exclusively for:
- **Authorized security testing** with written permission
- **Educational purposes** in controlled environments
- **Security research** on owned devices
- **Defensive security** assessments

**Prohibited uses:**
- Unauthorized access to devices
- Malicious attacks or harassment
- Privacy violations
- Any illegal activities

## Reporting a Vulnerability

**Please do NOT open public issues for security vulnerabilities.**

### How to Report

Use [GitHub Security Advisories](https://github.com/mfscpayload-690/bt-sec-analyzer/security/advisories) for responsible disclosure.

Include:
1. **Description**: Clear explanation of the vulnerability
2. **Impact**: Potential security impact
3. **Steps to Reproduce**: Detailed reproduction steps
4. **Environment**: OS, Python version, dependencies
5. **Proof of Concept**: If applicable (non-destructive)
6. **Suggested Fix**: If you have one

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 5 business days
- **Fix Timeline**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days
- **Disclosure**: Coordinated disclosure after fix

### Responsible Disclosure

We follow responsible disclosure practices:
1. Report received and acknowledged
2. Vulnerability validated and assessed
3. Fix developed and tested
4. Security advisory published
5. Public disclosure (after users have time to update)

## Security Features

### Built-in Safeguards

1. **Ethical Mode**: Enforces logging and confirmations
2. **Audit Logging**: All actions logged with timestamps
3. **User Confirmations**: Required before destructive operations
4. **Privilege Isolation**: Minimal privilege principle
5. **Input Validation**: MAC addresses, parameters validated

### Best Practices

- Always enable ethical mode in production
- Enable audit logging
- Require confirmations for attacks
- Use pkexec for privilege escalation
- Review audit logs regularly
- Keep dependencies updated

## Known Limitations

1. **Hardware Dependencies**: Some attacks require specific hardware
2. **Permission Requirements**: Root needed for certain operations
3. **Platform Support**: Primary support for Linux
4. **Bluetooth Stack**: Depends on BlueZ reliability

## Security Contacts

- **Security Issues**: [GitHub Security Advisories](https://github.com/mfscpayload-690/bt-sec-analyzer/security/advisories)
- **General Questions**: [GitHub Discussions](https://github.com/mfscpayload-690/bt-sec-analyzer/discussions)
- **Non-Security Bugs**: [GitHub Issues](https://github.com/mfscpayload-690/bt-sec-analyzer/issues)

## Recognition

We appreciate responsible disclosure. Security researchers will be:
- Acknowledged in security advisories (with permission)
- Listed in SECURITY_CONTRIBUTORS.md
- Thanked publicly (if desired)

## Legal

Users are responsible for compliance with all applicable laws, including:
- Computer Fraud and Abuse Act (CFAA) - USA
- Computer Misuse Act - UK
- EU Directive on Attacks against Information Systems
- GDPR (for personal data)
- Local laws and regulations

**Unauthorized use may result in criminal and civil penalties.**

---

Thank you for helping keep bt-sec-analyzer secure!
