"""Runtime configuration sourced from environment variables with sane defaults.

Anything under the E2E_* prefix is user-overridable at run time or in CI, keeping
credentials and toggles out of test code.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    base_url: str = os.getenv("E2E_BASE_URL", "https://www.saucedemo.com")
    browser: str = os.getenv("E2E_BROWSER", "chrome").lower()
    # Headed by default so a developer sees the browser locally; CI overrides
    # this to `true` via the GitHub Actions workflow env.
    headless: bool = _get_bool("E2E_HEADLESS", False)
    implicit_wait: float = float(os.getenv("E2E_IMPLICIT_WAIT", "0"))
    explicit_wait: float = float(os.getenv("E2E_EXPLICIT_WAIT", "10"))
    # Optional pacing delay (seconds) inserted between demo steps.
    # 0 means no pause — safe for CI. Set e.g. 1.0 to slow a headed demo down.
    step_delay: float = float(os.getenv("E2E_STEP_DELAY", "0"))
    window_width: int = int(os.getenv("E2E_WINDOW_WIDTH", "1440"))
    window_height: int = int(os.getenv("E2E_WINDOW_HEIGHT", "900"))

    standard_user: str = os.getenv("E2E_STANDARD_USER", "standard_user")
    locked_user: str = os.getenv("E2E_LOCKED_USER", "locked_out_user")
    problem_user: str = os.getenv("E2E_PROBLEM_USER", "problem_user")
    password: str = os.getenv("E2E_PASSWORD", "secret_sauce")


CONFIG = Config()
