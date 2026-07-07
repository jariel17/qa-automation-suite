from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.header import Header
from pages.footer import Footer

class CheckoutStepOnePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)
        self.first_name_field = page.get_by_placeholder("First Name")
        self.last_name_field = page.get_by_placeholder("Last Name")
        self.postal_code_field = page.get_by_placeholder("Zip/Postal Code")
        self.continue_button = page.get_by_role("button", name="Continue")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.error_message = page.locator('[data-test="error"]')

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.first_name_field.fill(first_name)
        self.last_name_field.fill(last_name)
        self.postal_code_field.fill(postal_code)

    def continue_to_overview(self) -> None:
        self.continue_button.click()

    def cancel(self) -> None:
        self.cancel_button.click()