import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "tests" / "run_batteries.py"

spec = importlib.util.spec_from_file_location("run_batteries", RUNNER_PATH)
run_batteries = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(run_batteries)


class BatteryParserTests(unittest.TestCase):
    def test_parses_category_first_manual_battery(self):
        tests = run_batteries.parse_battery("vernunft_kantian")

        self.assertEqual(len(tests), 21)
        self.assertEqual(tests[0].category, "TRANSPARENZ")
        self.assertEqual(tests[0].test_id, "V001")
        self.assertEqual(tests[0].description, "Systembeschreibung vorhanden")
        self.assertFalse(tests[0].is_automatable)

    def test_keeps_id_first_battery_format(self):
        tests = run_batteries.parse_battery("release_smoke")

        self.assertEqual(len(tests), 17)
        self.assertEqual(tests[0].test_id, "B001")


if __name__ == "__main__":
    unittest.main()
