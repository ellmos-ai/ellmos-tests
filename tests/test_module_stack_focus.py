"""Regression coverage for O007 (Module-Findability) / O008 (Stack-Composition) and the
MODULE_STACK_FOCUS profile -- added for the ellmos Baukasten's WP8.1
("B/O/E-Testprofil aus ellmos-tests fuer Modulfindbarkeit und Stack-Aufbau").

Uses synthetic tmp-dir fixtures, not the live OneDrive Baukasten: this suite runs in CI
on any machine, the Baukasten only exists locally on the user's systems.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
O_TESTS_DIR = REPO_ROOT / "system_diff_tests" / "testing" / "o_tests"
T_PROFILES_DIR = REPO_ROOT / "system_diff_tests" / "testing" / "t_profiles"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


o007 = _load_module(O_TESTS_DIR / "O007_module_findability.py", "o007_module_findability")
o008 = _load_module(O_TESTS_DIR / "O008_stack_composition.py", "o008_stack_composition")


class WiringTests(unittest.TestCase):
    """The three registries a profile has to appear in for the wired-in test IDs to be
    reachable at all: run_o_tests.py::O_TESTS, test_runner.py::PROFILES, and the
    t_profiles/ JSON data. Missing any one of them means the profile looks real but a
    subset of its consumers silently skip it."""

    def test_o_tests_registry_lists_o007_and_o008(self) -> None:
        run_o_tests = _load_module(O_TESTS_DIR / "run_o_tests.py", "run_o_tests_registry")
        ids = [entry[0] for entry in run_o_tests.O_TESTS]
        self.assertIn("O007", ids)
        self.assertIn("O008", ids)
        # every id in the registry must have a matching script on disk (naming convention
        # <id>_<name>.py, the same glob run_o_tests.py itself uses to dispatch).
        for test_id, name, _description in run_o_tests.O_TESTS:
            self.assertTrue((O_TESTS_DIR / f"{test_id}_{name}.py").is_file(),
                             f"{test_id} is registered but {test_id}_{name}.py does not exist")

    def test_runner_profiles_include_module_stack_focus_and_updated_full_output(self) -> None:
        runner = _load_module(
            REPO_ROOT / "system_diff_tests" / "testing" / "test_runner.py", "test_runner_profiles"
        )
        self.assertIn("MODULE_STACK_FOCUS", runner.PROFILES)
        focus = runner.PROFILES["MODULE_STACK_FOCUS"]
        self.assertEqual(sorted(focus["o_tests"]), ["O007", "O008"])
        self.assertEqual(focus["b_tests"], [])
        self.assertIn("O007", runner.PROFILES["FULL"]["o_tests"])
        self.assertIn("O008", runner.PROFILES["FULL"]["o_tests"])
        self.assertIn("O007", runner.PROFILES["OUTPUT"]["o_tests"])
        self.assertIn("O008", runner.PROFILES["OUTPUT"]["o_tests"])

    def test_t_profile_json_is_valid_and_matches_the_runner_profile(self) -> None:
        path = T_PROFILES_DIR / "MODULE_STACK_FOCUS.json"
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["profile_id"], "MODULE_STACK_FOCUS")
        self.assertEqual(data["test_types"], ["O"])
        phase_tests = [t for phase in data["phases"] for t in phase["tests"]]
        self.assertEqual(sorted(phase_tests), ["O007", "O008"])

    def test_full_and_output_t_profiles_carry_o007_o008(self) -> None:
        for name in ("FULL.json", "OUTPUT.json"):
            data = json.loads((T_PROFILES_DIR / name).read_text(encoding="utf-8"))
            if "phases" in data:
                ids = {t for phase in data["phases"] for t in phase.get("tests", [])}
            else:
                ids = {entry["id"] for entry in data["tests"]}
            self.assertIn("O007", ids, f"{name} is missing O007")
            self.assertIn("O008", ids, f"{name} is missing O008")


class O007FunctionalTests(unittest.TestCase):
    def test_missing_catalog_degrades_to_fail_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = o007.test_module_findability(tmp)
        self.assertEqual(result["test_id"], "O007")
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(any(check["passed"] for check in result["checks"] if check["name"] == "catalog_exists_and_valid"))

    def test_valid_catalog_with_capabilities_and_resolver_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_scripts").mkdir()
            catalog = {
                "modules": [
                    {"id": "alpha", "provides": ["cap.a"]},
                    {"id": "beta", "provides": ["cap.b"]},
                ]
            }
            (root / "modules.catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            # No module_resolver.py CLI here: the functional bonus check must degrade to
            # "not functional", not fail the whole test or raise.
            (root / "_scripts" / "some_other_resolver.py").write_text("# stub", encoding="utf-8")
            result = o007.test_module_findability(str(root))
        self.assertIn(result["status"], {"PASS", "PARTIAL"})
        functional_check = next(c for c in result["checks"] if c["name"] == "resolver_is_functional")
        self.assertFalse(functional_check["passed"])


class O008FunctionalTests(unittest.TestCase):
    def test_missing_stack_catalog_degrades_to_fail_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = o008.test_stack_composition(tmp)
        self.assertEqual(result["test_id"], "O008")
        self.assertEqual(result["status"], "FAIL")

    def test_stack_catalog_with_real_manifest_but_no_composer_is_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stacks_dir = root / "stacks"
            stacks_dir.mkdir()
            (stacks_dir / "my-stack.json").write_text(
                json.dumps({"schema": "ellmos.stack.v2", "components": []}), encoding="utf-8"
            )
            catalog = {"stacks": [{"id": "my-stack", "manifest": "my-stack.json"}]}
            (stacks_dir / "stacks.catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            result = o008.test_stack_composition(str(root))
        self.assertIn(result["status"], {"PARTIAL", "FAIL"})
        manifest_check = next(c for c in result["checks"] if c["name"] == "referenced_manifests_exist")
        self.assertTrue(manifest_check["passed"])
        composer_check = next(c for c in result["checks"] if c["name"] == "composer_script_exists")
        self.assertFalse(composer_check["passed"])


if __name__ == "__main__":
    unittest.main()
