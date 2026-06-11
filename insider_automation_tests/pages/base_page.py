from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


class BasePage:
    TIMEOUT = 20

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    def open(self, url):
        self.driver.get(url)

    @property
    def current_url(self):
        return self.driver.current_url

    @property
    def title(self):
        return self.driver.title

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def find_all_visible(self, locator):
        self.wait.until(EC.visibility_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.find_clickable(locator).click()

    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def hover(self, locator):
        element = self.find(locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def scroll_to(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def wait_url_contains(self, fragment, timeout=20):
        WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))

    def is_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def switch_to_new_tab(self):
        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def accept_cookies_if_present(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "wt-cli-accept-all-btn"))
            )
            btn.click()
        except Exception:
            pass
