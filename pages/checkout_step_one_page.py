from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_step_two_page import CheckoutStepTwoPage


class CheckoutStepOnePage(BasePage):
    url_path = "/checkout-step-one.html"

    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE = (By.ID, "continue")
    ERROR_BANNER = (By.CSS_SELECTOR, "[data-test='error']")

    def fill_customer_information(self, first_name, last_name, postal_code):
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.POSTAL_CODE, postal_code)
        return self

    def submit(self):
        self.click(self.CONTINUE)
        return CheckoutStepTwoPage(self.driver)

    def error_message(self):
        return self.text_of(self.ERROR_BANNER)

    def has_error(self):
        return self.is_visible(self.ERROR_BANNER, timeout=3)
