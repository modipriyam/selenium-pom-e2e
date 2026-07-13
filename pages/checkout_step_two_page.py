from __future__ import annotations

from typing import List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_complete_page import CheckoutCompletePage


class CheckoutStepTwoPage(BasePage):
    url_path = "/checkout-step-two.html"

    PAGE_TITLE = (By.CLASS_NAME, "title")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICES = (By.CLASS_NAME, "inventory_item_price")
    SUBTOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")

    def is_loaded(self) -> bool:
        return self.is_visible(self.PAGE_TITLE) and self.text_of(self.PAGE_TITLE) == "Checkout: Overview"

    def item_names(self) -> List[str]:
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    @staticmethod
    def _parse_currency(text: str) -> float:
        return float(text.split("$")[-1])

    def subtotal(self) -> float:
        return self._parse_currency(self.text_of(self.SUBTOTAL_LABEL))

    def tax(self) -> float:
        return self._parse_currency(self.text_of(self.TAX_LABEL))

    def total(self) -> float:
        return self._parse_currency(self.text_of(self.TOTAL_LABEL))

    def finish(self) -> CheckoutCompletePage:
        self.click(self.FINISH_BUTTON)
        return CheckoutCompletePage(self.driver)

    def cancel(self):
        from pages.inventory_page import InventoryPage

        self.click(self.CANCEL_BUTTON)
        return InventoryPage(self.driver)
