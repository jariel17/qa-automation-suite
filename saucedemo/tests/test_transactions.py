import pytest
from playwright.sync_api import expect

from data.users import USERS
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage


@pytest.mark.parametrize(
    "username,product_name",
    [
        pytest.param(USERS["standard"], "Sauce Labs Backpack", id="TC-08-standard-user"),
        pytest.param(USERS["error"], "Sauce Labs Bolt T-Shirt", id="TC-08-error-user"),
    ],
)
def test_add_to_cart(login_as, username, product_name):
    """TC-08: adding a product updates its button, the cart badge, and the cart page."""
    login_page = login_as(username)
    inventory_page = InventoryPage(login_page.page)

    inventory_page.add_to_cart(product_name)

    expect(inventory_page.get_item_button(product_name)).to_have_text("Remove")
    expect(inventory_page.header.cart_badge).to_have_text("1")

    inventory_page.header.go_to_cart()
    cart_page = CartPage(login_page.page)
    expect(cart_page.cart_items).to_have_count(1)
    assert product_name in cart_page.get_cart_item_names()

PRODUCTS_TO_ADD = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Onesie",
    "Test.allTheThings() T-Shirt (Red)",
]

@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="TC-09-standard-user"),
        pytest.param(USERS["error"], id="TC-09-error-user"),
    ],
)
def test_add_multiple_items_to_cart(login_as, username):
    """TC-09: adding all 6 products updates the badge, the cart page, and every item's button."""
    login_page = login_as(username)
    inventory_page = InventoryPage(login_page.page)

    expected_prices = {
        name: price
        for name, price in zip(inventory_page.get_product_names(), inventory_page.get_product_prices())
        if name in PRODUCTS_TO_ADD
    }
    
    for product_name in PRODUCTS_TO_ADD:
        inventory_page.add_to_cart(product_name)
        expect(inventory_page.get_item_button(product_name)).to_have_text("Remove")

    expect(inventory_page.header.cart_badge).to_have_text("6")

    inventory_page.header.go_to_cart()
    cart_page = CartPage(login_page.page)
    expect(cart_page.cart_items).to_have_count(6)

    cart_names = cart_page.get_cart_item_names()
    assert set(cart_names) == set(PRODUCTS_TO_ADD)

    cart_price_map = dict(zip(cart_names, cart_page.get_cart_item_prices()))
    for product_name in PRODUCTS_TO_ADD:
        assert cart_price_map[product_name] == expected_prices[product_name]


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="TC-10-standard-user"),
        pytest.param(USERS["error"], id="TC-10-error-user"),
    ],)
def test_remove_item_from_cart(login_as, username):
    """TC-10: removing one item from the cart updates the badge, cart page, and inventory buttons."""
    login_page = login_as(username)
    inventory_page = InventoryPage(login_page.page)

    inventory_page.add_to_cart("Sauce Labs Backpack")
    inventory_page.add_to_cart("Sauce Labs Bike Light")

    inventory_page.header.go_to_cart()
    cart_page = CartPage(login_page.page)
    cart_page.remove_from_cart("Sauce Labs Backpack")

    expect(cart_page.header.cart_badge).to_have_text("1")
    expect(cart_page.cart_items).to_have_count(1)
    cart_names = cart_page.get_cart_item_names()
    expect(cart_page.header.cart_badge).to_have_text("1")
    expect(cart_page.cart_items).to_have_count(1)
    cart_names = cart_page.get_cart_item_names()
    assert "Sauce Labs Backpack" not in cart_names
    assert "Sauce Labs Bike Light" in cart_names

    cart_page.continue_shopping()

    expect(inventory_page.get_item_button("Sauce Labs Backpack")).to_have_text("Add to cart")
    expect(inventory_page.get_item_button("Sauce Labs Bike Light")).to_have_text("Remove")

BACKPACK_PRICE = 29.99
TAX_RATE = 0.08

FIRST_NAME = "Ariel"
LAST_NAME = "Acosta"
POSTAL_CODE = "12345"

@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="TC-11-standard-user"),
        pytest.param(
            USERS["error"], id="TC-11-error-user-last-name-not-retained"
        ),
    ],
)
def test_full_checkout_happy_path(login_as, username):
    """TC-11: standard_user checks out one item, inventory to complete, no errors at any step.
    error_user hits a documented defect: Last Name silently drops its typed value, and the
    validation gate that should catch the resulting empty field doesn't."""
    login_page = login_as(username)
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.add_to_cart("Sauce Labs Backpack")
    inventory_page.header.go_to_cart()

    cart_page = CartPage(page)
    expect(cart_page.cart_items).to_have_count(1)
    cart_page.checkout()

    checkout_step_one = CheckoutStepOnePage(page)
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")
    checkout_step_one.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
    first_name_after_fill = checkout_step_one.first_name_field.input_value()
    last_name_after_fill = checkout_step_one.last_name_field.input_value()
    postal_code_after_fill = checkout_step_one.postal_code_field.input_value()

    checkout_step_one.continue_to_overview()

    checkout_step_two = CheckoutStepTwoPage(page)
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")

    assert first_name_after_fill == FIRST_NAME
    assert last_name_after_fill == LAST_NAME
    assert postal_code_after_fill == POSTAL_CODE
    assert "Sauce Labs Backpack" in checkout_step_two.get_line_item_names()

    expected_tax = round(BACKPACK_PRICE * TAX_RATE, 2)
    expected_total = round(BACKPACK_PRICE + expected_tax, 2)

    assert checkout_step_two.get_subtotal() == BACKPACK_PRICE
    assert checkout_step_two.get_tax() == expected_tax
    assert checkout_step_two.get_total() == expected_total

    checkout_step_two.finish()

    checkout_complete = CheckoutCompletePage(page)
    expect(page).to_have_url("https://www.saucedemo.com/checkout-complete.html")
    expect(checkout_complete.complete_header).to_have_text("Thank you for your order!")
    expect(checkout_complete.complete_text).to_have_text(
        "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    )

@pytest.mark.parametrize(
    "username,first_name,last_name,postal_code,expected_error",
    [
        pytest.param(
            USERS["standard"], "", LAST_NAME, POSTAL_CODE,
            "Error: First Name is required",
            id="TC-12-standard-missing-first-name",
        ),
        pytest.param(
            USERS["standard"], FIRST_NAME, "", POSTAL_CODE,
            "Error: Last Name is required",
            id="TC-12-standard-missing-last-name",
        ),
        pytest.param(
            USERS["standard"], FIRST_NAME, LAST_NAME, "",
            "Error: Postal Code is required",
            id="TC-12-standard-missing-postal-code",
        ),
        pytest.param(
            USERS["error"], "", LAST_NAME, POSTAL_CODE,
            "Error: First Name is required",
            id="TC-12-error-user-missing-first-name",
        ),
        pytest.param(
            USERS["error"], FIRST_NAME, "", POSTAL_CODE,
            "Error: Last Name is required",
            id="TC-12-error-user-missing-last-name"
        ),
        pytest.param(
            USERS["error"], FIRST_NAME, LAST_NAME, "",
            "Error: Postal Code is required",
            id="TC-12-error-user-missing-postal-code",
        ),
    ],
)
def test_checkout_field_validation(login_as, username, first_name, last_name, postal_code, expected_error):
    """TC-12: checkout step one blocks continue and shows the right error when a required field is blank."""
    
    login_page = login_as(username)
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.add_to_cart("Sauce Labs Backpack")
    inventory_page.header.go_to_cart()

    cart_page = CartPage(page)
    cart_page.checkout()

    checkout_step_one = CheckoutStepOnePage(page)
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")

    checkout_step_one.fill_info(first_name, last_name, postal_code)
    checkout_step_one.continue_to_overview()

    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")
    expect(checkout_step_one.error_message).to_have_text(expected_error)


def test_cart_subtotal_equals_sum_of_line_items(login_as):
    """TC-15: checkout step two subtotal equals the sum of individual item prices read from the cart page."""
    login_page = login_as(USERS["standard"])
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.add_to_cart("Sauce Labs Backpack")
    inventory_page.add_to_cart("Sauce Labs Bike Light")
    inventory_page.header.go_to_cart()

    cart_page = CartPage(page)
    cart_prices = cart_page.get_cart_item_prices()
    cart_page.checkout()

    checkout_step_one = CheckoutStepOnePage(page)
    checkout_step_one.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
    checkout_step_one.continue_to_overview()

    checkout_step_two = CheckoutStepTwoPage(page)
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")

    assert checkout_step_two.get_subtotal() == round(sum(cart_prices), 2)


def test_checkout_step_two_subtotal_plus_tax_equals_total(login_as):
    """TC-16: checkout step two's displayed subtotal + tax equals the displayed total."""
    login_page = login_as(USERS["standard"])
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.add_to_cart("Sauce Labs Backpack")
    inventory_page.add_to_cart("Sauce Labs Bike Light")
    inventory_page.header.go_to_cart()

    cart_page = CartPage(page)
    cart_page.checkout()

    checkout_step_one = CheckoutStepOnePage(page)
    checkout_step_one.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
    checkout_step_one.continue_to_overview()

    checkout_step_two = CheckoutStepTwoPage(page)
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")

    subtotal = checkout_step_two.get_subtotal()
    tax = checkout_step_two.get_tax()
    total = checkout_step_two.get_total()

    assert round(subtotal + tax, 2) == total