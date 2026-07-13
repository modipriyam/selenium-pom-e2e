from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    NAME = (By.CLASS_NAME, "inventory_details_name")
    DESCRIPTION = (By.CLASS_NAME, "inventory_details_desc")
    PRICE = (By.CLASS_NAME, "inventory_details_price")
    ADD_BUTTON = (By.CSS_SELECTOR, "button[id^='add-to-cart']")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "button[id^='remove']")
    BACK_BUTTON = (By.ID, "back-to-products")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    def is_loaded(self) -> bool:
        return self.is_visible(self.NAME)

    def name(self) -> str:
        return self.text_of(self.NAME)

    def description(self) -> str:
        return self.text_of(self.DESCRIPTION)

    def price(self) -> float:
        return float(self.text_of(self.PRICE).replace("$", ""))

    def add_to_cart(self) -> "ProductDetailPage":
        self.click(self.ADD_BUTTON)
        return self

    def is_in_cart(self) -> bool:
        return self.is_visible(self.REMOVE_BUTTON, timeout=2)

    def cart_count(self) -> int:
        if not self.is_visible(self.CART_BADGE, timeout=1):
            return 0
        return int(self.text_of(self.CART_BADGE))

    def back_to_products(self):
        from pages.inventory_page import InventoryPage

        self.click(self.BACK_BUTTON)
        return InventoryPage(self.driver)
