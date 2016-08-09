# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure QoS:



Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration(target_station):
    wlan_cfg = defineWLANConf()
    test_cfgs = []

    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create WLAN OPEN-NONE'
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg['open_none']]},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Data_Plane_Test'
    common_name = 'Data plane testing on WLANs %s' % wlan_cfg['open_none']['ssid']
    test_cfgs.append(({'target_station': target_station},
                        test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Debug_PS'
    common_name = 'Displays information about all processes that are running'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Debug_Delete_Station'
    common_name = 'Delete the station with the specified MAC address'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Debug_Restart_AP'
    common_name = 'Restarts the device with the specified MAC address'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Debug_Save_Config'
    common_name = 'Upload the ZD\'s config file to TFTP site'
    test_cfgs.append(({'debug_info': {'tftp_server_ip': '192.168.0.10'}},
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Debug_Save_Debug_Info'
    common_name = 'Saves debug information'
    test_cfgs.append(({'debug_info': {'tftp_server_ip': '192.168.0.10'}},
                      test_name, common_name, 1, False))
    
    return test_cfgs

def defineWLANConf():
    wlan_cfg = {'open_none': {'ssid':'CLI-OPEN-NONE', 'auth':'open', 'encryption':'none'},}
                
    return wlan_cfg

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    target_station = testsuite.getTargetStation(sta_ip_list, 'Pick an wireless station: ')

    ts_name = 'ZD CLI - Configure Debug mode'
    ts = testsuite.get_testsuite(ts_name, 'Verify the debug mode commands under CLI', combotest=True)
    test_cfgs = defineTestConfiguration(target_station)

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
    createTestSuite(**_dict)
