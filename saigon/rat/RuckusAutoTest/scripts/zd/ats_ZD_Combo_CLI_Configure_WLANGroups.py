'''
Created on 2011-1-20
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure wlan group commands in ZD CLI work well.

'''
#Update the data-plane steps by Jacky Luh@2011-09-27


import logging
import time
import copy
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def define_wlan_cfg_list():
    logging.info('Generate a list of the WLAN configuration')
    
    conf = {'ssid': '',
            'auth': 'open',
            'encryption': 'none',
            }
    
    wlan_cfg_list = []
    for i in range(4):
        cfg = copy.deepcopy(conf)
        ssid = "zdcli-wlan-%s-%d" % (time.strftime("%H%M%S"), i)
        cfg['ssid'] = ssid
        wlan_cfg_list.append(cfg)
    
    return wlan_cfg_list
                
                    
def define_wlan_group_cfg_list(wlan_cfg_list):
    logging.info('Generate a list of the WLAN group configuration')
    wlan_list = []
    for i in range(len(wlan_cfg_list)):
        wlan_list.append(wlan_cfg_list[i]['ssid'])
    
    wlan_member = {}
    wlan_member[wlan_list[0]] = {}
    wlan_member[wlan_list[1]] = {'vlan_override': 'none'}
    #wlan_member[wlan_list[2]] = {'vlan_override': 'untag'}
    wlan_member[wlan_list[2]] = {'vlan_override': 'tag', 'tag_override': '302',}
                
    wg_cfg_list = []
    wg_cfg_list.append(dict(wg_name = 'Default', description = 'Default WLANs for Access Points',
                             wlan_member = wlan_member))
    
    wg_name = "zdcli-wlan-group-%s" % time.strftime("%H%M%S")
    new_wg_name = "new-%s" % wg_name
    wg_cfg_list.append(dict(wg_name = wg_name, new_wg_name = new_wg_name, description = 'WLAN Group for Testing',
                            wlan_member = wlan_member))

    return wg_cfg_list
    
    
def define_test_cfg(cfg):
    test_cfgs = []
    dest_ip = '172.16.10.252'
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create WLANs in ZD GUI'
    test_cfgs.append(( {'wlan_cfg_list':cfg['wlan_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_WLAN_Groups'
    common_name = '[Configure WLAN Groups] Configure WLAN groups in ZD CLI'
    test_cfgs.append(( {'wg_cfg_list':cfg['wg_cfg_list']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_WlanGroup_All'
    common_name = '[Configure WLAN Groups] Get all WLAN groups info from ZD GUI'   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '[Configure WLAN Groups] Get all WLAN groups info from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup_All'
    common_name = '[Configure WLAN Groups] Verify all WLAN groups info'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    #Modified by Liang Aihua on 2014-11-4 for these steps not exist in database.
    #test_name = 'CB_ZD_Create_Station'
    #common_name = '[Configure WLAN Groups] Get the station'
    #test_params = {'sta_tag': 'sta1', 'sta_ip_addr': cfg['sta_ip_list'][0]}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Associate_Station_1'
    #common_name = '[Configure WLAN Groups] The station associated the wlan from default wlan group'
    #test_params = {'sta_tag': 'sta1', 'wlan_cfg': cfg['wlan_cfg_list'][0]}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    #common_name = '[Configure WLAN Groups] Get target station Wifi addresses'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    #common_name = '[Configure WLAN Groups] Client ping dest-ip[%s] which is allowed' % dest_ip
    #test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #test_name = 'CB_Station_Remove_All_Wlans'
    #common_name = '[Configure WLAN Groups] Remove the wlan from the station'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
    #common_name = '[Configure WLAN Groups] Uncheck all wlans member in default wlangroup'
    #test_cfgs.append(({}, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Create_Active_AP'
    #common_name = '[Configure WLAN Groups] Get the active ap'
    #test_params = {'ap_tag': 'active_ap', 'active_ap': cfg['active_aps_mac_list'][0]}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #radio_mode = cfg['radio_mode']
    #if radio_mode == 'bg':
    #    radio_mode = 'g'
    
    #for wg_n in cfg['wg_cfg_list']:
    #    if wg_n.has_key('new_wg_name') and wg_n['new_wg_name']:
    #        wg_name = wg_n['new_wg_name']
    
    #test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    #common_name = '[Configure WLAN Groups] Assign the active ap to the new wlangroup'
    #test_cfgs.append(({'active_ap': cfg['active_ap_list'][0],
    #                   'wlan_group_name': wg_name,
    #                   'radio_mode': radio_mode}, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Associate_Station_1'
    #common_name = '[Configure WLAN Groups] The station associated the wlan from newly wlangroup'
    #test_params = {'sta_tag': 'sta1', 'wlan_cfg': cfg['wlan_cfg_list'][0]}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    #common_name = '[Configure WLAN Groups] Get target station Wifi addresses from newly wlan ssid'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    #common_name = '[Configure WLAN Groups] Client ping dest-ip[%s] which is allowed from newly wlan ssid.' % dest_ip
    #test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #test_name = 'CB_Station_Remove_All_Wlans'
    #common_name = '[Configure WLAN Groups] Remove the newly wlan from the station'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    #common_name = '[Configure WLAN Groups] Assign the active ap to default wlangroup'
    #test_cfgs.append(({'active_ap': cfg['active_ap_list'][0],
    #                   'wlan_group_name': 'Default',
    #                   'radio_mode': radio_mode}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Remove_All_WLAN_Groups'
    common_name = '[Remove All WLAN Groups] Remove all WLAN groups from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_WlanGroup_All'
    common_name = '[Remove All WLAN Groups] Get all WLAN groups info from ZD GUI'   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '[Remove All WLAN Groups] Get all WLAN groups info from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup_All'
    common_name = '[Remove All WLAN Groups] Verify all WLAN groups info'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD via GUI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = []
    active_aps_mac_list = []

    wlan_cfg_list = define_wlan_cfg_list()
    wg_cfg_list = define_wlan_group_cfg_list(wlan_cfg_list)
    
    target_sta_radio = testsuite.get_target_sta_radio() 
        
    fit_ap_model = dict() 
    for ap_sym_name, ap_info in ap_sym_dict.items(): 
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            fit_ap_model[ap_sym_name] = ap_info
    
    try:
        active_ap_list = testsuite.getActiveAp(fit_ap_model)
        print active_ap_list
        if not active_ap_list:
            raise Exception("No found the surpported ap in the testbed env.")
    except:
        raise Exception("No found the surpported ap in the testbed env.")
       
    for active_ap in active_ap_list:
        for u_ap in ap_sym_dict.keys():
            ap_mac = ap_sym_dict[u_ap]['mac']
            if u_ap == active_ap:
                active_aps_mac_list.append(ap_mac)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "ZD CLI Configure WLAN Group" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure WLAN group commands in ZD CLI work well" ,
                                 combotest=True)
    
    tcfg = {'wlan_cfg_list': wlan_cfg_list,
            'wg_cfg_list': wg_cfg_list,
            'active_ap_list': active_ap_list,
            'active_aps_mac_list': active_aps_mac_list,
            'sta_ip_list': sta_ip_list,
            'radio_mode': target_sta_radio,
            }
    
    test_cfgs = define_test_cfg(tcfg)
 
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
    