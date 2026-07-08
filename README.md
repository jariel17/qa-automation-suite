# QA Automation Suite

Two independent automated test suites, one for a web application, one for a public API,
built to show a full spread of QA automation practice: functional UI testing, page object
design, browser performance budgets, targeted security checks, and API contract/negative
testing.

## Projects

### `saucedemo/`

A Playwright (Python) + pytest suite against [saucedemo.com](https://www.saucedemo.com/), a
Sauce Labs demo e-commerce app, built on a Page Object Model. Covers login and its negative
paths, cart and checkout flows, content/data
integrity across saucedemo's intentionally-broken demo personas, browser performance budgets, and
a set of security checks anchored to OWASP Top 10 categories.

### `datausa_api/`

A Postman/Newman collection against the public [Data USA](https://datausa.io/) Tesseract API,
a read-only statistical data service with no authentication. Covers cube/dimension metadata,
the core data-query endpoint across every output format it supports, pagination behavior, and
a set of negative tests checked for safe, structured error handling.

Both suites verify real, live behavior rather than mocked responses, and both are written to
keep passing/failing signal meaningful: a known, reproducible defect is documented and asserted
against the *correct* expected behavior.

## Stack

- **Python**, managed with **uv**
- **Playwright** for browser automation, **pytest** as the runner
- **requests** for direct HTTP calls (performance and security checks that don't need a
  browser)
- **ruff** for linting
- **Postman / Newman** for the API suite

## Setup

```bash
uv sync
uv run playwright install chromium
```

## Running

```bash
# saucedemo suite
uv run pytest saucedemo/tests/ -v

# a single file
uv run pytest saucedemo/tests/test_security.py -v
```

The two PageSpeed Insights performance cases need a `PSI_API_KEY` (a free Google API key) in
a `saucedemo/.env` file. Without it, those two cases skip cleanly rather than failing.

For the API suite, import the collection and environment files in `datausa_api/` into Postman
and run them in order, or run them
headlessly with Newman:

```bash
newman run "datausa_api/Data USA API Test Suite.postman_collection.json" \
  -e "datausa_api/Data USA API.postman_environment.json"
```
