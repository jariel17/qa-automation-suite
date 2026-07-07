from playwright.sync_api import Page

class Footer:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.twitter_link = page.get_by_role("link", name="Twitter")
        self.facebook_link = page.get_by_role("link", name="Facebook")
        self.linkedin_link = page.get_by_role("link", name="LinkedIn")
        self.footer_text = page.locator('[data-test="footer-copy"]')