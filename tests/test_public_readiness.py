#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regressionstests fuer die Public-Readiness des Repos (Review-Loop 2026-07-12).

Deckt drei Befunde ab:
  * usecases.json und tools/usecases_sync.py enthielten absolute Privatpfade
    inkl. Benutzername (Public-Blocker).
  * tests/run_batteries.py::_run_grep_check meldete IMMER SKIP - das
    automatisierte Anti-PII-Gate vor Releases pruefte damit nichts.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

# Alias, damit pytest die Dataclass nicht als Testklasse einzusammeln versucht.
from run_batteries import TestCase as BatteryTestCase, _run_grep_check  # noqa: E402

# Absolute Windows-/Unix-Heimatpfade und Klarnamen, die nicht ins Repo gehoeren.
FORBIDDEN = ("C:/Users/", "C:\\Users\\", "/home/lukas", "/Users/lukas")


def _tracked_files() -> list[str]:
    """Getrackte Dateien via git.

    Raises:
        unittest.SkipTest: wenn kein git verfuegbar ist (z. B. Quell-Tarball
            ohne .git). Der Test soll dort uebersprungen werden, nicht mit
            einem Fehler abbrechen - in CI und in jedem Klon laeuft er normal.
    """
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise unittest.SkipTest(f"git nicht verfuegbar: {exc}") from exc
    return [line for line in out.stdout.splitlines() if line.strip()]


class TestNoPrivatePathsInTrackedFiles(unittest.TestCase):
    """Kein getracktes Artefakt darf einen absoluten Benutzerpfad enthalten."""

    def test_usecases_json_source_db_is_not_absolute(self):
        meta = json.loads((REPO_ROOT / "usecases.json").read_text(encoding="utf-8"))["_meta"]
        source_db = meta["source_db"]
        self.assertEqual(source_db, Path(source_db).name)
        for needle in FORBIDDEN:
            self.assertNotIn(needle, source_db)

    def test_generator_has_no_hardcoded_user_paths(self):
        text = (REPO_ROOT / "tools" / "usecases_sync.py").read_text(encoding="utf-8")
        for needle in FORBIDDEN:
            self.assertNotIn(needle, text, f"Privatpfad im Generator: {needle}")

    def test_no_absolute_user_paths_in_tracked_python_and_json(self):
        offenders = []
        for rel in _tracked_files():
            if not rel.endswith((".py", ".json")):
                continue
            path = REPO_ROOT / rel
            if not path.is_file() or path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in FORBIDDEN:
                if needle in text:
                    offenders.append(f"{rel}: {needle}")
        self.assertEqual(offenders, [], f"Privatpfade in getrackten Dateien: {offenders}")


class TestGrepCheckActuallyChecks(unittest.TestCase):
    """Das Anti-PII-Gate muss echte Treffer finden - und keine erfinden."""

    def _case(self, method: str) -> BatteryTestCase:
        return BatteryTestCase(
            test_id="T001", category="pii", description="grep-Gate",
            check_method=method, test_type="B",
        )

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.system = Path(self._tmp.name)
        (self.system / "clean.py").write_text("name = 'placeholder'\n", encoding="utf-8")
        (self.system / "leaky.py").write_text("owner = 'Lukas Geiger'\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_hit_when_expecting_none_is_a_failure(self):
        result = _run_grep_check(
            self._case('grep "Lukas\\|Geiger" leaky.py -> 0'), str(self.system)
        )
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(result.details, "Fundstellen muessen gemeldet werden")

    def test_clean_file_passes(self):
        result = _run_grep_check(
            self._case('grep "Lukas\\|Geiger" clean.py -> 0'), str(self.system)
        )
        self.assertEqual(result.status, "PASS")

    def test_unparseable_method_fails_instead_of_skipping(self):
        result = _run_grep_check(
            self._case("grep nach bekannten Namen/E-Mails"), str(self.system)
        )
        self.assertEqual(result.status, "FAIL")

    def test_missing_target_fails(self):
        result = _run_grep_check(
            self._case('grep "Lukas" gibt_es_nicht.py -> 0'), str(self.system)
        )
        self.assertEqual(result.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
