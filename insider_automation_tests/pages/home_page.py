from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://insiderone.com/"

    # "We're hiring" link — now lives in the footer (site rebranded, Company nav removed)
    _WE_ARE_HIRING = (By.XPATH, "//a[@href='/careers/' and contains(normalize-space(), \"We're hiring\")]")

    def open_homepage(self):
        self.open(self.URL)
        self.accept_cookies_if_present()
        return self

    def is_homepage_loaded(self):
        return "Insider" in self.title

    def click_we_are_hiring(self):
        from pages.careers_page import CareersPage
        element = self.find_clickable(self._WE_ARE_HIRING)
        self.scroll_to(element)
        self.js_click(element)
        return CareersPage(self.driver)
