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