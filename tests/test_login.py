import pytest

from pages.login_page import LoginPage
from utils.config import CONFIG


def test_valid_login(driver):
    inventory = LoginPage(driver).open().login(CONFIG.standard_user, CONFIG.password)
    assert inventory.is_loaded()
    assert "/inventory.html" in driver.current_url


def test_locked_out_user(driver):
    login = LoginPage(driver).open()
    login.login(CONFIG.locked_user, CONFIG.password)
    assert login.has_error()
    assert "locked out" in login.error_message().lower()


@pytest.mark.parametrize(
    "username, password, expected_fragment",
    [
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("standard_user", "wrong_password", "do not match"),
    ],
    ids=["missing-username", "missing-password", "bad-credentials"],
)
def test_bad_login(driver, username, password, expected_fragment):
    login = LoginPage(driver).open()
    login.login(username, password)
    assert login.has_error()
    assert expected_fragment.lower() in login.error_message().lower()
