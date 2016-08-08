# coding:utf-8

from selenium import webdriver
import time
import os
from exceptions import Exception
'''
    selenium 控制窗口切换
'''
# 打开浏览器，输入URL地址
driver = webdriver.Firefox()
driver.implicitly_wait(3)# 等候10s
driver.get("http://www.baidu.com")

# 获得百度搜索窗口的句柄
search_window = driver.current_window_handle

driver.find_element_by_link_text('登录').click()
driver.find_element_by_link_text('立即注册').click()

# 获得当前所有的打开的句柄
all_handles = driver.window_handles

# 进入注册窗口
for handle in all_handles:
    if handle != search_window:
        driver.switch_to_window(handle)
        print 'now register window!'
        # driver.find_element_by_name("account").send_keys('username')
        # driver.find_element_by_name('password').send_keys('password')
        #...
        time.sleep(10)

# 回到搜索窗口
for hanle in all_handles:
    if handle == search_window:
        driver.switch_to_window(handle)
        print 'now search window!'
        driver.find_element_by_id("TANGRAM__PSP_2__closeBtn").click()
        driver.find_element_by_id("kw").send_keys('selenium')
        driver.find_element_by_id('su').click()
        time.sleep(2)

# close web
driver.quit()