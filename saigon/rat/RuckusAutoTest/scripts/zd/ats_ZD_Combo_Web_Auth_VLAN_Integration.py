'''
Web Authentication tag VLAN w/o WLAN Group

Created @2011-8-15
@author: cwang@ruckuswireless.com

Update @2011-11-22
author: cwang@ruckuswireless.com
Description:
	Remove the TCID key, add test case name per case

'''
import re
import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

#define an ID generator
def gen():
    k = 0
    while True:
        k += 1
        yield k
        
ID_GEN = gen().next


#def _tcid(base_id, model_id=None):
#    if model_id:
#        return u'TCID:05.01.03.%02d.%d' % (base_id, model_id)
#    else: return u'TCID:05.01.03.%02d' % (base_id)

# each test_params is a tuple with 2 elemens: (<test_params dict>, <TCID dict>)
def make_test_parameters():
    test_params = {}
    _base_id = 1
    tcid_base_ap_model = {}
    for ap_model in const.get_all_ap_model_id():
        if ap_model[0] != 'none': tcid_base_ap_model[ap_model[0]] = _tcid(_base_id, ap_model[1])
        else: tcid_base_ap_model[ap_model[0]] = _tcid(_base_id)
    test_params[1] = ({}, tcid_base_ap_model)
    return test_params


def get_common_name(tcid, ap_model = 'none'):
    if ap_model == 'none':
        desc = 'VLAN tagging with WebAuth enabled on WLAN'
    else:
        desc = 'VLAN tagging with WebAuth on %s' % ap_model

    return '[%s - %s]' % (tcid, desc)


def get_ap_model_list(ap_sym_dict):
    ap_model_list = []
    for ap in ap_sym_dict.itervalues():
        if ap['model'] not in ap_model_list:
            ap_model_list.append(ap['model'])

    return sorted(ap_model_list)


def build_tcs(target_station, 
              target_station_radio, 
              active_ap, 
              ap_sym_dict = None, 
              active_ap_list = None):
        
    test_cfgs = []
             
    open_wlan = dict(ssid = "RAT-Open-None", 
                     auth = "open", 
                     encryption = "none",
                     vlan_id = '2',
                     do_webauth = True
                     )
                    
    test_cfgs.extend(clean_steps(LEVEL = 0))                   
        
    test_cfgs.append(({'username': 'local.username',
                       'password': 'local.password'},
                      'CB_ZD_Create_Local_User',
                      'Create a local user',
                      0, 
                      False,
                      ))
            
    test_cfgs.append(({'wlan_cfg_list':[open_wlan]},
                      'CB_ZD_Create_Wlan',
                      'Create wlan',
                      0, 
                      False,
                      ))
          

    param_cfg = dict(active_ap = active_ap)
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Find_Active_AP', 
                      'Find an Active AP', 
                      0, 
                      False))
    
    auth_info = {'username': 'local.username',
                 'password': 'local.password'}
    #tcid = _tcid(1)
    #tcid = '%s.%d' % (tcid, const.get_radio_id(target_station_radio))
    #tcid = get_common_name(tcid)
    tcid = "WebAuth tag VLAN without WLANGroup"
    test_cfgs.extend(encode_tcid(tcid,
                                 station_steps(active_ap, 
                                 target_station, 
                                 target_station_radio, 
                                 open_wlan, 
                                 None, 
                                 auth_info)))

    
    test_cfgs.append(({}, 
                     'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group', 
                     'Remove all wlans out of default', 
                     0, 
                     False,
                     ))
    
       
    test_cfgs.append(({'wlangroups_map':{'wg_1':open_wlan['ssid'],                                         
                                        }}, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLANGroup and WLAN in pair', 
                      0, 
                      False))     
        
    params = make_test_parameters()    
    for test_params, test_id in params.itervalues():
        for ap_id in active_ap_list:            
            active_ap_info = ap_sym_dict[ap_id]
            if re.search('mesh', active_ap_info['status']):
                print "By design, skip mesh AP [%s %s]" % (ap_id, ap_sym_dict[ap_id])
                continue
            ap_model = active_ap_info['model']
            #tcid = test_id[ap_model]
            #tcid = "%s.%d" %(tcid, const.get_radio_id(target_station_radio))
            #tcid = get_common_name(tcid, ap_model)
	    tcid = "Webauth tag VLAN with WLANGroup in %s" % ap_model
            active_ap = ap_id
            param_cfg = dict(active_ap = active_ap)
            test_cfgs.append((param_cfg, 
                              'CB_ZD_Find_Active_AP', 
                              'Find Active AP {%s, %s}' % (ap_id, ap_model)
                              0, 
                              False))                                
            test_cfgs.extend(encode_tcid(tcid,
                                         station_steps(active_ap, 
                                                       target_station, 
                                                       target_station_radio, 
                                                       open_wlan, 
                                                       'wg_1', 
                                                       auth_info))) 
            
    
    test_cfgs.extend(clean_steps(LEVEL = 1))
    
             
    return test_cfgs

def clean_steps(LEVEL = 0):
    return [({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup ENV', 
            LEVEL, 
            False),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup ENV', 
            LEVEL, 
            False),
            ]
    
def station_steps(active_ap, sta, radio, wlan, wg, auth_info):
    test_cfgs = []
    test_cfgs.extend(station_a_steps(active_ap, sta, radio, wlan, wg))
    test_cfgs.extend(station_c_steps(auth_info))
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'allowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       'The station ping a target IP', 
                       2, 
                       False))
    
    test_cfgs.append(({'sta_tag':'sta_1',
                       'ip':'20.0.2.252/255.255.255.0'},
                       'CB_ZD_WebAuth_Check_VLAN_Subnet',
                       'Verify VLAN subnet',
                       2,
                       False))
    test_cfgs.extend(station_p_steps(active_ap, radio, wlan, auth_info))
    return test_cfgs
   
def station_a_steps(active_ap, sta, radio, wlan, wg):
    test_cfgs = []
    if wg:
        param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = wg, 
                     radio_mode = radio)        
        test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Associate AP with radio %s to %s' % (radio, wg), 
                      0, 
                      False))
 

    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': sta}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       1, 
                       False))
      
     
    test_cfgs.append(({'ap_tag': 'tap', 
                       'active_ap': active_ap}, 
                      'CB_ZD_Create_Active_AP', 
                      'Get the active AP', 
                      1, 
                      False))        
        
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': wlan}, 
                      'CB_ZD_Associate_Station_1', 
                      'Associate the station', 
                      1, 
                      False))    

    
    test_cfgs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get wifi address', 
                      1, 
                      False))
    
        
    test_cfgs.append(({'sta_tag': 'sta_1'},
                          'CB_Station_CaptivePortal_Start_Browser',
                          'Open authentication web page',
                          1,
                          False,
                          ))
    
    param_cfg = {'wlan_cfg':wlan, 
                 'chk_empty':False, 
                 'status':'Unauthorized',
                 'chk_radio':False,
                 'radio_mode':radio,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                 
                 }
    test_cfgs.append((param_cfg,                        
                      'CB_ZD_Verify_Station_Info_V2',
                      'Verify the station before web auth', 
                      2, 
                      False)) 

        
    return test_cfgs 

def station_c_steps(auth_info):
    test_cfgs = []
    param_cfgs = {'sta_tag':'sta_1'}
    param_cfgs.update(auth_info)
    test_cfgs.append((param_cfgs, 
                      'CB_Station_CaptivePortal_Perform_WebAuth', 
                      'Perform Web authentication', 
                      1, 
                      False)) 
    return test_cfgs

def station_p_steps(active_ap, radio, wlan, auth_info, chk = True):
    test_cfgs = []
    if chk:
        param_cfg = {'wlan_cfg':wlan, 
                 'chk_empty':False, 
                 'status':'Authorized',
                 'chk_radio':False,
                 'radio_mode':radio,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                                  
                 'username':auth_info['username']}  
      
        test_cfgs.append((param_cfg,                        
                      'CB_ZD_Verify_Station_Info_V2',
                      'Verify the station after web auth', 
                      2,
                      False))
      
    param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = 'Default', 
                     radio_mode = radio)           
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Associate AP with radio %s to %s' % (radio, 'Default'), 
                      0, 
                      False))
     
    test_cfgs.append(({'sta_tag':'sta_1'},
                      'CB_Station_CaptivePortal_Quit_Browser',
                      'Close Authentication browser',
                      1,
                      False,
                      ))     
    return test_cfgs    

def encode_tcid(tcid, test_cfgs):
    #append test cases identifier.
    if tcid:
        test_cfgs_copy = []
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            common_name = '[%s]%s' % (tcid, common_name)
            test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup)) 
        return test_cfgs_copy
        
    return test_cfgs  

#def decorate_common_name(test_cfgs):
#    test_cfgs_copy = []
#    
#    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:        
#        common_name = '%s.%s' % (ID_GEN(), common_name) 
#        test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup))
#                    
#    return test_cfgs_copy


def show_notice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)
    
    
def create_test_suite(**kwargs):
    STA_INDEX = 0
    STA_RADIO_INDEX = 1
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "VLAN Configuration - WebAuth",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:        
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        show_notice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)        
    else:        
        target_sta = sta_ip_list[attrs["station"][STA_INDEX]]
        target_sta_radio = attrs["station"][STA_RADIO_INDEX]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
        
      
    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break
    if not active_ap:
        raise Exception('Have not found valid AP model')           
          
    if attrs["interactive_mode"]:
        ts_name = "VLAN Configuration - WebAuth"        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "Verify the feature VLAN configuration - WebAuth", 
                                 combotest=True)
                

    test_cfgs = build_tcs(target_sta, 
                          target_sta_radio, 
                          active_ap, 
                          ap_sym_dict = ap_sym_dict, 
                          active_ap_list = active_ap_list)
    
    #test_cfgs = decorate_common_name(test_cfgs)
    
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
          
