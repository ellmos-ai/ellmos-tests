#!/usr/bin/env python3
"""Print basic interactive elements from a page and save a screenshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--screenshot", default="system_diff_tests/output/playwright/page_discovery.png")
    args = parser.parse_args()

    screenshot = Path(args.screenshot)
    screenshot.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(args.url)
        page.wait_for_load_state("networkidle")

        buttons = page.locator("button").all()
        print(f"Buttons: {len(buttons)}")
        for index, button in enumerate(buttons):
            text = button.inner_text() if button.is_visible() else "[hidden]"
            print(f"  [{index}] {text}")

        links = page.locator("a[href]").all()
        print(f"Links: {len(links)}")
        for link in links[:20]:
            print(f"  - {link.inner_text().strip()} -> {link.get_attribute('href')}")

        inputs = page.locator("input, textarea, select").all()
        print(f"Inputs: {len(inputs)}")
        for field in inputs:
            name = field.get_attribute("name") or field.get_attribute("id") or "[unnamed]"
            field_type = field.get_attribute("type") or "text"
            print(f"  - {name} ({field_type})")

        page.screenshot(path=str(screenshot), full_page=True)
        browser.close()

    print(f"Screenshot saved to {screenshot}")


if __name__ == "__main__":
    main()
