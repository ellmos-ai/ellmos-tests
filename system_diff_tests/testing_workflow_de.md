# Test-Workflow

> Systematische Bewertung von LLM-OS-Systemen mit B/O/E-Tests

**Version:** 1.0 | **Stand:** 2026-01-26 (gepflegt 2026-07-30)
**Quelle:** Konsolidiert aus WORKFLOW_4_TESTVERFAHREN, TESTKONZEPT, SYSTEMKLASSEN_KONZEPT, E-Test-Aufgaben, Prompt-Template

---

## 1. Übersicht

Dieser Workflow beschreibt drei komplementäre Testperspektiven zur Bewertung von `SKILL.md`-basierten Systemen:

```
+-----------------+  +-----------------+  +-----------------+
| B-Tests         |  | O-Tests         |  | E-Tests         |
| BEOBACHTUNG     |  | AUSGABE         |  | ERFAHRUNG       |
+-----------------+  +-----------------+  +-----------------+
| Extern          |  | Funktional      |  | Intern          |
| Automatisiert   |  | Input->Output   |  | Subjektiv       |
| "Was existiert?"|  | "Funktioniert?" |  | "Wie fühlt es   |
|                 |  |                 |  |  sich an?"      |
+-----------------+  +-----------------+  +-----------------+
  Inventar            Validierung          Workflow
  Struktur            Korrektheit          Orientierung
  Konsistenz          Vollständigkeit      Kognitive Last
  Metriken            Robustheit           Handlungsfähigkeit
```

---

## 2. Systemklassen

Vor dem Testen: System klassifizieren. Vergleiche nur innerhalb derselben Klasse oder mit klassenspezifischer Gewichtung.

| Klasse | Definition | Beispiele | Test-Fokus |
|---|---|---|---|
| **SKILL** | Einzelne Fähigkeit, eine `SKILL.md`-Datei | Anthropic Skills (docx, pdf) | Lesbarkeit, Vollständigkeit, Anwendbarkeit |
| **AGENT/HUB** | Skill-Sammlung mit zentraler Steuerung | _CHIAH | Navigation, Tools, Help-System, Konsistenz |
| **TEXT-OS** | Vollständiges Betriebssystem für Claude/LLM-Sessions | _BATCH, recludOS, BACH v1.1 | Lifecycle, Memory, Automation, Recovery |

**Anforderungen pro Klasse:**
- SKILL muss NICHT Task-Management haben
- AGENT muss NICHT Daemon haben
- OS MUSS Session-Lifecycle haben

---

## 3. Testprofile

| Profil | Dauer | Tests | Zweck |
|---|---|---|---|
| **QUICK** | ~10 Min | E001, E002, E010 | Erster Eindruck |
| **STANDARD** | ~25 Min | 9 E-Tests (ohne E008) | Vollständige Erfahrung |
| **FULL** | ~40 Min | Alle 10 E-Tests | Gründliche Analyse |
| **MEMORY_FOCUS** | ~15 Min | E005, E006, E010 | Memory-Vergleich |
| **TASK_FOCUS** | ~15 Min | E003, E004, E010 | Task-Vergleich |
| **OBSERVATION** | ~20 Min | B001–B008 | Externe Analyse (automatisiert) |
| **OUTPUT** | ~30 Min | O001–O006 | Funktions-Tests (automatisiert) |

Profil-Definitionen als JSON unter: `tests/PROFILE/*.json`

**Empfohlene Reihenfolge:**
1. OBSERVATION (B-Tests) - Objektive Basis schaffen
2. OUTPUT (O-Tests) - Funktionale Validierung
3. QUICK (E-Tests) - Ersten Eindruck gewinnen
4. Bei Interesse: STANDARD/FULL - Vollständige Erfahrung

---

## 4. B-Tests (Beobachtung) - Automatisiert

**Charakteristik:** Extern, automatisierbar, objektiv messbar
**Output:** Zahlen, Prozente, Listen
**Skripte:** `tests/BEOBACHTUNG/`

| ID | Skript | Misst |
|---|---|---|
| B001 | `B001_file_inventory.py` | Anzahl Dateien nach Typ, Größen |
| B002 | `B002_format_consistency.py` | Einheitlichkeit der Formate |
| B003 | `B003_directory_depth.py` | Max/Avg Tiefe der Struktur |
| B004 | `B004_naming_analysis.py` | Konsistenz der Benennung |
| B005 | `B005_documentation_check.py` | Vollständigkeit der Doku |
| B006 | `B006_code_metrics.py` | LOC, Komplexität |
| B007 | `B007_dependencies.py` | Externe Dependencies |
| B008 | `B008_age_analysis.py` | Letzte Änderungen |

### Ausführung

```bash
# Einzelnes System testen
cd tests/BEOBACHTUNG
python run_b_tests.py "C:\Pfad\zum\System"

# Alle Systeme testen (Beispiel, Pfade via config.py / ELLMOS_ONEDRIVE)
cd ..\..
python run_all.py --system BACH_v1.1 --only b
python run_all.py --system _BATCH --only b
python run_all.py --system _CHIAH --only b
python run_all.py --system recludOS --only b
```

---

## 5. O-Tests (Ausgabe) - Funktional

**Charakteristik:** Input->Output Validierung, funktional
**Output:** Pass/Fail, Korrektheit in %
**Skripte:** `tests/AUSGABE/`

| ID | Skript | Prüft |
|---|---|---|
| O001 | `O001_task_roundtrip.py` | Erstellen->Lesen->Ändern->Löschen |
| O002 | `O002_memory_persistence.py` | Schreiben->Neustart->Lesen |
| O003 | `O003_tool_registry.py` | Tool aufrufen->Ergebnis prüfen |
| O004 | `O004_backup_restore.py` | Backup->Löschen->Restore |
| O005 | `O005_config_validation.py` | Config-Dateien parsbar? |
| O006 | `O006_export_import.py` | Daten exportieren->importieren |

---

## 6. E-Tests (Erfahrung) - Subjektiv

**Charakteristik:** Intern, subjektiv, prozessorientiert, zeitgemessen
**Output:** Zeiten, Bewertungen (1–5), Freitext
**Aufgaben-Definitionen:** `tests/ERFAHRUNG/AUFGABEN/E001-E010_*.txt`
**Prompt-Template:** `tests/ERFAHRUNG/PROMPT_TEMPLATE.txt`

---

## 7. Bewertungsdimensionen (1–5 Skala)

| Dimension | Beschreibung |
|---|---|
| D1 Onboarding | Wie schnell kann man loslegen? |
| D2 Navigation | Wie gut findet man sich zurecht? |
| D3 Memory | Wie gut funktioniert Persistenz? |
| D4 Tasks | Wie gut ist Aufgabenverwaltung? |
| D5 Kommunikation | Wie gut ist User-Interaktion? |
| D6 Tools | Wie gut sind Werkzeuge nutzbar? |
| D7 Fehlertoleranz | Wie robust bei Fehlern/Recovery? |

---

## 8. Ergebnis-Format & Datenbank

Ergebnisse werden als JSON gespeichert unter `tests/ERGEBNISSE/<system>/` oder in der SQLite-Datenbank (`tests/test_library.db`).
