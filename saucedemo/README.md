# Sauce Demo Test Suite

Automated test suite for [saucedemo.com](https://www.saucedemo.com/), a Sauce Labs demo
e-commerce app. Built with **Playwright (Python) + pytest** on a **Page Object Model**.

Covers functional flows, data and content integrity, browser
performance, and a set of targeted security checks.

## Structure

```
saucedemo/
├── conftest.py          # shared fixtures: login_as, perf_timer, error_monitor
├── data/
│   └── users.py         # saucedemo's fixed user personas + password
├── pages/                # Page Object Model
│   ├── base_page.py       # shared page behavior (screenshot capture)
│   ├── header.py           # composed into every post-login page (has-a, not is-a)
│   ├── footer.py
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── inventory_item_page.py
│   ├── cart_page.py
│   ├── checkout_step_one_page.py
│   ├── checkout_step_two_page.py
│   └── checkout_complete_page.py
├── perf/
│   └── psi.py            # Google PageSpeed Insights (Lighthouse) API client
└── tests/
    ├── test_authentication.py
    ├── test_transactions.py
    ├── test_dynamic_content.py
    ├── test_performance.py
    └── test_security.py
```

`Header` and `Footer` are composed into page objects.

Locators follow a priority order: accessible role/label/placeholder first, raw CSS as a last resort.

## What's covered

**`test_authentication.py`**, login and its negative paths: a successful login lands on a
fully populated inventory page with no console or network errors. Five negative-login
scenarios each assert the exact error text and confirm the user stays on the login page.

**`test_transactions.py`**, cart and checkout: adding one or all six products to the cart,
removing an item, a full checkout happy path, checkout field validation, and two arithmetic checks, cart subtotal equals the sum of its line items,
and subtotal plus tax equals the displayed total.

**`test_dynamic_content.py`**, content and data integrity: each of the inventory images maps
to its own distinct product, cart state survives navigating to a product detail page and back,
product name, description, and price match a known-correct catalog, and each of the sort
dropdown's four options produces a specific order.

**`test_performance.py`**, browser-oriented performance: login and inventory-render timing
budgets measured around the actual user action, a full checkout journey
timing budget, and synthetic Lighthouse audits via the PageSpeed Insights API. Overall score plus
per-metric budgets for LCP (Largest Contentful Paint), FCP (First Contentful Paint), TBT (Total Blocking Time), and CLS (Cumulative Layout Shift), split by mobile and desktop strategy.

**`test_security.py`**, targeted security checks: SQLi/XSS-style payloads submitted through
the login form, asserting no auth bypass. Session cookie hardening, presence of security response headers (CSP, X-Frame-Options,
X-Content-Type-Options, Referrer-Policy), and forced-browsing checks confirming every
post-login page actually requires an active session.

## Two different kinds of "red," on purpose

This suite uses two failure conventions:

- **Hard failures** on saucedemo's intentionally-broken personas (`problem_user`,
  `visual_user`, `error_user`) stay as plain failing assertions. They document real,
  reproducible defects in specific user flows and stay visibly red in a normal run, so a defect can't
  quietly disappear from the report.
- **Xfail** `pytest.mark.xfail(strict=True)` is used instead for non-functional issues where a case documents a known finding.

Either way, the *expected result* asserted in the test always states the correct or secure
behavior.

## Full test results

Each row states what the test asserts, which persona/browser it targets, and the current
result on the live app. **Result** is one of:

- **PASS**, correct behavior confirmed, no known issue.
- **XFAIL**, `xfail(strict=True)`, a documented finding; expected to fail today, would flip to
  a loud unexpected-pass failure if the underlying issue ever got fixed.
- **FAIL**, plain hard failure tied to one of saucedemo's intentionally-broken demo personas
  (`problem_user`, `visual_user`, `error_user`), left red on purpose.


### test_authentication.py

| Test ID | Checks | Result |
|---|---|---|
| `test_successful_login_standard_user` (TC-01) | standard_user reaches a fully populated inventory page, no console/network errors | PASS |
| `TC-02-locked-out` | locked_out_user is rejected with the correct error | PASS |
| `TC-03-no-username` | blank username is rejected with the correct error | PASS |
| `TC-04-incorrect-username` | wrong username is rejected with the correct error | PASS |
| `TC-05-no-password` | blank password is rejected with the correct error | PASS |
| `TC-06-incorrect-password` | wrong password is rejected with the correct error | PASS |

### test_transactions.py

| Test ID | Checks | Result | Expected because |
|---|---|---|---|
| `TC-08-standard-user` | add one product to cart | PASS | |
| `TC-08-error-user` | same, with error_user adding the Bolt T-Shirt | FAIL | error_user's add-to-cart button doesn't flip to "Remove" for this product, a known persona defect |
| `TC-09-standard-user` | add all 6 products | PASS | |
| `TC-09-error-user` | same, error_user | FAIL | includes the same Bolt T-Shirt button defect as TC-08 |
| `TC-10-standard-user` | remove one item from cart | PASS | |
| `TC-10-error-user` | same, error_user, using Backpack + Bike Light (not the Bolt T-Shirt) | PASS | doesn't touch the broken product, so the defect never triggers here |
| `TC-11-standard-user` | full checkout happy path, zero-tolerance error monitor | PASS | |
| `TC-11-error-user-last-name-not-retained` | same, error_user | FAIL | error_user's last name field doesn't retain the typed value through checkout, a known persona defect |
| `TC-12-standard-missing-first-name` | blank first name blocks checkout with the right error | PASS | |
| `TC-12-standard-missing-last-name` | blank last name blocks checkout with the right error | PASS | |
| `TC-12-standard-missing-postal-code` | blank postal code blocks checkout with the right error | PASS | |
| `TC-12-error-user-missing-first-name` | same, error_user | PASS | error_user's known bug is scoped to the last name field, first name validation is unaffected |
| `TC-12-error-user-missing-last-name` | same, error_user, blank last name | FAIL | same last-name-field defect as TC-11, the blank value isn't read back correctly so validation never fires and checkout proceeds anyway |
| `TC-12-error-user-missing-postal-code` | same, error_user, blank postal code | PASS | doesn't touch the broken field |
| `TC-15-test_cart_subtotal_equals_sum_of_line_items` | cart subtotal equals sum of line items, real numbers off the page | PASS | |
| `TC-16-test_checkout_step_two_subtotal_plus_tax_equals_total` | subtotal + tax equals displayed total | PASS | |

### test_dynamic_content.py

| Test ID | Checks | Result | Expected because |
|---|---|---|---|
| `TC-07-standard-user` | every inventory image maps to its own product | PASS | |
| `TC-07-problem-user` | same, problem_user | FAIL | problem_user serves the same broken placeholder image for all 6 products, a known persona defect |
| `TC-07-visual-user` | same, visual_user | FAIL | visual_user swaps the Backpack's image for the wrong one, a known persona defect |
| `TC-13-test_cart_persistence_across_navigation` | cart state survives a product-detail visit and back | PASS | |
| `TC-17-standard-user` | product name/description/price match the known-correct catalog | PASS | |
| `TC-17-problem-user` | same, problem_user | PASS | problem_user's known defect is image-only, prices/descriptions are unaffected |
| `TC-17-visual-user` | same, visual_user | FAIL | visual_user serves scrambled prices for all 6 products, a known persona defect |
| `TC-14-test_sort_dropdown_reordering` | all four sort options (A-Z, Z-A, price low-high, price high-low) produce a verified order | PASS | |

### test_performance.py

| Test ID | Checks | Result | Expected because |
|---|---|---|---|
| `PERF-01-standard-user` | login-to-inventory transition under 3s | PASS | |
| `PERF-01-glitch-user` | same, performance_glitch_user | XFAIL | known defect, glitch_user's login transition consistently exceeds the 3s budget |
| `PERF-02-standard-user` | inventory render under 2s | PASS | |
| `PERF-02-glitch-user` | same, performance_glitch_user | XFAIL | known defect, glitch_user's inventory render consistently exceeds the 2s budget |
| `PERF-03-standard-user` | full checkout journey under 5s | PASS | |
| `PERF-03-glitch-user` | same, performance_glitch_user | PASS | glitch_user's injected delay is isolated to login and inventory render, it doesn't show up in the checkout journey, so no xfail is coded here and none is expected |
| `PERF-04-mobile` / `PERF-04-desktop` | PSI performance score above floor | PASS | (skips cleanly without `PSI_API_KEY`) |
| `PERF-05-desktop-lcp` | desktop LCP within Core Web Vitals budget | PASS | (skips cleanly without `PSI_API_KEY`) |
| `PERF-05-mobile-lcp` | mobile LCP within budget | XFAIL | known finding, mobile LCP measured 2.74s-3.06s across baseline runs against a 2.5s (skips cleanly without `PSI_API_KEY`) |
| `PERF-05-desktop-fcp` | desktop FCP within budget | PASS | (skips cleanly without `PSI_API_KEY`) |
| `PERF-05-mobile-fcp` | mobile FCP within budget | XFAIL | known finding, mobile FCP measured 2.74s-2.86s across baseline runs against a 1.8s (skips cleanly without `PSI_API_KEY`) |
| `PERF-05-desktop-tbt` / `PERF-05-mobile-tbt` | total blocking time within budget | PASS | (skips cleanly without `PSI_API_KEY`) |
| `PERF-05-desktop-cls` / `PERF-05-mobile-cls` | cumulative layout shift within budget | PASS | (skips cleanly without `PSI_API_KEY`) |

### test_security.py

| Test ID | Checks | Result | Expected because |
|---|---|---|---|
| `SEC-01-sqli-or-true` / `SEC-01-sqli-comment` | SQLi-style login payloads authenticate nowhere, no dialog, no uncaught JS error | PASS | |
| `SEC-02-xss-script-tag` / `SEC-02-xss-attr-breakout` | XSS-style login payloads execute nothing, reflect nowhere | PASS | |
| `SEC-03-httponly` | session cookie is HttpOnly | XFAIL | known finding, `session-username` cookie observed `httpOnly=False` |
| `SEC-04-secure` | session cookie is Secure | XFAIL | known finding, `session-username` cookie observed `secure=False` on an HTTPS-only site |
| `test_session_cookie_samesite_is_restrictive` (SEC-05) | session cookie SameSite is Lax or Strict | PASS | |
| `test_session_cookie_value_is_opaque` (SEC-06) | session cookie value isn't the plaintext username | XFAIL | known finding, the cookie's value is observed to literally be `standard_user` |
| `SEC-07-csp` | Content-Security-Policy header present | XFAIL | known finding, no CSP header on the live site |
| `SEC-08-xfo` | X-Frame-Options header present | XFAIL | known finding, no X-Frame-Options header, page is iframe-embeddable |
| `SEC-09-xcto` | X-Content-Type-Options header present | XFAIL | known finding, header absent |
| `SEC-10-referrer` | Referrer-Policy header present | XFAIL | known finding, header absent |
| `SEC-11-inventory` / `-cart` / `-checkout-step-one` / `-checkout-step-two` / `-checkout-complete` | each protected page redirects to login when accessed without a session | PASS | |

## Running

From the repository root:

```bash
uv sync
uv run playwright install chromium

# whole suite
uv run pytest saucedemo/tests/ -v

# one file
uv run pytest saucedemo/tests/test_security.py -v
```

The two PageSpeed Insights performance cases (`PERF-04`, `PERF-05`) need a `PSI_API_KEY` in a
`saucedemo/.env` file (a free Google API key). Without it, those two cases skip cleanly.
Everything else runs regardless.

Current clean run: **63 collected, 45 passed, 11 xfailed** (documented findings),
**7 failed** (intentional persona-defect exposure). Full breakdown in
[Full test results](#full-test-results).
