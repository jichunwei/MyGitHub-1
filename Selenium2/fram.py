# coding:utf-8

from selenium import webdriver
import time
import os
from exceptions import Exception

# 打开浏览器，输入URL地址
driver = webdriver.Firefox()
file = "file:///" + os.path.abspath("frame.html")
driver.get(file)

# 直接定位ifram里头的元素，操作将会失败
try:
    ck = driver.find_element_by_xpath("html/body/form/input[1]")  # 第一个checkbox button
    ck.click()
except Exception as msg:
    print msg
    time.sleep(1)
    # 切换到iframe iframe(id = "if")
    try:
        driver.switch_to_frame("if")
    except Exception as msg:
        print msg
    else:
        print "定位表单成功"
        # 操作iframe里头的元素
        print "---选择checkbox button---"
        driver.find_element_by_xpath("html/body/form/input[1]").click()
time.sleep(2)
# close web
driver.close()
