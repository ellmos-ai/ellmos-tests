# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- `tools/usecases_sync.py` — Generator für zentralen, maschinenlesbaren Use-Case-Katalog.
  Liest `BACH/system/data/bach.db` (read-only, mode=ro, kein bach_api-Import) und schreibt
  `usecases.json` mit Feldern: id, title, description, module, test_score, last_tested,
  covering_skill, coverage_status. covering_skill/coverage_status aus NAIV_FINALAUDIT_2026-06-22.
- `usecases.json` — maschinenlesbarer UC-Katalog (50 anwenderorientierte UCs, 33 COVERED /
  13 PARTIAL / 4 OPEN, 45 mit covering_skill). Zwei UC-Universen klar getrennt (siehe unten).
- `tests/batteries/usecases.txt` — neu generiert aus den 50 aktuellen anwenderorientierten UCs
  (Kalender, Medikamente, Versicherungen, RPG, ...) mit covering_skill-Annotation.
- `tests/batteries/usecases_system_legacy.txt` — Archiv des alten systemorientierten Katalogs
  (UC001–UC049, Stand 2026-02-18, ATI-Pipeline / MCP / DB-Integrität). Thematisch verschieden
  vom anwenderorientierten Katalog; wird nicht gelöscht, aber nicht mehr aktiv gepflegt.

### Hinweis: Zwei UC-Universen
`usecases.json` / neues `usecases.txt` = anwenderorientiert (50 UCs aus bach.db).
`usecases_system_legacy.txt` = systemorientiert (UC001–UC049, veraltet). Nicht verwechseln.

### Added (cont.)
- `SKILL.md`, `AGENTS.md`, and `ellmos-module.json` package the project as an LLM-bindable ellmos module.
- BACH `tools/testing` compatibility surfaces: `system_diff_tests/testing/run_external.py`, top-level `run_b_tests.py` / `run_o_tests.py` wrappers, and `system_diff_tests/testing/profiles/`.
- Optional Playwright helper scripts under `system_diff_tests/testing/playwright/` with portable output paths.
- `requirements-optional.txt` documents optional browser-testing dependencies separately from the stdlib core.
- `tests/test_module_surfaces.py` verifies the module manifest, profile mirror, and runner import surface.
- CI: `tests.yml` GitHub Actions smoke workflow — Python 3.12 on ubuntu-latest, standard-library unit tests
- CI: `welcome.yml` — welcome message posted on first-time issue or pull request
- CI: `stale.yml` — marks issues and PRs stale after 30 days, auto-closes after 37 days
- `tests/test_config_paths.py` — regression tests for environment-variable-based path resolution
- `tests/test_run_batteries.py` covers both ID-first and category-first battery definition formats.
- Liability disclaimer in `README.md` (§ 521 BGB, MIT)
- German section in root `README.md` (bilingual policy)
- This `CHANGELOG.md`

### Added (public-readiness review, 2026-07-12)
- `tests/test_public_readiness.py` — regression tests that keep absolute user paths out of tracked files and prove the grep gate reports real hits.
- `pytest.ini` — pins the automated suite to `tests/`. The `test_*.py` scripts under `testing/` are manual HQ5/HQ6 scripts that load `bach_api` and write into a real BACH installation; a bare `pytest` in the repo root would otherwise collect and execute them.

### Security / Privacy
- `usecases.json` and `tools/usecases_sync.py` no longer leak the absolute path of the local BACH database. `_meta.source_db` now records the plain basename (`bach.db`); the generator writes `db_path.name` instead of the full path.
- `tools/usecases_sync.py`: removed the two hardcoded personal fallback paths (`C:/Users/<name>/...`). Database discovery now runs through `ELLMOS_ONEDRIVE`/`OneDrive` and home-relative candidates only.
- `tests/run_batteries.py::_run_grep_check` is implemented instead of always returning SKIP. It searches the configured system path for the patterns declared in a battery's check method and fails on unexpected hits, listing the offending file and line. The anti-PII gates in `release_smoke` and `connector_tests` were a no-op before this. Check methods that carry no machine-readable pattern now report FAIL ("check manually") rather than a silent SKIP.

### Changed
- `ellmos-module.v2.json` is the canonical manifest (the module catalog references `manifest_format: v2`); its `source_of_truth` now points at `https://github.com/ellmos-ai/ellmos-tests`. The v1 `ellmos-module.json` is marked `deprecated` and kept only as a discovery signature for readers that still look for that filename (e.g. `ellmos-agent-bridge`).
- README: the `Tests-24_total` badge was misleading — 24 counts B/O/E *definitions* (10 of them manual E-tasks), not automated tests. Split into a definitions badge and an automated-suite badge, with the distinction spelled out in both the English and German sections.
- `testing/test_hq6_snapshot.py`: snapshot code moved into `main()` behind a `__main__` guard and the system path resolved via `system_diff_tests.config`. It previously imported a sibling directory that no longer exists (`BACH_strawberry`) at module level, which broke `pytest` collection for the whole repo.
- `system_diff_tests/run_all.py`, `b_tests/run_b_tests.py`, and `o_tests/run_o_tests.py` now force UTF-8 subprocess decoding on Windows.
- README project structure now reflects the actual module/test layout, including generated output folders.
- `system_diff_tests/config.py`: path resolution migrated to `.TOPICS/.AI/.OS` layout; `ELLMOS_BASE_PATH` and `ELLMOS_ONEDRIVE` env vars now supported across all config paths
- Translated `tests/README.md` to English and clarified the battery runner workflow.
- Normalized German umlauts in the public code of conduct and battery runner CLI text.
- `tests/run_batteries.py`: category-first battery headers such as `TRANSPARENZ | V001 | ...` now parse correctly, restoring the 21-test Kantian reasonability battery in `--list`.

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
