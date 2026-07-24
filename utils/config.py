import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    base_url: str = os.getenv("E2E_BASE_URL", "https://www.saucedemo.com")
    headless: bool = os.getenv("E2E_HEADLESS", "").lower() == "true"
    explicit_wait: float = float(os.getenv("E2E_EXPLICIT_WAIT", "10"))

    standard_user: str = os.getenv("E2E_STANDARD_USER", "standard_user")
    locked_user: str = os.getenv("E2E_LOCKED_USER", "locked_out_user")
    password: str = os.getenv("E2E_PASSWORD", "secret_sauce")


CONFIG = Config()
