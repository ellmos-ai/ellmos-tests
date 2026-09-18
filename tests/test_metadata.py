"""Contract tests for repository metadata, PEP 621 compliance, bilingual documentation parity,
Mermaid diagram syntax integrity, and governance invariants (INV-LOCAL-01 through INV-SLA-10).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class MetadataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme_en = REPO_ROOT / "README.md"
        self.readme_de = REPO_ROOT / "README_de.md"
        self.pyproject = REPO_ROOT / "pyproject.toml"
        self.licenses = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
        self.security = REPO_ROOT / "SECURITY.md"
        self.llms = REPO_ROOT / "llms.txt"
        self.marketing_log = REPO_ROOT / "MARKETING-LOG.txt"

    def test_required_governance_files_exist(self) -> None:
        files = [
            self.readme_en,
            self.readme_de,
            self.pyproject,
            self.licenses,
            self.security,
            self.llms,
            self.marketing_log,
        ]
        for f in files:
            self.assertTrue(f.is_file(), f"Missing required file: {f.name}")

    def test_pyproject_pep621_metadata_and_urls(self) -> None:
        content = self.pyproject.read_text(encoding="utf-8")
        self.assertIn('version = "0.2.1"', content)
        self.assertIn('license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]', content)

        required_urls = [
            "Homepage",
            "Documentation",
            "Repository",
            "Issues",
            "Changelog",
            "Security",
            "Third-Party Licenses",
            "Parent Organization",
            "Umbrella Ecosystem",
            "Marketing Log",
            "LLM Ready",
        ]
        for url_name in required_urls:
            pattern = rf'"{url_name}"\s*=\s*"https?://' if " " in url_name or "-" in url_name else rf'{url_name}\s*=\s*"https?://'
            self.assertTrue(
                re.search(pattern, content),
                f"Missing or malformed URL key in pyproject.toml: {url_name}",
            )

    def test_bilingual_navigation_and_anchor_parity(self) -> None:
        content_en = self.readme_en.read_text(encoding="utf-8")
        content_de = self.readme_de.read_text(encoding="utf-8")

        for num in range(1, 19):
            prefix = f"## {num:02d}."
            self.assertIn(prefix, content_en, f"English README missing section {prefix}")
            self.assertIn(prefix, content_de, f"German README missing section {prefix}")

        required_anchors = [
            "overview",
            "personas",
            "comparative-matrix",
            "architecture",
            "lifecycle",
            "b-tests",
            "o-tests",
            "e-tests",
            "dimensions",
            "profiles",
            "feature-db",
            "usecases",
            "classification",
            "quickstart",
            "structure",
            "ecosystem",
            "security",
            "liability",
        ]
        for anchor in required_anchors:
            self.assertIn(
                f'id="{anchor}"',
                content_en,
                f"English README missing anchor: {anchor}",
            )
            self.assertIn(
                f'id="{anchor}"',
                content_de,
                f"German README missing reciprocal anchor: {anchor}",
            )

    def test_third_party_licenses_invariants_and_sbom(self) -> None:
        content = self.licenses.read_text(encoding="utf-8")
        self.assertIn("RunAsInvoker", content)
        self.assertIn("Python Standard Library", content)
        self.assertIn("0.2.1", content)

        for i in range(1, 10):
            inv = f"INV-LOCAL-{i:02d}"
            self.assertIn(inv, content, f"THIRD_PARTY_LICENSES.md missing invariant: {inv}")
        self.assertIn("INV-SLA-10", content)

    def test_security_policy_contract(self) -> None:
        content = self.security.read_text(encoding="utf-8")
        self.assertIn("0.2.x", content)
        self.assertIn("48 hours", content)
        self.assertIn("5 business days", content)
        self.assertIn("RunAsInvoker", content)
        self.assertIn("Zero-Egress", content)

    def test_llms_txt_contract(self) -> None:
        content = self.llms.read_text(encoding="utf-8")
        self.assertIn("Last-checked: 2026-09-18", content)
        self.assertIn("0.2.1", content)
        self.assertIn("Quick Navigation Parity Index (18-Point Layout)", content)

    def test_german_statutory_bgb_notice(self) -> None:
        content_de = self.readme_de.read_text(encoding="utf-8")
        self.assertIn("§ 521 BGB", content_de)
        self.assertIn("Gefälligkeitsrecht", content_de)

    def test_mermaid_guardrails(self) -> None:
        for md_file in [self.readme_en, self.readme_de]:
            content = md_file.read_text(encoding="utf-8")
            blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", content, re.DOTALL)
            self.assertGreater(len(blocks), 0, f"No mermaid blocks in {md_file.name}")
            for block in blocks:
                if "sequenceDiagram" in block:
                    lines = [line.strip() for line in block.splitlines()]
                    for line in lines:
                        if "->>" in line or "-->>" in line or "Note" in line:
                            self.assertNotIn(
                                ";",
                                line,
                                f"Forbidden semicolon in sequenceDiagram in {md_file.name}: {line}",
                            )


if __name__ == "__main__":
    unittest.main()
