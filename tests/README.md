# Test Batteries

**Status:** 2026-05-24 | **Scope:** battery runner and predefined battery files

This directory contains reusable test batteries for LLM operating systems and
SKILL.md-based agent systems. The batteries are text definitions; the runner
parses them, executes checks that can be automated, and marks subjective
experience tasks as manual.

## Structure

```text
tests/
|-- batteries/              # Test battery definitions
|   |-- release_smoke.txt           # Critical smoke checks before release
|   |-- vernunft_kantian.txt        # Seven-dimensional reasonability test
|   |-- usecases.txt                # Use-case coverage checks
|   |-- db_integrity.txt            # Database integrity checks
|   |-- dist_type_check.txt         # Distribution classification checks
|   |-- llm_agnostic.txt            # LLM-agnostic behavior checks
|   |-- connector_tests.txt         # Connector and bridge checks
|   |-- registration.txt            # Registration checks
|   |-- swarm_search.txt            # Swarm-search checks
|   |-- system_integration.txt      # System integration checks
|   `-- user_experience.txt         # UX and workflow checks
|-- results/                # Runner output, usually YYYY-MM-DD_battery.json
|-- interpretations/        # Human-readable Markdown analysis
|-- run_batteries.py        # Battery runner
|-- run_db_tests.py         # Database-specific tests
`-- README.md
```

## Test Perspectives

- **B-Tests (Observation):** Static, automated checks. What exists in the system?
- **O-Tests (Output):** Functional input-to-output checks. What does the system do?
- **E-Tests (Experience):** Subjective workflow checks. How does the system feel in use?

## Battery Runner

`run_batteries.py` reads `tests/batteries/*.txt`, parses test definitions, and
executes automatable checks such as file existence, subprocess commands, SQL
queries, and simple pattern searches.

### Commands

```bash
# List all batteries
python tests/run_batteries.py --list

# Run one battery
python tests/run_batteries.py --battery release_smoke --system-path "/path/to/system"

# Run all batteries
python tests/run_batteries.py --all --system-path "/path/to/system"

# Verbose output
python tests/run_batteries.py --battery db_integrity --system-path "/path/to/system" -v
```

### Automated Coverage

| Check method      | Automated? | Description |
|:------------------|:----------:|:------------|
| `os.path.exists()` | Yes | File and directory existence checks |
| `subprocess` | Yes | Python or CLI command execution |
| SQL | Yes | SQLite queries against configured databases |
| grep / pattern search | Partial | Pattern checks in files |
| Manual E-Tests | No | Subjective assessment required |

### Output

- Colorized terminal output when supported
- Per-battery summary and overall result
- `NO_COLOR` disables color output
- `FORCE_COLOR` forces color output

## Workflow

1. Pick a battery: `python tests/run_batteries.py --list`
2. Run it: `python tests/run_batteries.py --battery NAME --system-path PATH`
3. Store machine-readable results in `tests/results/`
4. Write human-readable findings in `tests/interpretations/`
5. Convert findings into tracked project tasks

## Release Requirement

`release_smoke.txt` is the minimum release gate for this module. Do not publish
or tag a release until the release smoke battery has passed or a documented
exception exists in the release notes.

## Configuration

System paths are centralized in `system_diff_tests/config.py`.

Environment variables:

- `ELLMOS_BASE_PATH` - root of the `ellmos-tests` project
- `ELLMOS_ONEDRIVE` - OneDrive base path, defaulting to `~/OneDrive`
- `NO_COLOR` - disable color output
- `FORCE_COLOR` - force color output
