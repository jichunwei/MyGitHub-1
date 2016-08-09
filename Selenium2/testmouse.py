# coding:utf-8
'''
    测试鼠标悬浮
'''

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Firefox()
driver.get("http://www.baidu.com")

above = driver.find_element_by_xpath(".//*[@id='u1']/a[8]")
ActionChains(driver).move_to_element(above).perform()
