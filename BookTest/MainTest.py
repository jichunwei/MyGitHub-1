# coding:utf-8
'''
    数据驱动测试用例： 不同用户的登录测试

'''

from selenium import webdriver
from  Public import Login

class LoginTest():

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(3)
        self.driver.get("http://127.0.0.1:8000/admin/")

    # admin登录
    def test_admin_login(self):
        username = 'admin'
        password = 'administrator'
        Login().user_login(self.driver, username, password)
        Login().user_logout(self.driver)
        self.driver.quit()

    # guest 用户登录
    def test_guest_login(self):
        username = 'tan'
        password = 'tanshixiong'
        Login().user_login(self.driver, username, password)
        Login().user_logout(self.driver)
        self.driver.quit()

#admin login
LoginTest().test_admin_login()
#guest login
LoginTest().test_guest_login()