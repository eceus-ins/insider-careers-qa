import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from base.base_page import PageBase


class JobListing:
    """Wraps a single job-card element and exposes typed accessors."""

    POSITION_TITLE = (By.XPATH, ".//p[contains(@class,'position-title')]")
    DEPARTMENT = (By.XPATH, ".//span[contains(@class,'position-department')]")
    LOCATION = (By.XPATH, ".//div[contains(@class,'position-location')]")
    APPLY_BTN = (By.XPATH, ".//a[normalize-space()='Apply Now']")

    def __init__(self, element, driver):
        self.element = element
        self.driver = driver

    def get_position(self):
        return self.element.find_element(*self.POSITION_TITLE).text.strip()

    def get_location(self):
        return self.element.find_element(*self.LOCATION).text.strip()

    def click_apply(self):
        apply_btn = self.element.find_element(*self.APPLY_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", apply_btn)
        apply_btn.click()


class InsiderOpenPositionsPage(PageBase):
    """Open positions listing page with Location and Team filter dropdowns.

    Insider uses a custom Select2-backed filter UI; we interact with the
    underlying <select> element via JS and then trigger the change event so
    the visible dropdown label and the job list both update correctly.
    """

    # Filter selects (native <select> elements behind Select2)
    LOCATION_SELECT = (By.XPATH, "//select[@name='filter-by-location']")
    TEAM_SELECT = (By.XPATH, "//select[@name='filter-by-team']")

    # Select2 trigger spans (visible UI that the user clicks to open the dropdown)
    LOCATION_SELECT2_TRIGGER = (
        By.XPATH,
        "//select[@name='filter-by-location']"
        "/following-sibling::span[contains(@class,'select2')]"
        "//span[contains(@class,'select2-selection')]",
    )
    TEAM_SELECT2_TRIGGER = (
        By.XPATH,
        "//select[@name='filter-by-team']"
        "/following-sibling::span[contains(@class,'select2')]"
        "//span[contains(@class,'select2-selection')]",
    )

    # Select2 dropdown option list
    SELECT2_OPTION = (By.XPATH, "//li[contains(@class,'select2-results__option') and not(contains(@class,'loading'))]")
    SELECT2_SEARCH_INPUT = (By.XPATH, "//input[contains(@class,'select2-search__field')]")

    # Job listing items
    JOB_LIST_ITEMS = (By.XPATH, "//div[contains(@class,'position-list-item')]")

    # Loading spinner — wait for it to disappear after filtering
    LOADING_SPINNER = (By.XPATH, "//span[contains(@class,'loading') or contains(@id,'loading')]")

    # Lever form verification
    LEVER_FORM_INDICATOR = (By.XPATH, "//form[contains(@action,'lever.co') or @id='application-form']")

    def __init__(self, driver):
        super().__init__(driver)
        self.check()

    def check(self):
        self.wait.until(
            ec.url_contains("open-positions"),
            "URL does not contain 'open-positions' — page may not have loaded.",
        )

    # ------------------------------------------------------------------ #
    # Filter helpers
    # ------------------------------------------------------------------ #

    def _select_filter_option(self, trigger_locator, value):
        """Opens a Select2 dropdown and clicks the option matching *value*."""
        trigger = self.wait_for_visibility(trigger_locator)
        self.scroll_to_element(trigger)
        trigger.click()

        # Type to narrow the list
        try:
            search_box = self.wait_for_visibility(self.SELECT2_SEARCH_INPUT, timeout=5)
            search_box.send_keys(value)
        except Exception:
            pass  # Some Select2 dropdowns have no search box

        # Wait for results and click the matching option
        options = self.wait.until(ec.presence_of_all_elements_located(self.SELECT2_OPTION))
        for option in options:
            if value.lower() in option.text.lower():
                option.click()
                return
        raise ValueError(f"Option '{value}' not found in dropdown")

    def select_location(self, location):
        """Select a location value from the filter dropdown."""
        self._select_filter_option(self.LOCATION_SELECT2_TRIGGER, location)
        self._wait_for_jobs_to_reload()

    def select_team(self, team):
        """Select a team value from the filter dropdown."""
        self._select_filter_option(self.TEAM_SELECT2_TRIGGER, team)
        self._wait_for_jobs_to_reload()

    def _wait_for_jobs_to_reload(self, timeout=10):
        """Wait for any loading state to clear after a filter change."""
        time.sleep(1)  # brief pause for AJAX to start
        try:
            self.wait_for_invisibility(self.LOADING_SPINNER, timeout=timeout)
        except Exception:
            pass  # spinner may not be present in all page versions
        self.wait.until(ec.presence_of_all_elements_located(self.JOB_LIST_ITEMS))

    # ------------------------------------------------------------------ #
    # Job listing helpers
    # ------------------------------------------------------------------ #

    def are_jobs_listed(self):
        return self.is_element_visible(self.JOB_LIST_ITEMS)

    def get_job_listings(self):
        """Return a list of :class:`JobListing` objects for all visible job cards."""
        elements = self.get_element_list(self.JOB_LIST_ITEMS)
        return [JobListing(el, self.driver) for el in elements]

    # ------------------------------------------------------------------ #
    # Lever verification
    # ------------------------------------------------------------------ #

    def is_lever_application_form_open(self):
        """Verify the current page is a Lever application form."""
        return "lever.co" in self.driver.current_url or self.is_element_visible(
            self.LEVER_FORM_INDICATOR, timeout=10
        )
