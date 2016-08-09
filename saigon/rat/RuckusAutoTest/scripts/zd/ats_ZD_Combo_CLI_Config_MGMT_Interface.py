'''
Description:
    Configure MGMT Interface information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration(mgmt_if_conf):
    common_id = '[mgmt-if]'
    test_cfgs = []

    test_name = 'CB_ZD_CLI_Disable_MGMT_IF'
    common_name = '%s1.Disable MGMT Interface via ZD CLI' %common_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Config_MGMT_IF'
    common_name = '%s2.Configure MGMT Interface via ZD CLI' %common_id
    param_cfg = dict(mgmt_if_conf=mgmt_if_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Verify_MGMT_IF_Set_Get'
    common_name = '%s3.Verify MGMT Interface CLI Set and CLI/GUI Get are the same info' %common_id
    param_cfg = dict(mgmt_if_conf=mgmt_if_conf)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_MGMT_IF_Remove_Vlan'
    common_name = '%s4.Remove VLAN from MGMT Interface' %common_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_MGMT_IF_No_Vlan'
    common_name = '%s5.Verify there is no VLAN info in MGMT Interface info' %common_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_WebUI_Launch'
    common_name = '%s6.Launch ZD WebUI at management interface' %common_id
    param_cfg = dict(ip_addr=mgmt_if_conf['ip_addr'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Disable_MGMT_IF'
    common_name = '%s7.Disable MGMT Interface via ZD CLI' %common_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    return test_cfgs


def def_conf():
    conf = {}
    conf['ip_addr'] = '192.168.1.2'
    conf['net_mask'] = '255.255.254.0'
    conf['vlan_id'] = '2'
    return conf


def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'Configure MGMT Interface via CLI and Verify via GUI'
    ts = testsuite.get_testsuite(ts_name, 'MGMT Interface CLI Configuration', combotest=True)
    mgmt_conf = def_conf()
    test_cfgs = define_test_configuration(mgmt_conf)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
