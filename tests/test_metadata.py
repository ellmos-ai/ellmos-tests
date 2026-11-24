"""Contract tests for repository metadata, PEP 621/639 compliance, bilingual documentation parity,
Mermaid diagram syntax integrity, CI/pytest hygiene, and governance invariants (INV-LOCAL-01..10).
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class MetadataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme_en = REPO_ROOT / "README.md"
        self.readme_de = REPO_ROOT / "README_de.md"
        self.pyproject = REPO_ROOT / "pyproject.toml"
        self.pytest_ini = REPO_ROOT / "pytest.ini"
        self.gitignore = REPO_ROOT / ".gitignore"
        self.manifest_in = REPO_ROOT / "MANIFEST.in"
        self.licenses = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
        self.security = REPO_ROOT / "SECURITY.md"
        self.code_of_conduct = REPO_ROOT / "CODE_OF_CONDUCT.md"
        self.contributing = REPO_ROOT / "CONTRIBUTING.md"
        self.llms = REPO_ROOT / "llms.txt"
        self.llm = REPO_ROOT / "llm.txt"
        self.skill = REPO_ROOT / "SKILL.md"
        self.ci_workflow = REPO_ROOT / ".github" / "workflows" / "tests.yml"
        self.dependabot = REPO_ROOT / ".github" / "dependabot.yml"
        self.issue_config = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"

    def test_required_governance_files_exist(self) -> None:
        files = [
            self.readme_en,
            self.readme_de,
            self.pyproject,
            self.pytest_ini,
            self.gitignore,
            self.manifest_in,
            self.licenses,
            self.security,
            self.code_of_conduct,
            self.contributing,
            self.llms,
            self.llm,
            self.skill,
            self.ci_workflow,
            self.dependabot,
            self.issue_config,
        ]
        for f in files:
            self.assertTrue(f.is_file(), f"Missing required file: {f.name}")

    def test_pyproject_pep621_metadata_and_urls(self) -> None:
        content = self.pyproject.read_text(encoding="utf-8")
        self.assertIn('version = "0.2.1"', content)
        self.assertIn('license = "MIT"', content)
        self.assertIn('license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]', content)
        self.assertNotIn("License :: OSI Approved", content)
        self.assertNotIn("MARKETING-LOG.txt", content)

        required_urls = [
            "Homepage",
            "Documentation",
            "Repository",
            "Issues",
            "Changelog",
            "Contributing",
            "Code of Conduct",
            "Security",
            "Third-Party Licenses",
            "Parent Organization",
            "Umbrella Ecosystem",
            "LLM Ready",
        ]
        for url_name in required_urls:
            pattern = (
                rf'"{url_name}"\s*=\s*"https?://'
                if " " in url_name or "-" in url_name
                else rf'{url_name}\s*=\s*"https?://'
            )
            self.assertTrue(
                re.search(pattern, content),
                f"Missing or malformed URL key in pyproject.toml: {url_name}",
            )

    def test_packaging_setup_excludes_flat_layout_collisions(self) -> None:
        content = self.pyproject.read_text(encoding="utf-8")
        self.assertIn("[tool.setuptools.packages.find]", content)
        self.assertIn('include = ["system_diff_tests*"]', content)
        manifest_text = self.manifest_in.read_text(encoding="utf-8")
        self.assertIn("include llms.txt", manifest_text)
        self.assertIn("include llm.txt", manifest_text)
        self.assertIn("exclude MARKETING-LOG.txt", manifest_text)

    def test_pytest_no_relative_basetemp_and_excludes_temp(self) -> None:
        for cfg in (self.pyproject, self.pytest_ini):
            text = cfg.read_text(encoding="utf-8")
            self.assertNotIn("--basetemp=.pytest_temp", text)
            self.assertNotIn("--basetemp=.pytest_tmp", text)
            self.assertIn(".pytest_temp*", text)
            self.assertIn("xfail_strict = true", text)
            self.assertIn("--strict-markers", text)
            self.assertIn("asyncio_default_fixture_loop_scope", text)

    def test_marketing_log_not_tracked_and_gitignored(self) -> None:
        gitignore_text = self.gitignore.read_text(encoding="utf-8")
        self.assertIn("MARKETING-LOG.txt", gitignore_text)
        self.assertIn(".pytest_temp/", gitignore_text)
        try:
            proc = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "MARKETING-LOG.txt"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise unittest.SkipTest(f"git unavailable: {exc}") from exc
        if proc.returncode == 0:
            self.fail("MARKETING-LOG.txt must not be tracked in git")

    def test_code_of_conduct_has_no_template_email(self) -> None:
        text = self.code_of_conduct.read_text(encoding="utf-8")
        self.assertNotIn("lukas@geiger.sh", text)
        self.assertIn("github.com/ellmos-ai/ellmos-tests/issues", text)
        self.assertIn("security/advisories/new", text)

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

    def test_p022_llm_install_prompt_parity(self) -> None:
        for readme in (self.readme_en, self.readme_de):
            text = readme.read_text(encoding="utf-8")
            self.assertIn("```text", text)
            self.assertIn("llms.txt", text)
            self.assertIn("SKILL.md", text)
            self.assertNotIn("MARKETING-LOG.txt", text)
        llm_text = self.llm.read_text(encoding="utf-8")
        self.assertIn("llms.txt", llm_text)

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
        self.assertIn("Last-checked: 2026-11-24", content)
        self.assertIn("0.2.1", content)
        self.assertIn("Quick Navigation Parity Index (18-Point Layout)", content)
        for field in ("Prerequisites", "Install command", "Verification command", "Minimal example"):
            self.assertIn(field, content)

    def test_ci_workflow_matrix_and_packaging_checks(self) -> None:
        ci_text = self.ci_workflow.read_text(encoding="utf-8")
        for needle in (
            "ubuntu-latest",
            "windows-latest",
            "macos-latest",
            '"3.10"',
            '"3.11"',
            '"3.12"',
            '"3.13"',
            "workflow_dispatch:",
            "contents: read",
            "pip install --no-build-isolation --dry-run .",
            "pip check",
            "ruff check .",
            "pytest -ra",
        ):
            self.assertIn(needle, ci_text)

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
