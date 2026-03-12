# Feature Mapping Workflow

> System-Kartographie, Feature-Erfassung und Datenbank-Verwaltung

**Version:** 1.0 | **Stand:** 2026-01-26
**Quelle:** Konsolidiert aus WORKFLOW_2_MAPPING, populate_db.py, query_db.py, schema.sql

---

## 1. Uebersicht

Dieses Workflow beschreibt die systematische Erfassung und strukturierte Speicherung von System-Features in einer SQLite-Datenbank. Es dient als Grundlage fuer Vergleiche (siehe comparation_workflow.md).

```
+----------+    +----------+    +----------+    +----------+
| SCHRITT 1|---->| SCHRITT 2|---->| SCHRITT 3|---->| SCHRITT 4|
| Dir-Scan |    | Features |    | Datenbank|    |   Diff   |
+----------+    +----------+    +----------+    +----------+
```

---

## 2. Schritt 1: Directory-Scan

**Ziel:** Vollstaendige Ordnerstruktur eines Systems erfassen

**Methode:**
- Claude: `fc_list_directory(<system_root>, depth=3)`
- CLI: `tree /F <system_root>` (Windows) oder `find <system_root> -maxdepth 3` (Unix)

**Output:** `mapping/<system>/directory-scan.txt`

**Format:**
```
<system>/
+-- ordner1/
|   +-- datei1.txt
|   +-- datei2.json
+-- ordner2/
```

**Tipps:**
- depth=2 fuer Uebersicht, depth=3 fuer Details
- Grosse Ordner (>50 Dateien) separat scannen

---

## 3. Schritt 2: Feature-Analyse

**Ziel:** Funktionen und Konzepte eines Systems identifizieren

**Aktivitaeten:**
1. SKILL.md / Entry Point lesen
2. Kern-Konzepte extrahieren
3. Tools/Befehle dokumentieren
4. Registries auflisten
5. Workflows verstehen

**Output:** `mapping/<system>/Features.txt`

**Format:**
```
===========================
SYSTEM: <name>
===========================

KERN-KONZEPTE:
1. Konzept A - Beschreibung
2. Konzept B - Beschreibung

TOOLS:
- tool1: Funktion
- tool2: Funktion

WORKFLOWS:
- Startup: ...
- Shutdown: ...
```

---

## 4. Schritt 3: Datenbank befuellen

**Ziel:** Features strukturiert in SQLite speichern

**Datenbank:** `mapping/feature_mapping.db`

### Schema (8 Tabellen)

| Tabelle | Zweck |
|---------|-------|
| `systems` | Registrierte Systeme (Name, Pfad, Klasse, Version) |
| `feature_categories` | Feature-Kategorien (Boot, Memory, Tasks, etc.) |
| `features` | Feature-Definitionen (Name, Kategorie, Beschreibung) |
| `feature_aliases` | Alternative Bezeichnungen fuer Features |
| `implementations` | Implementierungsstatus pro System+Feature |
| `ratings` | Bewertungen pro System+Feature |
| `file_fingerprints` | Datei-Fingerprints fuer Aenderungserkennung |
| `synopses` | Gespeicherte Vergleichstexte |

**Schema-Datei:** `mapping/schema.sql`

### Befuellen

```bash
cd mapping
python populate_db.py
```

**Was populate_db.py tut:**
- Initialisiert DB mit Schema
- Legt Systeme an (mit Pfad, Klasse, Version)
- Definiert 39 Features in 8 Kategorien
- Erstellt 43 Feature-Aliase
- Erfasst 63 Implementierungen mit Status (full/partial/none/planned)
- Berechnet Ratings

**WICHTIG:** Der DB-Pfad in populate_db.py und query_db.py muss ggf. angepasst werden:
```python
# Aktuell hardcoded - bei Bedarf aendern:
DB_PATH = r'<Pfad>\feature_mapping.db'
```

### Abfragen

```bash
cd mapping
python query_db.py matrix              # Feature-Matrix aller Systeme
python query_db.py synopsis            # Automatische Synopse
python query_db.py gaps <system>       # Feature-Luecken eines Systems
python query_db.py alias <suchbegriff> # Feature-Alias suchen
python query_db.py tech <system>       # Technologie-Stack
python query_db.py profile <system>    # System-Profil
```

### Feature-Kategorien

| Kategorie | Beispiel-Features |
|-----------|------------------|
| BOOT/START | Auto-Startup, Session-Lifecycle, Partner-System |
| MEMORY | Kurzzeit, Langzeit, Lessons Learned, Sessions |
| TASKS | Task-Manager, Priorisierung, Hierarchische Tasks |
| TOOLS | Tool-Registry, CLI, Python-Scripts |
| AGENTEN | Multi-Agent, Delegation, Spezialisierung |
| AUTOMATION | Daemon, Scanner, Injektoren, Recurring |
| WARTUNG | Backup, Restore, Papierkorb, Selbstheilung |
| DOKUMENTATION | SKILL.md, Help-System, GUI/Dashboard |

### Implementierungs-Status

| Status | Bedeutung |
|--------|-----------|
| `full` | Vollstaendig implementiert |
| `partial` | Teilweise implementiert |
| `none` | Nicht implementiert |
| `planned` | Geplant / in Entwicklung |

---

## 5. Schritt 4: Diff erstellen

**Ziel:** Aenderungen seit letztem Scan erkennen

**Aktivitaeten:**
1. Alten Scan laden
2. Neuen Scan erstellen
3. Differenzen berechnen
4. Aenderungen dokumentieren

**Output:** `mapping/<system>/scan-diff.txt`

**Format:**
```
AENDERUNGEN seit <datum>:

+ NEU:
  - /ordner/neue_datei.txt

- GELOESCHT:
  - /ordner/alte_datei.txt

~ GEAENDERT:
  - /ordner/datei.txt (Groesse: 1KB -> 2KB)
```

---

## 6. Wartung

### Veraltete Daten
- Veraltete Scans ueberschreiben (nicht archivieren)
- Nicht mehr existierende Systeme aus DB entfernen
- Datenbank-Backup erstellen vor groesseren Aenderungen

### Datenbank optimieren
```bash
python -c "import sqlite3; c=sqlite3.connect('feature_mapping.db'); c.execute('VACUUM'); c.close()"
```

---

## 7. Checkliste

### Pro System
- [ ] Ordner `mapping/<system>/` existiert
- [ ] `directory-scan.txt` aktuell
- [ ] `Features.txt` vollstaendig
- [ ] Datenbank-Eintraege vorhanden
- [ ] `scan-diff.txt` (falls Update)

### Gesamt
- [ ] Alle zu vergleichenden Systeme kartographiert
- [ ] Feature-Datenbank befuellt
- [ ] DB-Pfade in Scripts korrekt
- [ ] Bereit fuer Vergleich (-> comparation_workflow.md)

---

## 8. Verzeichnisstruktur

```
mapping/
  feature_mapping.db               SQLite-Datenbank
  schema.sql                       DB-Schema Definition
  populate_db.py                   DB initialisieren + befuellen
  query_db.py                      DB abfragen (6 Befehle)
  FEATURE_VERGLEICH_ALLE_SYSTEME.txt  Feature-Matrix als Text

  <system>/                        Pro System:
    directory-scan.txt             Ordnerstruktur
    Features.txt                   Feature-Analyse
    scan-diff.txt                  Aenderungen seit letztem Scan
    DOCS/                          Zusaetzliche Dokumentation
```
