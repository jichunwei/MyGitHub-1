"""
This test suite is configure to allow testing follow test cases - which are belong to Mesh - RFMD DFS channel hop:
    - Verify following commands are configurable:
        set rfmd enable, set rfmd disable, get rfmd
        get radarthreshold, set radarthreshold XX
        Verify that no AP reboots when changing AP RFMD status
        To make sure that AP default threshold value is 2.
    - Mesh AP apply Fixed channel:
        Root AP enables RFMD, Mesh APs detect radar event
        Root AP disables RFMD, Mesh APs detect radar event
        Root AP enables RFMD but in non-DFS channel, Mesh APs detect radar event
        Root AP disables RFMD and in non-DFS channel, Mesh APs detect radar event
        Root AP enables RFMD and detects its own radar events
    - Mesh AP apply AUto channel:
        Root AP enables RFMD, Mesh APs detect radar event
        Root AP disables RFMD, Mesh APs detect radar event
        Root AP enables RFMD but in non-DFS channel, Mesh APs detect radar event
        Root AP disables RFMD and in non-DFS channel, Mesh APs detect radar event
        Root AP enables RFMD and detects its own radar events
    - Multiple Mesh hops: 
        All APs in multi-hop mesh topology enable RFMD
        Only RAP and the last leaf MAP enable RFMD

    expect result: All steps should result properly.
    
    How to:
        1)    Get 11-an DFS channel allowed per country from the file '/etc/airespider-default/country-list.xml'in ZD shell mode, and get specified value for United Kingdom
        2)    Enter per-AP's shell, ensure all APs enable RFMD.
        3)    In ZD GUI, ensure all APs are using fixed DFS channel.
        4)    In Mesh AP2, input shell command 'radartool -i wifi1 rfmdsetradar 1'.
        5)    In Root AP1, input shell command 'rfmd -d'to check the radar event table includes AP2 info and no channel hop occurs (less than radar event threshold). 
              Make sure that mesh connection loss should not happen.
        6)    Verify that life-time of a radar event is 10-sec in Root AP1. After 10-sec, the event will be purged from radar event table.
        7)    Both In Mesh AP2 and Mesh AP3, input shell command 'radartool -i wifi1 rfmdsetradar 1'.
        8)    Radar threshold is 2 in Root AP, input shell command 'rfmd -d' to check radar event table. 
        9)    In Mesh AP1 and AP2, input shell command 'rfmd -d' to verify that table is empty.
        10)   Since that the number of received events is equal to the threshold, RAP would have a channel hop. 
        11)   Check that mesh connection should be fine during this process.
        12)   Get new channel value from ZD GUI after a short while, and check the event 'AP[xx:xx:xx:xx] detects radar burst on radio [11a/n] and channel [xxx] goes 
              into non-occupancy period'.
        13)   In Root AP1, input shell command 'radartool -i wifi1 shownol'to verify that original DFS channel is in blocked list. Blocked time it 30 minutes.
        14)   Check that within 30 minutes, we can't assign blocked DFS channel to Root AP in ZD GUI. After 30 minutes, input shell command 'radartool -i wifi1 shownol' 
              again to verify that original DFS channel value is purged in blocked list and we can assign blocked DFS channel to Root AP in ZD GUI again.
        15)   Change Route AP RMFD option and Mesh AP channel(fixed/auto), then repeat step 4) to 14).
    
Created on August 2012
@author: kevin.tan@ruckuswireless.com
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

input_seq = ['root_ap', 'mesh_1_hop_ap1', 'mesh_1_hop_ap2']

def defineTestConfiguration(mesh_tree_conf, cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    
    sta_tag = 'sta%s' % radio_mode
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
    test_cfgs.append(({'country_code':'United Kingdom', 'unfix_ap': False, 'allow_indoor_channel':True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP1'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'active_ap': mesh_tree_conf['root_ap']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP2'
    test_cfgs.append(({'ap_tag': 'AP2',
                       'active_ap': mesh_tree_conf['mesh_1_hop_ap1']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP3'
    test_cfgs.append(({'ap_tag': 'AP3',
                       'active_ap': mesh_tree_conf['mesh_1_hop_ap2']}, test_name, common_name, 0, False))

    #Fixed channel configuration    
    test_name = 'CB_ZD_RFMD_Configuration'
    common_name = '[configuration] Test RFMD configuration'
    test_cfgs.append(({'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3'}, test_name, common_name, 1, False))

    #Fixed channel test    
    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[fixed channel, Root AP enables RFMD with DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'fixed', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': True, 'root_dfs':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[fixed channel, Root AP disables RFMD with DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'fixed', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': False, 'root_dfs':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[fixed channel, Root AP enables RFMD with non-DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'fixed', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': True, 'root_dfs':False}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[fixed channel, Root AP disables RFMD with non-DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'fixed', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': False, 'root_dfs':False}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[fixed channel, Root AP enables RFMD and detects its own radar events] RFMD test'
    test_cfgs.append(({'channel_type': 'fixed', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_own_detect': True}, test_name, common_name, 1, False))

    #Auto channel test
    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[auto channel, Root AP enables RFMD with DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'auto', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': True, 'root_dfs':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[auto channel, Root AP disables RFMD with DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'auto', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': False, 'root_dfs':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[auto channel, Root AP enables RFMD with non-DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'auto', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': True, 'root_dfs':False}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[auto channel, Root AP disables RFMD with non-DFS channel] RFMD test'
    test_cfgs.append(({'channel_type': 'auto', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_rfmd': False, 'root_dfs':False}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_RFMD_DFS_Channel_Test'
    common_name = '[auto channel, Root AP enables RFMD and detects its own radar events] RFMD test'
    test_cfgs.append(({'channel_type': 'auto', 'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'root_own_detect': True}, test_name, common_name, 1, False))

    #Multiple hops Mesh APs Testing
    test_name = 'CB_ZD_RFMD_Multihop_Test'
    common_name = '[multiple hops, all APs in multiple hops mesh topology enable RFMD] RFMD test'
    test_cfgs.append(({'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'all_ap_rfmd': True}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_RFMD_Multihop_Test'
    common_name = '[multiple hops, only RAP and the last leaf MAP enable RFMD] RFMD test'
    test_cfgs.append(({'root_ap': 'AP1', 'mesh_ap_1': 'AP2', 'mesh_ap_2': 'AP3', 'all_ap_rfmd': False}, test_name, common_name, 1, False))

    #Recover to original status
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'Set country code back to US'
    test_cfgs.append(({'country_code':'United States', 'unfix_ap': False}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({},test_name, common_name, 0, True))
    
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

    print 'Please configure your own Mesh topology:'
    mesh_topo = {'root_ap': '',
                 'mesh_1_hop_ap1': '',
                 'mesh_1_hop_ap2': '',}
    mesh_tree_conf = _get_mesh_tree_from_user_input(ap_sym_dict, mesh_topo)

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
        
    ts_name = 'Mesh - RFMD'
    ts = testsuite.get_testsuite(ts_name, 'Verify the mesh RFMD functionality', combotest=True)
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