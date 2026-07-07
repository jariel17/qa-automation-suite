from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.header import Header
from pages.footer import Footer

class CheckoutCompletePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)
        self.complete_header = page.locator(".complete-header")
        self.complete_text = page.locator(".complete-text")
        self.pony_express_image = page.get_by_alt_text("Pony Express")
        self.back_home_button = page.get_by_role("button", name="Back Home")
    
    def back_home(self) -> None:
        self.back_home_button.click()
        