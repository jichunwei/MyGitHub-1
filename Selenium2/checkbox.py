# coding:utf-8
from selenium import webdriver
import os, time

driver = webdriver.Firefox()
file_path = 'file:///' + os.path.abspath('checkbox.html')
driver.get(file_path)

# 选择页面上所有的 tag name 为input的元素
inputs = driver.find_elements_by_tag_name("input")

# 然后从中过滤出type 为 checkbox 的元素，单击勾选
for i in inputs:
    count = 1
    if i.get_attribute('type') == 'checkbox':
        i.click()
        count = count + 1
        print "---勾选按钮第 %d 的按钮---"  % count
        time.sleep(1)

# 取消第一个checkbox
print "===去掉勾选的第一个按钮==="
driver.find_element_by_xpath("html/body/form/input[1]").click()
time.sleep(2)
driver.quit()