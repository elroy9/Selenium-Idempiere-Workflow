from utils.driver_setup import get_driver
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pages.node_page import NodePage
from selenium.webdriver.common.by import By
import time

driver = get_driver()
login = LoginPage(driver)
workflow = WorkflowPage(driver)
node = NodePage(driver)

try:
    login.open()
    time.sleep(2)
    login.input_username("elroy.juwono")
    login.input_password("elroy.juwono")
    login.check_select_role()
    login.click_ok()
    time.sleep(2)
    login.select_client_and_role("920", "FICO Team Admin")
    time.sleep(4)
    workflow.search_menu("Workflow")
    time.sleep(3)
    workflow.click_search_button()
    time.sleep(2)
    workflow.fill_search_key("%Workflow PPBP%")
    time.sleep(3)
    node.click_node_tab()
    node.click_new()
    time.sleep(2)
    node.fill_search_key("(TEST)")
    node.fill_name("(TEST)")
    time.sleep(1)

    # Cari label Workflow Responsible lalu print outer HTML parent-parentnya
    label = driver.find_element(By.XPATH, 
        "//span[contains(@class,'idempiere-label') and text()='Workflow Responsible']")
    
    # Print struktur ancestor level 1-5
    for level in range(1, 6):
        ancestor_xpath = f"ancestor::*[{level}]"
        ancestor = label.find_element(By.XPATH, ancestor_xpath)
        print(f"\n=== ANCESTOR LEVEL {level} ===")
        print(f"tag: {ancestor.tag_name} | class: {ancestor.get_attribute('class')}")
        # Cari combobox di dalam ancestor ini
        combos = ancestor.find_elements(By.XPATH, ".//input[contains(@class,'z-combobox-input')]")
        print(f"combobox ditemukan di level ini: {len(combos)}")

    input("\nTekan Enter untuk tutup...")

finally:
    driver.quit()