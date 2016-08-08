from calculator import count

import unittest

class MyTest(unittest.TestCase):
    def setUp(self):
        print "test case start"

    def tearDown(self):
        print "test case end"


class TestAdd():
    def test_add(self):
        j = count(2, 3)
        self.assertEqual(j.add(), 5)

    def test_add2(self):
        j = count(41, 76)
        self.assertEqual(j.add(), 117, msg="The result is error")


class TestSub():

    def test_sub(self):
        j = count(2, 3)
        self.assertEqual(j.sub(), -1)

    def test_sub2(self):
        j = count(71, 46)
        self.assertEqual(j.sub(), 25)

if __name__ == "__main__":
    unittest.main()
