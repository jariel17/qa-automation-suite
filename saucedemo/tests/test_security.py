import pytest
import requests
from playwright.sync_api import expect

from data.users import USERS
from pages.login_page import LoginPage

SAUCEDEMO_URL = "https://www.saucedemo.com/"
INVALID_CREDENTIALS_ERROR = (
    "Epic sadface: Username and password do not match any user in this service"
)


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("' OR '1'='1", id="SEC-01-sqli-or-true"),
        pytest.param("admin'--", id="SEC-01-sqli-comment"),
        pytest.param("<script>alert('xss')</script>", id="SEC-02-xss-script-tag"),
        pytest.param("\"><img src=x onerror=alert('xss')>", id="SEC-02-xss-attr-breakout"),
    ],
)
def test_login_rejects_malicious_input_safely(page, payload):
    """SEC-01/SEC-02: SQLi/XSS-style login input authenticates nowhere, executes nothing, reflects nowhere.
    Maps to OWASP Top 10 2025: A05 Injection.
    """
    dialogs = []
    page_errors = []

    def _on_dialog(dialog):
        dialogs.append(dialog.message)
        dialog.dismiss()

    def _on_page_error(error):
        page_errors.append(str(error))

    page.on("dialog", _on_dialog)
    page.on("pageerror", _on_page_error)

    login_page = LoginPage(page)
    login_page.load()
    login_page.login(payload, "irrelevant")

    # No auth bypass
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(login_page.error_message).to_have_text(INVALID_CREDENTIALS_ERROR)

    # No script execution (XSS)
    assert dialogs == [], f"Payload triggered a JS dialog: {dialogs}"
    assert page_errors == [], f"Payload triggered an uncaught JS error: {page_errors}"


def _get_session_cookie(login_as):
    login_page = login_as(USERS["standard"])
    cookies = login_page.page.context.cookies()
    return next(c for c in cookies if c["name"] == "session-username")


@pytest.mark.parametrize(
    "attribute,expected",
    [
        pytest.param("httpOnly", True, id="SEC-03-httponly",
            marks=pytest.mark.xfail(
                reason=(
                    "Known finding: session-username cookie is not HttpOnly, readable "
                    "by page JavaScript (observed httpOnly=False)."
                ),
                strict=True,
            ),
        ),
        pytest.param("secure", True, id="SEC-04-secure",
            marks=pytest.mark.xfail(
                reason=(
                    "Known finding: session-username cookie is not marked Secure on an "
                    "HTTPS-only site (observed secure=False)."
                ),
                strict=True,
            ),
        ),
    ],
)
def test_session_cookie_flag(login_as, attribute, expected):
    """SEC-03/SEC-04: session cookie HttpOnly/Secure flags. Secure behaviour is asserted;
    real gaps are carried as documented findings via xfail.
    Maps to OWASP Top 10 2025: A07 Authentication Failures (HttpOnly, SEC-03), A04
    Cryptographic Failures (Secure, SEC-04).
    """
    session_cookie = _get_session_cookie(login_as)
    assert session_cookie[attribute] is expected


def test_session_cookie_samesite_is_restrictive(login_as):
    """SEC-05: session cookie SameSite is Lax or Strict.
    Maps to OWASP Top 10 2025: A07 Authentication Failures.
    """
    session_cookie = _get_session_cookie(login_as)
    assert session_cookie["sameSite"] in ("Lax", "Strict")


@pytest.mark.xfail(
    reason=(
        "Known finding: the session-username cookie's value is the plaintext username "
        "itself (observed value == 'standard_user'), not an opaque/random session token. "
        "A trivially predictable session identifier."
    ),
    strict=True,
)
def test_session_cookie_value_is_opaque(login_as):
    """SEC-06: session cookie value should be an opaque token, not the plaintext username.
    Maps to OWASP Top 10 2025: A07 Authentication Failures.
    """
    session_cookie = _get_session_cookie(login_as)
    assert session_cookie["value"] != "standard_user"


@pytest.mark.parametrize(
    "header",
    [
        pytest.param("Content-Security-Policy", id="SEC-07-csp",
            marks=pytest.mark.xfail(
                reason="Known finding: no CSP header present.",
                strict=True,
            ),
        ),
        pytest.param("X-Frame-Options", id="SEC-08-xfo",
            marks=pytest.mark.xfail(
                reason=(
                    "Known finding: no X-Frame-Options header present, page is "
                    "embeddable in an iframe."
                ),
                strict=True,
            ),
        ),
        pytest.param(
            "X-Content-Type-Options", id="SEC-09-xcto", marks=pytest.mark.xfail(
                reason=(
                    "Known finding: no X-Content-Type-Options header present "
                ),
                strict=True,
            ),
        ),
        pytest.param("Referrer-Policy", id="SEC-10-referrer",
            marks=pytest.mark.xfail(
                reason="Known finding: no Referrer-Policy header present.",
                strict=True,
            ),
        ),
    ],
)
def test_security_response_header_present(header):
    """SEC-07/SEC-08/SEC-09/SEC-10: saucedemo login page carries expected security headers.

    Maps to OWASP Top 10 2025: A02 Security Misconfiguration.
    """
    response = requests.get(SAUCEDEMO_URL, timeout=10)
    assert header in response.headers


PROTECTED_PATHS = [
    "inventory.html",
    "cart.html",
    "checkout-step-one.html",
    "checkout-step-two.html",
    "checkout-complete.html",
]


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(p, id=f"SEC-11-{p.removesuffix('.html')}")
        for p in PROTECTED_PATHS
    ],
)
def test_protected_page_requires_login(page, path):
    """SEC-11: protected pages are not reachable without an active session.

    Maps to OWASP Top 10 2025: A01 Broken Access Control.
    """
    page.goto(f"{SAUCEDEMO_URL}{path}")

    expect(page).to_have_url(SAUCEDEMO_URL)
    login_page = LoginPage(page)
    expect(login_page.error_message).to_have_text(
        f"Epic sadface: You can only access '/{path}' when you are logged in."
    )
    expect(login_page.username_field).to_be_visible()
