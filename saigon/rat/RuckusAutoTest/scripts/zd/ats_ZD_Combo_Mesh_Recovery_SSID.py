# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Dec 2011

This testsuite is configure to allow testing follow test cases - which are belong to eMesh - BASIC:


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

input_seq = ['root_ap', 'mesh_1_hop_ap', 'emesh_2_hops_ap']

def defineTestConfiguration(mesh_tree_conf, target_station):
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Initialize test environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD'
    test_cfgs.append(({'mesh_ap_mac_list':[],
                       'for_upgrade_test':False},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify the Root AP'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'active_ap': mesh_tree_conf['root_ap']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify the Mesh AP'
    test_cfgs.append(({'ap_tag': 'AP2',
                       'active_ap': mesh_tree_conf['mesh_1_hop_ap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr': target_station,
                       'sta_tag': 'STA1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Root AP becomes Mesh with mesh ACL] Setting up an 1 hop Mesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'test_option': 'form_mesh_mesh_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Recovery_SSID_Testing'
    common_name = '[Mesh - Recovery SSID] verify recovery ssid wlan on mesh AP'
    test_cfgs.append(({'ap_tag': 'AP2',
                       'sta_tag': 'STA1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Mesh ACL Mesh AP becomes Root] Reconnect the Mesh AP as Root'
    test_cfgs.append(({'ap_list': ['AP2'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, True))  
    
    return test_cfgs
 
def _get_mesh_tree_from_user_input(ap_sym_dict, expected_topo):
    ap_info_list = ap_sym_dict.copy()
       
    for param in input_seq:
        if not param in expected_topo.keys():
            continue
        
        for ap in ap_info_list.keys():
            print ap, ap_info_list[ap]
            
        if type(expected_topo[param]) is list:
            msg = 'Please select %s, separated by space/[ALL] to select all/[ENTER] to pass: '
            msg = msg % param.upper().replace('_', ' ')
            rinput = raw_input(msg).lower().strip().split()
            if not rinput:
                continue      
            if 'all' in rinput:
                expected_topo[param] = ap_info_list.keys()
                ap_info_list = {}
                continue               
            for ap in rinput:
                if ap in ap_info_list.keys():
                    expected_topo[param].append(ap)
                    del ap_info_list[ap]
        else:
            msg = 'Please select one %s: ' % param.upper().replace('_', ' ')
            rinput = raw_input(msg).strip()
            expected_topo[param] = rinput
            del ap_info_list[rinput]

    return expected_topo
 
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta = testsuite.getTargetStation(sta_ip_list)
    
    print 'Please configure your own Mesh topology (please select the current root aps only):'
    mesh_topo = {'root_ap': '',
                 'mesh_1_hop_ap': ''}
    
    mesh_tree_conf = _get_mesh_tree_from_user_input(ap_sym_dict, mesh_topo)
    ts_name = 'Mesh Recover-SSID test'
    ts = testsuite.get_testsuite(ts_name, 'Verify the mesh recovery-ssid functionality', combotest=True)
    test_cfgs = defineTestConfiguration(mesh_tree_conf, target_sta)

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
