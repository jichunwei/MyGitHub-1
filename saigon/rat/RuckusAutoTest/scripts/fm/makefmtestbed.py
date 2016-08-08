'''
This program is the same as libZD_TestSuite.py with one special feature
that it uses PrettyPrinter to generate testbed config in a pretty format
so it is easy to read and modify.
It can also generate testbed config without generate L3Switch dictionary.

Example:
    # create testbed without L3Switch attribute
        maketestbed name=fm.sys ftype=[b|basic|none]
    # default add L3Switch attributes will be defined later
'''

from libFM_TestSuite import get_fm_testbed
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.common import lib_Debug as bugme
import re, sys
from pprint import pprint, pformat

def printUsage():
    u = [
      '',
      'Usage:',
      '    maketestbed.py name=<testbed> ftype=[b|basic|none] version=[8|9]',
      '',
      'Paramenters:',
      '    testbed: your test bed name',
      '    ftype:   currently only one of these (b - [default], basic, none) is accepted',
      '    version: version of your FM (8 or 9). Default is "FlexMaster"',
      '            When Feature Update is enhanced, we dont need this option anymore',
      '',]
    for i in u: print i


if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    if 'ftype' not in _dict:
        _dict['ftype'] = 'b'

    if _dict['ftype'] == 'b' or \
       _dict['ftype'] == None or \
       re.match(r'.basic.|.none.', _dict['ftype'], re.I):
        tb = get_fm_testbed(**_dict)
    else:
        printUsage()
        exit(1)

    bugme.do_trace()

    print "\nTestbed created:"
    print "Name: %s" % tb.name
    tbcfg = eval(tb.config)
    print "Configuration:"
    pprint(tbcfg)
    tb.config = pformat(tbcfg)
    tb.save()
    exit()

