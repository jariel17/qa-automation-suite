import pytest
from playwright.sync_api import expect

from data.users import USERS
from pages.inventory_page import InventoryPage

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
