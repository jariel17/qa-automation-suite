from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.header import Header
from pages.footer import Footer

class InventoryItemPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)
        self.back_to_products_button = page.get_by_role("button", name="Back to products")

    def back_to_products(self) -> None:
        self.back_to_products_button.click()
