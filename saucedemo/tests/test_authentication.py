import pytest
from playwright.sync_api import expect

from data.users import PASSWORD, USERS
from pages.inventory_page import InventoryPage


def test_successful_login_standard_user(login_as, error_monitor):
    """TC-01: standard_user logs in and lands on a fully populated inventory page, with no
    console errors, uncaught JS exceptions, or failed/4xx-5xx network requests (excluding the
    known events.backtrace.io, see conftest.error_monitor)."""
    
    login_page = login_as(USERS["standard"])
    page = login_page.page
    inventory_page = InventoryPage(page)

    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(inventory_page.header.title_bar).to_have_text("Products")
    expect(inventory_page.items).to_have_count(6)

    inventory_page.wait_for_images_to_load()
    for image in inventory_page.item_images.all():
        expect(image).to_be_visible()

    expect(login_page.error_message).not_to_be_visible()

    assert not error_monitor, "\n".join(error_monitor)


@pytest.mark.parametrize(
    "username,password,expected_error",
    [
        pytest.param(
            USERS["locked_out"],
            PASSWORD,
            "Epic sadface: Sorry, this user has been locked out.",
            id="TC-02-locked-out",
        ),
        pytest.param(
            "",
            PASSWORD,
            "Epic sadface: Username is required",
            id="TC-03-no-username",
        ),
        pytest.param(
            "wrong_user",
            PASSWORD,
            "Epic sadface: Username and password do not match any user in this service",
            id="TC-04-incorrect-username",
        ),
        pytest.param(
            USERS["standard"],
            "",
            "Epic sadface: Password is required",
            id="TC-05-no-password",
        ),
        pytest.param(
            USERS["standard"],
            "wrong_password",
            "Epic sadface: Username and password do not match any user in this service",
            id="TC-06-incorrect-password",
        ),
    ],
)
def test_negative_login(login_as, username, password, expected_error):
    """TC-02 through TC-06: rejected logins stay on the login page with the right error."""
    login_page = login_as(username, password)

    expect(login_page.error_message).to_have_text(expected_error)
    expect(login_page.page).to_have_url("https://www.saucedemo.com/")
