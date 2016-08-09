import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (18.01, tcid)

def defineTestConfiguration(target_station, invalid_station):
    test_cfgs = []

    test_name = 'ZD_MAC_Authentication'
    common_name = 'Valid/Invalid username and password'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'authorized_station':target_station,
                                            'unauthorized_station':invalid_station,
                                            'testcase':'with-valid-and-invalid-client'},
                      test_name, common_name, tcid(1)))

    common_name = 'MAC Authentication with encryption type'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'authorized_station':target_station,
                                            'testcase':'with-encryption-type'},
                      test_name, common_name, tcid(2)))

    common_name = 'IOP with Radius on Win2003 (IAS)'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.250',
                                            'server_port': '16450',
                                            'server_name': 'Win2k3 Radius',
                                            'radius_auth_secret': '1234567890'},
                                            'authorized_station':target_station,
                                            'testcase':'with-IAS'},
                      test_name, common_name, tcid(3)))

    common_name = 'IOP with FreeRadius'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'authorized_station':target_station,
                                            'testcase':'with-free-radius'},
                      test_name, common_name, tcid(4)))

    common_name = 'Block the invalid client'
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'unauthorized_station':invalid_station,
                                            'testcase':'with-blocking-the-invalid-client'},
                      test_name, common_name, tcid(5)))

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        valid_sta = 0,
        invalid_sta = 1,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs['interactive_mode']:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
        invalid_sta = testsuite.getTargetStation(sta_ip_list, "Pick a invalid wireless station (with MAC is not existed on Radius server): ")
    else:
        target_sta = attrs['valid_sta']
        invalid_sta = attrs['invalid_sta']

    ts_name = 'MAC Authentication'
    if attrs['testsuite_name']: ts_name = attrs['testsuite_name']
    test_cfgs = defineTestConfiguration(target_sta, invalid_sta)
    ts = testsuite.get_testsuite(ts_name, 'MAC Authentication', interactive_mode = attrs["interactive_mode"])

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
