""" 
Created on 2014-04-30
@author: chen.tao@odc-ruckuswireless.com
"""

import sys
import time
import random
import copy
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):

    test_cfgs = []

    hotspot_cfg = {'login_page': 'http://192.168.0.250/login.html',
                   'name': 'hs_for_flexible_mac',
                   'auth_svr': 'radius_for_flexible_mac',
                   'idle_timeout': None,
                   'enable_mac_auth': True,
                   'mac_bypass_format':'mac',
                   'mac_addr_format':'aabbccddeeff'
                            }

    ras_cfg =  {'server_addr': '192.168.0.252',
                'server_port' : '1812',
                'server_name' : "radius_for_flexible_mac",
                'radius_auth_secret': '1234567890',
                'radius_auth_method': 'chap',
                    }

    wlan_cfg = {
        'ssid': "Flexible_mac_addr_hs_mac_auth" ,
        'name': "Flexible_mac_addr_hs_mac_auth" ,
        'type': 'hotspot',
        'hotspot_name':'hs_for_flexible_mac',
        'auth': "open", 
        'encryption': "none",
        'mac_addr_format':"aabbccddeeff",
        }
    
    radio_mode = cfg['radio_mode'] 
    ap_tag = 'ap%s' % radio_mode
    sta_radio_mode = radio_mode

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': 'sta1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service on active zd'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list'],
                  }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

#testcase 1
    mac_addr_format = 'aabbccddeeff'
    hs_cfg_mac_format_1 = deepcopy(hotspot_cfg)
    hs_cfg_mac_format_1['mac_addr_format'] = mac_addr_format
    test_cfgs.extend(test_process(wlan_cfg,mac_addr_format,hs_cfg_mac_format_1,cfg))
#testcase 2
    mac_addr_format = 'AABBCCDDEEFF'
    hs_cfg_mac_format_2 = deepcopy(hotspot_cfg)
    hs_cfg_mac_format_2['mac_addr_format'] = mac_addr_format
    test_cfgs.extend(test_process(wlan_cfg,mac_addr_format,hs_cfg_mac_format_2,cfg))

#testcase 3
    mac_addr_format = 'aa:bb:cc:dd:ee:ff'
    hs_cfg_mac_format_3 = deepcopy(hotspot_cfg)
    hs_cfg_mac_format_3['mac_addr_format'] = mac_addr_format
    test_cfgs.extend(test_process(wlan_cfg,mac_addr_format,hs_cfg_mac_format_3,cfg))
    
#testcase 4
    mac_addr_format = 'AA:BB:CC:DD:EE:FF'
    hs_cfg_mac_format_4 = deepcopy(hotspot_cfg)
    hs_cfg_mac_format_4['mac_addr_format'] = mac_addr_format
    test_cfgs.extend(test_process(wlan_cfg,mac_addr_format,hs_cfg_mac_format_4,cfg))
    
#testcase 5
    mac_addr_format = 'aa-bb-cc-dd-ee-ff'
    hs_cfg_mac_format_5 = deepcopy(hotspot_cfg)
    hs_cfg_mac_format_5['mac_addr_format'] = mac_addr_format
    test_cfgs.extend(test_process(wlan_cfg,mac_addr_format,hs_cfg_mac_format_5,cfg))
    
#testcase 6
    mac_addr_format = 'AA-BB-CC-DD-EE-FF'
    hs_cfg_mac_format_6 = deepcopy(hotspot_cfg)
    hs_cfg_mac_format_6['mac_addr_format'] = mac_addr_format
    test_cfgs.extend(test_process(wlan_cfg,mac_addr_format,hs_cfg_mac_format_6,cfg))
    

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station for the next test'
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 0, True))
                        
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list'],
                  }
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Server_Add_STA_MAC_As_Radius_User'                
    common_name = "Add station mac in radius users to recover env"
    test_cfgs.append(({'mac_format_type': 'all_formats',
                       'sta_tag':'sta1'}, test_name, common_name, 0, True))
    

    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD after test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
      
    return test_cfgs
def test_process(init_wlan_cfg,mac_addr_format,hs_cfg,cfg):

    wlan_cfg = deepcopy(init_wlan_cfg)
    wlan_cfg['mac_addr_format'] = mac_addr_format
    
    radio_mode = cfg['radio_mode'] 
 
    radio_mode = cfg['radio_mode'] 

    sta_radio_mode = radio_mode

    ap_tag = 'ap%s' % radio_mode

    test_cfgs = []
    
    uppercase = 'uppercase ' if 'A' in mac_addr_format else ''
    test_case_name = '[MAC Addr Format %s%s]'%(uppercase,mac_addr_format)

    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    common_name = '%sCreate a Hotspot profile'% (test_case_name)
    test_cfgs.append(({'hotspot_conf':hs_cfg}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = '%sCreate WLAN from CLI.'% (test_case_name)
    test_cfgs.append(({'wlan_conf':wlan_cfg}, test_name, common_name, 2, False))

    test_name = 'CB_Server_Del_STA_MAC_As_Radius_User'                
    common_name = "%sDelete station mac info in Radius"% (test_case_name)
    test_cfgs.append(({'mac_format_type': 'all_formats',
                       'sta_tag':'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_Server_Add_STA_MAC_As_Radius_User'
    common_name = "%sAdd station's MAC addr as radius user"% (test_case_name)
    test_cfgs.append(({'mac_format_type': mac_addr_format,
                       'sta_tag':'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station1 to the WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station1 status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1',
                       'ap_tag': ap_tag,
                       'username':'mac.bypass',#@author: yuyanan @since:2014-12-30 @change:behavior change
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_Server_Del_STA_MAC_As_Radius_User'
    common_name = "%sDelete station's MAC addr as radius user"% (test_case_name)
    test_cfgs.append(({'mac_format_type': mac_addr_format,
                       'sta_tag':'sta1'}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs on ZD'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = '%sRemove all Hotspot Profiles from ZD'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')

def check_duplicated_common_name(test_cfgs):
    common_name_list = []
    duplicate_flag = False
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if common_name in common_name_list:
            duplicate_flag = False
            print '####################'
            print common_name
            print '####################'
        else:
            common_name_list.append(common_name)
    return duplicate_flag
    
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]

    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list':all_ap_mac_list
            }         
    test_cfgs = define_test_cfg(tcfg)   
    check_max_length(test_cfgs)
    is_duplicated = check_duplicated_common_name(test_cfgs)
    if is_duplicated:
        return    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Flexible_MAC_Addr_Fomat_Hotspot_MAC"

    ts = testsuite.get_testsuite(ts_name, "Flexible_MAC_Addr_Fomat_Hotspot_MAC" , combotest=True)

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