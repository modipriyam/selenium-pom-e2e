from __future__ import annotations

from typing import List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.cart_page import CartPage


class InventoryPage(BasePage):
    url_path = "/inventory.html"

    APP_TITLE = (By.CLASS_NAME, "title")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    @staticmethod
    def _slug(product_name: str) -> str:
        return product_name.lower().replace(" ", "-")

    def _add_button(self, product_name: str) -> tuple[str, str]:
        return (By.ID, f"add-to-cart-{self._slug(product_name)}")

    def _remove_button(self, product_name: str) -> tuple[str, str]:
        return (By.ID, f"remove-{self._slug(product_name)}")

    def is_loaded(self) -> bool:
        return self.is_visible(self.APP_TITLE) and self.text_of(self.APP_TITLE) == "Products"

    def product_names(self) -> List[str]:
        elements = self.driver.find_elements(By.CLASS_NAME, "inventory_item_name")
        return [el.text for el in elements]

    def add_to_cart(self, product_name: str) -> "InventoryPage":
        self.click(self._add_button(product_name))
        return self

    def remove_from_cart(self, product_name: str) -> "InventoryPage":
        self.click(self._remove_button(product_name))
        return self

    def cart_count(self) -> int:
        if not self.is_visible(self.CART_BADGE, timeout=1):
            return 0
        return int(self.text_of(self.CART_BADGE))

    def open_cart(self) -> CartPage:
        self.click(self.CART_LINK)
        return CartPage(self.driver)

    def sort_by(self, visible_text: str) -> "InventoryPage":
        self.select_by_visible_text(self.SORT_DROPDOWN, visible_text)
        return self
