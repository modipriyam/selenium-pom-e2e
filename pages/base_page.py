from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import CONFIG


class BasePage:
    """Shared helpers for every page object."""

    url_path = ""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, CONFIG.explicit_wait)

    def open(self):
        self.driver.get(f"{CONFIG.base_url.rstrip('/')}/{self.url_path.lstrip('/')}")
        return self

    def click(self, locator):
        # Native .click() silently no-ops on SauceDemo's React buttons in
        # headless Chrome. Scroll into view + JS click is reliable.
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
            el,
        )

    def type_text(self, locator, value):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(value)

        # send_keys can race with a React re-render and leave the field empty.
        # If that happens, force the value in via the native setter.
        if el.get_attribute("value") != value:
            self.driver.execute_script(
                "const el = arguments[0], val = arguments[1];"
                "const setter = Object.getOwnPropertyDescriptor("
                "  window.HTMLInputElement.prototype, 'value').set;"
                "setter.call(el, val);"
                "el.dispatchEvent(new Event('input', { bubbles: true }));"
                "el.dispatchEvent(new Event('change', { bubbles: true }));",
                el,
                value,
            )

    def text_of(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def is_visible(self, locator, timeout=None):
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False
