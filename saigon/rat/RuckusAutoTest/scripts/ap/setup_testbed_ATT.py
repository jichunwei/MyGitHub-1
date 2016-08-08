'''
Use to make testbed for ATT Data Collection
'''

from libATT_TestSuite import *
from RuckusAutoTest.common.lib_KwList import *
from RuckusAutoTest.common import lib_Debug as bugme
import re
from pprint import pprint, pformat

def printUsage():
    u = [
      '',
      'Usage:',
      '    setup_testbed_ATT.py name=<testbed>',
      '',
      'Paramenters:',
      '    testbed: your test bed name',
      '',]
    for i in u: print i


if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])

    tb = getTestbedATT(**_dict)

    bugme.do_trace()

    print "\nTestbed created:"
    print "Name: %s" % tb.name
    tbcfg = eval(tb.config)
    print "Configuration:"
    pprint(tbcfg)
    tb.config = pformat(tbcfg)
    tb.save()
    exit()



























