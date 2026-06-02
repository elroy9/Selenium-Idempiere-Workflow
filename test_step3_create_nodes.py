from utils.driver_setup import get_driver
from utils.csv_helper import load_csv
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pages.node_page import NodePage
import time

CSV_PATH = "data/testing_workflow_ppbp.csv"

def test_create_nodes():
    driver = get_driver()
    login = LoginPage(driver)
    workflow = WorkflowPage(driver)
    node = NodePage(driver)

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
        print("✅ Login berhasil")

        # === STEP 2: Buka Workflow PPBP ===
        workflow.search_menu("Workflow")
        time.sleep(3)
        workflow.click_search_button()
        time.sleep(2)
        workflow.fill_search_key("%Workflow PPBP%")
        time.sleep(3)
        print("✅ Halaman Workflow PPBP terbuka")

        # === STEP 3: Klik Tab Node ===
        node.click_node_tab()

        # === STEP 4: Baca CSV & Buat Nodes ===
        rows = load_csv(CSV_PATH, limit=1)
        print(f"\n✅ {len(rows)} baris data dimuat dari CSV")

        for i, row in enumerate(rows):
            print(f"\n🔄 Memproses baris {i+1}: {row['COST CENTER']}")
            node.create_nodes_from_row(row)

        print(f"\n✅ SELESAI! Semua node berhasil dibuat.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_create_nodes()