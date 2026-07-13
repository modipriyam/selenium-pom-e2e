"""One long end-to-end journey suitable for a live demo.

Run headed with a pacing delay so a viewer can follow along:

    E2E_STEP_DELAY=1.2 pytest tests/test_demo_e2e.py -v -s

This same test also runs in CI (headless, no delay) as part of the regular
suite - the delay is opt-in via the `E2E_STEP_DELAY` env var and defaults
to 0. Assertions never rely on the sleep; it only paces the visible playback.
"""
from __future__ import annotations

import logging
import math

import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG

log = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.regression
def test_demo_full_shopping_journey(driver):
    """Log in -> sort -> browse a product -> build cart -> checkout -> log out."""

    # 1. Log in as the happy-path user.
    log.info("STEP 1 - Login")
    login = LoginPage(driver).open()
    login.pause()
    inventory = login.login(CONFIG.standard_user, CONFIG.password)
    assert inventory.is_loaded()
    assert inventory.cart_count() == 0
    inventory.pause()

    # 2. Sort by price (high -> low) and confirm the ordering.
    log.info("STEP 2 - Sort products by price, high to low")
    inventory.sort_by("Price (high to low)")
    prices = inventory.product_prices()
    assert prices == sorted(prices, reverse=True), f"Sort order incorrect: {prices}"
    inventory.pause()

    # 3. Open the most expensive product's detail page.
    top_product_name = inventory.product_names()[0]
    log.info("STEP 3 - Open detail page for top-priced item: %s", top_product_name)
    pdp = inventory.open_product_details(top_product_name)
    assert pdp.is_loaded()
    assert pdp.name() == top_product_name
    assert len(pdp.description()) > 0
    pdp.pause()

    # 4. Add the item to cart from the PDP.
    log.info("STEP 4 - Add %s to cart from the PDP", top_product_name)
    pdp.add_to_cart()
    assert pdp.is_in_cart()
    assert pdp.cart_count() == 1
    pdp.pause()

    # 5. Go back to inventory and add two more items.
    log.info("STEP 5 - Back to inventory, add two more items")
    inventory = pdp.back_to_products()
    inventory.sort_by("Name (A to Z)")
    inventory.pause()
    inventory.add_to_cart("Sauce Labs Bike Light")
    inventory.pause(0.4)
    inventory.add_to_cart("Sauce Labs Bolt T-Shirt")
    assert inventory.cart_count() == 3
    inventory.pause()

    # 6. Open the cart, then use Continue Shopping to prove the cart survives.
    log.info("STEP 6 - Open cart, then use Continue Shopping to return")
    cart = inventory.open_cart()
    assert cart.is_loaded()
    assert cart.item_count() == 3
    assert set(cart.item_names()) == {
        top_product_name,
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
    }
    cart.pause()

    inventory = cart.continue_shopping()
    assert inventory.is_loaded()
    assert inventory.cart_count() == 3
    inventory.pause()

    # 7. Add a fourth item, then walk into checkout.
    log.info("STEP 7 - Add a fourth item and proceed to checkout")
    inventory.add_to_cart("Sauce Labs Onesie")
    assert inventory.cart_count() == 4
    inventory.pause()

    cart = inventory.open_cart()
    assert cart.item_count() == 4
    cart_total = round(sum(cart.item_prices()), 2)
    step_one = cart.proceed_to_checkout()
    step_one.pause()

    # 8. Demonstrate form validation by submitting empty first.
    log.info("STEP 8 - Attempt empty submission, expect validation error")
    step_one.submit_expecting_error()
    assert step_one.has_error()
    assert "First Name is required" in step_one.error_message()
    step_one.pause()

    # 9. Fill out the customer form and continue to overview.
    log.info("STEP 9 - Fill customer details and continue")
    step_two = step_one.fill_customer_information("Demo", "Tester", "94107").submit()
    assert step_two.is_loaded()
    cart_item_names = set(cart.item_names())
    assert set(step_two.item_names()) == cart_item_names
    assert math.isclose(step_two.subtotal(), cart_total, abs_tol=0.01)
    expected_total = round(step_two.subtotal() + step_two.tax(), 2)
    assert math.isclose(step_two.total(), expected_total, abs_tol=0.01)
    log.info(
        "     subtotal=%.2f  tax=%.2f  total=%.2f",
        step_two.subtotal(),
        step_two.tax(),
        step_two.total(),
    )
    step_two.pause()

    # 10. Finish the order and verify the confirmation.
    log.info("STEP 10 - Finish order and verify confirmation")
    complete = step_two.finish()
    assert complete.is_loaded()
    assert complete.order_is_confirmed(), (
        f"Unexpected confirmation header: {complete.confirmation_header()!r}"
    )
    log.info("     Confirmation header: %r", complete.confirmation_header())
    complete.pause()

    # 11. Log out via the burger menu to end where we started.
    log.info("STEP 11 - Log out via burger menu")
    inventory_final = complete.back_to_products()
    assert inventory_final.is_loaded()
    inventory_final.pause()
    login_again = inventory_final.logout()
    assert login_again.is_visible(login_again.LOGIN_BUTTON)
    assert driver.current_url.rstrip("/").endswith("saucedemo.com")
    log.info("STEP 11 - Journey complete")
