import os

import pytest
from playwright.sync_api import expect

from data.users import PASSWORD, USERS
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from perf.psi import fetch_psi_result

LOGIN_BUDGET_SECONDS = 3.0


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="PERF-01-standard-user"),
        pytest.param(USERS["performance_glitch"], id="PERF-01-glitch-user",
            marks=pytest.mark.xfail(
                reason=(
                    "Known defect: performance_glitch_user login transition exceeds the "
                    "3s budget"
                ),
                strict=True,
            ),
        ),
    ],
)
def test_login_transition_timing(page, perf_timer, username):
    """PERF-01: login transition (submit -> inventory visible) completes within budget.
    Functional gate: inventory product list becomes visible.
    Performance gate: transition duration stays under the 3s login budget.
    """
    login_page = LoginPage(page)
    login_page.load()
    login_page.fill_credentials(username, PASSWORD)

    with perf_timer() as sw:
        login_page.submit()
        inventory_page = InventoryPage(page)
        expect(inventory_page.items.first).to_be_visible()

    print(f"\n[PERF-01] {username}: {sw.duration:.3f}s")
    assert sw.duration < LOGIN_BUDGET_SECONDS


INVENTORY_BUDGET_SECONDS = 2.0


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="PERF-02-standard-user"),
        pytest.param(USERS["performance_glitch"], id="PERF-02-glitch-user",
            marks=pytest.mark.xfail(
                reason=(
                    "Known defect: performance_glitch_user inventory render exceeds the 2s "
                    "budget "
                ),
                strict=True,
            ),
        ),
    ],
)
def test_inventory_load_and_render_timing(login_as, perf_timer, username):
    """PERF-02: inventory page load + render timing on an authenticated reload.
    Functional gate: all 6 products visible after reload.
    Performance gate: render-complete stays under the 2s inventory budget.
    """
    login_page = login_as(username)
    page = login_page.page
    inventory_page = InventoryPage(page)

    with perf_timer() as sw:
        page.reload()
        expect(inventory_page.items).to_have_count(6)

    nav_timing = page.evaluate(
        "() => { const [nav] = performance.getEntriesByType('navigation'); "
        "return { domContentLoaded: nav.domContentLoadedEventEnd / 1000, "
        "loadEventEnd: nav.loadEventEnd / 1000 }; }"
    )

    print(f"\n[PERF-02] {username}: render={sw.duration:.3f}s nav={nav_timing}")
    assert sw.duration < INVENTORY_BUDGET_SECONDS


CHECKOUT_BUDGET_SECONDS = 5.0
CHECKOUT_PRODUCT = "Sauce Labs Backpack"
FIRST_NAME = "Ariel"
LAST_NAME = "Acosta"
POSTAL_CODE = "12345"


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(USERS["standard"], id="PERF-03-standard-user"),
        pytest.param(USERS["performance_glitch"], id="PERF-03-glitch-user"),
    ],
)
def test_checkout_journey_timing(login_as, perf_timer, username):
    """PERF-03: full checkout journey (cart -> confirmation) completes within budget.

    Login and cart setup happen before timing starts. 
    The glitch does not show up here. No xfail needed.
    """
    login_page = login_as(username)
    page = login_page.page
    inventory_page = InventoryPage(page)

    inventory_page.add_to_cart(CHECKOUT_PRODUCT)
    inventory_page.header.go_to_cart()
    cart_page = CartPage(page)

    with perf_timer() as sw:
        cart_page.checkout()

        checkout_step_one = CheckoutStepOnePage(page)
        checkout_step_one.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
        checkout_step_one.continue_to_overview()

        checkout_step_two = CheckoutStepTwoPage(page)
        checkout_step_two.finish()

        checkout_complete = CheckoutCompletePage(page)
        expect(checkout_complete.complete_header).to_be_visible()

    print(f"\n[PERF-03] {username}: {sw.duration:.3f}s")
    assert sw.duration < CHECKOUT_BUDGET_SECONDS


PSI_URL = "https://www.saucedemo.com/"
PSI_SCORE_FLOOR = 0.5
PSI_API_KEY = os.environ.get("PSI_API_KEY")

_psi_skip = pytest.mark.skipif(
    not PSI_API_KEY,
    reason=(
        "PSI_API_KEY not set in environment; skipping PageSpeed Insights audit "
    ),
)


@_psi_skip
@pytest.mark.parametrize(
    "strategy",
    [
        pytest.param("mobile", id="PERF-04-mobile"),
        pytest.param("desktop", id="PERF-04-desktop"),
    ],
)
def test_login_page_psi_score(strategy):
    """PERF-04: login page passes a PageSpeed Insights performance audit.

    """
    result = fetch_psi_result(PSI_URL, strategy)
    lr = result["lighthouseResult"]
    score = lr["categories"]["performance"]["score"]
    audits = lr["audits"]

    fcp = audits["first-contentful-paint"]["numericValue"] / 1000
    lcp = audits["largest-contentful-paint"]["numericValue"] / 1000
    tbt = audits["total-blocking-time"]["numericValue"]
    cls = audits["cumulative-layout-shift"]["numericValue"]

    print(
        f"\n[PERF-04] strategy={strategy} score={score:.2f} "
        f"FCP={fcp:.3f}s LCP={lcp:.3f}s TBT={tbt:.0f}ms CLS={cls:.4f}"
    )

    assert score >= PSI_SCORE_FLOOR


PSI_METRIC_CASES = [
    pytest.param("lcp", "largest-contentful-paint", 2.5, "seconds", "desktop", id="PERF-05-desktop-lcp"),
    pytest.param("lcp", "largest-contentful-paint", 2.5, "seconds", "mobile", id="PERF-05-mobile-lcp",
        marks=pytest.mark.xfail(
            reason=(
                "Known finding: saucedemo login page's mobile LCP observed 2.74s-3.06s across "
                "5 baseline runs, consistently exceeding the 2.5s Core Web Vitals "
                "'good' line."
            ),
            strict=True,
        ),
    ),
    pytest.param("fcp", "first-contentful-paint", 1.8, "seconds", "desktop", id="PERF-05-desktop-fcp"),
    pytest.param("fcp", "first-contentful-paint", 1.8, "seconds", "mobile", id="PERF-05-mobile-fcp",
        marks=pytest.mark.xfail(
            reason=(
                "Known finding: saucedemo login page's mobile FCP observed 2.74s-2.86s across "
                "5 baseline runs, consistently exceeding the 1.8s good line."
            ),
            strict=True,
        ),
    ),
    pytest.param("tbt", "total-blocking-time", 200, "ms", "desktop", id="PERF-05-desktop-tbt"),
    pytest.param("tbt", "total-blocking-time", 200, "ms", "mobile", id="PERF-05-mobile-tbt"),
    pytest.param("cls", "cumulative-layout-shift", 0.1, "raw", "desktop", id="PERF-05-desktop-cls"),
    pytest.param("cls", "cumulative-layout-shift", 0.1, "raw", "mobile", id="PERF-05-mobile-cls"),
]


@_psi_skip
@pytest.mark.parametrize("metric_name,audit_id,budget,unit,strategy", PSI_METRIC_CASES)
def test_login_page_psi_metric_budgets(metric_name, audit_id, budget, unit, strategy):
    """PERF-05: login page meets per-metric PSI performance budgets.

    Reuses PERF-04's PSI call for the same strategy. Each metric/strategy pair is its own
    parametrized case so a single failing metric don't masks the other three.
    """
    result = fetch_psi_result(PSI_URL, strategy)
    audits = result["lighthouseResult"]["audits"]
    raw_value = audits[audit_id]["numericValue"]
    value = raw_value / 1000 if unit == "seconds" else raw_value

    print(
        f"\n[PERF-05] strategy={strategy} metric={metric_name} value={value:.4f} "
        f"budget={budget}"
    )

    assert value <= budget
