import os
from playwright.sync_api import Playwright, BrowserType
from pytest import fixture

# Playwright configuration for Django E2E tests
@fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments"""
    return {
        **browser_type_launch_args,
        "headless": os.getenv("HEADLESS", "true").lower() == "true",
        "slow_mo": int(os.getenv("SLOW_MO", "0")),
    }

@fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context arguments"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }

# Base URL for the Django development server
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")