from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    url_path = "/checkout-complete.html"

    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")

    def is_loaded(self):
        return self.is_visible(self.COMPLETE_HEADER)

    def confirmation_header(self):
        return self.text_of(self.COMPLETE_HEADER)

    def order_is_confirmed(self):
        return "thank you for your order" in self.confirmation_header().lower()
