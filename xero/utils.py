import base64
import json
from typing import List

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


# define a retry function for easy retries
def retry(f: callable, n: int, *args, **kwargs):
    assert n > 1, "Just call the function directly!"
    for _ in range(n-1):
        try:
            f(*args, **kwargs)
            return
        except:
            print("Failed once ... retrying")
    f(*args, **kwargs)


def encode_credentials(email: str, password: str) -> str:
    json_creds = json.dumps({'XERO_EMAIL': email, 'XERO_PASSWORD': password})
    return base64.b64encode(bytes(json_creds, "utf-8")).decode()


def decode_credentials(credentials: str) -> dict:
    return json.loads(base64.b64decode(credentials).decode())


class DriverExtender:
    def __init__(self, driver: WebDriver):
        self.driver = driver


class Waiter(DriverExtender):

    def ec(self, ec, timeout=5, poll_frequency=0.1) -> WebElement:
        return WebDriverWait(self.driver, timeout, poll_frequency).until(ec)

    def present(self, loc: tuple, *args, **kwargs) -> WebElement:
        return self.ec(EC.presence_of_element_located(loc), *args, **kwargs)

    def clickable(self, loc: tuple, *args, **kwargs) -> WebElement:
        return self.ec(EC.element_to_be_clickable(loc), *args, **kwargs)

    def xpath_present(self, xp: str, *args, **kwargs) -> WebElement:
        return self.present((By.XPATH, xp), *args, **kwargs)

    def xpath_clickable(self, xp: str, *args, **kwargs) -> WebElement:
        return self.clickable((By.XPATH, xp), *args, **kwargs)

    def automation_id_clickable(self, id: str, *args, **kwargs) -> WebElement:
        return self.clickable((By.CSS_SELECTOR, f'[data-automationid="{id}"]'), *args, **kwargs)

    def data_name_clickable(self, name: str, *args, **kwargs) -> WebElement:
        return self.clickable((By.CSS_SELECTOR, f'[data-name="{name}"]'), *args, **kwargs)

    def url_contains(self, part, *args, **kwargs):
        return self.ec(EC.url_contains(part), *args, **kwargs)


class Finder(DriverExtender):
    def one(self, by, value, *args, **kwargs) -> WebElement:
        return self.driver.find_element(by, value, *args, **kwargs)

    def all(self, by, value, *args, **kwargs) -> List[WebElement]:
        return self.driver.find_elements(by, value, *args, **kwargs)

    def id(self, id, *args, **kwargs) -> WebElement:
        return self.one(By.ID, id, *args, **kwargs)

    def all_id(self, id, *args, **kwargs) -> List[WebElement]:
        return self.all(By.ID, id, *args, **kwargs)

    def one_xpath(self, xp, *args, **kwargs) -> WebElement:
        return self.one(By.XPATH, xp, *args, **kwargs)

    def all_xpath(self, xp, *args, **kwargs) -> List[WebElement]:
        return self.all(By.XPATH, xp, *args, **kwargs)

    def automation_id(self, id: str, *args, **kwargs) -> WebElement:
        css_aid = f'[data-automationid="{id}"]'
        return self.one(By.CSS_SELECTOR, css_aid, *args, **kwargs)

    def all_automation_id(self, id: str, *args, **kwargs) -> List[WebElement]:
        css_aid = f'[data-automationid="{id}"]'
        return self.all(By.CSS_SELECTOR, css_aid, *args, **kwargs)

    def data_name(self, name: str, *args, **kwargs) -> WebElement:
        css_nme = f'[data-name="{name}"]'
        return self.one(By.CSS_SELECTOR, css_nme, *args, **kwargs)
