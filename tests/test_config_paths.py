import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class ConfigPathTests(unittest.TestCase):
    def _reload_config(self, onedrive: Path):
        os.environ["ELLMOS_ONEDRIVE"] = str(onedrive)
        import system_diff_tests.config as config

        return importlib.reload(config)

    def test_known_systems_prefer_current_topics_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            onedrive = Path(tmp) / "OneDrive"
            bach_root = onedrive / ".TOPICS" / ".AI" / ".OS" / "BACH"
            bach_root.mkdir(parents=True)

            config = self._reload_config(onedrive)

            self.assertEqual(config.get_system_path("BACH_v2_vanilla"), bach_root)
            self.assertEqual(
                config.get_bach_system_path("BACH_v2_vanilla"),
                bach_root / "system",
            )
            self.assertEqual(
                config.get_bach_db_path("BACH_v2_vanilla"),
                bach_root / "system" / "data" / "bach.db",
            )

    def test_system_layout_is_per_system_not_hardcoded(self):
        """A non-BACH system must not inherit BACH's "system/" subdirectory.

        The path helpers used to append "system" unconditionally, which is
        BACH's layout. Any stack that keeps its code at the root -- which is
        what this testkit is meant to evaluate too -- got a path pointing at a
        directory that does not exist.
        """
        with tempfile.TemporaryDirectory() as tmp:
            onedrive = Path(tmp) / "OneDrive"
            bach_root = onedrive / ".TOPICS" / ".AI" / ".OS" / "BACH"
            other_root = (onedrive / ".TOPICS" / ".AI" / ".OS" / "_archive"
                          / "_LEGACY" / "recludOS")
            bach_root.mkdir(parents=True)
            other_root.mkdir(parents=True)

            config = self._reload_config(onedrive)

            # BACH keeps its layout
            self.assertEqual(
                config.get_system_code_path("BACH_v2_vanilla"),
                bach_root / "system",
            )
            # a system without a layout entry keeps its code at the root
            self.assertEqual(
                config.get_system_code_path("recludOS"),
                other_root,
            )
            # and it has no database path to offer
            with self.assertRaises(KeyError):
                config.get_system_db_path("recludOS")

            # the deprecated aliases still behave exactly as before for BACH
            self.assertEqual(
                config.get_bach_system_path("BACH_v2_vanilla"),
                config.get_system_code_path("BACH_v2_vanilla"),
            )

    def test_known_systems_fall_back_to_legacy_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            onedrive = Path(tmp) / "OneDrive"
            legacy_root = onedrive / ".AI" / "BACH_v1.1"
            legacy_root.mkdir(parents=True)

            config = self._reload_config(onedrive)

            self.assertEqual(config.get_system_path("BACH_v1.1"), legacy_root)


if __name__ == "__main__":
    unittest.main()
