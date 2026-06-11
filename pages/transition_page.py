from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TransitionPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.wait_long = WebDriverWait(driver, 30)

    def wait_for_page_stable(self, seconds=2):
        time.sleep(seconds)

    def safe_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", element)

    def go_to_node(self, node_name):
        for attempt in range(3):
            try:
                node_tab = self.driver.find_element(
                    By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Node']"
                )
                self.safe_click(node_tab)
                self.wait_for_page_stable(2)
                break
            except:
                time.sleep(1)

        # Tunggu sampai Find button benar-benar visible dan enabled
        # Scope ke toolbar yang sedang aktif/visible saja
        # Tambah wait_for_page_stable extra untuk antisipasi server lag
        self.wait_for_page_stable(2)
        find_btn = self.wait_long.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Find24.png')]/..")
        ))
        self.safe_click(find_btn)
        self.wait_for_page_stable(2)

        search_key_field = self.wait_long.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@instancename='Value' and contains(@class,'z-textbox')]")
        ))
        search_key_field.clear()
        search_key_field.send_keys(node_name)
        self.wait_for_page_stable(1)
        search_key_field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(3)
        print(f"   ✅ Node '{node_name}' ditemukan")

    def click_transition_tab(self):
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Transition']")
        ))
        self.safe_click(tab)
        self.wait_for_page_stable(2)
        print("   ✅ Tab Transition diklik")

    def click_condition_tab(self):
        tabs = self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Condition']")
        ))
        target_tab = tabs[-1]
        self.safe_click(target_tab)
        self.wait_for_page_stable(2)
        print("   ✅ Tab Condition diklik")

    def click_new_transition(self):
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SHIFT + Keys.ALT + 'n')
        # Tunggu sampai form baru muncul (indikator: "Inserted" di status bar)
        # Ini lebih reliable daripada time.sleep karena menunggu server response
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[normalize-space(text())='Inserted']")
            ))
        except:
            # Kalau "Inserted" tidak muncul, tunggu biasa
            self.wait_for_page_stable(3)
        print("   ✅ New transition (Shift+Alt+N)")

    def fill_next_node(self, value):
        # Tunggu sampai span 'Next Node in workflow' benar-benar ada di DOM
        # Ini menggantikan wait_for_page_stable(3) yang tidak reliable saat server lag
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[@title='Next Node in workflow']")
        ))
        self.wait_for_page_stable(1)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        fields = self.driver.find_elements(
            By.XPATH, "//span[@title='Next Node in workflow']/ancestor::tr//input[contains(@class,'z-combobox-input')]"
        )

        next_node_field = None
        for f in fields:
            try:
                if f.is_displayed() and f.is_enabled() and f.size['width'] > 0:
                    next_node_field = f
            except:
                continue

        if not next_node_field:
            raise Exception("Next Node field tidak ditemukan atau tidak visible")

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_node_field)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", next_node_field)
        time.sleep(1)
        self.driver.execute_script("arguments[0].value = '';", next_node_field)
        next_node_field.send_keys(value)
        self.wait_for_page_stable(2)
        next_node_field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(3)
        print(f"   Next Node: {value}")

    def fill_condition(self, column_value, op_value, cond_value):
        self.click_condition_tab()
        self.wait_for_page_stable(1)

        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SHIFT + Keys.ALT + 'n')
        self.wait_for_page_stable(3)

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']")
        ))
        self.wait_for_page_stable(1)

        # COLUMN
        all_combos = self.driver.find_elements(
            By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']/ancestor::*[5]//input[contains(@class,'z-combobox-input')]"
        )
        enabled = [c for c in all_combos if c.is_enabled() and c.is_displayed() and c.size['width'] > 0]
        col_field = enabled[1]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", col_field)
        time.sleep(1)
        ActionChains(self.driver).move_to_element(col_field).click().send_keys(column_value).perform()
        self.wait_for_page_stable(2)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self.wait_for_page_stable(2)
        print(f"   Column: {column_value}")

        # OPERATION
        all_combos2 = self.driver.find_elements(
            By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']/ancestor::*[5]//input[contains(@class,'z-combobox-input')]"
        )
        enabled2 = [c for c in all_combos2 if c.is_enabled() and c.is_displayed() and c.size['width'] > 0]
        op_field = enabled2[2]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", op_field)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", op_field)
        time.sleep(0.5)
        op_field.send_keys(' =')
        self.wait_for_page_stable(1)
        op_field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(1)
        print(f"   Operator: =")

        # VALUE
        all_textareas = self.driver.find_elements(
            By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']"
        )
        value_textarea = None
        for t in all_textareas:
            try:
                if t.is_displayed() and t.size['height'] > 0:
                    value_textarea = t
            except:
                continue

        if not value_textarea:
            raise Exception("Value textarea tidak ditemukan")

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", value_textarea)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", value_textarea)
        time.sleep(0.5)
        value_textarea.send_keys(Keys.CONTROL + 'a')
        time.sleep(0.3)
        value_textarea.send_keys(str(cond_value))
        time.sleep(0.5)

        # Blur dulu supaya ZK Framework simpan value
        # TIDAK pakai Keys.TAB — bisa pindahkan fokus ke element lain
        self.driver.execute_script("arguments[0].blur();", value_textarea)
        time.sleep(1)
        print(f"   Value: {cond_value}")

        # Klik Parent Record untuk naik dari Condition ke Transition
        # Pastikan ada 1 detik jeda setelah blur sebelum klik
        self.wait_for_page_stable(1)
        self._click_parent_record_with_debug()

    def _click_parent_record_with_debug(self):
        """Klik Parent Record — ambil yang TERAKHIR visible (paling dalam di DOM)."""
        all_parents = self.driver.find_elements(
            By.XPATH, "//img[contains(@src,'Parent24.png')]/.."
        )
        print(f"   🔍 Parent24 ditemukan: {len(all_parents)} buah")
        for i, p in enumerate(all_parents):
            try:
                print(f"      [{i}] displayed={p.is_displayed()} enabled={p.is_enabled()} class={p.get_attribute('class')}")
            except:
                pass

        # Ambil yang TERAKHIR visible dan enabled
        # Iterasi 1: hanya 1 Parent24 → ambil satu-satunya
        # Iterasi 2+: ada 2 Parent24, [0]=hidden [1]=visible
        #   [1] adalah toolbar aktif untuk level Condition saat ini
        #   sehingga klik [1] naik dari Condition → Transition (benar)
        target = None
        for p in reversed(all_parents):
            try:
                if p.is_displayed() and p.is_enabled():
                    target = p
                    break
            except:
                continue

        if not target:
            raise Exception("Parent Record tidak ditemukan atau tidak bisa diklik")

        self.safe_click(target)
        self.wait_for_page_stable(2)
        print("   ✅ Parent Record diklik (auto-save + naik ke Transition)")

    def save(self):
        # Di CPERP, klik Parent Record sudah auto-save
        # Tidak perlu klik Save lagi — cukup print konfirmasi
        print("   ✅ Disimpan (auto-save via Parent Record)")

    def navigate_via_next_node_label(self):
        """
        Navigasi ke node berikutnya via label Next Node in workflow.
        Setelah fill_condition() + Parent Record, kita sudah di level Transition.
        Cari Next Node label yang VISIBLE dan DISPLAYED saja.
        """
        # Debug: cek breadcrumb posisi saat ini
        try:
            bc = self.driver.find_elements(By.XPATH,
                "//*[contains(@class,'breadcrumb') or contains(@id,'breadcrumb')]//*[self::a or self::span][normalize-space(text())!='']"
            )
            bc_texts = [b.text.strip() for b in bc if b.is_displayed() and b.text.strip()]
            print(f"   🔍 Posisi saat ini: {' > '.join(bc_texts)}")
        except:
            pass

        # Kalau masih ada link 'Transition' di breadcrumb = masih di Condition
        try:
            transition_link = self.driver.find_element(
                By.XPATH, "//a[normalize-space(text())='Transition']"
            )
            if transition_link.is_displayed():
                self.safe_click(transition_link)
                self.wait_for_page_stable(2)
                print("   ✅ Naik ke Transition via breadcrumb")
        except:
            pass

        # Cari Next Node label — pakai wait.until dengan re-find fresh
        # Jangan simpan referensi lama (stale element)
        # Cari yang visible di form aktif saja
        for attempt in range(3):
            try:
                all_labels = self.driver.find_elements(
                    By.XPATH,
                    "//span[contains(@class,'idempiere-zoomable-label')"
                    " and @title='Next Node in workflow']"
                )
                print(f"   🔍 Next Node label ditemukan: {len(all_labels)} buah")

                target_label = None
                for lbl in all_labels:
                    try:
                        if lbl.is_displayed() and lbl.size['width'] > 0:
                            target_label = lbl
                            print(f"      → Klik label: '{lbl.text}'")
                            break
                    except:
                        continue

                if not target_label:
                    raise Exception("Tidak ada label visible")

                self.safe_click(target_label)
                self.wait_for_page_stable(3)
                print("   ✅ Navigate via Next Node label")
                return

            except Exception as e:
                print(f"   ⚠️ Attempt {attempt+1} gagal: {e}, retry...")
                time.sleep(2)

        raise Exception("Next Node label tidak bisa diklik setelah 3 percobaan")

    def process_pga_chain(self, full_name, csv_value):
        chain = [
            ("(Mapping PGA GM)",                        f"(Approval PGA GM {full_name})"),
            (f"(Approval PGA GM {full_name})",           "(Mapping PGA Deputy BU Head)"),
            ("(Mapping PGA Deputy BU Head)",             f"(Approval PGA Dep BU Head {full_name})"),
            (f"(Approval PGA Dep BU Head {full_name})",  "(Mapping PGA BU Head)"),
            ("(Mapping PGA BU Head)",                    f"(Approval PGA BU Head {full_name})"),
            (f"(Approval PGA BU Head {full_name})",      "(Mapping PGA HOO)"),
            ("(Mapping PGA HOO)",                        f"(Approval PGA HOO {full_name})"),
            (f"(Approval PGA HOO {full_name})",          "(Mapping PGA Division Head)"),
            ("(Mapping PGA Division Head)",              f"(Approval PGA Div Head {full_name})"),
            (f"(Approval PGA Div Head {full_name})",     "(DocComplete)"),
        ]

        print(f"\n--- PGA Chain [{full_name}] ---")
        self.go_to_node(chain[0][0])

        for i, (from_node, to_node) in enumerate(chain):
            print(f"\n   [{i+1}/{len(chain)}] {from_node} → {to_node}")
            self.click_transition_tab()
            self.click_new_transition()
            self.fill_next_node(to_node)
            self.fill_condition("User1_ID_Cost Center", "=", csv_value)
            self.save()

            if i < len(chain) - 1:
                self.navigate_via_next_node_label()

        # Tutup semua window lain setelah chain selesai supaya tidak lag
        self.close_other_windows()
        print(f"--- PGA Chain [{full_name}] SELESAI ---")

    def process_legal_chain(self, full_name, csv_value):
        chain = [
            ("(Mapping Legal)",                             f"(Approval Head Legal {full_name})"),
            (f"(Approval Head Legal {full_name})",           "(Mapping Legal GM)"),
            ("(Mapping Legal GM)",                          f"(Approval Legal GM {full_name})"),
            (f"(Approval Legal GM {full_name})",             "(Mapping Legal Deputy BU Head)"),
            ("(Mapping Legal Deputy BU Head)",              f"(Approval Legal Dep BU Head {full_name})"),
            (f"(Approval Legal Dep BU Head {full_name})",    "(Mapping Legal BU Head)"),
            ("(Mapping Legal BU Head)",                     f"(Approval Legal BU Head {full_name})"),
            (f"(Approval Legal BU Head {full_name})",        "(Mapping Legal HOO)"),
            ("(Mapping Legal HOO)",                         f"(Approval Legal HOO {full_name})"),
            (f"(Approval Legal HOO {full_name})",            "(Mapping Legal Division Head)"),
            ("(Mapping Legal Division Head)",               f"(Approval Legal Div Head {full_name})"),
            (f"(Approval Legal Div Head {full_name})",       "(DocComplete)"),
        ]

        print(f"\n--- Legal Chain [{full_name}] ---")
        self.go_to_node(chain[0][0])

        for i, (from_node, to_node) in enumerate(chain):
            print(f"\n   [{i+1}/{len(chain)}] {from_node} → {to_node}")
            self.click_transition_tab()
            self.click_new_transition()
            self.fill_next_node(to_node)
            self.fill_condition("User1_ID_Cost Center", "=", csv_value)
            self.save()

            if i < len(chain) - 1:
                self.navigate_via_next_node_label()

        # Tutup semua window lain setelah chain selesai supaya tidak lag
        self.close_other_windows()
        print(f"--- Legal Chain [{full_name}] SELESAI ---")

    def close_other_windows(self):
        """
        Tutup semua tab Workflow yang terbuka.
        1. Klik Home tab via JS
        2. Dispatch contextmenu pada li.desktop-hometab (bukan span)
        3. Klik Close All Windows via JS (presence_of_element_located, bukan element_to_be_clickable)
        """
        try:
            # Step 1: Klik Home tab via JS — bypass scroll tab bar
            home_span = self.driver.find_element(
                By.XPATH,
                "//li[contains(@class,'desktop-hometab')]"
                "//span[contains(@class,'z-tab-text')]"
            )
            self.driver.execute_script("arguments[0].click();", home_span)
            self.wait_for_page_stable(1)
            print("   ✅ Tab Home diklik")

            # Step 2: Dispatch contextmenu pada <li> desktop-hometab
            # Handler contextmenu ada di <li>, bukan di <span> anaknya
            home_li = self.driver.find_element(
                By.XPATH, "//li[contains(@class,'desktop-hometab')]"
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new MouseEvent('contextmenu',"
                "{bubbles:true,cancelable:true,view:window}));",
                home_li
            )
            time.sleep(2)

            # Step 3: Klik Close All Windows via JS
            # Gunakan presence_of_element_located (bukan element_to_be_clickable)
            # karena span dalam popup ZK tidak selalu dianggap 'clickable' oleh Selenium
            close_all = self.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "//span[contains(@class,'z-menuitem-text')"
                 " and normalize-space(text())='Close All Windows']")
            ))
            self.driver.execute_script("arguments[0].click();", close_all)
            self.wait_for_page_stable(3)
            print("   ✅ Close All Windows berhasil")

        except Exception as e:
            print(f"   ⚠️ Close All Windows gagal: {e}")