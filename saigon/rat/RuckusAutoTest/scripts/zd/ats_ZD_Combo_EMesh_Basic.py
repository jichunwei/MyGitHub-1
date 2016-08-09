# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to eMesh - BASIC:
4.1.1    eMAP - Dashboard
4.1.2    eMAP - Monitor-Mesh
4.1.3    eMAP - event
4.1.5    eMAP - Speedflex
4.1.11    Upgrade/Downgrade

Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

input_seq = ['root_ap', 'mesh_1_hop_ap', 'mesh_2_hops_ap', 'emesh_2_hops_aps', 'emesh_3_hops_aps']

def defineTestConfiguration(mesh_tree_conf):
    test_cfgs = []

    test_name = 'CB_ZD_Init_Mesh_Test_Environment'
    common_name = 'Initiate test environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Setup_2Hops_EMesh_Topo'
    common_name = 'Setting up a 2 hops eMesh network'
    test_cfgs.append(({'mesh_tree': mesh_tree_conf}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_eMesh_2_Hops_Events'
    common_name = 'Verify the emesh forming events'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Mesh_Topo_On_Dashboard'
    common_name = 'Verify the mesh tree on Dashboard'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SpeedFlex_Between_2_APs'
    common_name = 'Verify the speedflex between Mesh AP and eMesh AP with allow difference is 20%'
    test_cfgs.append(({'ap1': mesh_tree_conf['mesh_1_hop_ap'],
                       'ap2': mesh_tree_conf['emesh_2_hops_aps'][0],
                       'allowed_diff': 0.2}, 
                       test_name, common_name, 1, False))
    
    # Please configure the params to match your upgrade requirements
    test_name = 'CB_ZD_Upgrade'
    common_name = 'Upgarde ZD'
    test_cfgs.append(({'image_file_path': '',
                       'build_stream': '',
                       'build_number': '',
                       'force_upgrade': False}, 
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Mesh_Topo'
    common_name = 'Verify the mesh tree after upgraded'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Upgrade'
    common_name = 'Downgrade ZD to testing build'
    test_cfgs.append(({'image_file_path': '',
                       'build_stream': '',
                       'build_number': '',
                       'force_upgrade': False}, 
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Mesh_Topo'
    common_name = 'Verify the mesh tree after downgraded'
    test_cfgs.append(({}, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_Init_Mesh_Test_Environment'
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'task':'cleanup'}, test_name, common_name, 0, True))

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
            input = raw_input(msg).upper().strip().split()
            if not input:
                continue      
            if 'ALL' in input:
                expected_topo[param] = ap_info_list.keys()
                ap_info_list = {}
                continue               
            for ap in input:
                if ap in ap_info_list.keys():
                    expected_topo[param].append(ap)
                    del ap_info_list[ap]
        else:
            msg = 'Please select one %s: ' % param.upper().replace('_', ' ')
            input = raw_input(msg).strip()
            expected_topo[param] = input
            del ap_info_list[input]

    return expected_topo
 
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']

    print 'Please configure your own eMesh topology'
    emesh_2_hops_topo = {'root_ap': '',
                         'mesh_1_hop_ap': '',
                         'emesh_2_hops_aps': [],}
    mesh_tree_conf = _get_mesh_tree_from_user_input(ap_sym_dict, emesh_2_hops_topo)
    ts_name = 'eMesh testing: BASIC'
    ts = testsuite.get_testsuite(ts_name, 'Verify the eMesh network functionality', combotest=True)
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
