import pytest
from playwright.sync_api import expect

from data.users import USERS
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


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