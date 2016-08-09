"""
    Verify Autonomous WLAN Smart Redundancy failover and work well still.

    expect result: All steps should result properly.
    
    How to:
        1) Create active AP
        2) Initialize SR environment and enable SR option
        3) Create an Autonomous WLAN
        4) Verify Autonomous WLAN info in standby ZD
        5) Delete WLAN
        6) Verify no Autonomous WLAN info in standby ZD
        7) Create an Autonomous WLAN
        8) Verify Autonomous WLAN info in standby ZD
        9) Station associate the WLAN
        10) Get station wifi address
        11) Verify client status is 'authorized' and client can ping target station successfully.
        12) Client disconnects from the WLAN
        13) ZD failover
        14) Station associate the WLAN
        15) Get station wifi address
        16) Verify client status is 'authorized' and client can ping target station successfully.
        17) Client disconnects from the WLAN
        18) ZD failover back to initial status
        19) Delete WLAN

Created on 2013-04-17
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

def _define_wlan_cfg(type='standard', auth='open', wpa_ver = '', encryption = 'none', key_index = '1', key_string = '', 
                     sta_auth = '', sta_wpa_ver = '', sta_encryption = '', 
                     vlan_id = ''):
    wlan_cfg = dict(ssid='rat-autonomous', auth=auth, wpa_ver=wpa_ver, encryption=encryption, key_index=key_index, key_string=key_string,
                    sta_auth=sta_auth, sta_wpa_ver=sta_wpa_ver, sta_encryption=sta_encryption)
    
    wlan_cfg['type'] = type

    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id
    
    return wlan_cfg

def define_test_cfg(cfg, wlan_cfg_params):
    test_cfgs = []
    target_ip_addr = cfg['target_ping_ip_addr']

    radio_mode = cfg['radio_mode']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'

    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
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

    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))

    index = 0
    for wlan_cfg_param in wlan_cfg_params:
        wlan_cfg = _define_wlan_cfg('autonomous', wlan_cfg_param[0], wlan_cfg_param[1], wlan_cfg_param[2], wlan_cfg_param[3], wlan_cfg_param[4],\
                                    wlan_cfg_param[5], wlan_cfg_param[6], wlan_cfg_param[7], cfg['vlan_id'])
    
#        test_case_name = "[Client association in active and standby ZD]"
        index += 1
        if index == 1:
            test_case_name = "[%s %s]" % (wlan_cfg['auth'], wlan_cfg['encryption'])
        elif index in [2,3,6,7]:
            test_case_name = "[%s %s %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'], wlan_cfg['encryption'])
        elif index in [4,5,8,9]:
            test_case_name = "[%s %s %s sta %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_encryption'])
        elif index in [10,11,12,13]:
            test_case_name = "[%s %s %s sta %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'])
        elif index in [14,15,16,17]:
            test_case_name = "[%s %s %s sta %s %s]" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'], wlan_cfg['sta_encryption'])
        elif index in [18,19]:
            test_case_name = "[%s %s]" % (wlan_cfg['auth'], wlan_cfg['encryption'])
        else:
            pass

        ########################################## case 1 ############################################################
        test_case_name_1 = "[WLAN parameter synchronize - %s]" % test_case_name.replace("[","").replace("]","")
    
        test_name = 'CB_ZD_SR_WLAN_Sync_Testing'
        common_name = '%sSynchronization testing on ZD' % (test_case_name_1)
        test_cfgs.append(({'wlan_cfg':wlan_cfg, 
                           }, test_name, common_name, 1, False))

        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sCreate autonomous WLAN on ZD' % (test_case_name)
        test_cfgs.append(({'wlan_cfg_list':[wlan_cfg], 
                           'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 1, False))
    
        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station' % (test_case_name)
        test_cfgs.append(({'wlan_cfg': wlan_cfg,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet WiFi address of the station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
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
    
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_SR_Failover'
        common_name = '%sFailover the active ZD' % (test_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station in standby ZD' % (test_case_name)
        test_cfgs.append(({'wlan_cfg': wlan_cfg,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet WiFi address of the station in standby ZD' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify client information Authorized status in standby ZD' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg,
                           'radio_mode':sta_radio_mode,},
                           test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP in standby ZD' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))
    
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station in standby ZD' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
            
        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = '%sRemove all the WLANs from ZD' % (test_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, True))
    
        test_name = 'CB_ZD_SR_Failover'
        common_name = '%sFailover the active ZD to initial status' % (test_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, True))


    #Recover test environment
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD after test'
    test_cfgs.append(({},test_name, common_name, 0, True))

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
            'target_url': 'http://172.16.10.252/',
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
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

#    select_option = raw_input("\n\
#    1.  Open None\n\
#    2.  WPA+TKIP\n\
#    3.  WPA+AES\n\
#    4.  WPA+AUTO,       station WPA+TKIP\n\
#    5.  WPA+AUTO,       station WPA+AES\n\
#    6.  WPA2+TKIP\n\
#    7.  WPA2+AES\n\
#    8.  WPA2+AUTO,      station WPA2+TKIP\n\
#    9.  WPA2+AUTO,      station WPA2+AES\n\
#    10. WPA_Mixed+TKIP, station WPA+TKIP\n\
#    11. WPA_Mixed+TKIP, station WPA2+TKIP\n\
#    12. WPA_Mixed+AES,  station WPA+AES\n\
#    13. WPA_Mixed+AES,  station WPA2+AES\n\
#    14. WPA_Mixed+AUTO, station WPA+TKIP\n\
#    15. WPA_Mixed+AUTO, station WPA+AES\n\
#    16. WPA_Mixed+AUTO, station WPA2+TKIP\n\
#    17. WPA_Mixed+AUTO, station WPA2+AES\n\
#    18. WEP-64\n\
#    19. WEP-128\n\n\
#    Select encryption type of Autonomous WLAN[1-19, default is 1 <Open None>]: ")
#    
#    if not select_option or int(select_option) not in range(1,20):
#        select_option = 1

    test_cfgs = define_test_cfg(tcfg, list)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Autonomous WLAN SR"

    ts = testsuite.get_testsuite(ts_name, ("Autonomous WLAN SR"), combotest=True)

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
