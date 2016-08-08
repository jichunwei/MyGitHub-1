# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Jun 2013

This testsuite is configure to allow testing follow test cases - which are belong to Background scanning:


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_cfg(cfg):
    test_cfgs = []
    ap_tag = cfg['active_ap']
    
    tcname = {'ng': 'Background Scanning - 2.4G',
              'bg': 'Background Scanning - 2.4G',
              'na': 'Background Scanning - 5G',
              'a': 'Background Scanning - 5G',}[cfg['radio']]
    
    dis_all_wlan_service = {'radio_bg': {'wlan_service': 'No'},
                            'radio_ng': {'wlan_service': 'No'},
                            'radio_na': {'wlan_service': 'No'},
                            'radio_a': {'wlan_service': 'No'},}
    
    ap_conf = {'ng': {'radio_ng': {'wlan_service': 'Yes'}},
               'bg': {'radio_bg': {'wlan_service': 'Yes'}},
               'na': {'radio_na': {'wlan_service': 'Yes'}},
               'a': {'radio_a': {'wlan_service': 'Yes'}}}[cfg['radio']]
    
    scan_interval = 20
    service_cfg = {'scan_24g': True, 'scan_24g_interval': scan_interval,
                   'scan_5g': True, 'scan_5g_interval': scan_interval,}
    
    wlan_cfg_list = [{'ssid': 'BGSCAN WLAN1', 'bgscan': True},
                     {'ssid': 'BGSCAN WLAN2', 'bgscan': True}]
    disbg_wlan_cfg = {'ssid': 'BGSCAN WLAN1', 'bgscan': False}
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD and disable switch port connectet to ap %s,let it become mesh ap'% cfg['mesh_ap']
    test_cfgs.append(({'mesh_ap_list':cfg['mesh_ap'],
                       'for_upgrade_test':False},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = '[%s] Create active AP' % tcname
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))                
            
    test_name = 'CB_ZD_CLI_Configure_Service'
    common_name = '[%s] Enable background scanning service' % tcname
    test_cfgs.append(({'service_cfg': service_cfg}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = '[%s] Create WLANs' % tcname
    test_cfgs.append(({'wlan_cfg_list': wlan_cfg_list}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = '[%s] Disable the WLAN service on all radio' % tcname
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg': dis_all_wlan_service}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = '[%s] Enable WLAN server on %s radio' % (tcname, cfg['radio'])
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg': ap_conf}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Enable_80211debug_Mode'
    common_name = '[%s] Enable the 80211debug mode on AP CLI' % tcname
    test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Verify_Background_Scanning_Message'
    common_name = '[%s] Verify the scanning messages from "apmgr"' % tcname
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_msg': 'apmgr',
                       'scan_interval' : scan_interval}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Verify_Background_Scanning_Message'
    common_name = '[%s] Verify the scanning messages from "meshd"' % tcname
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_msg': 'meshd'}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Verify_Neighbour_AP_List'
    common_name = '[%s] Verify neighbour AP list' % tcname
    test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '[%s] Disable Background scanning on WLAN' % tcname
    test_cfgs.append(({'wlan_cfg': disbg_wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Verify_Background_Scanning_Message'
    common_name = '[%s] Verify there is no scanning message from "apmgr"' % tcname
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_msg': 'apmgr',
                       'scan_interval' : scan_interval,
                       'negative': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Verify_Background_Scanning_Message'
    common_name = '[%s] Verify there are scanning messages from "meshd"' % tcname
    test_cfgs.append(({'ap_tag': ap_tag,
                       'expected_msg': 'meshd'}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Verify_Neighbour_AP_List'
    common_name = '[%s] Verify there is the neighbour AP list' % tcname
    test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False))
       
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, True))  
    
    return test_cfgs
 
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    tb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    support_radio_list = []
    active_ap = None
    mesh_ap = []
    radio = None
    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios']
        for rad in ap_support_radio_list:
            if rad not in support_radio_list:
                support_radio_list.append(rad) 

    for i in range(len(support_radio_list)):
        print "%s - %s" % (i, support_radio_list[i])
    while not radio:
        idx = raw_input('Please enter the index of the expected radio for your test: ')
        try:
            radio = support_radio_list[int(idx)]
        except:
            pass

    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios'] 
        if not radio in ap_support_radio_list:
            continue

        ret = testsuite.getApTargetType(ap_sym_name, ap_info, ts_cfg["interactive_mode"])
        desired_ap = raw_input("Is this AP under test (y/n)?: ").lower() == "y"

        if desired_ap and 'ROOT'.lower() in ret.lower():
            active_ap = ap_sym_name
        
        if desired_ap and 'MESH'.lower() in ret.lower():
            mesh_ap.append(ap_sym_name)
        
    if len(mesh_ap) == 0 :
        raise Exception("there is no mesh ap")
        return
        
    test_cfgs = define_test_cfg({'active_ap': active_ap,
                                 'mesh_ap': mesh_ap,
                                 'radio': radio})
    
    ts_name = {'ng': 'Background Scanning - 2.4G',
              'bg': 'Background Scanning - 2.4G',
              'na': 'Background Scanning - 5G',
              'a': 'Background Scanning - 5G',}[radio]    
    ts = testsuite.get_testsuite(ts_name, "Verify the background scanning service", combotest=True)
    
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
