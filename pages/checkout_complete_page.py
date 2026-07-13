from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    url_path = "/checkout-complete.html"

    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    COMPLETE_TEXT = (By.CLASS_NAME, "complete-text")
    BACK_HOME = (By.ID, "back-to-products")
    PONY_IMAGE = (By.CLASS_NAME, "pony_express")

    def is_loaded(self) -> bool:
        return self.is_visible(self.COMPLETE_HEADER)

    def confirmation_header(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)

    def confirmation_body(self) -> str:
        return self.text_of(self.COMPLETE_TEXT)

    def order_is_confirmed(self) -> bool:
        header = self.confirmation_header().lower()
        return "thank you for your order" in header
