from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_complete_page import CheckoutCompletePage


class CheckoutStepTwoPage(BasePage):
    url_path = "/checkout-step-two.html"

    PAGE_TITLE = (By.CLASS_NAME, "title")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    SUBTOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")

    def is_loaded(self):
        return self.is_visible(self.PAGE_TITLE) and self.text_of(self.PAGE_TITLE) == "Checkout: Overview"

    def item_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def subtotal(self):
        return float(self.text_of(self.SUBTOTAL_LABEL).split("$")[-1])

    def tax(self):
        return float(self.text_of(self.TAX_LABEL).split("$")[-1])

    def total(self):
        return float(self.text_of(self.TOTAL_LABEL).split("$")[-1])

    def finish(self):
        self.click(self.FINISH_BUTTON)
        return CheckoutCompletePage(self.driver)
