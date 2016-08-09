# coding:utf-8

from selenium import webdriver
from HTMLTestRunner import HTMLTestRunner
import unittest


class Baidu(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "https://www.baidu.com/"

    def test_baidu_search(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_id("kw").send_keys("HTMLTestRunner")
        driver.find_element_by_id("su").click()

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    testunit = unittest.TestSuite()

    # 定义报告存放路径
    fp = open('./log/report.html', 'wb')
    # 定义测试报告
    runner = HTMLTestRunner(stream=fp,
                            title='百度搜索测试的报告',
                            description='用例执行情况:')

    testunit.addTest(Baidu("test_baidu_search"))
    runner.run(testunit)  # 运行测试用例
    fp.close()  # 关闭测试报告
