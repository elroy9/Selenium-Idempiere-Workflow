from utils.driver_setup import get_driver
from utils.csv_helper import load_csv, parse_cost_center
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pages.transition_page import TransitionPage
import time

CSV_PATH = "data/testing_workflow_ppbp.csv"

def go_to_workflow_node_tab(driver, workflow, transition):
    """Helper: kembali ke Workflow PPBP Node tab"""
    workflow.search_menu("Workflow")
    time.sleep(3)
    workflow.click_search_button()
    time.sleep(2)
    workflow.fill_search_key("%Workflow PPBP%")
    time.sleep(3)
    node_tab = driver.find_element("xpath",
        "//span[contains(@class,'z-tab-text') and normalize-space(text())='Node']")
    node_tab.click()
    time.sleep(2)
    print("✅ Kembali ke Workflow PPBP Node tab")

def test_connect_nodes():
    driver = get_driver()
    login = LoginPage(driver)
    workflow = WorkflowPage(driver)
    transition = TransitionPage(driver)

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

        # === STEP 2: Buka Workflow PPBP Node tab ===
        go_to_workflow_node_tab(driver, workflow, transition)

        # === STEP 3: Baca CSV ===
        rows = load_csv(CSV_PATH, limit=1)  # Test 1 baris dulu
        print(f"\n✅ {len(rows)} baris data dimuat dari CSV")

        for i, row in enumerate(rows):
            cost_center = row['COST CENTER']
            csv_value = row['Value']
            full_name, abbrev = parse_cost_center(cost_center)

            print(f"\n{'='*50}")
            print(f"🔄 Baris {i+1}: {cost_center}")
            print(f"   Full Name : {full_name}")
            print(f"   Value     : {csv_value}")
            print(f"{'='*50}")

            # === PGA Chain ===
            transition.process_pga_chain(full_name, csv_value)

            # === Kembali ke Workflow PPBP untuk Legal Chain ===
            go_to_workflow_node_tab(driver, workflow, transition)

            # === Legal Chain ===
            transition.process_legal_chain(full_name, csv_value)

            # === Kembali jika ada baris berikutnya ===
            if i < len(rows) - 1:
                go_to_workflow_node_tab(driver, workflow, transition)

        print(f"\n✅ SELESAI! Semua transisi berhasil dibuat.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_connect_nodes()