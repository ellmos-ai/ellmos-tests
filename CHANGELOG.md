# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- German section in root README.md (bilingual policy)
- This CHANGELOG.md

---

## [0.1.1] — 2026-03-15

### Fixed
- Removed personally identifiable information (real email, employer names) from `tests/batteries/connector_tests.txt`
- Replaced 5 hardcoded Windows paths with environment-variable-based resolution (`testing/test_api_modus_a.py`, `testing/test_api_modus_b.py`, `tests/run_db_tests.py`, `tests/smoke_test_sq072_pdf_migration.py`, `system_diff_tests/mapping/update_bach_v1_1.py`)

### Changed
- Clone URL updated from `lukisch/ellmos-tests` to `ellmos-ai/ellmos-tests`
- `TODO.md` added to `.gitignore` and removed from tracking
- GitHub topics set via API

---

## [0.1.0] — 2026-03-12

### Added
- Initial release of the ellmos-tests framework
- **B-Tests (Observation):** 8 automated tests (B001–B008) — file inventory, format consistency, directory depth, naming analysis, documentation check, code metrics, dependency scan, age analysis
- **O-Tests (Output):** 6 functional tests (O001–O006) — task roundtrip, memory persistence, tool registry, backup/restore, config validation, export/import
- **E-Tests (Experience):** 10 subjective evaluation tasks (E001–E010) — readability, navigation, task creation, task finding, memory write/read, tool usage, error recovery, session start, overall impression
- Feature Mapping DB schema (`schema.sql`) with population and query scripts
- Test battery system with parser and runner (`run_batteries.py`)
- 11 predefined test batteries (release_smoke, vernunft_kantian, usecases, db_integrity, connector_tests, etc.)
- Central configuration via `system_diff_tests/config.py` with environment variable support
- Cross-system comparison tools (`compare_systems.py`)
- 4 test profiles (QUICK, STANDARD, FULL, OBSERVATION) with time estimates
- 7 evaluation dimensions (Onboarding, Navigation, Memory, Tasks, Communication, Tools, Error Tolerance)
- System classification (SKILL / AGENT / TEXT-OS)
- `TODO.md` with public-readiness checklist
- MIT License, CONTRIBUTING.md, README.md
