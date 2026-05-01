"""
Feature-Mapping Update: BACH_v1.1 hinzufuegen
==============================================
Fuegt BACH_v1.1 als neues System zur feature_mapping.db hinzu
und traegt alle erkannten Feature-Implementierungen ein.

Usage:
    python update_bach_v1_1.py
"""
import sqlite3
import os
import sys
from pathlib import Path

DB_PATH = str(Path(__file__).parent / "feature_mapping.db")

# System-Basispfad ueber zentrale Config
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from system_diff_tests.config import get_system_path

BACH_V1_1_PATH = str(get_system_path("BACH_v1.1"))

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ═══════════════════════════════════════════════════════════════════════════
# 1. BACH_v1.1 als System registrieren
# ═══════════════════════════════════════════════════════════════════════════
cursor.execute("""
    INSERT OR IGNORE INTO systems (name, type, version, entry_point, base_path)
    VALUES (?, ?, ?, ?, ?)
""", ("BACH_v1.1", "system", "1.1.66", "SKILL.md",
      BACH_V1_1_PATH))

# System-ID holen
cursor.execute("SELECT id FROM systems WHERE name = 'BACH_v1.1'")
bach_id = cursor.fetchone()[0]

# Feature-IDs holen
cursor.execute("SELECT id, canonical_name FROM features")
feature_ids = {row[1]: row[0] for row in cursor.fetchall()}

# ═══════════════════════════════════════════════════════════════════════════
# 2. Neue Features die nur BACH_v1.1 hat (noch nicht in der DB)
# ═══════════════════════════════════════════════════════════════════════════
new_features = [
    ("session_partner", "Partner-Sessions", 3, "Partner-spezifische Sessions (claude, gemini)"),
    ("gui_web_dashboard", "Web-Dashboard", 4, "Flask-basiertes Web-Dashboard (25+ Seiten)"),
    ("gui_wiki", "Wiki-System", 4, "Integriertes Wiki mit Editing"),
    ("gui_skills_board", "Skills-Board", 4, "Agenten-Uebersicht mit Sektionen"),
    ("daemon_wartung", "Wartungs-Daemon", 5, "Shell-Jobs ausfuehren"),
    ("task_recurring_system", "Recurring-System", 1, "Wiederkehrende Task-Erinnerungen"),
    ("memory_sessions", "Session-Berichte", 2, "Session-Summaries in DB"),
    ("memory_search", "Assoziative Suche", 2, "Relevanz-basierte Memory-Suche"),
    ("tools_maintain", "Selbstheilung", 6, "heal, registry, skills, docs Checks"),
    ("agents_multi", "Multi-Agenten", 9, "12+ Agenten (beruflich + privat)"),
    ("agents_ati", "ATI-Agent", 9, "Software-Entwickler-Agent mit Bootstrapping"),
    ("agents_steuer", "Steuer-Agent", 9, "Beleg-/Posten-Verwaltung, DATEV-Export"),
    ("comm_partner_system", "Partner-System", 7, "10 Partner, Delegation, Token-Zones"),
    ("session_startup_modes", "Startup-Modi", 3, "gui/text/dual/silent Modi"),
    ("backup_nas", "NAS-Integration", 10, "Backup auf NAS-Speicher"),
    ("docs_help_system", "Help-System", 8, "16+ Hilfe-Themen, kontextuell"),
    ("special_inbox_watcher", "Inbox-Watcher", 6, "Auto-Sort mit Regex-Rules"),
    ("tools_prompt_generator", "Prompt-Generator", 6, "Prompt-Session-Service"),
]

for canonical, display, cat_id, desc in new_features:
    cursor.execute("""
        INSERT OR IGNORE INTO features (canonical_name, display_name, category_id, description)
        VALUES (?, ?, ?, ?)
    """, (canonical, display, cat_id, desc))

# Feature-IDs aktualisieren nach Insert
cursor.execute("SELECT id, canonical_name FROM features")
feature_ids = {row[1]: row[0] for row in cursor.fetchall()}

# ═══════════════════════════════════════════════════════════════════════════
# 3. BACH_v1.1 Implementierungen eintragen
# ═══════════════════════════════════════════════════════════════════════════
bach_implementations = [
    # Task-Management
    ("task_system", "data/bach.db (tasks table)", "sqlite", "implemented"),
    ("task_priorities", "hub/handlers/task_handler.py", "python", "implemented"),
    ("task_scanner", None, None, "not_implemented"),
    ("task_delegation", "hub/handlers/partner_handler.py", "python", "implemented"),
    ("task_recurring_system", "hub/handlers/recurring_handler.py", "python", "implemented"),
    ("special_problems_first", None, None, "planned"),

    # Memory
    ("memory_short_term", "data/bach.db (memory_working)", "sqlite", "implemented"),
    ("memory_long_term", "data/bach.db (memory_facts)", "sqlite", "implemented"),
    ("memory_context_sources", "hub/handlers/memory_handler.py", "python", "implemented"),
    ("memory_lessons_learned", "data/bach.db (memory_lessons)", "sqlite", "implemented"),
    ("memory_archive", "memory/archive/", "folder", "implemented"),
    ("memory_sessions", "data/bach.db (memory_sessions)", "sqlite", "implemented"),
    ("memory_search", "hub/handlers/memory_handler.py", "python", "implemented"),

    # Session-Management
    ("session_dual_mode", "hub/handlers/startup_handler.py", "python", "implemented"),
    ("session_start_protocol", "hub/handlers/startup_handler.py", "python", "implemented"),
    ("session_shutdown_protocol", "hub/handlers/shutdown_handler.py", "python", "implemented"),
    ("session_crash_recovery", None, None, "partial"),
    ("session_snapshots", None, None, "not_implemented"),
    ("session_partner", "hub/handlers/startup_handler.py", "python", "implemented"),
    ("session_startup_modes", "hub/handlers/startup_handler.py", "python", "implemented"),

    # GUI
    ("gui_main", "tools/gui_server.py", "python/flask", "implemented"),
    ("gui_web_dashboard", "tools/gui_server.py (25+ Seiten)", "flask/html", "implemented"),
    ("gui_wiki", "tools/gui_server.py /wiki", "flask/html", "implemented"),
    ("gui_skills_board", "tools/gui_server.py /skills", "flask/html", "implemented"),
    ("gui_dashboard", "tools/gui_server.py /dashboard", "flask/html", "implemented"),
    ("gui_systray", None, None, "not_implemented"),
    ("gui_html_viewer", "tools/gui_server.py", "flask", "implemented"),

    # Daemon/Automatisierung
    ("daemon_headless", None, None, "partial"),
    ("daemon_auto_session", None, None, "not_implemented"),
    ("daemon_wartung", "hub/handlers/daemon_handler.py", "python", "implemented"),
    ("daemon_time_budget", None, None, "not_implemented"),

    # Tools
    ("tools_registry", "data/bach.db (tools table)", "sqlite", "implemented"),
    ("tools_action_hub", "bach.py (CLI-Zentrale)", "python", "implemented"),
    ("tools_dev", "tools/ (45+ Scripts)", "python", "implemented"),
    ("tools_maintenance", "hub/handlers/maintain_handler.py", "python", "implemented"),
    ("tools_maintain", "hub/handlers/maintain_handler.py", "python", "implemented"),
    ("tools_prompt_generator", "skills/_services/prompt_generator/", "python", "implemented"),
    ("special_inbox_watcher", "tools/inbox_watcher.py", "python", "implemented"),
    ("special_directory_watcher", None, None, "not_implemented"),

    # Kommunikation
    ("comm_partner_system", "hub/handlers/partner_handler.py", "python", "implemented"),
    ("comm_async_messaging", "data/bach.db (messages)", "sqlite", "implemented"),
    ("comm_message_box", None, None, "not_implemented"),
    ("comm_multi_ai", "hub/handlers/partner_handler.py", "python", "implemented"),
    ("comm_contacts", None, None, "not_implemented"),

    # Dokumentation
    ("docs_system", "docs/", "markdown", "implemented"),
    ("docs_directory_truth", "data/bach.db (files_truth)", "sqlite", "implemented"),
    ("docs_rules", "docs/CONCEPT_*.md", "markdown", "implemented"),
    ("docs_best_practices", "docs/", "markdown", "implemented"),
    ("docs_help_system", "help/ (16+ Themen)", "txt", "implemented"),

    # Agenten
    ("agents_system", "skills/_agents/ (12+)", "python/md", "implemented"),
    ("agents_multi", "skills/_agents/", "python/md", "implemented"),
    ("agents_ati", "skills/_agents/ati/", "python/md", "implemented"),
    ("agents_steuer", "skills/_agents/steuer-agent.txt", "python", "implemented"),
    ("agents_services", "skills/_services/", "python", "implemented"),
    ("agents_actors_model", None, None, "not_implemented"),
    ("agents_think_modules", None, None, "not_implemented"),

    # Backup
    ("backup_auto", "hub/handlers/backup_handler.py", "python", "implemented"),
    ("backup_nas", "hub/handlers/backup_handler.py", "python", "implemented"),
    ("backup_trash", "data/bach.db (files_trash)", "sqlite", "implemented"),

    # RAG
    ("rag_pipeline", None, None, "not_implemented"),
    ("rag_vector_store", None, None, "not_implemented"),
    ("rag_local_models", None, None, "not_implemented"),

    # Datei-Ops (nicht direkt - laeuft ueber MCP/Claude)
    ("file_crud", None, None, "not_implemented"),
    ("file_search", None, None, "not_implemented"),
    ("file_sessions", None, None, "not_implemented"),
    ("file_process_mgmt", None, None, "not_implemented"),

    # Spezial
    ("special_injectors", "data/bach.db (automation_injectors)", "sqlite", "implemented"),
    ("special_transfer_port", None, None, "not_implemented"),
    ("special_mapping", None, None, "not_implemented"),
    ("special_ollama", None, None, "not_implemented"),
]

for canonical, path, tech, status in bach_implementations:
    fid = feature_ids.get(canonical)
    if fid and status in ("implemented", "partial"):
        cursor.execute("""
            INSERT OR IGNORE INTO implementations (feature_id, system_id, path, technology, status)
            VALUES (?, ?, ?, ?, ?)
        """, (fid, bach_id, path, tech, status))

conn.commit()

# ═══════════════════════════════════════════════════════════════════════════
# STATISTIK
# ═══════════════════════════════════════════════════════════════════════════
cursor.execute("""
    SELECT COUNT(*) FROM implementations WHERE system_id = ?
""", (bach_id,))
impl_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM features")
total_features = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM systems")
total_systems = cursor.fetchone()[0]

print(f"BACH_v1.1 hinzugefuegt!")
print(f"  System-ID: {bach_id}")
print(f"  Implementierungen: {impl_count}")
print(f"  Gesamt-Features in DB: {total_features}")
print(f"  Gesamt-Systeme in DB: {total_systems}")

conn.close()
