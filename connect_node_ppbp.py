from utils.driver_setup import get_driver
from utils.csv_helper import load_csv, parse_cost_center
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pages.transition_page import TransitionPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import getpass
import os

def get_user_input():
    print("=" * 50)
    print("  SELENIUM IDEMPIERE - WORKFLOW PPBP AUTOMATION")
    print("=" * 50)

    username = input("\n👤 Username iDempiere: ").strip()
    password = getpass.getpass("🔑 Password iDempiere: ")

    while True:
        csv_path = input("\n📂 Path file CSV (contoh: data/testing_workflow_ppbp.csv): ").strip()
        if os.path.exists(csv_path):
            break
        print(f"   ❌ File tidak ditemukan: {csv_path}. Coba lagi.")

    while True:
        try:
            limit = int(input("\n🔢 Berapa baris CSV yang ingin diproses? ").strip())
            if limit > 0:
                break
            print("   ❌ Masukkan angka lebih dari 0.")
        except ValueError:
            print("   ❌ Masukkan angka yang valid.")

    print(f"\n✅ Input diterima:")
    print(f"   Username : {username}")
    print(f"   Password : {'*' * len(password)}")
    print(f"   File CSV : {csv_path}")
    print(f"   Jumlah baris: {limit}")
    print("=" * 50)

    return username, password, csv_path, limit


def go_to_workflow_node_tab(driver, workflow):
    workflow.search_menu("Workflow")
    time.sleep(5)

    # Tunggu sampai breadcrumb "Workflow" muncul — tanda halaman sudah load
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[normalize-space(text())='Workflow' and contains(@class,'z-label')]"
             " | //div[contains(@class,'adwindow')]")
        )
    )
    time.sleep(2)

    workflow.click_search_button()
    time.sleep(2)
    workflow.fill_search_key("%Workflow PPBP%")
    time.sleep(3)

    first_record = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'z-grid-body')]//tr[contains(@class,'z-row')][1]//td[2]")
        )
    )
    driver.execute_script("arguments[0].click();", first_record)
    time.sleep(2)
    print("✅ Record dipilih")

    node_tab = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Node']")
        )
    )
    driver.execute_script("arguments[0].click();", node_tab)
    time.sleep(2)
    print("✅ Kembali ke Workflow PPBP Node tab")


def test_connect_nodes():
    username, password, csv_path, limit = get_user_input()

    driver = get_driver()
    login = LoginPage(driver)
    workflow = WorkflowPage(driver)
    transition = TransitionPage(driver)

    try:
        # === STEP 1: Login ===
        login.open()
        time.sleep(2)
        login.input_username(username)
        login.input_password(password)
        login.check_select_role()
        login.click_ok()
        time.sleep(2)
        login.select_client_and_role("920", "FICO Team Admin")
        time.sleep(4)
        print("✅ Login berhasil")

        # === STEP 2: Buka Workflow PPBP Node tab ===
        go_to_workflow_node_tab(driver, workflow)

        # === STEP 3: Baca CSV ===
        rows = load_csv(csv_path, limit=limit)
        print(f"\n✅ {len(rows)} baris data dimuat dari CSV")

        for i, row in enumerate(rows):
            cost_center = row['COST CENTER']
            csv_value = row['Value']
            full_name, abbrev = parse_cost_center(cost_center)

            print(f"\n{'='*50}")
            print(f"🔄 Baris {i+1}/{len(rows)}: {cost_center}")
            print(f"   Full Name : {full_name}")
            print(f"   Value     : {csv_value}")
            print(f"{'='*50}")

            # === PGA Chain ===
            transition.process_pga_chain(full_name, csv_value)

            # Setelah close_other_windows, navigate ke Workflow PPBP dulu
            go_to_workflow_node_tab(driver, workflow)

            # === Legal Chain ===
            transition.process_legal_chain(full_name, csv_value)

            # Kalau ada baris berikutnya, buka Workflow PPBP lagi
            if i < len(rows) - 1:
                go_to_workflow_node_tab(driver, workflow)

        print(f"\n{'='*50}")
        print(f"✅ SELESAI! {len(rows)} baris berhasil diproses.")
        print(f"{'='*50}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_connect_nodes()