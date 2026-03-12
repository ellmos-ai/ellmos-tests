"""
Automatisierter DB-Integritäts-Tester (SQ027)
Führt DB001-DB015 + DT001-DT017 aus und speichert Ergebnisse.

Ausführung: python tests/run_db_tests.py [--battery db_integrity|dist_type|all]
"""

import sqlite3
import json
from datetime import datetime
import argparse
import sys
import io
from pathlib import Path

# Windows-Encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\User\OneDrive\.AI\BACH_v2_vanilla\system\data\bach.db'
RESULTS_DIR = Path(__file__).parent / 'results'

# ============================================================
# TEST-DEFINITIONEN
# ============================================================

DB_INTEGRITY_TESTS = [
    ("DB001", "Schema", "Tabellenzahl >= 130",
     "SELECT COUNT(*) FROM sqlite_master WHERE type='table'",
     lambda r: r[0][0] >= 130, lambda r: f"{r[0][0]} Tabellen"),

    ("DB002a", "Schema", "skills Tabelle vorhanden",
     "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='skills'",
     lambda r: r[0][0] == 1, lambda r: "OK" if r[0][0] else "FEHLT"),

    ("DB002b", "Schema", "dist_type_defaults vorhanden",
     "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dist_type_defaults'",
     lambda r: r[0][0] == 1, lambda r: "OK" if r[0][0] else "FEHLT"),

    ("DB002c", "Schema", "distribution_snapshots vorhanden",
     "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='distribution_snapshots'",
     lambda r: r[0][0] == 1, lambda r: "OK" if r[0][0] else "FEHLT"),

    ("DB002d", "Schema", "instance_identity vorhanden",
     "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='instance_identity'",
     lambda r: r[0][0] == 1, lambda r: "OK" if r[0][0] else "FEHLT"),

    ("DB004a", "dist_type", "skills: nur gültige dist_type Werte",
     "SELECT COUNT(*) FROM skills WHERE dist_type NOT IN (0,1,2)",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} ungültige Werte"),

    ("DB004b", "dist_type", "tools: nur gültige dist_type Werte",
     "SELECT COUNT(*) FROM tools WHERE dist_type NOT IN (0,1,2)",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} ungültige Werte"),

    ("DB005", "dist_type", "skills: CORE > 700",
     "SELECT COUNT(*) FROM skills WHERE dist_type=2",
     lambda r: r[0][0] > 700, lambda r: f"{r[0][0]} CORE-Skills"),

    ("DB006", "dist_type", "tools: CORE > 200",
     "SELECT COUNT(*) FROM tools WHERE dist_type=2",
     lambda r: r[0][0] > 200, lambda r: f"{r[0][0]} CORE-Tools"),

    ("DB007", "dist_type", "tasks: USER > 900",
     "SELECT COUNT(*) FROM tasks WHERE dist_type=0",
     lambda r: r[0][0] > 900, lambda r: f"{r[0][0]} USER-Tasks"),

    ("DB013", "Daten", "dist_type_defaults: >= 160 Einträge",
     "SELECT COUNT(*) FROM dist_type_defaults",
     lambda r: r[0][0] >= 160, lambda r: f"{r[0][0]} Einträge"),

    ("DB011", "Daten", "skills: keine NULL-Pflichtfelder",
     "SELECT COUNT(*) FROM skills WHERE name IS NULL OR path IS NULL",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} NULL-Felder"),

    ("DB012", "Daten", "tools: keine NULL-Namen",
     "SELECT COUNT(*) FROM tools WHERE name IS NULL",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} NULL-Namen"),
]

DIST_TYPE_TESTS = [
    ("DT001", "skills", "Extension-Skills (außer 4 Templates) = USER=0",
     "SELECT COUNT(*) FROM skills WHERE path LIKE 'C:%' AND dist_type != 0 AND name NOT IN ('FavExtract','MetaWiki','SQLiteViewer','UniversalCompiler')",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT002", "skills", "Template-Extensions = TEMPLATE=1",
     "SELECT COUNT(*) FROM skills WHERE name IN ('FavExtract','MetaWiki','SQLiteViewer','UniversalCompiler') AND dist_type != 1",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT003", "skills", "Foerderplaner = USER=0",
     "SELECT COUNT(*) FROM skills WHERE path LIKE 'agents/_experts/foerderplaner%' AND dist_type != 0",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT004", "skills", "Worksheet-Generator = USER=0",
     "SELECT COUNT(*) FROM skills WHERE path LIKE 'agents/_experts/worksheet_generator%' AND dist_type != 0",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT005", "skills", "recludos.md = USER=0",
     "SELECT dist_type FROM skills WHERE path = 'skills/_os/recludos.md'",
     lambda r: len(r) > 0 and r[0][0] == 0, lambda r: f"dist_type={r[0][0] if r else 'NICHT GEFUNDEN'}"),

    ("DT006", "skills", "copilot.md (lowercase) = USER=0",
     "SELECT dist_type FROM skills WHERE path = 'skills/_templates/copilot.md'",
     lambda r: len(r) > 0 and r[0][0] == 0, lambda r: f"dist_type={r[0][0] if r else 'NICHT GEFUNDEN'}"),

    ("DT007", "skills", "skills/_protocols/ = CORE=2",
     "SELECT COUNT(*) FROM skills WHERE path LIKE 'skills/_protocols/%' AND dist_type != 2",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT010", "tools", "Externe Tools = TEMPLATE=1",
     "SELECT COUNT(*) FROM tools WHERE type='external' AND dist_type != 1",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT011", "tools", "Steuer-Tools (category) = USER=0",
     "SELECT COUNT(*) FROM tools WHERE category='steuer' AND dist_type != 0",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT012", "tools", "Steuer-Pfad = USER=0",
     "SELECT COUNT(*) FROM tools WHERE path LIKE 'tools/steuer/%' AND dist_type != 0",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} falsch klassifiziert"),

    ("DT017", "defaults", "dist_type_defaults: keine Duplikate",
     "SELECT COUNT(*) FROM (SELECT path FROM dist_type_defaults GROUP BY path HAVING COUNT(*) > 1)",
     lambda r: r[0][0] == 0, lambda r: f"{r[0][0]} Duplikate"),
]


def run_tests(conn, tests, battery_name):
    """Führt eine Liste von Tests aus und gibt Ergebnisse zurück."""
    c = conn.cursor()
    results = []
    passed = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"  Batterie: {battery_name}")
    print(f"{'='*60}")

    for test_id, category, description, sql, check_fn, format_fn in tests:
        try:
            c.execute(sql)
            rows = c.fetchall()
            passed_test = check_fn(rows)
            detail = format_fn(rows)
            status = "PASS" if passed_test else "FAIL"
            if passed_test:
                passed += 1
            else:
                failed += 1

            symbol = "✓" if passed_test else "✗"
            print(f"  {symbol} [{test_id}] {description}: {detail}")

            results.append({
                "id": test_id,
                "category": category,
                "description": description,
                "status": status,
                "detail": detail
            })
        except Exception as e:
            failed += 1
            print(f"  ! [{test_id}] {description}: FEHLER - {e}")
            results.append({
                "id": test_id,
                "category": category,
                "description": description,
                "status": "ERROR",
                "detail": str(e)
            })

    print(f"\n  Ergebnis: {passed} PASS | {failed} FAIL")
    return results, passed, failed


def save_results(all_results, battery_name):
    """Speichert Ergebnisse als JSON in results/."""
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = RESULTS_DIR / f"{timestamp}_{battery_name}.json"

    total_pass = sum(1 for r in all_results if r["status"] == "PASS")
    total_fail = sum(1 for r in all_results if r["status"] != "PASS")

    output = {
        "battery": battery_name,
        "timestamp": datetime.now().isoformat(),
        "db": DB_PATH,
        "summary": {
            "total": len(all_results),
            "passed": total_pass,
            "failed": total_fail,
            "score_pct": round(total_pass / len(all_results) * 100, 1) if all_results else 0
        },
        "tests": all_results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n  Gespeichert: {filename}")
    return output


def main():
    parser = argparse.ArgumentParser(description='BACH DB Test Runner')
    parser.add_argument('--battery', default='all',
                        choices=['db_integrity', 'dist_type', 'all'],
                        help='Welche Testbatterie ausführen')
    args = parser.parse_args()

    print(f"BACH DB Test Runner | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"DB: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    all_results = []

    try:
        if args.battery in ('db_integrity', 'all'):
            results, p, f = run_tests(conn, DB_INTEGRITY_TESTS, 'DB-Integrität')
            all_results.extend(results)

        if args.battery in ('dist_type', 'all'):
            results, p, f = run_tests(conn, DIST_TYPE_TESTS, 'dist_type Konsistenz')
            all_results.extend(results)

    finally:
        conn.close()

    # Ergebnisse speichern
    output = save_results(all_results, args.battery)

    # Zusammenfassung
    score = output["summary"]["score_pct"]
    total_pass = output["summary"]["passed"]
    total_fail = output["summary"]["failed"]
    print(f"\n{'='*60}")
    print(f"  GESAMT: {total_pass} PASS | {total_fail} FAIL | Score: {score}%")

    if score == 100:
        print("  STATUS: ALLE TESTS BESTANDEN ✓")
    elif score >= 90:
        print("  STATUS: Fast alle Tests bestanden (Kleinigkeiten)")
    elif score >= 75:
        print("  STATUS: Mehrere Fehler - Überprüfung empfohlen")
    else:
        print("  STATUS: KRITISCH - Viele Fehler!")

    print(f"{'='*60}")

    sys.exit(0 if total_fail == 0 else 1)


if __name__ == '__main__':
    main()
