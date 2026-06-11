from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from base.base_page import PageBase


class InsiderHomePage(PageBase):
    """Insider One main homepage — https://useinsider.com/"""

    # "We're hiring" link — now lives in the footer (site rebranded to insiderone.com, Company nav removed)
    WE_ARE_HIRING_LINK = (By.XPATH, "//a[@href='/careers/' and contains(normalize-space(), \"We're hiring\")]")

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
        return "insiderone.com" in self.driver.current_url or "useinsider.com" in self.driver.current_url

    def click_we_are_hiring(self):
        """Scroll to footer and click 'We're hiring' link (Company nav was removed in site rebrand)."""
        element = self.scroll_to_and_get(self.WE_ARE_HIRING_LINK)
        element.click()
