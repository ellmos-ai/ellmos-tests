# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank fuer Ihr Interesse, zu diesem Projekt beizutragen!

### Wie Sie beitragen koennen

1. **Bug melden:** Erstellen Sie ein Issue mit dem Label `bug`
2. **Feature vorschlagen:** Erstellen Sie ein Issue mit dem Label `enhancement`
3. **Code beitragen:** Erstellen Sie einen Pull Request

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`
3. Committen Sie Ihre Aenderungen: `git commit -m "Beschreibung der Aenderung"`
4. Pushen Sie den Branch: `git push origin feature/mein-feature`
5. Erstellen Sie einen Pull Request

### Developer Certificate of Origin (DCO)

Dieses Projekt verwendet den [Developer Certificate of Origin (DCO)](https://developercertificate.org/).
Bitte signieren Sie jeden Commit mit `--signoff`:

    git commit --signoff -m "Beschreibung der Aenderung"

Damit bestaetigen Sie, dass Sie das Recht haben, den Code unter der Projektlizenz einzureichen.

### Code-Richtlinien

- Python: PEP 8 Stil, kompatibel mit **Python 3.10+**
- Encoding: UTF-8 fuer alle Dateien
- Sprache: Code und Kommentare auf Deutsch oder Englisch
- Keine hardcoded Pfade oder API-Keys
- Moeglichst nur Standardbibliothek-Abhaengigkeiten verwenden

### Neue Tests hinzufuegen

#### B-Tests (Beobachtung)
- Neue Skripte in `system_diff_tests/testing/b_tests/` ablegen
- Namenskonvention: `B0XX_description.py`
- Jeder Test muss ein JSON-Ergebnis mit mindestens einem `score`-Feld ausgeben

#### O-Tests (Ausgabe)
- Neue Skripte in `system_diff_tests/testing/o_tests/` ablegen
- Namenskonvention: `O0XX_description.py`
- Tests muessen einen Systempfad als Argument akzeptieren

#### E-Tests (Erfahrung)
- Aufgabendefinitionen in die E-Test-Dateien einfuegen
- E-Tests sind subjektiv und werden manuell ausgefuehrt -- Bewertungskriterien klar dokumentieren

#### Testbatterien
- Neue Batterie-Dateien in `tests/batteries/` ablegen
- Eine Test-ID pro Zeile, Kommentare mit `#`

### Erste Schritte

```bash
git clone https://github.com/ellmos-ai/ellmos-tests.git
cd ellmos-tests
pip install -r requirements.txt
python system_diff_tests/run_all.py "/pfad/zum/llm-os"
```

---

## English

Thank you for your interest in contributing to this project!

### How to Contribute

1. **Report bugs:** Create an issue with the `bug` label
2. **Suggest features:** Create an issue with the `enhancement` label
3. **Contribute code:** Create a Pull Request

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Description of change"`
4. Push the branch: `git push origin feature/my-feature`
5. Create a Pull Request

### Developer Certificate of Origin (DCO)

This project uses the [Developer Certificate of Origin (DCO)](https://developercertificate.org/).
Please sign off every commit with `--signoff`:

    git commit --signoff -m "Description of change"

This certifies that you have the right to submit the code under the project license.

### Code Guidelines

- Python: PEP 8 style, compatible with **Python 3.10+**
- Encoding: UTF-8 for all files
- Language: Code and comments in German or English
- No hardcoded paths or API keys
- Use only standard library dependencies where possible

### Adding New Tests

#### B-Tests (Observation)
- Place new scripts in `system_diff_tests/testing/b_tests/`
- Follow the naming convention: `B0XX_description.py`
- Each test must output a JSON result with at minimum a `score` field

#### O-Tests (Output)
- Place new scripts in `system_diff_tests/testing/o_tests/`
- Follow the naming convention: `O0XX_description.py`
- Tests must accept a system path as argument

#### E-Tests (Experience)
- Add task definitions to the E-Test task files
- E-Tests are subjective and manually executed — document the evaluation criteria clearly

#### Test Batteries
- Add new battery files to `tests/batteries/`
- One test ID per line, comments with `#`

### Getting Started

```bash
git clone https://github.com/ellmos-ai/ellmos-tests.git
cd ellmos-tests
pip install -r requirements.txt
python system_diff_tests/run_all.py "/path/to/your/llm-os"
```

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
