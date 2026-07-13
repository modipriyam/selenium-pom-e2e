from __future__ import annotations

import datetime as dt
import logging
import os
from pathlib import Path
from typing import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from utils.config import CONFIG
from utils.driver_factory import build_driver

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"


def pytest_configure(config: pytest.Config) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    log.info(
        "E2E config | base_url=%s browser=%s headless=%s",
        CONFIG.base_url,
        CONFIG.browser,
        CONFIG.headless,
    )


@pytest.fixture()
def driver(request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    drv = build_driver()
    request.node._driver = drv
    try:
        yield drv
    finally:
        drv.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    drv: WebDriver | None = getattr(item, "_driver", None)
    if drv is None:
        return

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = item.name.replace("/", "_").replace("[", "_").replace("]", "_")
    path = SCREENSHOTS_DIR / f"{safe_name}-{timestamp}.png"
    try:
        drv.save_screenshot(str(path))
        log.error("Saved failure screenshot: %s", path)
        if os.getenv("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
                fh.write(f"- Failure screenshot: `{path.relative_to(ROOT_DIR)}`\n")
    except Exception as exc:
        log.warning("Could not save screenshot for %s: %s", item.name, exc)
