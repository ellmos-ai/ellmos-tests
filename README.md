# ellmos-tests

> Testing framework for LLM operating systems

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-24_total-orange)

---

## What is this?

**ellmos-tests** evaluates and compares SKILL.md-based systems (LLM operating systems) through three complementary test perspectives. It provides a structured methodology to assess how well an LLM-OS performs across onboarding, navigation, memory, task management, tools, communication, and error tolerance.

---

## Test Philosophy: B / O / E

| Perspective | Type | Question | Tests |
|-------------|------|----------|-------|
| **B-Tests** (Observation) | Automated, external | *"What exists?"* | 8 tests (B001–B008) |
| **O-Tests** (Output) | Functional, input→output | *"Does it work?"* | 6 tests (O001–O006) |
| **E-Tests** (Experience) | Subjective, process-oriented | *"How does it feel?"* | 10 tasks (E001–E010) |

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ B-Tests         │  │ O-Tests         │  │ E-Tests         │
│ OBSERVATION     │  │ OUTPUT          │  │ EXPERIENCE      │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ Inventory       │  │ Validation      │  │ Workflow         │
│ Structure       │  │ Correctness     │  │ Orientation      │
│ Consistency     │  │ Completeness    │  │ Cognitive Load   │
│ Metrics         │  │ Robustness      │  │ Agency           │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Features

- **8 B-Tests** — File inventory, format consistency, directory depth, naming analysis, documentation check, code metrics, dependency scan, age analysis
- **6 O-Tests** — Task roundtrip, memory persistence, tool registry, backup/restore, config validation, export/import
- **10 E-Tests** — SKILL.md readability, navigation, task creation, task finding, memory write/read, tool usage, error recovery, session start, overall impression
- **Feature Mapping DB** — SQLite database with 50+ features, multi-dimensional ratings, alias resolution, gap analysis, and duplicate detection
- **Synopsis Generator** — Automated cross-system comparisons with JSON + Markdown output
- **Test Batteries** — Predefined test collections (smoke tests, UX tests, integration tests, etc.)
- **System Classification** — SKILL / AGENT / TEXT-OS with class-appropriate test weighting

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/lukisch/ellmos-tests.git
cd ellmos-tests

# Run B-Tests against a system
python system_diff_tests/run_all.py "/path/to/your/llm-os" --only b

# Run O-Tests against a system
python system_diff_tests/run_all.py "/path/to/your/llm-os" --only o

# Run all automated tests
python system_diff_tests/run_all.py "/path/to/your/llm-os"

# Use a known system name (configured in config.py)
python system_diff_tests/run_all.py --system recludOS

# List available test batteries
python tests/run_batteries.py --list

# Run a specific battery
python tests/run_batteries.py --battery release_smoke --system-path "/path/to/system"
```

---

## Project Structure

```
ellmos-tests/
├── system_diff_tests/
│   ├── config.py                 # Central configuration (paths, known systems)
│   ├── run_all.py                # Main test runner (B + O tests)
│   ├── testing_workflow.md       # Full B/O/E methodology documentation
│   ├── comparation_workflow.md   # Cross-system comparison guide
│   ├── feature_mapping_workflow.md
│   ├── testing/                  # B-Test and O-Test scripts
│   │   ├── b_tests/             # B001–B008 observation tests
│   │   └── o_tests/             # O001–O006 output tests
│   ├── mapping/
│   │   ├── schema.sql           # Feature mapping DB schema
│   │   ├── populate_db.py       # DB population script
│   │   ├── query_db.py          # DB query utilities
│   │   └── Templates/           # Scan and diff templates
│   └── output/                  # Test results per system (JSON)
├── tests/
│   ├── batteries/               # Test battery definitions (.txt)
│   ├── results/                 # Battery runner results (JSON)
│   ├── interpretations/         # Human-readable analysis
│   ├── run_batteries.py         # Battery test runner
│   └── run_db_tests.py          # Database-specific tests
├── testing/                     # Additional test scripts
│   ├── test_api_modus_a.py
│   ├── test_api_modus_b.py
│   └── test_hq6_snapshot.py
└── README.md
```

---

## Test Profiles

| Profile | Duration | Tests | Purpose |
|---------|----------|-------|---------|
| **QUICK** | ~10 min | E001, E002, E010 | First impression |
| **STANDARD** | ~25 min | 9 E-Tests (excl. E008) | Full experience |
| **FULL** | ~40 min | All 10 E-Tests | Thorough analysis |
| **MEMORY_FOCUS** | ~15 min | E005, E006, E010 | Memory comparison |
| **TASK_FOCUS** | ~15 min | E003, E004, E010 | Task comparison |
| **OBSERVATION** | ~20 min | B001–B008 | External analysis (automated) |
| **OUTPUT** | ~30 min | O001–O006 | Functional tests (automated) |

**Recommended order:** OBSERVATION → OUTPUT → QUICK → STANDARD/FULL

---

## 7 Evaluation Dimensions

Each system is rated on a 1–5 scale across these dimensions:

| Dimension | Question |
|-----------|----------|
| **D1 Onboarding** | How quickly can you get started? |
| **D2 Navigation** | How well can you find your way around? |
| **D3 Memory** | How well does persistence work? |
| **D4 Tasks** | How good is task management? |
| **D5 Communication** | How good is user interaction? |
| **D6 Tools** | How usable are the tools? |
| **D7 Error Tolerance** | How robust is error handling/recovery? |

### Score Interpretation

| Score | Meaning |
|-------|---------|
| 1 | Very poor / Not present |
| 2 | Poor / Deficient |
| 3 | Average / Acceptable |
| 4 | Good / Above average |
| 5 | Excellent |

---

## System Classification

Before testing, classify the system under test:

| Class | Definition | Test Focus |
|-------|-----------|------------|
| **SKILL** | Single capability, one SKILL.md file | Readability, completeness, applicability |
| **AGENT/HUB** | Skill collection with central control | Navigation, tools, help system, consistency |
| **TEXT-OS** | Full operating system for LLM sessions | Lifecycle, memory, automation, recovery |

---

## Configuration

System paths are managed centrally via `system_diff_tests/config.py`.

Environment variables:
- `ELLMOS_BASE_PATH` — Root of the ellmos-tests project
- `ELLMOS_ONEDRIVE` — OneDrive base path (default: `~/OneDrive`)
- `NO_COLOR` — Disable colored terminal output
- `FORCE_COLOR` — Force colored terminal output

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

[MIT](LICENSE) — Copyright 2026 Lukas Geiger
