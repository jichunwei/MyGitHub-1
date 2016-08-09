# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to ZD CLI - Configure Mesh:

16.1    Sets Mesh SSID.                                       ssid <ssid>
16.2    Sets Mesh pass phrase.                                passphrase <passphrase>
16.3    Set the option value of loop avoidance for Mesh.      loop-avoid {OPTION}    Not availbale on 9.2
16.4    Set the value of gateway timeout for Mesh.            gw-timeout {SECOND}    Not availbale on 9.2
16.5    Set the hex value of RX omni antenna for Mesh.        rx-omni {MODEL} {HEX}  Not availbale on 9.2
16.6    Enter Mesh hop count threshold.                       hops-warn-threshold <threshold>
16.7    Disables Mesh hop count detection.                    no detect-hops
16.8    Enter Mesh downlinks threshold.                       fan-out-threshold <threshold>
16.9    Disables Mesh downlinks detection.                    no detect-fanout

Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys
import time
import copy
import string
import random

import logging
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

VALID_CHARS = string.ascii_letters + string.digits
VALID_NUM_CHARS_RANGE_FOR_ESSID = (2, 32)
VALID_NUM_CHARS_RANGE_FOR_PASSPHRASE = (8, 63)
VALID_VALUE_RANGE_FOR_THRESHOLD = (1, 255)

wlan_cfg = {'ssid': "open-wlan-%s" % (time.strftime("%H%M%S")),
            'auth': "open",
            'encryption': "none",
           }

wg_cfg = dict(name='wg-mesh-ap-assign', description='wg-mesh-ap-assign')

def defineTestConfiguration(cfg):
    test_cfgs = []
    dest_ip = '172.16.10.252'
    e = VALID_NUM_CHARS_RANGE_FOR_ESSID
    p = VALID_NUM_CHARS_RANGE_FOR_PASSPHRASE
    t = VALID_VALUE_RANGE_FOR_THRESHOLD
    
    test_name = 'CB_ZD_CLI_Configure_Mesh'
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True}, test_name, common_name, 0, False))
    
    common_name = '[SSID]Sets Mesh SSID - ssid <ssid>'
    mesh_name = ''.join(random.sample(VALID_CHARS, random.randint(e[0], e[1])))
    test_cfgs.append(({'mesh_conf': {'mesh_name': mesh_name}}, 
                      test_name, common_name, 1, False))
    
    common_name = '[Passphrase]Sets Mesh Passphrase - passphrase <passphrase>'
    passphrase = ''.join(random.sample(VALID_CHARS, random.randint(p[0], p[1])))
    test_cfgs.append(({'mesh_conf': {'mesh_passphrase': passphrase}}, 
                      test_name, common_name, 1, False))
    
    common_name = '[Hop Count Threshold]Enter Mesh hop count threshold - hops-warn-threshold <threshold>'
    test_cfgs.append(({'mesh_conf': {'mesh_hop_detection': 'Enabled',
                                     'mesh_hops_threshold': '%s' % random.randint(t[0], t[1])}}, 
                      test_name, common_name, 1, False))
    
    common_name = '[Hop Count Detection]Disables Mesh hop count detection - no detect-hops'
    test_cfgs.append(({'mesh_conf': {'mesh_hop_detection': 'Disabled'}}, 
                      test_name, common_name, 1, False))
    
    common_name = '[Downlinks Threshold]Enter Mesh downlinks threshold - fan-out-threshold <threshold>'
    test_cfgs.append(({'mesh_conf': {'mesh_downlinks_detection': 'Enabled',
                                     'mesh_downlinks_threshold': '%s' % random.randint(t[0], t[1])}}, 
                      test_name, common_name, 1, False))
    
    #Modified by Liang Aihua on 2014-11-4 for these steps not exist in database.
    #ptest_name = 'CB_ZD_Create_Station'
    #common_name = 'Get the station'
    #test_params = {'sta_tag': 'sta1', 'sta_ip_addr': cfg['sta_ip_list'][0]}
    #test_cfgs.append((test_params, ptest_name, common_name, 0, False))
    
    #ptest_name = 'CB_ZD_Create_Active_AP'
    #common_name = 'Get the active ap'
    #test_params = {'ap_tag': 'active_ap', 'active_ap': cfg['active_aps_mac_list'][0]}
    #test_cfgs.append((test_params, ptest_name, common_name, 0, False))
    
    #radio_mode = cfg['radio_mode']
    #if radio_mode == 'bg':
    #    radio_mode = 'g'

    #ptest_name = 'CB_ZD_Create_Wlans_Wg_Assign_Wlan_AP'
    #common_name = 'Create wlan, wlan group and assign active ap to the wlan group'
    #test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
    #                   'enable_wlan_on_default_wlan_group': False,
    #                   'wgs_cfg': wg_cfg,
    #                   'ap_tag': 'active_ap',
    #                   'radio_mode': radio_mode}, ptest_name, common_name, 1, False))
    
    #ptest_name = 'CB_ZD_Associate_Station_1'
    #common_name = 'The station associated the wlan from the mesh ap'
    #test_params = {'sta_tag': 'sta1', 'wlan_cfg': wlan_cfg}
    #test_cfgs.append((test_params, ptest_name, common_name, 1, False))
    
    #ptest_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    #common_name = 'Get target station Wifi addresses'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, ptest_name, common_name, 1, False))
    
    #ptest_name = 'CB_Station_Ping_Dest_Is_Allowed'
    #common_name = 'Client ping dest-ip[%s] which is allowed' % dest_ip
    #test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    #test_cfgs.append((test_params, ptest_name, common_name, 2, False))
    
    #ptest_name = 'CB_Station_Remove_All_Wlans'
    #common_name = 'Remove the newly wlan from the station'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, ptest_name, common_name, 1, False))
    
    #ptest_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    #common_name = 'Assign the active ap to default wlangroup'
    #test_cfgs.append(({'active_ap': cfg['active_ap_list'][0],
    #                   'wlan_group_name': 'Default',
    #                   'radio_mode': radio_mode}, ptest_name, common_name, 1, False))
    
    common_name = '[Downlinks Detection]Disables Mesh downlinks detection - no detect-fanout'
    test_cfgs.append(({'mesh_conf': {'mesh_downlinks_detection': 'Disabled'}}, 
                      test_name, common_name, 1, False))
    
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True}, test_name, common_name, 0, True))
    
    return test_cfgs
     
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = []
    active_aps_mac_list = []
    
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
 
    ts_name = 'ZD CLI - Configure Mesh'
    ts = testsuite.get_testsuite(ts_name, 'Verify configure Mesh commands under ZD CLI', combotest=True)
    
    tcfg = {'active_ap_list': active_ap_list,
            'active_aps_mac_list': active_aps_mac_list,
            'sta_ip_list': sta_ip_list,
            'radio_mode': target_sta_radio,
            }
    test_cfgs = defineTestConfiguration(tcfg)

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
