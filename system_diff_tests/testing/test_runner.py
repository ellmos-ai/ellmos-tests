#!/usr/bin/env python3
"""
Test Runner - Profil-basierte Testausfuehrung
==============================================
Fuehrt B-Tests und O-Tests fuer ein beliebiges System aus.

Usage:
    python test_runner.py <system_path> [--profile PROFILE] [--output OUTPUT]
    python test_runner.py <system_path> --compare <system_path_2>
    python test_runner.py --list-profiles

Beispiele:
    python test_runner.py "C:/pfad/zum/system"
    python test_runner.py "C:/pfad/zum/system" --profile QUICK
    python test_runner.py "C:/sys1" --compare "C:/sys2" --profile FULL
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

TESTING_DIR = Path(__file__).parent
PROJECT_ROOT = TESTING_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "output"

# Test-Profile
PROFILES = {
    "QUICK": {
        "b_tests": ["B001"],
        "o_tests": ["O001"],
        "description": "Schnelltest (~5 Min)"
    },
    "STANDARD": {
        "b_tests": ["B001", "B002", "B003", "B004", "B005"],
        "o_tests": ["O001", "O002", "O003"],
        "description": "Standard (~20 Min)"
    },
    "FULL": {
        "b_tests": ["B001", "B002", "B003", "B004", "B005", "B006", "B007", "B008"],
        "o_tests": ["O001", "O002", "O003", "O004", "O005", "O006"],
        "description": "Vollstaendig (~40 Min)"
    },
    "OBSERVATION": {
        "b_tests": ["B001", "B002", "B003", "B004", "B005", "B006", "B007", "B008"],
        "o_tests": [],
        "description": "Nur B-Tests (~15 Min)"
    },
    "OUTPUT": {
        "b_tests": [],
        "o_tests": ["O001", "O002", "O003", "O004", "O005", "O006"],
        "description": "Nur O-Tests (~20 Min)"
    }
}


def run_tests(system_path: str, profile: str = "STANDARD", output_dir: str = None):
    """Fuehrt Tests fuer ein System aus."""

    system_name = Path(system_path).name
    profile_config = PROFILES.get(profile, PROFILES["STANDARD"])

    if output_dir is None:
        output_dir = RESULTS_DIR / system_name
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"TEST RUNNER")
    print("=" * 70)
    print(f"System:  {system_path}")
    print(f"Profil:  {profile} - {profile_config['description']}")
    print(f"Output:  {output_dir}")
    print("=" * 70)

    results = {
        "system": system_name,
        "system_path": str(system_path),
        "profile": profile,
        "test_date": datetime.now().isoformat(),
        "b_tests": {},
        "o_tests": {},
        "summary": {
            "b_avg": 0.0,
            "o_avg": 0.0,
            "overall": 0.0
        }
    }

    b_scores = []
    o_scores = []

    # B-Tests ausfuehren
    if profile_config["b_tests"]:
        print("\n--- B-TESTS (Beobachtung) ---")
        b_tests_dir = TESTING_DIR / "b_tests"

        for test_id in profile_config["b_tests"]:
            for script in b_tests_dir.glob(f"{test_id}_*.py"):
                print(f"\n[{test_id}] {script.stem}...", end=" ")
                try:
                    proc = subprocess.run(
                        [sys.executable, str(script), system_path],
                        capture_output=True, text=True, timeout=60
                    )
                    if proc.returncode == 0:
                        test_result = json.loads(proc.stdout)
                        score = test_result.get("score", 0)
                        b_scores.append(score)
                        results["b_tests"][test_id] = {
                            "status": "success", "score": score, "data": test_result
                        }
                        print(f"OK (Score: {score})")
                    else:
                        results["b_tests"][test_id] = {"status": "error", "error": proc.stderr[:200]}
                        print("FEHLER")
                except subprocess.TimeoutExpired:
                    results["b_tests"][test_id] = {"status": "timeout"}
                    print("TIMEOUT")
                except Exception as e:
                    results["b_tests"][test_id] = {"status": "exception", "error": str(e)}
                    print(f"EXCEPTION: {e}")

    # O-Tests ausfuehren
    if profile_config["o_tests"]:
        print("\n--- O-TESTS (Ausgabe) ---")
        o_tests_dir = TESTING_DIR / "o_tests"

        for test_id in profile_config["o_tests"]:
            for script in o_tests_dir.glob(f"{test_id}_*.py"):
                print(f"\n[{test_id}] {script.stem}...", end=" ")
                try:
                    proc = subprocess.run(
                        [sys.executable, str(script), system_path],
                        capture_output=True, text=True, timeout=120
                    )
                    if proc.returncode == 0:
                        test_result = json.loads(proc.stdout)
                        score = test_result.get("score", 0)
                        o_scores.append(score)
                        results["o_tests"][test_id] = {
                            "status": test_result.get("status", "OK"),
                            "score": score, "data": test_result
                        }
                        print(f"{test_result.get('status', 'OK')} (Score: {score})")
                    else:
                        results["o_tests"][test_id] = {"status": "ERROR", "error": proc.stderr[:200]}
                        print("FEHLER")
                except subprocess.TimeoutExpired:
                    results["o_tests"][test_id] = {"status": "TIMEOUT"}
                    print("TIMEOUT")
                except Exception as e:
                    results["o_tests"][test_id] = {"status": "EXCEPTION", "error": str(e)}
                    print(f"EXCEPTION: {e}")

    # Zusammenfassung
    if b_scores:
        results["summary"]["b_avg"] = round(sum(b_scores) / len(b_scores), 2)
    if o_scores:
        results["summary"]["o_avg"] = round(sum(o_scores) / len(o_scores), 2)

    all_scores = b_scores + o_scores
    if all_scores:
        results["summary"]["overall"] = round(sum(all_scores) / len(all_scores), 2)

    # Ergebnis speichern
    filename = f"TEST_{system_name}_{profile}_{datetime.now().strftime('%Y-%m-%d')}.json"
    out_file = output_dir / filename

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"B-Tests: {len(b_scores)} ausgefuehrt, Avg: {results['summary']['b_avg']}/5.0")
    print(f"O-Tests: {len(o_scores)} ausgefuehrt, Avg: {results['summary']['o_avg']}/5.0")
    print(f"Gesamt:  {results['summary']['overall']}/5.0")
    print(f"\nErgebnis: {out_file}")

    return results


def compare_two(system1: str, system2: str, profile: str = "STANDARD"):
    """Vergleicht zwei Systeme."""

    print("=" * 70)
    print("SYSTEMVERGLEICH")
    print("=" * 70)

    results1 = run_tests(system1, profile)
    print("\n" + "-" * 70 + "\n")
    results2 = run_tests(system2, profile)

    print("\n" + "=" * 70)
    print("VERGLEICH")
    print("=" * 70)
    print(f"{'Metrik':<20} {results1['system']:<15} {results2['system']:<15} {'Delta':<10}")
    print("-" * 70)
    print(f"{'B-Tests Avg':<20} {results1['summary']['b_avg']:<15} {results2['summary']['b_avg']:<15} {results1['summary']['b_avg'] - results2['summary']['b_avg']:+.2f}")
    print(f"{'O-Tests Avg':<20} {results1['summary']['o_avg']:<15} {results2['summary']['o_avg']:<15} {results1['summary']['o_avg'] - results2['summary']['o_avg']:+.2f}")
    print(f"{'Gesamt':<20} {results1['summary']['overall']:<15} {results2['summary']['overall']:<15} {results1['summary']['overall'] - results2['summary']['overall']:+.2f}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test Runner - Profil-basierte Testausfuehrung")
    parser.add_argument("system_path", nargs="?", default=None, help="Pfad zum System")
    parser.add_argument("--profile", "-p", default="STANDARD", choices=PROFILES.keys(), help="Testprofil")
    parser.add_argument("--output", "-o", default=None, help="Output-Verzeichnis")
    parser.add_argument("--compare", "-c", default=None, help="Vergleiche mit anderem System")
    parser.add_argument("--list-profiles", action="store_true", help="Zeige verfuegbare Profile")

    args = parser.parse_args()

    if args.list_profiles:
        print("\nVerfuegbare Profile:")
        print("-" * 50)
        for name, config in PROFILES.items():
            b = len(config['b_tests'])
            o = len(config['o_tests'])
            print(f"  {name:<15} {config['description']:<30} B:{b} O:{o}")
        return

    if not args.system_path:
        parser.print_help()
        sys.exit(1)

    if args.compare:
        compare_two(args.system_path, args.compare, args.profile)
    else:
        run_tests(args.system_path, args.profile, args.output)


if __name__ == "__main__":
    main()
