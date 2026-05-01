"""
Zentrale Konfiguration fuer ellmos-tests
=========================================
Alle Pfade und System-Definitionen an einer Stelle.

Konfiguration ueber Umgebungsvariablen:
  ELLMOS_BASE_PATH  - Root des ellmos-tests Projekts
  ELLMOS_ONEDRIVE   - OneDrive-Basispfad (fuer System-Pfade)
  BACH_SYSTEM_PATH   - Optionaler direkter BACH-system Pfad in einzelnen Tests
  BACH_DB_PATH       - Optionaler direkter BACH-DB Pfad in DB-Tests
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# BASIS-PFADE
# ═══════════════════════════════════════════════════════════════════════════

# Projekt-Root: ellmos-tests/system_diff_tests/../ = ellmos-tests/
BASE_DIR = Path(
    os.environ.get("ELLMOS_BASE_PATH",
                    str(Path(__file__).resolve().parent.parent))
)

# OneDrive-Basis (fuer System-Pfade)
_default_onedrive = Path.home() / "OneDrive"
ONEDRIVE_DIR = Path(os.environ.get("ELLMOS_ONEDRIVE", str(_default_onedrive)))

# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT / DATENBANK
# ═══════════════════════════════════════════════════════════════════════════

OUTPUT_DIR = BASE_DIR / "system_diff_tests" / "output"
DB_PATH = BASE_DIR / "system_diff_tests" / "mapping" / "feature_mapping.db"

# ═══════════════════════════════════════════════════════════════════════════
# BEKANNTE SYSTEME
# ═══════════════════════════════════════════════════════════════════════════
# Name -> relative Pfad-Kandidaten unter OneDrive.
# Die aktuelle .TOPICS-Struktur wird bevorzugt, alte Layouts bleiben als
# Fallback fuer historische Testdaten erhalten.

_SYSTEM_RELATIVE_PATHS = {
    "BACH_v2_vanilla": (
        ".TOPICS/.AI/.OS/BACH",
        ".AI/BACH_v2_vanilla",
    ),
    "BACH_strawberry": (
        ".TOPICS/.AI/.OS/BACH",
        ".AI/BACH_strawberry",
    ),
    "BACH_v1.1": (
        ".TOPICS/.AI/.OS/_archive/_backups/BACH_v1.1",
        ".AI/BACH_v1.1",
    ),
    "recludOS": (
        ".TOPICS/.AI/.OS/_archive/_LEGACY/recludOS",
        ".AI/recludOS",
    ),
    "_BATCH": (
        ".TOPICS/.AI/.OS/_archive/_LEGACY/_BATCH",
        ".SOFTWARE/_BATCH",
    ),
    "_CHIAH": (
        ".TOPICS/.AI/.OS/_archive/_LEGACY/_CHIAH",
        ".SOFTWARE/_CHIAH",
    ),
    "BACH_STREAM": (
        ".TOPICS/.AI/.OS/_archive/_LEGACY/BACH_STREAM",
        ".AI/BACH_STREAM",
    ),
    "AI-Portable": (
        ".TOPICS/.AI/.OS/_archive/_LEGACY/BACH_STREAM/PRODUCTION/MAPPING/AI-Portable",
        ".AI/AI-Portable",
    ),
    "Templates": (
        ".TOPICS/.AI/_templates",
        ".AI/Templates",
    ),
    "recludos-filecommander-mcp": (
        ".TOPICS/.AI/.OS/_archive/_LEGACY/recludos-filecommander-mcp",
        ".AI/recludos-filecommander-mcp",
    ),
}


def _resolve_relative_path(relative_paths: tuple[str, ...]) -> Path:
    candidates = [ONEDRIVE_DIR / Path(rel) for rel in relative_paths]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def get_system_path(name: str) -> Path:
    """Gibt den absoluten Pfad zu einem bekannten System zurueck."""
    relative_paths = _SYSTEM_RELATIVE_PATHS.get(name)
    if relative_paths is None:
        raise KeyError(f"Unbekanntes System: {name}")
    return _resolve_relative_path(relative_paths)


def get_bach_system_path(name: str = "BACH_v2_vanilla") -> Path:
    """Gibt den Python-Systempfad einer bekannten BACH-Installation zurueck."""
    return get_system_path(name) / "system"


def get_bach_db_path(name: str = "BACH_v2_vanilla") -> Path:
    """Gibt den Standardpfad zur BACH-Datenbank zurueck."""
    return get_bach_system_path(name) / "data" / "bach.db"


def get_systems_dict() -> dict[str, str]:
    """Gibt ein dict Name->absoluter Pfad fuer alle bekannten Systeme zurueck."""
    return {name: str(get_system_path(name))
            for name in _SYSTEM_RELATIVE_PATHS}


# Abwaertskompatibel: KNOWN_SYSTEMS als dict (wird von compare_systems.py benutzt)
KNOWN_SYSTEMS = get_systems_dict()
