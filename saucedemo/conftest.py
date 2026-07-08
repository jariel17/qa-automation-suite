import time
from contextlib import contextmanager

import pytest
from dotenv import load_dotenv
from pages.login_page import LoginPage
from data.users import PASSWORD

load_dotenv()


@pytest.fixture
def login_as(page):
    def _login_as(username: str, password: str = PASSWORD) -> LoginPage:
        login_page = LoginPage(page)
        login_page.load()
        login_page.login(username, password)
        return login_page
    return _login_as


KNOWN_NOISE_DOMAINS = ("events.backtrace.io",)
"""Domains excluded from error_monitor."""


def _is_known_noise(url: str) -> bool:
    return any(domain in url for domain in KNOWN_NOISE_DOMAINS)


@pytest.fixture
def error_monitor(page):
    """Collects console errors, uncaught JS exceptions, 4xx/5xx responses, and failed
    requests seen during the test, excluding KNOWN_NOISE_DOMAINS. Assert the returned list
    is empty at the end of the flow being validated."""
    problems: list[str] = []

    def _on_console(msg):
        if msg.type == "error" and not _is_known_noise(msg.location["url"]):
            problems.append(f"console error: {msg.text} ({msg.location['url']})")

    def _on_pageerror(exc):
        problems.append(f"pageerror: {exc}")

    def _on_response(response):
        if response.status >= 400 and not _is_known_noise(response.url):
            problems.append(f"response {response.status}: {response.url}")

    def _on_requestfailed(request):
        problems.append(f"requestfailed: {request.url} ({request.failure})")

    page.on("console", _on_console)
    page.on("pageerror", _on_pageerror)
    page.on("response", _on_response)
    page.on("requestfailed", _on_requestfailed)

    return problems


class Stopwatch:
    def __init__(self) -> None:
        self.duration: float | None = None


@contextmanager
def _perf_timer():
    sw = Stopwatch()
    start = time.perf_counter()
    try:
        yield sw
    finally:
        sw.duration = time.perf_counter() - start


@pytest.fixture
def perf_timer():
    return _perf_timer