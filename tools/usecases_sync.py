#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""
usecases_sync.py - BACH-UC-Katalog → ellmos-tests/usecases.json
================================================================

Liest die usecases-Tabelle aus BACH/system/data/bach.db (read-only, mode=ro)
und schreibt einen maschinenlesbaren Use-Case-Katalog nach:

    ellmos-tests/usecases.json          (kanonischer Katalog)

Felder je UC:
    id, title, description, module, test_score, last_tested,
    covering_skill, coverage_status

coverage_status / covering_skill stammen aus dem NAIV_FINALAUDIT_2026-06-22.
Das Mapping basiert auf Titel-Vergleich (nicht auf Positions-/ID-Übereinstimmung),
da die Einfüge-Reihenfolge in der DB von der Audit-Nummerierung abweicht.

Hinweis zu zwei UC-Universen
------------------------------
Dieses Skript erzeugt den ANWENDERORIENTIERTEN Katalog (50 UCs aus bach.db:
Kalender, Medikamente, Versicherungen, RPG ...).

Die Datei tests/batteries/usecases_system_legacy.txt enthält den veralteten
SYSTEMORIENTIERTEN Katalog (UC001–UC049, Stand 2026-02-18: ATI-Pipeline, MCP,
DB-Integrität ...). Beide Listen sind thematisch verschieden und dürfen nicht
verwechselt werden.

Nutzung
--------
    python tools/usecases_sync.py [--db PATH] [--out PATH] [--check-only]

Optionen
--------
    --db PATH       Pfad zur bach.db (Standard: auto-detect über ELLMOS_ONEDRIVE
                    oder Windows-/Unix-Default)
    --out PATH      Ausgabepfad für usecases.json (Standard: <modul-root>/usecases.json)
    --check-only    Nur prüfen ob 50 UCs vorhanden, nichts schreiben
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Audit-Mapping: DB-id → (covering_skill, coverage_status)
# Handgeprüft auf Basis von NAIV_FINALAUDIT_2026-06-22.md (Titel-Match).
# OPEN-Einträge haben covering_skill=None.
# ---------------------------------------------------------------------------
AUDIT_MAPPING: dict[int, dict] = {
    1:  {"covering_skill": "bewerbungsexperte",       "coverage_status": "COVERED"},
    2:  {"covering_skill": "folder-flattening",       "coverage_status": "PARTIAL"},
    3:  {"covering_skill": "buero",                   "coverage_status": "COVERED"},
    4:  {"covering_skill": "gesundheit",              "coverage_status": "COVERED"},
    5:  {"covering_skill": "haushalt-manager",        "coverage_status": "COVERED"},
    6:  {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    7:  {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    8:  {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    9:  {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    10: {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    11: {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    12: {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    13: {"covering_skill": "gesundheit",              "coverage_status": "COVERED"},
    14: {"covering_skill": "haushalt-manager",        "coverage_status": "COVERED"},
    15: {"covering_skill": "haushalt-manager",        "coverage_status": "COVERED"},
    16: {"covering_skill": "gesundheit",              "coverage_status": "PARTIAL"},
    17: {"covering_skill": "medizin-daten",           "coverage_status": "COVERED"},
    18: {"covering_skill": "medizin-daten",           "coverage_status": "COVERED"},
    19: {"covering_skill": "medizin-daten",           "coverage_status": "PARTIAL"},
    20: {"covering_skill": "medizin-daten",           "coverage_status": "COVERED"},
    21: {"covering_skill": "medizin-daten",           "coverage_status": "COVERED"},
    22: {"covering_skill": "gesundheit",              "coverage_status": "PARTIAL"},
    23: {"covering_skill": "gesundheit",              "coverage_status": "PARTIAL"},
    24: {"covering_skill": "gesundheit",              "coverage_status": "PARTIAL"},
    25: {"covering_skill": "dossier-briefing",        "coverage_status": "COVERED"},
    26: {"covering_skill": "location-suche",          "coverage_status": "COVERED"},
    27: {"covering_skill": "reiseroute",              "coverage_status": "COVERED"},
    28: {"covering_skill": "kalender",                "coverage_status": "PARTIAL"},
    29: {"covering_skill": "kalender",                "coverage_status": "COVERED"},
    30: {"covering_skill": "build-your-users-mind",   "coverage_status": "PARTIAL"},
    31: {"covering_skill": "haushalt-manager",        "coverage_status": "COVERED"},
    32: {"covering_skill": "finanz-versicherung",     "coverage_status": "COVERED"},
    33: {"covering_skill": "selbstmanagement",        "coverage_status": "COVERED"},
    34: {"covering_skill": "selbstmanagement",        "coverage_status": "COVERED"},
    35: {"covering_skill": "selbstmanagement",        "coverage_status": "PARTIAL"},
    36: {"covering_skill": "selbstmanagement",        "coverage_status": "COVERED"},
    37: {"covering_skill": "gesundheit",              "coverage_status": "PARTIAL"},
    38: {"covering_skill": "notizblock",              "coverage_status": "PARTIAL"},
    39: {"covering_skill": "foerderplaner",           "coverage_status": "PARTIAL"},
    40: {"covering_skill": None,                      "coverage_status": "PARTIAL"},
    41: {"covering_skill": "formbuilder-reader",      "coverage_status": "COVERED"},
    42: {"covering_skill": "hauslagerist-reader",     "coverage_status": "COVERED"},
    43: {"covering_skill": None,                      "coverage_status": "OPEN"},
    44: {"covering_skill": "haushalt-manager",        "coverage_status": "COVERED"},
    45: {"covering_skill": "gesundheit",              "coverage_status": "COVERED"},
    46: {"covering_skill": "mediabrain-reader",       "coverage_status": "COVERED"},
    47: {"covering_skill": None,                      "coverage_status": "OPEN"},
    48: {"covering_skill": "rpg",                     "coverage_status": "COVERED"},
    49: {"covering_skill": None,                      "coverage_status": "OPEN"},
    50: {"covering_skill": None,                      "coverage_status": "OPEN"},
}

EXPECTED_COUNT = 50


def _find_db() -> Path:
    """Sucht bach.db über Umgebungsvariable oder Windows/Unix-Default."""
    onedrive = os.environ.get("ELLMOS_ONEDRIVE") or os.environ.get("OneDrive")
    candidates = []
    if onedrive:
        candidates.append(
            Path(onedrive) / ".TOPICS" / ".AI" / ".OS" / "BACH" / "system" / "data" / "bach.db"
        )
    candidates += [
        Path.home() / "OneDrive" / ".TOPICS" / ".AI" / ".OS" / "BACH" / "system" / "data" / "bach.db",
        Path("C:/Users/lukas/OneDrive/.TOPICS/.AI/.OS/BACH/system/data/bach.db"),
        Path("C:/Users/User/OneDrive/.TOPICS/.AI/.OS/BACH/system/data/bach.db"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "bach.db nicht gefunden. Pfad via --db angeben oder ELLMOS_ONEDRIVE setzen."
    )


def _read_usecases(db_path: Path) -> list[dict]:
    """Liest alle Usecases aus bach.db (read-only, kein bach_api-Import)."""
    uri = db_path.as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, title, description, workflow_name, test_score, last_tested "
            "FROM usecases ORDER BY id"
        )
        rows = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
    return rows


def _build_catalog(rows: list[dict]) -> list[dict]:
    """Baut den JSON-Katalog mit covering_skill und coverage_status."""
    catalog = []
    for row in rows:
        db_id = row["id"]
        mapping = AUDIT_MAPPING.get(db_id, {})
        entry = {
            "id":               db_id,
            "title":            row["title"] or "",
            "description":      row["description"] or "",
            "module":           row["workflow_name"] or "",
            "test_score":       row["test_score"] if row["test_score"] is not None else 0,
            "last_tested":      row["last_tested"] or None,
            "covering_skill":   mapping.get("covering_skill"),
            "coverage_status":  mapping.get("coverage_status", "UNKNOWN"),
        }
        catalog.append(entry)
    return catalog


def _validate(catalog: list[dict]) -> list[str]:
    """Prüft Vollständigkeit des Katalogs und Mappings. Gibt Fehler-/Warnliste zurück."""
    errors = []
    ids_in_catalog = {e["id"] for e in catalog}

    # Alle 50 DB-IDs müssen vorhanden sein
    if len(catalog) != EXPECTED_COUNT:
        errors.append(f"Erwartet {EXPECTED_COUNT} UCs, gefunden {len(catalog)}")

    # Jede Mapping-ID muss im Katalog auftauchen
    unmapped = set(AUDIT_MAPPING.keys()) - ids_in_catalog
    if unmapped:
        errors.append(f"Mapping-IDs ohne DB-Eintrag: {sorted(unmapped)}")

    # Kein UC darf status UNKNOWN haben (alle müssen gemappt sein)
    unknown = [e["id"] for e in catalog if e["coverage_status"] == "UNKNOWN"]
    if unknown:
        errors.append(f"UCs ohne Audit-Mapping (UNKNOWN): {unknown}")

    return errors


def _stats(catalog: list[dict]) -> dict:
    """Zählt COVERED/PARTIAL/OPEN und with_covering_skill."""
    counts: dict[str, int] = {"COVERED": 0, "PARTIAL": 0, "OPEN": 0, "UNKNOWN": 0}
    with_skill = 0
    for e in catalog:
        status = e["coverage_status"]
        counts[status] = counts.get(status, 0) + 1
        if e["covering_skill"] is not None:
            with_skill += 1
    return {
        "total": len(catalog),
        "covered": counts["COVERED"],
        "partial": counts["PARTIAL"],
        "open": counts["OPEN"],
        "with_covering_skill": with_skill,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db",  help="Pfad zur bach.db")
    parser.add_argument("--out", help="Ausgabepfad für usecases.json")
    parser.add_argument("--check-only", action="store_true", help="Nur prüfen, nichts schreiben")
    args = parser.parse_args()

    # DB-Pfad auflösen
    db_path = Path(args.db) if args.db else _find_db()
    print(f"DB:  {db_path}")

    # Ausgabepfad: Standard = Modul-Root (Elternverzeichnis von tools/)
    module_root = Path(__file__).parent.parent
    out_path = Path(args.out) if args.out else module_root / "usecases.json"

    # Daten lesen
    rows = _read_usecases(db_path)
    catalog = _build_catalog(rows)

    # Validierung
    errors = _validate(catalog)
    if errors:
        for e in errors:
            print(f"FEHLER: {e}", file=sys.stderr)
        return 1

    stats = _stats(catalog)
    print(
        f"UCs: {stats['total']} total | "
        f"{stats['covered']} COVERED | "
        f"{stats['partial']} PARTIAL | "
        f"{stats['open']} OPEN | "
        f"{stats['with_covering_skill']} mit covering_skill"
    )

    if args.check_only:
        print("--check-only: keine Datei geschrieben.")
        return 0

    # JSON schreiben
    payload = {
        "_meta": {
            "generator":    "tools/usecases_sync.py",
            "source_db":    str(db_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "audit_source": "NAIV_FINALAUDIT_2026-06-22.md",
            "note": (
                "Anwenderorientierter BACH-Use-Case-Katalog (50 UCs). "
                "Nicht verwechseln mit tests/batteries/usecases_system_legacy.txt "
                "(systemorientiert, UC001-UC049, Stand 2026-02-18)."
            ),
        },
        "stats": stats,
        "usecases": catalog,
    }
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"OUT: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
