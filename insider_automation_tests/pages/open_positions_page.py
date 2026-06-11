from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class OpenPositionsPage(BasePage):

    # "X Open Positions" link inside the Software Development department block
    _SOFTWARE_DEV_POSITIONS_LINK = (By.XPATH,
        "//h3[contains(normalize-space(),'Software Development')]"
        "/following-sibling::a[contains(normalize-space(),'Open Position')] | "
        "//div[.//h3[contains(normalize-space(),'Software Development')]]"
        "//a[contains(normalize-space(),'Open Position')]"
    )

    # Select2 filter containers (span wrapping the visible selected value)
    _LOCATION_FILTER = (By.XPATH, "//span[@id='select2-filter-by-location-container']")
    _TEAM_FILTER = (By.XPATH, "//span[@id='select2-filter-by-department-container']")

    # Search field that appears after a Select2 dropdown is opened
    _SELECT2_SEARCH = (By.CSS_SELECTOR, ".select2-search__field")

    # Job listing cards and their inner fields
    _JOB_ITEMS = (By.CSS_SELECTOR, "#jobs-list .position-list-item")
    _JOB_TITLE = (By.CSS_SELECTOR, "p.position-title")
    _JOB_DEPARTMENT = (By.CSS_SELECTOR, "span.position-department")
    _JOB_LOCATION = (By.CSS_SELECTOR, "span.position-location")
    _JOB_APPLY_BTN = (By.CSS_SELECTOR, "a.btn-navy")

    def click_software_development_positions(self):
        element = self.find_clickable(self._SOFTWARE_DEV_POSITIONS_LINK)
        self.scroll_to(element)
        element.click()

    def _select_from_dropdown(self, container_locator, option_text):
        self.find_clickable(container_locator).click()
        search_input = self.find_clickable(self._SELECT2_SEARCH)
        search_input.send_keys(option_text)
        option = self.find_clickable((By.XPATH,
            f"//li[contains(@class,'select2-results__option')"
            f" and contains(normalize-space(),'{option_text}')]"
        ))
        option.click()

    def select_location(self, location: str):
        self._select_from_dropdown(self._LOCATION_FILTER, location)

    def select_team(self, team: str):
        self._select_from_dropdown(self._TEAM_FILTER, team)

    def wait_for_jobs_to_load(self):
        return self.find_all_visible(self._JOB_ITEMS)

    def get_all_jobs(self):
        return self.driver.find_elements(*self._JOB_ITEMS)

    def get_job_title(self, job_element) -> str:
        return job_element.find_element(*self._JOB_TITLE).text.strip()

    def get_job_department(self, job_element) -> str:
        return job_element.find_element(*self._JOB_DEPARTMENT).text.strip()

    def get_job_location(self, job_element) -> str:
        return job_element.find_element(*self._JOB_LOCATION).text.strip()

    def click_apply_on_first_job(self):
        jobs = self.get_all_jobs()
        apply_btn = jobs[0].find_element(*self._JOB_APPLY_BTN)
        self.scroll_to(apply_btn)
        apply_btn.click()
