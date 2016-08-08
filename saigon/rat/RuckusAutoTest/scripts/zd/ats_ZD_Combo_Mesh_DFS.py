"""
@Author: Kevin Tan - kevin.tan@ruckuswireless.com
@Since: Feb 2012

This test suite is configure to allow testing follow test cases - which are belong to Mesh - BASIC for IPv6:


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

input_seq = ['root_ap', 'mesh_1_hop_ap', 'emesh_2_hops_ap']

def defineTestConfiguration(mesh_tree_conf, cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD in the beginning'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'Set country code to UK'
    test_cfgs.append(({'country_code':'United Kingdom'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify AP1'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'active_ap': mesh_tree_conf['root_ap']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify AP2'
    test_cfgs.append(({'ap_tag': 'AP2',
                       'active_ap': mesh_tree_conf['mesh_1_hop_ap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify AP3'
    test_cfgs.append(({'ap_tag': 'AP3',
                       'active_ap': mesh_tree_conf['emesh_2_hops_ap']}, test_name, common_name, 0, False))

    #Fixed channel configuration    
    test_name = 'CB_ZD_DFS_Fixed_Channel_Testing'
    common_name = '[Verify DFS fixed channel blocking] Verify on AP1'
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_DFS_Fixed_Channel_Testing'
    common_name = '[Verify DFS fixed channel blocking] Verify on AP2'
    test_cfgs.append(({'ap_tag': 'AP2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_DFS_Fixed_Channel_Testing'
    common_name = '[Verify DFS fixed channel blocking] Verify on AP3'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 2, False))

    #Auto channel configuration
    test_name = 'CB_ZD_DFS_Auto_Channel_Testing'
    common_name = '[Verify DFS auto channel blocking] Verify on AP1'
    test_cfgs.append(({'ap_tag': 'AP1'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_DFS_Auto_Channel_Testing'
    common_name = '[Verify DFS auto channel blocking] Verify on AP2'
    test_cfgs.append(({'ap_tag': 'AP2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_DFS_Auto_Channel_Testing'
    common_name = '[Verify DFS auto channel blocking] Verify on AP3'
    test_cfgs.append(({'ap_tag': 'AP3'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'Set country code back to US'
    test_cfgs.append(({'country_code':'United States'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))

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
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list     = tbcfg['sta_ip_list']
    ap_sym_dict     = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    print 'Please configure your own eMesh topology:'
    emesh_2_hops_topo = {'root_ap': '',
                         'mesh_1_hop_ap': '',
                         'emesh_2_hops_ap': '',}
    mesh_tree_conf = _get_mesh_tree_from_user_input(ap_sym_dict, emesh_2_hops_topo)

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        if target_sta_radio != 'na':
            print "DFS only supports 802.11na(5GHz), select 11na automatically"
            target_sta_radio = 'na'
    else:        
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    tcfg = {
            'target_station':'%s' % target_sta,
            'all_ap_mac_list': all_ap_mac_list,
            'radio_mode': target_sta_radio,
            }
        
    ts_name = 'Mesh - DFS'
    ts = testsuite.get_testsuite(ts_name, 'Verify the mesh DFS functionality', combotest=True)
    test_cfgs = defineTestConfiguration(mesh_tree_conf, tcfg)

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