import pytest
from playwright.sync_api import expect

from data.users import USERS
from pages.inventory_page import InventoryPage
from pages.inventory_item_page import InventoryItemPage

EXPECTED_IMAGE_SLUGS = {
    "Sauce Labs Backpack": "sauce-backpack",
    "Sauce Labs Bike Light": "bike-light",
    "Sauce Labs Bolt T-Shirt": "bolt-shirt",
    "Sauce Labs Fleece Jacket": "sauce-pullover",
    "Sauce Labs Onesie": "red-onesie",
    "Test.allTheThings() T-Shirt (Red)": "red-tatt",
}


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="TC-07-standard-user"),
        pytest.param(USERS["problem"], id="TC-07-problem-user"),
        pytest.param(USERS["visual"], id="TC-07-visual-user"),
    ],
)
def test_product_image_integrity(login_as, username):
    """TC-07: each of the 6 inventory images loads, isn't the broken placeholder, and maps to its own product."""
    login_page = login_as(username)
    inventory_page = InventoryPage(login_page.page)

    expect(inventory_page.items).to_have_count(6)
    inventory_page.wait_for_images_to_load()

    image_map = inventory_page.get_product_image_map()
    mismatches = [
        f"{product_name}: expected slug {EXPECTED_IMAGE_SLUGS[product_name]!r} not found in src {src!r}"
        for product_name, src in image_map.items()
        if EXPECTED_IMAGE_SLUGS[product_name] not in src
    ]
    assert not mismatches, "\n".join(mismatches)


def test_cart_persistence_across_navigation(login_as):
    """TC-13: cart badge and item button state persist after visiting a product detail page and returning."""
    login_page = login_as(USERS["standard"])
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.add_to_cart("Sauce Labs Backpack")
    expect(inventory_page.header.cart_badge).to_have_text("1")

    inventory_page.open_product("Sauce Labs Backpack")
    detail_page = InventoryItemPage(page)
    expect(detail_page.header.cart_badge).to_have_text("1")

    detail_page.back_to_products()
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

    expect(inventory_page.header.cart_badge).to_have_text("1")
    expect(inventory_page.get_item_button("Sauce Labs Backpack")).to_have_text("Remove")


KNOWN_CORRECT_CATALOG = {
    "Sauce Labs Backpack": (
        "carry.allTheThings() with the sleek, streamlined Sly Pack that melds "
        "uncompromising style with unequaled laptop and tablet protection.",
        "$29.99",
    ),
    "Sauce Labs Bike Light": (
        "A red light isn't the desired state in testing but it sure helps when riding "
        "your bike at night. Water-resistant with 3 lighting modes, 1 AAA battery included.",
        "$9.99",
    ),
    "Sauce Labs Bolt T-Shirt": (
        "Get your testing superhero on with the Sauce Labs bolt T-shirt. From American "
        "Apparel, 100% ringspun combed cotton, heather gray with red bolt.",
        "$15.99",
    ),
    "Sauce Labs Fleece Jacket": (
        "It's not every day that you come across a midweight quarter-zip fleece jacket "
        "capable of handling everything from a relaxing day outdoors to a busy day at "
        "the office.",
        "$49.99",
    ),
    "Sauce Labs Onesie": (
        "Rib snap infant onesie for the junior automation engineer in development. "
        "Reinforced 3-snap bottom closure, two-needle hemmed sleeved and bottom "
        "won't unravel.",
        "$7.99",
    ),
    "Test.allTheThings() T-Shirt (Red)": (
        "This classic Sauce Labs t-shirt is perfect to wear when cozying up to your "
        "keyboard to automate a few tests. Super-soft and comfy ringspun combed cotton.",
        "$15.99",
    ),
}


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="TC-17-standard-user"),
        pytest.param(USERS["problem"], id="TC-17-problem-user"),
        pytest.param(USERS["visual"], id="TC-17-visual-user"),
    ],
)
def test_product_info_integrity(login_as, username):
    """TC-17: each product's name, description, and price match the known-correct catalog."""
    login_page = login_as(username)
    inventory_page = InventoryPage(login_page.page)

    info_map = inventory_page.get_product_info_map()

    mismatches = [
        f"{name}: expected {KNOWN_CORRECT_CATALOG[name]!r}, got {info!r}"
        for name, info in info_map.items()
        if info != KNOWN_CORRECT_CATALOG[name]
    ]
    assert not mismatches, "\n".join(mismatches)


EXPECTED_AZ_ORDER = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Onesie",
    "Test.allTheThings() T-Shirt (Red)",
]


def test_sort_dropdown_reordering(login_as):
    """TC-14: az/za/lohi/hilo sort options each produce the correct item order."""
    login_page = login_as(USERS["standard"])
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.sort_by("az")
    assert inventory_page.get_product_names() == EXPECTED_AZ_ORDER

    inventory_page.sort_by("za")
    assert inventory_page.get_product_names() == list(reversed(EXPECTED_AZ_ORDER))

    inventory_page.sort_by("lohi")
    prices = inventory_page.get_product_prices()
    assert prices == sorted(prices)

    inventory_page.sort_by("hilo")
    prices = inventory_page.get_product_prices()
    assert prices == sorted(prices, reverse=True)
