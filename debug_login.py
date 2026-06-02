from utils.driver_setup import get_driver
import time

driver = get_driver()
driver.get("http://10.1.3.152:9292/webui/index.zul")
time.sleep(3)  # Tunggu halaman load penuh

# Print semua input yang ditemukan di halaman
inputs = driver.find_elements("tag name", "input")
print(f"\n=== Ditemukan {len(inputs)} input element ===")
for i, el in enumerate(inputs):
    print(f"[{i}] type='{el.get_attribute('type')}' | id='{el.get_attribute('id')}' | name='{el.get_attribute('name')}' | class='{el.get_attribute('class')}'")

# Print semua button
buttons = driver.find_elements("tag name", "button")
print(f"\n=== Ditemukan {len(buttons)} button element ===")
for i, btn in enumerate(buttons):
    print(f"[{i}] text='{btn.text}' | id='{btn.get_attribute('id')}' | class='{btn.get_attribute('class')}'")

input("\nTekan Enter untuk tutup...")
driver.quit()
