from utils.driver_setup import get_driver
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
import time

def test_search_workflow():
    driver = get_driver()
    login = LoginPage(driver)
    workflow = WorkflowPage(driver)

    try:
        # === STEP 1: Login ===
        login.open()
        time.sleep(2)
        login.input_username("elroy.juwono")
        login.input_password("elroy.juwono")
        login.check_select_role()
        login.click_ok()
        time.sleep(2)
        login.select_client_and_role("920", "FICO Team Admin")
        time.sleep(4)
        print(f"✅ Login berhasil | {driver.title}")

        # === STEP 2: Cari menu Workflow + Enter ===
        workflow.search_menu("Workflow")
        time.sleep(3)  # Tunggu halaman Workflow load

        # === STEP 3: Klik tombol Search (kaca pembesar) ===
        workflow.click_search_button()
        time.sleep(2)

        # === STEP 4: Isi Search Key ===
        workflow.fill_search_key("%Workflow PPBP%")
        time.sleep(3)
        print(f"\n✅ STEP 2 SELESAI!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_search_workflow()