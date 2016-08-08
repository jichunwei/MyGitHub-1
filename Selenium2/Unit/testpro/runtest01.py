# coding:utf-8
'''
    TestLoader提供的discover()
    discover(start_dir, pattern='test*.py', top_level_dir=None)


'''
import unittest

#定义测试用例的目录为当前目录
test_dir = './'
discover = unittest.defaultTestLoader.discover(test_dir, pattern='test*.py')

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(discover)
