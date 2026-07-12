#!/usr/bin/env python3
"""Capture browser console messages from a page."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--output", default="system_diff_tests/output/playwright/console.log")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    console_logs: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        def handle_console_message(message):
            entry = f"[{message.type}] {message.text}"
            console_logs.append(entry)
            print(entry)

        page.on("console", handle_console_message)
        page.goto(args.url)
        page.wait_for_load_state("networkidle")
        browser.close()

    output.write_text("\n".join(console_logs), encoding="utf-8")
    print(f"Saved {len(console_logs)} console messages to {output}")


if __name__ == "__main__":
    main()
