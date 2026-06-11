import os
import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


_CI = os.environ.get("CI", "false").lower() == "true"


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Browser to use for test execution: chrome or firefox"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=_CI,
        help="Run browser in headless mode (auto-enabled in CI)"
    )


@pytest.fixture(scope="function")
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
        else:
            options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        drv = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        drv = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options
        )
        if not headless:
            drv.maximize_window()
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    yield drv
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv:
            os.makedirs("screenshots", exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"screenshots/FAIL_{item.name}_{ts}.png"
            drv.save_screenshot(path)
            print(f"\nScreenshot saved: {path}")
