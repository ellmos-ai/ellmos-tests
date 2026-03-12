#!/usr/bin/env python3
"""
System Diff Tests - Zentraler Test-Runner
==========================================
Fuehrt B-Tests und O-Tests gegen ein beliebiges System aus
und speichert Ergebnisse im output/-Ordner.

Usage:
    python run_all.py <system_path>
    python run_all.py <system_path> --only b
    python run_all.py <system_path> --only o
    python run_all.py <system_path> --output <custom_output_dir>
    python run_all.py --system recludOS

Systempfade werden ueber config.py aufgeloest (Env: ELLMOS_ONEDRIVE).
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent

# Zentrale Config importieren
sys.path.insert(0, str(PROJECT_ROOT))
from config import OUTPUT_DIR, KNOWN_SYSTEMS

TESTING_DIR = PROJECT_ROOT / "testing"
B_TESTS_DIR = TESTING_DIR / "b_tests"
O_TESTS_DIR = TESTING_DIR / "o_tests"


def run_test_suite(runner_script: str, system_path: str, output_dir: str, label: str) -> dict:
    """Fuehrt einen Test-Runner aus und gibt Ergebnisse zurueck."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  System: {Path(system_path).name}")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}")

    try:
        proc = subprocess.run(
            [sys.executable, runner_script, system_path, output_dir],
            capture_output=False,
            text=True,
            timeout=600
        )
        return {"status": "ok", "returncode": proc.returncode}
    except subprocess.TimeoutExpired:
        print(f"\n  TIMEOUT: {label} hat das Zeitlimit ueberschritten")
        return {"status": "timeout"}
    except Exception as e:
        print(f"\n  FEHLER: {e}")
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="System Diff Tests - Zentraler Test-Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python run_all.py --system recludOS
  python run_all.py --system _BATCH --only b
  python run_all.py "C:\\pfad\\zum\\system" --output "C:\\custom\\output"

Bekannte Systeme (via config.py / ELLMOS_ONEDRIVE):
  """ + "\n  ".join(f"{k}: {v}" for k, v in KNOWN_SYSTEMS.items()) + """
        """
    )
    parser.add_argument("system_path", nargs="?", help="Pfad zum zu testenden System")
    parser.add_argument("--system", help="Name eines bekannten Systems aus config.py")
    parser.add_argument("--only", choices=["b", "o"], help="Nur B-Tests oder O-Tests ausfuehren")
    parser.add_argument("--output", help="Custom Output-Verzeichnis (Default: output/<system_name>/)")

    args = parser.parse_args()

    # System-Pfad bestimmen: --system NAME oder direkter Pfad
    if args.system:
        if args.system not in KNOWN_SYSTEMS:
            print(f"FEHLER: Unbekanntes System '{args.system}'. Bekannt: {', '.join(KNOWN_SYSTEMS)}")
            sys.exit(1)
        system_path = KNOWN_SYSTEMS[args.system]
    elif args.system_path:
        system_path = args.system_path
    else:
        parser.print_help()
        sys.exit(1)

    system_name = Path(system_path).name

    if not Path(system_path).exists():
        print(f"FEHLER: System-Pfad existiert nicht: {system_path}")
        sys.exit(1)

    # Output-Verzeichnis bestimmen
    if args.output:
        output_dir = args.output
    else:
        output_dir = str(OUTPUT_DIR / system_name)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n{'#'*60}")
    print(f"  SYSTEM DIFF TESTS")
    print(f"  System:  {system_name}")
    print(f"  Pfad:    {system_path}")
    print(f"  Output:  {output_dir}")
    print(f"  Datum:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'#'*60}")

    results = {}

    # B-Tests
    if args.only is None or args.only == "b":
        b_runner = str(B_TESTS_DIR / "run_b_tests.py")
        if Path(b_runner).exists():
            results["b_tests"] = run_test_suite(b_runner, system_path, output_dir, "B-TESTS (Beobachtung)")
        else:
            print(f"\n  WARNUNG: B-Test Runner nicht gefunden: {b_runner}")

    # O-Tests
    if args.only is None or args.only == "o":
        o_runner = str(O_TESTS_DIR / "run_o_tests.py")
        if Path(o_runner).exists():
            results["o_tests"] = run_test_suite(o_runner, system_path, output_dir, "O-TESTS (Ausgabe/Output)")
        else:
            print(f"\n  WARNUNG: O-Test Runner nicht gefunden: {o_runner}")

    # Zusammenfassung
    print(f"\n{'#'*60}")
    print(f"  ZUSAMMENFASSUNG")
    print(f"{'#'*60}")

    for suite, result in results.items():
        status = result.get("status", "unknown")
        icon = "OK" if status == "ok" and result.get("returncode", 1) == 0 else "FEHLER"
        print(f"  {suite}: {icon}")

    print(f"\n  Ergebnisse gespeichert in: {output_dir}")

    # Liste gespeicherte Dateien
    output_path = Path(output_dir)
    if output_path.exists():
        files = sorted(output_path.glob("*.json"))
        if files:
            print(f"\n  Ergebnis-Dateien:")
            for f in files:
                size = f.stat().st_size
                print(f"    - {f.name} ({size:,} bytes)")

    print()


if __name__ == "__main__":
    main()
