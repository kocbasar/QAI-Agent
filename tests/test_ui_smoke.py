import pytest

from app.core.config import get_settings


def test_test_environment_homepage_is_available():
    """Check that the configured test environment can be opened."""

    settings = get_settings()

    if not settings.ui_test_base_url:
        pytest.skip("UI_TEST_BASE_URL is not configured")

    playwright = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright is not installed",
    )

    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()

        try:
            page = browser.new_page()
            response = page.goto(
                settings.ui_test_base_url,
                wait_until="domcontentloaded",
            )

            assert response is not None
            assert response.status < 400
        finally:
            browser.close()
