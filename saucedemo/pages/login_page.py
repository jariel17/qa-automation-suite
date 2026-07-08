from playwright.sync_api import Page
from pages.base_page import BasePage

BASE_URL = "https://www.saucedemo.com/"

class LoginPage(BasePage):
    
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_field = page.get_by_placeholder("Username")
        self.password_field = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.error_message = page.locator('[data-test="error"]')
    
    def load(self) -> None:
        self.page.goto(BASE_URL)

    def fill_credentials(self, username: str, password: str) -> None:
        self.username_field.fill(username)
        self.password_field.fill(password)

    def submit(self) -> None:
        self.login_button.click()

    def login(self, username: str, password: str) -> None:
        self.fill_credentials(username, password)
        self.submit()