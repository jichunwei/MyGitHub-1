from libATT_TestSuite import get_testsuite, getActiveApUpdate, getTestbed,\
                         getTestbedConfig, addTestCase, sys
from RuckusAutoTest.common.lib_KwList import as_dict
#from RuckusAutoTest.common.Ratutils import *
#from RuckusAutoTest.common import lib_Debug as bugme

def defineTestParams():
    test_params = []

    test_name = 'CB_AP_FW_Update_Custom'
    common_name = 'Verify if user can load the custom file successfully via CLI (for ATT)'
    test_param = {'fw_info':{'control':'control_7811.rcks', 'proto':'tftp', 'host':'192.168.2.5'}}
    exc_level = 0
    is_cleanup = False
    test_params.append((test_name, common_name, test_param, exc_level, is_cleanup))

    test_name = 'CB_Verify_AP_Custom_Setting'
    common_name = 'Verify the custom settings after AP applying the custom file (for ATT)'
    test_param = {'custom_setting': {'country_code': 'US',
                                     'remote_mgmt':'none',
                                     'dc_info':'enabled',
                                     'fw_info': {'host':'cpe.sbcglobal.net',
                                                 'control':'bbt/data/ruckus_firmware/fwcntrl_7811.rcks',
                                                 'user':'ftpdrop',
                                                 'password':'hand2bbt'}}}
    exc_level = 0
    is_cleanup = False
    test_params.append((test_name, common_name, test_param, exc_level, is_cleanup))

    return test_params

def make_test_suite(**kwargs):
    tbi = getTestbed(**kwargs)
    tbcfg = getTestbedConfig(tbi)
    dict_aps = tbcfg['ap_sym_dict']
    active_ap = getActiveApUpdate(dict_aps.keys())[0]

    ts = get_testsuite('Customization file for ATT (Combo test)', 'Verify if the customization file for ATT is applied successfully')
    test_params = defineTestParams()

    test_added = 0
    test_order = 0
    for test_name, common_name, test_param, exc_level, is_cleanup in test_params:
        test_param.update({'active_ap': active_ap})
        if addTestCase(ts, test_name, common_name, test_param, test_order, exc_level, is_cleanup) > 0:
            print 'ADD: Test case %s' % common_name
            test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite %s" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = as_dict(sys.argv[1:])
    make_test_suite(**_dict)

