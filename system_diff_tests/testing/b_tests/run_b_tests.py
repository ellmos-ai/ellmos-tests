#!/usr/bin/env python3
"""
B-Test Runner
=============
Fuehrt alle B-Tests (Beobachtung) fuer ein System aus.

Usage:
    python run_b_tests.py <system_path> [output_dir]

Beispiel:
    python run_b_tests.py "C:/pfad/zum/system" "C:/pfad/zum/output"
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# B-Test Definitionen
B_TESTS = [
    ("B001", "file_inventory", "Datei-Inventar"),
    ("B002", "format_consistency", "Format-Konsistenz"),
    ("B003", "directory_depth", "Verzeichnistiefe"),
    ("B004", "naming_analysis", "Naming-Analyse"),
    ("B005", "documentation_check", "Dokumentations-Check"),
    ("B006", "code_metrics", "Code-Metriken"),
    ("B007", "dependencies", "Abhaengigkeiten"),
    ("B008", "age_analysis", "Alter-Analyse"),
]

def run_b_tests(system_path: str, output_dir: str = None) -> dict:
    """Fuehrt alle B-Tests aus und sammelt Ergebnisse."""
    
    script_dir = Path(__file__).parent
    system_name = Path(system_path).name
    
    results = {
        "system": system_name,
        "system_path": system_path,
        "test_date": datetime.now().isoformat(),
        "tests": {},
        "summary": {
            "total": len(B_TESTS),
            "success": 0,
            "failed": 0,
            "avg_score": 0.0
        }
    }
    
    scores = []
    
    for test_id, test_name, description in B_TESTS:
        script_name = f"{test_id}_{test_name}.py"
        script_path = script_dir / script_name
        
        print(f"\n[{test_id}] {description}...", end=" ")
        
        if not script_path.exists():
            print("SKIP (Script nicht gefunden)")
            results["tests"][test_id] = {"status": "skip", "error": "Script not found"}
            continue
        
        try:
            # Fuehre Test aus
            proc = subprocess.run(
                [sys.executable, str(script_path), system_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if proc.returncode == 0:
                test_result = json.loads(proc.stdout)
                score = test_result.get("score", 0)
                scores.append(score)
                
                results["tests"][test_id] = {
                    "status": "success",
                    "description": description,
                    "score": score,
                    "data": test_result
                }
                results["summary"]["success"] += 1
                print(f"OK (Score: {score})")
            else:
                results["tests"][test_id] = {
                    "status": "error",
                    "error": proc.stderr[:500]
                }
                results["summary"]["failed"] += 1
                print(f"FEHLER")
                
        except subprocess.TimeoutExpired:
            results["tests"][test_id] = {"status": "timeout"}
            results["summary"]["failed"] += 1
            print("TIMEOUT")
        except json.JSONDecodeError as e:
            results["tests"][test_id] = {"status": "parse_error", "error": str(e)}
            results["summary"]["failed"] += 1
            print("PARSE ERROR")
        except Exception as e:
            results["tests"][test_id] = {"status": "exception", "error": str(e)}
            results["summary"]["failed"] += 1
            print(f"EXCEPTION: {e}")
    
    # Durchschnitt berechnen
    if scores:
        results["summary"]["avg_score"] = round(sum(scores) / len(scores), 2)
    
    # Speichern falls output_dir
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"B_TEST_{system_name}_{datetime.now().strftime('%Y-%m-%d')}.json"
        out_file = out_path / filename
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nErgebnis gespeichert: {out_file}")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_b_tests.py <system_path> [output_dir]")
        print("\nBeispiel:")
        print('  python run_b_tests.py "C:\\...\\recludOS"')
        print('  python run_b_tests.py "C:\\...\\recludOS" "C:\\...\\output\\recludOS"')
        print("\nOhne output_dir wird automatisch <project_root>/output/<system>/ verwendet.")
        sys.exit(1)

    system_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        # Default: <project_root>/output/<system_name>/
        project_root = Path(__file__).parent.parent.parent
        system_name = Path(system_path).name
        output_dir = str(project_root / "output" / system_name)
    
    print(f"="*60)
    print(f"B-TEST RUNNER")
    print(f"System: {system_path}")
    print(f"="*60)
    
    results = run_b_tests(system_path, output_dir)
    
    print(f"\n{'='*60}")
    print(f"ZUSAMMENFASSUNG")
    print(f"{'='*60}")
    print(f"Tests: {results['summary']['success']}/{results['summary']['total']} erfolgreich")
    print(f"Durchschnitt: {results['summary']['avg_score']}/5.0")

if __name__ == "__main__":
    main()
