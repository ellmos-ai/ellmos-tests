"""
Zentrale Konfiguration fuer ellmos-tests
=========================================
Alle Pfade und System-Definitionen an einer Stelle.

Konfiguration ueber Umgebungsvariablen:
  ELLMOS_BASE_PATH  - Root des ellmos-tests Projekts
  ELLMOS_ONEDRIVE   - OneDrive-Basispfad (fuer System-Pfade)
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
# Name -> relativer Pfad unter OneDrive (wird dynamisch aufgeloest)

_SYSTEM_RELATIVE_PATHS = {
    "BACH_v1.1":    ".AI/BACH_v1.1",
    "recludOS":     ".AI/recludOS",
    "_BATCH":       ".SOFTWARE/_BATCH",
    "_CHIAH":       ".SOFTWARE/_CHIAH",
    "BACH_STREAM":  ".AI/BACH_STREAM",
    "AI-Portable":  ".AI/AI-Portable",
    "Templates":    ".AI/Templates",
    "recludos-filecommander-mcp": ".AI/recludos-filecommander-mcp",
}


def get_system_path(name: str) -> Path:
    """Gibt den absoluten Pfad zu einem bekannten System zurueck."""
    rel = _SYSTEM_RELATIVE_PATHS.get(name)
    if rel is None:
        raise KeyError(f"Unbekanntes System: {name}")
    return ONEDRIVE_DIR / rel


def get_systems_dict() -> dict[str, str]:
    """Gibt ein dict Name->absoluter Pfad fuer alle bekannten Systeme zurueck."""
    return {name: str(ONEDRIVE_DIR / rel)
            for name, rel in _SYSTEM_RELATIVE_PATHS.items()}


# Abwaertskompatibel: KNOWN_SYSTEMS als dict (wird von compare_systems.py benutzt)
KNOWN_SYSTEMS = get_systems_dict()
