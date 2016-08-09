import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def getTestCfg(target_station):
    test_params = []
    test_params.append(({'target_station': target_station},
                        "TCID:13.02.01 - PMK function", "ZD_PMK_Cache_Function"))
    test_params.append(({'target_station': target_station},
                        "TCID:13.02.02 - PMK Roaming L2LWAPP", "ZD_PMK_Cache_Roaming"))
    test_params.append(({'target_station': target_station},
                        "TCID:13.02.05 - PMK Timing", "ZD_PMK_Cache_Timing"))

    return test_params

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    target_station = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station (Windows XP Sp2 - Broadcom wireless card): ")
    test_cfgs = getTestCfg(target_station)
    
    activeAps = None
    l3_test = raw_input('Do you want to test PMK Roaming between L3 APs (y/n)?')
    if l3_test and l3_test.strip().lower()[0] == 'y':
        while True:
            print 'Please select only 2 APs to test PMK Roaming with L3LWAPP:'
            activeAps = testsuite.getActiveAp(ap_sym_dict)            
            if len(activeAps) == 2:
                test_cfgs.append(({'target_station': target_station, 'test_mode': 'l3', 'active_ap_list': activeAps},
                                    "TCID:13.02.03 - PMK Roaming L3LWAPP", "ZD_PMK_Cache_Roaming"))
                break

    encrypt_option = raw_input('Select the Encryption Option for testing - TKIP or AES ?')
    if encrypt_option and encrypt_option.strip().lower() in ['tkip', 'aes']:
        for test_params in test_cfgs:
            test_params['encryption_option'] = encrypt_option
    else:
        print 'The encryption "%s" does not support' % encrypt_option

    ts = testsuite.get_testsuite("PMK cache", "Verify the behavior of PMK in the ZD")
    
    test_order = 1
    test_added = 0
    for test_params, common_name, test_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)
