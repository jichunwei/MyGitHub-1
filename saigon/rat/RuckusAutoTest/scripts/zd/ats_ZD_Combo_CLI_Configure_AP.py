'''
Created on 2011-2-17
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure AP 
             commands in ZD CLI work well.

Request: 
    Enable mesh in ZD.

'''


import sys
import time
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_Constant
from RuckusAutoTest.common import lib_KwList as kwlist
                

def define_ap_cfgs(ap_mac_addr, active_radio, wg_cfg, mesh_uplink_aps):
    radio_mode = 'radio_%s' % active_radio
    radio_digit = '2.4' if 'g' in active_radio else '5'
    ap_cfg_list = []
    
    tcid = '[Set %sGHz radio config and AP basic info randomly]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'tcid': tcid})

    tcid = '[Set %sGHz radio config to Auto]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        radio_mode: {'channelization': 'Auto',
                                     'channel': 'Auto',
                                     'power': 'Auto',
                                     'wlangroups': wg_cfg['name']},
                        'tcid': tcid})
    
    tcid = '[Set %sGHz radio TX power to Full]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        radio_mode: {'power': 'Full',
                                     'wlangroups': wg_cfg['name']},
                        'tcid': tcid})
    
    tcid = '[Set %sGHz radio TX power to 1/2]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        radio_mode: {'power': '1/2',
                                     'wlangroups': wg_cfg['name']},
                        'tcid': tcid})
    
    tcid = '[Set %sGHz radio TX power to 1/4]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        radio_mode: {'power': '1/4',
                                     'wlangroups': wg_cfg['name']},
                        'tcid': tcid})

    tcid = '[Set %sGHz radio TX power to 1/8]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        radio_mode: {'power': '1/8',
                                     'wlangroups': wg_cfg['name']},
                        'tcid': tcid})
    
    tcid = '[Set %sGHz radio TX power to Min]' % radio_digit
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        radio_mode: {'power': 'Min',
                                     'wlangroups': wg_cfg['name']},
                        'tcid': tcid})
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'port_override': True,
                        'tcid': '[Enable override the global port setting]'})
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'port_override': False,
                        'tcid': '[Disable override the global port setting]'})   

    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'network_setting': {'ip_mode': 'dhcp'},
                        'tcid': '[Set IP address mode to DHCP]'}) 
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'network_setting': {'ip_mode': 'keep'},
                        'tcid': '[Set IP address mode to use its current setting]'})
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'network_setting': {'ip_mode': 'static',
                                            'ip_addr': '192.168.32.%d' % random.randint(205, 249),
                                            'net_mask': '255.255.255.0',
                                            'gateway': '192.168.32.253',
                                            'pri_dns': '192.168.0.252',
                                            },
                        'tcid': '[Set IP address manually with gateway]'})

    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'network_setting': {'ip_mode': 'static',
                                            'ip_addr': '192.168.32.%d' % random.randint(205, 249),
                                            'net_mask': '255.255.255.0',
                                            'pri_dns': '192.168.0.252',
                                            'sec_dns': '192.168.0.250'},
                        'tcid': '[Set IP address manually with second DNS server]'})
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'mesh_mode': 'root-ap',
                        'tcid': '[Set mesh mode to Root AP]'})
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'mesh_mode': 'mesh-ap',
                        'mesh_uplink_mode': 'Manual',
                        'mesh_uplink_aps': mesh_uplink_aps,
                        'tcid': '[Set mesh mode to Mesh AP and add uplink APs manually]'}) 

    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'mesh_mode': 'mesh-ap',
                        'mesh_uplink_mode': 'Manual',
                        'mesh_uplink_aps': [],
                        'tcid': '[Set mesh mode to Mesh AP and delete all uplink APs manually]'}) 
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'mesh_mode': 'auto',
                        'mesh_uplink_mode': 'Smart',
                        'tcid': '[Set mesh mode to Auto and mesh uplink mode to Smart]'})
    
    ap_cfg_list.append({'mac_addr': ap_mac_addr,
                        'mesh_mode': 'disable',
                        'tcid': '[Disable mesh mode]'})

    return ap_cfg_list

    
def define_data_plan_test_cfg(sta_tag, wlan_cfg, tcid):
    test_cfgs = []
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%s Station associate wlan and get wifi address' % tcid
    test_cfgs.append(({'wlan_cfg': wlan_cfg, 'sta_tag': sta_tag}, 
                      test_name, common_name, 2, False))
    
    #test_name = 'CB_Station_CaptivePortal_Download_File'
    #common_name = '%s Station download file from web server' % tcid
    #test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
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
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable Mesh on ZD before test'
    test_param = {'for_upgrade_test':False}
    test_cfgs.append((test_param, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create a wlan'
    test_cfgs.append(({'wlan_cfg_list': [tcfg['wlan_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
    common_name = 'Remove all wlans from Default wlan group'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create a wlan group for the wlan"
    test_cfgs.append(({'wgs_cfg': tcfg['wg_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Backup_APs_Setting'
    common_name = 'Back up the AP settings before test'   
    test_cfgs.append(({'ap_mac_list': [tcfg['ap_mac_addr']]}, test_name, common_name, 0, False)) 
    
    
    for i in range(len(tcfg['ap_cfg_list'])):
        ap_cfg = tcfg['ap_cfg_list'][i]
        tcid = ap_cfg.pop('tcid')  
        
        if i == 0:
            test_name = 'CB_ZD_CLI_Generate_AP_Cfg'
            common_name = '%s Generate AP settings for ZD CLI' % tcid
            test_params = {'ap_mac_addr': tcfg['ap_mac_addr'], 
                           'active_radio': tcfg['active_radio'],
                           'wg_name': tcfg['wg_cfg']['name']}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
    
            test_name = 'CB_ZD_CLI_Configure_AP'
            common_name = '%s Configure AP in ZD CLI' % tcid
            test_cfgs.append(({}, test_name, common_name, 2, False))
        
        else:
            test_name = 'CB_ZD_CLI_Configure_AP'
            common_name = '%s Configure AP in ZD CLI' % tcid 
            test_cfgs.append(({'ap_cfg': ap_cfg}, test_name, common_name, 1, False)) 
            
        test_name = 'CB_ZD_Get_AP_Cfg'
        common_name = '%s Get AP settings from ZD GUI' % tcid
        test_cfgs.append(({'ap_mac_addr': tcfg['ap_mac_addr']}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Verify_AP_Cfg_With_GUI'
        common_name = '%s Verify AP settings in ZD GUI'% tcid  
        test_cfgs.append(({}, test_name, common_name, 2, False))
        
        if i < 7:
            test_cfgs.extend(define_data_plan_test_cfg(sta_tag, tcfg['wlan_cfg'], tcid))
    
    
    test_name = 'CB_ZD_Restore_APs_Setting'
    common_name = 'Restore the AP to original settings after test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all wlan groups from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Close browser in the station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_station = (0, "ng"),
                 uplink_ap_list = [],
                 testsuite_name = ""
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an active AP: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            
            else:
                break
        
        select_tips = "Select the uplink APs(Enter symbolic APs from above list, separated by space)"
        while True:
            uplink_ap_syms = raw_input(select_tips)
            uplink_ap_syms = uplink_ap_syms.split()
            if not uplink_ap_syms:
                continue
            
            for ap in uplink_ap_syms:
                if ap not in ap_sym_dict:
                    print "AP[%s] doesn't exist." % ap
                    continue

            break
        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio() 
        
    else:
        active_ap = attrs["active_ap"]
        uplink_ap_syms = attrs['uplink_ap_list']
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if target_sta_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, target_sta_radio)
        return
    
    active_radio = target_sta_radio
    
    uplink_mac_addr_list = []
    for ap in uplink_ap_syms:
        uplink_mac_addr_list.append(ap_sym_dict[ap]['mac'])
    
    wlan_cfg = dict(ssid = "rat-wlan-%s-1" % time.strftime("%H%M%S"), 
                    auth = 'open', encryption = 'none')
    
    wg_cfg = dict(name = 'rat_wlan_group', 
                  description = '',
                  vlan_override = False, 
                  wlan_member = {wlan_cfg['ssid']: {}})
    
    ap_cfg_list = define_ap_cfgs(ap_sym_dict[active_ap]['mac'], 
                                 active_radio, 
                                 wg_cfg, 
                                 uplink_mac_addr_list)
    
    tcfg = {'ap_mac_addr': ap_sym_dict[active_ap]['mac'],
            'sta_ip_addr': sta_ip_addr,
            'active_radio': active_radio,
            'wlan_cfg': wlan_cfg,
            'wg_cfg': wg_cfg,
            'ap_cfg_list': ap_cfg_list
            }
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "Mesh - ZD CLI - Configure AP Settings - %s" % active_radio
        #ts_name = "Mesh - ZD CLI - Configure AP Settings - %s - %s" % (active_ap_model, active_radio)
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure AP commands in ZD CLI work well",
                                 combotest = True)
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
    