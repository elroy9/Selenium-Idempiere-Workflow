from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WorkflowPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def search_menu(self, keyword):
        """Cari menu via search bar di atas, tekan Enter untuk buka halaman."""
        search_bar = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[contains(@class,'z-bandbox-input')]")
        ))
        search_bar.clear()
        search_bar.send_keys(keyword)
        time.sleep(2)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(3)  # Tunggu halaman Workflow load
        print(f"✅ Search bar diisi dan Enter: {keyword}")

    def click_search_button(self):
        """
        Buka dialog pencarian record via Alt+F (Lookup Record).
        Lebih reliable daripada klik Find24.png yang bisa tidak terlihat
        saat halaman masih loading atau posisi tab berubah.
        """
        body = self.wait.until(EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        ))
        body.send_keys(Keys.ALT + 'f')
        time.sleep(2)  # Tunggu dialog search muncul
        print("✅ Lookup Record dibuka (Alt+F)")

    def fill_search_key(self, value):
        """Isi field search di dialog yang terbuka, tekan Enter."""
        search_key = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@class='z-textbox' and @instancename='Value']")
        ))
        search_key.clear()
        search_key.send_keys(value)
        search_key.send_keys(Keys.ENTER)
        print(f"✅ Search Key diisi: {value}")