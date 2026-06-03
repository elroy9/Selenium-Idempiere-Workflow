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
        """Hanya dipakai untuk node PERTAMA di chain"""
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

        # Isi field Name di dialog — ambil index ke-2 (Name, bukan Description)
        name_inputs = self.wait_long.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class,'z-window')]//input[contains(@class,'z-textbox')]")
        ))
        # Name field biasanya index ke-2 (0=Doc No, 1=Search Key, 2=Name)
        name_field = name_inputs[2] if len(name_inputs) > 2 else name_inputs[0]
        name_field.clear()
        name_field.send_keys(node_name)
        self.wait_for_page_stable(1)
        name_field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(3)
        print(f"   ✅ Node '{node_name}' ditemukan")

    def navigate_via_next_node_label(self):
        """Klik label 'Next Node' (zoomable) untuk navigate ke node berikutnya"""
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
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Condition']")
        ))
        self.safe_click(tab)
        self.wait_for_page_stable(2)

    def click_new_transition(self):
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SHIFT + Keys.ALT + 'n')
        self.wait_for_page_stable(2)
        print("   ✅ New transition (Shift+Alt+N)")

    def fill_next_node(self, value):
        self.wait_for_page_stable(2)

        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[@title='Next Node in workflow']/ancestor::tr//input[contains(@class,'z-combobox-input')]")
        ))

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)
        time.sleep(0.5)

        # Native click agar keyboard focus benar-benar berpindah
        try:
            field.click()
        except:
            self.driver.execute_script("arguments[0].click();", field)
        time.sleep(1)

        field.send_keys(value)
        self.wait_for_page_stable(2)
        field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(1)
        print(f"   Next Node: {value}")

    def fill_condition(self, column_value, op_value, cond_value):
        self.click_condition_tab()
        self.wait_for_page_stable(1)

        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SHIFT + Keys.ALT + 'n')
        self.wait_for_page_stable(2)

        value_textarea = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']")
        ))

        all_combos = self.driver.find_elements(
            By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']/ancestor::*[5]//input[contains(@class,'z-combobox-input')]"
        )
        enabled_combos = [c for c in all_combos if c.is_enabled()]

        # Fill Column (index 1)
        col_field = enabled_combos[1]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", col_field)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", col_field)
        time.sleep(1)
        col_field.send_keys(column_value)
        self.wait_for_page_stable(2)
        col_field.send_keys(Keys.ENTER)
        self.wait_for_page_stable(1)
        print(f"   Column: {column_value}")

        # Fill Operator (index 2) — klik dropdown button lalu pilih "="
        op_field = enabled_combos[2]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", op_field)
        time.sleep(0.5)
        op_btn = self.driver.find_element(
            By.XPATH, f"//input[@id='{op_field.get_attribute('id')}']/following-sibling::a[contains(@class,'z-combobox-button')]"
        )
        self.driver.execute_script("arguments[0].click();", op_btn)
        self.wait_for_page_stable(1)
        item = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//li[contains(@class,'z-comboitem')]//span[contains(@class,'z-comboitem-text') and contains(text(),'=')]")
        ))
        self.driver.execute_script("arguments[0].click();", item)
        self.wait_for_page_stable(1)
        print(f"   Operator: =")

        # Fill Value
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", value_textarea)
        time.sleep(0.5)
        value_textarea.clear()
        value_textarea.send_keys(str(cond_value))
        self.wait_for_page_stable(1)
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