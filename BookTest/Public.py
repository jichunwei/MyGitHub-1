# coding:utf-8
'''
    定义一个login模块,测试数据驱动用例
'''
import time

class Login():

    # 登录
    def user_login(self, driver, username='admin', password='administrator'):
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys(username)
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys(password)
        driver.find_element_by_xpath(".//*[@id='login-form']/div[3]/input").click()

    # 退出
    def user_logout(self, driver):
        driver.find_element_by_xpath(".//*[@id='user-tools']/a[3]").click()
        # driver.find_element_by_link_text("Log out").click() #错误
        time.sleep(5)
        driver.quit()


