import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (22.01, tcid)

def defineTestConfiguration(target_station):
    test_cfgs = []

    test_name = 'ZD_L2ACL_Option'
    common_name = 'Create maximum 32 ACL policies'
    test_cfgs.append(({'target_station': target_station, 'testcase':'create-max-l2-acls', 'max_entries':32},
                      test_name, common_name, tcid(1)))

    common_name = 'Create maximum 128 MAC client entries'
    test_cfgs.append(({'target_station': target_station, 'testcase':'create-max-mac-entries', 'max_entries':128},
                      test_name, common_name, tcid(2)))

    common_name = 'Clone an ACL entry'
    test_cfgs.append(({'target_station': target_station, 'testcase':'clone-acl'},
                      test_name, common_name, tcid(3)))

    common_name = 'Change policy from allow to deny'
    test_cfgs.append(({'target_station': target_station, 'testcase':'edit-acl'},
                      test_name, common_name, tcid(9)))

    common_name = 'Remove an ACL entry from a wlan'
    test_cfgs.append(({'target_station': target_station, 'testcase':'remove-acl-out-a-wlan'},
                      test_name, common_name, tcid(10)))

    common_name = 'Delete an using ACL'
    test_cfgs.append(({'target_station': target_station, 'testcase':'delete-an-using-acl'},
                      test_name, common_name, tcid(11)))

    test_name = 'ZD_L2ACL_Integration'
    common_name = 'Test with Client Isolation'
    test_cfgs.append(({'target_station': target_station, 'testcase':'with-isolation', 'dest_ip':'192.168.0.253'},
                      test_name, common_name, tcid(13)))

    common_name = 'Test with Web Authentication'
    test_cfgs.append(({'target_station': target_station, 'testcase':'with-web-authentication', 'dest_ip':'192.168.0.253'},
                      test_name, common_name, tcid(14)))

    common_name = 'Test with VLAN'
    test_cfgs.append(({'target_station': target_station, 'testcase':'with-vlan', 'vlan_id':'2', 'dest_ip':'20.0.2.253/255.255.255.0'},
                      test_name, common_name, tcid(15)))

    common_name = 'Test with tunnel'
    test_cfgs.append(({'target_station': target_station, 'testcase':'with-tunnel', 'dest_ip': '192.168.0.0'},
                      test_name, common_name, tcid(17)))
    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")

    ts_name = 'L2 ACL'

    test_cfgs = defineTestConfiguration(target_sta)
    ts = testsuite.get_testsuite(ts_name, 'Verify L2 ACL Functionality')

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
