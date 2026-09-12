# Comparison Workflow

> Comparative analysis and synopsis of multiple LLM OS systems

**Version:** 1.0 | **As of:** 2026-01-26
**Source:** Consolidated from WORKFLOW_3_SYNOPSE, WORKFLOW_1_SYNTHESE (Phases 1–3), Synopsis templates

---

## 1. Overview

This workflow describes the systematic comparison and evaluation of multiple systems. It combines test results (`testing_workflow.md`) and feature mappings (`feature_mapping_workflow.md`) into a comprehensive assessment.

```
+----------+    +----------+    +----------+    +----------+
| STEP 1   |---->| STEP 2   |---->| STEP 3   |---->| STEP 4   |
| Collect  |    | Compare  |    | Evaluate |    | Synopsis |
+----------+    +----------+    +----------+    +----------+
```

---

## 2. Prerequisites

Before a comparison can take place:

- [ ] All target systems mapped (`feature_mapping_workflow.md`, Steps 1–3)
- [ ] Feature database populated (`mapping/feature_mapping.db`)
- [ ] Test results available (`testing_workflow.md`)
  - Minimum requirement: B-Tests and O-Tests (automated)
  - Ideal: E-Tests as well (manual)

---

## 3. Step 1: Collect Data

**Collect from three sources:**

| Source | Path | Content |
|---|---|---|
| Feature Mapping | `mapping/<system>/Features.txt` | Core concepts, tools, workflows |
| Test Results | `tests/ERGEBNISSE/<system>/*.json` | B/O/E Test Scores |
| Feature DB | `mapping/feature_mapping.db` | Implementation status |

**Database Queries for Quick Overview:**
```bash
cd mapping
python query_db.py matrix     # Feature Matrix
python query_db.py synopsis   # Automated Synopsis
```

---

## 4. Step 2: Feature Comparison

**Activities:**
1. Generate feature matrix (which system offers which features?)
2. Compare implementation status across systems
3. Identify differences
4. Highlight commonalities

**Matrix Format:**

```
Feature              Sys1      Sys2      Sys3      Sys4
-------------------------------------------------------
CLI                  full      full      none      full
Auto-Logging         none      full      none      full
Task Manager         JSON      SQLite    JSON      SQLite
Short-Term Memory    MD        MD+DB     MD        DB
Long-Term Memory     100+Rep.  archive/  snapshots DB
GUI/Dashboard        Manager   none      ControlCt Streamlit
Daemon/Headless      yes       no        no        yes
```

**Implementation Metrics:**
```bash
python query_db.py gaps <system>    # Missing features
python query_db.py profile <system> # System profile
```

---

## 5. Step 3: Evaluation

### 5.1 Dimensional Rating (7 Dimensions, 1–5 Scale)

| Dimension | Evaluation Focus |
|---|---|
| D1 Onboarding | How quickly can a user get started? SKILL.md quality, Getting Started guide |
| D2 Navigation | How well organized is the layout? Directory structure, naming conventions |
| D3 Memory | State persistence, short-term/long-term split, context restoration |
| D4 Tasks | Task management, prioritization, CRUD operations |
| D5 Communication | User interaction, feedback loops, messaging |
| D6 Tools | Tool availability, registry clarity, documentation |
| D7 Error Tolerance | Backup, recovery, recycle bin, system robustness |

**Overall Score Calculation:**
```
Overall Score = Average of all 7 dimension scores
```

### 5.2 Strengths & Weaknesses Analysis

For each system:
- Top 3 strengths (with rationale)
- Top 3 weaknesses (with rationale)
- Top 3 recommendations

### 5.3 System Classification

Classify systems into standard tiers (see `testing_workflow.md`, Section 2):
- SKILL (basic)
- AGENT/HUB (intermediate)
- TEXT-OS (complex)

**Important:** Compare only within the same class, or apply class-specific weightings!

---

## 6. Step 4: Write Synopsis

### 6.1 Structure

The synopsis follows this structure:

1. **Overall Result** - Ranking table (Score, Time, Class, Characteristics)
2. **System Classification** - SKILL / AGENT / TEXT-OS categorization
3. **Dimensional Comparison** - Direct side-by-side breakdown of the 7 dimensions
4. **Automated Test Results** - B-Test and O-Test scores
5. **B-Test Details** - Individual B-test metrics
6. **O-Test Details** - Individual O-test metrics
7. **E-Test Details** - Individual E-test results (if conducted)
8. **Feature Matrix** - Implementation comparison table
9. **Strengths/Weaknesses Matrix** - Per system breakdown
10. **Feature Statistics** - Totals for full/partial/none/planned
11. **Unique Features** - Features exclusive to specific systems
12. **Recommendations** - Actionable advice per system
13. **Feature Mapping DB Analysis** - Database-backed insights (if available)
14. **Conclusion** - Overall winner, best onboarding, best documentation

### 6.2 Overall Result Template

```
+-------------+----------+---------+-----------+-------------------------------+
| System      | Score    | Time    | Class     | Characteristics               |
+-------------+----------+---------+-----------+-------------------------------+
| 1. SysA     | X.X/5.0  | MM:SS   | TEXT-OS   | ...                           |
| 2. SysB     | X.X/5.0  | MM:SS   | AGENT/HUB | ...                           |
| 3. SysC     | X.X/5.0  | MM:SS   | TEXT-OS   | ...                           |
+-------------+----------+---------+-----------+-------------------------------+
```

### 6.3 Dimensional Comparison Template

```
                    Sys1    Sys2    Sys3    Sys4    BEST
                    ----    ----    ----    ----    ----
D1 Onboarding        5       4       3       4    Sys1
D2 Navigation        4       5       4       4    Sys2
D3 Memory            5       3       5       5    Sys1/Sys3
D4 Tasks             5       4       4       5    Sys1/Sys4
D5 Communication     4       4       4       4    Tied
D6 Tools             5       5       4       5    Sys1/Sys2/Sys4
D7 Error Tolerance   4       4       4       4    Tied
```

### 6.4 Best-of Extraction

For each system, document which features are prime candidates for adoption:

```
Adopt from System A:
  - Feature X (Rationale)
  - Feature Y (Rationale)

DO NOT adopt:
  - Feature Z (Too complex / Obsolete / Irrelevant)
```

---

## 7. Output

### Synopsis Document

**Storage Location:** `tests/VERGLEICH/` or as a standalone `.md` document

**Naming Convention:**
- `SYNOPSE_<Topic>_<Date>.txt`
- `SYSTEMVERGLEICH_<Scope>_<Date>.md`
- `VERGLEICH_<N>_SYSTEME_<Date>.md`

**Length:** 10–20 KB (comprehensive) or 3–5 KB (summary)

### Conclusion Template

```
OVERALL WINNER: <System> (<Score>/5.0)
  Rationale: ...

BEST ONBOARDING: <System>
  Rationale: ...

BEST DOCUMENTATION: <System>
  Rationale: ...

FOR A NEW SYSTEM (Best-of Blend):
  Combine <SysA> Feature + <SysB> Feature + <SysC> Feature
  Expected Result: ...
```

---

## 8. Integration with Synthesis (WORKFLOW 1)

If building a new system following a comparison:

| Synthesis Phase | Relevance | Information Utilized |
|---|---|---|
| Phase 1: Data Collection | Supplied by this workflow | Feature maps, test scores, synopsis |
| Phase 2: Architecture | Best-of extraction input | Selected features for inclusion |
| Phase 3: Dossier | Synopsis as decision basis | Architectural justification |
| Phase 4–5: Customization | Comparison as benchmark reference | Optimal implementation patterns |
| Phase 6–7: Implementation | Feature DB as checklist | Verification of implemented features |

---

## 9. Checklist

### Before Comparison
- [ ] All systems mapped (`feature_mapping_workflow.md`)
- [ ] Feature matrix created or DB populated
- [ ] Test results available (B/O/E)
- [ ] Systems classified (SKILL/AGENT/TEXT-OS)

### During Comparison
- [ ] Feature matrix documented
- [ ] All 7 dimensions evaluated (1–5 scale)
- [ ] Strengths and weaknesses per system identified
- [ ] Best-of candidates highlighted

### After Comparison
- [ ] Synopsis written and archived
- [ ] Recommendations formulated
- [ ] Conclusion and ranking published
- [ ] Optional: Best-of extraction prepared for next-generation system

---

## 10. Directory Structure (Overall)

```
system_diff_tests/
  testing_workflow.md          <- How to test
  feature_mapping_workflow.md  <- How to map features
  comparation_workflow.md      <- How to compare (this file)

  tests/                       All test data
    BEOBACHTUNG/               B-Test scripts
    AUSGABE/                   O-Test scripts
    ERFAHRUNG/                 E-Test tasks + prompt
    ERGEBNISSE/                Results per system
    PROFILE/                   Test profiles (JSON)
    VERGLEICH/                 Synopses and comparisons
    ...

  mapping/                     All mapping data
    feature_mapping.db         Feature database
    populate_db.py             Populate DB
    query_db.py                Query DB
    schema.sql                 DB schema
    <system>/                  Per-system scans + features
    ...
```
