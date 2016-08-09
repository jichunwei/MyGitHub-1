# coding:utf-8
'''
    上传文件
    send_keys 实现上传

'''

from selenium import webdriver
import os
from time import sleep

#open webBrowser
driver = webdriver.Firefox()
file_path = "file:///" + os.path.abspath('upfile.html')
driver.get(file_path)

#定位上传按钮，添加本地文件
# driver.find_element_by_name("file").send_keys("D:\\workspace\Selenium2\upfile.html")

driver.find_element_by_name("file").click()
os.system("D:\workspace\Selenium2\upfile.exe")
sleep(3)

#close webbrowser
driver.quit()

