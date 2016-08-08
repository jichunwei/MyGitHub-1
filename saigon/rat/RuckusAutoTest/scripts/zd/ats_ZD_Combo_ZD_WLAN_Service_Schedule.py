'''
Description:
    support: single band/dual band AP.
    1) Create a open-none WLAN.
    2) Create a WLAN-Group
    3) Group this WLAN to WLAN-Group.
    4) Select an active AP.
    5) Associate WLAN-Group to active AP.
    6) Pick-up a station.
    7) Associate ssid to sttion.
    8) Check station list on ZD.
    9) Ping to target server from station.
    10)Set service schedule to off.
    11)Check station list on zd.
    12)Ping to target server from station and is unpingable.
    13)Set service schedule to current time plus 30 mins.
    14)Check station list on zd.
    15)Ping to target server from station.
    16)Waiting for 30 Mins.
    17)Check station list on zd.
    18)Ping to target server from station and is unpingable.
    
Author: cwang@ruckuswireless.com
'''

import sys
#import copy
import time
#import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

def define_wlan_cfg():    
    wlan_cfg = dict(ssid = "rat-wlan-service-schedule-%s" % (time.strftime("%H%M%S")),
                    auth = "open", wpa_ver = "", encryption = "none",
                    key_index = "" , key_string = "",
                    username = "", password = "", auth_svr = "", 
                    web_auth = None, do_service_schedule=None,)    
    return wlan_cfg


def define_test_configuration(tbcfg, fcfg):
    test_cfgs = []    
    #do WLAN service schedule on test case    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'    
    common_name = 'Remove All Wlan Groups for cleanup ENV.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Remove_All_Wlans'    
    common_name = 'Clean all Wlans for cleanup ENV.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
#    test_name = 'CB_ZD_Clear_All_Events' 
#    common_name = '%sClean all events' % tl_id
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#   
    
    wlan_cfg = define_wlan_cfg() 
    test_ip_addr = testsuite.getTestbedServerIp(tbcfg)
    
    wlan_ssid = wlan_cfg['ssid']
    test_name = 'CB_ZD_Create_Wlan'    
    common_name = 'Create WLAN %s to prepare for testing.' % (wlan_ssid)
    param_cfg = dict(wlan_cfg_list = [wlan_cfg])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
    common_name = 'Remove all wlans out of default wlan group for cleanup ENV.'     
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   
        
    
    wlan_group_name = 'service-schedule-wlan-group'
    test_name = 'CB_ZD_Create_Wlan_Group'
    common_name = 'Create Wlan Group: %s to prepare for testing' % (wlan_group_name)
    param_cfg = dict(wgs_cfg = dict(name = wlan_group_name,
                                    description = wlan_group_name))
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
    common_name = 'Assign wlan: %s to wg: %s to prepare for testing.' % (wlan_ssid, wlan_group_name)
    param_cfg = dict(wlangroup_name = wlan_group_name,
                     wlan_name_list = [wlan_ssid]
                     )
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
#    import pdb
#    pdb.set_trace()
    active_ap = fcfg['active_ap_list'][0]
    target_ap_conf = fcfg['ap_sym_dict'][active_ap]
    radios = const.get_radio_mode_by_ap_model(target_ap_conf['model'])
    
    test_name = 'CB_ZD_Find_Active_AP'
    common_name = 'Create an Active AP: %s to prepare for testing.' % (active_ap)     
    param_cfg = dict(active_ap = active_ap)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    for radio in radios:    
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = 'Associate AP: %s, radio: %s to WLAN Group: %s to prepare for testing.' % (active_ap, radio, wlan_group_name)     
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = wlan_group_name, 
                         radio_mode = radio)
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
     

    test_name = 'CB_ZD_Find_Station'
    common_name = 'Find the target Station to prepare'
    param_cfg = dict(target_station = tbcfg['sta_ip_list'][0])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'Clean all Wlans from station to prepare'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = 'Associate the Station to the Wlan to prepare'
    param_cfg = dict(wlan_cfg = wlan_cfg)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = 'Get the Station WIFI IP Address to prepare'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
         
    #test link identifier    
    tl_id = '[WLAN service schedule on]'        
    test_name = 'CB_ZD_Schedule_WLAN_Service'
    common_name = '%sSchedule WLAN on' % tl_id    
    param_cfg = dict(ssid = wlan_ssid, 
                     on = True,
                     off = False, 
                     specific = False,)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 

    
#    test_ip_addr = testsuite.getTestbedServerIp(tbcfg)
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Allowed'
    common_name = '%sThe station ping a target IP' % tl_id
    test_cfgs.append(({'target_ip':test_ip_addr}, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%sVerify the station information on ZD' % tl_id    
    test_cfgs.append(({'wlan_cfg':wlan_cfg}, test_name, common_name, 2, False))
    
    tl_id = '[WLAN service schedule off]'        
    test_name = 'CB_ZD_Schedule_WLAN_Service'
    common_name = '%sSchedule WLAN off' % tl_id    
    param_cfg = dict(ssid = wlan_ssid, 
                     on = False,
                     off = True, 
                     specific = False,)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
            
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Denied'
    common_name = '%sThe station ping a target IP' % tl_id
    test_cfgs.append(({'target_ip':test_ip_addr}, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%sVerify the station information on ZD' % tl_id    
    test_cfgs.append(({'wlan_cfg':wlan_cfg, 'chk_empty':True}, test_name, common_name, 2, False))   
    
    tl_id = '[WLAN service schedule specific]'
    test_name = 'CB_ZD_Schedule_WLAN_Service'
    common_name = '%sSchedule WLAN specific' % tl_id    
    param_cfg = dict(ssid = wlan_ssid, 
                     on = False,
                     off = False, 
                     specific = True,)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
            
    test_name = 'CB_ZD_Associate_Station'
    common_name = '%sAssociate the Station to the Wlan' % tl_id
    param_cfg = dict(wlan_cfg = wlan_cfg)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '%sGet the Station WIFI IP Address' % tl_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Allowed'
    common_name = '%sThe station ping a target IP' % tl_id
    test_cfgs.append(({'target_ip':test_ip_addr}, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%sVerify the station information on ZD when wlan service is enabled' % tl_id    
    test_cfgs.append(({'wlan_cfg':wlan_cfg, 'chk_empty':False}, test_name, common_name, 2, False))  

    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWating for half an hour' % tl_id    
    test_cfgs.append(({'timeout':1800}, test_name, common_name, 1, False))
         
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Denied'
    common_name = '%sThe station ping a target IP' % tl_id
    test_cfgs.append(({'target_ip':test_ip_addr}, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%sVerify the station information on ZD when wlan service is disabled' % tl_id    
    test_cfgs.append(({'wlan_cfg':wlan_cfg, 'chk_empty':True}, test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'    
    common_name = 'Remove All Wlan Groups to finish'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Remove_All_Wlans'    
    common_name = 'Clean all Wlans to finish'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    return test_cfgs
        

def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)
        
    ts_name = 'WLAN Service - configurable'
    ts = testsuite.get_testsuite(ts_name, 'WLAN Service - configurable[on, off, specific:15Mins]', combotest=True)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    fcfg = {}
    ap_sym_dict = tbcfg['ap_sym_dict']
    fcfg['ap_sym_dict'] = ap_sym_dict
    sta_ip_list = tbcfg['sta_ip_list']
    fcfg['sta_ip_list'] = sta_ip_list
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")   
        target_sta_radio = testsuite.get_target_sta_radio()     
    else:
        target_sta = sta_ip_list[attrs["station"][0]] 
        target_sta_radio = attrs["station"][1]       

    active_ap = None    
#    import pdb
#    pdb.set_trace()
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            print active_ap
            break
    if active_ap:
        fcfg['active_ap_list'] = [active_ap]
    else:
        raise Exception("Doesn't find active ap")
    
    test_cfgs = define_test_configuration(tbcfg, fcfg)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    

#----------------------------------#
#     Access Method
#----------------------------------#    

if __name__ == "__main__":    
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    