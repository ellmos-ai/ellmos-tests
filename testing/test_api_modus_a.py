#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für BACH API - Modus A (Synchron)
HQ5 Nutzertest - Modus A/B Testing
Erstellt: 2026-02-21, Runde 27
"""

import time
from pathlib import Path
import sys
import os

# BACH-API laden (aus Strawberry)
# Pfad wird ueber BACH_SYSTEM_PATH env-var oder zentrale Config aufgeloest
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from system_diff_tests.config import get_bach_system_path

_default_bach = str(get_bach_system_path("BACH_strawberry"))
STRAWBERRY_PATH = Path(os.environ.get("BACH_SYSTEM_PATH", _default_bach))
if str(STRAWBERRY_PATH) not in sys.path:
    sys.path.insert(0, str(STRAWBERRY_PATH))

# Test-Ergebnisse
results = {
    "t1_basis": {"passed": 0, "total": 6},
    "t2_fehler": {"passed": 0, "total": 4},
    "t3_performance": {"passed": 0, "total": 3},
}


def test_basis_funktionen():
    """T1.1 - T1.6: Basis-Funktionen"""
    print("=" * 60)
    print("T1: BASIS-FUNKTIONEN (Modus A - Synchron)")
    print("=" * 60 + "\n")

    from bach_api import get_app

    # T1.1: Task erstellen
    print("[T1.1] Task erstellen...")
    try:
        # Nutze execute direkt, da add() eventuell CLI-Args erwartet
        from bach_api import get_app
        app = get_app()
        result = app.execute("task", "add", ["API Test Task - Modus A", "--priority", "P1", "--category", "testing"])
        print(f"  ✓ PASS: Task erstellt")
        print(f"    Output: {result if result else '(kein Output)'}")
        results["t1_basis"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T1.2: Task abrufen (list)
    print("[T1.2] Task abrufen (list)...")
    try:
        from bach_api import get_app
        app = get_app()
        result = app.execute("task", "list", [])
        print(f"  ✓ PASS: Task list funktioniert")
        print(f"    Anzahl Tasks: {result.count('│') if result else 0}")  # Grobe Schätzung
        results["t1_basis"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T1.3: Task als erledigt markieren (skip - würde Test-Task erledigen)
    print("[T1.3] Task erledigen... (SKIP - würde produktive Tasks beeinflussen)")
    print()

    # T1.4: Memory schreiben
    print("[T1.4] Memory schreiben...")
    try:
        from bach_api import get_app
        app = get_app()
        result = app.execute("mem", "write", ["API Test Memory - Modus A - Kategorie: testing"])
        print(f"  ✓ PASS: Memory geschrieben")
        print(f"    Output: {result if result else '(kein Output)'}")
        results["t1_basis"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T1.5: Memory lesen
    print("[T1.5] Memory lesen...")
    try:
        from bach_api import get_app
        app = get_app()
        result = app.execute("mem", "read", [])
        if result and "API Test Memory" in result:
            print(f"  ✓ PASS: Memory gelesen, Test-Eintrag gefunden")
            results["t1_basis"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Memory gelesen, aber Test-Eintrag nicht gefunden")
            print(f"    Output (erste 200 Zeichen): {result[:200] if result else '(leer)'}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T1.6: Wiki durchsuchen
    print("[T1.6] Wiki durchsuchen...")
    try:
        from bach_api import get_app
        app = get_app()
        result = app.execute("wiki", "search", ["BACH"])
        if result and ("Treffer" in result or "│" in result):
            print(f"  ✓ PASS: Wiki-Suche funktioniert")
            # Zähle Zeilen mit │ (Tabellentrenner)
            lines = result.split('\n') if result else []
            result_lines = [l for l in lines if '│' in l and not l.strip().startswith('─')]
            print(f"    Geschätzte Treffer: {len(result_lines)}")
            results["t1_basis"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Wiki-Suche lief, aber unerwartetes Format")
            print(f"    Output (erste 200 Zeichen): {result[:200] if result else '(leer)'}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    print("=" * 60)
    print(f"T1 ABGESCHLOSSEN: {results['t1_basis']['passed']}/{results['t1_basis']['total']} PASS")
    print("=" * 60 + "\n")


def test_fehlerbehandlung():
    """T2.1 - T2.4: Fehlerbehandlung"""
    print("=" * 60)
    print("T2: FEHLERBEHANDLUNG")
    print("=" * 60 + "\n")

    from bach_api import get_app

    # T2.1: Ungültige Task-ID (schwer zu testen ohne interne Details)
    print("[T2.1] Ungültige Task-ID... (SKIP - schwer isoliert zu testen)")
    print()

    # T2.2: DB nicht erreichbar (würde System beschädigen)
    print("[T2.2] DB nicht erreichbar... (SKIP - zu destruktiv)")
    print()

    # T2.3: Leerer Memory-Text
    print("[T2.3] Leerer Memory-Text...")
    try:
        app = get_app()
        result = app.execute("mem", "write", [""])
        # Wenn kein Fehler, dann ist Validation nicht streng
        print(f"  ⚠ INFO: Leerer Text wurde akzeptiert (keine strenge Validation)")
        print(f"    Output: {result if result else '(kein Output)'}")
    except Exception as e:
        print(f"  ✓ PASS: Validation-Error wie erwartet: {e}")
        results["t2_fehler"]["passed"] += 1
    print()

    # T2.4: Wiki-Suche ohne Treffer
    print("[T2.4] Wiki-Suche ohne Treffer...")
    try:
        app = get_app()
        result = app.execute("wiki", "search", ["XYZXYZXYZ_NONEXISTENT_TERM_12345"])
        if result and ("Keine Treffer" in result or "0 Treffer" in result or len(result) < 50):
            print(f"  ✓ PASS: Keine Treffer, kein Crash")
            results["t2_fehler"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Suche lief, aber unklar ob Treffer")
            print(f"    Output (erste 100 Zeichen): {result[:100] if result else '(leer)'}")
    except Exception as e:
        print(f"  ✗ FAIL: Exception bei No-Results-Suche: {e}")
    print()

    print("=" * 60)
    print(f"T2 ABGESCHLOSSEN: {results['t2_fehler']['passed']}/{results['t2_fehler']['total']} PASS")
    print("=" * 60 + "\n")


def test_performance():
    """T3.1 - T3.3: Performance"""
    print("=" * 60)
    print("T3: PERFORMANCE")
    print("=" * 60 + "\n")

    from bach_api import get_app

    # T3.1: Task erstellen
    print("[T3.1] Task erstellen (Performance)...")
    try:
        app = get_app()
        start = time.time()
        app.execute("task", "add", ["Perf Test Task", "--priority", "P1"])
        elapsed = (time.time() - start) * 1000
        status = "✓ PASS" if elapsed < 100 else "⚠ SLOW"
        print(f"  {status}: {elapsed:.2f}ms (Target < 100ms)")
        if elapsed < 100:
            results["t3_performance"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T3.2: Memory lesen
    print("[T3.2] Memory lesen (Performance)...")
    try:
        app = get_app()
        start = time.time()
        app.execute("mem", "read", ["--limit", "10"])
        elapsed = (time.time() - start) * 1000
        status = "✓ PASS" if elapsed < 50 else "⚠ SLOW"
        print(f"  {status}: {elapsed:.2f}ms (Target < 50ms)")
        if elapsed < 50:
            results["t3_performance"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T3.3: Wiki-Suche
    print("[T3.3] Wiki-Suche (Performance)...")
    try:
        app = get_app()
        start = time.time()
        app.execute("wiki", "search", ["BACH", "--limit", "100"])
        elapsed = (time.time() - start) * 1000
        status = "✓ PASS" if elapsed < 200 else "⚠ SLOW"
        print(f"  {status}: {elapsed:.2f}ms (Target < 200ms)")
        if elapsed < 200:
            results["t3_performance"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    print("=" * 60)
    print(f"T3 ABGESCHLOSSEN: {results['t3_performance']['passed']}/{results['t3_performance']['total']} PASS")
    print("=" * 60 + "\n")


def print_summary():
    """Gesamt-Zusammenfassung"""
    total_pass = sum(r["passed"] for r in results.values())
    total_tests = sum(r["total"] for r in results.values())
    percentage = (total_pass / total_tests * 100) if total_tests > 0 else 0

    print("\n" + "=" * 60)
    print("GESAMT-ERGEBNIS: MODUS A (Synchron)")
    print("=" * 60)
    print(f"T1 Basis-Funktionen:  {results['t1_basis']['passed']}/{results['t1_basis']['total']}")
    print(f"T2 Fehlerbehandlung:  {results['t2_fehler']['passed']}/{results['t2_fehler']['total']}")
    print(f"T3 Performance:       {results['t3_performance']['passed']}/{results['t3_performance']['total']}")
    print("-" * 60)
    print(f"GESAMT:               {total_pass}/{total_tests} ({percentage:.1f}%)")
    print("=" * 60)

    if percentage >= 75:
        print("BEWERTUNG: EXCELLENT ✓")
    elif percentage >= 50:
        print("BEWERTUNG: GOOD ✓")
    elif percentage >= 30:
        print("BEWERTUNG: ACCEPTABLE ~")
    else:
        print("BEWERTUNG: NEEDS WORK ✗")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BACH API Test - Modus A (Synchron)")
    print("HQ5 Nutzertest - API-Modi Testing")
    print("=" * 60 + "\n")

    try:
        test_basis_funktionen()
        test_fehlerbehandlung()
        test_performance()
    except Exception as e:
        print(f"\n!!! KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()

    print_summary()

    print("=" * 60)
    print("ALLE TESTS ABGESCHLOSSEN")
    print("=" * 60)
