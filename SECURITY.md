# Security Policy

## Reporting a vulnerability

Please do not open a public issue for security problems.
Use GitHub's **Report a vulnerability** button (Security tab of this repo) to send a private report.

## Scope and honest limits

This is a **simulation** project. It does not control real hardware.

- Never commit SROS2 keystores, private keys, or ROS bags. `.gitignore` blocks the common ones.
- ROS 2 traffic is unencrypted by default. See `docs/SECURITY_HARDENING.md` for the localhost-only, domain-isolation and SROS2 options this repo provides.
