from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage

_QA_CARD_ANY = (By.XPATH, "//div[@data-department='Quality Assurance']//a")


class OpenPositionsPage(BasePage):
    # Lever jobs board locators
    _JOB_ITEMS = (By.CSS_SELECTOR, ".posting")
    _JOB_TITLE = (By.CSS_SELECTOR, ".posting-title h5")
    _JOB_LOCATION = (By.CSS_SELECTOR, ".sort-by-location")
    _JOB_APPLY_BTN = (By.CSS_SELECTOR, "a.posting-btn-submit")

    def click_quality_assurance_positions(self):
        # JS updates the href from '#' to a lever.co URL; poll until that happens
        card = WebDriverWait(self.driver, 40).until(
            lambda d: next(
                (el for el in d.find_elements(*_QA_CARD_ANY)
                 if "lever.co" in (el.get_attribute("href") or "")),
                None
            ),
            "Quality Assurance card href was not updated to lever.co within timeout"
        )
        self.scroll_to(card)
        self.js_click(card)

    def wait_for_jobs_to_load(self):
        return self.find_all_visible(self._JOB_ITEMS)

    def get_all_jobs(self):
        return self.driver.find_elements(*self._JOB_ITEMS)

    def get_job_title(self, job_element) -> str:
        titles = job_element.find_elements(*self._JOB_TITLE)
        return titles[0].text.strip() if titles else ""

    def get_job_location(self, job_element) -> str:
        locs = job_element.find_elements(*self._JOB_LOCATION)
        return locs[0].text.strip() if locs else ""

    def get_istanbul_jobs(self, jobs):
        return [j for j in jobs if "ISTANBUL" in self.get_job_location(j).upper()]

    def click_apply_on_first_istanbul_job(self, istanbul_jobs):
        job = istanbul_jobs[0]
        apply_btn = job.find_element(*self._JOB_APPLY_BTN)
        self.scroll_to(apply_btn)
        apply_btn.click()

    def switch_to_new_tab(self):
        try:
            WebDriverWait(self.driver, 5).until(lambda d: len(d.window_handles) > 1)
            self.driver.switch_to.window(self.driver.window_handles[-1])
        except Exception:
            pass
