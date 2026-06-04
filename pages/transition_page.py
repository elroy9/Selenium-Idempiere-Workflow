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
        # Klik tab Node
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

        # Klik Find
        find_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Find24.png')]/..")
        ))
        self.safe_click(find_btn)
        self.wait_for_page_stable(2)

        # Isi Search Key field (instancename="Value")
        search_key_field = self.wait_long.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@instancename='Value' and contains(@class,'z-textbox')]")
        ))
        search_key_field.clear()
        search_key_field.send_keys(node_name)
        self.wait_for_page_stable(1)
        search_key_field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(3)
        print(f"   ✅ Node '{node_name}' ditemukan")

    def navigate_via_next_node_label(self):
        # Balik ke level Transition dulu dari Condition
        try:
            transition_link = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[normalize-space(text())='Transition']")
            ))
            self.safe_click(transition_link)
            self.wait_for_page_stable(2)
            print("   ✅ Kembali ke Transition")
        except:
            pass

        # Klik label Next Node yang zoomable
        label = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'idempiere-zoomable-label') and @title='Next Node in workflow']")
        ))
        self.safe_click(label)
        self.wait_for_page_stable(3)
        print("   ✅ Navigate via Next Node label")

    def click_transition_tab(self):
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Transition']")
        ))
        self.safe_click(tab)
        self.wait_for_page_stable(2)
        print("   ✅ Tab Transition diklik")

    def click_condition_tab(self):
        # Ambil semua tab Condition yang ada, pilih yang terakhir (nested dalam Transition)
        tabs = self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Condition']")
        ))
        
        # Klik tab Condition yang terakhir (nested di Transition)
        target_tab = tabs[-1]
        self.safe_click(target_tab)
        self.wait_for_page_stable(2)
        print("   ✅ Tab Condition diklik")

    def click_new_transition(self):
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SHIFT + Keys.ALT + 'n')
        self.wait_for_page_stable(2)
        print("   ✅ New transition (Shift+Alt+N)")

    def fill_next_node(self, value):
        self.wait_for_page_stable(3)

        # Scroll ke atas dulu
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Cari SEMUA Next Node input, ambil yang visible dan punya size
        fields = self.driver.find_elements(
            By.XPATH, "//span[@title='Next Node in workflow']/ancestor::tr//input[contains(@class,'z-combobox-input')]"
        )

        next_node_field = None
        for f in fields:
            try:
                if f.is_displayed() and f.is_enabled() and f.size['width'] > 0:
                    next_node_field = f
                    # Ambil yang TERAKHIR (paling baru di DOM)
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

        value_textarea = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']")
        ))
        self.wait_for_page_stable(1)

        # Fill Column
        all_combos = self.driver.find_elements(
            By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']/ancestor::*[5]//input[contains(@class,'z-combobox-input')]"
        )
        enabled_combos = [c for c in all_combos if c.is_enabled() and c.is_displayed() and c.size['width'] > 0]
        col_field = enabled_combos[1]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", col_field)
        time.sleep(1)
        ActionChains(self.driver).move_to_element(col_field).click().send_keys(column_value).perform()
        self.wait_for_page_stable(2)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self.wait_for_page_stable(2)
        print(f"   Column: {column_value}")

        # Tab ke Operator — active element pasti Operator setelah Tab
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(1.5)

        # Ambil active element ID (fresh, tidak stale)
        active_el = self.driver.switch_to.active_element
        active_id = active_el.get_attribute('id')

        # Cari dropdown button adjacent ke active element
        op_btn = self.driver.find_element(
            By.XPATH, f"//input[@id='{active_id}']/following-sibling::a[contains(@class,'z-combobox-button')]"
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", op_btn)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", op_btn)
        self.wait_for_page_stable(1)

        # Klik item pertama di popup (yaitu "=")
        item = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'z-combobox-popup')]//li[contains(@class,'z-comboitem')][1]")
        ))
        self.driver.execute_script("arguments[0].click();", item)
        self.wait_for_page_stable(1)
        print(f"   Operator: =")

        # Fill Value
        value_textarea = self.driver.find_element(
            By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']"
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", value_textarea)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", value_textarea)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].value = '';", value_textarea)
        self.driver.execute_script(f"arguments[0].value = '{cond_value}';", value_textarea)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", value_textarea)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", value_textarea)
        self.driver.execute_script("arguments[0].blur();", value_textarea)
        time.sleep(1)
        print(f"   Value: {cond_value}")
        
    def save(self):
        save_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Save24.png')]/..")
        ))
        self.safe_click(save_btn)
        self.wait_for_page_stable(2)
        print("   ✅ Disimpan")

    def process_pga_chain(self, full_name, csv_value):
        chain = [
            ("(Mapping PGA GM)",                         f"(Approval PGA GM {full_name})"),
            (f"(Approval PGA GM {full_name})",            "(Mapping PGA Deputy BU Head)"),
            ("(Mapping PGA Deputy BU Head)",              f"(Approval PGA Dep BU Head {full_name})"),
            (f"(Approval PGA Dep BU Head {full_name})",   "(Mapping PGA BU Head)"),
            ("(Mapping PGA BU Head)",                     f"(Approval PGA BU Head {full_name})"),
            (f"(Approval PGA BU Head {full_name})",       "(Mapping PGA HOO)"),
            ("(Mapping PGA HOO)",                         f"(Approval PGA HOO {full_name})"),
            (f"(Approval PGA HOO {full_name})",           "(Mapping PGA Division Head)"),
            ("(Mapping PGA Division Head)",               f"(Approval PGA Div Head {full_name})"),
            (f"(Approval PGA Div Head {full_name})",      "(DocComplete)"),
        ]

        print(f"\n--- PGA Chain [{full_name}] ---")

        # Search HANYA untuk node pertama
        self.go_to_node(chain[0][0])

        for i, (from_node, to_node) in enumerate(chain):
            print(f"\n   [{i+1}/{len(chain)}] {from_node} → {to_node}")
            self.click_transition_tab()
            self.click_new_transition()
            self.fill_next_node(to_node)
            self.fill_condition("User1_ID_Cost Center", "=", csv_value)
            self.save()

            # Navigate ke next node via label (kecuali step terakhir)
            if i < len(chain) - 1:
                self.navigate_via_next_node_label()

    def process_legal_chain(self, full_name, csv_value):
        chain = [
            ("(Mapping Legal)",                              f"(Approval Head Legal {full_name})"),
            (f"(Approval Head Legal {full_name})",            "(Mapping Legal GM)"),
            ("(Mapping Legal GM)",                           f"(Approval Legal GM {full_name})"),
            (f"(Approval Legal GM {full_name})",              "(Mapping Legal Deputy BU Head)"),
            ("(Mapping Legal Deputy BU Head)",               f"(Approval Legal Dep BU Head {full_name})"),
            (f"(Approval Legal Dep BU Head {full_name})",     "(Mapping Legal BU Head)"),
            ("(Mapping Legal BU Head)",                      f"(Approval Legal BU Head {full_name})"),
            (f"(Approval Legal BU Head {full_name})",         "(Mapping Legal HOO)"),
            ("(Mapping Legal HOO)",                          f"(Approval Legal HOO {full_name})"),
            (f"(Approval Legal HOO {full_name})",             "(Mapping Legal Division Head)"),
            ("(Mapping Legal Division Head)",                f"(Approval Legal Div Head {full_name})"),
            (f"(Approval Legal Div Head {full_name})",        "(DocComplete)"),
        ]

        print(f"\n--- Legal Chain [{full_name}] ---")

        # Search HANYA untuk node pertama
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