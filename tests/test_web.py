import os
import pytest
# import pyautogui
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = Options()
chrome_options.add_argument("--headless")

zebrate_url = "https://zebrate.herokuapp.com/"
# zebrate_url = "http://localhost:8501/"
horse_url = "https://media.istockphoto.com/photos/wild-horses-running-free-picture-id1019461046?k=6&m=1019461046&s=612x612&w=0&h=RN04ILkViwine-g3B9BjtUmGV_mucSiQgv8mKM-F644="


def test_put_image_link():
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(zebrate_url)
    sleep(5)
    link_inputer = driver.find_element(By.TAG_NAME, 'input')
    link_inputer.send_keys(horse_url)  # заполнить
    link_inputer.send_keys(Keys.RETURN)  # отправить
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(5)
    driver.close()


# def test_send_image_file():
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     driver.get(zebrate_url)
#     sleep(5)
#     upload_file = driver.find_element(By.XPATH, '//button[text()="Browse files"]')
#     # upload_file.send_keys(os.getcwd() + "/big_horse.jpeg")
#     upload_file.click()
#     pyautogui.write(os.getcwd() + "/big_horse.jpeg", interval=0.25)
#     pyautogui.press('return')
#     sleep(5)
#     driver.close()
#
#
# def test_download_tensor():
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     driver.get(zebrate_url)
#     sleep(5)
#     tensor_checkbox = driver.find_element(By.XPATH, '//*[text()="Show me the horse tensor"]')
#     tensor_checkbox.click()
#     sleep(15)
#     download_tensor = driver.find_element(By.XPATH, '//*[text()="Download tensor"]')
#     download_tensor.click()
#     sleep(5)
#     driver.close()
#
#
# def test_download_horse():
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     driver.get(zebrate_url)
#     sleep(5)
#     download_horse_image = driver.find_element(By.XPATH, '//*[text()="Download horse"]')
#     download_horse_image.click()
#     sleep(5)
#     driver.close()
#
#
# def test_download_zebra():
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     driver.get(zebrate_url)
#     sleep(10)
#     download_zebra_image = driver.find_element(By.XPATH, '//*[text()="Download zebra"]')
#     download_zebra_image.click()
#     sleep(5)
#     driver.close()
#
#
# def test_fullscreen_zebra():
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     driver.set_window_size(1600, 900)
#     driver.get(zebrate_url)
#     sleep(10)
#     fullscreen_zebra_image = driver.find_elements(By.XPATH, '//*[@title="fullscreen-enter"]')[1]
#     fullscreen_zebra_image.click()
#     sleep(10)
#     driver.close()
#
#
# def test_rerun_neural_network():
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     driver.get(zebrate_url)
#     sleep(5)
#     btn = driver.find_element(By.ID, 'MainMenuButton')
#     btn.click()
#     btn_rerun = driver.find_element(By.XPATH, '//span[text()="Rerun"]')
#     btn_rerun.click()
#     sleep(5)
#     driver.close()
