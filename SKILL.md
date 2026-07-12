---
name: ellmos-tests
version: 0.2.0
type: skill
author: Lukas Geiger
created: 2026-06-18
updated: 2026-06-18
anthropic_compatible: true
standalone: true
category: testing
tags: [ellmos, llm-os, testing, evaluation, b-tests, o-tests, e-tests]
dependencies:
  tools: []
  services: []
  protocols: []
description: >
  Standalone B/O/E testkit for evaluating SKILL.md-based LLM operating systems.
---

# ellmos-tests

Use this module when an LLM should evaluate a local LLM-OS, agent hub, or SKILL.md-based system with the B/O/E method.

## What It Provides

- B-tests: automated observation tests for inventory, structure, naming, docs, code metrics, dependencies, and age.
- O-tests: functional output tests for task, memory, tool registry, backup, config, and export/import surfaces.
- E-tests: manual experience tasks for orientation, memory, task workflows, tool use, recovery, and session startup.
- Battery runner: curated checklist-style batteries under `tests/batteries/`.
- Optional browser helpers: Playwright wrappers under `system_diff_tests/testing/playwright/`.

## Standard Commands

```bash
PYTHONIOENCODING=utf-8 python system_diff_tests/run_all.py "<system_path>" --only b
PYTHONIOENCODING=utf-8 python system_diff_tests/run_all.py "<system_path>" --only o
PYTHONIOENCODING=utf-8 python system_diff_tests/testing/run_external.py "<system_path>" --profile STANDARD
PYTHONIOENCODING=utf-8 python tests/run_batteries.py --list
```

Known systems are resolved through `system_diff_tests/config.py`.

## Boundaries

- Results are generated under ignored output folders by default.
- Do not include private corpora, local BACH context, `.db` files, result archives, `__pycache__`, or `.pytest_cache` in the module package.
- Prefer environment variables (`ELLMOS_BASE_PATH`, `ELLMOS_ONEDRIVE`, `BACH_SYSTEM_PATH`, `BACH_DB_PATH`) over hardcoded user paths.
- Playwright is optional; the core module remains Python-stdlib only.

## Extraction Note

This module preserves the portable part of BACH `system/tools/testing`. BACH remains the upstream feature source, while `ellmos-tests` is the standalone module surface for reuse across ellmos, Sovereign, and other LLM-OS systems.
