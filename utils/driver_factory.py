"""Create Selenium WebDriver instances configured for local and CI runs."""
from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver

from utils.config import CONFIG

log = logging.getLogger(__name__)


def _chrome(headless: bool) -> WebDriver:
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    # Stable defaults for CI containers where /dev/shm is tiny and there is no GPU.
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument(f"--window-size={CONFIG.window_width},{CONFIG.window_height}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(service=ChromeService(), options=opts)


def _firefox(headless: bool) -> WebDriver:
    opts = FirefoxOptions()
    if headless:
        opts.add_argument("-headless")
    opts.add_argument(f"--width={CONFIG.window_width}")
    opts.add_argument(f"--height={CONFIG.window_height}")
    return webdriver.Firefox(service=FirefoxService(), options=opts)


def build_driver() -> WebDriver:
    log.info("Launching %s (headless=%s)", CONFIG.browser, CONFIG.headless)
    if CONFIG.browser == "chrome":
        driver = _chrome(CONFIG.headless)
    elif CONFIG.browser == "firefox":
        driver = _firefox(CONFIG.headless)
    else:
        raise ValueError(f"Unsupported browser: {CONFIG.browser!r}")

    if CONFIG.implicit_wait > 0:
        driver.implicitly_wait(CONFIG.implicit_wait)
    driver.set_page_load_timeout(60)
    return driver
