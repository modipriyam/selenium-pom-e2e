import math

import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG


@pytest.mark.e2e
def test_full_purchase_journey(driver):
    # login
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    assert inventory.is_loaded()
    assert inventory.cart_count() == 0

    # add three items, then drop one
    for name in ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt"]:
        inventory.add_to_cart(name)
    assert inventory.cart_count() == 3

    inventory.remove_from_cart("Sauce Labs Bolt T-Shirt")
    assert inventory.cart_count() == 2

    # view cart
    cart = inventory.open_cart()
    assert cart.is_loaded()
    assert cart.item_count() == 2
    assert set(cart.item_names()) == {"Sauce Labs Backpack", "Sauce Labs Bike Light"}
    expected_subtotal = round(sum(cart.item_prices()), 2)

    # try checkout with an empty form
    step_one = cart.proceed_to_checkout()
    step_one.submit()
    assert step_one.has_error()

    # fill it in and continue
    step_two = step_one.fill_customer_information("John", "Smith", "94016").submit()
    assert step_two.is_loaded()
    assert set(step_two.item_names()) == {"Sauce Labs Backpack", "Sauce Labs Bike Light"}

    # totals add up
    assert math.isclose(step_two.subtotal(), expected_subtotal, abs_tol=0.01)
    assert math.isclose(step_two.total(), step_two.subtotal() + step_two.tax(), abs_tol=0.01)

    # place the order
    complete = step_two.finish()
    assert complete.is_loaded()
    assert complete.order_is_confirmed()
