"""
Verify Autonomous WLAN Encryption types with AP connected
    
    Authentication option is Open only
    Encryption types permutation and combination:
    1.    None
    2.    WLAN(WPA+AES), station(WPA+AES)
    3.    WLAN(WPA+TKIP), station(WPA+ TKIP)
    4.    WLAN(WPA+AUTO), station(WPA+AES)
    5.    WLAN(WPA+ AUTO), station(WPA+ TKIP)
    6.    WLAN(WPA2+AES), station(WPA2+AES)
    7.    WLAN(WPA2+TKIP), station(WPA2+ TKIP)
    8.    WLAN(WPA2+AUTO), station(WPA2+AES)
    9.    WLAN(WPA2+ AUTO), station(WPA2+ TKIP)
    10.    WLAN(WPA-Mixed+ AES), station(WPA+AES)
    11.    WLAN(WPA-Mixed+ AES), station(WPA2+AES)
    12.    WLAN(WPA-Mixed +TKIP), station(WPA+ TKIP)
    13.    WLAN(WPA-Mixed +TKIP), station(WPA2+ TKIP)
    14.    WLAN(WPA-Mixed+ AUTO), station(WPA+AES)
    15.    WLAN(WPA-Mixed+ AUTO), station(WPA2+AES)
    16.    WLAN(WPA-Mixed + AUTO), station(WPA+ TKIP)
    17.    WLAN(WPA-Mixed + AUTO), station(WPA2+ TKIP)
    18.    WEP-64
    19.    WEP-128

    expect result: All steps should result properly.
    
    How to:
        1) Create an Autonomous WLAN, encryption type is None
        2) Station associate the WLAN
        3) Get station WiFi address
        4) Verify station information in ZD, status is Authorized
        5) Client can ping target station successfully.
        6) Configure an invalid route in ZD 'Static route table'
        7) Wait AP disconnected
        8) Verify WLAN still exists and client still alive by AP CLI
        9) Client can still ping target station successfully.
        10) Client disconnects from the WLAN
        11) Station associate the WLAN
        12) Get station WiFi address
        13) Verify client alive by AP CLI
        14) Client can ping target station successfully.
        15) Delete the invalid route in ZD and wait AP reconnected to ZD again
        16) Remove the WLAN
        17) Create an Autonomous WLAN with other encryption type(such as WPA+AES) and repeat step 1)-16)

Created on 2013-04-11
@author: kevin.tan
"""

import sys
import time
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

check_wlan_timeout = 5

def _define_wlan_cfg(auth='open', wpa_ver = '', encryption = 'none', key_index = '1', key_string = '', 
                     sta_auth = '', sta_wpa_ver = '', sta_encryption = '', 
                     vlan_id = '',random_num=''):
    #@author:yuyanan @since:2014-12-26 @change:optimize wlan name
    wlan_ssid = 'autonomous-auto-test-'+random_num
    wlan_cfg = dict(ssid=wlan_ssid, auth=auth, wpa_ver=wpa_ver, encryption=encryption, key_index=key_index, key_string=key_string,
                    sta_auth=sta_auth, sta_wpa_ver=sta_wpa_ver, sta_encryption=sta_encryption)
    
    wlan_cfg['type'] = 'autonomous'

    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id
    
    return wlan_cfg

def define_test_cfg(cfg, wlan_cfg_param_list):
    test_cfgs = []
    
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    target_ip_addr = cfg['target_ping_ip_addr']

    radio_mode = cfg['radio_mode']
    vlan_id  = cfg['vlan_id']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'

    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = 'Delete all static routes from ZD'
    test_cfgs.append(({'operation': 'delete all'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Auto_Recovery'
    common_name = 'Config AP recovery option disabled'
    test_cfgs.append(({'recovery_enabled': False}, test_name, common_name, 0, False))

    #@author:yuyanan @since:2014-12-26 @bug:zf-11264
    random_num = utils.make_random_string(random.randint(4,6), "hex")
    index = 0
    for i in wlan_cfg_param_list:
        wlan_cfg = _define_wlan_cfg(i[0], i[1], i[2], i[3], i[4],i[5], i[6],i[7],cfg['vlan_id'],random_num)

        index += 1
        if index == 1:
            test_case_name = "[%s %s]" % (wlan_cfg['auth'], wlan_cfg['encryption'])
        elif index in range(2,11):
            test_case_name = "[%s %s %s sta %s %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'], wlan_cfg['sta_encryption'])
        #elif index in [4,5,8,9]:
        #    test_case_name = "[%s %s %s sta %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_encryption'])
        #elif index in [10,11,12,13]:
        #    test_case_name = "[%s %s %s sta %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'])
        #elif index in [14,15,16,17]:
        #    test_case_name = "[%s %s %s sta %s %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'], wlan_cfg['sta_encryption'])
        elif index in [11,12]:
            test_case_name = "[%s %s]" % (wlan_cfg['auth'], wlan_cfg['encryption'])
        else:
            pass

        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sCreate or Edit WLAN on ZD' % (test_case_name)
        test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                           'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 1, False))
            
        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station to the WLAN' % (test_case_name)
        test_cfgs.append(({'wlan_cfg': wlan_cfg,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet WiFi address of the station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Verify_Expected_Subnet'
        common_name = '%sVerify station wifi ipaddr in expected subnet' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                          test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify client information Authorized status in ZD' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg,
                           'radio_mode':sta_radio_mode,},
                           test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Config_Static_Route'
        common_name = '%sConfigure an invalid route to AP' % (test_case_name)
        test_cfgs.append(({'operation': 'add',
                            'parameter': None, 'ap_tag': ap_tag}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Wait_AP_Status'
        common_name = '%sWait active AP status changed to disconnected' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'disconnected'}, test_name, common_name, 2, False))

        test_name = 'CB_AP_CLI_Check_Wlans'
        common_name = '%sCheck WLAN is still available in AP CLI' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag,  
                           'num_of_ssids':1}, test_name, common_name, 2, False))

        test_name = 'CB_AP_CLI_Check_Station'
        common_name = '%sCheck station is still available in AP CLI' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'ssid': wlan_cfg['ssid'],
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can still ping a target IP' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))

        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station after AP disconnected' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station to the WLAN after AP disconnected' % (test_case_name)
        test_cfgs.append(({'wlan_cfg': wlan_cfg,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet WiFi address of the station after AP disconnected' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

        test_name = 'CB_AP_CLI_Check_Station'
        common_name = '%sCheck station is available in AP CLI after AP disconnected' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'ssid': wlan_cfg['ssid'],
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP after AP disconnected' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Config_Static_Route'
        common_name = '%sDelete all static routes' % (test_case_name)
        test_cfgs.append(({'operation': 'delete all',
                            'parameter': None}, test_name, common_name, 2, True))

        test_name = 'CB_ZD_Wait_AP_Status'
        common_name = '%sWait active AP status changed back to connected' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected',
		                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},}, test_name, common_name, 2, True))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station in the end' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = 'Delete all static routes at last'
    test_cfgs.append(({'operation': 'delete all'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Auto_Recovery'
    common_name = 'Config AP recovery option enabled'
    test_cfgs.append(({'recovery_enabled': True}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove the wlan from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))

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
    
    expected_sub_mask = '255.255.255.0'
    enable_vlan = False
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)

        enable_vlan = raw_input("Is VLAN id 2 enabled? [y/n]: ").lower() == "y"
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    server_ip_addr  = testsuite.getTestbedServerIp(tbcfg)
    target_ping_ip_addr = '172.16.10.252'

    if enable_vlan:
        expected_subnet = '20.0.2.0'
        vlan_id = '2'
    else:
        expected_subnet = utils.get_network_address(server_ip_addr, expected_sub_mask)
        vlan_id = ''

    tcfg = {
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
            'vlan_id': vlan_id,
            }
   
    key_string_wpa      = utils.make_random_string(random.randint(8, 63), "hex")
    key_string_wpa2     = utils.make_random_string(random.randint(8, 63), "hex")
    key_string_wpa_mixed= utils.make_random_string(random.randint(8, 63), "hex")
    key_string_wep64_0  = utils.make_random_string(10, "hex"),
    key_string_wep128_0 = utils.make_random_string(26, "hex"),
    
    if type(key_string_wep64_0) == type((1,2)):
        key_string_wep64 = key_string_wep64_0[0]
    else:
        key_string_wep64 = key_string_wep64_0
    
    if type(key_string_wep128_0) == type((1,2)):
        key_string_wep128 = key_string_wep128_0[0]
    else:
        key_string_wep128 = key_string_wep128_0

    #######<auth>  <wpa_ver> <encryption> <key_index> <key_string> <sta_auth> <sta_wpa_ver> <sta_encryption>###### 
    list = [('open', '', 'none', '', '', 'open', '', 'none'),#1
#           ('PSK', 'WPA', 'TKIP', '', key_string_wpa,'PSK', 'WPA', 'TKIP'),#2
#           ('PSK', 'WPA', 'AES', '', key_string_wpa,'PSK', 'WPA', 'AES'), #3
#           ('PSK', 'WPA', 'Auto', '', key_string_wpa,'PSK', 'WPA', 'TKIP'), #4
#           ('PSK', 'WPA', 'Auto', '', key_string_wpa,'PSK', 'WPA', 'AES'), #5
#           ('PSK', 'WPA2', 'TKIP', '', key_string_wpa2,'PSK', 'WPA2', 'TKIP'),#6
           ('PSK', 'WPA2', 'AES', '', key_string_wpa2,'PSK', 'WPA2', 'AES'),#7
           ('PSK', 'WPA2', 'Auto', '', key_string_wpa2, 'PSK', 'WPA2', 'TKIP'), #8
           ('PSK', 'WPA2', 'Auto', '', key_string_wpa2, 'PSK', 'WPA2', 'AES'), #9
#           ('PSK', 'WPA_Mixed', 'TKIP', '', key_string_wpa_mixed, 'PSK', 'WPA', 'TKIP'),  #10
#           ('PSK', 'WPA_Mixed', 'TKIP', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'TKIP'),  #11
           ('PSK', 'WPA_Mixed', 'AES', '', key_string_wpa_mixed, 'PSK', 'WPA', 'AES'),  #12
           ('PSK', 'WPA_Mixed', 'AES', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'AES'),  #13
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA', 'TKIP'), #14
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA', 'AES'), #15
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'TKIP'), #16
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'AES'), #17
           ('open', '', 'WEP-64', '1', key_string_wep64, 'open', '', 'WEP-64'),#18
           ('open', '', 'WEP-128', '1', key_string_wep128, 'open', '', 'WEP-128'),#19
            ]

    test_cfgs = define_test_cfg(tcfg, list)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Autonomous WLAN EncryptionTypes - %s" % target_sta_radio

    ts = testsuite.get_testsuite(ts_name, ("Autonomous WLAN EncryptionTypes"), combotest=True)

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
