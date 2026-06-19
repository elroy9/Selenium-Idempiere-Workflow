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
    print("  WORKFLOW RESPONSIBLE CHECKER — GASOLINE")
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
#  BUKA HALAMAN WORKFLOW RESPONSIBLE (fresh setiap dipanggil)
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

    # Pakai visibility_of_element_located (bukan presence) — pastikan field
    # benar-benar TERLIHAT, bukan cuma ada di DOM (bisa jadi dari tab lama
    # yang tertutup tab baru). Tidak ada retry di sini supaya tidak membuka
    # tab duplikat berkali-kali.
    WebDriverWait(driver, 25).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@instancename='Name' and contains(@class,'z-textbox')]")
        )
    )
    time.sleep(1)
    print("✅ Halaman Workflow Responsible terbuka")


# ─────────────────────────────────────────────
#  TUTUP SEMUA WINDOW — pola sama dengan TransitionPage
#  (Home tab klik -> contextmenu -> Close All Windows)
# ─────────────────────────────────────────────
def close_all_windows(driver):
    try:
        home_span = driver.find_element(
            By.XPATH,
            "//li[contains(@class,'desktop-hometab')]//span[contains(@class,'z-tab-text')]"
        )
        driver.execute_script("arguments[0].click();", home_span)
        time.sleep(1)

        home_li = driver.find_element(
            By.XPATH, "//li[contains(@class,'desktop-hometab')]"
        )
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('contextmenu',"
            "{bubbles:true,cancelable:true,view:window}));",
            home_li
        )
        time.sleep(2)

        close_all = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//span[contains(@class,'z-menuitem-text')"
                 " and normalize-space(text())='Close All Windows']")
            )
        )
        driver.execute_script("arguments[0].click();", close_all)
        time.sleep(2)
        print("   ✅ Close All Windows berhasil")

    except Exception as e:
        print(f"   ⚠️ Close All Windows gagal (dilanjut tanpa close): {e}")


# ─────────────────────────────────────────────
#  TUTUP POPUP "No Records found" KALAU MUNCUL
# ─────────────────────────────────────────────
def dismiss_no_records_popup(driver, max_attempts=3):
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


# ─────────────────────────────────────────────
#  CEK SATU NAMA WR (asumsi window sudah dalam mode Find / fresh)
# ─────────────────────────────────────────────
def check_wr(driver, wr_name):
    wait = WebDriverWait(driver, 15)

    # Pastikan field Name benar-benar visible dulu sebelum diisi
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@instancename='Name' and contains(@class,'z-textbox')]")
    ))

    # Isi field Name — ambil yang visible+enabled TERAKHIR
    name_fields = driver.find_elements(
        By.XPATH, "//input[@instancename='Name' and contains(@class,'z-textbox')]"
    )
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

    return found


# ─────────────────────────────────────────────
#  CEK WR UNTUK SATU FARM (GASOLINE — hanya 1 WR)
#  Setiap farm: buka fresh -> cek -> tutup semua window
# ─────────────────────────────────────────────
def check_wr_for_farm(driver, full_name):
    wr_name = f"PGA {full_name} GASOLINE USAGE"

    open_workflow_responsible(driver)
    found = check_wr(driver, wr_name)
    status = "✅" if found else "❌"
    print(f"   {status} {wr_name}")

    close_all_windows(driver)

    return [(wr_name, status)], found


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    username, password, client, role, csv_path, limit = get_user_input()

    driver = get_driver()
    login  = LoginPage(driver)

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

            results, all_ok = check_wr_for_farm(driver, full_name)
            summary[full_name] = results

        # ── PRINT SUMMARY ──────────────────────────
        print(f"\n\n{'='*55}")
        print(f"  SUMMARY HASIL CEK WORKFLOW RESPONSIBLE GASOLINE")
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
        import traceback
        print(f"\n❌ ERROR: {e}")
        print("\n--- TRACEBACK LENGKAP ---")
        traceback.print_exc()
        print("-------------------------\n")
        input("Tekan Enter untuk tutup browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()