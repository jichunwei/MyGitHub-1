"""
Mesh

Mesh

1. Set up mesh enviorment, wait mesh set up

   2 Root 2 Mesh

2. Enable 1 Mesh AP's 5G service(daul band 5G, single band 2.4G), Station connects to Mesh AP

3. [Check Mesh uplink selection setting in AP CLI]Mesh,AP CLI configuraton, set rssi, check all AP's status, set default, check all AP's status, check Station connect

4. [Throughput to station]Start Throughput to Station, check all AP's status, no reset event. send 3 minutes and then sleep 5 minutes

(Station will disconnect when MeshAP change uplink)

5. [Reboot root AP]Root AP1 reboot,Root AP2 reboot

6. [Manual uplink selection]Set 1 mesh manual uplink selection, check all AP's status

7. Start Throughput to Station, check all AP's status, no reset event. 2 times, each time 3 minutes and then sleep 5 minutes

8. [eMesh]Set up emesh enviorment, wait eMesh set up

   1 Root 1 Mesh 2 eMesh

9. eMesh AP, AP CLI configuraton, set rssi, check all AP's status, set default, check all AP's status, check Station connect

10. Start Throughput to Station, check all AP's status, no reset event. 2 times, each time 3 minutes and then sleep 5 minutes
    
Created on 2013-11
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

wlan_cfg = {"name" : "Rqa-auto-RAT-Uplink-Mesh-1",
            "ssid" : "Rqa-auto-RAT-Uplink-Mesh-1",
            "auth" : "open",
            "encryption" : "none",
            }
server_ip = '192.168.0.252'


def build_tcs(sta1_ip_addr, all_aps_mac_list, active_ap1, active_ap1_mac, active_ap2, active_ap2_mac, active_ap3, active_ap3_mac, active_ap4, active_ap4_mac, target_sta_radio):
    tcs = []
                  
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
  
    tcs.append(({'active_ap': active_ap1,
                 'ap_tag':'AP_01'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Root AP_01',
                0,
                False))

    tcs.append(({'active_ap': active_ap2,
                 'ap_tag':'AP_02'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Root AP_02',
                0,
                False))

    tcs.append(({'active_ap': active_ap3,
                 'ap_tag':'AP_03'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Mesh AP_03',
                0,
                False))

    tcs.append(({'active_ap': active_ap4,
                 'ap_tag':'AP_04'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Mesh AP_04',
                0,
                False))

    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': sta1_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 1', 
                   0, 
                   False))

    tcs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_02',
                       'test_option': 'form_mesh_mesh_acl',
                       'vlan':'779'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Setting up mesh ap AP_02', 
                   0, 
                   False))    
    
    tcs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_03',
                       'test_option': 'form_mesh_smart_acl'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Setting up mesh ap AP_03', 
                   0, 
                   False))
 
    tcs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_04',
                       'test_option': 'form_mesh_smart_acl',
                       'vlan':'778' }, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Setting up mesh ap AP_04', 
                   0, 
                   False))

    tcs.append(({'ap_list': ['AP_02'],
                       'test_option': 'reconnect_as_root'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Reconnect AP_02 as Root', 
                   0, 
                   False))
    
    tcs.append(({'cfg_type': 'init', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Config All APs Radio - Disable WLAN Service', 
                 0, 
                 False))
    
    tcs.append(({'ap_tag': 'AP_03',                      
                 'cfg_type': 'config',
                 'ap_cfg': {'wlan_service': True, 'radio': target_sta_radio}},
                 'CB_ZD_Config_AP_Radio',
                 'Config active AP Radio %s - Enable WLAN Service %s' % (active_ap3,target_sta_radio),
                 0, 
                 False))
    
    tcs.append(({'wlan_conf':wlan_cfg},
                'CB_ZD_CLI_Create_Wlan',
                'Create WLAN 1 from CLI',
                0,
                False)) 
        
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  'Associate the station', 
                  0, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  'Ping Dest is Allowed', 
                  0, 
                  False))  
    
    tc_name="[Check Mesh uplink selection setting in AP CLI]"
    #AP CLI change and check
    tcs.append(({'ap_tag': 'AP_03',
                 'type': 'rssi'}, 
                 'CB_AP_CLI_Set_Mesh_Uplink_Selection', 
                  '%sSet mesh uplink selection to rssi' % tc_name, 
                  1, 
                  False))  

    tcs.append(({'ap_tag': 'AP_03',
                 'type': 'default'}, 
                 'CB_AP_CLI_Set_Mesh_Uplink_Selection', 
                  '%sSet mesh uplink selection to default' % tc_name, 
                  2, 
                  True)) 

    tc_name="[Throughput to station]"
    tcs.append(({}, 
                 'CB_ZD_Clear_Event', 
                  "%sClear zd all event through Web" % tc_name, 
                  1, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1',
                   'zapd_sta': server_ip,
                   'duration':'180', 
                   'up_speed':'100',}, 
                 'CB_ZD_Start_Back_Ground_Traffic', 
                  "%sStart back ground traffic between client and linux server" % tc_name, 
                  2, 
                  False))
    
    wait_time = 280
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds' % (tc_name, wait_time), 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station after enable traffic' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after enable traffic' %tc_name, 
                  2, 
                  False))
    
    tcs.append(({'event':'reboot',
                 'negative': True}, 
                 'CB_ZD_Check_Event', 
                  "%sCheck no reboot event" % tc_name, 
                  2, 
                  False))
       
    tc_name="[Reboot root AP]"
    tcs.append(({'ap_tag': 'AP_01',}, 
                 'CB_ZD_Reboot_AP', 
                  '%sAP_01 reboot' % tc_name, 
                  1, 
                  False))    

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station after root AP reboot 1st time' % tc_name, 
                  2, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after root AP reboot 1st time' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ap_tag': 'AP_02',
                 'status': 'Connected (Root AP)'}, 
                 'CB_ZD_Verify_AP_Status', 
                  '%sCheck AP_02 status after AP_01 reboot' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'ap_tag': 'AP_03',
                 'status': 'Connected (Mesh AP'}, 
                 'CB_ZD_Verify_AP_Status', 
                  '%sCheck AP_03 status after AP_01 reboot' % tc_name, 
                  2, 
                  False))

    tcs.append(({'ap_tag': 'AP_04',
                 'status': 'Connected (Mesh AP'}, 
                 'CB_ZD_Verify_AP_Status', 
                  '%sCheck AP_04 status after AP_01 reboot' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ap_tag': 'AP_02',}, 
                 'CB_ZD_Reboot_AP', 
                  '%sAP_02 reboot' % tc_name, 
                  2, 
                  False))    

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station after root AP reboot 2nd time' % tc_name, 
                  2, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after root AP reboot 2nd time'% tc_name, 
                  2, 
                  False))

    tcs.append(({'ap_tag': 'AP_01',
                 'status': 'Connected (Root AP)'}, 
                 'CB_ZD_Verify_AP_Status', 
                  '%sCheck AP_01 status after AP_02 reboot'% tc_name, 
                  2, 
                  False)) 

    tcs.append(({'ap_tag': 'AP_03',
                 'status': 'Connected (Mesh AP'}, 
                 'CB_ZD_Verify_AP_Status', 
                  '%sCheck AP_03 status after AP_02 reboot'% tc_name, 
                  2, 
                  False))

    tcs.append(({'ap_tag': 'AP_04',
                 'status': 'Connected (Mesh AP'}, 
                 'CB_ZD_Verify_AP_Status', 
                  '%sCheck AP_04 status after AP_02 reboot'% tc_name, 
                  2, 
                  False))  
    
    tc_name = "[Manual uplink selection]"
    tcs.append(({'ap_list': ['AP_04'],
                    'test_option': 'reconnect_as_root'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   '%sReconnect AP_04 as Root' % tc_name, 
                   1,
                   False))

    tcs.append(({'root_ap': 'AP_01',
                    'mesh_ap': 'AP_04',
                    'test_option': 'form_mesh_mesh_acl',
                    'vlan':'778' }, 
                   'CB_ZD_Mesh_Provisioning', 
                   '%sSetting up mesh ap AP_04 by manual' % tc_name, 
                   2, 
                   False))
    
    tcs.append(({}, 
                 'CB_ZD_Clear_Event', 
                  "%sClear zd all event through Web" % tc_name, 
                  2, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1',
                   'zapd_sta': server_ip,
                   'duration':'180', 
                   'up_speed':'100',}, 
                 'CB_ZD_Start_Back_Ground_Traffic', 
                  "%sStart back ground traffic between client and linux server" % tc_name, 
                  2, 
                  False))
    
    wait_time = 280
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds' % (tc_name, wait_time), 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station after enable traffic' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after enable traffic' %tc_name, 
                  2, 
                  False))
    
    tcs.append(({'event':'reboot',
                 'negative': True}, 
                 'CB_ZD_Check_Event', 
                  "%sCheck no reboot event" % tc_name, 
                  2, 
                  False))  
    
    #---------------------------------------------eMesh---------------------------------
    tc_name="[eMesh]"
    tcs.append(({'ap_list': ['AP_02', 'AP_03','AP_04'],
                       'test_option': 'reconnect_as_root'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   '%sReconnect all active APs as Root' % tc_name, 
                   1, 
                   False))

    tcs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_02',
                       'emesh_ap': ['AP_03','AP_04'],
                       'test_option': 'form_emesh_smart_acl'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   '%sSetting up Mesh AP AP_02, eMesh AP AP_03,AP_04' % tc_name, 
                   2, 
                   False))

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed' % tc_name, 
                  2, 
                  False))  
    
    tcs.append(({'ap_tag': 'AP_03',
                 'type': 'rssi'}, 
                 'CB_AP_CLI_Set_Mesh_Uplink_Selection', 
                  '%sSet mesh uplink selection to rssi' % tc_name, 
                  2, 
                  False))

    tcs.append(({'ap_tag': 'AP_03',
                 'type': 'default'}, 
                 'CB_AP_CLI_Set_Mesh_Uplink_Selection', 
                  '%sSet mesh uplink selection to default' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({}, 
                 'CB_ZD_Clear_Event', 
                  "%sClear zd all event through Web" % tc_name, 
                  2, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1',
                   'zapd_sta': server_ip,
                   'duration':'180', 
                   'up_speed':'100',}, 
                 'CB_ZD_Start_Back_Ground_Traffic', 
                  "%sStart back ground traffic between client and linux server" % tc_name, 
                  2, 
                  False))
    
    wait_time = 280
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds' % (tc_name, wait_time), 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station after enable traffic' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after enable traffic' %tc_name, 
                  2, 
                  False))
    
    tcs.append(({'event':'reboot',
                 'negative': True}, 
                 'CB_ZD_Check_Event', 
                  "%sCheck no reboot event" % tc_name, 
                  2, 
                  False))
            
    tcs.append(({'ap_list': ['AP_01', 'AP_02', 'AP_03','AP_04'],
                       'test_option': 'reconnect_as_root'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Reconnect all active APs as Root', 
                   0, 
                   True))
            
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                True))

    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Mesh uplink selection enhancement"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
        
    sta1_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the first wireless station: ")
    
    if not sta1_ip_addr:
        raise Exception("Get station fail, sta1: %s" % sta1_ip_addr)
    
    print "\n--------IMPORTANT: Please select radio------------\n"
    print "if APs are dual band AP, please select na, make sure station support na.\nIf APs are single band AP,please select ng."
    target_sta_radio = testsuite.get_target_sta_radio()
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    if len(active_ap_list) < 4:
        raise Exception("Need four active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    active_ap1_mac = ap_sym_dict[active_ap1]['mac']
    
    active_ap2 = active_ap_list[1]
    active_ap2_mac = ap_sym_dict[active_ap2]['mac']

    active_ap3 = active_ap_list[2]
    active_ap3_mac = ap_sym_dict[active_ap3]['mac']

    active_ap4 = active_ap_list[3]
    active_ap4_mac = ap_sym_dict[active_ap4]['mac']
    
    ts_name = attrs['testsuite_name']    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Mesh uplink selection enhancement", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, all_aps_mac_list, active_ap1, active_ap1_mac, active_ap2, active_ap2_mac, active_ap3, active_ap3_mac, active_ap4, active_ap4_mac, target_sta_radio)

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
    