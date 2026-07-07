import pytest
from pages.login_page import LoginPage
from data.users import PASSWORD

@pytest.fixture
def login_as(page):
    def _login_as(username: str, password: str = PASSWORD) -> LoginPage:
        login_page = LoginPage(page)
        login_page.load()
        login_page.login(username, password)
        return login_page
    return _login_as