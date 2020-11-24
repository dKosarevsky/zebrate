import pytest
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# zebrate_url = "https://zebrate.herokuapp.com/"
zebrate_url = "http://localhost:8501/"
horse_url = "https://media.istockphoto.com/photos/wild-horses-running-free-picture-id1019461046?k=6&m=1019461046&s=612x612&w=0&h=RN04ILkViwine-g3B9BjtUmGV_mucSiQgv8mKM-F644="
driver_location = "/home/if/bmstu/011_T_D/zebrate/tests/chromedriver"


def test_open_web():
    driver = webdriver.Chrome(driver_location)
    driver.get(zebrate_url)
    sleep(5)
    driver.close()


def test_put_image_link():
    driver = webdriver.Chrome(driver_location)
    driver.get(zebrate_url)
    sleep(5)
    link_inputer = driver.find_element(By.TAG_NAME, 'input')
    link_inputer.send_keys(horse_url)    # заполнить
    link_inputer.send_keys(Keys.RETURN)  # отправить
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(5)
    driver.close()


def test_open_menu():
    driver = webdriver.Chrome(driver_location)
    driver.get(zebrate_url)
    sleep(5)
    btn = driver.find_elements(By.TAG_NAME, 'button')[1]
    btn.click()
    sleep(5)
    driver.close()


def test_click_browse_files():
    driver = webdriver.Chrome(driver_location)
    driver.get(zebrate_url)
    sleep(5)
    btn = driver.find_element(By.XPATH, '//button[text()="Browse files"]')
    btn.click()
    sleep(5)
    driver.close()
