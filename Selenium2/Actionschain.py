# coding:utf-8
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# 登录Django
URL = "http://127.0.0.1:8000/admin/login/?next=/admin/"
driver = webdriver.Firefox()
driver.get(URL)

driver.find_element_by_id("id_username").send_keys("admin")
time.sleep(1)
driver.find_element_by_id("id_password").send_keys("administrator")
driver.find_element_by_xpath(".//*[@id='login-form']/div[3]/input").click()

# 鼠标右击
right_click = driver.find_element_by_link_text("Authors")
ActionChains(driver).context_click(right_click).perform()

time.sleep(3)

driver.quit()

