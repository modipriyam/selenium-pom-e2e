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
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator, value):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(value)

    def text_of(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def is_visible(self, locator, timeout=None):
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False
