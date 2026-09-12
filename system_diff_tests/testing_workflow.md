# Testing Workflow

> Systematic evaluation of LLM OS systems using B/O/E tests

**Version:** 1.0 | **As of:** 2026-01-26
**Source:** Consolidated from WORKFLOW_4_TESTVERFAHREN, TESTKONZEPT, SYSTEMKLASSEN_KONZEPT, E-Test tasks, Prompt template

---

## 1. Overview

This workflow describes three complementary testing perspectives for evaluating `SKILL.md`-based systems:

```
+-----------------+  +-----------------+  +-----------------+
| B-Tests         |  | O-Tests         |  | E-Tests         |
| OBSERVATION     |  | OUTPUT          |  | EXPERIENCE      |
+-----------------+  +-----------------+  +-----------------+
| External        |  | Functional      |  | Internal        |
| Automated       |  | Input->Output   |  | Subjective      |
| "What exists?"  |  | "Does it work?" |  | "How does it    |
|                 |  |                 |  |  feel?"         |
+-----------------+  +-----------------+  +-----------------+
  Inventory            Validation           Workflow
  Structure            Correctness          Orientation
  Consistency          Completeness         Cognitive Load
  Metrics              Robustness           Agency / Actionability
```

---

## 2. System Classes

Before testing: classify the system. Compare only within the same class or with class-specific weighting.

| Class | Definition | Examples | Test Focus |
|---|---|---|---|
| **SKILL** | Single capability, one `SKILL.md` file | Anthropic Skills (docx, pdf) | Readability, completeness, applicability |
| **AGENT/HUB** | Skill collection with central control | _CHIAH | Navigation, tools, help system, consistency |
| **TEXT-OS** | Full operating system for Claude/LLM sessions | _BATCH, recludOS, BACH v1.1 | Lifecycle, memory, automation, recovery |

**Requirements per class:**
- SKILL does NOT need task management
- AGENT does NOT need a daemon
- OS MUST have a session lifecycle

---

## 3. Test Profiles

| Profile | Duration | Tests | Purpose |
|---|---|---|---|
| **QUICK** | ~10 min | E001, E002, E010 | First impression |
| **STANDARD** | ~25 min | 9 E-tests (excl. E008) | Full experience |
| **FULL** | ~40 min | All 10 E-tests | Thorough analysis |
| **MEMORY_FOCUS** | ~15 min | E005, E006, E010 | Memory comparison |
| **TASK_FOCUS** | ~15 min | E003, E004, E010 | Task comparison |
| **OBSERVATION** | ~20 min | B001–B008 | External analysis (automated) |
| **OUTPUT** | ~30 min | O001–O006 | Functional tests (automated) |

Profile definitions as JSON under: `tests/PROFILE/*.json`

**Recommended sequence:**
1. OBSERVATION (B-Tests) - Establish objective baseline
2. OUTPUT (O-Tests) - Functional validation
3. QUICK (E-Tests) - Gain initial user impression
4. Optional: STANDARD/FULL - Full experience evaluation

---

## 4. B-Tests (Observation) - Automated

**Characteristics:** External, automatable, objectively measurable
**Output:** Numbers, percentages, lists
**Scripts:** `tests/BEOBACHTUNG/`

| ID | Script | Measures |
|---|---|---|
| B001 | `B001_file_inventory.py` | File counts by type, sizes |
| B002 | `B002_format_consistency.py` | Uniformity of formats |
| B003 | `B003_directory_depth.py` | Max/avg structure depth |
| B004 | `B004_naming_analysis.py` | Naming consistency |
| B005 | `B005_documentation_check.py` | Documentation completeness |
| B006 | `B006_code_metrics.py` | LOC, complexity |
| B007 | `B007_dependencies.py` | External dependencies |
| B008 | `B008_age_analysis.py` | Recent modifications |

### Execution

```bash
# Test a single system
cd tests/BEOBACHTUNG
python run_b_tests.py "C:\Path\To\System"

# Test all systems (example, paths via config.py / ELLMOS_ONEDRIVE)
cd ..\..
python run_all.py --system BACH_v1.1 --only b
python run_all.py --system _BATCH --only b
python run_all.py --system _CHIAH --only b
python run_all.py --system recludOS --only b
```

**Known Limitations:**
- B001 and B003 do not have a top-level `score` field in JSON output; the runner sets score to 0. Evaluate via `metrics` or `evaluation` fields.
- For very large systems (>2000 files), B002/B006/B007 may hit a 60-second timeout.
- Result JSON is saved under `tests/ERGEBNISSE/<system>/B_TEST_<system>_<date>.json`.

---

## 5. O-Tests (Output) - Functional

**Characteristics:** Input->Output validation, functional
**Output:** Pass/Fail, correctness in %
**Scripts:** `tests/AUSGABE/`

| ID | Script | Checks |
|---|---|---|
| O001 | `O001_task_roundtrip.py` | Create->Read->Update->Delete |
| O002 | `O002_memory_persistence.py` | Write->Restart->Read |
| O003 | `O003_tool_registry.py` | Call tool->Verify result |
| O004 | `O004_backup_restore.py` | Backup->Delete->Restore |
| O005 | `O005_config_validation.py` | Config files parseable? |
| O006 | `O006_export_import.py` | Export->Import data |

### Execution

```bash
cd tests/AUSGABE
python run_o_tests.py "C:\Path\To\System"
```

**Result Format:** JSON under `tests/ERGEBNISSE/<system>/O_TEST_<system>_<date>.json`

---

## 6. E-Tests (Experience) - Subjective

**Characteristics:** Internal, subjective, process-oriented, time-measured
**Output:** Timestamps/durations, ratings (1–5), free text
**Task Definitions:** `tests/ERFAHRUNG/AUFGABEN/E001-E010_*.txt`
**Prompt Template:** `tests/ERFAHRUNG/PROMPT_TEMPLATE.txt`

| ID | Name | Evaluates |
|---|---|---|
| E001 | SKILL.md Readability | Initial orientation, clarity |
| E002 | Navigation | Directory structure exploration |
| E003 | Create Task | Workflow, steps, time required |
| E004 | Find Task | Discoverability, logical placement |
| E005 | Write Memory | Location, method, format |
| E006 | Read Memory | Context restoration |
| E007 | Use Tool | Find, comprehend, execute |
| E008 | Error Recovery | Backups, recycle bin / undo mechanism |
| E009 | Start Session | Bootstrap experience |
| E010 | Overall Impression | Holistic evaluation across dimensions |

### Execution Protocol

E-Tests are conducted manually by Claude (or a human evaluator):

1. **Preparation:** Choose test profile, read PROMPT_TEMPLATE.txt
2. **Start:** Start timer (fc_get_time or clock)
3. **Execution:** Work through tasks sequentially, recording T_START/T_END per task
4. **Documentation:** Produce structured result JSON

### Critical Rules

```
TIME MEASUREMENT:
  Before each task: Record start timestamp (T_START)
  After each task:  Record end timestamp (T_END)
  Calculate delta:  T_TOTAL = T_END - T_START (seconds)

ABORT CRITERIA:
  Single task: Max 10 minutes (600 seconds)
  After 5 min without progress: Consider aborting task
  Result on abort: "TIMEOUT"

  Overall test:
  - FULL:     Max 60 minutes
  - STANDARD: Max 30 minutes
  - QUICK:    Max 15 minutes

IMMEDIATE ABORT:
  - System unreachable
  - Critical files missing
  - Infinite loop detected
```

### E-Test Tasks in Detail

**E001 - SKILL.md Readability:**
1. Open SKILL.md and read completely
2. Answer: Purpose understood? First action clear? Core concepts identified? Getting Started present?
3. Ratings (1–5): Readability, Structure, Completeness

**E002 - Navigation:**
1. Explore file system (max depth 3)
2. Locate: Documentation, Config, Tools, Temp, Memory, Tasks
3. Ratings (1–5): Structural logic, Naming, Navigation

**E003 - Create Task:**
1. Locate task storage location
2. Create task "SEP test task"
3. Verify task existence
4. Ratings (1–5): Clarity, Simplicity, Documentation

**E004 - Find Task:**
1. Search existing tasks
2. Read at least one task file
3. Understand task structure

**E005 - Write Memory:**
1. Locate memory system
2. Write short-term memory entry
3. Write long-term memory entry

**E006 - Read Memory (Context):**
1. Simulate session restart — what happened in the previous session?
2. Identify long-term context
3. Restore full session context

**E007 - Use Tool:**
1. Locate tool directory / registry
2. Select and understand a tool
3. Execute tool or document execution method

**E008 - Error Recovery:**
1. Locate backup system
2. Inspect recycle bin / undo mechanism
3. Document recovery workflow

**E009 - Start Session:**
1. Locate startup protocol / bootloader
2. Follow documented steps
3. Rate degree of automation

**E010 - Overall Impression:**
1. Summarize system in a single sentence
2. Top 3 strengths + Top 3 weaknesses
3. Rate all 7 evaluation dimensions (1–5)

---

## 7. Evaluation Dimensions (1–5 Scale)

| Dimension | Description |
|---|---|
| D1 Onboarding | How quickly can a user or agent get started? |
| D2 Navigation | How easily can one navigate the workspace? |
| D3 Memory | How well does state persistence work? |
| D4 Tasks | How efficient is task management? |
| D5 Communication | How effective is user/agent interaction? |
| D6 Tools | How accessible and well-documented are tools? |
| D7 Error Tolerance | How robust against failures and easy to recover? |

| Rating | Meaning |
|---|---|
| 1 | Very poor / Missing |
| 2 | Poor / Subpar |
| 3 | Fair / Acceptable |
| 4 | Good / Above average |
| 5 | Excellent / Outstanding |

**Success Status per Test:**

| Status | Code | Meaning |
|---|---|---|
| SUCCESS | 2 | Task fully completed |
| PARTIAL | 1 | Partially completed or completed with assistance |
| FAILED | 0 | Failed to complete |
| TIMEOUT | -1 | Time limit exceeded |
| BLOCKED | -2 | Not testable (feature missing) |

---

## 8. Time Measurements (Metrics Reference)

| Metric | Description | Unit |
|---|---|---|
| T_ORIENT | Time to initial orientation | Seconds |
| T_TASK_CREATE | Time to create a task | Seconds |
| T_TASK_FIND | Time to locate a task | Seconds |
| T_MEMORY_WRITE | Time to write a memory entry | Seconds |
| T_MEMORY_READ | Time to read memory | Seconds |
| T_TOOL_FIND | Time to find a tool | Seconds |
| T_TOOL_USE | Time to use a tool | Seconds |
| T_TOTAL | Total task duration | Seconds |

| Count | Description |
|---|---|
| N_FILES_TOUCHED | Number of files touched |
| N_STEPS | Number of steps to goal |
| N_TOOLS_USED | Number of tools utilized |
| N_ERRORS | Number of errors / failed attempts |

---

## 9. Result Format

Results are stored as JSON under: `tests/ERGEBNISSE/<system>/`

**Naming Convention:**
- B-Tests: `B_TEST_<system>_<date>.json`
- O-Tests: `O_TEST_<system>_<date>.json`
- E-Tests: `<PROFILE>_<date>.json`

**E-Test JSON Schema:**

```json
{
  "meta": {
    "system": "[SYSTEM_NAME]",
    "profile": "STANDARD",
    "tester": "Claude",
    "date": "[DATE]",
    "test_start": "[TIMESTAMP]",
    "test_end": "[TIMESTAMP]",
    "total_time_sec": 0
  },
  "tests": {
    "E001": {"time_sec": 0, "status": "SUCCESS", "notes": ""},
    "E002": {"time_sec": 0, "status": "", "notes": ""},
    "...": {}
  },
  "dimensions": {
    "d1_onboarding": 0,
    "d2_navigation": 0,
    "d3_memory": 0,
    "d4_tasks": 0,
    "d5_communication": 0,
    "d6_tools": 0,
    "d7_error_tolerance": 0
  },
  "overall_rating": 0.0,
  "summary": {
    "one_sentence": "",
    "strengths": ["", "", ""],
    "weaknesses": ["", "", ""],
    "recommendations": ["", "", ""]
  },
  "handlungsfaehigkeit": {
    "tools_used": [],
    "successful_actions": 0,
    "failed_attempts": 0,
    "files_touched": 0
  }
}
```

---

## 10. Database Integration

Test results can also be stored in SQLite:

- **Schema:** `tests/test_schema.sql`
- **Populate:** `python tests/populate_tests.py`
- **Query:** `python tests/query_tests.py`
- **Database:** `tests/test_library.db`

---

## 11. 12 System Components (Categories)

Every system is evaluated across these 12 functional areas:

| No. | Category | Description | B | O | E |
|---|---|---|---|---|---|
| K01 | BOOT/START | System startup, bootstrap, init | x | x | x |
| K02 | MEMORY | Short-term, long-term, context | x | x | x |
| K03 | TASKS | Task management, priority | x | x | x |
| K04 | TOOLS | Available tools, registry | x | x | x |
| K05 | AGENTS/SKILLS | Agents, services, delegation | x | x | x |
| K06 | LEARNING | Lessons learned, improvement | x | x | x |
| K07 | AUTONOMY | Daemon, automation | x | x | - |
| K08 | MAINTENANCE | Backup, recovery, recycle bin | x | x | x |
| K09 | NAVIGATION | Directory structure, naming, GUI | x | - | x |
| K10 | COMMUNICATION | User interaction, messaging | x | x | x |
| K11 | DOCUMENTATION | SKILL.md, rulebooks, guides | x | - | x |
| K12 | SHUTDOWN | Clean termination, persistence | x | x | x |

---

## 12. Checklist

### Before Testing
- [ ] System path known
- [ ] Test profile selected (QUICK/STANDARD/FULL/OBSERVATION/OUTPUT)
- [ ] System classified (SKILL/AGENT/TEXT-OS)
- [ ] Timing mechanism ready

### During Testing
- [ ] Start time recorded (per test and overall)
- [ ] Observations documented
- [ ] Abort criteria monitored on failure

### After Testing
- [ ] Result JSON saved under `tests/ERGEBNISSE/<system>/`
- [ ] `TEST_MEMORY.txt` updated (for multi-part tests)
- [ ] For comparison runs: update synopsis (see `comparation_workflow.md`)

---

## 13. Post-Processing

Upon completing test runs:
- Archive old test results (>30 days)
- Reset `TEST_MEMORY.txt` when no active tests remain
- Optimize database: `python -c "import sqlite3; c=sqlite3.connect('test_library.db'); c.execute('VACUUM'); c.close()"`

---

## Directory Structure

```
tests/
  BEOBACHTUNG/         B-Tests (B001-B008 + Runner)
  AUSGABE/             O-Tests (O001-O006 + Runner)
  ERFAHRUNG/
    AUFGABEN/          E-Test Task Definitions (E001-E010)
    PROMPT_TEMPLATE.txt  Standard Test Prompt for LLM Testers
  ERGEBNISSE/          Results per System
    <system>/          JSON Files per Test Run
  PROFILE/             Test Profiles as JSON
  VERGLEICH/           Synopses and Comparisons
  TESTKONZEPT.txt      Detailed Test Concept Reference
  SYSTEMKLASSEN_KONZEPT.txt  Classification Details
  test_schema.sql      DB Schema
  test_library.db      SQLite Database
  populate_tests.py    Populate DB
  query_tests.py       Query DB
```
