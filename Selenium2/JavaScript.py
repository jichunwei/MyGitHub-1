# coding:utf-8
'''
    调用javaScript
'''

from selenium import webdriver
from time import sleep
import logging

logging.basicConfig(level=logging.DEBUG)
driver = webdriver.Firefox()
driver.get("http://www.baidu.com")
driver.set_window_size(600, 500)

#搜索
driver.find_element_by_id("kw").send_keys("selenium")
driver.find_element_by_id("su").click()
sleep(2)

#通过javascript设置浏览器窗口的滚动条位置
js="windows.scrollTo(100,450);"
driver.execute_script(js)
sleep(3)

driver.quit()