# Feature-Mapping-Workflow

> Systemkartographie, Feature-Erfassung und Datenbank-Verwaltung

**Version:** 1.0 | **Stand:** 2026-01-26 (gepflegt 2026-07-30)
**Quelle:** Konsolidiert aus WORKFLOW_2_MAPPING, `populate_db.py`, `query_db.py`, `schema.sql`

---

## 1. Übersicht

Dieser Workflow beschreibt die systematische Erfassung und strukturierte Speicherung von Systemfeatures in einer SQLite-Datenbank. Er dient als Grundlage für systemübergreifende Vergleiche (siehe `comparation_workflow_de.md`).

```
+----------+    +----------+    +----------+    +----------+
| SCHRITT 1|---->| SCHRITT 2|---->| SCHRITT 3|---->| SCHRITT 4|
| Verz-Scan|    | Features |    | Datenbank|    |   Diff   |
+----------+    +----------+    +----------+    +----------+
```

---

## 2. Schritt 1: Verzeichnisscan

**Ziel:** Vollständige Ordnerstruktur eines Systems erfassen.

**Ausgabe:** `mapping/<system>/directory-scan.txt`

---

## 3. Schritt 2: Feature-Analyse

**Ziel:** Funktionalitäten und Architekturkonzepte identifizieren.

**Ausgabe:** `mapping/<system>/Features.txt`

---

## 4. Schritt 3: Datenbank befüllen

**Ziel:** Erfasste Features in strukturierter SQLite-Form speichern (`mapping/feature_mapping.db`).

```bash
cd mapping
python populate_db.py
python query_db.py matrix
```
