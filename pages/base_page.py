from __future__ import annotations

import logging
import time
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
        # Native .click() sometimes no-ops on SauceDemo's React buttons in
        # headless Chrome; scroll-into-view + JS click is reliable.
        element = self._clickable(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
            element,
        )

    def native_click(self, locator: Locator) -> None:
        self._clickable(locator).click()

    def type_text(self, locator: Locator, value: str, clear_first: bool = True) -> None:
        element = self._visible(locator)
        element.click()
        if clear_first:
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
        element.send_keys(value)

        # React can drop the value if send_keys races with a re-render;
        # if that happens, set the value via JS and fire input/change events.
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

    def pause(self, seconds: float | None = None) -> None:
        delay = CONFIG.step_delay if seconds is None else seconds
        if delay > 0:
            time.sleep(delay)
