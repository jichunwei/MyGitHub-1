# coding:utf-8

'''
    单元测试框架
'''
from calculator import count
import unittest

class TestCount(unittest.TestCase):

    def setUp(self):
        print "Test start"

    def test_add(self):
        j = count(2, 3)
        self.assertEqual(j.add(),5)

    def tearDown(self):
        print "Test end"

if __name__ == "__main__":
    unittest.main()
