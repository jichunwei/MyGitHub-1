# coding:utf-8
'''
    警告框的处理
    selenium webdriver
    swith_to_alert()
    参数：    accept(), 接受现有警告框
            dismiss(), 解散现有警告框
            text,   返回 alert/confirm/prompt中的文字信息
            send_keys(KyesToSend) 发送文本值警告框, KeysToSend: 将文本发送至警告框
'''

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import re
import time

driver = webdriver.Firefox()
driver.get("https://www.baidu.com")

#鼠标悬停在'设置'链接
link = driver.find_element_by_link_text('设置')
ActionChains(driver).move_to_element(link).perform()

# 打开搜索设置
driver.find_element_by_link_text('搜索设置').click()

# 保存设置
driver.find_element_by_class_name('prefpanelgo').click()
time.sleep(2)

# 接受告警框
driver.switch_to_alert().accept()

#quit web
driver.quit()