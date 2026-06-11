from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CareersPage(BasePage):

    # "Explore open roles" CTA button on the careers landing page
    _EXPLORE_ROLES_BTN = (By.XPATH,
        "//a[contains(normalize-space(), 'Explore open roles') or "
        "contains(normalize-space(), 'Explore Open Roles') or "
        "contains(normalize-space(), 'See All Open Positions')]"
    )

    def is_careers_page(self):
        self.wait_url_contains("careers")
        return "careers" in self.current_url

    def is_explore_roles_button_visible(self):
        return self.is_visible(self._EXPLORE_ROLES_BTN)

    def click_explore_open_roles(self):
        from pages.open_positions_page import OpenPositionsPage
        self.click(self._EXPLORE_ROLES_BTN)
        return OpenPositionsPage(self.driver)
