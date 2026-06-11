import logging
import unittest

from base.decorators import (  # noqa: F401 — re-exported via "from base.base_test import *"
    Owner, Priority, ProductTeam, decorator_loader, error_logger, CaseId,
)


class BaseTest(unittest.TestCase):
    """Base class for all test cases.

    The WebDriver instance (self.driver) is injected by the conftest
    browser_driver fixture before setUp() is called, so setUp() in subclasses
    should only contain test-specific data setup — never driver creation.
    """

    driver = None
    browser = "chrome"

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        cls.logger = logging.getLogger(cls.__name__)

    def navigate_url(self, url):
        self.driver.get(url)
        self.logger.info(f"Navigated to: {url}")

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
