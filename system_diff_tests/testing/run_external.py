#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Run ellmos B/O/E tests against an external LLM-OS style system.

Usage:
    python run_external.py <system_path> [--profile STANDARD]
    python run_external.py --list-known
    python run_external.py --all --profile QUICK
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import KNOWN_SYSTEMS, OUTPUT_DIR

PROFILES = {
    "QUICK": {"b_tests": True, "o_tests": False, "e_tests": False},
    "STANDARD": {"b_tests": True, "o_tests": True, "e_tests": False},
    "FULL": {"b_tests": True, "o_tests": True, "e_tests": True},
}


def _runner_path(kind: str) -> Path:
    if kind == "b":
        return CURRENT_DIR / "b_tests" / "run_b_tests.py"
    if kind == "o":
        return CURRENT_DIR / "o_tests" / "run_o_tests.py"
    raise ValueError(f"Unknown runner kind: {kind}")


def _run_runner(kind: str, system_path: str, output_dir: Path) -> dict:
    script = _runner_path(kind)
    if not script.exists():
        return {"status": "skip", "error": f"{kind.upper()}-test runner not found"}

    try:
        proc = subprocess.run(
            [sys.executable, str(script), system_path, str(output_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "runner exceeded 600s"}
    except Exception as exc:
        return {"status": "exception", "error": str(exc)}

    prefix = "B_TEST" if kind == "b" else "O_TEST"
    system_name = Path(system_path).resolve().name
    result_file = output_dir / f"{prefix}_{system_name}_{datetime.now().strftime('%Y-%m-%d')}.json"
    if result_file.exists():
        return json.loads(result_file.read_text(encoding="utf-8"))

    return {
        "status": "error" if proc.returncode else "ok",
        "returncode": proc.returncode,
        "stdout": proc.stdout[-2000:],
        "stderr": proc.stderr[-2000:],
    }


def test_system(system_path: str, profile: str = "STANDARD") -> dict:
    """Run the selected profile against one system path."""
    profile_name = profile.upper()
    profile_config = PROFILES.get(profile_name, PROFILES["STANDARD"])
    system = Path(system_path).resolve()
    output_dir = OUTPUT_DIR / system.name
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "system": system.name,
        "system_path": str(system),
        "profile": profile_name,
        "test_date": datetime.now().isoformat(),
        "b_tests": None,
        "o_tests": None,
        "e_tests": None,
        "summary": {},
    }

    print(f"\n{'=' * 60}")
    print(f"TEST: {system.name}")
    print(f"Profile: {profile_name}")
    print(f"Output: {output_dir}")
    print(f"{'=' * 60}")

    if profile_config["b_tests"]:
        print("\n[B-TESTS] Observation tests")
        results["b_tests"] = _run_runner("b", str(system), output_dir)

    if profile_config["o_tests"]:
        print("\n[O-TESTS] Output tests")
        results["o_tests"] = _run_runner("o", str(system), output_dir)

    if profile_config["e_tests"]:
        results["e_tests"] = {"status": "manual", "note": "E-tests require an LLM operator"}

    scores = []
    for suite in ("b_tests", "o_tests"):
        suite_result = results.get(suite)
        if suite_result and "summary" in suite_result:
            score = suite_result["summary"].get("avg_score")
            if isinstance(score, (int, float)):
                scores.append(score)

    if scores:
        results["summary"]["avg_score"] = round(sum(scores) / len(scores), 2)
        results["summary"]["scored_suites"] = len(scores)

    result_file = output_dir / f"EXTERNAL_TEST_{system.name}_{datetime.now().strftime('%Y-%m-%d')}.json"
    result_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved: {result_file}")
    return results


def test_all_known(profile: str = "STANDARD") -> dict:
    results = {}
    for name, path in KNOWN_SYSTEMS.items():
        if Path(path).exists():
            results[name] = test_system(path, profile)
        else:
            results[name] = {"status": "not_found", "path": path}
            print(f"[SKIP] {name}: {path}")
    return results


def main() -> None:
    args = sys.argv[1:]
    profile = "STANDARD"
    if "--profile" in args:
        idx = args.index("--profile")
        if idx + 1 >= len(args):
            print("Error: --profile needs a value")
            sys.exit(2)
        profile = args[idx + 1].upper()
        del args[idx : idx + 2]

    if not args:
        print(__doc__)
        sys.exit(1)

    target = args[0]
    if target == "--list-known":
        for name, path in KNOWN_SYSTEMS.items():
            marker = "OK" if Path(path).exists() else "--"
            print(f"{marker} {name}: {path}")
    elif target == "--all":
        test_all_known(profile)
    elif target in KNOWN_SYSTEMS:
        test_system(KNOWN_SYSTEMS[target], profile)
    elif Path(target).exists():
        test_system(target, profile)
    else:
        print(f"Error: path or known system not found: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
