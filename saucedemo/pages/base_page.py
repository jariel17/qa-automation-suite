from playwright.sync_api import Page
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"

class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def capture_screenshot(self, file_name: str) -> None:
        self.page.screenshot(path=SCREENSHOTS_DIR / f"{file_name}.png")