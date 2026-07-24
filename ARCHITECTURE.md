# Architecture & interview notes

## Stack

- Python 3.10+
- Selenium 4.25 (uses Selenium Manager, so no manual chromedriver)
- pytest 8.3 + pytest-html for reports
- GitHub Actions for CI

## Layers

```
tests/            what a user does           (no Selenium calls)
   |
   v
pages/            how each page works        (locators + actions)
   |
   v
BasePage          Selenium primitives        (wait, click, type, is_visible)
   |
   v
Selenium WebDriver + Chrome
```

Plus two supporting pieces:

- `utils/config.py` - reads env vars into a frozen dataclass (`CONFIG`)
- `conftest.py` - `driver` fixture (fresh Chrome per test) + a hook that
  screenshots the browser when a test fails

## How a test runs

1. pytest picks up the test and requests the `driver` fixture
2. `conftest._build_driver()` starts Chrome (headless if `E2E_HEADLESS=true`)
3. Test does `LoginPage(driver).open().login(...)` and gets back an
   `InventoryPage` - each action returns the page it lands on, so tests
   read as a sentence
4. Every page-object method delegates to `BasePage.click` / `type_text` /
   `text_of` / `is_visible`, which wrap `WebDriverWait` + `expected_conditions`
5. Assertions are in the test, not the page object (page objects don't know
   about pytest)
6. On failure, `pytest_runtest_makereport` grabs the driver off the test
   node and writes a screenshot into `screenshots/`
7. Fixture teardown calls `driver.quit()`

## Design choices worth calling out

- **POM.** Tests describe user intent (`add_to_cart`, `proceed_to_checkout`).
  When SauceDemo changes an id, one page object changes and every test that
  used it keeps working.
- **Explicit waits only.** No `implicitly_wait`, no `time.sleep`. Every
  interaction goes through `WebDriverWait(..., CONFIG.explicit_wait)`.
- **Fresh driver per test.** Function-scoped fixture. Tests never share
  state, which is what lets them run in any order (and later, in parallel).
- **Env-driven config.** Same suite runs headed on my laptop and headless
  in CI just by flipping `E2E_HEADLESS=true`. Credentials, base URL, and
  wait timeout are all overridable.
- **`data-test` selectors where SauceDemo provides them** (error banners).
  Stable across styling changes; `id` is fine for the buttons that have them.
- **Return-the-next-page pattern.** `login()` returns `InventoryPage`,
  `proceed_to_checkout()` returns `CheckoutStepOnePage`, etc. Tests chain
  actions instead of manually instantiating pages.
- **Screenshot on failure.** The pytest `pytest_runtest_makereport` hook
  stashes the driver on `item._driver` in the fixture, then reads it back
  when a test fails. Standard pytest recipe.

## Interview talking points

**"Walk me through the project."**
E2E test suite for saucedemo.com in Python, using Selenium and pytest with
the Page Object Model. Tests cover login (positive, locked user, bad
credentials) and the full checkout flow (parameterized across three cart
shapes), plus one big end-to-end journey in `test_portal_e2e.py` marked
`@pytest.mark.e2e`. Runs headed locally, headless in GitHub Actions.

**"Why POM?"**
Separates *what the user does* from *how the UI works*. Tests stay short
and readable, and when the DOM changes only the page object changes.

**"How do you handle waits?"**
Explicit only. Every helper in `BasePage` waits for the element to be
visible or clickable before acting. I don't use `implicitly_wait` because
it mixes badly with explicit waits and hides races. No `time.sleep`.

**"How do you handle test data?"**
Credentials and URL come from env vars via a frozen dataclass in
`utils/config.py`. The three checkout scenarios are inline in the test
file - small enough that JSON was overkill.

**"How do you keep tests non-flaky?"**
Fresh driver per test, explicit waits at every step, `math.isclose` for
float comparisons on totals, and a screenshot hook so I can see the DOM
state at the moment of failure. If a test does start flaking, the
screenshot usually tells me whether it's a race, a locator, or the app.

**"How do you scale this?"**
Tests are independent, so `pytest-xdist` gets you parallel runs.
The real limit is SauceDemo itself (single shared standard_user session),
so a bigger suite would need a pool of test users. For a real app I'd
also do API-level setup (create a logged-in session via API, then hand
the cookie to Selenium) to skip the login UI in every test.

**"What's in CI?"**
GitHub Actions, ubuntu-latest, Python 3.12, headless Chrome. Runs on
push and PR to `main`. Uploads the pytest HTML report as an artifact,
and failure screenshots as a separate artifact if anything failed.

**"What would you add next?"**
- `pytest-rerunfailures` for the known-flaky tests
- API-level auth setup to skip UI login in most tests
- Parallel runs with a user pool
- Visual regression on the key pages
