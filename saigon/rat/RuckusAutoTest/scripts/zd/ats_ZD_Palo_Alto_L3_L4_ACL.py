import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (22.02, tcid)

def defineTestConfiguration(target_station):
    test_cfgs = []

    test_name = 'ZD_L3ACL_Option'
    common_name = 'Create maximum 32 ACL policies'
    test_cfgs.append(({'target_station': target_station, 'testcase':'create-max-l3-acls', 'max_entries':32},
                      test_name, common_name, tcid(1)))

    common_name = 'Create maximum 32 Rule entries'
    test_cfgs.append(({'target_station': target_station, 'testcase':'create-max-rule-entries', 'max_entries':32},
                      test_name, common_name, tcid(2)))

    test_name = 'ZD_L3ACL_Rule_Editing'
    common_name = 'Change policy from allow to deny'
    test_cfgs.append(({'target_station': target_station, 'testing_rule':{'action':'Allow'}, 'new_rule_conf':{'action':'Deny'}},
                      test_name, common_name, tcid(7)))

    common_name = 'Change policy from FTP to HTTP'
    test_cfgs.append(({'target_station': target_station, 'testing_rule':{'application':'FTP'}, 'new_rule_conf':{'application':'HTTP'}},
                      test_name, common_name, tcid(8)))

    common_name = 'Change policy protocol from TCP to UDP'
    test_cfgs.append(({'target_station': target_station, 'testing_rule':{'protocol':'6'}, 'new_rule_conf':{'protocol':'17'}},
                      test_name, common_name, tcid(9)))

    common_name = 'Change policy destination address'
    test_cfgs.append(({'target_station': target_station, 'testing_rule':{'dst_addr':'Any'}, 'new_rule_conf':{'dst_addr':'192.168.0.0/24'}},
                      test_name, common_name, tcid(10)))

    common_name = 'Change policy destination port'
    test_cfgs.append(({'target_station': target_station, 'testing_rule':{'dst_port':'Any'}, 'new_rule_conf':{'dst_port':'1234'}},
                      test_name, common_name, tcid(11)))

    common_name = 'Change order of ACL Rule'
    test_cfgs.append(({'target_station': target_station, 'testing_rule':{}, 'new_rule_conf':{'order':'2'}},
                      test_name, common_name, tcid(14)))

    test_name = 'ZD_L3ACL_Integration'
    common_name = 'Test with Web Authentication'
    test_cfgs.append(({'target_station': target_station, 'testcase':'with-web-authentication', 'dest_ip':'192.168.0.253'},
                      test_name, common_name, tcid(15)))

    common_name = 'Test with VLAN'
    test_cfgs.append(({'target_station': target_station, 'testcase':'with-vlan', 'vlan_id':'2', 'dest_ip':'20.0.2.252/255.255.255.0'},
                      test_name, common_name, tcid(16)))

    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")

    ts_name = 'L3/L4 ACL'

    test_cfgs = defineTestConfiguration(target_sta)
    ts = testsuite.get_testsuite(ts_name, 'Verify L3/L4 ACL Functionality')

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
