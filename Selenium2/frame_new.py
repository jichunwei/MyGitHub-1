# coding:utf-8

from selenium import webdriver
import time

driver = webdriver.Firefox()
driver.get("http://127.0.0.1:8000/")

#选择frame
driver.switch_to_frame('fra')
driver.find_element_by_xpath(".//*[@id='buy']").click()
time.sleep(3)
driver.find_element_by_xpath("//option[@value='13']").click()
driver.switch_to_alert()



