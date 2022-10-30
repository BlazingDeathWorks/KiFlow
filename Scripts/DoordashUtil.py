from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def define_click_link(driver: webdriver, attribute: str, content: str):
    elems = driver.find_elements(By.TAG_NAME, "a")
    attribute += "=\""
    for i in range(len(elems)):
        elem = elems[i]
        # Disect Outer HTML
        outer_html = elem.get_attribute("outerHTML")
        start = outer_html.find(attribute) + len(attribute)
        end = outer_html.find("\"", start)
        content_html = outer_html[start:end]

        if ((content not in content_html)):
            continue

        # Click Button
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        elem.click()
        return


def define_send_input(driver: webdriver, attribute: str, content: str, input: str, clear: bool = True):
    elems = driver.find_elements(By.TAG_NAME, "input")
    attribute += "=\""
    for i in range(len(elems)):
        elem = elems[i]
        # Disect Outer HTML
        outer_html = elem.get_attribute("outerHTML")
        start = outer_html.find(attribute) + len(attribute)
        end = outer_html.find("\"", start)
        content_html = outer_html[start:end]

        if ((content not in content_html)):
            continue

        # Click Button
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        if (clear):
            elem.clear()
        elem.send_keys(input)
        return


def define_click_button(driver: webdriver, attribute: str, content: str):
    elems = driver.find_elements(By.TAG_NAME, "button")
    attribute += "=\""
    for i in range(len(elems)):
        elem = elems[i]
        # Disect Outer HTML
        outer_html = elem.get_attribute("outerHTML")
        start = outer_html.find(attribute) + len(attribute)
        end = outer_html.find("\"", start)
        content_html = outer_html[start:end]

        if ((content not in content_html)):
            continue

        # Click Button
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        elem.click()
        return


def search_click_button(driver: webdriver, label: str, sec: float = 0.0):
    elems = driver.find_elements(By.TAG_NAME, "button")
    elem = None
    for i in range(len(elems)):
        if (label in elems[i].text):
            elem = elems[i]
            break
    if (elem != None):
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        time.sleep(sec)
        elem.click()


def search_click_checkbox(driver: webdriver, label: str):
    elems = driver.find_elements(By.TAG_NAME, "label")
    for i in range(len(elems)):
        elem = elems[i]
        # # Contains
        # if ((not exact) and (label in elem.text)):
        #     # Disect Outer HTML
        #     outer_html = elem.get_attribute("outerHTML")
        #     start = outer_html.find("\"")
        #     end = outer_html.find("\"", start + 1)
        #     id = outer_html[start+1:end]

        #     # Get Button
        #     elem = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located(
        #             (By.ID,
        #              id)
        #         )
        #     )
        #     driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        #     if (elem.is_selected()):
        #         return
        #     elem.click()
        #     return
        # Starts with
        if (elem.text.startswith(label)):
            # Disect Outer HTML
            outer_html = elem.get_attribute("outerHTML")
            start = outer_html.find("\"")
            end = outer_html.find("\"", start + 1)
            id = outer_html[start+1:end]

            # Get Button
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID,
                     id)
                )
            )
            driver.execute_script("arguments[0].scrollIntoView(false);", elem)
            if (elem.is_selected()):
                return
            elem.click()
            return
