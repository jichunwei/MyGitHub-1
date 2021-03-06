"""
This program is the same as libZD_TestSuite.py with one special feature
that it uses PrettyPrinter to generate testbed config in a pretty format
so it is easy to read and modify.

It can also generate testbed config without generate L3Switch dictionary.

Example:

    # create testbed without L3Switch attribute

        maketestbed name=netanya.sys ftype=b
        maketestbed name=net.sys.1 ftype=basic
        maketestbed name=net.sys.2 ftype=none

    # default add L3Switch attributes

        maketestbed name=mesh.specific
        maketestbed name=mesh.i.fanout
"""
import sys
import re
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Debug as bugme

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    if _dict.has_key('ftype') and \
        (re.match(r'.*basic.*|none', _dict['ftype'], re.I) or _dict['ftype'] == 'b'):
        tb = testsuite.getTestbed2(**_dict)
    else:
        tb = testsuite.getMeshTestbed(**_dict)

    bugme.do_trace()

    ppp = pprint.PrettyPrinter(indent = 0)
    print "\nTestbed created:"
    print "Name: %s" % tb.name
    tbcfg = testsuite.getTestbedConfig(tb)
    print "Configuration:"
    ppp.pprint(tbcfg)
    tb.config = ppp.pformat(tbcfg)
    tb.save()
    exit()

