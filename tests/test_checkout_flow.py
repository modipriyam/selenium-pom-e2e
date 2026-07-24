import math

import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG

SCENARIOS = [
    ("one_item", ["Sauce Labs Backpack"], ("John", "Smith", "94016")),
    (
        "three_items",
        ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt"],
        ("Jane", "Doe", "10001"),
    ),
    (
        "mixed_prices",
        ["Sauce Labs Fleece Jacket", "Sauce Labs Onesie", "Test.allTheThings() T-Shirt (Red)"],
        ("Test", "User", "12345"),
    ),
]


@pytest.mark.parametrize(
    "products, customer",
    [(p, c) for _, p, c in SCENARIOS],
    ids=[s[0] for s in SCENARIOS],
)
def test_checkout(driver, products, customer):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    assert inventory.is_loaded()
    assert inventory.cart_count() == 0

    for product in products:
        inventory.add_to_cart(product)
    assert inventory.cart_count() == len(products)

    cart = inventory.open_cart()
    assert cart.is_loaded()
    assert cart.item_count() == len(products)
    assert set(cart.item_names()) == set(products)
    cart_total = round(sum(cart.item_prices()), 2)

    step_one = cart.proceed_to_checkout()
    step_two = step_one.fill_customer_information(*customer).submit()

    assert step_two.is_loaded()
    assert set(step_two.item_names()) == set(products)
    assert math.isclose(step_two.subtotal(), cart_total, abs_tol=0.01)
    expected_total = round(step_two.subtotal() + step_two.tax(), 2)
    assert math.isclose(step_two.total(), expected_total, abs_tol=0.01)

    complete = step_two.finish()
    assert complete.is_loaded()
    assert complete.order_is_confirmed()


def test_checkout_requires_customer_info(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    inventory.add_to_cart("Sauce Labs Backpack")
    step_one = inventory.open_cart().proceed_to_checkout()

    step_one.submit()  # nothing filled in
    assert step_one.has_error()
    assert "First Name is required" in step_one.error_message()


def test_remove_from_cart(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)

    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.add_to_cart("Sauce Labs Bike Light")
    assert inventory.cart_count() == 2

    inventory.remove_from_cart("Sauce Labs Backpack")
    assert inventory.cart_count() == 1

    cart = inventory.open_cart()
    assert cart.item_names() == ["Sauce Labs Bike Light"]
