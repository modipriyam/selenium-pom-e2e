from __future__ import annotations

import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG


@pytest.mark.smoke
@pytest.mark.login
def test_valid_login_lands_on_inventory(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    assert inventory.is_loaded()
    assert "/inventory.html" in driver.current_url


@pytest.mark.login
def test_locked_out_user_sees_error(driver):
    login = (
        LoginPage(driver)
        .open()
        .login_expecting_failure(CONFIG.locked_user, CONFIG.password)
    )
    assert login.has_error()
    assert "locked out" in login.error_message().lower()


@pytest.mark.login
@pytest.mark.parametrize(
    "username, password, expected_fragment",
    [
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("standard_user", "wrong_password", "do not match"),
    ],
    ids=["missing-username", "missing-password", "bad-credentials"],
)
def test_login_negative_cases(driver, username, password, expected_fragment):
    login = LoginPage(driver).open().login_expecting_failure(username, password)
    assert login.has_error()
    assert expected_fragment.lower() in login.error_message().lower()
