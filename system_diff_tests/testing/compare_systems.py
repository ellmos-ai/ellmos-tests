#!/usr/bin/env python3
"""
System Comparator
=================
Erstellt Synopsen und Vergleiche zwischen LLM-OS Systemen
basierend auf vorhandenen Testergebnissen.

Usage:
    python compare_systems.py <sys1> <sys2> [sys3 ...]
    python compare_systems.py --all
    python compare_systems.py --from-results
    python compare_systems.py --from-results --output synopse.md

Beispiele:
    python compare_systems.py recludOS _BATCH
    python compare_systems.py --all --output vergleich.md
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Zentrale Config importieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import KNOWN_SYSTEMS, OUTPUT_DIR

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = OUTPUT_DIR


def load_test_results(system_name: str) -> Dict[str, Any]:
    """Laedt Testergebnisse fuer ein System aus output/."""
    results_dir = RESULTS_DIR / system_name

    if not results_dir.exists():
        return {"status": "no_results"}

    b_files = list(results_dir.glob("B_TEST_*.json"))
    o_files = list(results_dir.glob("O_TEST_*.json"))

    result = {"system": system_name, "b_tests": None, "o_tests": None}

    if b_files:
        latest_b = max(b_files, key=lambda p: p.stat().st_mtime)
        with open(latest_b, 'r', encoding='utf-8') as f:
            result["b_tests"] = json.load(f)

    if o_files:
        latest_o = max(o_files, key=lambda p: p.stat().st_mtime)
        with open(latest_o, 'r', encoding='utf-8') as f:
            result["o_tests"] = json.load(f)

    return result


def analyze_skill_md(system_path: str) -> Dict[str, Any]:
    """Analysiert SKILL.md eines Systems."""
    path = Path(system_path)

    skill_paths = [
        path / "SKILL.md",
        path / "main" / "system" / "boot" / "SKILL.md",
        path / "SKILL.txt",
    ]

    skill_file = None
    for sp in skill_paths:
        if sp.exists():
            skill_file = sp
            break

    if not skill_file:
        return {"found": False}

    content = skill_file.read_text(encoding='utf-8', errors='ignore')

    return {
        "found": True,
        "path": str(skill_file),
        "size_kb": round(len(content) / 1024, 2),
        "lines": len(content.splitlines()),
        "has_frontmatter": content.startswith("---"),
        "has_quick_start": "quick start" in content.lower() or "quickstart" in content.lower(),
    }


def count_files(system_path: str) -> Dict[str, int]:
    """Zaehlt Dateien nach Typ."""
    path = Path(system_path)
    counts = {"python": 0, "markdown": 0, "json": 0, "txt": 0, "other": 0, "total": 0, "directories": 0}

    try:
        for item in path.rglob("*"):
            if "__pycache__" in str(item) or "node_modules" in str(item):
                continue
            if item.is_dir():
                counts["directories"] += 1
                continue
            counts["total"] += 1
            ext = item.suffix.lower()
            if ext == ".py": counts["python"] += 1
            elif ext == ".md": counts["markdown"] += 1
            elif ext == ".json": counts["json"] += 1
            elif ext == ".txt": counts["txt"] += 1
            else: counts["other"] += 1
    except Exception:
        pass

    return counts


def compare_systems(system_names: List[str]) -> Dict[str, Any]:
    """Vergleicht mehrere Systeme."""

    comparison = {
        "date": datetime.now().isoformat(),
        "systems": {},
        "ranking": [],
    }

    for name in system_names:
        path = KNOWN_SYSTEMS.get(name)
        if not path or not Path(path).exists():
            comparison["systems"][name] = {"status": "not_found"}
            continue

        system_data = {
            "path": path,
            "skill_md": analyze_skill_md(path),
            "file_counts": count_files(path),
            "test_results": load_test_results(name),
        }

        b_score = 0
        o_score = 0

        if system_data["test_results"].get("b_tests"):
            b_data = system_data["test_results"]["b_tests"]
            b_score = b_data.get("summary", {}).get("avg_score", 0)

        if system_data["test_results"].get("o_tests"):
            o_data = system_data["test_results"]["o_tests"]
            o_score = o_data.get("summary", {}).get("avg_score", 0)

        system_data["scores"] = {
            "b_score": b_score,
            "o_score": o_score,
            "total": round((b_score + o_score) / 2, 2) if b_score or o_score else 0
        }

        comparison["systems"][name] = system_data

    # Ranking
    ranked = sorted(
        [(name, data["scores"]["total"]) for name, data in comparison["systems"].items()
         if data.get("scores")],
        key=lambda x: x[1], reverse=True
    )
    comparison["ranking"] = [{"rank": i+1, "system": name, "score": score}
                             for i, (name, score) in enumerate(ranked)]

    return comparison


def generate_markdown_report(comparison: Dict[str, Any]) -> str:
    """Generiert Markdown-Bericht."""
    lines = [
        "# System-Vergleich (Synopse)",
        "",
        f"**Erstellt:** {comparison['date'][:10]}",
        f"**Systeme:** {len(comparison['systems'])}",
        "",
        "---",
        "",
        "## Ranking",
        "",
        "| Rang | System | Score |",
        "|:----:|--------|:-----:|",
    ]

    for item in comparison["ranking"]:
        lines.append(f"| {item['rank']} | **{item['system']}** | {item['score']}/5.0 |")

    lines.extend(["", "---", "", "## Detail-Vergleich", ""])

    system_names = list(comparison["systems"].keys())
    lines.append("| Aspekt |" + "|".join(f" {n} " for n in system_names) + "|")
    lines.append("|--------|" + "|".join(":------:" for _ in system_names) + "|")

    # SKILL.md
    row = "| SKILL.md |"
    for name in system_names:
        data = comparison["systems"][name]
        if data.get("status") == "not_found":
            row += " N/A |"
        else:
            size = data.get("skill_md", {}).get("size_kb", "?")
            row += f" {size} KB |"
    lines.append(row)

    # Python-Dateien
    row = "| Python |"
    for name in system_names:
        data = comparison["systems"][name]
        if data.get("status") == "not_found":
            row += " N/A |"
        else:
            row += f" {data.get('file_counts', {}).get('python', 0)} |"
    lines.append(row)

    # Dateien total
    row = "| Dateien |"
    for name in system_names:
        data = comparison["systems"][name]
        if data.get("status") == "not_found":
            row += " N/A |"
        else:
            row += f" {data.get('file_counts', {}).get('total', 0)} |"
    lines.append(row)

    # B-Score
    row = "| B-Score |"
    for name in system_names:
        data = comparison["systems"][name]
        row += f" {data.get('scores', {}).get('b_score', 'N/A')} |"
    lines.append(row)

    # O-Score
    row = "| O-Score |"
    for name in system_names:
        data = comparison["systems"][name]
        row += f" {data.get('scores', {}).get('o_score', 'N/A')} |"
    lines.append(row)

    # Gesamt
    row = "| **Gesamt** |"
    for name in system_names:
        data = comparison["systems"][name]
        row += f" **{data.get('scores', {}).get('total', 'N/A')}** |"
    lines.append(row)

    lines.extend(["", "---", ""])

    if comparison["ranking"]:
        winner = comparison["ranking"][0]
        lines.append(f"**Testsieger:** {winner['system']} mit {winner['score']}/5.0")

    lines.extend(["", "---", "", "*Generiert von system_diff_tests compare_systems.py*"])

    return "\n".join(lines)


def main():
    output_file = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--all":
        systems = list(KNOWN_SYSTEMS.keys())
    elif arg == "--from-results":
        if RESULTS_DIR.exists():
            systems = [d.name for d in RESULTS_DIR.iterdir() if d.is_dir()]
        else:
            print("Keine Ergebnisse gefunden. Zuerst Tests ausfuehren.")
            sys.exit(1)
    else:
        systems = [a for a in sys.argv[1:] if not a.startswith("--")]

    print(f"Vergleiche Systeme: {', '.join(systems)}")

    comparison = compare_systems(systems)
    report = generate_markdown_report(comparison)

    print("\n" + report)

    # Speichern
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = RESULTS_DIR / f"SYNOPSE_{datetime.now().strftime('%Y-%m-%d')}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')
    print(f"\nGespeichert: {output_path}")

    json_path = output_path.with_suffix(".json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
