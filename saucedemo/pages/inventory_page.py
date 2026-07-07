from playwright.sync_api import Page
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
        self.item_names = page.locator(".inventory_item_name")
        self.item_prices = page.locator(".inventory_item_price")

    def add_to_cart(self, product_name: str) -> None:
        item = self.page.locator(".inventory_item").filter(has_text=product_name)
        item.get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, product_name: str) -> None:
        item = self.page.locator(".inventory_item").filter(has_text=product_name)
        item.get_by_role("button", name="Remove").click()

    def sort_by(self, value: str) -> None:
        self.sort_dropdown.select_option(value=value)

    def get_product_names(self) -> list[str]:
        return self.item_names.all_inner_texts() #no auto-wait

    def get_product_prices(self) -> list[float]:
        price_texts = self.item_prices.all_inner_texts()
        prices = [float(p.replace("$", "")) for p in price_texts]
        return prices
