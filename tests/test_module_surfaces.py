import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ModuleSurfaceTests(unittest.TestCase):
    def test_module_manifest_and_skill_exist(self):
        manifest_path = REPO_ROOT / "ellmos-module.json"
        skill_path = REPO_ROOT / "SKILL.md"
        agents_path = REPO_ROOT / "AGENTS.md"

        self.assertTrue(manifest_path.exists())
        self.assertTrue(skill_path.exists())
        self.assertTrue(agents_path.exists())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "ellmos-tests")
        self.assertIn("testing.llm_os", manifest["wiring"]["provides"])

    def test_profile_compatibility_folder_is_populated(self):
        profiles_dir = REPO_ROOT / "system_diff_tests" / "testing" / "profiles"
        profile_names = {
            "QUICK.json",
            "STANDARD.json",
            "FULL.json",
            "MEMORY_FOCUS.json",
            "TASK_FOCUS.json",
            "OUTPUT.json",
            "OBSERVATION.json",
        }

        self.assertEqual(profile_names, {path.name for path in profiles_dir.glob("*.json")})
        for profile in profiles_dir.glob("*.json"):
            json.loads(profile.read_text(encoding="utf-8"))

    def test_run_external_imports_without_playwright(self):
        runner_path = REPO_ROOT / "system_diff_tests" / "testing" / "run_external.py"
        spec = importlib.util.spec_from_file_location("run_external", runner_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        self.assertIn("STANDARD", module.PROFILES)


if __name__ == "__main__":
    unittest.main()
