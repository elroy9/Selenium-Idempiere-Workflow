from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.csv_helper import parse_cost_center
import time


class NodePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def click_node_tab(self):
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'z-tab-text') and normalize-space(text())='Node']")
        ))
        tab.click()
        time.sleep(2)
        print("✅ Tab Node diklik")

    def click_new(self):
        new_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'New24.png')]/..")
        ))
        new_btn.click()
        time.sleep(2)
        print("✅ Tombol New diklik")

    def fill_search_key(self, value):
        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@instancename='AD_WF_Node0Value']")
        ))
        field.clear()
        field.send_keys(value)
        time.sleep(1)
        print(f"   Search Key: {value}")

    def fill_name(self, value):
        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@instancename='AD_WF_Node0Name']")
        ))
        field.clear()
        field.send_keys(value)
        time.sleep(1)
        self.driver.execute_script("document.activeElement.blur();")
        time.sleep(2)
        print(f"   Name: {value}")

    def fill_combobox_by_label(self, label_text, value):
        field = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//span[contains(@class,'idempiere-label') and text()='{label_text}']/ancestor::tr//input[contains(@class,'z-combobox-input')]")
        ))

        self.driver.execute_script("arguments[0].click();", field)
        time.sleep(1)
        self.driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(value)
        time.sleep(2)  # Tunggu suggestion muncul

        # Tekan Enter untuk pilih suggestion pertama
        field.send_keys(Keys.ENTER)
        time.sleep(1)
        print(f"   {label_text}: {value}")

    def fill_workflow_responsible(self, value):
        time.sleep(1)
        self.fill_combobox_by_label("Workflow Responsible", value)
        
    def fill_action(self, value="User Choice"):
        self.fill_combobox_by_label("Action", value)
        time.sleep(3)

    def fill_column(self, value="IsApproved_Approved"):
        self.fill_combobox_by_label("Column", value)

    def save_node(self):
        save_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'Save24.png')]/..")
        ))
        save_btn.click()
        time.sleep(2)
        print("   ✅ Node disimpan")

    def create_node(self, search_key, name, wf_responsible):
        self.click_new()
        self.fill_search_key(search_key)
        self.fill_name(name)
        self.fill_workflow_responsible(wf_responsible)
        self.fill_action("User Choice")
        self.fill_column("IsApproved_Approved")
        self.save_node()
        print(f"   ✅ Node selesai dibuat")

    def create_nodes_from_row(self, row):
        cost_center = row['COST CENTER']
        full_name, abbrev = parse_cost_center(cost_center)

        print(f"\n{'='*50}")
        print(f"Cost Center : {cost_center}")
        print(f"Full Name   : {full_name}")
        print(f"Abbrev      : {abbrev}")
        print(f"{'='*50}")

        pga_nodes = [
            {
                "search_key": f"(Approval PGA GM {abbrev})",
                "name": f"(Approval PGA GM {full_name})",
                "wf_responsible": f"GM {full_name} PPBP"
            },
            {
                "search_key": f"(Approval PGA Dep BU Head {abbrev})",
                "name": f"(Approval PGA Dep BU Head {full_name})",
                "wf_responsible": f"Deputy BU Head {full_name} PPBP"
            },
            {
                "search_key": f"(Approval PGA BU Head {abbrev})",
                "name": f"(Approval PGA BU Head {full_name})",
                "wf_responsible": f"BU Head {full_name} PPBP"
            },
            {
                "search_key": f"(Approval PGA HOO {abbrev})",
                "name": f"(Approval PGA HOO {full_name})",
                "wf_responsible": f"HOO {full_name} PPBP"
            },
            {
                "search_key": f"(Approval PGA Div Head {abbrev})",
                "name": f"(Approval PGA Div Head {full_name})",
                "wf_responsible": f"Division Head {full_name} PPBP"
            },
        ]

        legal_nodes = [
            {
                "search_key": f"(Approval Head Legal {abbrev})",
                "name": f"(Approval Head Legal {full_name})",
                "wf_responsible": f"Head Legal {full_name} PPBP"
            },
            {
                "search_key": f"(Approval Legal GM {abbrev})",
                "name": f"(Approval Legal GM {full_name})",
                "wf_responsible": f"GM {full_name} PPBP"
            },
            {
                "search_key": f"(Approval Legal Dep BU Head {abbrev})",
                "name": f"(Approval Legal Dep BU Head {full_name})",
                "wf_responsible": f"Deputy BU Head {full_name} PPBP"
            },
            {
                "search_key": f"(Approval Legal BU Head {abbrev})",
                "name": f"(Approval Legal BU Head {full_name})",
                "wf_responsible": f"BU Head {full_name} PPBP"
            },
            {
                "search_key": f"(Approval Legal HOO {abbrev})",
                "name": f"(Approval Legal HOO {full_name})",
                "wf_responsible": f"HOO {full_name} PPBP"
            },
            {
                "search_key": f"(Approval Legal Div Head {abbrev})",
                "name": f"(Approval Legal Div Head {full_name})",
                "wf_responsible": f"Division Head {full_name} PPBP"
            },
        ]

        print("\n--- Membuat PGA Nodes ---")
        for node in pga_nodes:
            print(f"\n📌 {node['name']}")
            self.create_node(node['search_key'], node['name'], node['wf_responsible'])

        print("\n--- Membuat Legal Nodes ---")
        for node in legal_nodes:
            print(f"\n📌 {node['name']}")
            self.create_node(node['search_key'], node['name'], node['wf_responsible'])