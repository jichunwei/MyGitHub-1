# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Feb 2012

This test suite is configure to allow testing follow test cases - which are belong to Mesh - BASIC for IPv6:


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
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Forming Mesh with mesh ACL] Setting up an 1 hop Mesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'test_option': 'form_mesh_mesh_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect the Mesh AP as Root'
    test_cfgs.append(({'ap_list': ['AP2'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Forming Mesh with smart ACL] Setting up an 1 hop Mesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'test_option': 'form_mesh_smart_acl'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect the Mesh AP ACL as Root'
    test_cfgs.append(({'ap_list': ['AP2'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 0, False))
    
    ap1_ip_param = {'ip_version': 'IPv6',
                    'IPv6': {'IPv6_mode': 'manual',
                             'IPv6_addr': '2020:db8:1::45',
                             'ipv6_prefix_len': '64',
                             'ipv6_gateway': '2020:db8:1::251'},
                    }
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = 'Reconnect AP1 with IP %s' % ap1_ip_param['IPv6']['IPv6_addr']
    test_cfgs.append(({'ap_tag': 'AP1',
                       'ip_cfg': ap1_ip_param}, test_name, common_name, 0, False))

    ap2_ip_param = {'ip_version': 'IPv6',
                    'IPv6': {'IPv6_mode': 'manual',
                             'IPv6_addr': '2020:db8:33::46',
                             'ipv6_prefix_len': '64',
                             'ipv6_gateway': '2020:db8:1::251'},
                    }
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = 'Reconnect AP2 with IP %s' % ap2_ip_param['IPv6']['IPv6_addr']
    test_cfgs.append(({'ap_tag': 'AP2',
                       'ip_cfg': ap2_ip_param}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Firming mesh from 2 different subnet APs] Set up mesh with AP1 and AP2'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'test_option': 'form_mesh_smart_acl',
                       'is_test_pass': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect the AP2 as Root'
    test_cfgs.append(({'ap_list': ['AP2'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = 'Reconnect AP1 and AP2 in same ZD subnet'
    test_cfgs.append(({'ap_tag': ['AP1', 'AP2'],
                       'ip_cfg': {'ip_version': 'IPv6',
                                  'IPv6': {'IPv6_mode': 'auto'}
                                  }
                       }, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '[Forming 2 hops eMesh network with mesh ACL] Setting up a 2 hops eMesh network'
    test_cfgs.append(({'root_ap': 'AP1',
                       'mesh_ap': 'AP2',
                       'emesh_ap': 'AP3',
                       'test_option': 'form_emesh_mesh_acl'}, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_Verify_ZD_GW_Detection'
    common_name = '[Gateway and ZD detection] Verify on the Root AP'
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_ZD_GW_Detection'
    common_name = '[Gateway and ZD detection] Verify on the Mesh AP'
    test_cfgs.append(({'ap_tag': 'AP2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_ZD_GW_Detection'
    common_name = '[Gateway and ZD detection] Verify on the eMesh AP'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-IPv6Only Mesh-IPv6Only eMesh-Dual'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-IPv6Only Mesh-Dual eMesh-Dual'
    test_cfgs.append(({'ap_tag': 'AP2'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-IPv6Only Mesh-Dual eMesh-IPv6Only'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-Dual Mesh-Dual eMesh-IPv6Only'
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-Dual Mesh-Dual eMesh-Dual'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-Dual Mesh-IPv6Only eMesh-Dual'
    test_cfgs.append(({'ap_tag': 'AP2'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing'
    common_name = '[Verify AP IP modes changing] RAP-Dual Mesh-IPv6Only eMesh-IPv6Only'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_DFS_Channel_Testing'
    common_name = '[Verify DFS channel blocking] Verify on the Root AP'
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_DFS_Channel_Testing'
    common_name = '[Verify DFS channel blocking] Verify on the Mesh AP'
    test_cfgs.append(({'ap_tag': 'AP2',
                       'is_block_channel': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_DFS_Channel_Testing'
    common_name = '[Verify DFS channel blocking] Verify on the eMesh AP'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect all active APs as Root'
    test_cfgs.append(({'ap_list': ['AP1', 'AP2', 'AP3'],
                       'test_option': 'reconnect_as_root'}, test_name, common_name, 0, False))
    
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
    ts_name = 'IPV6 Mesh - Basic'
    ts = testsuite.get_testsuite(ts_name, 'Verify the mesh network functionality in ipv6', combotest=True)
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