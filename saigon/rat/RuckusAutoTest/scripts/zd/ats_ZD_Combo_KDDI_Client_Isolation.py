"""
@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: May, 2012

This suite includes the KDDI related test cases for client isolation.
Required: 2 W7 clients
          L3 connection APs
"""

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_WlanGroup_cfg(wlan_cfgs):
    wlangroup_cfg = {}
   
    wlangroup_cfg['client-isolation-wlangroup-1'] = [wlan_cfgs[i]['ssid'] for i in range(6)]
    wlangroup_cfg['client-isolation-wlangroup-2'] = [wlan_cfgs[6]['ssid']]
    wlangroup_cfg['client-isolation-wlangroup-3'] = [wlan_cfgs[7]['ssid']]

    return wlangroup_cfg

def define_Wlan_cfg(radius_server_name, hotspot_profile_name):
    wlan_cfgs = []
    
    wlan_cfgs.append(dict(ssid = 'isolation-01', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "", 
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, do_tunnel = True,
                           do_isolation = "full"))

    wlan_cfgs.append(dict(ssid = 'isolation-01-vlan-10', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "", vlan_id = '10',
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, do_tunnel = True,
                           do_isolation = "full"))
    
    wlan_cfgs.append(dict(ssid = 'isolation-01-dynamic-vlan', auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                           sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = "", dvlan = True,
                           username = "", password = "", auth_svr = radius_server_name, ras_port = "",
                           ras_secret = "", use_radius = True, do_tunnel = True,
                           do_isolation = "full"))
    
    wlan_cfgs.append(dict(ssid = 'isolation-02', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, do_tunnel = True,
                           do_isolation = "full"))

    wlan_cfgs.append(dict(ssid = 'isolation-02-vlan-10', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "", vlan_id = '10',
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, do_tunnel = True,
                           do_isolation = "full"))
    
    wlan_cfgs.append(dict(ssid = 'isolation-02-dynamic-vlan', auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                           sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = "", dvlan = True,
                           username = "", password = "", auth_svr = radius_server_name, ras_port = "",
                           ras_secret = "", use_radius = True, do_tunnel = True,
                           do_isolation = "full"))
    
    wlan_cfgs.append(dict(ssid = 'isolation-03-guest-access', type='guest', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, do_tunnel = True,
                           do_isolation = "full"))
    
    wlan_cfgs.append(dict(ssid = 'isolation-04-hotspot', type = 'hotspot', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, do_tunnel = True,
                           hotspot_profile = hotspot_profile_name))   
    
    return wlan_cfgs


def define_test_cfg(cfg):
    test_cfgs = []

    test_name = 'CB_ZD_Create_Station'
    common_name = 'get the station %s' % cfg['target_station_01']
    test_cfgs.append(( {'sta_ip_addr':cfg['target_station_01'],
                        'sta_tag': 'STA1'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'get the station %s' % cfg['target_station_02']
    test_cfgs.append(( {'sta_ip_addr':cfg['target_station_02'],
                        'sta_tag': 'STA2'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'get the active %s' % cfg['active_ap_1']
    test_cfgs.append(({'active_ap':cfg['active_ap_1'],
                       'ap_tag': 'AP1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'get the active %s' % cfg['active_ap_2']
    test_cfgs.append(({'active_ap':cfg['active_ap_2'],
                       'ap_tag': 'AP2'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'create_local_user %s' % cfg['local_user']
    test_cfgs.append((cfg['local_user'], test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'create radius server %s' % cfg['aaa_server']['server_name']
    test_cfgs.append(({'auth_ser_cfg_list': [cfg['aaa_server']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = 'create hotspot profile %s' % cfg['hotspot_profile']['name']
    test_cfgs.append(({'hotspot_profiles_list': [cfg['hotspot_profile']]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlans'
    common_name = "create the expected WLANs for test on ZD"
    test_cfgs.append(( {'wlan_cfg_list': cfg['wlan_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_WLANGroups_with_WLANs'
    common_name = 'create expected wlan groups for test on ZD'
    test_cfgs.append(({'wlangroups_map': cfg['wgs_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group'
    common_name = 'remove all wlans from default wlan group'
    wlan_list = [wlan['ssid'] for wlan in cfg['wlan_cfg_list']]
    test_cfgs.append(({'wlan_name_list': wlan_list}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = 'assign active ap AP1 to wlangroup "client-isolation-wlangroup-1"'
    test_cfgs.append(({'active_ap': 'AP_01', 'wlan_group_name': 'client-isolation-wlangroup-1', 'radio_mode': cfg['radio_mode']},
                      test_name, common_name, 0, False))
    
    #@author: Jane.Guo @since: 2013-06-27 add a step to add acls of guest access.
    restricted_subnet_list = ['10.0.0.0/8',
                               '172.16.0.0/12',
                               '192.168.0.0/16',]
    test_name = 'CB_ZD_Set_Guest_Restricted_Subnet_Access'
    common_name = 'Add restricted subnet access'
    test_params = {'restricted_subnet_list': restricted_subnet_list}
    test_cfgs.append((test_params,test_name, common_name, 0, False))
    
    zd_subnet = '192.168.0.0/255.255.255.0'
    vlan2_subnet = '20.0.2.0/255.255.255.0'
    vlan10_subnet = '192.168.10.0/255.255.255.0'
    vlan20_subnet = '192.168.20.0/255.255.255.0'
    vlan10_user = {'username':'finance.user', 'password':'finance.user'}
    vlan20_user = {'username':'marketing.user', 'password':'marketing.user'}
    
    #
    testcase = 'Isolation on 1 AP - same wlan'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][0]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'sta_tag': 'STA1', 
                        'expected_subnet': zd_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][0]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'sta_tag': 'STA2',
                        'expected_subnet': zd_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    testcase = 'Isolation on 1 AP - same wlan - same vlan'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][1]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'sta_tag': 'STA1', 
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][1]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'sta_tag': 'STA2',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))

    #
    testcase = 'Isolation on 1 AP - same wlan - different dynamic vlans'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][2]['ssid'])
    wlan_cfg1 = dict(cfg['wlan_cfg_list'][2])
    wlan_cfg1.update(vlan10_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg1, 'sta_tag': 'STA1', 
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][2]['ssid'])
    wlan_cfg2 = dict(cfg['wlan_cfg_list'][2])
    wlan_cfg2.update(vlan20_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg2, 'sta_tag': 'STA2',
                        'expected_subnet': vlan20_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    testcase = 'Isolation on 1 AP - different wlans'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][0]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'sta_tag': 'STA1', 
                        'expected_subnet': zd_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][3]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][3], 'sta_tag': 'STA2',
                        'expected_subnet': zd_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    testcase = 'Isolation on 1 AP - different  wlans - same vlan'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][1]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'sta_tag': 'STA1', 
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][4]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][4], 'sta_tag': 'STA2',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))

    #
    testcase = 'Isolation on 1 AP - different wlans - different dynamic vlans'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][2]['ssid'])
    wlan_cfg3 = dict(cfg['wlan_cfg_list'][2])
    wlan_cfg3.update(vlan10_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg3, 'sta_tag': 'STA1', 
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    wlan_cfg4 = dict(cfg['wlan_cfg_list'][5])
    wlan_cfg4.update(vlan20_user)
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][5]['ssid'])
    test_cfgs.append(( {'wlan_cfg': wlan_cfg4, 'sta_tag': 'STA2',
                        'expected_subnet': vlan20_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    # 2 APs
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = 'assign active ap AP2 to wlangroup "client-isolation-wlangroup-1"'
    test_cfgs.append(({'active_ap': 'AP_02', 'wlan_group_name': 'client-isolation-wlangroup-1', 'radio_mode': cfg['radio_mode']},
                      test_name, common_name, 0, False))
    
    testcase = 'Isolation on 2 APs - same wlan'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s" on AP1' % (testcase, cfg['wlan_cfg_list'][0]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'sta_tag': 'STA1', 'ap_tag': 'AP1',
                        'expected_subnet': zd_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s" on AP2' % (testcase, cfg['wlan_cfg_list'][0]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'sta_tag': 'STA2', 'ap_tag': 'AP2',
                        'expected_subnet': zd_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    testcase = 'Isolation on 2 APs - same wlan - same vlan'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s" on AP1' % (testcase, cfg['wlan_cfg_list'][1]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'sta_tag': 'STA1', 'ap_tag': 'AP1',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s" on AP2' % (testcase, cfg['wlan_cfg_list'][1]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'sta_tag': 'STA2', 'ap_tag': 'AP2',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))

    #
    testcase = 'Isolation on 2 APs - same wlan - different dynamic vlans'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s" on AP1' % (testcase, cfg['wlan_cfg_list'][2]['ssid'])
    wlan_cfg5 = dict(cfg['wlan_cfg_list'][2])
    wlan_cfg5.update(vlan10_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg5, 'sta_tag': 'STA1', 'ap_tag': 'AP1',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s" on AP2' % (testcase, cfg['wlan_cfg_list'][2]['ssid'])
    wlan_cfg6 = dict(cfg['wlan_cfg_list'][2])
    wlan_cfg6.update(vlan20_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg6, 'sta_tag': 'STA2', 'ap_tag': 'AP2',
                        'expected_subnet': vlan20_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
        #
    testcase = 'Isolation on 2 APs - different wlans'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s" on AP1' % (testcase, cfg['wlan_cfg_list'][0]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'sta_tag': 'STA1', 'ap_tag': 'AP1',
                        'expected_subnet': zd_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s" on AP2' % (testcase, cfg['wlan_cfg_list'][3]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][3], 'sta_tag': 'STA2', 'ap_tag': 'AP2',
                        'expected_subnet': zd_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1,
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    testcase = 'Isolation on 2 APs - different  wlans - same vlan'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s" on AP1' % (testcase, cfg['wlan_cfg_list'][1]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'sta_tag': 'STA1', 'ap_tag': 'AP1',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s" on AP2' % (testcase, cfg['wlan_cfg_list'][4]['ssid'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][4], 'sta_tag': 'STA2', 'ap_tag': 'AP2',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))

    #
    testcase = 'Isolation on 2 APs - different wlans - different dynamic vlans'

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s" on AP1' % (testcase, cfg['wlan_cfg_list'][2]['ssid'])
    wlan_cfg7 = dict(cfg['wlan_cfg_list'][2])
    wlan_cfg7.update(vlan10_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg7, 'sta_tag': 'STA1', 'ap_tag': 'AP1',
                        'expected_subnet': vlan10_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s" on AP2' % (testcase, cfg['wlan_cfg_list'][5]['ssid'])
    wlan_cfg8 = dict(cfg['wlan_cfg_list'][5])
    wlan_cfg8.update(vlan20_user)
    test_cfgs.append(( {'wlan_cfg': wlan_cfg8, 'sta_tag': 'STA2', 'ap_tag': 'AP2',
                        'expected_subnet': vlan20_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = 'assign active ap AP1 to wlangroup "client-isolation-wlangroup-2"'
    test_cfgs.append(({'active_ap': 'AP_01', 'wlan_group_name': 'client-isolation-wlangroup-2', 'radio_mode': cfg['radio_mode']},
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = 'assign active ap AP2 back to Default wlan group'
    test_cfgs.append(({'active_ap': 'AP_02', 'wlan_group_name': 'Default', 'radio_mode': cfg['radio_mode']},
                      test_name, common_name, 0, False))
    
    testcase = 'Isolation on guest wlan'
    wlan_cfg9 = dict(cfg['wlan_cfg_list'][6])
    wlan_cfg9.update(cfg['local_user'])
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][6]['ssid'])
    test_cfgs.append(( {'wlan_cfg': wlan_cfg9, 'sta_tag': 'STA1', 
                        'expected_subnet': zd_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][6]['ssid'])
    test_cfgs.append(( {'wlan_cfg': wlan_cfg9, 'sta_tag': 'STA2',
                        'expected_subnet': zd_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    #
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = 'assign active ap AP1 to wlangroup "client-isolation-wlangroup-3"'
    test_cfgs.append(({'active_ap': 'AP_01', 'wlan_group_name': 'client-isolation-wlangroup-3', 'radio_mode': cfg['radio_mode']},
                      test_name, common_name, 0, False))
    
    testcase = 'Isolation on hotspot wlan'
    wlan_cfg10 = dict(cfg['wlan_cfg_list'][7])
    wlan_cfg10.update(cfg['local_user'])
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA1 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][7]['ssid'])
    test_cfgs.append(( {'wlan_cfg': wlan_cfg10, 'sta_tag': 'STA1', 
                        'expected_subnet': zd_subnet}, test_name, common_name, 1, False))

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '[%s]: associate the station STA2 to wlan "%s"' % (testcase, cfg['wlan_cfg_list'][7]['ssid'])
    test_cfgs.append(( {'wlan_cfg':wlan_cfg10, 'sta_tag': 'STA2',
                        'expected_subnet': zd_subnet}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 1 to station 2' % testcase
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[%s]: can not ping from station 2 to station 1' % testcase
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 
                       'isolation_option': 'full'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 1 to station 2' % testcase
    test_cfgs.append(({'sta_tag': 'STA1', 'dest_sta_tag': 'STA2', 'allow': False}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Arping_Targets'
    common_name = '[%s]: can not arping from station 2 to station 1' % testcase
    test_cfgs.append(({'sta_tag': 'STA2', 'dest_sta_tag': 'STA1', 'allow': False}, test_name, common_name, 2, False))
    
    
    # cleanup
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'remove all wlans from the station 1 to clean up'
    test_cfgs.append(({'sta_tag': 'STA1'}, test_name, common_name, 0, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'remove all wlans from the station 2 to clean up'
    test_cfgs.append(({'sta_tag': 'STA2'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'remove all wlangroups setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'remove all wlans setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'remove all users setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'remove all hotspot setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'remove all authentication server setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta_01 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 1: ")
        target_sta_02 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 2: ")
    else:
        target_sta_01 = sta_ip_list[attrs["station1"][0]]
        target_sta_02 = sta_ip_list[attrs["station2"][0]]

    active_ap_1 = testsuite.getActiveAp(ap_sym_dict)[0]
    active_ap_2 = testsuite.getActiveAp(ap_sym_dict)[0]    
    
    local_user = {'username': 'user.local', 'password': 'user.local'}
    hotspot_profile = {'name': 'client isolation hotspot',
                       'login_page': 'http://192.168.0.250/login.html',
                       'idle_timeout': None,
                       'auth_svr': 'Local Database',
                       'client_isolation': 'full'}    
    aaa_server = dict(server_name = '192.168.0.252', type = 'radius-auth', backup = False, 
                      server_addr = '192.168.0.252', server_port = '1812', radius_auth_secret = '1234567890')
    
    wlan_cfg_list = define_Wlan_cfg(aaa_server['server_name'], hotspot_profile['name'])
    wlangroup_cfg = define_WlanGroup_cfg(wlan_cfg_list)
    
    tcfg = {'target_station_01':'%s' % target_sta_01,
            'target_station_02':'%s' % target_sta_02,
            'active_ap_1':'%s' % active_ap_1,
            'active_ap_2':'%s' % active_ap_2,
            'radio_mode': 'ng',
            'wlan_cfg_list': wlan_cfg_list,
            'wgs_cfg_list': wlangroup_cfg,
            'local_user': local_user,
            'hotspot_profile': hotspot_profile,
            'aaa_server': aaa_server,
            }
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else:
        ts_name = "Combo Client Full Isolation - L3 APs" 

    ts = testsuite.get_testsuite(ts_name,
                                "Verify client isolation with Full Isolation under L3 tunnel",
                                interactive_mode = attrs["interactive_mode"],
                                combotest=True)

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
