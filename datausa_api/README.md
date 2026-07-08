# Data USA API Test Suite

A Postman/Newman collection testing the public [Data USA](https://datausa.io/) Tesseract API
(`https://api.datausa.io/tesseract`), a read-only OLAP-style statistical data service (cubes,
dimensions, measures) with no authentication.

**20 requests, 82 assertions**, across three folders: Metadata, Data Queries, and Negative
tests.

## Structure

```
datausa_api/
├── Data USA API Test Suite.postman_collection.json
└── Data USA API.postman_environment.json
```

## What's covered

**Metadata** (`DATAUSA-01` to `-05`): the cube catalog, full schema detail for two specific
cubes, and dimension member listings, each validated against a real JSON Schema.

**Data Queries** (`DATAUSA-06` to `-13`): the core `/data.*` query endpoint exercised across
every output format it supports, JSON records, JSON arrays, CSV, TSV, Parquet, and XLSX, plus
pagination behavior (`limit`/`offset`) checked against the actual dataset size.

**Negative tests** (`DATAUSA-14` to `-20`): a missing required parameter, an invalid cube
name, an invalid dimension level, an invalid `include` filter value, an unsupported output
format, a zero `limit`, and a SQL-injection-style payload in a filter value, each checked for
a safe, structured error response with no internal detail leaked.

## Design notes

- **Dynamic data extraction** `DATAUSA-04` extracts California's state ID from a
  members response into an environment variable; a later request re-verifies that exact row
  by ID rather than by name. `DATAUSA-06` extracts a computed row count that `DATAUSA-13`'s
  pagination assertion depends on. Because of this, the collection is meant to run in order,
  full collection, not individual requests in isolation.

- **Authentication is explicitly not applicable.** This is a genuinely public, unauthenticated API.

- **Parameterization.** Cube name, dimension levels, measure, year, and page size are all
  environment variables (`population_cube`, `state_level`, `year_level`, `measure_population`,
  `selected_year`, `page_limit`), not hardcoded into request URLs, so the same requests can be
  pointed at a different cube or year by changing the environment alone.

## Findings

The negative-test and format-coverage requests found the following defects:

- Two invalid-entity lookups (invalid cube name, invalid dimension level) return a structured
  `400`, but the response body leaks a `debug_mode` flag and an internal traceback.
- Several edge-case parameter values, a `limit=0`, an invalid `include` filter, return a bare, unstructured `500 Internal Server Error` insteadof a clean `400`.
- Three output-format variants of the data  endpoint (`jsonarrays`, `.parquet`, `.xlsx`)
  currently return `500` for a query that succeeds fine as `.jsonrecords`, `.csv`, or `.tsv`.


## Full test results

Every request below states what it checks and its current result. **Result** is PASS when
every assertion in the request passes, or FAIL when at least one does.

Result here is per request. The assertion-level count in "Running" below (62
pass / 20 fail out of 82) is finer-grained: 8 of the 20 requests below carry at least one
failing assertion, accounting for all 20 failed assertions between them.

### Metadata

| Request | Checks | Result | Notes |
|---|---|---|---|
| `DATAUSA-01` List cubes | cube catalog is a non-empty array, population cube is present, matches the cube-catalog schema | PASS | |
| `DATAUSA-02` Get cube schema | earnings cube's schema is well-formed, name matches the request | PASS | |
| `DATAUSA-03` Get population cube schema | population cube's dimensions and measures are well-formed | PASS | |
| `DATAUSA-04` Get State members | at least 50 US states returned, schema holds, California's state ID extracted for later chaining | PASS | |
| `DATAUSA-05` Get Year members | year members are well-formed 4-digit keys, the selected year is present | PASS | |

### Data Queries

| Request | Checks | Result | Notes |
|---|---|---|---|
| `DATAUSA-06` population by state, jsonrecords | full unpaginated dataset, matches schema, California's row matches the ID from DATAUSA-04, row count captured for later chaining | PASS | |
| `DATAUSA-07` population by state, jsonarrays | same query, `jsonarrays` output | FAIL | live API returns a bare `500` for this format instead of `200`, one of the three broken output formats |
| `DATAUSA-08` population by state, csv | same query, `csv` output | PASS | |
| `DATAUSA-09` population by state, tsv | same query, `tsv` output | PASS | |
| `DATAUSA-10` population by state, parquet | same query, `parquet` output | FAIL | returns a bare 500 for this format instead of 200, one of the three broken output formats |
| `DATAUSA-11` population by state, xlsx | same query, `xlsx` output | FAIL | returns a bare 500 for this format instead of 200, one of the three broken output formats |
| `DATAUSA-12` population by state, limit=5 offset=0 | page reflects the requested limit, `page.total` still reflects the full dataset | PASS | |
| `DATAUSA-13` population by state, limit=10 offset=5 | same, non-zero offset | FAIL | returns a bare 500 as soon as the offset is non-zero, pagination is broken with an offset even though `limit` alone works fine (DATAUSA-12) |

### Negative tests

| Request | Checks | Result | Notes |
|---|---|---|---|
| `DATAUSA-14` Missing required parameter | clean `400`, error names the missing parameter | PASS | |
| `DATAUSA-15` Invalid cube name | structured `400`, error type names the invalid cube | FAIL | status and error-shape assertions pass. The "no internal leak" assertion fails, response includes `debug_mode` and a `traceback` |
| `DATAUSA-16` `limit=0` | invalid limit is handled gracefully | FAIL | returns a bare `500` instead of a structured `4xx` |
| `DATAUSA-17` Invalid dimension level | structured `400`, error type names the invalid level | FAIL | status and error-shape assertions pass. The "no internal leak" assertion fails, response includes debug_mode and a traceback |
| `DATAUSA-18` Invalid `include` filter value | invalid filter is handled gracefully, no leak | FAIL | `500` instead of `4xx`, and the body isn't even JSON, a plain-text stack trace |
| `DATAUSA-19` Invalid output format (`jsonx`) | unsupported format returns `400`, no internal detail | PASS |  |
| `DATAUSA-20` SQLi-style payload in a filter value | query never succeeds, no internal detail leaked | PASS | fails safely; this case doesn't require a specific status code, only that injection doesn't succeed and nothing leaks |

## Running

Import both files into Postman, select the **Data USA API** environment, and run the full
collection in order.

Or via [Newman](https://github.com/postmanlabs/newman):

```bash
newman run "Data USA API Test Suite.postman_collection.json" \
  -e "Data USA API.postman_environment.json"
```

Current clean run: **20/20 requests execute, 82/82 assertions run, 62 pass / 20
fail**, the 20 failures are the documented findings above.
