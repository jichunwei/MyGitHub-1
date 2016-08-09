from libATT_TestSuite import get_testsuite, getActiveApUpdate, getTestbed,\
                         getTestbedConfig, addTestCase, sys
from RuckusAutoTest.common.lib_KwList import as_dict
#from RuckusAutoTest.common.Ratutils import *
#from RuckusAutoTest.common import lib_Debug as bugme

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)
    dict_aps = tbcfg['ap_sym_dict']
    active_ap_list = getActiveApUpdate(dict_aps.keys())

    ts = get_testsuite('Customization file for ATT (Regression test)', 'Verify if the customization file for ATT is applied successfully')
    test_name = 'AP_ATT_FW_Update_Custom'
    common_name = '1.12 - Customization file for ATT (Regression test) - AP (%s)'
    test_param = {'fw_info':{'control':'control_7811.rcks', 'proto':'tftp', 'host':'192.168.2.5'}}

    test_added = 0
    test_order = 0
    exc_level = 0
    is_cleanup = False

    for ap in active_ap_list:
        test_param.update({'active_ap': ap})
        if addTestCase(ts, test_name, common_name % ap, test_param, test_order, exc_level, is_cleanup) > 0:
            print 'ADD: Test case %s' % common_name
            test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite %s" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)

