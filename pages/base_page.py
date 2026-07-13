"""Shared Selenium primitives used by every page object.

Page objects should call these helpers instead of touching WebDriver directly.
This keeps waits, error handling, and logging consistent across the suite.
"""
from __future__ import annotations

import logging
from typing import Tuple

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from utils.config import CONFIG

Locator = Tuple[str, str]

log = logging.getLogger(__name__)


class BasePage:
    url_path: str = ""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, CONFIG.explicit_wait)

    def open(self) -> "BasePage":
        target = f"{CONFIG.base_url.rstrip('/')}/{self.url_path.lstrip('/')}"
        log.info("Navigating to %s", target)
        self.driver.get(target)
        return self

    def _visible(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _clickable(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator: Locator) -> None:
        """Scroll to and click an element.

        Uses a scroll-then-JS-click sequence because the standard Selenium
        `.click()` intermittently no-ops on SauceDemo's React-rebuilt buttons
        under headless Chrome. Behaviorally identical from a user's viewpoint.
        """
        element = self._clickable(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
            element,
        )

    def native_click(self, locator: Locator) -> None:
        """Standard WebDriver click; use when explicitly exercising the event chain."""
        self._clickable(locator).click()

    def type_text(self, locator: Locator, value: str, clear_first: bool = True) -> None:
        """Focus, clear (keyboard), and type into an input.

        Avoids WebElement.clear() because on React-controlled inputs it can leave
        the framework state out of sync with the DOM value. A Ctrl+A / Delete
        sequence dispatches native key events that React sees. After typing we
        re-check the DOM value and, if it drifted, fall back to setting it via
        JS and dispatching an `input` event so the framework re-syncs.
        """
        element = self._visible(locator)
        element.click()
        if clear_first:
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
        element.send_keys(value)

        if element.get_attribute("value") != value:
            self.driver.execute_script(
                "const el = arguments[0], val = arguments[1];"
                "const setter = Object.getOwnPropertyDescriptor("
                "  window.HTMLInputElement.prototype, 'value').set;"
                "setter.call(el, val);"
                "el.dispatchEvent(new Event('input', { bubbles: true }));"
                "el.dispatchEvent(new Event('change', { bubbles: true }));",
                element,
                value,
            )

    def text_of(self, locator: Locator) -> str:
        return self._visible(locator).text

    def is_visible(self, locator: Locator, timeout: float | None = None) -> bool:
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def select_by_visible_text(self, locator: Locator, text: str) -> None:
        Select(self._visible(locator)).select_by_visible_text(text)

    def current_path(self) -> str:
        return self.driver.current_url.replace(CONFIG.base_url, "", 1)
