import os
import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

_CI = os.environ.get("CI", "false").lower() == "true"


def _get_chrome_service():
    """Use webdriver-manager locally; let Selenium Manager handle CI."""
    if _CI:
        return None  # Selenium 4.x built-in Selenium Manager auto-downloads driver
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeService(ChromeDriverManager().install())
    except Exception:
        return None


def _get_firefox_service():
    if _CI:
        return None
    try:
        from webdriver_manager.firefox import GeckoDriverManager
        return FirefoxService(GeckoDriverManager().install())
    except Exception:
        return None


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
        service = _get_chrome_service()
        drv = webdriver.Chrome(service=service, options=options) if service else webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        service = _get_firefox_service()
        drv = webdriver.Firefox(service=service, options=options) if service else webdriver.Firefox(options=options)
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


# ─── DB Raporlama ────────────────────────────────────────────────────────────
import getpass
import subprocess

import pymysql

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3307)),
    "user":     os.getenv("DB_USER", "test_user"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "test_results_db"),
    "charset":  "utf8mb4",
}

_build_id = None
_session_started_at = None


def _get_connection():
    return pymysql.connect(**DB_CONFIG)


def _current_branch():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def pytest_sessionstart(session):
    global _build_id, _session_started_at
    _session_started_at = datetime.datetime.now()

    job_name     = os.getenv("JOB_NAME", "local-run")
    build_number = int(os.getenv("BUILD_NUMBER", 0))
    branch       = os.getenv("BRANCH_NAME") or _current_branch()
    triggered_by = os.getenv("BUILD_USER") or getpass.getuser()

    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO build_runs (job_name, build_number, branch, started_at, status, triggered_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (job_name, build_number, branch, _session_started_at, "running", triggered_by))
            conn.commit()
            _build_id = cursor.lastrowid
        finally:
            conn.close()
    except Exception as e:
        print(f"\n[DB] Bağlantı kurulamadı, DB raporlama devre dışı: {e}")


def pytest_runtest_logreport(report):
    if report.when != "call" or _build_id is None:
        return

    if report.skipped:
        status = "skip"
    elif report.passed:
        status = "pass"
    else:
        status = "fail"

    nodeid = report.nodeid
    error_message = str(report.longrepr)[:500] if report.failed else None

    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO test_runs
                        (build_id, suite_name, test_name, status, duration_ms, run_at, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    _build_id,
                    nodeid.split("::")[0],
                    nodeid.split("::")[-1],
                    status,
                    int(report.duration * 1000),
                    datetime.datetime.now(),
                    error_message,
                ))
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"\n[DB] Test sonucu yazılamadı: {e}")


def pytest_sessionfinish(session, exitstatus):
    if _build_id is None:
        return

    duration_ms = int((datetime.datetime.now() - _session_started_at).total_seconds() * 1000)

    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE build_runs SET status = %s, duration_ms = %s WHERE id = %s",
                    ("success" if exitstatus == 0 else "failure", duration_ms, _build_id)
                )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"\n[DB] Build durumu güncellenemedi: {e}")
