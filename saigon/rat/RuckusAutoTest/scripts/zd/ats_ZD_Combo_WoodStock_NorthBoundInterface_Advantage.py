'''
ZeroIT/DPSK via Northbound Interface
    Case#1:
        ZeroIT via Northbound Interface        
    Steps:
        1) Create a Open None WLAN
        2) Associate it from Station
        3) Create a Open None WLAN with ZeroIT option.
        4) Download ZeroIT auto-config file as "prov.exe" via northbound command
        5) Install it
        6) Verify client works well
        7) Remove all WLAN from ZD.

    Case#2:
        ZeroIT with DPSK via Northbound Interface.
    Steps:
        1) Create a Open Nnoe
        2) Associate it from Station
        3) Create a Open-WPA-TKIP-ZeroIT-DPSK with ZeroIT and DPSK
        5) Download ZeroIT auto-config file as "prov.exe" via Northbound command
        6) Install it 
        7) Verify Client works well
        8) Remove all WLAN from ZD.
Created on 2012-5-24
@author: cwang@ruckuswireless.com
'''
from copy import deepcopy

from string import Template
import time
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


#Configuration for test suites.
_base_cfg = {
        'req-password':'1234',              
        }

_base_wlan_cfg = {
             'ssid':        'RAT-Open-None',
             'auth':        'open',
             'encryption':  'none',
             'type':        'standard',            
             }

_wlan_cfg = {
             'ssid':        'RAT-Open-None-ZeroIT',
             'auth':        'open',
             'encryption':  'none',
             'type':        'standard',
             'do_zero_it': True             
             }

_wlan_cfg2 = {
             'ssid':        'RAT-Open-WPA-TKIP-ZeroIT-DPSK',
             'auth':        'open',
             'encryption':  'wpa',
             'algorithm': 'TKIP',
             'type':        'standard',
             'do_zero_it': True             
             }

_wgs_cfg = {
            }


def build_tcs(cfg):
    tcs = []
    tcs.extend(init_tcs())
    radio_mode = cfg['radio_mode']
    
    wlan_list = [_base_wlan_cfg, _wlan_cfg, _wlan_cfg2]
    
    wlanstr = ",".join([wlan['ssid'] for wlan in wlan_list])
    
    tcs.append(({'wlan_cfg_list':wlan_list},
                  'CB_ZD_Create_Wlans',
                  'Create WLAN %s' % wlanstr,
                  0, 
                  False,
                  ))       
    
    tcs.append(({'cfg_type': 'init',
                 'all_ap_mac_list': None}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Config All APs Radio - Disable WLAN Service', 
                 0, 
                 False))
        
    tcs.append(({'active_ap':cfg['active_ap'],
                 'ap_tag': 'tap'}, 
                 'CB_ZD_Create_Active_AP', 
                 'Create active AP', 
                 0, 
                 False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'sta_ip_addr': cfg['target_station'],
                 },
                'CB_ZD_Create_Station',
                'Find a station',
                0, 
                False
                ))
    
    tcs.append(({'cfg_type': 'config',
                 'ap_tag': 'tap',
                 'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                 }, 
                'CB_ZD_Config_AP_Radio', 
                'Config active AP Radio %s - Enable WLAN Service' % (radio_mode), 
                0, 
                False))
    
   
    tcs.append(({'enable':True,
                 'password':'1234',
                 },
                'CB_ZD_Set_Northbound_Interface',
                'Enable Northbound Interface',
                0,
                False
                ))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': _base_wlan_cfg}, 
                 'CB_ZD_Associate_Station_1', 
                 'Associate the station', 
                 1, 
                 False))    

    
    tcs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get wifi address', 
                      1, 
                      False))
     
#    param_cfg = {'wlan_cfg':_base_wlan_cfg, 
#                 'chk_empty':False, 
#                 'status':'Unauthorized',
#                 'chk_radio':False,
#                 'radio_mode':radio_mode,
#                 'sta_tag':'sta_1',
#                 'ap_tag':'tap',                 
#                 }
#    tcs.append((param_cfg,                        
#                  'CB_ZD_Verify_Station_Info_V2',
#                  'Verify the station before auth', 
#                  2, 
#                  False)) 
    
#    tcs.append(({'sta_tag': 'sta_1',
#                   'condition': 'disallowed',
#                   'target_ip': '172.126.0.252',},
#                   'CB_ZD_Client_Ping_Dest', 
#                   'The station ping a target IP before auth', 
#                   2, 
#                   False))
    
    param_cfg = {'wlan_cfg':_base_wlan_cfg, 
                 'chk_empty':False, 
                 'status':'Authorized',
                 'chk_radio':False,
                 'radio_mode':radio_mode,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                   
                 }
    tcs.append((param_cfg,                        
                  'CB_ZD_Verify_Station_Info_V2',
                  'Verify the station After auth', 
                  2, 
                  False)) 
    
    tcs.append(({'sta_tag': 'sta_1',
                   'condition': 'allowed',
                   'target_ip': '172.126.0.252',},
                   'CB_ZD_Client_Ping_Dest', 
                   'The station ping a target IP after auth', 
                   2, 
                   False))
    
    #Case$1
    case_name = "[Northbound interface with ZeroIT]"
    data = '<ruckus><req-password>$req_password</req-password><version>1.0</version><command cmd=\"get-prov-file\" ipaddr=\"\" macaddr=\"00:00:00:00:00:00\" username=\"\" user-agent=\"Mozilla/4.0\"><wlansvc name=\"$ssid\" expiration=\"4380\" key-length=\"8\" vlan-id=\"$vlan_id\"/></command></ruckus>'
    data = Template(data).substitute(dict(req_password=_base_cfg.get("req-password"),
                                   ssid = _wlan_cfg.get("ssid"),
                                   vlan_id = _wlan_cfg.get("vlan_id", "")
                                   ))
    data = data.replace("\n", "")
    tcs.append(({'url':"https://%s/admin/_portalintf.jsp" % cfg.get('zd_ip', "192.168.0.2"),
                 'data':data,
                 },
                'CB_WebPortal_Get_And_Install_Prov_File',
                '%sDownload Zero-IT prov.exe file.' % case_name,
                1,
                False
                ))
    
    param_cfg = {'wlan_cfg':_wlan_cfg, 
                 'chk_empty':False, 
                 'status':'Authorized',
                 'chk_radio':False,
                 'radio_mode':radio_mode,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                   
                 }
    tcs.append((param_cfg,                        
                  'CB_ZD_Verify_Station_Info_V2',
                  '%sVerify the station' % case_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                   'condition': 'allowed',
                   'target_ip': '172.126.0.252',},
                   'CB_ZD_Client_Ping_Dest', 
                   '%sThe station ping a target IP' % case_name, 
                   2, 
                   False))
    
    #Case$2
    case_name = "[Northbound interface with ZeroIT and PSK]"
    data = '<ruckus><req-password>$req_password</req-password><version>1.0</version><command cmd=\"get-prov-file\" ipaddr=\"\" macaddr=\"00:00:00:00:00:00\" username=\"\" user-agent=\"Mozilla/4.0\"><wlansvc name=\"$ssid\" expiration=\"4380\" key-length=\"8\" vlan-id=\"$vlan_id\"/></command></ruckus>'
    data = Template(data).substitute(dict(req_password=_base_cfg.get("req-password"),
                                   ssid = _wlan_cfg2.get("ssid"),
                                   vlan_id = _wlan_cfg2.get("vlan_id", "")
                                   ))
    data = data.replace("\n", "")
    tcs.append(({'url':"https://%s/admin/_portalintf.jsp" % cfg.get('zd_ip', "192.168.0.2"),
                 'data':data,
                 },
                'CB_WebPortal_Get_And_Install_Prov_File',
                '%sDownload Zero-IT prov.exe file.' % case_name,
                1,
                False
                ))
    
    param_cfg = {'wlan_cfg':_wlan_cfg2, 
                 'chk_empty':False, 
                 'status':'Authorized',
                 'chk_radio':False,
                 'radio_mode':radio_mode,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                   
                 }
    tcs.append((param_cfg,                        
                  'CB_ZD_Verify_Station_Info_V2',
                  '%sVerify the station' % case_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                   'condition': 'allowed',
                   'target_ip': '172.126.0.252',},
                   'CB_ZD_Client_Ping_Dest', 
                   '%sThe station ping a target IP' % case_name, 
                   2, 
                   False))
    
    tcs.extend(clean_tcs())
    
    return tcs

def init_tcs():
    return [({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup ENV', 
            0, 
            False),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup ENV', 
            0, 
            False),            
            ]

def clean_tcs():
    return [({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Clean All WLAN Groups for cleanup ENV', 
            0, 
            True),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Remove all WLANs for cleanup ENV', 
            0, 
            True),                       
            ]



def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Woodstock Northbound Interface-Advantage",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    zd_ip_addr = tbcfg['ZD']['ip_addr']
    sta_ip_list = tbcfg['sta_ip_list']
        
    if attrs["interactive_mode"]:        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:        
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name            
            break
        
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)

    ts_name_list = [('Woodstock Northbound Interface-Advantage', build_tcs),                    
                    ]
    cfg = {}
    cfg['radio_mode'] = target_sta_radio
    cfg['active_ap'] = active_ap
    cfg['target_station'] = sta_ip_addr
    cfg['zd_ip'] = zd_ip_addr
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)
                
        test_cfgs = fn(cfg)
        
        test_order = 1
        test_added = 0
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)

