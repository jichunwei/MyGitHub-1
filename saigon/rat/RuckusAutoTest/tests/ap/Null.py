"""
Implementation of a dummy null test case.
"""

from RuckusAutoTest.models import Test


class Null(Test):
    def config(self):
        print "Config Test @ %s %s" % (self.testbed, self.params)
    def test(self):
        print "Running Null(Test)"
        return "PASS","A-OK!"
    def cleanup(self):
        print "Cleanup"
