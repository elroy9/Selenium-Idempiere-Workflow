from utils.driver_setup import get_driver
from utils.csv_helper import load_csv, parse_cost_center
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pages.node_page import NodePage
from pages.transition_page import TransitionPage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import getpass
import os


# ─────────────────────────────────────────────
#  USER INPUT
# ─────────────────────────────────────────────
def get_user_input():
    print("=" * 50)
    print("  SELENIUM IDEMPIERE - WORKFLOW GASOLINE")
    print("=" * 50)

    username = input("\n👤 Username iDempiere: ").strip()
    password = getpass.getpass("🔑 Password iDempiere: ")

    while True:
        csv_path = input("\n📂 Path file CSV (contoh: data/workflow_gasoline.csv): ").strip()
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
    print(f"   Username     : {username}")
    print(f"   Password     : {'*' * len(password)}")
    print(f"   File CSV     : {csv_path}")
    print(f"   Jumlah baris : {limit}")
    print("=" * 50)

    return username, password, csv_path, limit


# ─────────────────────────────────────────────
#  NAVIGATE TO WORKFLOW GASOLINE NODE TAB
# ─────────────────────────────────────────────
def go_to_workflow_node_tab(driver, workflow):
    workflow.search_menu("Workflow")
    time.sleep(5)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[normalize-space(text())='Workflow' and contains(@class,'z-label')]"
             " | //div[contains(@class,'adwindow')]")
        )
    )
    time.sleep(2)

    workflow.click_search_button()
    time.sleep(2)
    workflow.fill_search_key("%WFGasolineUsage%")
    time.sleep(4)  # Tambah wait lebih lama

    # Tunggu sampai grid muncul dulu
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'z-grid-body')]//tr[contains(@class,'z-row')]")
        )
    )
    time.sleep(1)

    first_record = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'z-grid-body')]//tr[contains(@class,'z-row')][1]//td[2]")
        )
    )
    driver.execute_script("arguments[0].click();", first_record)
    time.sleep(2)
    print("✅ Record Workflow Gasoline dipilih")

    node_tab = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Node']")
        )
    )
    driver.execute_script("arguments[0].click();", node_tab)
    time.sleep(2)
    print("✅ Kembali ke Workflow Gasoline Node tab")


# ─────────────────────────────────────────────
#  NODE CREATION — GASOLINE (1 node per row)
# ─────────────────────────────────────────────
def create_gasoline_node(node_page, row):
    """
    Buat 1 node per baris CSV:
      Search Key : (Approval PGA **)   → ** = abbrev cost center
      Name       : (Approval PGA {})   → {} = full name cost center
      WF Resp    : PGA {} GASOLINE USAGE
      Action     : User Choice
      Column     : IsApproved_Approved
    """
    cost_center = row['COST CENTER']
    full_name, abbrev = parse_cost_center(cost_center)

    search_key  = f"(Approval PGA {abbrev})"
    name        = f"(Approval PGA {full_name})"
    wf_resp     = f"PGA {full_name} GASOLINE USAGE"

    print(f"\n   📌 Membuat node: {name}")
    print(f"      Search Key        : {search_key}")
    print(f"      Workflow Resp     : {wf_resp}")

    node_page.create_node(search_key, name, wf_resp)
    print(f"   ✅ Node selesai dibuat")


# ─────────────────────────────────────────────
#  TRANSITION CHAIN — GASOLINE
#  (Mapping PGA) → (Approval PGA {}) → (DocComplete)
# ─────────────────────────────────────────────
def process_gasoline_chain(transition_page, full_name, csv_value):
    chain = [
        ("(Mapping PGA)",          f"(Approval PGA {full_name})"),
        (f"(Approval PGA {full_name})", "(DocComplete)"),
    ]

    print(f"\n--- Gasoline Chain [{full_name}] ---")
    transition_page.go_to_node(chain[0][0])

    for i, (from_node, to_node) in enumerate(chain):
        print(f"\n   [{i+1}/{len(chain)}] {from_node} → {to_node}")
        transition_page.click_transition_tab()
        transition_page.click_new_transition()
        transition_page.fill_next_node(to_node)
        transition_page.fill_condition("User1_ID_Cost Center", "=", csv_value)
        transition_page.save()

        if i < len(chain) - 1:
            transition_page.navigate_via_next_node_label()

    transition_page.close_other_windows()
    print(f"--- Gasoline Chain [{full_name}] SELESAI ---")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    username, password, csv_path, limit = get_user_input()

    driver      = get_driver()
    login       = LoginPage(driver)
    workflow    = WorkflowPage(driver)
    node_page   = NodePage(driver)
    transition  = TransitionPage(driver)

    try:
        # ── STEP 1: Login ───────────────────────────
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

        # ── STEP 2: Buka Workflow Gasoline Node tab ─
        go_to_workflow_node_tab(driver, workflow)

        # ── Baca CSV ────────────────────────────────
        rows = load_csv(csv_path, limit=limit)
        print(f"\n✅ {len(rows)} baris data dimuat dari CSV")

        for i, row in enumerate(rows):
            cost_center = row['COST CENTER']
            csv_value   = row['Value']
            full_name, abbrev = parse_cost_center(cost_center)

            print(f"\n{'='*50}")
            print(f"🔄 Baris {i+1}/{len(rows)}: {cost_center}")
            print(f"   Full Name : {full_name}")
            print(f"   Abbrev    : {abbrev}")
            print(f"   Value     : {csv_value}")
            print(f"{'='*50}")

            # ── STEP 3: Buat Node ───────────────────
            create_gasoline_node(node_page, row)

            # Close windows dulu agar state bersih sebelum connect
            transition.close_other_windows()

            # ── STEP 4: Connect Node ────────────────
            go_to_workflow_node_tab(driver, workflow)
            process_gasoline_chain(transition, full_name, csv_value)

            # Kalau ada baris berikutnya
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
    main()