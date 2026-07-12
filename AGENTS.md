# AGENTS.md

This repository uses `SKILL.md` as the LLM-facing operating instruction.

Read in this order before editing or running tests:

1. `SKILL.md`
2. `README.md`
3. `system_diff_tests/testing_workflow.md`
4. `tests/README.md`

Rules:

- Keep the module standalone and user-neutral.
- Do not commit generated outputs, caches, private BACH context, databases, or local result archives.
- Prefer small compatibility additions over breaking the historical `system_diff_tests/testing/` layout.
- Run `PYTHONIOENCODING=utf-8 python -m unittest discover -s tests -p "test_*.py"` after code changes.
