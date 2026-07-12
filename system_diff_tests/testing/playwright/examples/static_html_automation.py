#!/usr/bin/env python3
"""Open a local HTML file and save a screenshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    parser.add_argument("--screenshot", default="system_diff_tests/output/playwright/static_page.png")
    args = parser.parse_args()

    html_file = Path(args.html_file).resolve()
    if not html_file.exists():
        raise SystemExit(f"HTML file not found: {html_file}")

    screenshot = Path(args.screenshot)
    screenshot.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(html_file.as_uri())
        page.screenshot(path=str(screenshot), full_page=True)
        browser.close()

    print(f"Screenshot saved to {screenshot}")


if __name__ == "__main__":
    main()
