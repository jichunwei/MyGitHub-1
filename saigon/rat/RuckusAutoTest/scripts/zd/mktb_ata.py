"""
This program is the same as libZD_TestSuite.py with one special feature
that it uses PrettyPrinter to generate testbed config in a pretty format
so it is easy to read and modify.

It can also generate testbed config without generate L3Switch dictionary.

Example:

    # create testbed
        mktb_sm.py name=sr.test  
"""


import libZD_TestSuite_ata as ts
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Debug as bugme
import sys
import re
import pprint
    
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    if _dict.has_key('debug') and _dict['debug']==True:
        bugme.pdb.set_trace()
    #Set the testbed type to ZD_SM, perform Smart Redundancy Test suites.
    _dict['tbtype'] = 'ZD_ATA_Stations'

    tb = ts.buildTestBed(**_dict)
        
    ppp = pprint.PrettyPrinter(indent=0)
    print "\nZD Smart redundancy TestBed created:"
    print "Name: %s" % tb.name
    tbcfg = ts.getTestbedConfig(tb)
    print "Configuration:"
    ppp.pprint(tbcfg)
    tb.config = ppp.pformat(tbcfg)
    tb.save()    
    exit()


