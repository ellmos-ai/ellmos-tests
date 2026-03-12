"""
Feature-Mapping - Query Tool
Synopsen und Vergleiche generieren
"""
import sqlite3
import sys
import json
from pathlib import Path
from typing import Optional

# Zentrale Config importieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DB_PATH as _DB_PATH

DB_PATH = str(_DB_PATH)

def get_connection():
    return sqlite3.connect(DB_PATH)

# ═══════════════════════════════════════════════════════════════════════════
# FEATURE-MATRIX
# ═══════════════════════════════════════════════════════════════════════════
def feature_matrix(category: Optional[str] = None):
    """Zeigt welches System welches Feature hat"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        f.display_name as Feature,
        fc.name as Kategorie,
        GROUP_CONCAT(DISTINCT s.name || ':' || i.status) as Systeme
    FROM features f
    LEFT JOIN feature_categories fc ON f.category_id = fc.id
    LEFT JOIN implementations i ON f.id = i.feature_id
    LEFT JOIN systems s ON i.system_id = s.id
    """
    
    if category:
        query += f" WHERE fc.name LIKE '%{category}%'"
    
    query += " GROUP BY f.id ORDER BY fc.name, f.display_name"
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n" + "="*80)
    print("FEATURE-MATRIX")
    print("="*80)
    
    current_cat = None
    for row in results:
        feature, cat, systems = row
        if cat != current_cat:
            print(f"\n--- {cat or 'Keine Kategorie'} ---")
            current_cat = cat
        
        systems_parsed = []
        if systems:
            for s in systems.split(','):
                if s:
                    parts = s.split(':')
                    if len(parts) == 2:
                        name, status = parts
                        icon = "+" if status == "implemented" else "~" if status == "partial" else "?"
                        systems_parsed.append(f"{icon}{name}")
        
        print(f"  {feature}: {', '.join(systems_parsed) if systems_parsed else '-'}")
    
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# FEATURE-SYNOPSE
# ═══════════════════════════════════════════════════════════════════════════
def feature_synopsis(feature_name: str):
    """Vergleicht ein Feature ueber alle Systeme"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        f.display_name,
        f.description,
        s.name as system_name,
        i.path,
        i.technology,
        i.status,
        GROUP_CONCAT(fa.alias) as aliase
    FROM features f
    LEFT JOIN implementations i ON f.id = i.feature_id
    LEFT JOIN systems s ON i.system_id = s.id
    LEFT JOIN feature_aliases fa ON f.id = fa.feature_id AND (fa.system_id = s.id OR fa.system_id IS NULL)
    WHERE f.canonical_name LIKE ? OR f.display_name LIKE ?
    GROUP BY f.id, s.id
    """, (f"%{feature_name}%", f"%{feature_name}%"))
    
    results = cursor.fetchall()
    
    if not results:
        print(f"Kein Feature gefunden fuer: {feature_name}")
        return
    
    print("\n" + "="*80)
    print(f"SYNOPSE: {results[0][0]}")
    print(f"Beschreibung: {results[0][1]}")
    print("="*80)
    
    for row in results:
        _, _, system, path, tech, status, aliases = row
        if system:
            status_icon = "[+]" if status == "implemented" else "[~]" if status == "partial" else "[?]"
            print(f"\n{status_icon} {system}")
            print(f"    Pfad: {path or '-'}")
            print(f"    Technologie: {tech or '-'}")
            if aliases:
                print(f"    Aliase: {aliases}")
    
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# FEATURE-LUECKEN
# ═══════════════════════════════════════════════════════════════════════════
def feature_gaps(system_name: Optional[str] = None):
    """Zeigt Features die einem System fehlen"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        s.name as system_name,
        f.display_name as missing_feature,
        fc.name as category
    FROM systems s
    CROSS JOIN features f
    LEFT JOIN feature_categories fc ON f.category_id = fc.id
    LEFT JOIN implementations i ON f.id = i.feature_id AND i.system_id = s.id
    WHERE i.id IS NULL
    """
    
    if system_name:
        query += f" AND s.name = '{system_name}'"
    
    query += " ORDER BY s.name, fc.name"
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n" + "="*80)
    print("FEATURE-LUECKEN" + (f" - {system_name}" if system_name else ""))
    print("="*80)
    
    current_system = None
    for row in results:
        system, feature, category = row
        if system != current_system:
            print(f"\n--- {system} ---")
            current_system = system
        print(f"  [-] {feature} ({category})")
    
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# ALIAS-SUCHE
# ═══════════════════════════════════════════════════════════════════════════
def find_by_alias(alias: str):
    """Findet Features anhand eines Alias (Dateiname, Ordner, Konzept)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        f.display_name,
        f.canonical_name,
        fa.alias,
        fa.alias_type,
        s.name as system_specific
    FROM feature_aliases fa
    JOIN features f ON fa.feature_id = f.id
    LEFT JOIN systems s ON fa.system_id = s.id
    WHERE fa.alias LIKE ?
    """, (f"%{alias}%",))
    
    results = cursor.fetchall()
    
    print("\n" + "="*80)
    print(f"ALIAS-SUCHE: '{alias}'")
    print("="*80)
    
    for row in results:
        display, canonical, alias_val, alias_type, system_spec = row
        system_info = f" (nur {system_spec})" if system_spec else ""
        print(f"  '{alias_val}' [{alias_type}] -> {display}{system_info}")
    
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# TECHNOLOGIE-VERGLEICH
# ═══════════════════════════════════════════════════════════════════════════
def tech_comparison():
    """Vergleicht Technologie-Nutzung pro System"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        s.name,
        i.technology,
        COUNT(*) as count
    FROM implementations i
    JOIN systems s ON i.system_id = s.id
    WHERE i.technology IS NOT NULL
    GROUP BY s.name, i.technology
    ORDER BY s.name, count DESC
    """)
    
    results = cursor.fetchall()
    
    print("\n" + "="*80)
    print("TECHNOLOGIE-VERGLEICH")
    print("="*80)
    
    current_system = None
    for row in results:
        system, tech, count = row
        if system != current_system:
            print(f"\n{system}:")
            current_system = system
        print(f"  {tech}: {count}x")
    
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM-PROFIL
# ═══════════════════════════════════════════════════════════════════════════
def system_profile(system_name: str):
    """Zeigt alle Features eines Systems"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        s.name, s.type, s.version, s.entry_point
    FROM systems s
    WHERE s.name = ?
    """, (system_name,))
    
    sys_info = cursor.fetchone()
    if not sys_info:
        print(f"System nicht gefunden: {system_name}")
        return
    
    print("\n" + "="*80)
    print(f"SYSTEM-PROFIL: {sys_info[0]}")
    print(f"Typ: {sys_info[1]} | Version: {sys_info[2]} | Entry: {sys_info[3]}")
    print("="*80)
    
    cursor.execute("""
    SELECT 
        fc.name as category,
        f.display_name,
        i.technology,
        i.status,
        i.path
    FROM implementations i
    JOIN features f ON i.feature_id = f.id
    JOIN systems s ON i.system_id = s.id
    LEFT JOIN feature_categories fc ON f.category_id = fc.id
    WHERE s.name = ?
    ORDER BY fc.name, f.display_name
    """, (system_name,))
    
    results = cursor.fetchall()
    
    current_cat = None
    for row in results:
        cat, feature, tech, status, path = row
        if cat != current_cat:
            print(f"\n--- {cat or 'Sonstige'} ---")
            current_cat = cat
        status_icon = "[+]" if status == "implemented" else "[~]"
        print(f"  {status_icon} {feature} ({tech}) - {path or '-'}")
    
    print(f"\nTotal: {len(results)} Features")
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
BACH_STREAM Feature-Mapping Query Tool
=====================================
Befehle:
  matrix [kategorie]     - Feature-Matrix anzeigen
  synopsis <feature>     - Feature-Synopse erstellen
  gaps [system]          - Feature-Luecken anzeigen
  alias <suchbegriff>    - Nach Alias suchen
  tech                   - Technologie-Vergleich
  profile <system>       - System-Profil anzeigen
  
Beispiele:
  python query_db.py matrix Memory
  python query_db.py synopsis task_system
  python query_db.py gaps _CHIAH
  python query_db.py alias MEMORY.md
  python query_db.py profile recludOS
""")
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "matrix":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        feature_matrix(category)
    elif cmd == "synopsis":
        if len(sys.argv) < 3:
            print("Fehler: Feature-Name erforderlich")
        else:
            feature_synopsis(sys.argv[2])
    elif cmd == "gaps":
        system = sys.argv[2] if len(sys.argv) > 2 else None
        feature_gaps(system)
    elif cmd == "alias":
        if len(sys.argv) < 3:
            print("Fehler: Suchbegriff erforderlich")
        else:
            find_by_alias(sys.argv[2])
    elif cmd == "tech":
        tech_comparison()
    elif cmd == "profile":
        if len(sys.argv) < 3:
            print("Fehler: System-Name erforderlich")
        else:
            system_profile(sys.argv[2])
    else:
        print(f"Unbekannter Befehl: {cmd}")
