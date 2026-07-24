import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.config import CONFIG

ROOT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"
REPORT_PATH = ROOT_DIR / "reports" / "report.html"


def _build_driver():
    opts = Options()
    if CONFIG.headless:
        opts.add_argument("--headless=new")
        # needed in CI containers
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)


@pytest.fixture()
def driver(request):
    drv = _build_driver()
    request.node._driver = drv
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # save a screenshot when a test fails
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    drv = getattr(item, "_driver", None)
    if drv is None:
        return
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    drv.save_screenshot(str(SCREENSHOTS_DIR / f"{item.name}-{stamp}.png"))


def pytest_sessionfinish(session, exitstatus):
    # auto-open the HTML report locally; opt out with E2E_OPEN_REPORT=false or in CI
    if os.environ.get("CI"):
        return
    if os.environ.get("E2E_OPEN_REPORT", "true").lower() in {"0", "false", "no"}:
        return
    if not REPORT_PATH.exists():
        return
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(REPORT_PATH)])
        elif sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(REPORT_PATH)])
        elif sys.platform == "win32":
            os.startfile(str(REPORT_PATH))  # type: ignore[attr-defined]
    except Exception:
        pass
