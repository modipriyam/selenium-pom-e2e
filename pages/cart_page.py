from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_step_one_page import CheckoutStepOnePage


class CartPage(BasePage):
    url_path = "/cart.html"

    PAGE_TITLE = (By.CLASS_NAME, "title")
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICES = (By.CLASS_NAME, "inventory_item_price")
    CHECKOUT_BUTTON = (By.ID, "checkout")

    def is_loaded(self):
        return self.is_visible(self.PAGE_TITLE) and self.text_of(self.PAGE_TITLE) == "Your Cart"

    def item_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def item_prices(self):
        return [float(el.text.replace("$", "")) for el in self.driver.find_elements(*self.ITEM_PRICES)]

    def item_count(self):
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BUTTON)
        return CheckoutStepOnePage(self.driver)
