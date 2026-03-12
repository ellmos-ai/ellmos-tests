# BACH Testinfrastruktur (SQ027)

**Stand:** 2026-03-12 | **Bezug:** MASTERPLAN SQ027

---

## Struktur

```
tests/
├── batteries/              # Testbatterien (Listen von Test-IDs)
│   ├── release_smoke.txt           # Smoke Test vor jedem Release (KRITISCH)
│   ├── vernunft_kantian.txt        # 7-dimensionaler Vernunftstest (SQ036)
│   ├── usecases.txt                # 49+ Use Cases (SQ014)
│   ├── db_integrity.txt            # Datenbankintegritaet
│   ├── dist_type_check.txt         # Distribution-Klassifizierung
│   ├── llm_agnostic.txt            # LLM-Agnostik Tests
│   ├── connector_tests.txt         # Connector/Bridge Tests
│   ├── registration.txt            # Registrierungstests
│   ├── swarm_search.txt            # Schwarm-Suche Tests
│   ├── system_integration.txt      # System-Integration
│   └── user_experience.txt         # UX-Tests
├── results/                # Testergebnisse (YYYY-MM-DD_batterie.json)
├── interpretations/        # Auswertungen als Markdown
├── run_batteries.py        # Automatischer Test-Runner (NEU)
├── run_db_tests.py         # DB-spezifische Tests
└── README.md               # Diese Datei
```

## Perspektiven (aus BACH_STREAM Testkonzept)

- **B-Tests (Beobachtung):** Statisch, automatisiert. Was IST im System?
- **O-Tests (Ausgabe):** Funktional, Input->Output. Was TUT das System?
- **E-Tests (Erfahrung):** Prozessual, subjektiv. Wie FUEHLT sich das System an?

## Battery Runner (run_batteries.py)

Der automatische Test-Runner liest Battery-Dateien und fuehrt automatisierbare Tests aus.

### Verfuegbare Kommandos

```bash
# Alle Batterien auflisten
python tests/run_batteries.py --list

# Eine bestimmte Batterie ausfuehren
python tests/run_batteries.py --battery release_smoke --system-path "C:\pfad\zum\system"

# Alle Batterien ausfuehren
python tests/run_batteries.py --all --system-path "C:\pfad\zum\system"

# Ausfuehrliche Ausgabe
python tests/run_batteries.py --battery db_integrity --system-path "C:\pfad\zum\system" -v
```

### Was wird automatisch getestet?

| Pruefmethode      | Automatisiert? | Beschreibung                     |
|:------------------|:--------------:|:---------------------------------|
| os.path.exists()  | Ja             | Dateien/Ordner Existenz-Checks   |
| subprocess        | Ja             | Python-Befehle ausfuehren        |
| SQL               | Ja             | SQLite-Queries gegen bach.db     |
| grep              | Teilweise      | Pattern-Suche in Dateien         |
| Manuell (E-Tests) | Nein           | Subjektive Bewertung erforderlich|

### Ausgabe

- Farbige Ausgabe im Terminal (gruen=PASS, rot=FAIL, gelb=SKIP)
- Zusammenfassung pro Batterie und Gesamtergebnis
- `NO_COLOR` Umgebungsvariable deaktiviert Farben

## Workflow

```
1. Batterie auswaehlen:        python run_batteries.py --list
2. Tests ausfuehren:           python run_batteries.py --battery NAME --system-path PFAD
3. Ergebnis in results/ ablegen (YYYY-MM-DD_batterie.json)
4. Interpretation in interpretations/ schreiben
5. Aufgaben ableiten -> MASTERPLAN Sidequests
```

## Release-Pflicht

**release_smoke.txt** MUSS vor jedem Release bestanden sein.
Kein Release ohne gruenen Smoke-Test.

## Konfiguration

System-Pfade werden ueber `system_diff_tests/config.py` zentral verwaltet.
Umgebungsvariablen:

- `ELLMOS_BASE_PATH` - Root des ellmos-tests Projekts
- `ELLMOS_ONEDRIVE` - OneDrive-Basispfad (Default: ~/OneDrive)
- `NO_COLOR` - Farbausgabe deaktivieren
- `FORCE_COLOR` - Farbausgabe erzwingen
