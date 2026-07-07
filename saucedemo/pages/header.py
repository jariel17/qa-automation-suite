from playwright.sync_api import Page

class Header:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.burger_menu_button = page.get_by_role("button", name="Open Menu")
        self.logout_link = page.get_by_role("link", name="Logout")
        self.reset_app_state_link = page.get_by_role("link", name="Reset App State")
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')
        self.title_bar = page.locator('[data-test="title"]')

    def open_menu(self) -> None:
        self.burger_menu_button.click()

    def reset_app_state(self) -> None:
        self.open_menu()
        self.reset_app_state_link.click()

    def logout(self) -> None:
        self.open_menu()
        self.logout_link.click()

    def go_to_cart(self) -> None:
        self.cart_link.click()

    def get_cart_count(self) -> int:
        if self.cart_badge.count() == 0: # count checks whether there is a badge or not
            return 0
        return int(self.cart_badge.inner_text())
    
    def get_page_title(self) -> str:
        page_title = self.title_bar.inner_text()
        return page_title
    