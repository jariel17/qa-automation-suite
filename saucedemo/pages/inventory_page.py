from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.header import Header
from pages.footer import Footer

BASE_URL = "https://www.saucedemo.com/"

class InventoryPage(BasePage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self.items = page.locator(".inventory_item")
        self.item_names = page.locator(".inventory_item_name")
        self.item_prices = page.locator(".inventory_item_price")
        self.item_images = page.locator(".inventory_item_img img")

    def add_to_cart(self, product_name: str) -> None:
        item = self.page.locator(".inventory_item").filter(has_text=product_name)
        item.get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, product_name: str) -> None:
        item = self.page.locator(".inventory_item").filter(has_text=product_name)
        item.get_by_role("button", name="Remove").click()

    def sort_by(self, value: str) -> None:
        self.sort_dropdown.select_option(value=value)

    def get_item_button(self, product_name: str) -> Locator:
        item = self.page.locator(".inventory_item").filter(has_text=product_name)
        return item.locator("button")

    def get_product_names(self) -> list[str]:
        return self.item_names.all_inner_texts() #no auto-wait

    def get_product_prices(self) -> list[float]:
        price_texts = self.item_prices.all_inner_texts()
        prices = [float(p.replace("$", "")) for p in price_texts]
        return prices

    def wait_for_images_to_load(self) -> None:
        self.page.wait_for_function(
            "() => [...document.querySelectorAll('.inventory_item_img img')]"
            ".every(img => img.complete && img.naturalWidth > 0)"
        )

    def get_product_image_map(self) -> dict[str, str]:
        image_map = {}
        for item in self.items.all():
            name = item.locator(".inventory_item_name").inner_text()
            src = item.locator(".inventory_item_img img").get_attribute("src")
            image_map[name] = src
        return image_map
