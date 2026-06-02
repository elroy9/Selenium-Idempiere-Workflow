from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://10.1.3.152:9292/webui/index.zul"

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(BASE_URL)
        print(f"✅ Membuka halaman: {BASE_URL}")

    def input_username(self, username):
        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='text' and contains(@class,'z-textbox')]")
        ))
        field.clear()
        field.send_keys(username)
        print(f"✅ Username diisi: {username}")

    def input_password(self, password):
        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password']")
        ))
        field.clear()
        field.send_keys(password)
        print("✅ Password diisi")

    def check_select_role(self):
        # Checkbox index 0 = Select Role, index 1 = Remember Me
        checkboxes = self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//input[@type='checkbox']")
        ))
        select_role_cb = checkboxes[0]
        if not select_role_cb.is_selected():
            select_role_cb.click()
        print("✅ Checkbox 'Select Role' dicentang")

    def click_ok(self):
        ok_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'login-btn') and contains(.,'OK')]")
        ))
        ok_btn.click()
        print("✅ Tombol OK diklik")

    def select_client_and_role(self, client_name, role_name):
        import time
        time.sleep(2)  # Tunggu dialog role muncul sepenuhnya

        # Client & Role sudah ter-select otomatis, langsung klik OK
        ok_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'login-btn') and contains(.,'OK')]")
        ))
        ok_btn.click()
        print(f"✅ Tombol OK (role dialog) diklik")