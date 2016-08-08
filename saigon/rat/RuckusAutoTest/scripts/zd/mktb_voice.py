"""
This program is the same as libZD_TestSuite.py with one special feature
that it uses PrettyPrinter to generate testbed config in a pretty format
so it is easy to read and modify.

It can also generate testbed config without generate L3Switch dictionary.

Example:
    # create testbed for Spectralink phone testing
    mktb_spectralink.py name=l2
    mktb_spectralink.py name=l3.tunnel.vlan
    mktb_spectralink.py name=l2.tunnel zd_ip_addr=192.168.31.2 

"""

import libZD_TestSuite_Voice as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Debug as bugme
import sys
import re
import pprint

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    if _dict.has_key('debug') and _dict['debug']==True:
        bugme.pdb.set_trace()
    tb = testsuite.getTestbed4(**_dict)

    ppp = pprint.PrettyPrinter(indent=0)
    print "\nTestbed created:"
    print "Name: %s" % tb.name
    tbcfg = testsuite.getTestbedConfig(tb)
    print "Configuration:"
    ppp.pprint(tbcfg)
    tb.config = ppp.pformat(tbcfg)
    tb.save()
    exit()

