'''
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure service commands in ZD CLI work well.

'''


import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
                
    
def define_service_cfg_list():
    service_cfg_list = []
    service_cfg_list.append(dict(adjust_ap_power = True,
                                 adjust_ap_channel = True,
                                 scan_24g = True,
                                 scan_5g = True,
                                 detect_aeroscout_rfid = True,
                                 scan_24g_interval = '20',
                                 scan_5g_interval = '30',
                                 cfg_name = 'Enable all services'))
    
    service_cfg_list.append(dict(adjust_ap_power = False,
                                 adjust_ap_channel = False,
                                 scan_24g = False,
                                 scan_5g = False,
                                 detect_aeroscout_rfid = False,
                                 scan_24g_interval = '',
                                 scan_5g_interval = '',
                                 cfg_name = 'Disable all services'))
                
    return service_cfg_list
       

def define_data_plan_test_cfg(sta_tag, wlan_cfg, tcid):
    test_cfgs = []
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%s Station associate wlan and get wifi address' % tcid
    test_cfgs.append(({'wlan_cfg': wlan_cfg, 'sta_tag': sta_tag}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = '%s Station download file from web server' % tcid
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    return test_cfgs


def define_test_cfg(tcfg):
    sta_tag = tcfg['sta_ip_addr']
    test_cfgs = []

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create the target station'
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': tcfg['sta_ip_addr']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in the station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a wlan in ZD GUI'
    test_cfgs.append(({'wlan_cfg_list': [tcfg['wlan_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_Service_Info'
    common_name = 'Bake up service info in ZD GUI'
    test_cfgs.append(({'back_up': True}, test_name, common_name, 0, False))
        
        
    for service_cfg in tcfg['service_cfg_list']:
        test_name = 'CB_ZD_CLI_Configure_Service'
        common_name = '[%s] Configure service in ZD CLI' % service_cfg['cfg_name']
        test_cfgs.append(({'service_cfg': service_cfg}, test_name, common_name, 1, False))
     
        test_name = 'CB_ZD_Get_Service_Info'
        common_name = '[%s] Get service info from ZD GUI' % service_cfg['cfg_name']
        test_cfgs.append(({}, test_name, common_name, 2, False))
           
        test_name = 'CB_ZD_CLI_Verify_Service_Cfg_In_GUI'
        common_name = '[%s] Verify service info in ZD GUI' % service_cfg['cfg_name']
        test_cfgs.append(({'service_cfg': service_cfg}, test_name, common_name, 2, False))
        
        tcid = '[%s]' % service_cfg['cfg_name']
        test_cfgs.extend(define_data_plan_test_cfg(sta_tag, tcfg['wlan_cfg'], tcid))
    
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Close browser in the station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Configure_Service'
    common_name = 'Restore service cfg in ZD CLI'
    test_cfgs.append(({'restore': True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = 0,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list)
        
    else:
        sta_ip_addr = sta_ip_list[attrs["station"]]
    
    wlan_cfg = (dict(ssid = "service-priority-2g-%s" % time.strftime("%H%M%S"),
                     auth = 'open', encryption = 'none'))
    
    service_cfg_list = define_service_cfg_list()
    
    tcfg = {'wlan_cfg': wlan_cfg,
            'service_cfg_list': service_cfg_list,
            'sta_ip_addr': sta_ip_addr,
            }
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "ZD CLI - Configure Service" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure service commands in ZD CLI work well",
                                 combotest=True)
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
    