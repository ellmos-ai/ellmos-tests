#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQ6 Test 1: Snapshot erstellen.

Manuelles Skript, kein pytest-Test: Es braucht eine echte BACH-Installation und
schreibt in sie hinein. Aufruf::

    python testing/test_hq6_snapshot.py

Der Systempfad wird ueber system_diff_tests.config aufgeloest (frueher lag hier
ein hartkodierter Geschwisterpfad, der nach dem Modulumzug ins Leere zeigte und
die pytest-Collection abbrechen liess). Ohne erreichbare Installation endet das
Skript mit einem Hinweis statt mit einem Import-Fehler.
"""
import sys
from pathlib import Path

SYSTEM_NAME = "BACH_strawberry"
SNAPSHOT_NAME = "test_snapshot_hq6_runde27"


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from system_diff_tests.config import get_system_path

    root = get_system_path(SYSTEM_NAME)
    if not (root / "system" / "core").is_dir():
        print(f"SKIP: {SYSTEM_NAME} nicht gefunden unter {root}")
        return 0

    sys.path.insert(0, str(root / "system"))
    from core.distribution import DistributionManager

    dm = DistributionManager(root)
    print("Creating snapshot...")
    try:
        snapshot_id = dm.create_snapshot(SNAPSHOT_NAME)
        print(f"OK: Snapshot created: {snapshot_id}")
        return 0
    except Exception as exc:  # pragma: no cover - haengt an der Zielinstallation
        print(f"FEHLER: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
