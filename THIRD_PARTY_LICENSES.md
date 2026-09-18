# Third-Party Licenses and Governance Invariants

**Repository:** ellmos-ai/ellmos-tests  
**Status:** Canonical & Audited  
**Date:** 2026-09-18  
**Package Version:** 0.2.1  
**Execution Context:** `RunAsInvoker` (Unprivileged User Mode)  

---

## 1. Runtime Dependencies SBOM

`ellmos-tests` is designed under the **Zero Mandatory Runtime Dependencies** architecture.
The core B/O/E testkit (B-Tests observation, O-Tests output, E-Tests experience prompts, battery runner, and SQLite feature mapping database) runs entirely using the **Python Standard Library**.

| Component | License | Type | Notes |
|---|---|---|---|
| Python Standard Library (`sys`, `os`, `json`, `sqlite3`, `pathlib`, `re`, `unittest`, `subprocess`, `importlib`) | Python Software Foundation License (PSF-2.0) | Runtime | 100% stdlib execution; no external packages needed |

---

## 2. Optional Development & Integration Dependencies

Optional packages are used solely for optional browser automation helpers and local test running conveniences:

| Component | License | Scope | Purpose |
|---|---|---|---|
| `playwright` | Apache-2.0 | Optional (dev/helpers) | Optional browser-based smoke test utilities under `system_diff_tests/testing/playwright/` |
| `pytest` | MIT | Optional (test runner) | Alternative test runner for developers; core suite uses stdlib `unittest` |

---

## 3. Zero-Copyleft & Isolation Guarantees

1. **Permissive Licensing**: `ellmos-tests` is licensed under the permissive **MIT License**.
2. **Zero-Copyleft Contagion**: The repository contains no GPL, AGPL, or viral copyleft dependencies in its runtime path.
3. **Subprocess Isolation**: When testing external target systems (e.g. executing resolvers, CLI scripts, or target modules), all executions occur via isolated subprocesses without linking or in-process contamination.

---

## 4. RunAsInvoker Non-Elevation Guarantee

`ellmos-tests` strictly operates within the unprivileged user context (`RunAsInvoker`):
- **No Administrator Privileges Required**: Does not request or require UAC elevation on Windows or `sudo` / `root` permissions on Linux/macOS.
- **Local Filesystem Confinement**: File operations, SQLite cache updates, and test outputs are confined strictly to repository-local or explicitly configured user directory paths.
- **Zero-Egress Isolation**: The core evaluation suite operates 100% offline, transmitting zero telemetry, zero analytics, and zero test payloads to external remote servers.

---

## 5. Governance & System Invariants

The following ten invariants are formally guaranteed and preserved across all releases:

- **INV-LOCAL-01 (Tri-Modal Evaluation Methodology)**: System quality is assessed through three complementary perspectives: static Observation (B-Tests), functional Output (O-Tests), and UX Experience (E-Tests).
- **INV-LOCAL-02 (Native LLM-OS & SKILL Binding)**: Native support for `SKILL.md`, `AGENTS.md`, and `ellmos-module.v2.json` declarations as first-class operating surfaces.
- **INV-LOCAL-03 (Zero-Egress Local Execution)**: Complete local-first execution; no external API calls, telemetry, or network requirements for core B/O/E testing.
- **INV-LOCAL-04 (Cross-System Synopsis & Gap Analysis)**: Structured SQLite feature mapping database with 50+ dimensions for multi-system comparisons and gap analysis.
- **INV-LOCAL-05 (Curated Checklist Batteries & Profile Engine)**: Modular execution profiles (`QUICK`, `STANDARD`, `FULL`, `MEMORY_FOCUS`, `TASK_FOCUS`, `OBSERVATION`, `OUTPUT`, `MODULE_STACK_FOCUS`) and customizable battery formats.
- **INV-LOCAL-06 (Modular Baukasten Composition Auditing)**: Dedicated O-tests (O007 module findability, O008 stack composition) for modular system registries.
- **INV-LOCAL-07 (Standard-Library-First Architecture)**: Zero mandatory external runtime dependencies or heavy machine learning frameworks for core framework operation.
- **INV-LOCAL-08 (Unprivileged RunAsInvoker Security)**: Strict non-elevated user-mode execution across all supported platforms.
- **INV-LOCAL-09 (Multi-Device Sync & Lock Resilience)**: Clean separation of generated outputs, persistent state, and test configurations to resist cloud synchronization conflicts and file locks.
- **INV-SLA-10 (Enterprise Security SLA & Triage)**: Formal 48-hour initial response SLA for privately reported security vulnerabilities with a 5-day triage commitment.
