# Playwright Helpers

- Source lineage: BACH `system/tools/testing/playwright`
- Original upstream noted by BACH: `anthropics/skills`, `skills/webapp-testing/`, commit `a5bcdd7`, Apache-2.0
- Module integration: adapted for ellmos-tests on 2026-06-18

## Changes From BACH Copy

- Output paths are relative and portable.
- Example URLs and selectors are CLI arguments instead of hardcoded test targets.
- The helpers remain optional; core ellmos-tests has no Playwright dependency.
