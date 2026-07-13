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
    headless: bool = _get_bool("E2E_HEADLESS", True)
    implicit_wait: float = float(os.getenv("E2E_IMPLICIT_WAIT", "0"))
    explicit_wait: float = float(os.getenv("E2E_EXPLICIT_WAIT", "10"))
    window_width: int = int(os.getenv("E2E_WINDOW_WIDTH", "1440"))
    window_height: int = int(os.getenv("E2E_WINDOW_HEIGHT", "900"))

    standard_user: str = os.getenv("E2E_STANDARD_USER", "standard_user")
    locked_user: str = os.getenv("E2E_LOCKED_USER", "locked_out_user")
    problem_user: str = os.getenv("E2E_PROBLEM_USER", "problem_user")
    password: str = os.getenv("E2E_PASSWORD", "secret_sauce")


CONFIG = Config()
