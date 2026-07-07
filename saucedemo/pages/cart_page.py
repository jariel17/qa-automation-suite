from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.header import Header
from pages.footer import Footer

class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)
        self.cart_items = page.locator(".cart_item")
        self.cart_item_names = page.locator(".inventory_item_name")
        self.cart_item_prices = page.locator(".inventory_item_price")
        self.checkout_button = page.get_by_role("button", name="checkout")
        self.continue_shopping_button = page.get_by_role("button", name="Continue Shopping")

    def remove_from_cart(self, product_name: str) -> None:
        item = self.cart_items.filter(has_text=product_name)
        item.get_by_role("button", name="Remove").click()

    def get_cart_item_names(self) -> list[str]:
        items = self.cart_item_names.all_inner_texts()
        return items
    
    def get_cart_item_prices(self) -> list[float]:
        price_texts = self.cart_item_prices.all_inner_texts()
        prices = [float(p.replace("$", "")) for p in price_texts]
        return prices

    def checkout(self) -> None:
        self.checkout_button.click()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()