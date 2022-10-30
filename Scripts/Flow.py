import dearpygui.dearpygui as dpg
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from Ki import Ki
from Ki import Preset
import json
import DoordashUtil
import os


def save_account_path():
    global account_path
    account_path = dpg.get_value(SAVED_ACCOUNT_PATH)
    if (not account_path.endswith("info.txt")):
        if (not account_path.endswith('/')):
            account_path += "/"
        account_path += "info.txt"
    account_path = account_path.replace("\\", "/")
    dpg.set_value(SAVED_ACCOUNT_PATH, account_path)
    # Update Path Info
    f = open(PATH_PATH, "wt")
    f.write(account_path)
    f.close()
    # Create txt at Account Path
    f = open(account_path, "at")
    f.close()


def create_major_node():
    global major_node
    global placed_nodes
    global amount_node
    # First Run
    if (major_node == None):
        major_node = dpg.add_input_text(
            hint="Enter Item", parent=preset_order_group, indent=0)
        placed_nodes.append(major_node)
        return
    # Compile Composite Order
    major_node = dpg.add_input_text(
        hint="Enter Item", parent=preset_order_group, indent=0)
    placed_nodes.append(major_node)
    amount_node = None


def create_minor_node():
    global placed_nodes
    if (major_node == None):
        return
    placed_nodes.append(dpg.add_input_text(hint="Enter Topping",
                                           parent=preset_order_group, indent=25))


def create_amount_node():
    global placed_nodes
    global amount_node
    if (major_node == None or amount_node != None):
        return
    amount_node = dpg.add_slider_int(
        indent=50, clamped=True, default_value=1, min_value=1, max_value=10, parent=preset_order_group)
    placed_nodes.append(amount_node)


def delete_previous_node():
    global placed_nodes
    global major_node
    global amount_node

    if (len(placed_nodes) <= 0):
        major_node = None
        return
    index = len(placed_nodes) - 1
    deleting_node = placed_nodes[index]
    del placed_nodes[index]
    dpg.delete_item(deleting_node)
    if (amount_node == deleting_node):
        amount_node = None
        return

    if (len(placed_nodes) <= 0):
        major_node = None


def save_preset():
    # Input Check
    if (len(str.strip(dpg.get_value(name_node))) == 0 or len(str.strip(dpg.get_value(url_node))) == 0):
        return

    # Initialize Node Sets
    index = 0
    major_node: str = ""
    minor_nodes: list[str] = []
    orders: list = []
    while (index < len(placed_nodes)):
        indent = dpg.get_item_indent(placed_nodes[index])
        node = str(dpg.get_value(placed_nodes[index]))

        if (len(node) == 0):
            return

        if (indent == 0):
            if (len(major_node) != 0):
                ki = Ki(major_node, minor_nodes)
                orders.append(ki)
            minor_nodes = []
            major_node = node
        else:
            minor_nodes.append(node)

        if (index + 1 >= len(placed_nodes)):
            ki = Ki(major_node, minor_nodes)
            orders.append(ki)
        index += 1

    # Create Preset
    if (not os.path.exists(PRESETS_FOLDER_PATH + str(dpg.get_value(name_node)) + ".json")):
        dpg.add_button(label=str(dpg.get_value(name_node)), callback=lambda: start_automation(
            str(dpg.get_value(name_node))), width=150, height=50, parent=preset_group)

    # Save JSON to File
    preset = Preset(dpg.get_value(url_node), orders)
    data = preset.create_json()
    f = open(PRESETS_FOLDER_PATH +
             str(dpg.get_value(name_node) + ".json"), "wt")
    f.write(data)
    f.close()

    # Clear Interface
    dpg.set_value(name_node, '')
    dpg.set_value(url_node, '')
    while (len(placed_nodes) > 0):
        delete_previous_node()


def execute():
    # Retrieve Account Info
    f = open(dpg.get_value(SAVED_ACCOUNT_PATH), 'rt')
    gmail = f.readline().strip()
    password = f.readline().strip()
    f.close()

    # Retrieve JSON Data
    f = open(PRESETS_FOLDER_PATH +
             str(dpg.get_value("Execute Name")) + ".json", "rt")
    data = json.load(f)

    # Navigate to Doordash
    driver = webdriver.Firefox()
    driver.get("https://identity.doordash.com/auth?client_id=1666519390426295040&enable_last_social=false&intl=en-US&layout=consumer_web&prompt=none&redirect_uri=https%3A%2F%2Fwww.doordash.com%2Fpost-login%2F&response_type=code&scope=%2A&state=%2Fhome%2F%7C%7Cc9f7fe06-01b5-44ff-9943-fe2678d290ea&_ga=2.20327291.258091593.1663907403-1076543356.1663907402")
    time.sleep(3)

    # Email Input
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID,
             "FieldWrapper-0")
        )
    )
    elem.send_keys(gmail)

    # Password Input
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID,
             "FieldWrapper-1")
        )
    )
    elem.send_keys(password)

    # Sign in Button
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID,
             "login-submit-button")
        )
    )
    elem.click()

    # Navigate to Restaurant
    time.sleep(3)
    driver.get(data["url"])
    time.sleep(3)

    # Order Loop
    for order in data["orders"]:
        time.sleep(2)
        DoordashUtil.search_click_button(driver, order["item"])
        time.sleep(1)
        for topping in order["toppings"]:
            try:
                x = int(topping)
                for i in range(x-1):
                    DoordashUtil.define_click_button(
                        driver, "aria-label", "Increase quantity by 1")
            except:
                DoordashUtil.search_click_checkbox(driver, topping)
        DoordashUtil.search_click_button(driver, "Add to cart")
    time.sleep(2)
    DoordashUtil.define_click_link(driver, "data-anchor-id", "CheckoutButton")


def start_automation(preset_name: str):
    # Retrieve Account Info
    f = open(dpg.get_value(SAVED_ACCOUNT_PATH), 'rt')
    gmail = f.readline().strip()
    password = f.readline().strip()
    f.close()

    # Retrieve JSON Data
    f = open(PRESETS_FOLDER_PATH +
             preset_name + ".json", "rt")
    data = json.load(f)

    # Navigate to Doordash
    driver = webdriver.Firefox()
    driver.get("https://identity.doordash.com/auth?client_id=1666519390426295040&enable_last_social=false&intl=en-US&layout=consumer_web&prompt=none&redirect_uri=https%3A%2F%2Fwww.doordash.com%2Fpost-login%2F&response_type=code&scope=%2A&state=%2Fhome%2F%7C%7Cc9f7fe06-01b5-44ff-9943-fe2678d290ea&_ga=2.20327291.258091593.1663907403-1076543356.1663907402")
    time.sleep(3)

    # Email Input
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID,
             "FieldWrapper-0")
        )
    )
    elem.send_keys(gmail)

    # Password Input
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID,
             "FieldWrapper-1")
        )
    )
    elem.send_keys(password)

    # Sign in Button
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID,
             "login-submit-button")
        )
    )
    elem.click()

    # Navigate to Restaurant
    time.sleep(3)
    driver.get(data["url"])
    time.sleep(3)

    # Order Loop
    for order in data["orders"]:
        time.sleep(2)
        DoordashUtil.search_click_button(driver, order["item"])
        time.sleep(1)
        for topping in order["toppings"]:
            try:
                x = int(topping)
                for i in range(x-1):
                    DoordashUtil.define_click_button(
                        driver, "aria-label", "Increase quantity by 1")
            except:
                DoordashUtil.search_click_checkbox(driver, topping)
        DoordashUtil.search_click_button(driver, "Add to cart")
    time.sleep(2)
    DoordashUtil.define_click_link(driver, "data-anchor-id", "CheckoutButton")


def show_execute_window():
    with dpg.window(label="Execute", width=400, height=300, pos=[400, 400]):
        dpg.add_input_text(tag="Execute Name")
        dpg.add_button(label="Execute", callback=execute)


dpg.create_context()
dpg.create_viewport(title="KiFlow")
dpg.setup_dearpygui()

# Global Variables
SAVED_ACCOUNT_PATH = dpg.generate_uuid()
PATH_PATH = "./Saved/path/info.txt"
PRESETS_FOLDER_PATH = "./Saved/presets/"
account_path = ""
url_node = dpg.generate_uuid()
name_node = dpg.generate_uuid()
preset_order_group: int | str = None
major_node: int | str = None
placed_nodes: list[int | str] = []
amount_node: int | str = None
preset_group: int | str = None

# Menu Bar
with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Quit")
    with dpg.menu(label="Window"):
        dpg.add_menu_item(label="Execute", callback=show_execute_window)

# Windows
with dpg.window(label="Account", width=600, height=300, no_close=True, pos=[524, 0], no_move=True, autosize=True):
    f = open(PATH_PATH, "rt")
    account_path = f.readline()
    with dpg.group(horizontal=True, horizontal_spacing=5):
        dpg.add_text("Path")
        dpg.add_input_text(default_value=account_path,
                           tag=SAVED_ACCOUNT_PATH, width=450)
    dpg.add_button(label="Save", callback=save_account_path)
    f.close()

with dpg.window(label="Configuration", width=400, height=300, pos=[166, 0], no_close=True, autosize=True, no_move=True):
    with dpg.group(horizontal=True, horizontal_spacing=5):
        dpg.add_text("Name")
        dpg.add_input_text(tag=name_node)

    with dpg.group(horizontal=True, horizontal_spacing=12):
        dpg.add_text("URL")
        dpg.add_input_text(tag=url_node)

    button_group = dpg.add_group(horizontal=True, horizontal_spacing=10)
    dpg.add_button(label="Add Item", parent=button_group,
                   callback=create_major_node)
    dpg.add_button(label="Add Topping", parent=button_group,
                   callback=create_minor_node)
    dpg.add_button(label="Add Amount", parent=button_group,
                   callback=create_amount_node)
    dpg.add_button(label="Delete Node", parent=button_group,
                   callback=delete_previous_node)

    preset_order_group = dpg.add_group()
    dpg.add_text("Orders", parent=preset_order_group)

    dpg.add_button(label="Save", callback=save_preset)

with dpg.window(label="Presets", width=167, height=300, pos=[0, 0], autosize=True, no_close=True, no_move=True):
    preset_group = dpg.add_group()
    for file in os.scandir(PRESETS_FOLDER_PATH):
        if (file.is_file()):
            filename = file.name.replace(".json", '')
            dpg.add_button(label=filename, callback=lambda: start_automation(
                filename), width=150, height=50, parent=preset_group)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
