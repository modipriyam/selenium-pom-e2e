from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    url_path = "/"

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_BANNER = (By.CSS_SELECTOR, "[data-test='error']")

    def login(self, username, password):
        self.type_text(self.USERNAME, username)
        self.type_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)
        return InventoryPage(self.driver)

    def error_message(self):
        return self.text_of(self.ERROR_BANNER)

    def has_error(self):
        return self.is_visible(self.ERROR_BANNER, timeout=3)
