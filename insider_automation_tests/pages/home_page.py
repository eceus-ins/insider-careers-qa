from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://useinsider.com/"

    # Main navigation "Company" dropdown trigger
    _COMPANY_NAV = (By.XPATH, "//nav//li/a[normalize-space()='Company']")

    # "We're hiring!" link inside the Company dropdown
    _WE_ARE_HIRING = (By.XPATH, "//a[contains(normalize-space(), \"We're hiring\")]")

    def open_homepage(self):
        self.open(self.URL)
        self.accept_cookies_if_present()
        return self

    def is_homepage_loaded(self):
        return "Insider" in self.title

    def click_we_are_hiring(self):
        from pages.careers_page import CareersPage
        self.hover(self._COMPANY_NAV)
        self.find_visible(self._WE_ARE_HIRING)
        self.click(self._WE_ARE_HIRING)
        return CareersPage(self.driver)
