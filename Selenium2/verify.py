# coding:utf-8
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# 登录Django
URL = "http://127.0.0.1:8000/admin/login/?next=/admin/"
driver = webdriver.Firefox()
driver.get(URL)

print "Befor login=================="
# 打印当前页面的title
title = driver.title
print title

# 打印当前页面的URL
now_url = driver.current_url
print now_url

# 登录
driver.find_element_by_id("id_username").clear()
driver.find_element_by_id("id_username").send_keys("admin")
time.sleep(1)
driver.find_element_by_id("id_password").clear()
driver.find_element_by_id("id_password").send_keys("administrator")

print ('After loging------------')

# 再次打印当前页面的title
title = driver.title
print title

# 再次打印当前页面的URL
now_url = driver.current_url
print now_url

# 获得登录的用户名
# user = driver.find_element_by_xpath(".//*[@id='user-tools']/strong")
# user.text
# print user.text

driver.quit()
