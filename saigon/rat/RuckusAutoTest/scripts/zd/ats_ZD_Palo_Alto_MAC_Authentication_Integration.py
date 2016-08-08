import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (18.02, tcid)

def defineTestConfiguration(target_station):
    test_cfgs = []

#    common_name = 'Isolation - MAC Authentication'
#    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
#                                            'server_port': '1812',
#                                            'server_name': 'freeRadius',
#                                            'radius_auth_secret': '1234567890'},
#                                            'authorized_station':target_station,
#                                            'testcase':'with-isolation'},
#                      'ZD_MAC_Authentication', common_name, tcid(2)))

    common_name = 'L2 ACL - MAC Authentication'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'target_station':target_station,
                                            'dest_ip':'192.168.0.252',
                                            'testcase':'with-mac-authentication'},
                      'ZD_L2ACL_Integration', common_name, '18.02.03.01'))

    common_name = 'L3/L4 ACL - MAC Authentication'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'target_station':target_station,
                                            'dest_ip':'192.168.0.252',
                                            'testcase':'with-mac-authentication'},
                      'ZD_L3ACL_Integration', common_name, '18.02.03.02'))

    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")

    ts_name = 'MAC Authentication Integration'

    test_cfgs = defineTestConfiguration(target_sta)
    ts = testsuite.get_testsuite(ts_name, 'MAC Authentication Integration')

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
