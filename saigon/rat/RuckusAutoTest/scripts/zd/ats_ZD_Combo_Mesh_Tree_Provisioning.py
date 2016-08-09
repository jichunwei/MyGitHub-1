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

def defineTestConfiguration(mesh_tree_conf):
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Initialize test environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Policy_Mgmt_VLAN'
    common_name = 'Backup AP Mgmt VLAN current settings'
    test_cfgs.append(({'cfg_type': "init"}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Policy_Mgmt_VLAN'
    common_name = 'Config AP Mgmt VLAN to 1'
    test_cfgs.append(({'mgmt_vlan': {'mode': "enable", 'vlan_id': '1', },
                       'cfg_type': "config",
                       }, 
                      test_name, common_name, 0, False))
    
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
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify the Link AP'
    test_cfgs.append(({'ap_tag': 'AP3',
                       'active_ap': mesh_tree_conf['emesh_2_hops_ap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_AP_Mesh_Mode_Configuration'
    common_name = '[Force AP as Root mode] Verify AP %s at Root mode' % mesh_tree_conf['mesh_1_hop_ap']
    test_cfgs.append(({'ap_tag': 'AP2',
                       'test_option': 'force-mesh-mode-to-root'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_AP_Mesh_Mode_Configuration'
    common_name = '[Force AP as Mesh mode] Verify AP %s at Mesh mode' % mesh_tree_conf['mesh_1_hop_ap']
    test_cfgs.append(({'ap_tag': 'AP2',
                       'test_option': 'force-mesh-mode-to-mesh'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_AP_Mesh_Mode_Configuration'
    common_name = '[Force AP to disable mesh] Verify AP %s at mesh disabled mode' % mesh_tree_conf['mesh_1_hop_ap']
    test_cfgs.append(({'ap_tag': 'AP2',
                       'test_option': 'force-mesh-mode-to-disabled'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_AP_Mesh_Mode_Configuration'
    common_name = '[Force AP as Auto mode] Verify AP %s at Auto mode' % mesh_tree_conf['mesh_1_hop_ap']
    test_cfgs.append(({'ap_tag': 'AP2',
                       'test_option': 'force-mesh-mode-to-auto'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Root AP becomes Mesh with mesh ACL] Setting up an 1 hop Mesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'test_option': 'form_mesh_mesh_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Mesh ACL Mesh AP becomes Root] Reconnect the Mesh AP as Root'
    test_cfgs.append(({'ap_list': ['AP2'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Root AP becomes Mesh with smart ACL] Setting up an 1 hop Mesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'test_option': 'form_mesh_smart_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Smart ACL Mesh AP becomes Root] Reconnect the Mesh AP as Root'
    test_cfgs.append(({'ap_list': ['AP2'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Forming 2 hops eMesh network with smart ACL] Setting up a 2 hops eMesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'emesh_ap': 'AP3',
                       'test_option': 'form_emesh_smart_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Mesh and Link AP become Root] Setting up a 2 hops eMesh network'
    test_cfgs.append(({'ap_list': ['AP2', 'AP3'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Forming 2 hops eMesh network with mesh ACL] Setting up a 2 hops eMesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'emesh_ap': 'AP3',
                       'test_option': 'form_emesh_mesh_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_eMesh_2_Hops_Events'
    common_name = '[Verify the emesh forming events]'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Mesh_Topo_On_Dashboard'
    common_name = '[Verify the mesh tree on Dashboard]'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    #The following 2 cases should be obsoleted, ZF-6560
#    test_name = 'CB_ZD_Verify_SpeedFlex_Between_2_APs'
#    common_name = '[Verify the speedflex between Root AP and Mesh AP] with allow difference is 20%'
#    test_cfgs.append(({'ap1': 'AP1',
#                       'ap2': 'AP2',
#                       'allowed_diff': 0.2}, 
#                       test_name, common_name, 1, False))
#    
#    test_name = 'CB_ZD_Verify_SpeedFlex_Between_2_APs'
#    common_name = '[Verify the speedflex between Mesh AP and eMesh AP] with allow difference is 20%'
#    test_cfgs.append(({'ap1': 'AP2',
#                       'ap2': 'AP3',
#                       'allowed_diff': 0.2}, 
#                       test_name, common_name, 1, False))
    
#    test_name = 'CB_ZD_Mesh_Tree_Stability_RAP_Channel_Change'
#    common_name = '[Stability - RAP 2.4G channel change] Verify if the mesh AP 2.4G channel change follow Root AP'
#    test_cfgs.append(({'ap_tag': 'AP1','verify_aps': ['AP2'],
#                       'radio_cfg': {'radio': 'ng', 'channel': '4'}}, test_name, common_name, 1, False))
# ----------------> This test case only support for 2.4G single band APs
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_RAP_Channel_Change'
    common_name = '[Stability - RAP 5G channel change] Verify if the mesh AP 5G channel change follow Root AP'
    test_cfgs.append(({'ap_tag': 'AP1','verify_aps': ['AP2'],
                       'radio_cfg': {'radio': 'na', 'channel': '149'}}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_Mesh_Config_Change'
    common_name = '[Stability - Mesh SSID change] Verify if the mesh tree reforming successfully after mesh SSID changed'
    #@author: Jane.Guo @since: 2013-09 fix bug zf-5372
    test_cfgs.append(({'mesh_conf': {'mesh_name': 'Mesh-test-12345678'}}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_Mesh_Config_Change'
    common_name = '[Stability - Mesh Passphrase change] Verify if the mesh tree reforming successfully after mesh passphrase changed'
    test_cfgs.append(({'mesh_conf': {'mesh_passphrase': 'Y_azJya8vBqf8hU9rdXG_bpQ5uiOAxr-_W0xRYTEDpqOWeBsrlvyPch2BYR1rPY'}}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_Rebooting'
    common_name = '[Stability - RAP reboot] Verify if the mesh tree reforming successfully after root AP rebooted'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'test_option': 'reboot_ap'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_Rebooting'
    common_name = '[Stability - MAP reboot] Verify if the mesh tree reforming successfully after mesh AP rebooted'
    test_cfgs.append(({'ap_tag': 'AP2',
                       'test_option': 'reboot_ap'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_Rebooting'
    common_name = '[Stability - ZD reboot] Verify if the mesh tree reforming successfully after ZD rebooted'
    test_cfgs.append(({'test_option': 'reboot_zd'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect all active APs as Root'
    test_cfgs.append(({'ap_list': ['AP1', 'AP2', 'AP3'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Policy_Mgmt_VLAN'
    common_name = 'Restore AP Mgmt VLAN settings'
    test_cfgs.append(({'cfg_type': "teardown"}, test_name, common_name, 0, True))

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

    print 'Please configure your own eMesh topology (please select the current root aps only):'
    emesh_2_hops_topo = {'root_ap': '',
                         'mesh_1_hop_ap': '',
                         'emesh_2_hops_ap': '',}
    mesh_tree_conf = _get_mesh_tree_from_user_input(ap_sym_dict, emesh_2_hops_topo)
    ts_name = 'Dual bands Mesh Tree - Provisioning and Stability'
    ts = testsuite.get_testsuite(ts_name, 'Verify the mesh network functionality', combotest=True)
    test_cfgs = defineTestConfiguration(mesh_tree_conf)

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
