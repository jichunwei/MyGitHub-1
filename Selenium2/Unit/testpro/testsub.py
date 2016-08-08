from calculator import count
import unittest

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