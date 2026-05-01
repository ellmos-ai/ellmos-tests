# Testing Workflow

> Systematische Bewertung von LLM-OS-Systemen mit B/O/E-Tests

**Version:** 1.0 | **Stand:** 2026-01-26
**Quelle:** Konsolidiert aus WORKFLOW_4_TESTVERFAHREN, TESTKONZEPT, SYSTEMKLASSEN_KONZEPT, E-Test-Aufgaben, Prompt-Template

---

## 1. Uebersicht

Dieses Workflow beschreibt drei komplementaere Testperspektiven zur Bewertung von SKILL.md-basierten Systemen:

```
+-----------------+  +-----------------+  +-----------------+
| B-Tests         |  | O-Tests         |  | E-Tests         |
| BEOBACHTUNG     |  | AUSGABE         |  | ERFAHRUNG       |
+-----------------+  +-----------------+  +-----------------+
| Extern          |  | Funktional      |  | Intern          |
| Automatisiert   |  | Input->Output   |  | Subjektiv       |
| "Was existiert?"|  | "Funktioniert?" |  | "Wie fuehlt es  |
|                 |  |                 |  |  sich an?"      |
+-----------------+  +-----------------+  +-----------------+
  Inventar            Validierung          Workflow
  Struktur            Korrektheit          Orientierung
  Konsistenz          Vollstaendigkeit     Kognitive Last
  Metriken            Robustheit           Handlungsfaehigkeit
```

---

## 2. Systemklassen

Vor dem Testen: System klassifizieren. Vergleiche nur innerhalb derselben Klasse oder mit klassenspezifischer Gewichtung.

| Klasse | Definition | Beispiele | Test-Fokus |
|--------|-----------|-----------|------------|
| **SKILL** | Einzelne Faehigkeit, eine SKILL.md Datei | Anthropic Skills (docx, pdf) | Lesbarkeit, Vollstaendigkeit, Anwendbarkeit |
| **AGENT/HUB** | Skill-Sammlung mit zentraler Steuerung | _CHIAH | Navigation, Tools, Help-System, Konsistenz |
| **TEXT-OS** | Vollstaendiges Betriebssystem fuer Claude-Sessions | _BATCH, recludOS, BACH v1.1 | Lifecycle, Memory, Automation, Recovery |

**Anforderungen pro Klasse:**
- SKILL muss NICHT Task-Management haben
- AGENT muss NICHT Daemon haben
- OS MUSS Session-Lifecycle haben

---

## 3. Testprofile

| Profil | Dauer | Tests | Zweck |
|--------|-------|-------|-------|
| **QUICK** | ~10 Min | E001, E002, E010 | Erster Eindruck |
| **STANDARD** | ~25 Min | 9 E-Tests (ohne E008) | Vollstaendige Erfahrung |
| **FULL** | ~40 Min | Alle 10 E-Tests | Gruendliche Analyse |
| **MEMORY_FOCUS** | ~15 Min | E005, E006, E010 | Memory-Vergleich |
| **TASK_FOCUS** | ~15 Min | E003, E004, E010 | Task-Vergleich |
| **OBSERVATION** | ~20 Min | B001-B008 | Externe Analyse (automatisiert) |
| **OUTPUT** | ~30 Min | O001-O006 | Funktions-Tests (automatisiert) |

Profil-Definitionen als JSON unter: `tests/PROFILE/*.json`

**Empfohlene Reihenfolge:**
1. OBSERVATION (B-Tests) - Objektive Basis schaffen
2. OUTPUT (O-Tests) - Funktionale Validierung
3. QUICK (E-Tests) - Ersten Eindruck gewinnen
4. Bei Interesse: STANDARD/FULL - Vollstaendige Erfahrung

---

## 4. B-Tests (Beobachtung) - Automatisiert

**Charakteristik:** Extern, automatisierbar, objektiv messbar
**Output:** Zahlen, Prozente, Listen
**Skripte:** `tests/BEOBACHTUNG/`

| ID | Skript | Misst |
|----|--------|-------|
| B001 | `B001_file_inventory.py` | Anzahl Dateien nach Typ, Groessen |
| B002 | `B002_format_consistency.py` | Einheitlichkeit der Formate |
| B003 | `B003_directory_depth.py` | Max/Avg Tiefe der Struktur |
| B004 | `B004_naming_analysis.py` | Konsistenz der Benennung |
| B005 | `B005_documentation_check.py` | Vollstaendigkeit der Doku |
| B006 | `B006_code_metrics.py` | LOC, Komplexitaet |
| B007 | `B007_dependencies.py` | Externe Dependencies |
| B008 | `B008_age_analysis.py` | Letzte Aenderungen |

### Ausfuehrung

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

**Bekannte Einschraenkungen:**
- B001 und B003 haben kein top-level `score` Feld im JSON-Output; der Runner setzt Score auf 0. Auswertung ueber `metrics` bzw. `evaluation` Felder.
- Bei sehr grossen Systemen (>2000 Dateien) kann B002/B006/B007 ein 60-Sekunden-Timeout erreichen.
- Ergebnis-JSON wird unter `tests/ERGEBNISSE/<system>/B_TEST_<system>_<datum>.json` gespeichert.

---

## 5. O-Tests (Ausgabe) - Funktional

**Charakteristik:** Input->Output Validierung, funktional
**Output:** Pass/Fail, Korrektheit in %
**Skripte:** `tests/AUSGABE/`

| ID | Skript | Prueft |
|----|--------|--------|
| O001 | `O001_task_roundtrip.py` | Erstellen->Lesen->Aendern->Loeschen |
| O002 | `O002_memory_persistence.py` | Schreiben->Neustart->Lesen |
| O003 | `O003_tool_registry.py` | Tool aufrufen->Ergebnis pruefen |
| O004 | `O004_backup_restore.py` | Backup->Loeschen->Restore |
| O005 | `O005_config_validation.py` | Config-Dateien parsbar? |
| O006 | `O006_export_import.py` | Daten exportieren->importieren |

### Ausfuehrung

```bash
cd tests/AUSGABE
python run_o_tests.py "C:\Pfad\zum\System"
```

**Ergebnis-Format:** JSON unter `tests/ERGEBNISSE/<system>/O_TEST_<system>_<datum>.json`

---

## 6. E-Tests (Erfahrung) - Subjektiv

**Charakteristik:** Intern, subjektiv, prozessorientiert, zeitgemessen
**Output:** Zeiten, Bewertungen (1-5), Freitext
**Aufgaben-Definitionen:** `tests/ERFAHRUNG/AUFGABEN/E001-E010_*.txt`
**Prompt-Template:** `tests/ERFAHRUNG/PROMPT_TEMPLATE.txt`

| ID | Name | Erfasst |
|----|------|---------|
| E001 | SKILL.md Lesbarkeit | Erste Orientierung, Verstaendnis |
| E002 | Navigation | Dateisystem-Erkundung |
| E003 | Task erstellen | Workflow, Schritte, Zeit |
| E004 | Task finden | Auffindbarkeit, Logik |
| E005 | Memory schreiben | Wo? Wie? Format? |
| E006 | Memory lesen | Kontext-Wiederherstellung |
| E007 | Tool nutzen | Finden, Verstehen, Ausfuehren |
| E008 | Fehler-Recovery | Backups, Papierkorb finden |
| E009 | Session starten | Bootstrap-Erfahrung |
| E010 | Gesamteindruck | Alle Dimensionen bewerten |

### Durchfuehrung

E-Tests werden manuell von Claude (oder einem Tester) durchgefuehrt:

1. **Vorbereitung:** Testprofil waehlen, PROMPT_TEMPLATE.txt lesen
2. **Start:** Zeitmessung starten (fc_get_time oder Uhr)
3. **Tests:** Aufgaben der Reihe nach abarbeiten, pro Aufgabe T_START/T_END notieren
4. **Dokumentation:** Ergebnis-JSON erstellen

### Kritische Regeln

```
ZEITMESSUNG:
  Vor jeder Aufgabe:   Startzeit notieren
  Nach jeder Aufgabe:  Endzeit notieren
  Differenz berechnen: T_TOTAL = T_END - T_START (Sekunden)

ABBRUCHKRITERIEN:
  Einzelaufgabe: Max 10 Minuten (600 Sekunden)
  Nach 5 Min ohne Fortschritt: Abbruch erwaegen
  Ergebnis bei Abbruch: "TIMEOUT"

  Gesamttest:
  - FULL:     Max 60 Minuten
  - STANDARD: Max 30 Minuten
  - QUICK:    Max 15 Minuten

SOFORT-ABBRUCH:
  - System nicht erreichbar
  - Kritische Dateien fehlen
  - Endlosschleife erkannt
```

### E-Test Aufgaben im Detail

**E001 - SKILL.md Lesbarkeit:**
1. SKILL.md oeffnen und vollstaendig lesen
2. Beantworten: Zweck verstanden? Erste Handlung klar? Kernkonzepte identifiziert? Getting Started vorhanden?
3. Bewertungen (1-5): Lesbarkeit, Struktur, Vollstaendigkeit

**E002 - Navigation:**
1. Dateisystem erkunden (max depth 3)
2. Finden: Dokumentation, Config, Tools, Temp, Memory, Tasks
3. Bewertungen (1-5): Struktur-Logik, Naming, Navigation

**E003 - Task erstellen:**
1. Task-Speicherort finden
2. Task "SEP-Testaufgabe" erstellen
3. Verifizieren dass Task existiert
4. Bewertungen (1-5): Klarheit, Einfachheit, Dokumentation

**E004 - Task finden:**
1. Existierende Tasks suchen
2. Mindestens einen Task lesen
3. Task-Struktur verstehen

**E005 - Memory schreiben:**
1. Memory-System finden
2. Kurzzeit-Eintrag schreiben
3. Langzeit-Eintrag schreiben

**E006 - Memory lesen (Kontext):**
1. Simuliere "Neustart" - was passierte in letzter Session?
2. Langzeit-Infos identifizieren
3. Kontext wiederherstellen

**E007 - Tool nutzen:**
1. Tool-Liste finden
2. Tool auswaehlen und verstehen
3. Tool ausfuehren oder dokumentieren wie

**E008 - Fehler-Recovery:**
1. Backup-System finden
2. Papierkorb/Undo-Mechanismus pruefen
3. Recovery-Workflow dokumentieren

**E009 - Session starten:**
1. Start-Protokoll finden
2. Dokumentierte Schritte folgen
3. Automatisierungsgrad bewerten

**E010 - Gesamteindruck:**
1. System in einem Satz beschreiben
2. Top 3 Staerken + Schwaechen
3. Alle 7 Dimensionen bewerten (1-5)

---

## 7. Bewertungsdimensionen (1-5 Skala)

| Dimension | Beschreibung |
|-----------|-------------|
| D1 Onboarding | Wie schnell kann man loslegen? |
| D2 Navigation | Wie gut findet man sich zurecht? |
| D3 Memory | Wie gut funktioniert Persistenz? |
| D4 Tasks | Wie gut ist Aufgabenverwaltung? |
| D5 Kommunikation | Wie gut ist User-Interaktion? |
| D6 Tools | Wie gut sind Werkzeuge nutzbar? |
| D7 Fehlertoleranz | Wie robust bei Fehlern/Recovery? |

| Wert | Bedeutung |
|------|-----------|
| 1 | Sehr schlecht / Nicht vorhanden |
| 2 | Schlecht / Mangelhaft |
| 3 | Mittel / Akzeptabel |
| 4 | Gut / Ueberdurchschnittlich |
| 5 | Sehr gut / Exzellent |

**Erfolgsstatus pro Test:**

| Status | Code | Bedeutung |
|--------|------|-----------|
| SUCCESS | 2 | Aufgabe vollstaendig erledigt |
| PARTIAL | 1 | Teilweise erledigt oder mit Hilfe |
| FAILED | 0 | Nicht geschafft |
| TIMEOUT | -1 | Zeitlimit ueberschritten |
| BLOCKED | -2 | Nicht testbar (Feature fehlt) |

---

## 8. Zeitmessungen (Metriken-Referenz)

| Metrik | Beschreibung | Einheit |
|--------|-------------|---------|
| T_ORIENT | Zeit bis erste Orientierung | Sekunden |
| T_TASK_CREATE | Zeit fuer Task-Erstellung | Sekunden |
| T_TASK_FIND | Zeit um Task zu finden | Sekunden |
| T_MEMORY_WRITE | Zeit fuer Memory-Eintrag | Sekunden |
| T_MEMORY_READ | Zeit um Memory zu lesen | Sekunden |
| T_TOOL_FIND | Zeit um Tool zu finden | Sekunden |
| T_TOOL_USE | Zeit um Tool zu nutzen | Sekunden |
| T_TOTAL | Gesamtzeit der Aufgabe | Sekunden |

| Zaehlung | Beschreibung |
|----------|-------------|
| N_FILES_TOUCHED | Anzahl beruehrter Dateien |
| N_STEPS | Anzahl Schritte bis Ziel |
| N_TOOLS_USED | Anzahl genutzter Tools |
| N_ERRORS | Anzahl Fehler/Fehlversuche |

---

## 9. Ergebnis-Format

Ergebnisse werden als JSON gespeichert unter: `tests/ERGEBNISSE/<system>/`

**Namenskonvention:**
- B-Tests: `B_TEST_<system>_<datum>.json`
- O-Tests: `O_TEST_<system>_<datum>.json`
- E-Tests: `<PROFIL>_<datum>.json`

**E-Test JSON-Schema:**

```json
{
  "meta": {
    "system": "[SYSTEMNAME]",
    "profile": "STANDARD",
    "tester": "Claude",
    "date": "[DATUM]",
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

## 10. Datenbank

Test-Ergebnisse koennen auch in SQLite gespeichert werden:

- **Schema:** `tests/test_schema.sql`
- **Befuellen:** `python tests/populate_tests.py`
- **Abfragen:** `python tests/query_tests.py`
- **Datenbank:** `tests/test_library.db`

---

## 11. 12 Systemkomponenten (Kategorien)

Jedes System wird in diesen 12 Bereichen geprueft:

| Nr | Kategorie | Beschreibung | B | O | E |
|----|-----------|-------------|---|---|---|
| K01 | BOOT/START | Systemstart, Bootstrap, Init | x | x | x |
| K02 | MEMORY | Kurzzeit, Langzeit, Kontext | x | x | x |
| K03 | TASKS | Aufgabenverwaltung, Prio | x | x | x |
| K04 | TOOLS | Verfuegbare Werkzeuge, Registry | x | x | x |
| K05 | AGENTEN/SKILLS | Agenten, Services, Delegation | x | x | x |
| K06 | LERNEN | Lessons Learned, Verbesserung | x | x | x |
| K07 | SELBSTSTEUERUNG | Daemon, Automatisierung | x | x | - |
| K08 | WARTUNG | Backup, Recovery, Papierkorb | x | x | x |
| K09 | NAVIGATION | Verzeichnisstruktur, Naming, GUI | x | - | x |
| K10 | KOMMUNIKATION | User-Interaktion, Messaging | x | x | x |
| K11 | DOKUMENTATION | SKILL.md, Regelwerke, Guides | x | - | x |
| K12 | SHUTDOWN | Sauberer Abschluss, Persistierung | x | x | x |

---

## 12. Checkliste

### Vor dem Test
- [ ] System-Pfad bekannt
- [ ] Testprofil gewaehlt (QUICK/STANDARD/FULL/OBSERVATION/OUTPUT)
- [ ] System klassifiziert (SKILL/AGENT/TEXT-OS)
- [ ] Zeitmessung vorbereitet

### Waehrend des Tests
- [ ] Startzeit notiert (pro Test und gesamt)
- [ ] Beobachtungen dokumentiert
- [ ] Bei Problemen: Abbruchkriterien beachten

### Nach dem Test
- [ ] JSON-Ergebnis gespeichert unter `tests/ERGEBNISSE/<system>/`
- [ ] TEST_MEMORY.txt aktualisiert (bei mehrteiligen Tests)
- [ ] Bei Vergleich: Synopse aktualisieren (siehe comparation_workflow.md)

---

## 13. Nachbereitung

Nach Abschluss der Tests:
- Alte Testergebnisse archivieren (>30 Tage)
- TEST_MEMORY.txt zuruecksetzen wenn keine laufenden Tests
- Datenbank optimieren: `python -c "import sqlite3; c=sqlite3.connect('test_library.db'); c.execute('VACUUM'); c.close()"`

---

## Verzeichnisstruktur

```
tests/
  BEOBACHTUNG/         B-Tests (B001-B008 + Runner)
  AUSGABE/             O-Tests (O001-O006 + Runner)
  ERFAHRUNG/
    AUFGABEN/          E-Test Aufgabendefinitionen (E001-E010)
    PROMPT_TEMPLATE.txt  Standard-Testprompt fuer Claude
  ERGEBNISSE/          Ergebnisse pro System
    <system>/          JSON-Dateien pro Testlauf
  PROFILE/             Testprofile als JSON
  VERGLEICH/           Synopsen und Vergleiche
  TESTKONZEPT.txt      Ausfuehrliche Testkonzept-Referenz
  SYSTEMKLASSEN_KONZEPT.txt  Klassifizierungsdetails
  test_schema.sql      DB-Schema
  test_library.db      SQLite-Datenbank
  populate_tests.py    DB befuellen
  query_tests.py       DB abfragen
```
