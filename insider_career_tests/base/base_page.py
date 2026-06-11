import os
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class PageBase:
    DEFAULT_TIMEOUT = 15

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)
        self.actions = ActionChains(driver)

    def check(self):
        pass

    def get_element(self, locator, timeout=None):
        _wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        return _wait.until(ec.presence_of_element_located(locator))

    def get_element_list(self, locator, timeout=None):
        _wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        _wait.until(ec.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def click_element(self, locator, timeout=None):
        _wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        element = _wait.until(ec.element_to_be_clickable(locator))
        element.click()
        return element

    def wait_for_visibility(self, locator, timeout=None, message=""):
        _wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        return _wait.until(ec.visibility_of_element_located(locator), message)

    def wait_for_invisibility(self, locator, timeout=None):
        _wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        return _wait.until(ec.invisibility_of_element_located(locator))

    def hover_over(self, locator):
        element = self.wait_for_visibility(locator)
        self.actions.move_to_element(element).perform()
        return element

    def scroll_to_element(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element
        )

    def scroll_to_and_get(self, locator, timeout=None):
        element = self.get_element(locator, timeout)
        self.scroll_to_element(element)
        return element

    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def is_element_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                ec.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def switch_to_new_tab(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def take_screenshot(self, name="screenshot"):
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(screenshots_dir, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        return path
