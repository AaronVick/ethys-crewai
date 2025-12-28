# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you believe you have found a security vulnerability, please report it privately to the maintainers:

- **Email**: security@ethys.dev (or use GitHub security advisory if available)
- **Subject**: Security Vulnerability in ethys-crewai

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Security Best Practices

When using this library:

1. **Never commit private keys** - Use environment variables or secure secret management
2. **Use `.env` files** - Add `.env` to `.gitignore`, never commit secrets
3. **Rotate keys** - Rotate API keys and private keys if compromised
4. **Safe logging** - Disable logging of request bodies/headers containing secrets
5. **Limit approvals** - For contract interactions, use specific amounts, not unlimited approvals
6. **Verify URLs** - Always verify the API endpoint URL is correct (default: https://402.ethys.dev)
7. **Keep dependencies updated** - Regularly update dependencies for security patches

## Disclosure Policy

- Vulnerabilities will be disclosed after a fix is available
- We will credit reporters (with permission)
- Critical vulnerabilities will be patched and disclosed within 7 days
- Non-critical vulnerabilities will be patched in the next regular release

