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

import libZD_TestSuite as ts
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Debug as bugme
import sys
import re
import pprint

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    if _dict.has_key('debug') and _dict['debug']==True:
        bugme.pdb.set_trace()
    #Set the testbed type is ZD_Scaling other than ZD_Stations
    _dict['tbtype'] = 'ZD_Scaling'

    if _dict.has_key('ftype') and \
        (re.match(r'.*basic.*|none', _dict['ftype'], re.I) or _dict['ftype'] == 'b'):
        tb = ts.getTestbed2(**_dict)
    else:
        tb = ts.getMeshTestbed(**_dict)
    ppp = pprint.PrettyPrinter(indent=0)
    print "\nZD Scaling testbed created:"
    print "Name: %s" % tb.name
    tbcfg = ts.getTestbedConfig(tb)
    print "Configuration:"
    ppp.pprint(tbcfg)
    tb.config = ppp.pformat(tbcfg)
    tb.save()
    exit()

