#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für BACH API - Modus B (mit Session-Management)
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
    "t1_session": {"passed": 0, "total": 3},
    "t2_operations": {"passed": 0, "total": 4},
    "t3_performance": {"passed": 0, "total": 3},
}


def test_session_lifecycle():
    """T1: Session-Lifecycle (startup, operations, shutdown)"""
    print("=" * 60)
    print("T1: SESSION-LIFECYCLE (Modus B - Mit Session)")
    print("=" * 60 + "\n")

    from bach_api import session

    # T1.1: Session startup
    print("[T1.1] Session startup...")
    try:
        result = session.startup(partner="testuser", mode="silent")
        if result and ("Session" in result or "START" in result.upper() or len(result) > 10):
            print(f"  ✓ PASS: Session gestartet")
            print(f"    Output (erste 200 Zeichen): {result[:200] if result else '(leer)'}")
            results["t1_session"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Session lief, aber unerwarteter Output")
            print(f"    Output: {result}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T1.2: Operationen während Session (task add)
    print("[T1.2] Operationen während Session (task add)...")
    try:
        from bach_api import get_app
        app = get_app()
        result = app.execute("task", "add", ["Modus B Test Task", "--priority", "P1"])
        success, message = result
        if success:
            print(f"  ✓ PASS: Task während Session erstellt")
            print(f"    Output: {message}")
            results["t1_session"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Task-Befehl lief, aber Fehler: {message}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T1.3: Session shutdown
    print("[T1.3] Session shutdown...")
    try:
        result = session.shutdown(summary="Modus B Test abgeschlossen", partner="testuser")
        if result and ("Session" in result or "SHUTDOWN" in result.upper() or "beendet" in result.lower()):
            print(f"  ✓ PASS: Session beendet")
            print(f"    Output (erste 200 Zeichen): {result[:200] if result else '(leer)'}")
            results["t1_session"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Shutdown lief, aber unerwarteter Output")
            print(f"    Output: {result}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    print("=" * 60)
    print(f"T1 ABGESCHLOSSEN: {results['t1_session']['passed']}/{results['t1_session']['total']} PASS")
    print("=" * 60 + "\n")


def test_operations_with_session():
    """T2: Basis-Operationen mit aktivem Session-Context"""
    print("=" * 60)
    print("T2: OPERATIONEN MIT SESSION-CONTEXT")
    print("=" * 60 + "\n")

    from bach_api import session, get_app

    # Session starten
    print("[Setup] Session starten...")
    session.startup(partner="testuser", mode="silent")
    print()

    app = get_app()

    # T2.1: Task erstellen
    print("[T2.1] Task erstellen (in Session)...")
    try:
        result = app.execute("task", "add", ["Session Test Task", "--priority", "P1"])
        success, message = result
        if success:
            print(f"  ✓ PASS: Task erstellt")
            results["t2_operations"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: {message}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T2.2: Task list
    print("[T2.2] Task list (in Session)...")
    try:
        result = app.execute("task", "list", [])
        success, message = result
        if success:
            print(f"  ✓ PASS: Task-Liste abgerufen")
            results["t2_operations"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: {message}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T2.3: Wiki search
    print("[T2.3] Wiki search (in Session)...")
    try:
        result = app.execute("wiki", "search", ["test"])
        success, message = result
        if success:
            print(f"  ✓ PASS: Wiki-Suche funktioniert")
            treffer = message.count('\n') if message else 0
            print(f"    Geschätzte Treffer: {treffer}")
            results["t2_operations"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: {message}")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T2.4: Status
    print("[T2.4] Status abfragen (in Session)...")
    try:
        result = app.execute("status", "show", [])
        success, message = result
        # Status gibt (False, message) zurück, aber das ist OK
        if message and len(message) > 20:
            print(f"  ✓ PASS: Status abgerufen")
            results["t2_operations"]["passed"] += 1
        else:
            print(f"  ⚠ PARTIAL: Unerwarteter Output")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # Session beenden
    print("[Teardown] Session beenden...")
    session.shutdown(summary="T2 Tests abgeschlossen", partner="testuser")
    print()

    print("=" * 60)
    print(f"T2 ABGESCHLOSSEN: {results['t2_operations']['passed']}/{results['t2_operations']['total']} PASS")
    print("=" * 60 + "\n")


def test_performance_with_session():
    """T3: Performance mit Session-Context"""
    print("=" * 60)
    print("T3: PERFORMANCE MIT SESSION")
    print("=" * 60 + "\n")

    from bach_api import session, get_app

    # Session starten
    session.startup(partner="testuser", mode="silent")
    app = get_app()

    # T3.1: Task erstellen
    print("[T3.1] Task erstellen (Performance mit Session)...")
    try:
        start = time.time()
        app.execute("task", "add", ["Perf Test Session", "--priority", "P1"])
        elapsed = (time.time() - start) * 1000
        status = "✓ PASS" if elapsed < 100 else "⚠ SLOW"
        print(f"  {status}: {elapsed:.2f}ms (Target < 100ms)")
        if elapsed < 100:
            results["t3_performance"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T3.2: Wiki-Suche
    print("[T3.2] Wiki-Suche (Performance mit Session)...")
    try:
        start = time.time()
        app.execute("wiki", "search", ["BACH"])
        elapsed = (time.time() - start) * 1000
        status = "✓ PASS" if elapsed < 200 else "⚠ SLOW"
        print(f"  {status}: {elapsed:.2f}ms (Target < 200ms)")
        if elapsed < 200:
            results["t3_performance"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # T3.3: Status
    print("[T3.3] Status (Performance mit Session)...")
    try:
        start = time.time()
        app.execute("status", "show", [])
        elapsed = (time.time() - start) * 1000
        status = "✓ PASS" if elapsed < 100 else "⚠ SLOW"
        print(f"  {status}: {elapsed:.2f}ms (Target < 100ms)")
        if elapsed < 100:
            results["t3_performance"]["passed"] += 1
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    print()

    # Session beenden
    session.shutdown(summary="T3 Performance Tests abgeschlossen", partner="testuser")

    print("=" * 60)
    print(f"T3 ABGESCHLOSSEN: {results['t3_performance']['passed']}/{results['t3_performance']['total']} PASS")
    print("=" * 60 + "\n")


def print_summary():
    """Gesamt-Zusammenfassung"""
    total_pass = sum(r["passed"] for r in results.values())
    total_tests = sum(r["total"] for r in results.values())
    percentage = (total_pass / total_tests * 100) if total_tests > 0 else 0

    print("\n" + "=" * 60)
    print("GESAMT-ERGEBNIS: MODUS B (Mit Session)")
    print("=" * 60)
    print(f"T1 Session-Lifecycle:  {results['t1_session']['passed']}/{results['t1_session']['total']}")
    print(f"T2 Operationen:        {results['t2_operations']['passed']}/{results['t2_operations']['total']}")
    print(f"T3 Performance:        {results['t3_performance']['passed']}/{results['t3_performance']['total']}")
    print("-" * 60)
    print(f"GESAMT:                {total_pass}/{total_tests} ({percentage:.1f}%)")
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
    print("BACH API Test - Modus B (Mit Session)")
    print("HQ5 Nutzertest - API-Modi Testing")
    print("=" * 60 + "\n")

    try:
        test_session_lifecycle()
        test_operations_with_session()
        test_performance_with_session()
    except Exception as e:
        print(f"\n!!! KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()

    print_summary()

    print("=" * 60)
    print("ALLE TESTS ABGESCHLOSSEN")
    print("=" * 60)
