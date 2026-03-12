# TODO — ellmos-tests

Public-readiness checklist before switching repo `lukisch/ellmos-tests` from private to public.

---

## BLOCKER (must fix before public)

### 1. CRITICAL — Remove personally identifiable information (PII)
- [ ] `tests/batteries/connector_tests.txt` line ~80: **real email `lukasgeiger@googlemail.com`** → replace with `user@example.com`
- [ ] `tests/batteries/connector_tests.txt` line ~133: **employer references (`proAutismus`, `Caritas`)** → replace with `EmployerA`, `EmployerB`

### 2. CRITICAL — Remove hardcoded personal paths
- [ ] `testing/test_api_modus_a.py:14` — `C:\Users\lukas\OneDrive\.AI\BACH_strawberry\system` → use env var or config
- [ ] `testing/test_api_modus_b.py:14` — `C:\Users\lukas\OneDrive\.AI\BACH_strawberry\system` → use env var or config
- [ ] `tests/run_db_tests.py:19` — `C:\Users\User\OneDrive\.AI\BACH_v2_vanilla\system\data\bach.db` → use config
- [ ] `tests/smoke_test_sq072_pdf_migration.py:19` — `C:\Users\User\OneDrive\.AI\BACH_v2_vanilla\system` → use config
- [ ] `system_diff_tests/mapping/update_bach_v1_1.py:25` — `C:\Users\User\OneDrive\.AI\BACH_v1.1` → use config

All paths should use `system_diff_tests/config.py` (already exists with dynamic path resolution).

---

## HIGH PRIORITY

### 3. Translate German .txt documentation files
These are fully committed and entirely in German:

**Test concepts:**
- [ ] `system_diff_tests/testing/TESTKONZEPT.txt` (370 lines)
- [ ] `system_diff_tests/testing/SYSTEMKLASSEN_KONZEPT.txt` (120 lines)
- [ ] `system_diff_tests/testing/SKILL.txt` (170 lines)
- [ ] `system_diff_tests/testing/TEST_MEMORY.txt` (65 lines)

**E-Test task definitions:**
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E001_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E002_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E003_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E004_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E005_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E006_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E007_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E008_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E009_*.txt`
- [ ] `system_diff_tests/testing/e_tests/AUFGABEN/E010_*.txt`
- [ ] `system_diff_tests/testing/e_tests/PROMPT_TEMPLATE.txt` (310 lines)

**Rename directory:**
- [ ] `AUFGABEN/` → `tasks/`

### 4. Translate test battery files
- [ ] `tests/batteries/vernunft_kantian.txt` — fully German
- [ ] `tests/batteries/release_smoke.txt` — mostly German
- [ ] `tests/batteries/connector_tests.txt` — mixed (after PII removal)
- [ ] `tests/batteries/db_integrity.txt` — check language
- [ ] `tests/batteries/usecases.txt` — check language
- [ ] All other `tests/batteries/*.txt` — check and translate

### 5. Translate tests/README.md
- [ ] `tests/README.md` — currently fully German, should match root README (English)

---

## MEDIUM PRIORITY

### 6. Translate Python docstrings and comments
- [ ] `system_diff_tests/config.py` — German docstrings and comments
- [ ] `testing/test_api_modus_a.py` — German print statements and docstrings
- [ ] `testing/test_api_modus_b.py` — German print statements and docstrings
- [ ] `tests/run_db_tests.py` — German docstrings and test descriptions
- [ ] `tests/run_batteries.py` — German strings
- [ ] `system_diff_tests/mapping/populate_db.py` — German strings
- [ ] `system_diff_tests/testing/b_tests/B004_naming_analysis.py` — Umlauts in strings

### 7. Review workflow markdown files
- [ ] `system_diff_tests/testing_workflow.md` — check language, translate if needed
- [ ] `system_diff_tests/comparation_workflow.md` — check language, translate if needed
- [ ] `system_diff_tests/feature_mapping_workflow.md` — check language, translate if needed

---

## LOW PRIORITY

### 8. Clean up legacy test files
- [ ] `testing/test_hq6_snapshot.py` — check if still relevant
- [ ] `testing/test_api_modus_a.py` / `test_api_modus_b.py` — check if still relevant or should be archived

---

## STATUS

| Check          | Result |
|----------------|--------|
| Secrets        | PASS — no hardcoded keys |
| Private data   | **FAIL** — real email + employer refs + personal paths |
| BACH_KONTEXT/  | PASS — correctly in .gitignore |
| output/        | PASS — correctly in .gitignore |
| Bilingual      | **FAIL** — ~20 tracked files fully German |
| **Overall**    | **NOT READY for public** |

Last audited: 2026-03-12
