from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.cart_page import CartPage


class InventoryPage(BasePage):
    url_path = "/inventory.html"

    APP_TITLE = (By.CLASS_NAME, "title")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    def is_loaded(self):
        return self.is_visible(self.APP_TITLE) and self.text_of(self.APP_TITLE) == "Products"

    def add_to_cart(self, product_name):
        slug = product_name.lower().replace(" ", "-")
        self.click((By.ID, f"add-to-cart-{slug}"))

    def remove_from_cart(self, product_name):
        slug = product_name.lower().replace(" ", "-")
        self.click((By.ID, f"remove-{slug}"))

    def cart_count(self):
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        self.click(self.CART_LINK)
        return CartPage(self.driver)
