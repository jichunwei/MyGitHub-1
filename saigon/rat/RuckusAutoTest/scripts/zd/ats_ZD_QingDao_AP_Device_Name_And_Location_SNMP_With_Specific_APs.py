import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(sub_id, tcid, ap_model_id, ap_role_id):
    return "TCID:33.%02d.%02d.%s.%s" % (sub_id, tcid, ap_model_id, ap_role_id)

def defineTestConfiguration(sub_id, active_ap, ap_model_id, ap_role_id, ap_type):
    test_cfgs = []
    test_name = 'AP_Device_Name_And_Location_SNMP'

    common_name = 'Configured Device Name in ZD and check in APs CLI/WEB/SNMP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'ap_device_cfg': {'device_name':'AP_Device_Name'}, 'oid': '1.3.6.1.4.1.25053.1.1.4.1.1.1.1'},
                      test_name, common_name, tcid(sub_id, 1, ap_model_id, ap_role_id)))

    common_name = 'Configured Location in ZD and check in APs CLI/WEB/SNMP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'ap_device_cfg': {'device_location':'AP Device Location'}, 'oid': '1.3.6.1.2.1.1.6'},
                      test_name, common_name, tcid(sub_id, 2, ap_model_id, ap_role_id)))

    common_name = 'Configured GPS Coordinates in ZD and check in APs CLI/WEB/SNMP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'ap_device_cfg': {'gps_coordinates': {'latitude':'16', 'longitude': '10'}},
                       'oid': '1.3.6.1.4.1.25053.1.1.4.1.1.1.5'},
                      test_name, common_name, tcid(sub_id, 3, ap_model_id, ap_role_id)))

    common_name = 'Configured maximum length of Device Name in ZD and check in APs CLI/WEB/SNMP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'ap_device_cfg': {'device_name': utils.make_random_string(64,"alnum")},
                       'oid': '1.3.6.1.4.1.25053.1.1.4.1.1.1.1'},
                      test_name, common_name, tcid(sub_id, 4, ap_model_id, ap_role_id)))

    common_name = 'Configured maximum length of Location in ZD and check in APs CLI/WEB/SNMP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'ap_device_cfg': {'device_location': utils.make_random_string(64,"alnum")}, 'oid': '1.3.6.1.2.1.1.6'},
                      test_name, common_name, tcid(sub_id, 5, ap_model_id, ap_role_id)))

    common_name = 'Configured maximum value of GPS Coordinates in ZD and check in APs CLI/WEB/SNMP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'ap_device_cfg': {'gps_coordinates': {'latitude':'90.00000000', 'longitude': '180.00000000'}},
                       'oid': '1.3.6.1.4.1.25053.1.1.4.1.1.1.5'},
                      test_name, common_name, tcid(sub_id, 6, ap_model_id, ap_role_id)))

    return test_cfgs

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    test_cfgs = []
    sub_id = 2

    for active_ap in active_ap_list:
        active_ap_conf = ap_sym_dict[active_ap]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
        test_cfgs.extend(defineTestConfiguration(sub_id, active_ap, ap_model_id, ap_role_id, ap_type))

    ts_name = "AP Device Name and Location - SNMP"
    ts = testsuite.get_testsuite(ts_name, 'Verify AP Device Name, Location, GPS Coordinates configured on ZD')
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
