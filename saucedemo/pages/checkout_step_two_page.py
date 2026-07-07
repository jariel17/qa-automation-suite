from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.header import Header
from pages.footer import Footer

class CheckoutStepTwoPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)
        self.subtotal_label = page.locator(".summary_subtotal_label")
        self.tax_label = page.locator(".summary_tax_label")
        self.total_label = page.locator(".summary_total_label")
        self.finish_button = page.get_by_role("button", name="Finish")
        self.line_item_names = page.locator(".inventory_item_name")

    def get_line_item_names(self) -> list[str]:
        items = self.line_item_names.all_inner_texts()
        return items

    def get_subtotal(self) -> float:
        subtotal = self.subtotal_label.inner_text().split("$")[1]
        return float(subtotal)
    
    def get_tax(self) -> float:
        tax = self.tax_label.inner_text().split("$")[1]
        return float(tax)
    
    def get_total(self) -> float:
        total = self.total_label.inner_text().split("$")[1]
        return float(total)
    
    def finish(self) -> None:
        self.finish_button.click()