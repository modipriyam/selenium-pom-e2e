import datetime as dt
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.config import CONFIG

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"


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
