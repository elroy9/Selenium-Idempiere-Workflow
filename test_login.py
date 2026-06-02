from utils.driver_setup import get_driver
from pages.login_page import LoginPage
import time

def test_login():
    driver = get_driver()
    login = LoginPage(driver)

    try:
        login.open()
        time.sleep(2)  # Tunggu halaman load

        login.input_username("elroy.juwono")
        login.input_password("elroy.juwono")
        login.check_select_role()
        login.click_ok()

        time.sleep(3)  # Tunggu dialog role muncul

        login.select_client_and_role("920", "FICO Team Admin")

        time.sleep(3)
        print(f"\n✅ LOGIN BERHASIL! | Halaman: {driver.title}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")  # Biar bisa lihat kondisi browser saat error

    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()