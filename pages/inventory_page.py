from __future__ import annotations

from typing import List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.product_detail_page import ProductDetailPage


class InventoryPage(BasePage):
    url_path = "/inventory.html"

    APP_TITLE = (By.CLASS_NAME, "title")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    INVENTORY_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    INVENTORY_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    BURGER_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    RESET_APP_LINK = (By.ID, "reset_sidebar_link")

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
        return [el.text for el in self.driver.find_elements(*self.INVENTORY_ITEM_NAME)]

    def product_prices(self) -> List[float]:
        return [
            float(el.text.replace("$", ""))
            for el in self.driver.find_elements(*self.INVENTORY_ITEM_PRICE)
        ]

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

    def open_product_details(self, product_name: str) -> ProductDetailPage:
        for el in self.driver.find_elements(*self.INVENTORY_ITEM_NAME):
            if el.text == product_name:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                    el,
                )
                return ProductDetailPage(self.driver)
        raise ValueError(f"Product not found on inventory page: {product_name!r}")

    def sort_by(self, visible_text: str) -> "InventoryPage":
        self.select_by_visible_text(self.SORT_DROPDOWN, visible_text)
        return self

    def _open_menu(self) -> None:
        self.click(self.BURGER_BUTTON)
        self.wait.until(lambda d: d.find_element(*self.LOGOUT_LINK).is_displayed())

    def logout(self):
        from pages.login_page import LoginPage

        self._open_menu()
        self.click(self.LOGOUT_LINK)
        return LoginPage(self.driver)

    def reset_app_state(self) -> "InventoryPage":
        self._open_menu()
        self.click(self.RESET_APP_LINK)
        return self
