'''
by West.li
this suite backup a cfg file of zd
this cfg file include all configuration item in zd(the configuration item can be added by automation)
'''


import sys
import time
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


GP_RANGE = (1, 144000)


def define_hotspot_profile_cfgs():
    hotspot_cfg_list = []
    hotspot_cfg_list.append(dict(name = 'profile-gp-%s' % time.strftime("%H%M%S"),
                                 login_page = 'http://192.168.0.250/login.html',
                                 idle_timeout = random.randint(GP_RANGE[0], GP_RANGE[1])))
    
    return hotspot_cfg_list
        
        
def define_wlan_cfgs():
    wlan_cfg_list = []
    wlan_cfg_list.append(dict(ssid = "web-gp-%s" % time.strftime("%H%M%S"),
                              auth = "open", encryption = "none", 
                              do_webauth = True, 
                              do_grace_period = True,
                              grace_period = random.randint(GP_RANGE[0], GP_RANGE[1])))
    
    wlan_cfg_list.append(dict(ssid = "guest-gp-%s" % time.strftime("%H%M%S"),
                              auth = "open", encryption = "none", 
                              type = "guest",
                              do_grace_period = True,
                              grace_period = random.randint(GP_RANGE[0], GP_RANGE[1])))
    
    return wlan_cfg_list
 

def define_test_configuration():
    
    test_cfgs = [] 
    data_sync_time=5 #minutes
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'both ZD disable SR' 
    test_cfgs.append(({},test_name,common_name,0,False))      
    
    test_name = 'CB_ZD_Get_ZD2_Mac' 
    common_name = 'get ZD2 mac address'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = 'Disable switch port connected to zd2'
    test_cfgs.append(({'zd':'zd2_mac','device':'zd'},test_name, common_name, 0, False))
    
    test_case_name='Add configuration'
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = '[%s]clear ZD configuration' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item(second time) to ZD' % test_case_name
    test_cfgs.append(({'second':'Y'},test_name, common_name, 1, False))
    
    
    hotspot_profiles_list = define_hotspot_profile_cfgs()
    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = '[%s]Create hotspot profiles' % test_case_name
    test_cfgs.append(({'hotspot_profiles_list': hotspot_profiles_list}, 
                      test_name, common_name, 1, False))
    
    wlan_cfg_list = define_wlan_cfgs()
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s]Create WLANs' % test_case_name
    test_cfgs.append(({'wlan_cfg_list': wlan_cfg_list}, 
                      test_name, common_name, 1, False))
    
    
    test_case_name='backup cfg file'
    test_name = 'CB_ZD_Backup'
    common_name = '[%s]Backup current configuration' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Cmb_Write_File_Path_To_File'
    common_name = '[%s]write config file to parameter defination file' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable sw port connected to standby zd' % test_case_name
    test_cfgs.append(({'device':'zd','number':1},test_name, common_name, 0, False)) 

    return test_cfgs 


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="make zd cfg file,prepare for other test"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="make zd cfg file,prepare for other test"
    test_cfgs = define_test_configuration()
    ts = testsuite.get_testsuite(ts_name, "make zd cfg file,prepare for other test", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    make_test_suite(**_dict)
    
