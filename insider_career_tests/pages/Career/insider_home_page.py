from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from base.base_page import PageBase


class InsiderHomePage(PageBase):
    """Insider One main homepage — https://useinsider.com/"""

    # Navbar
    NAVBAR_COMPANY_ITEM = (By.XPATH, "//li[contains(@class,'nav-item')]//a[normalize-space()='Company']")
    WE_ARE_HIRING_LINK = (By.XPATH, "//a[normalize-space()=\"We're hiring!\"]")
    # Fallback: generic careers link when the dropdown label differs
    CAREERS_NAV_LINK = (By.XPATH, "//a[contains(@href,'/careers') and not(contains(@href,'open-position'))]")

    INSIDER_LOGO = (By.XPATH, "//img[contains(@alt,'Insider') or contains(@src,'insider')]")

    def __init__(self, driver):
        super().__init__(driver)
        self.check()

    def check(self):
        self.wait.until(
            ec.visibility_of_element_located(self.INSIDER_LOGO),
            "Insider homepage logo is not visible — page may not have loaded.",
        )

    def is_loaded(self):
        return "useinsider.com" in self.driver.current_url

    def click_we_are_hiring(self):
        """Hover over the Company nav item to expose the dropdown, then click 'We're hiring!'"""
        self.hover_over(self.NAVBAR_COMPANY_ITEM)
        self.click_element(self.WE_ARE_HIRING_LINK)
