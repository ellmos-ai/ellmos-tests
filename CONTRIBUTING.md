# Contributing to ellmos-tests

Thank you for your interest in contributing!

## How to Contribute

1. **Fork** the repository
2. **Create a branch** for your feature or fix (`git checkout -b feature/my-feature`)
3. **Make your changes** and test them
4. **Commit** with a clear message
5. **Push** your branch and open a **Pull Request**

## Guidelines

- Keep Python code compatible with **Python 3.10+**
- Use only standard library dependencies where possible
- Follow existing code style and naming conventions
- Add or update tests when adding new functionality
- Test results (JSON files) should not be committed

## Adding New Tests

### B-Tests (Observation)
- Place new scripts in `system_diff_tests/testing/b_tests/`
- Follow the naming convention: `B0XX_description.py`
- Each test must output a JSON result with at minimum a `score` field

### O-Tests (Output)
- Place new scripts in `system_diff_tests/testing/o_tests/`
- Follow the naming convention: `O0XX_description.py`
- Tests must accept a system path as argument

### E-Tests (Experience)
- Add task definitions to the E-Test task files
- E-Tests are subjective and manually executed — document the evaluation criteria clearly

### Test Batteries
- Add new battery files to `tests/batteries/`
- One test ID per line, comments with `#`

## Reporting Issues

Use the GitHub issue templates for bug reports and feature requests.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
