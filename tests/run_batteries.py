#!/usr/bin/env python3
"""
Smoke-Test Battery Runner
==========================
Liest Testbatterien aus tests/batteries/*.txt, parst die Test-Definitionen
und fuehrt automatisierbare Tests (B-Tests, O-Tests, DB-Tests) aus.

Usage:
    python run_batteries.py --list
    python run_batteries.py --battery release_smoke
    python run_batteries.py --battery db_integrity
    python run_batteries.py --all
    python run_batteries.py --battery release_smoke --system-path "C:\\pfad\\zum\\system"
"""

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════
# FARBAUSGABE
# ═══════════════════════════════════════════════════════════════════════════

def _supports_color() -> bool:
    """Prueft ob das Terminal Farben unterstuetzt."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(sys.stdout, "isatty"):
        return False
    return sys.stdout.isatty()

_USE_COLOR = _supports_color()

def _c(text: str, code: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

def green(text: str) -> str:
    return _c(text, "32")

def red(text: str) -> str:
    return _c(text, "31")

def yellow(text: str) -> str:
    return _c(text, "33")

def bold(text: str) -> str:
    return _c(text, "1")

def dim(text: str) -> str:
    return _c(text, "2")


# ═══════════════════════════════════════════════════════════════════════════
# TEST-DATENMODELL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TestCase:
    """Einzelner Test aus einer Battery-Datei."""
    test_id: str
    category: str
    description: str
    details: list[str] = field(default_factory=list)
    check_method: Optional[str] = None
    expected: Optional[str] = None
    test_type: str = "unknown"  # B, O, E, DB, etc.

    @property
    def is_automatable(self) -> bool:
        """B-Tests und DB-Tests sind automatisierbar, E-Tests nicht."""
        return self.test_type in ("B", "O", "DB", "CN", "LLM", "UC")


@dataclass
class TestResult:
    """Ergebnis eines einzelnen Tests."""
    test_id: str
    status: str  # PASS, FAIL, SKIP, ERROR
    message: str = ""
    details: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# BATTERY-PARSER
# ═══════════════════════════════════════════════════════════════════════════

BATTERIES_DIR = Path(__file__).resolve().parent / "batteries"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def list_batteries() -> list[str]:
    """Listet alle verfuegbaren Battery-Dateien."""
    return sorted(p.stem for p in BATTERIES_DIR.glob("*.txt"))


def parse_battery(name: str) -> list[TestCase]:
    """Parst eine Battery-Datei und gibt TestCases zurueck."""
    battery_file = BATTERIES_DIR / f"{name}.txt"
    if not battery_file.exists():
        print(red(f"FEHLER: Battery '{name}' nicht gefunden: {battery_file}"))
        return []

    content = battery_file.read_text(encoding="utf-8", errors="ignore")
    tests: list[TestCase] = []
    current_test: Optional[TestCase] = None

    # Pattern: TEST_ID | Kategorie | Beschreibung
    test_header_re = re.compile(
        r"^([A-Z_]+\d+)\s*\|\s*(.+?)\s*\|\s*(.+)$"
    )

    for line in content.splitlines():
        stripped = line.strip()

        # Kommentare und Leerzeilen
        if not stripped or stripped.startswith("#"):
            # Section-Header wie "# B-TESTS ..."
            continue

        # Neuer Test-Header?
        match = test_header_re.match(stripped)
        if match:
            if current_test:
                tests.append(current_test)

            test_id = match.group(1)
            # Test-Typ aus Praefix ableiten
            type_match = re.match(r"([A-Z_]+)", test_id)
            test_type = type_match.group(1).rstrip("_") if type_match else "unknown"
            # Normalisiere: DB001 -> DB, B001 -> B, DB_R01 -> DB
            if test_type.startswith("DB"):
                test_type = "DB"
            elif len(test_type) > 3:
                test_type = test_type[:2]

            current_test = TestCase(
                test_id=test_id,
                category=match.group(2).strip(),
                description=match.group(3).strip(),
                test_type=test_type,
            )
            continue

        # Detail-Zeilen gehoeren zum aktuellen Test
        if current_test:
            if stripped.startswith("Pr"):  # Pruefmethode / Prüfmethode
                current_test.check_method = stripped.split(":", 1)[-1].strip()
            elif stripped.startswith("Erwartet") or stripped.startswith("SQL:"):
                current_test.expected = stripped
            elif stripped.startswith("Bewertung:"):
                current_test.check_method = stripped
            elif stripped.startswith("- ") or stripped.startswith("Status:"):
                current_test.details.append(stripped)

    if current_test:
        tests.append(current_test)

    return tests


# ═══════════════════════════════════════════════════════════════════════════
# TEST-EXECUTOR
# ═══════════════════════════════════════════════════════════════════════════

def execute_test(test: TestCase, system_path: Optional[str] = None) -> TestResult:
    """Fuehrt einen einzelnen Test aus.

    Automatisierbare Tests werden anhand ihrer Pruefmethode ausgefuehrt.
    E-Tests und Tests ohne klare Pruefmethode werden als SKIP markiert.
    """
    if not test.is_automatable:
        return TestResult(
            test_id=test.test_id,
            status="SKIP",
            message="E-Test (manuell) - automatische Ausfuehrung nicht moeglich",
        )

    # Tests die os.path.exists() nutzen
    if test.check_method and "exists" in test.check_method.lower():
        return _run_existence_checks(test, system_path)

    # Tests die subprocess nutzen
    if test.check_method and "subprocess" in test.check_method.lower():
        return _run_subprocess_checks(test, system_path)

    # Tests die SQL nutzen
    if test.check_method and "sql" in test.check_method.lower():
        return _run_sql_check(test, system_path)

    # Tests die grep nutzen
    if test.check_method and "grep" in test.check_method.lower():
        return _run_grep_check(test, system_path)

    # Kein automatisierbarer Test-Typ erkannt
    return TestResult(
        test_id=test.test_id,
        status="SKIP",
        message=f"Keine automatisierbare Pruefmethode: {test.check_method or 'nicht definiert'}",
    )


def _run_existence_checks(test: TestCase, system_path: Optional[str]) -> TestResult:
    """Fuehrt os.path.exists()-basierte Tests aus."""
    if not system_path:
        return TestResult(test.test_id, "SKIP", "Kein System-Pfad angegeben")

    base = Path(system_path)
    missing = []
    found = []

    for detail in test.details:
        # Parse "- datei.py existiert" oder "- ordner/ hat mindestens X"
        detail_clean = detail.lstrip("- ").strip()

        # "NICHT" Checks (Datei soll NICHT existieren)
        if "NICHT" in detail_clean:
            path_match = re.search(r"([\w./_-]+)", detail_clean)
            if path_match:
                check_path = base / path_match.group(1)
                if check_path.exists():
                    missing.append(f"Sollte NICHT existieren: {path_match.group(1)}")
                else:
                    found.append(f"Korrekt nicht vorhanden: {path_match.group(1)}")
            continue

        # "existiert" Checks
        if "existiert" in detail_clean:
            path_match = re.search(r"([\w./_-]+)\s+existiert", detail_clean)
            if path_match:
                check_path = base / path_match.group(1)
                if check_path.exists():
                    found.append(path_match.group(1))
                else:
                    missing.append(path_match.group(1))

    if missing:
        return TestResult(
            test.test_id, "FAIL",
            f"{len(missing)} fehlend, {len(found)} gefunden",
            details=[f"FEHLEND: {m}" for m in missing] + [f"OK: {f}" for f in found],
        )
    elif found:
        return TestResult(
            test.test_id, "PASS",
            f"Alle {len(found)} Pfade geprueft",
            details=[f"OK: {f}" for f in found],
        )
    else:
        return TestResult(test.test_id, "SKIP", "Keine pruefbaren Pfade gefunden")


def _run_subprocess_checks(test: TestCase, system_path: Optional[str]) -> TestResult:
    """Fuehrt subprocess-basierte Tests aus."""
    if not system_path:
        return TestResult(test.test_id, "SKIP", "Kein System-Pfad angegeben")

    results = []
    all_pass = True

    for detail in test.details:
        detail_clean = detail.lstrip("- ").strip()

        # Python-Befehle extrahieren
        py_match = re.search(r'python\s+(.+?)(?:\s*$|\s*->)', detail_clean)
        if py_match:
            cmd = py_match.group(1).strip()
            try:
                proc = subprocess.run(
                    [sys.executable, *cmd.split()],
                    cwd=system_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
                if proc.returncode == 0:
                    results.append(f"OK: {detail_clean}")
                else:
                    results.append(f"FAIL (rc={proc.returncode}): {detail_clean}")
                    all_pass = False
            except subprocess.TimeoutExpired:
                results.append(f"TIMEOUT: {detail_clean}")
                all_pass = False
            except Exception as e:
                results.append(f"ERROR ({e}): {detail_clean}")
                all_pass = False

    if not results:
        return TestResult(test.test_id, "SKIP", "Keine ausfuehrbaren Befehle gefunden")

    return TestResult(
        test.test_id,
        "PASS" if all_pass else "FAIL",
        f"{len([r for r in results if r.startswith('OK')])} OK / {len(results)} total",
        details=results,
    )


def _run_sql_check(test: TestCase, system_path: Optional[str]) -> TestResult:
    """Fuehrt SQL-basierte Tests aus."""
    if not system_path:
        return TestResult(test.test_id, "SKIP", "Kein System-Pfad angegeben")

    # Suche bach.db
    base = Path(system_path)
    db_candidates = [
        base / "data" / "bach.db",
        base / "bach.db",
        base / "system" / "data" / "bach.db",
    ]

    db_path = None
    for candidate in db_candidates:
        if candidate.exists():
            db_path = candidate
            break

    if not db_path:
        return TestResult(test.test_id, "SKIP", "bach.db nicht gefunden")

    # SQL aus expected oder details extrahieren
    sql_statements = []
    for detail in test.details + ([test.expected] if test.expected else []):
        if detail and "SQL:" in detail:
            sql = detail.split("SQL:", 1)[1].strip()
            sql_statements.append(sql)

    if not sql_statements:
        return TestResult(test.test_id, "SKIP", "Keine SQL-Statements gefunden")

    results = []
    all_pass = True

    for sql in sql_statements:
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
            conn.close()
            results.append(f"OK: {sql[:60]}... -> {rows[:3]}")
        except Exception as e:
            results.append(f"FAIL: {sql[:60]}... -> {e}")
            all_pass = False

    return TestResult(
        test.test_id,
        "PASS" if all_pass else "FAIL",
        f"SQL-Pruefung: {len(results)} Statements",
        details=results,
    )


def _run_grep_check(test: TestCase, system_path: Optional[str]) -> TestResult:
    """Fuehrt grep-basierte Tests aus."""
    if not system_path:
        return TestResult(test.test_id, "SKIP", "Kein System-Pfad angegeben")

    # Einfacher grep-basierter Check
    return TestResult(
        test.test_id, "SKIP",
        "Grep-Tests erfordern manuelle Ausfuehrung",
    )


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_battery(name: str, system_path: Optional[str] = None, verbose: bool = False) -> list[TestResult]:
    """Fuehrt eine komplette Test-Batterie aus."""
    tests = parse_battery(name)
    if not tests:
        return []

    print(f"\n{bold('=' * 60)}")
    print(f"  BATTERIE: {bold(name)}")
    print(f"  Tests: {len(tests)}")
    if system_path:
        print(f"  System: {system_path}")
    print(f"{bold('=' * 60)}\n")

    results: list[TestResult] = []

    for test in tests:
        result = execute_test(test, system_path)
        results.append(result)

        # Status-Icon
        if result.status == "PASS":
            icon = green("[PASS]")
        elif result.status == "FAIL":
            icon = red("[FAIL]")
        elif result.status == "SKIP":
            icon = yellow("[SKIP]")
        else:
            icon = red("[ERR ]")

        print(f"  {icon} {test.test_id} - {test.description}")
        if result.message and verbose:
            print(f"         {dim(result.message)}")
        if result.details and verbose:
            for d in result.details[:5]:
                print(f"         {dim(d)}")

    return results


def print_summary(battery_name: str, results: list[TestResult]):
    """Gibt eine Zusammenfassung aus."""
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    skipped = sum(1 for r in results if r.status == "SKIP")
    errors = sum(1 for r in results if r.status == "ERROR")
    total = len(results)

    print(f"\n{bold('-' * 60)}")
    print(f"  ZUSAMMENFASSUNG: {bold(battery_name)}")
    print(f"{bold('-' * 60)}")
    print(f"  Total:    {total}")
    print(f"  {green('Bestanden:')} {passed}")
    if failed:
        print(f"  {red('Fehlgeschlagen:')} {failed}")
    if skipped:
        print(f"  {yellow('Uebersprungen:')} {skipped}")
    if errors:
        print(f"  {red('Fehler:')} {errors}")

    if failed == 0 and errors == 0:
        if skipped == total:
            print(f"\n  {yellow('ERGEBNIS: Alle Tests uebersprungen (kein System-Pfad?)')}")
        else:
            print(f"\n  {green(bold('ERGEBNIS: BESTANDEN'))}")
    else:
        print(f"\n  {red(bold('ERGEBNIS: NICHT BESTANDEN'))}")
        # Fehlgeschlagene Tests auflisten
        for r in results:
            if r.status == "FAIL":
                print(f"    {red('X')} {r.test_id}: {r.message}")

    print()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Smoke-Test Battery Runner fuer ellmos-tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python run_batteries.py --list
  python run_batteries.py --battery release_smoke --system-path "C:\\pfad\\system"
  python run_batteries.py --all --system-path "C:\\pfad\\system"
  python run_batteries.py --battery db_integrity --system-path "C:\\pfad\\system" -v
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true",
                       help="Zeigt alle verfuegbaren Batterien")
    group.add_argument("--battery", type=str,
                       help="Name einer Batterie (ohne .txt)")
    group.add_argument("--all", action="store_true",
                       help="Alle Batterien ausfuehren")

    parser.add_argument("--system-path", type=str,
                        help="Pfad zum zu testenden System")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Ausfuehrliche Ausgabe")

    args = parser.parse_args()

    if args.list:
        batteries = list_batteries()
        print(f"\nVerfuegbare Testbatterien ({len(batteries)}):")
        print("-" * 40)
        for b in batteries:
            tests = parse_battery(b)
            auto = sum(1 for t in tests if t.is_automatable)
            manual = len(tests) - auto
            print(f"  {b:30s} ({len(tests)} Tests, {auto} auto, {manual} manuell)")
        print()
        return

    # Batterien bestimmen
    if args.all:
        battery_names = list_batteries()
    else:
        battery_names = [args.battery]

    all_results: dict[str, list[TestResult]] = {}
    total_pass = 0
    total_fail = 0
    total_skip = 0

    for name in battery_names:
        results = run_battery(name, args.system_path, verbose=args.verbose)
        if results:
            all_results[name] = results
            print_summary(name, results)
            total_pass += sum(1 for r in results if r.status == "PASS")
            total_fail += sum(1 for r in results if r.status == "FAIL")
            total_skip += sum(1 for r in results if r.status == "SKIP")

    # Gesamt-Zusammenfassung bei mehreren Batterien
    if len(all_results) > 1:
        print(f"\n{'#' * 60}")
        print(f"  GESAMTERGEBNIS")
        print(f"{'#' * 60}")
        print(f"  Batterien:     {len(all_results)}")
        print(f"  {green('Bestanden:')}    {total_pass}")
        if total_fail:
            print(f"  {red('Fehlgeschlagen:')} {total_fail}")
        if total_skip:
            print(f"  {yellow('Uebersprungen:')} {total_skip}")

        if total_fail == 0:
            print(f"\n  {green(bold('ALLE BATTERIEN BESTANDEN'))}")
        else:
            print(f"\n  {red(bold('NICHT ALLE BATTERIEN BESTANDEN'))}")
            for name, results in all_results.items():
                fails = [r for r in results if r.status == "FAIL"]
                if fails:
                    print(f"    {red('X')} {name}: {len(fails)} fehlgeschlagen")
        print()


if __name__ == "__main__":
    main()
