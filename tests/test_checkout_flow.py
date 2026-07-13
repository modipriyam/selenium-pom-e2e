from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "checkout_scenarios.json"
SCENARIOS = json.loads(DATA_FILE.read_text(encoding="utf-8"))


@pytest.mark.checkout
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_full_checkout_flow(driver, scenario):
    products = scenario["products"]
    customer = scenario["customer"]

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
    step_two = step_one.fill_customer_information(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    ).submit()

    assert step_two.is_loaded()
    assert set(step_two.item_names()) == set(products)
    assert math.isclose(step_two.subtotal(), cart_total, abs_tol=0.01)
    expected_total = round(step_two.subtotal() + step_two.tax(), 2)
    assert math.isclose(step_two.total(), expected_total, abs_tol=0.01)

    complete = step_two.finish()
    assert complete.is_loaded()
    assert complete.order_is_confirmed()


@pytest.mark.checkout
def test_checkout_requires_customer_information(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    inventory.add_to_cart("Sauce Labs Backpack")
    step_one = inventory.open_cart().proceed_to_checkout()

    step_one.submit_expecting_error()
    assert step_one.has_error()
    assert "First Name is required" in step_one.error_message()


@pytest.mark.checkout
def test_cart_updates_when_item_removed(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)

    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.add_to_cart("Sauce Labs Bike Light")
    assert inventory.cart_count() == 2

    inventory.remove_from_cart("Sauce Labs Backpack")
    assert inventory.cart_count() == 1

    cart = inventory.open_cart()
    assert cart.item_names() == ["Sauce Labs Bike Light"]
