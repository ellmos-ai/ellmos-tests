# Comparation Workflow

> Vergleichende Analyse und Synopse mehrerer LLM-OS-Systeme

**Version:** 1.0 | **Stand:** 2026-01-26
**Quelle:** Konsolidiert aus WORKFLOW_3_SYNOPSE, WORKFLOW_1_SYNTHESE (Phase 1-3), Synopse-Vorlagen

---

## 1. Uebersicht

Dieses Workflow beschreibt den systematischen Vergleich und die Bewertung mehrerer Systeme. Es vereint Testergebnisse (testing_workflow.md) und Feature-Mappings (feature_mapping_workflow.md) zu einer Gesamtbewertung.

```
+----------+    +----------+    +----------+    +----------+
| SCHRITT 1|---->| SCHRITT 2|---->| SCHRITT 3|---->| SCHRITT 4|
| Sammeln  |    |Vergleich |    | Bewerten |    |Synopse   |
+----------+    +----------+    +----------+    +----------+
```

---

## 2. Voraussetzungen

Bevor ein Vergleich moeglich ist:

- [ ] Alle Systeme kartographiert (feature_mapping_workflow.md, Schritte 1-3)
- [ ] Feature-Datenbank befuellt (`mapping/feature_mapping.db`)
- [ ] Testergebnisse vorhanden (testing_workflow.md)
  - Mindestens: B-Tests und O-Tests (automatisiert)
  - Ideal: Auch E-Tests (manuell)

---

## 3. Schritt 1: Daten sammeln

**Sammeln aus drei Quellen:**

| Quelle | Pfad | Inhalt |
|--------|------|--------|
| Feature-Mapping | `mapping/<system>/Features.txt` | Kern-Konzepte, Tools, Workflows |
| Testergebnisse | `tests/ERGEBNISSE/<system>/*.json` | B/O/E-Test Scores |
| Feature-DB | `mapping/feature_mapping.db` | Implementierungsstatus |

**DB-Abfrage fuer Schnelluebersicht:**
```bash
cd mapping
python query_db.py matrix     # Feature-Matrix
python query_db.py synopsis   # Auto-Synopse
```

---

## 4. Schritt 2: Feature-Vergleich

**Aktivitaeten:**
1. Feature-Matrix erstellen (welches System hat was?)
2. Implementierungsstatus pro System vergleichen
3. Unterschiede identifizieren
4. Gemeinsamkeiten finden

**Matrix-Format:**

```
Feature              Sys1      Sys2      Sys3      Sys4
-------------------------------------------------------
CLI                  full      full      none      full
Auto-Logging         none      full      none      full
Task-Manager         JSON      SQLite    JSON      SQLite
Memory Kurzzeit      MD        MD+DB     MD        DB
Memory Langzeit      100+Ber.  archive/  snapshots DB
GUI/Dashboard        Manager   none      ControlCt Streamlit
Daemon/Headless      ja        nein      nein      ja
```

**Implementierungs-Zaehlung:**
```bash
python query_db.py gaps <system>   # Fehlende Features
python query_db.py profile <system> # System-Profil
```

---

## 5. Schritt 3: Bewertung

### 5.1 Dimensionsbewertung (7 Dimensionen, Skala 1-5)

| Dimension | Was wird bewertet |
|-----------|------------------|
| D1 Onboarding | Wie schnell kann man loslegen? SKILL.md-Qualitaet, Getting Started |
| D2 Navigation | Wie gut findet man sich zurecht? Ordnerstruktur, Naming |
| D3 Memory | Persistenz, Kurzzeit/Langzeit, Kontext-Wiederherstellung |
| D4 Tasks | Aufgabenverwaltung, Priorisierung, CRUD |
| D5 Kommunikation | User-Interaktion, Feedback, Messaging |
| D6 Tools | Werkzeug-Verfuegbarkeit, Registry, Dokumentation |
| D7 Fehlertoleranz | Backup, Recovery, Papierkorb, Robustheit |

**Berechnung Gesamtnote:**
```
Gesamtnote = Durchschnitt aller 7 Dimensionen
```

### 5.2 Staerken-Schwaechen-Analyse

Pro System:
- Top 3 Staerken (mit Begruendung)
- Top 3 Schwaechen (mit Begruendung)
- Top 3 Empfehlungen

### 5.3 Systemklassifizierung

Systeme in Klassen einordnen (siehe testing_workflow.md, Abschnitt 2):
- SKILL (einfach)
- AGENT/HUB (mittel)
- TEXT-OS (komplex)

**Wichtig:** Vergleiche nur innerhalb derselben Klasse, oder nutze klassenspezifische Gewichtung!

---

## 6. Schritt 4: Synopse schreiben

### 6.1 Struktur

Die Synopse folgt diesem Aufbau:

1. **Gesamtergebnis** - Ranking-Tabelle (Note, Zeit, Klasse, Charakter)
2. **Systemklassifizierung** - SKILL/AGENT/TEXT-OS Einordnung
3. **Dimensionsvergleich** - 7 Dimensionen im Direktvergleich
4. **Automatisierte Testergebnisse** - B-Test und O-Test Scores
5. **B-Test Detail** - Einzelne B-Test Ergebnisse
6. **O-Test Detail** - Einzelne O-Test Ergebnisse
7. **E-Test Detail** - Einzelne E-Test Ergebnisse (falls vorhanden)
8. **Feature-Matrix** - Implementierungsvergleich
9. **Staerken-Schwaechen-Matrix** - Pro System
10. **Feature-Statistik** - Zaehlung full/partial/none/planned
11. **Einzigartige Features** - Was hat nur dieses System?
12. **Empfehlungen** - Pro System
13. **Feature-Mapping DB** - DB-basierte Analyse (falls vorhanden)
14. **Fazit** - Gesamtsieger, Bester Einstieg, Beste Doku

### 6.2 Vorlage Gesamtergebnis

```
+-------------+----------+---------+-----------+-------------------------------+
| System      | Note     | Zeit    | Klasse    | Charakter                     |
+-------------+----------+---------+-----------+-------------------------------+
| 1. SysA     | X.X/5.0  | MM:SS   | TEXT-OS   | ...                           |
| 2. SysB     | X.X/5.0  | MM:SS   | AGENT/HUB | ...                          |
| 3. SysC     | X.X/5.0  | MM:SS   | TEXT-OS   | ...                           |
+-------------+----------+---------+-----------+-------------------------------+
```

### 6.3 Vorlage Dimensionsvergleich

```
                    Sys1    Sys2    Sys3    Sys4    BEST
                    ----    ----    ----    ----    ----
D1 Onboarding        5       4       3       4    Sys1
D2 Navigation        4       5       4       4    Sys2
D3 Memory            5       3       5       5    Sys1/Sys3
D4 Tasks             5       4       4       5    Sys1/Sys4
D5 Kommunikation     4       4       4       4    Gleich
D6 Tools             5       5       4       5    Sys1/Sys2/Sys4
D7 Fehlertoleranz    4       4       4       4    Gleich
```

### 6.4 Best-of Extraktion

Fuer jedes System dokumentieren, welche Features als "Best-of" uebernommen werden koennten:

```
Von System A uebernehmen:
  - Feature X (Begruendung)
  - Feature Y (Begruendung)

NICHT uebernehmen:
  - Feature Z (zu komplex / veraltet / nicht relevant)
```

---

## 7. Output

### Synopse-Datei

**Ablage:** `tests/VERGLEICH/` oder als eigenstaendige .md-Datei

**Namenskonvention:**
- `SYNOPSE_<Thema>_<Datum>.txt`
- `SYSTEMVERGLEICH_<scope>_<Datum>.md`
- `VERGLEICH_<n>_SYSTEME_<Datum>.md`

**Laenge:** 10-20 KB (ausfuehrlich) oder 3-5 KB (Kurzfassung)

### Fazit-Template

```
GESAMTSIEGER: <System> (<Note>/5.0)
  Begruendung: ...

BESTER EINSTIEG: <System>
  Begruendung: ...

BESTE DOKUMENTATION: <System>
  Begruendung: ...

FUER NEUES SYSTEM (Best-of):
  Kombiniere <SysA> Feature + <SysB> Feature + <SysC> Feature
  Ergebnis: ...
```

---

## 8. Integration mit Synthese (WORKFLOW 1)

Falls nach dem Vergleich ein neues System gebaut werden soll:

| Synthese-Phase | Relevanz | Was wird genutzt |
|---------------|----------|-----------------|
| Phase 1: Datensammlung | Dieses Workflow liefert die Daten | Feature-Maps, Tests, Synopse |
| Phase 2: Architektur | Best-of Extraktion als Input | Welche Features uebernehmen? |
| Phase 3: Dossier | Synopse als Entscheidungsgrundlage | Begruendung der Architektur |
| Phase 4-5: Anpassung | Vergleich als Referenz | Was funktioniert wo am besten? |
| Phase 6-7: Umsetzung | Feature-DB als Checkliste | Alle geplanten Features implementiert? |

---

## 9. Checkliste

### Vor dem Vergleich
- [ ] Alle Systeme kartographiert (feature_mapping_workflow.md)
- [ ] Feature-Matrix erstellt oder DB befuellt
- [ ] Testergebnisse vorhanden (B/O/E)
- [ ] Systeme klassifiziert (SKILL/AGENT/TEXT-OS)

### Waehrend des Vergleichs
- [ ] Feature-Matrix dokumentiert
- [ ] Alle 7 Dimensionen bewertet (1-5)
- [ ] Staerken/Schwaechen pro System identifiziert
- [ ] Best-of Kandidaten markiert

### Nach dem Vergleich
- [ ] Synopse geschrieben und abgelegt
- [ ] Empfehlungen formuliert
- [ ] Fazit mit Ranking erstellt
- [ ] Bei Bedarf: Best-of Extraktion fuer neues System

---

## 10. Verzeichnisstruktur (Gesamt)

```
system_diff_tests/
  testing_workflow.md          <- Wie testen?
  feature_mapping_workflow.md  <- Wie kartographieren?
  comparation_workflow.md      <- Wie vergleichen? (diese Datei)

  tests/                       Alle Testdaten
    BEOBACHTUNG/               B-Test Skripte
    AUSGABE/                   O-Test Skripte
    ERFAHRUNG/                 E-Test Aufgaben + Prompt
    ERGEBNISSE/                Ergebnisse pro System
    PROFILE/                   Testprofile (JSON)
    VERGLEICH/                 Synopsen und Vergleiche
    ...

  mapping/                     Alle Mapping-Daten
    feature_mapping.db         Feature-Datenbank
    populate_db.py             DB befuellen
    query_db.py                DB abfragen
    schema.sql                 DB-Schema
    <system>/                  Pro-System Scans + Features
    ...
```
