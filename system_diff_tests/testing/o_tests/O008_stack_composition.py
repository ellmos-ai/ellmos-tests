#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
O008 - Stack-Composition
=========================
Testet, ob ein System vordefinierte Kompositionen (Stacks: Module +
Rollen + Policies) katalogisiert UND tatsaechlich zusammensetzen/pruefen
kann -- nicht nur dokumentiert.

Erkennungsmuster (generisch):
  - Stack-Katalog: *stacks.catalog*.json mit einer Liste benannter Stacks,
    von denen jeder ein Manifest referenziert.
  - Referenzierte Manifeste existieren tatsaechlich auf der Platte.
  - Composer/Validator-Skript: ein Skript, das Kompositionen gegen den
    Modulkatalog prueft bzw. aufloest (z. B. validate_composition.py,
    stack_cli.py).
  - Funktionaler Check (Bonus): folgt ein gefundenes Skript dem bekannten
    `resolve <manifest>` / `validate <manifest>` CLI-Vertrag (wie
    stack_cli.py in .MODULES/_scripts/), wird es gegen das erste
    referenzierte Manifest ausgefuehrt und die Ausgabe verifiziert.

Output: JSON mit Stack-Composition-Test-Ergebnis
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _find_stack_catalog(root: Path) -> Path | None:
    for pattern in ("*stacks.catalog*.json", "*stack*catalog*.json"):
        for candidate in root.rglob(pattern):
            if "__pycache__" in str(candidate) or "node_modules" in str(candidate):
                continue
            return candidate
    return None


def _load_stack_entries(path: Path) -> tuple[list[dict], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], str(exc)
    if isinstance(data, dict) and isinstance(data.get("stacks"), list):
        return data["stacks"], None
    if isinstance(data, list):
        return data, None
    return [], "stack catalog JSON has neither a top-level list nor a 'stacks' list"


def _find_composer_script(root: Path) -> Path | None:
    for pattern in ("*stack_cli*.py", "*validate_composition*.py", "*stack*resolve*.py", "*compos*.py"):
        for candidate in root.rglob(pattern):
            if "__pycache__" in str(candidate) or "node_modules" in str(candidate):
                continue
            return candidate
    return None


def test_stack_composition(root_path: str) -> dict:
    """Testet Stack-Katalogisierung + tatsaechliche Kompositionsfaehigkeit."""

    root = Path(root_path)
    if not root.exists():
        return {"error": f"Pfad existiert nicht: {root_path}"}

    result = {
        "system_path": str(root),
        "test_date": datetime.now().isoformat(),
        "test_id": "O008",
        "test_name": "Stack-Composition",
        "checks": [],
        "status": "UNKNOWN",
        "score": 0.0,
    }

    checks_passed = 0
    total_checks = 0

    # Check 1: Stack-Katalog vorhanden und valide
    total_checks += 1
    catalog_path = _find_stack_catalog(root)
    stacks: list[dict] = []
    if catalog_path is not None:
        stacks, error = _load_stack_entries(catalog_path)
        if error is None and stacks:
            checks_passed += 1
            result["checks"].append({
                "name": "stack_catalog_exists_and_valid",
                "passed": True,
                "details": f"{catalog_path.relative_to(root)}: {len(stacks)} Stacks",
            })
        else:
            result["checks"].append({
                "name": "stack_catalog_exists_and_valid",
                "passed": False,
                "details": error or "Katalog leer",
            })
    else:
        result["checks"].append({
            "name": "stack_catalog_exists_and_valid",
            "passed": False,
            "details": "keine Stack-Katalogdatei (*stacks.catalog*.json) gefunden",
        })

    # Check 2: referenzierte Manifeste existieren real
    total_checks += 1
    manifest_paths: list[Path] = []
    if stacks and catalog_path is not None:
        catalog_dir = catalog_path.parent
        existing = 0
        for entry in stacks:
            if not isinstance(entry, dict):
                continue
            manifest_field = entry.get("manifest")
            if not manifest_field:
                continue
            candidate = (catalog_dir / manifest_field).resolve()
            if candidate.is_file():
                existing += 1
                manifest_paths.append(candidate)
        if existing > 0:
            checks_passed += 1
            result["checks"].append({
                "name": "referenced_manifests_exist",
                "passed": True,
                "details": f"{existing}/{len(stacks)} Manifeste real vorhanden",
            })
        else:
            result["checks"].append({
                "name": "referenced_manifests_exist",
                "passed": False,
                "details": "kein referenziertes Manifest auf der Platte gefunden",
            })
    else:
        result["checks"].append({"name": "referenced_manifests_exist", "passed": False, "details": "kein Katalog"})

    # Check 3: Composer/Validator-Skript vorhanden
    total_checks += 1
    composer = _find_composer_script(root)
    if composer is not None:
        checks_passed += 1
        result["checks"].append({
            "name": "composer_script_exists",
            "passed": True,
            "details": str(composer.relative_to(root)),
        })
    else:
        result["checks"].append({
            "name": "composer_script_exists",
            "passed": False,
            "details": "kein Composer-/Validator-Skript gefunden",
        })

    # Check 4 (Bonus, funktional): bekannter CLI-Vertrag -> tatsaechlich zusammensetzen
    total_checks += 1
    functional = False
    functional_detail = "kein bekannter Composer-CLI-Vertrag gefunden -- nur statisch geprueft"
    if composer is not None and composer.name == "stack_cli.py" and manifest_paths:
        try:
            proc = subprocess.run(
                [sys.executable, str(composer), "resolve", str(manifest_paths[0])],
                capture_output=True, text=True, timeout=30, cwd=str(composer.parent),
            )
            if proc.returncode in (0, 1):  # 1 = resolve ran but reported unresolved refs; still functional
                try:
                    parsed = json.loads(proc.stdout)
                    if "components" in parsed:
                        functional = True
                        functional_detail = (
                            f"resolve {manifest_paths[0].name} -> "
                            f"{len(parsed.get('components', []))} Komponenten, "
                            f"{len(parsed.get('unresolved', []))} unaufgeloest"
                        )
                except json.JSONDecodeError:
                    functional_detail = "resolve lief, Ausgabe aber nicht als JSON lesbar"
            else:
                functional_detail = f"resolve exit={proc.returncode}: {proc.stderr[:200]}"
        except (OSError, subprocess.SubprocessError) as exc:
            functional_detail = f"Aufruf fehlgeschlagen: {exc}"
    if functional:
        checks_passed += 1
    result["checks"].append({
        "name": "composition_is_functional",
        "passed": functional,
        "details": functional_detail,
    })

    result["score"] = round(checks_passed / total_checks * 5, 2)
    if checks_passed >= total_checks * 0.75:
        result["status"] = "PASS"
    elif checks_passed >= total_checks * 0.5:
        result["status"] = "PARTIAL"
    else:
        result["status"] = "FAIL"
    result["summary"] = f"{checks_passed}/{total_checks} Checks bestanden"

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python O008_stack_composition.py <system_path> [output_json]")
        sys.exit(1)

    result = test_stack_composition(sys.argv[1])
    output = sys.argv[2] if len(sys.argv) > 2 else None

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Ergebnis gespeichert: {output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
