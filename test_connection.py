from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome options
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:
    # Ganti URL ini dengan URL iDempiere kamu
    driver.get("http://localhost:8080/webui/")
    print("✅ Berhasil buka halaman!")
    print(f"Title: {driver.title}")
    time.sleep(3)

finally:
    driver.quit()
    print("✅ Browser ditutup.")