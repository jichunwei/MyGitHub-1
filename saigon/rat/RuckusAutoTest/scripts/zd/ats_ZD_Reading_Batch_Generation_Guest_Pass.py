import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(id):
    return "TCID:03.01.%02d" % (id)

def getTestCfg():
    test_cfgs = []

    # Default params
    wlan_cfg = dict(
        type = 'guest',
        auth = 'open',
        encryption = 'none',
    )

    auth_info = dict(
     server_name = 'RADIUS',
     server_addr = '192.168.0.252',
     radius_auth_secret = '1234567890',
     server_port = '1812'
    )

    test_params_default = dict(
        number_profile = 10,
        auth_server_type = 'local',
        auth_server_config = {},
        username = 'rat_guest_pass',
        password = 'rat_guest_pass',
        wlan_cfg = wlan_cfg,
    )

    test_name="ZD_Batch_Generation_Guest_Pass"

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username',
                        'auth_server_type': 'local'})
    common_name = 'Import CSV file with predefined usernames + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(5)))

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username',
                        'auth_server_type': 'radius',
                        'auth_server_info': auth_info,
                        'username': 'ras.local.user',
                        'password': 'ras.local.user'})
    common_name = 'Import CSV file with predefined usernames + Radius Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(6)))

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username_guest_pass',
                        'auth_server_type': 'local'})
    common_name = 'Import CSV file with predefined usernames and guest passes + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(9)))

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username_guest_pass',
                        'auth_server_type': 'radius',
                        'auth_server_info': auth_info,
                        'username': 'ras.local.user',
                        'password': 'ras.local.user'})
    common_name = 'Import CSV file with predefined usernames and guest passes + Radius Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(10)))

    return test_cfgs

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts = testsuite.get_testsuite("Batch Generation of Guest Pass", "Verify Batch Generation of Guest Pass")

    test_order = 1
    test_added = 0
    test_cfgs = getTestCfg()
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
