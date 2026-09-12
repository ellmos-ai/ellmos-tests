# Vergleichs-Workflow

> Vergleichende Analyse und Synopse mehrerer LLM-OS-Systeme

**Version:** 1.0 | **Stand:** 2026-01-26 (gepflegt 2026-07-30)
**Quelle:** Konsolidiert aus WORKFLOW_3_SYNOPSE, WORKFLOW_1_SYNTHESE (Phasen 1–3), Synopse-Templates

---

## 1. Übersicht

Dieser Workflow beschreibt den systematischen Vergleich und die Auswertung mehrerer Systeme. Er führt Testergebnisse (`testing_workflow_de.md`) und Feature-Mappings (`feature_mapping_workflow_de.md`) in einer umfassenden Bewertung zusammen.

```
+----------+    +----------+    +----------+    +----------+
| SCHRITT 1|---->| SCHRITT 2|---->| SCHRITT 3|---->| SCHRITT 4|
| Sammeln  |    |Vergleichen|   | Bewerten |    | Synopse  |
+----------+    +----------+    +----------+    +----------+
```

---

## 2. Voraussetzungen

Bevor ein Vergleich stattfinden kann:

- [ ] Alle Zielsysteme erfasst (`feature_mapping_workflow_de.md`, Schritte 1–3)
- [ ] Feature-Datenbank befüllt (`mapping/feature_mapping.db`)
- [ ] Testergebnisse vorhanden (`testing_workflow_de.md`)
  - Mindestanforderung: B-Tests und O-Tests (automatisiert)
  - Ideal: Zusätzlich E-Tests (manuell)

---

## 3. Schritt 1: Daten sammeln

**Aus drei Quellen sammeln:**

| Quelle | Pfad | Inhalt |
|---|---|---|
| Feature Mapping | `mapping/<system>/Features.txt` | Kernkonzepte, Tools, Workflows |
| Testergebnisse | `tests/ERGEBNISSE/<system>/*.json` | B/O/E-Test-Scores |
| Feature DB | `mapping/feature_mapping.db` | Implementierungsstatus |

**Datenbank-Abfragen für schnellen Überblick:**
```bash
cd mapping
python query_db.py matrix     # Feature-Matrix
python query_db.py synopsis   # Automatische Synopse
```

---

## 4. Schritt 2: Feature-Vergleich

**Aktivitäten:**
1. Feature-Matrix erstellen (Welches System bietet welche Features?)
2. Implementierungsstatus systemübergreifend vergleichen
3. Unterschiede identifizieren
4. Gemeinsamkeiten hervorheben

---

## 5. Schritt 3: Bewertung

### 5.1 Dimensionale Bewertung (7 Dimensionen, Skala 1–5)

| Dimension | Fokus |
|---|---|
| D1 Onboarding | Wie schnell findet sich ein neuer Nutzer zurecht? |
| D2 Navigation | Wie gut strukturiert ist die Verzeichnisarchitektur? |
| D3 Memory | Zustands-Persistenz, Kurz- und Langzeitgedächtnis |
| D4 Tasks | Aufgabenverwaltung, Priorisierung, CRUD-Operationen |
| D5 Kommunikation | Interaktion, Feedback-Schleifen, Messaging |
| D6 Tools | Werkzeug-Verfügbarkeit, Dokumentation |
| D7 Fehlertoleranz | Backup, Wiederherstellung, Systemrobustheit |

---

## 6. Schritt 4: Synopse schreiben

Ergebnisse in `tests/VERGLEICH/` als strukturierte Synopse dokumentieren.
