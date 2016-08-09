import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def getCommonName(tcid, cname):
    return u"TCID:99.01.01.%02d - %s" % (tcid, cname)

def makeTestParams():
    test_cfg_list = [
        ( dict(password2='ruckus'),
          'ZD_Bug_8806',
          getCommonName(1, "Bug8806 - Admin with External AuthServ blocks SSH login") ), 
    ]
    return test_cfg_list

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ts = testsuite.get_testsuite("Security - Bugs Buster",
                      "Verify that known security bugs are cleared.")
    test_params=makeTestParams()
    test_order=0
    test_added = 0
    for test_param, test_name, common_name in test_params:
        test_order += 1
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

