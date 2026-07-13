"""Additional feature coverage: sorting, product detail page, burger menu,
checkout cancellation, and continue-shopping.

These tests use the existing POM surface; only ProductDetailPage was added.
Burger-menu actions live directly on InventoryPage rather than a separate
component class — deliberate, to avoid an abstraction that would not pay off.
"""
from __future__ import annotations

import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG


# ---------------------------------------------------------------------------
# Product sorting
# ---------------------------------------------------------------------------

SORT_CASES = [
    ("Name (A to Z)", "names", False),
    ("Name (Z to A)", "names", True),
    ("Price (low to high)", "prices", False),
    ("Price (high to low)", "prices", True),
]


@pytest.mark.regression
@pytest.mark.parametrize(
    "option, attribute, reverse",
    SORT_CASES,
    ids=[c[0] for c in SORT_CASES],
)
def test_products_sort_correctly(driver, option, attribute, reverse):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    assert inventory.is_loaded()

    inventory.sort_by(option)

    getter = inventory.product_names if attribute == "names" else inventory.product_prices
    displayed = getter()
    assert displayed == sorted(displayed, reverse=reverse), (
        f"{option} did not produce sorted order.\n  got: {displayed}"
    )


# ---------------------------------------------------------------------------
# Product detail page
# ---------------------------------------------------------------------------

@pytest.mark.regression
def test_product_detail_page_shows_correct_info_and_adds_to_cart(driver):
    """Open the PDP for Backpack, sanity-check its fields, add to cart from
    the PDP, and confirm the cart badge and button state both update."""
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    pdp = inventory.open_product_details("Sauce Labs Backpack")

    assert pdp.is_loaded()
    assert pdp.name() == "Sauce Labs Backpack"
    assert pdp.price() == 29.99
    assert len(pdp.description()) > 0
    assert "laptop" in pdp.description().lower()
    assert pdp.cart_count() == 0

    pdp.add_to_cart()
    assert pdp.is_in_cart(), "PDP add-to-cart button did not toggle to Remove"
    assert pdp.cart_count() == 1

    inventory_again = pdp.back_to_products()
    assert inventory_again.is_loaded()
    assert inventory_again.cart_count() == 1


# ---------------------------------------------------------------------------
# Burger menu: logout + reset app state
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_burger_menu_logout_returns_to_login(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    assert "/inventory.html" in driver.current_url

    login = inventory.logout()
    assert login.is_visible(login.LOGIN_BUTTON), "Login form not visible after logout"
    assert driver.current_url.rstrip("/").endswith("saucedemo.com")


@pytest.mark.regression
def test_reset_app_state_clears_cart(driver):
    """SauceDemo's badge stays visible until a page reload after reset, so we
    reload before asserting — reflecting the actual observable behavior."""
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.add_to_cart("Sauce Labs Bike Light")
    assert inventory.cart_count() == 2

    inventory.reset_app_state()
    driver.refresh()

    assert inventory.cart_count() == 0
    assert not inventory.is_visible(inventory._remove_button("Sauce Labs Backpack"), timeout=2)


# ---------------------------------------------------------------------------
# Cancel checkout at each step
# ---------------------------------------------------------------------------

@pytest.mark.checkout
def test_cancel_at_checkout_step_one_returns_to_cart(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    inventory.add_to_cart("Sauce Labs Backpack")
    cart = inventory.open_cart()
    step_one = cart.proceed_to_checkout()

    cart_again = step_one.cancel()
    assert cart_again.is_loaded()
    assert cart_again.item_names() == ["Sauce Labs Backpack"], "Cart contents lost after cancel"


@pytest.mark.checkout
def test_cancel_at_checkout_step_two_returns_to_inventory(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    inventory.add_to_cart("Sauce Labs Backpack")
    step_two = (
        inventory.open_cart()
        .proceed_to_checkout()
        .fill_customer_information("Ada", "Lovelace", "10001")
        .submit()
    )
    assert step_two.is_loaded()

    inventory_again = step_two.cancel()
    assert inventory_again.is_loaded()
    assert inventory_again.cart_count() == 1, "Cart should survive step-two cancel"


# ---------------------------------------------------------------------------
# Continue shopping
# ---------------------------------------------------------------------------

@pytest.mark.regression
def test_continue_shopping_returns_to_inventory_with_cart_intact(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.add_to_cart("Sauce Labs Bike Light")

    cart = inventory.open_cart()
    assert cart.item_count() == 2

    inventory_again = cart.continue_shopping()
    assert inventory_again.is_loaded()
    assert inventory_again.cart_count() == 2
