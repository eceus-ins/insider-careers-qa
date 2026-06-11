import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

_CI = os.environ.get("CI", "false").lower() == "true"


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser to run tests with: chrome or firefox. Omit to run both.",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=_CI,
        help="Run browser in headless mode (auto-enabled in CI)",
    )


def _create_driver(browser_name, headless=False):
    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
        else:
            options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        return webdriver.Chrome(options=options)
    if browser_name == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        driver = webdriver.Firefox(options=options)
        if not headless:
            driver.maximize_window()
        return driver
    raise ValueError(f"Unsupported browser: {browser_name}")


@pytest.fixture(autouse=True, params=["chrome", "firefox"])
def browser_driver(request):
    """Creates the WebDriver and injects it into the test instance before setUp runs.

    Parametrised over chrome/firefox; pass --browser=<name> to run only one.
    """
    selected = request.config.getoption("--browser")
    if selected and request.param != selected.lower():
        pytest.skip(f"Skipping '{request.param}' — running only '{selected}'")

    headless = request.config.getoption("--headless")
    driver = _create_driver(request.param, headless=headless)

    if request.instance is not None:
        request.instance.driver = driver
        request.instance.browser = request.param

    yield driver

    # Safety cleanup in case test tearDown did not call quit_driver()
    try:
        driver.quit()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    """Captures a screenshot when a test fails, before the driver is quit."""
    yield
    failed = any(
        getattr(request.node, f"rep_{when}", None) and
        getattr(request.node, f"rep_{when}").failed
        for when in ("setup", "call")
    )
    if not failed:
        return
    instance = request.instance
    if instance is None or not getattr(instance, "driver", None):
        return
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    browser_name = getattr(instance, "browser", "unknown")
    safe_name = request.node.name.replace("/", "_").replace(":", "_")
    path = os.path.join(screenshots_dir, f"FAIL_{safe_name}_{browser_name}_{timestamp}.png")
    try:
        instance.driver.save_screenshot(path)
        print(f"\nScreenshot saved: {path}")
    except Exception as exc:
        print(f"\nCould not save screenshot: {exc}")
