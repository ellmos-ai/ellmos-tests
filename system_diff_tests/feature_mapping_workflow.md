# Feature Mapping Workflow

> System cartography, feature discovery, and database management

**Version:** 1.0 | **As of:** 2026-01-26
**Source:** Consolidated from WORKFLOW_2_MAPPING, `populate_db.py`, `query_db.py`, `schema.sql`

---

## 1. Overview

This workflow describes the systematic recording and structured storage of system features in a SQLite database. It serves as the foundation for cross-system comparisons (see `comparation_workflow.md`).

```
+----------+    +----------+    +----------+    +----------+
| STEP 1   |---->| STEP 2   |---->| STEP 3   |---->| STEP 4   |
| Dir Scan |    | Features |    | Database |    |   Diff   |
+----------+    +----------+    +----------+    +----------+
```

---

## 2. Step 1: Directory Scan

**Objective:** Capture the complete directory layout of a system

**Method:**
- LLM / Agent: `fc_list_directory(<system_root>, depth=3)`
- CLI: `tree /F <system_root>` (Windows) or `find <system_root> -maxdepth 3` (Unix)

**Output:** `mapping/<system>/directory-scan.txt`

**Format:**
```
<system>/
+-- folder1/
|   +-- file1.txt
|   +-- file2.json
+-- folder2/
```

**Tips:**
- `depth=2` for high-level overview, `depth=3` for structural detail
- Large subdirectories (>50 files) should be scanned independently

---

## 3. Step 2: Feature Analysis

**Objective:** Identify functional capabilities and architectural concepts of a system

**Activities:**
1. Read `SKILL.md` / primary entry point
2. Extract core concepts
3. Document tools and commands
4. List registries and indexes
5. Analyze operational workflows

**Output:** `mapping/<system>/Features.txt`

**Format:**
```
===========================
SYSTEM: <name>
===========================

CORE CONCEPTS:
1. Concept A - Description
2. Concept B - Description

TOOLS:
- tool1: Functionality
- tool2: Functionality

WORKFLOWS:
- Startup: ...
- Shutdown: ...
```

---

## 4. Step 3: Populate Database

**Objective:** Persist discovered features in a structured SQLite format

**Database:** `mapping/feature_mapping.db`

### Schema (8 Tables)

| Table | Purpose |
|---|---|
| `systems` | Registered systems (Name, Path, Class, Version) |
| `feature_categories` | Feature categories (Boot, Memory, Tasks, etc.) |
| `features` | Feature definitions (Name, Category, Description) |
| `feature_aliases` | Alternative names and synonyms for features |
| `implementations` | Implementation status per system + feature |
| `ratings` | Evaluated ratings per system + feature |
| `file_fingerprints` | File fingerprints for change detection |
| `synopses` | Saved comparison texts and summaries |

**Schema File:** `mapping/schema.sql`

### Population Script

```bash
cd mapping
python populate_db.py
```

**What `populate_db.py` does:**
- Initializes database schema
- Registers systems (path, class, version)
- Defines 39 standard features across 8 categories
- Registers 43 feature aliases
- Records 63 feature implementation statuses (`full`, `partial`, `none`, `planned`)
- Calculates scores and ratings

**NOTE:** Ensure the database path in `populate_db.py` and `query_db.py` is configured appropriately:
```python
# Resolved dynamically or configured via env:
DB_PATH = r'<path>\feature_mapping.db'
```

### Database Queries

```bash
cd mapping
python query_db.py matrix              # Feature matrix across all systems
python query_db.py synopsis            # Automated comparison synopsis
python query_db.py gaps <system>       # Feature gaps for a specific system
python query_db.py alias <term>        # Search feature by alias
python query_db.py tech <system>       # Technology stack summary
python query_db.py profile <system>    # Complete system profile
```

### Feature Categories

| Category | Example Features |
|---|---|
| BOOT/START | Auto-startup, session lifecycle, partner system integration |
| MEMORY | Short-term, long-term, lessons learned, session logs |
| TASKS | Task manager, prioritization, hierarchical tasks |
| TOOLS | Tool registry, CLI interfaces, Python utility scripts |
| AGENTS | Multi-agent collaboration, delegation, specialization |
| AUTOMATION | Daemons, directory scanners, code injectors, recurring jobs |
| MAINTENANCE | Backup, restore, recycle bin, self-healing mechanisms |
| DOCUMENTATION | SKILL.md, help system, GUI / Dashboard |

### Implementation Status

| Status | Meaning |
|---|---|
| `full` | Fully implemented and verified |
| `partial` | Partially implemented |
| `none` | Not implemented |
| `planned` | Planned / in active development |

---

## 5. Step 4: Generate Diff

**Objective:** Detect changes and updates since the previous scan

**Activities:**
1. Load previous scan
2. Perform new directory scan
3. Compute structural and content diffs
4. Document modifications

**Output:** `mapping/<system>/scan-diff.txt`

**Format:**
```
CHANGES since <date>:

+ ADDED:
  - /folder/new_file.txt

- DELETED:
  - /folder/old_file.txt

~ MODIFIED:
  - /folder/file.txt (Size: 1KB -> 2KB)
```

---

## 6. Maintenance

### Stale Data
- Overwrite outdated scans (do not hoard obsolete scans)
- Remove decommissioned systems from the database
- Create a database backup prior to major schema modifications

### Database Optimization
```bash
python -c "import sqlite3; c=sqlite3.connect('feature_mapping.db'); c.execute('VACUUM'); c.close()"
```

---

## 7. Checklist

### Per System
- [ ] Folder `mapping/<system>/` exists
- [ ] `directory-scan.txt` up to date
- [ ] `Features.txt` complete
- [ ] Database entries populated
- [ ] `scan-diff.txt` generated (if updating)

### Overall
- [ ] All target comparison systems mapped
- [ ] Feature database fully populated
- [ ] Database paths in scripts correctly configured
- [ ] Ready for comparative analysis (-> `comparation_workflow.md`)

---

## 8. Directory Structure

```
mapping/
  feature_mapping.db               SQLite database
  schema.sql                       DB schema definition
  populate_db.py                   Initialize + populate database
  query_db.py                      Query database (6 commands)
  FEATURE_VERGLEICH_ALLE_SYSTEME.txt  Feature matrix summary text

  <system>/                        Per-system directory:
    directory-scan.txt             Directory layout
    Features.txt                   Feature analysis
    scan-diff.txt                  Diff since previous scan
    DOCS/                          Additional documentation
```
