'''
Description:
    Show Station information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys
#import copy
import time
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_wlan_cfg():
    wlan_cfgs = []
    wlan_cfgs.append(dict(ssid = "zdcli-station-%s" % (time.strftime("%H%M%S")), auth = "open", wpa_ver = "", encryption = "none",
                          key_index = "" , key_string = "",
                          username = "", password = "", auth_svr = ""))
    
    wlan_cfgs.append(dict(ssid = "zdcli-station-%s" % (time.strftime("%H%M%Y")), auth = "open", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))
    return wlan_cfgs


def define_test_configuration(tbcfg):
    test_cfgs = []
    wlan_cfg = define_wlan_cfg()
    
    ex_id = "[Station info configure from GUI, check from CLI]"
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%s1.Clean all Wlans' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%s2.Create two Wlans' % ex_id
    param_cfg = dict(wlan_cfg_list = wlan_cfg)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
      
    test_name = 'CB_ZD_Find_Station'
    common_name = '%s3.Find the target Station' % ex_id
    param_cfg = dict(target_station = tbcfg['sta_ip_list'][0])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '%s4.Clean all Wlans from station' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '%s5.Associate the Station to the Wlan' % ex_id
    param_cfg = dict(wlan_cfg = wlan_cfg[0])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '%s6.Get the Station WIFI IP Address' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Find_Station'
    common_name = '%s7.Find the target Station' % ex_id
    param_cfg = dict(target_station = tbcfg['sta_ip_list'][1])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '%s8.Clean all Wlans from station' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '%s9.Associate the Station to the Wlan' % ex_id
    param_cfg = dict(wlan_cfg = wlan_cfg[1])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '%s10.Get the Station WIFI IP Address' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Show_Station_All'
    common_name = '%s11.Show all station information' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_Station_Info_All'
    common_name = '%s12.Verify all station information' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Show_And_Verify_AP_Devname'
    common_name = '%s13.Show and verify station information by wlan name' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    return test_cfgs
        

def create_test_suite(**kwargs):
    ts_name = 'TCID: Show Station Information'
    ts = testsuite.get_testsuite(ts_name, 'Show Station Information in CLI', combotest=True)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    test_cfgs = define_test_configuration(tbcfg)

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
    