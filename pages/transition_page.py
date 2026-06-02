from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TransitionPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def search_node(self, name):
        find_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Find24.png')]/..")
        ))
        find_btn.click()
        time.sleep(2)

        name_field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class,'idempiere-label') and normalize-space(text())='Name']/ancestor::tr//input[contains(@class,'z-textbox')]")
        ))
        name_field.clear()
        name_field.send_keys(name)
        name_field.send_keys(Keys.ENTER)
        time.sleep(2)
        print(f"✅ Node '{name}' dicari")

    def click_transition_tab(self):
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Transition']")
        ))
        tab.click()
        time.sleep(1)

    def click_condition_tab(self):
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Condition']")
        ))
        tab.click()
        time.sleep(1)

    def click_new(self):
        new_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'New24.png')]/..")
        ))
        new_btn.click()
        time.sleep(2)

    def fill_next_node(self, value):
        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[@title='Next Node in workflow']/ancestor::tr//input[contains(@class,'z-combobox-input')]")
        ))
        self.driver.execute_script("arguments[0].click();", field)
        time.sleep(1)
        self.driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(value)
        time.sleep(2)
        field.send_keys(Keys.ENTER)
        time.sleep(1)
        print(f"   Next Node: {value}")

    def fill_condition(self, column_value, op_value, cond_value):
        self.click_condition_tab()
        time.sleep(1)

        # Anchor: Value textarea (reliable selector)
        value_textarea = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//textarea[@instancename='AD_WF_NextCondition0Value']")
        ))

        # Cari Column & Operator combobox dalam section yang sama
        combos = value_textarea.find_elements(By.XPATH,
            "ancestor::table//input[contains(@class,'z-combobox-input')]"
        )

        if len(combos) >= 2:
            # Fill Column
            col_field = combos[0]
            self.driver.execute_script("arguments[0].click();", col_field)
            time.sleep(1)
            col_field.send_keys(column_value)
            time.sleep(2)
            col_field.send_keys(Keys.ENTER)
            time.sleep(1)
            print(f"   Column: {column_value}")

            # Fill Operator
            op_field = combos[1]
            self.driver.execute_script("arguments[0].click();", op_field)
            time.sleep(1)
            op_field.send_keys(op_value)
            time.sleep(2)
            op_field.send_keys(Keys.ENTER)
            time.sleep(1)
            print(f"   Operator: {op_value}")

        # Fill Value
        value_textarea.clear()
        value_textarea.send_keys(str(cond_value))
        time.sleep(1)
        print(f"   Value: {cond_value}")

    def click_parent_record(self):
        link = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space(text())='Transition']")
        ))
        link.click()
        time.sleep(2)

    def navigate_to_next_node(self):
        label = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[@title='Next Node in workflow' and contains(@class,'idempiere-zoomable-label')]")
        ))
        label.click()
        time.sleep(2)

    def save(self):
        save_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Save24.png')]/..")
        ))
        save_btn.click()
        time.sleep(2)
        print("✅ Disimpan")

    def add_transition_with_condition(self, next_node, csv_value):
        self.click_transition_tab()
        time.sleep(1)
        self.click_new()
        self.fill_next_node(next_node)
        self.fill_condition("User1_ID_Cost Center", "=", csv_value)
        self.click_parent_record()

    def process_pga_chain(self, full_name, csv_value):
        chain = [
            ("Mapping PGA GM",                         f"(Approval PGA GM {full_name})"),
            (f"(Approval PGA GM {full_name})",          "Mapping PGA Deputy BU Head"),
            ("Mapping PGA Deputy BU Head",              f"(Approval PGA Dep BU Head {full_name})"),
            (f"(Approval PGA Dep BU Head {full_name})", "Mapping PGA BU Head"),
            ("Mapping PGA BU Head",                     f"(Approval PGA BU Head {full_name})"),
            (f"(Approval PGA BU Head {full_name})",     "Mapping PGA HOO"),
            ("Mapping PGA HOO",                         f"(Approval PGA HOO {full_name})"),
            (f"(Approval PGA HOO {full_name})",         "Mapping PGA Division Head"),
            ("Mapping PGA Division Head",               f"(Approval PGA Div Head {full_name})"),
            (f"(Approval PGA Div Head {full_name})",    "(DocComplete)"),
        ]

        print(f"\n--- PGA Chain [{full_name}] ---")
        self.search_node("Mapping PGA GM")
        time.sleep(2)

        for i, (from_node, to_node) in enumerate(chain):
            print(f"\n   [{i+1}/{len(chain)}] {from_node} → {to_node}")
            self.add_transition_with_condition(to_node, csv_value)
            if i < len(chain) - 1:
                self.navigate_to_next_node()
                time.sleep(1)

        self.save()

    def process_legal_chain(self, full_name, csv_value):
        chain = [
            ("Mapping Legal",                              f"(Approval Head Legal {full_name})"),
            (f"(Approval Head Legal {full_name})",          "Mapping Legal GM"),
            ("Mapping Legal GM",                           f"(Approval Legal GM {full_name})"),
            (f"(Approval Legal GM {full_name})",            "Mapping Legal Deputy BU Head"),
            ("Mapping Legal Deputy BU Head",               f"(Approval Legal Dep BU Head {full_name})"),
            (f"(Approval Legal Dep BU Head {full_name})",   "Mapping Legal BU Head"),
            ("Mapping Legal BU Head",                      f"(Approval Legal BU Head {full_name})"),
            (f"(Approval Legal BU Head {full_name})",       "Mapping Legal HOO"),
            ("Mapping Legal HOO",                          f"(Approval Legal HOO {full_name})"),
            (f"(Approval Legal HOO {full_name})",           "Mapping Legal Division Head"),
            ("Mapping Legal Division Head",                f"(Approval Legal Div Head {full_name})"),
            (f"(Approval Legal Div Head {full_name})",      "(DocComplete)"),
        ]

        print(f"\n--- Legal Chain [{full_name}] ---")
        self.search_node("Mapping Legal")
        time.sleep(2)

        for i, (from_node, to_node) in enumerate(chain):
            print(f"\n   [{i+1}/{len(chain)}] {from_node} → {to_node}")
            self.add_transition_with_condition(to_node, csv_value)
            if i < len(chain) - 1:
                self.navigate_to_next_node()
                time.sleep(1)

        self.save()