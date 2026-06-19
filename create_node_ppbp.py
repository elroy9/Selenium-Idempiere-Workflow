from utils.driver_setup import get_driver
from utils.csv_helper import load_csv
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pages.node_page import NodePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import getpass
import os

def get_user_input():
    print("=" * 50)
    print("  SELENIUM IDEMPIERE - WORKFLOW AUTOMATION")
    print("=" * 50)

    username = input("\n👤 Username iDempiere: ").strip()
    password = getpass.getpass("🔑 Password iDempiere: ")
    client   = input("🏢 Client (contoh: 920): ").strip()
    role     = input("👔 Role (contoh: FICO Team Admin): ").strip()

    while True:
        csv_path = input("\n📂 Path file CSV: ").strip()
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
    print(f"   Client   : {client}")
    print(f"   Role     : {role}")
    print(f"   File CSV : {csv_path}")
    print(f"   Jumlah baris: {limit}")
    print("=" * 50)

    return username, password, client, role, csv_path, limit


def test_create_nodes():
    username, password, client, role, csv_path, limit = get_user_input()

    driver = get_driver()
    login = LoginPage(driver)
    workflow = WorkflowPage(driver)
    node = NodePage(driver)

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

        # === STEP 2: Buka Workflow PPBP ===
        workflow.search_menu("Workflow")
        time.sleep(3)
        workflow.click_search_button()
        time.sleep(2)
        workflow.fill_search_key("%Workflow PPBP%")
        time.sleep(3)

        # Klik record pertama dari hasil search
        first_record = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class,'z-grid-body')]//tr[contains(@class,'z-row')][1]//td[2]")
            )
        )
        driver.execute_script("arguments[0].click();", first_record)
        time.sleep(2)
        print("✅ Halaman Workflow PPBP terbuka")

        # === STEP 3: Klik Tab Node ===
        node_tab = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Node']")
            )
        )
        driver.execute_script("arguments[0].click();", node_tab)
        time.sleep(2)
        print("✅ Tab Node diklik")

        # === STEP 4: Baca CSV & Buat Nodes ===
        rows = load_csv(csv_path, limit=limit)
        print(f"\n✅ {len(rows)} baris data dimuat dari CSV")

        for i, row in enumerate(rows):
            print(f"\n🔄 Memproses baris {i+1}/{len(rows)}: {row['COST CENTER']}")
            node.create_nodes_from_row(row)

        print(f"\n{'='*50}")
        print(f"✅ SELESAI! {len(rows)} baris berhasil diproses.")
        print(f"{'='*50}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_create_nodes()