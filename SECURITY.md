# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x: |

---

## Security Model and Execution Guarantees

`ellmos-tests` is designed with local-first, defensible isolation:

1. **Unprivileged User Mode (`RunAsInvoker`)**: The framework operates strictly under standard user privileges. It does not require or request administrator or root elevation.
2. **Zero-Egress Isolation**: Core test runners, observation engines, output validators, and SQLite feature databases operate completely offline. No telemetry, crash logs, or test data are transmitted to external endpoints.
3. **Target Sandboxing**: When executing target system CLI entrypoints or scripts during O-tests, operations are executed in isolated child processes with dedicated working directory parameters and timeout boundaries.
4. **Governance Invariants**: Adheres strictly to security and governance invariants `INV-LOCAL-01` through `INV-SLA-10` documented in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

## Reporting a Vulnerability

If you discover a security vulnerability in `ellmos-tests`, please report it responsibly:

1. **Do NOT open a public issue.**
2. **Use GitHub's [Private Vulnerability Reporting](../../security/advisories/new)** to submit your report confidentially.
3. Include detailed information:
   - Impact and attack vector description
   - Minimal reproduction steps or proof-of-concept
   - Affected versions and environments

### Service Level Agreement (SLA)

- **Initial Response**: Within **48 hours** (INV-SLA-10).
- **Status & Triage**: Within **5 business days** following initial response.
- **Fix & Disclosure**: Coordinated security release after validation and patch development.
