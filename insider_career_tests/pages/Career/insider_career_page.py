from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from base.base_page import PageBase


class InsiderCareerPage(PageBase):
    """Insider careers landing page — https://useinsider.com/careers/"""

    PAGE_HEADING = (By.XPATH, "//h1[contains(text(),'Career') or contains(text(),'career')]")
    EXPLORE_OPEN_ROLES_BTN = (By.XPATH, "//a[contains(normalize-space(),'Explore open roles') or contains(normalize-space(),'Find your dream job')]")

    # "Software Development" department block and its "Open Positions" link.
    # The block uses a data-team or similar attribute; we locate by visible text.
    SW_DEV_SECTION = (By.XPATH, "//h3[contains(normalize-space(),'Software Development')]")
    SW_DEV_OPEN_POSITIONS_LINK = (
        By.XPATH,
        "//h3[contains(normalize-space(),'Software Development')]"
        "/following-sibling::*//a[contains(normalize-space(),'Open Positions')]"
        " | "
        "//div[contains(normalize-space(),'Software Development')]"
        "//a[contains(normalize-space(),'Open Positions')]",
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.check()

    def check(self):
        self.wait.until(
            ec.url_contains("careers"),
            "URL does not contain 'careers' — Career page may not have loaded.",
        )

    def is_loaded(self):
        return "careers" in self.driver.current_url

    def is_explore_open_roles_visible(self):
        return self.is_element_visible(self.EXPLORE_OPEN_ROLES_BTN)

    def click_explore_open_roles(self):
        button = self.wait_for_visibility(self.EXPLORE_OPEN_ROLES_BTN)
        self.scroll_to_element(button)
        self.click_element(self.EXPLORE_OPEN_ROLES_BTN)

    def click_software_development_open_positions(self):
        """Scroll to the Software Development block and click its 'Open Positions' link."""
        section = self.wait_for_visibility(self.SW_DEV_SECTION)
        self.scroll_to_element(section)
        self.click_element(self.SW_DEV_OPEN_POSITIONS_LINK)
