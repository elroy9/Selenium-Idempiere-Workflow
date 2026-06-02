from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WorkflowPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def search_menu(self, keyword):
        search_bar = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@class,'z-bandbox-input')]")
        ))
        search_bar.clear()
        search_bar.send_keys(keyword)
        time.sleep(2)  # Tunggu dropdown muncul dulu
        search_bar.send_keys(Keys.ENTER)
        print(f"✅ Search bar diisi dan Enter: {keyword}")

    def click_search_button(self):
        search_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Find24.png')]/ancestor::span[contains(@class,'z-toolbarbutton-content')]/..")
        ))
        search_btn.click()
        print("✅ Tombol Search (kaca pembesar) diklik")

    def fill_search_key(self, value):
        search_key = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@class='z-textbox' and @instancename='Value']")
        ))
        search_key.clear()
        search_key.send_keys(value)
        search_key.send_keys(Keys.ENTER)
        print(f"✅ Search Key diisi: {value}")