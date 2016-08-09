# coding:utf-8
import unittest, time
from HTMLTestRunner import HTMLTestRunner
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

# 指定测试用例为当前文件夹下的xxx目录
test_dir = './'

discover = unittest.defaultTestLoader.discover(test_dir, pattern='test*.py')

if __name__ == '__main__':

    now = time.strftime("%Y-%m-%m %H-%M-%S")
    path = os.path.abspath("D:\workspace\Selenium2\Unit\TestReport")
    print path
    os.chdir(path)
    print os.getcwd()
    filename = now + 'result.html'
    fp = open(filename, 'wb')

    runner = HTMLTestRunner(stream=fp,
                            title='测试报告',
                            description='用例执行情况')

    runner.run(discover)
    fp.close()