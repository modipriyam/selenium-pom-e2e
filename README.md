# selenium-pom-e2e

Selenium + pytest UI tests for [saucedemo.com](https://www.saucedemo.com),
using the Page Object Model.

## Layout

- `pages/` - Page Object classes
- `tests/` - login + full-checkout E2E tests
- `utils/config.py` - env-driven config
- `conftest.py` - driver fixture + screenshot-on-failure hook

## Run

Needs Python 3.10+ and Chrome (Selenium 4.6+ handles chromedriver for you).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest                     # headed
E2E_HEADLESS=true pytest   # headless
```

HTML report at `reports/report.html`, failure screenshots under `screenshots/`.

## Env vars

- `E2E_BASE_URL` (default `https://www.saucedemo.com`)
- `E2E_HEADLESS` (default `false`; CI sets `true`)
- `E2E_EXPLICIT_WAIT` (default `10`)
- `E2E_STANDARD_USER` / `E2E_PASSWORD` / `E2E_LOCKED_USER`

## CI

`.github/workflows/e2e.yml` runs the suite on push / PR to `main` with
headless Chrome and uploads the HTML report + failure screenshots.
