# coding:utf-8
'''
    单元测试框架 unittest
    TestCase: 以test打头的
    TestSuite:  多个TestCase的集合
    TestRunner:  提供的run()方法来执行 testsuite/test case.
    TestFixture: 覆盖TestCase的setUp()和tearDown()方法来实现
'''

from calculator import count
import unittest

class TestAdd(unittest.TestCase):

    def setUp(self):
        print "Test add Start"

    def test_add(self):
        j = count(2, 3)
        self.assertEqual(j.add(), 5)

    def test_add2(self):
        j = count(41, 76)
        self.assertEqual(j.add(), 117, msg="The result is error")

    def tearDown(self):
        print "Test add end"


class TestSub(unittest.TestCase):

    def setUp(self):
        print "Test sub start"

    def test_sub(self):
        j = count(2, 3)
        self.assertEqual(j.sub(), -1)

    def test_sub2(self):
        j = count(71, 46)
        self.assertEqual(j.sub(), 25)

    def tearDown(self):
        print "Test sub end"

if __name__ == "__main__":
    # 构造测试集
    suite = unittest.TestSuite()
    suite.addTest(TestAdd("test_add"))
    suite.addTest(TestAdd("test_add2"))
    suite.addTest(TestSub("test_sub"))
    suite.addTest(TestSub("test_sub2"))

    #执行测试
    runner = unittest.TextTestRunner()
    runner.run(suite)

