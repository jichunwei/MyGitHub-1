"""
This program is the same as libZD_TestSuite_IPV6.py with one special feature
that it uses PrettyPrinter to generate testbed config in a pretty format
so it is easy to read and modify.

It generate testbed config with generate L3Switch dictionary.

Example:
   maketestbed name=ipv6test
    
"""
import sys
import pprint

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Debug as bugme

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    tb = testsuite.get_test_bed(**_dict)

    bugme.do_trace()

    ppp = pprint.PrettyPrinter(indent = 0)
    print "\nTestbed created:"
    print "Name: %s" % tb.name
    tbcfg = testsuite.get_testbed_config(tb)
    print "Configuration:"
    ppp.pprint(tbcfg)
    tb.config = ppp.pformat(tbcfg)
    tb.save()
    exit()
