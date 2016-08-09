import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(base_id):
    return u"TCID:01.01.01.%02d" % base_id

def getCommonName(tcid, test_desc):
    return u"%s-%s" % (tcid, test_desc)

def makeTestParams():
    test_params = []
    test_params.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False},
        "ZD_SetupWizardConfiguration",
        tcid(1),
        "Setup Wizard Configuration",))
    test_params.append(({},
        "ZD_SystemName",
        tcid(2),
        "System Name",))
    test_params.append(({},
        "ZD_StaticIPConfiguration",
        tcid(3),
        "Static IP Configuration",))
    test_params.append(({},
        "ZD_DynamicIPConfiguration",
        tcid(4),
        "Dynamic IP Configuration",))
    return test_params

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = None,
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "System - Basic"
    ts = testsuite.get_testsuite(ts_name,
                      "Verify that the ZD can perform basic system configuration properly",
                      interactive_mode = attrs["interactive_mode"])
    test_cfgs = makeTestParams()
    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs:
        common_name = getCommonName(tcid, test_desc)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

