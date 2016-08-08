# coding:utf-8
import unittest
import testadd
import testsub


suite = unittest.TestSuite()
# 构造测试套件
suite.addTest(testadd.TestAdd('test_add'))
suite.addTest(testadd.TestAdd("test_add2"))

suite.addTest(testsub.TestSub('test_sub'))
suite.addTest(testsub.TestSub('test_sub2'))

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
