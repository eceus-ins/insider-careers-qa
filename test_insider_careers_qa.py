import pytest
import unittest
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# ─── Driver Factory ───────────────────────────────────────────────────────────────


def create_driver(browser):
    if browser.lower() == "chrome":
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        return webdriver.Chrome(options=opts)
    if browser.lower() == "firefox":
        opts = FirefoxOptions()
        opts.add_argument("--width=1920")
        opts.add_argument("--height=1080")
        return webdriver.Firefox(options=opts)
    raise ValueError(f"Unsupported browser: {browser}")


# ─── Base Page ────────────────────────────────────────────────────────────────────


class BasePage:
    TIMEOUT = 15

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    def js_click(self, locator):
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
        self.driver.execute_script("arguments[0].click()", el)

    def find_all(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def is_visible(self, locator):
        try:
            return self.wait.until(
                EC.visibility_of_element_located(locator)
            ).is_displayed()
        except Exception:
            return False


# ─── Page Objects ─────────────────────────────────────────────────────────────────


class InsiderHomePage(BasePage):
    URL = "https://useinsider.com/"
    COOKIE_ACCEPT = (By.ID, "wt-cli-accept-all-btn")
    WE_ARE_HIRING = (By.XPATH, '//a[normalize-space()="We\'re hiring"]')

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self._accept_cookies()
        return self

    def _accept_cookies(self):
        try:
            btn = WebDriverWait(self.driver, 6).until(
                EC.element_to_be_clickable(self.COOKIE_ACCEPT)
            )
            btn.click()
            time.sleep(0.5)
        except Exception:
            pass

    def is_home_page(self):
        url = self.driver.current_url
        return "useinsider.com" in url or "insiderone.com" in url

    def click_we_are_hiring(self):
        self.js_click(self.WE_ARE_HIRING)
        return CareersPage(self.driver)


class CareersPage(BasePage):
    EXPLORE_OPEN_ROLES = (
        By.XPATH,
        "//a[contains(normalize-space(),'Explore open roles')]",
    )

    def is_careers_page(self):
        return "career" in self.driver.current_url.lower()

    def is_explore_open_roles_visible(self):
        return self.is_visible(self.EXPLORE_OPEN_ROLES)

    def click_explore_open_roles(self):
        self.js_click(self.EXPLORE_OPEN_ROLES)
        time.sleep(1)
        return OpenPositionsPage(self.driver)


class OpenPositionsPage(BasePage):
    # Careers page #open-roles section — Software Development card button
    SOFTWARE_DEV_BTN = (
        By.XPATH,
        "//h3[contains(text(),'Software Development')]"
        "/../..//a[contains(@class,'insiderone-icon-cards-grid-item-btn')]",
    )

    def click_software_development_positions(self):
        el = self.wait.until(EC.presence_of_element_located(self.SOFTWARE_DEV_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
        time.sleep(0.5)
        href = el.get_attribute("href")
        self.driver.get(href)
        self.wait.until(lambda d: "lever.co" in d.current_url)
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return JobListingsPage(self.driver)


class JobListingsPage(BasePage):
    # Lever job listing page
    # Filter buttons order: [0]=Location Type, [1]=Location, [2]=Team, [3]=Work Type
    FILTER_BUTTONS = (By.CSS_SELECTOR, ".filter-button")
    JOB_ITEMS = (By.CSS_SELECTOR, ".posting")
    JOB_TITLE = (By.CSS_SELECTOR, "h5[data-qa='posting-name']")
    JOB_LOCATION = (By.CSS_SELECTOR, ".sort-by-location")
    APPLY_BTN = (By.CSS_SELECTOR, "a.posting-btn-submit")

    def _pick_option(self, btn_index, value):
        btns = self.wait.until(EC.presence_of_all_elements_located(self.FILTER_BUTTONS))
        btns[btn_index].click()
        time.sleep(0.5)
        option_xpath = (
            f"//div[contains(@class,'filter-popup') and contains(@style,'display: block')]"
            f"//a[normalize-space()='{value}']"
        )
        self.wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath))).click()
        time.sleep(2)
        return self

    def filter_by_location(self, location):
        return self._pick_option(1, location)

    def filter_by_team(self, team):
        # After location selection, page reloads — team button index is still 2
        return self._pick_option(2, team)

    def has_listings(self):
        try:
            return len(self.find_all(self.JOB_ITEMS)) > 0
        except Exception:
            return False

    def get_all_titles(self):
        return [
            el.find_element(*self.JOB_TITLE).text
            for el in self.find_all(self.JOB_ITEMS)
        ]

    def get_all_locations(self):
        return [
            el.find_element(*self.JOB_LOCATION).text
            for el in self.find_all(self.JOB_ITEMS)
        ]

    def click_first_apply(self):
        first_item = self.find_all(self.JOB_ITEMS)[0]
        apply_btn = first_item.find_element(*self.APPLY_BTN)
        self.driver.execute_script("arguments[0].click()", apply_btn)
        return ApplicationFormPage(self.driver)


class ApplicationFormPage(BasePage):
    def is_lever_form(self):
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
        return "lever.co" in self.driver.current_url


# ─── Base Test ────────────────────────────────────────────────────────────────────


class BaseTest(unittest.TestCase):
    browser = "chrome"

    def setUp(self):
        self.driver = create_driver(self.browser)
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s"
        )

    def wait_for(self, seconds):
        time.sleep(seconds)

    def take_screenshot(self, label="failure"):
        os.makedirs("screenshots", exist_ok=True)
        path = f"screenshots/{label}_{int(time.time())}.png"
        self.driver.save_screenshot(path)
        self.logger.info(f"Screenshot saved -> {path}")

    def tearDown(self):
        self.driver.quit()


# ─── Test ─────────────────────────────────────────────────────────────────────────


class _TestInsiderCareersQAIstanbul(BaseTest):
    __test__ = False
    """
    1. Visit https://useinsider.com/ and verify the home page.
    2. Click "We're hiring" -> verify Careers page and "Explore open roles" button.
    3. Click "Explore open roles" -> click Software Development "xx Open Positions".
    4. Filter Location=Istanbul, Turkiye and Team=Quality Assurance -> verify listings shown.
    5. Verify every listing title contains "Quality Assurance" and location contains "Istanbul".
    6. Click Apply on first listing -> verify redirect to Lever Application Form.
    """

    def test_qa_istanbul_job_listings_and_apply(self):
        try:
            self.logger.info("1. Open Insider home page and verify")
            home_page = InsiderHomePage(self.driver)
            home_page.open()
            self.assertTrue(
                home_page.is_home_page(),
                f"Expected Insider home page but got URL: {self.driver.current_url}",
            )
            self.logger.info("Home page verified successfully!")

            self.logger.info(
                "2. Click 'We're hiring' -> verify Careers page and Explore open roles button"
            )
            careers_page = home_page.click_we_are_hiring()
            self.wait_for(1)
            self.assertTrue(
                careers_page.is_careers_page(),
                f"Expected Careers page but got URL: {self.driver.current_url}",
            )
            self.assertTrue(
                careers_page.is_explore_open_roles_visible(),
                "'Explore open roles' button is not visible on the Careers page.",
            )
            self.logger.info(
                "Careers page verified and 'Explore open roles' button found!"
            )

            self.logger.info(
                "3. Click 'Explore open roles' -> click Software Development Open Positions"
            )
            open_positions_page = careers_page.click_explore_open_roles()
            self.wait_for(1)
            job_listings_page = (
                open_positions_page.click_software_development_positions()
            )
            self.wait_for(2)
            self.logger.info(f"Lever jobs page opened: {self.driver.current_url}")

            self.logger.info(
                "4. Filter by Location=Istanbul then Team=Quality Assurance"
            )
            job_listings_page.filter_by_location("Istanbul")
            self.logger.info("Location filter set to: Istanbul")
            job_listings_page.filter_by_team("Quality Assurance")
            self.logger.info("Team filter set to: Quality Assurance")
            self.assertTrue(
                job_listings_page.has_listings(),
                "No job listings found after applying Location and Team filters.",
            )
            self.logger.info("Job listings are displayed after filtering!")

            self.logger.info("5. Verify title and location for every listed position")
            for title in job_listings_page.get_all_titles():
                self.assertTrue(
                    "Quality Assurance" in title or "QA" in title,
                    f"Title '{title}' does not contain 'Quality Assurance' or 'QA'.",
                )
            for loc in job_listings_page.get_all_locations():
                self.assertIn(
                    "Istanbul".upper(),
                    loc.upper(),
                    f"Location '{loc}' does not contain 'Istanbul'.",
                )
            self.logger.info("All listings verified: titles and locations match!")

            self.logger.info(
                "6. Click Apply on first listing -> verify Lever Application Form"
            )
            application_page = job_listings_page.click_first_apply()
            self.wait_for(2)
            self.assertTrue(
                application_page.is_lever_form(),
                f"Expected Lever application form but got URL: {self.driver.current_url}",
            )
            self.logger.info("Lever Application Form page verified successfully!")

        except Exception:
            self.take_screenshot(f"{self.__class__.__name__}_failure")
            raise


class TestInsiderCareersQAIstanbulChrome(_TestInsiderCareersQAIstanbul):
    __test__ = True
    browser = "chrome"
