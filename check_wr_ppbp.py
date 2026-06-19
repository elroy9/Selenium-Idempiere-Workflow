from utils.driver_setup import get_driver
from utils.csv_helper import load_csv, parse_cost_center
from pages.login_page import LoginPage
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
    print("=" * 55)
    print("  WORKFLOW RESPONSIBLE CHECKER — PPBP")
    print("=" * 55)

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
            limit = int(input("\n🔢 Berapa baris CSV yang ingin dicek? ").strip())
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
    print("=" * 55)

    return username, password, client, role, csv_path, limit


# ─────────────────────────────────────────────
#  BUKA HALAMAN WORKFLOW RESPONSIBLE
# ─────────────────────────────────────────────
def open_workflow_responsible(driver):
    search_bar = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@class,'z-bandbox-input')]")
        )
    )
    search_bar.clear()
    search_bar.send_keys("Workflow Responsible")
    time.sleep(2)
    search_bar.send_keys(Keys.ENTER)
    time.sleep(4)
    print("✅ Halaman Workflow Responsible terbuka")


# ─────────────────────────────────────────────
#  CEK SATU NAMA WR
# ─────────────────────────────────────────────
def dismiss_no_records_popup(driver, max_attempts=3):
    """Tutup popup 'No Records found' jika muncul, return True jika popup ditemukan & ditutup."""
    dismissed = False
    for _ in range(max_attempts):
        spans = driver.find_elements(
            By.XPATH, "//span[normalize-space(text())='No Records found']"
        )
        visible = [s for s in spans if s.is_displayed()]
        if not visible:
            break

        dismissed = True
        try:
            popup = visible[0].find_element(By.XPATH, "ancestor::div[contains(@class,'z-window')][1]")
            ok_btn = popup.find_element(
                By.XPATH, ".//button[contains(.,'OK')] | .//span[contains(@class,'z-toolbarbutton-text') and normalize-space(text())='OK']"
            )
            driver.execute_script("arguments[0].click();", ok_btn)
        except Exception:
            ok_btns = driver.find_elements(By.XPATH, "//button[contains(.,'OK')]")
            clicked = False
            for b in ok_btns:
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    clicked = True
                    break
            if not clicked:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

        time.sleep(1)

    return dismissed

def check_wr(driver, wr_name):
    wait = WebDriverWait(driver, 15)

    # Bersihkan dulu kalau ada popup nyangkut dari pengecekan sebelumnya
    dismiss_no_records_popup(driver)

    # Buka dialog search (Alt+F)
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.ALT + 'f')
    time.sleep(2)

    # Isi field Name — ambil yang visible+enabled TERAKHIR
    name_fields = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//input[@instancename='Name' and contains(@class,'z-textbox')]")
    ))
    target_field = None
    for f in name_fields:
        try:
            if f.is_displayed() and f.is_enabled():
                target_field = f
        except:
            continue

    if not target_field:
        raise Exception("Name field tidak ditemukan/visible")

    target_field.clear()
    target_field.send_keys(wr_name)
    target_field.send_keys(Keys.ENTER)
    time.sleep(2)

    # Cek popup "No Records found"
    popup_appeared = dismiss_no_records_popup(driver)
    found = not popup_appeared

    # Tutup Lookup Record (Cancel) supaya state bersih untuk pencarian berikutnya
    try:
        cancel_btns = driver.find_elements(By.XPATH, "//button[contains(.,'Cancel')]")
        visible_cancel = [c for c in cancel_btns if c.is_displayed() and c.is_enabled()]
        if visible_cancel:
            driver.execute_script("arguments[0].click();", visible_cancel[-1])
            time.sleep(1)
    except Exception:
        pass

    return found


# ─────────────────────────────────────────────
#  CEK SEMUA WR UNTUK SATU FARM
# ─────────────────────────────────────────────
def check_all_wr_for_farm(driver, full_name):
    wr_list = [
        f"Head Legal {full_name} PPBP",
        f"GM {full_name} PPBP",
        f"Deputy BU Head {full_name} PPBP",
        f"BU Head {full_name} PPBP",
        f"HOO {full_name} PPBP",
        f"Division Head {full_name} PPBP",
    ]

    results = []
    all_ok = True

    for wr_name in wr_list:
        found = check_wr(driver, wr_name)
        status = "✅" if found else "❌"
        if not found:
            all_ok = False
        results.append((wr_name, status))
        print(f"   {status} {wr_name}")

    return results, all_ok


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    username, password, client, role, csv_path, limit = get_user_input()

    driver = get_driver()
    login  = LoginPage(driver)

    # Summary untuk semua farm
    summary = {}

    try:
        # Login
        login.open()
        time.sleep(2)
        login.input_username(username)
        login.input_password(password)
        login.check_select_role()
        login.click_ok()
        time.sleep(2)
        login.select_client_and_role(client, role)
        time.sleep(4)
        print("✅ Login berhasil")

        # Buka Workflow Responsible
        open_workflow_responsible(driver)

        # Baca CSV
        rows = load_csv(csv_path, limit=limit)
        print(f"\n✅ {len(rows)} baris data dimuat dari CSV\n")

        for i, row in enumerate(rows):
            cost_center = row['COST CENTER']
            full_name, _ = parse_cost_center(cost_center)

            print(f"\n{'='*55}")
            print(f"🔄 Baris {i+1}/{len(rows)}: {cost_center}")
            print(f"   Farm : {full_name}")
            print(f"{'='*55}")

            results, all_ok = check_all_wr_for_farm(driver, full_name)
            summary[full_name] = results

        # ── PRINT SUMMARY ──────────────────────────
        print(f"\n\n{'='*55}")
        print(f"  SUMMARY HASIL CEK WORKFLOW RESPONSIBLE PPBP")
        print(f"{'='*55}")

        for farm, results in summary.items():
            farm_ok = all(s == "✅" for _, s in results)
            farm_status = "✅ LENGKAP" if farm_ok else "❌ ADA YANG KURANG"
            print(f"\n📍 {farm} — {farm_status}")
            for wr_name, status in results:
                print(f"   {status} {wr_name}")

        print(f"\n{'='*55}")
        print(f"✅ SELESAI! {len(rows)} baris dicek.")
        print(f"{'='*55}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()