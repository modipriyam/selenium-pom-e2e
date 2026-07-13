# selenium-pom-e2e

End-to-end UI tests for [saucedemo.com](https://www.saucedemo.com) built with
Selenium, pytest, and the Page Object Model. The suite is designed to run
locally on a developer laptop and headlessly in CI.

## The unique feature under test

The primary scenario is the **full checkout funnel**:

1. Log in as `standard_user`
2. Add one-to-many products from the inventory page
3. Verify the cart badge counter and cart contents
4. Fill in customer information (step one)
5. Verify subtotal, tax, and total math on the overview page (step two)
6. Confirm the order-complete page

Three cart shapes exercise the flow through data-driven parameterization:
single item, multi-item, and a higher-value cart with mixed prices. Auxiliary
tests cover negative login paths, form validation on step one, and cart
badge updates when items are removed.

## Project layout

```
selenium-pom-e2e/
├── .github/workflows/e2e.yml    # CI pipeline (headless Chrome)
├── conftest.py                  # driver fixture + screenshot-on-failure hook
├── data/checkout_scenarios.json # parameterized test data
├── pages/                       # Page Object Model classes
│   ├── base_page.py             # shared Selenium primitives
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   ├── checkout_step_one_page.py
│   ├── checkout_step_two_page.py
│   └── checkout_complete_page.py
├── tests/
│   ├── test_checkout_flow.py    # the primary scenario
│   └── test_login.py
├── utils/
│   ├── config.py                # env-driven configuration
│   └── driver_factory.py        # Chrome/Firefox builders
├── pytest.ini
└── requirements.txt
```

Each page object exposes intent-level actions (`login`, `add_to_cart`,
`proceed_to_checkout`, `finish`), never raw locators, so tests read like a
user script and the DOM is free to change without rewriting tests.

## Getting started

Prerequisites: Python 3.10+ and a recent Chrome install (Selenium 4.6+ ships
Selenium Manager, so no manual chromedriver setup is required).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the whole suite (headed by default — you see the browser)
pytest

# Run headlessly instead
E2E_HEADLESS=true pytest

# Run only smoke tests
pytest -m smoke
```

Reports land in `reports/report.html`; failure screenshots (if any) are saved
under `screenshots/`.

## Configuration

Everything is overridable via environment variables — set them in your shell or
in the workflow to point at a different environment.

| Variable            | Default                    | Description                       |
| ------------------- | -------------------------- | --------------------------------- |
| `E2E_BASE_URL`      | `https://www.saucedemo.com`| Target application URL            |
| `E2E_BROWSER`       | `chrome`                   | `chrome` or `firefox`             |
| `E2E_HEADLESS`      | `false` (locally)          | Locally headed; CI sets `true`    |
| `E2E_EXPLICIT_WAIT` | `10`                       | Seconds for explicit waits        |
| `E2E_STANDARD_USER` | `standard_user`            | Login username                    |
| `E2E_PASSWORD`      | `secret_sauce`             | Login password                    |

## CI

`.github/workflows/e2e.yml` runs the suite on every push and pull request
targeting `main`, plus on manual dispatch:

- Ubuntu latest, Python 3.12, headless Chrome
- Publishes the pytest HTML report as an artifact (`e2e-report`)
- Publishes failure screenshots as an artifact (`e2e-screenshots`) on failed
  runs only

## Extending the suite

- Add a new page object under `pages/` inheriting from `BasePage`
- Add scenario data to `data/checkout_scenarios.json` or a sibling JSON file
- Mark tests with the pytest markers declared in `pytest.ini` (`smoke`,
  `checkout`, `login`, `regression`) so slices of the suite can be run
  independently
