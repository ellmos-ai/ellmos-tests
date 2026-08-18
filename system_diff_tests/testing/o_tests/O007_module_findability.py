#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
O007 - Module-Findability
==========================
Testet, ob ein System Bausteine (Module/Capabilities) ueber einen
maschinenlesbaren Katalog + Resolver auffindbar macht, statt nur ueber
menschliches Durchsuchen von Ordnern.

Erkennungsmuster (generisch, nicht an ein bestimmtes System gebunden):
  - Katalogdatei: *.catalog*.json (bzw. modules.catalog.json), JSON-Liste
    von Eintraegen mit "id".
  - Capability-Deklaration: Eintraege tragen ein "provides"/"capabilities"-
    Feld (belegt, dass Findbarkeit ueber mehr als die ID moeglich ist).
  - Resolver-Skript: ein Skript neben dem Katalog, das IDs/Capabilities
    zu Pfaden aufloest.
  - Funktionaler Check (Bonus, kein Hard-Requirement): wenn der Resolver
    dem bekannten `resolve <id>` / `list` / `providers <capability>`
    CLI-Vertrag folgt (wie module_resolver.py in .MODULES/_scripts/),
    wird er tatsaechlich aufgerufen und die Ausgabe verifiziert.

Output: JSON mit Findability-Test-Ergebnis
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _find_catalog_files(root: Path) -> list[Path]:
    candidates = []
    for pattern in ("*modules.catalog*.json", "*module*catalog*.json"):
        candidates.extend(root.rglob(pattern))
    seen = set()
    result = []
    for path in candidates:
        if "__pycache__" in str(path) or "node_modules" in str(path):
            continue
        if path in seen:
            continue
        seen.add(path)
        result.append(path)
    return result


def _load_catalog(path: Path) -> tuple[list[dict], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], str(exc)
    if isinstance(data, dict) and isinstance(data.get("modules"), list):
        return data["modules"], None
    if isinstance(data, list):
        return data, None
    return [], "catalog JSON has neither a top-level list nor a 'modules' list"


def _find_resolver_script(root: Path) -> Path | None:
    for pattern in ("*module_resolver*.py", "*resolver*.py", "*resolve*.py"):
        for candidate in root.rglob(pattern):
            if "__pycache__" in str(candidate) or "node_modules" in str(candidate):
                continue
            return candidate
    return None


def test_module_findability(root_path: str) -> dict:
    """Testet Modul-Findbarkeit (Katalog + Resolver) eines Systems."""

    root = Path(root_path)
    if not root.exists():
        return {"error": f"Pfad existiert nicht: {root_path}"}

    result = {
        "system_path": str(root),
        "test_date": datetime.now().isoformat(),
        "test_id": "O007",
        "test_name": "Module-Findability",
        "checks": [],
        "catalog_files": [],
        "status": "UNKNOWN",
        "score": 0.0,
    }

    checks_passed = 0
    total_checks = 0

    # Check 1: Katalogdatei vorhanden und valide
    total_checks += 1
    catalog_files = _find_catalog_files(root)
    result["catalog_files"] = [str(p.relative_to(root)) for p in catalog_files[:10]]
    modules: list[dict] = []
    catalog_path: Path | None = None
    if catalog_files:
        for candidate in catalog_files:
            parsed_modules, error = _load_catalog(candidate)
            if error is None and parsed_modules:
                modules = parsed_modules
                catalog_path = candidate
                break
        if modules:
            checks_passed += 1
            result["checks"].append({
                "name": "catalog_exists_and_valid",
                "passed": True,
                "details": f"{catalog_path.relative_to(root)}: {len(modules)} Eintraege",
            })
        else:
            result["checks"].append({
                "name": "catalog_exists_and_valid",
                "passed": False,
                "details": "Katalogdatei gefunden, aber leer oder nicht als Modulliste lesbar",
            })
    else:
        result["checks"].append({
            "name": "catalog_exists_and_valid",
            "passed": False,
            "details": "Keine Katalogdatei (*modules.catalog*.json / *module*catalog*.json) gefunden",
        })

    # Check 2: Eintraege haben eindeutige IDs
    total_checks += 1
    if modules:
        ids = [m.get("id") for m in modules if isinstance(m, dict) and m.get("id")]
        unique = len(ids) == len(set(ids)) and len(ids) == len(modules)
        if unique and ids:
            checks_passed += 1
            result["checks"].append({
                "name": "unique_ids",
                "passed": True,
                "details": f"{len(ids)} eindeutige IDs",
            })
        else:
            result["checks"].append({
                "name": "unique_ids",
                "passed": False,
                "details": f"{len(ids)}/{len(modules)} Eintraege mit ID, Eindeutigkeit: {unique}",
            })
    else:
        result["checks"].append({"name": "unique_ids", "passed": False, "details": "kein Katalog"})

    # Check 3: Capability-Deklaration (Findbarkeit ueber mehr als die ID)
    total_checks += 1
    if modules:
        with_capabilities = sum(
            1 for m in modules
            if isinstance(m, dict) and (m.get("provides") or m.get("capabilities"))
        )
        if with_capabilities > 0:
            checks_passed += 1
            result["checks"].append({
                "name": "capability_declarations",
                "passed": True,
                "details": f"{with_capabilities}/{len(modules)} Eintraege mit provides/capabilities",
            })
        else:
            result["checks"].append({
                "name": "capability_declarations",
                "passed": False,
                "details": "keine Eintraege mit provides/capabilities-Feld",
            })
    else:
        result["checks"].append({"name": "capability_declarations", "passed": False, "details": "kein Katalog"})

    # Check 4: Resolver-Skript vorhanden
    total_checks += 1
    resolver = _find_resolver_script(root)
    if resolver is not None:
        checks_passed += 1
        result["checks"].append({
            "name": "resolver_script_exists",
            "passed": True,
            "details": str(resolver.relative_to(root)),
        })
    else:
        result["checks"].append({
            "name": "resolver_script_exists",
            "passed": False,
            "details": "kein Resolver-Skript (module_resolver.py o.ae.) gefunden",
        })

    # Check 5 (Bonus, funktional): bekannter CLI-Vertrag -> tatsaechlich aufrufen
    total_checks += 1
    functional = False
    functional_detail = "kein bekannter Resolver-CLI-Vertrag gefunden -- nur statisch geprueft"
    if resolver is not None and resolver.name == "module_resolver.py" and modules:
        first_id = modules[0].get("id") if isinstance(modules[0], dict) else None
        if first_id:
            try:
                proc = subprocess.run(
                    [sys.executable, str(resolver), "resolve", str(first_id)],
                    capture_output=True, text=True, timeout=30, cwd=str(resolver.parent),
                )
                if proc.returncode == 0 and (str(first_id) in proc.stdout or "path" in proc.stdout.lower()):
                    functional = True
                    functional_detail = f"resolve {first_id!r} exit=0, stdout nicht leer"
                else:
                    functional_detail = f"resolve {first_id!r} exit={proc.returncode}: {proc.stderr[:200]}"
            except (OSError, subprocess.SubprocessError) as exc:
                functional_detail = f"Aufruf fehlgeschlagen: {exc}"
    if functional:
        checks_passed += 1
    result["checks"].append({
        "name": "resolver_is_functional",
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
        print("Usage: python O007_module_findability.py <system_path> [output_json]")
        sys.exit(1)

    result = test_module_findability(sys.argv[1])
    output = sys.argv[2] if len(sys.argv) > 2 else None

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Ergebnis gespeichert: {output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
