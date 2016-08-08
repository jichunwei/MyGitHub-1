'''
Created on 2011-6-15

@author: serena.tan@ruckuswireless.com

RuckusAutoTest\\tests\\zd\\lib\\Chariot_Throughput_Test_Template.tst information:
    1    TCP    voice    Throughput.scr
    2    TCP    video    Throughput.scr
    3    TCP    data     Throughput.scr
    4    UDP    voice    Throughput.scr
    5    UDP    video    Throughput.scr
    6    UDP    data     Throughput.scr
    
    variable value in Throughput.scr:
        file_size: 1000000
        send_data_rate: UNLIMITED

'''


import time
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


FORMAT_NUM = {'Voice': 1,
              'Video': 2,
              'Data': 3
              }

CHARIOT_THROUGHPUT_TEST = "RuckusAutoTest\\tests\\zd\\lib\\Chariot_Throughput_Test_Template.tst"

CHARIOT_TMP_FILES = dict(clone_file = 'chariot_clone.txt',
                         new_test_file = 'chariot_test.tst',
                         result_file_tst = 'chariot_result.tst',
                         result_file_txt = 'chariot_result.txt')


def define_wlan_cfgs():
    wlan_cfgs = []
    wlan_cfgs.append(dict(ssid = "priority-high-rap-%s" % time.strftime("%H%M%S"),
                          auth = 'open', encryption = 'none', priority = 'high'))
    
    wlan_cfgs.append(dict(ssid = "priority-low-rap-%s" % time.strftime("%H%M%S"),
                          auth = 'open', encryption = 'none', priority = 'low'))
    
    wlan_cfgs.append(dict(ssid = "priority-high-map-%s" % time.strftime("%H%M%S"),
                          auth = 'open', encryption = 'none', priority = 'high'))
    
    wlan_cfgs.append(dict(ssid = "priority-low-map-%s" % time.strftime("%H%M%S"),
                          auth = 'open', encryption = 'none', priority = 'low'))
    
    return wlan_cfgs


def define_wlangroup_cfg(wlan_cfgs):
    wlan_member_rap = {}
    wlan_member_map = {}
    for wlan in wlan_cfgs:
        ssid = wlan['ssid']
        if 'rap' in ssid:
            wlan_member_rap[ssid] = {}
        
        elif 'map' in ssid:
            wlan_member_map[ssid] = {}
        
    wg_cfg_rap = dict(name = 'wlan_priority_rap', description = '',
                      vlan_override = False, wlan_member = wlan_member_rap)
    
    wg_cfg_map = dict(name = 'wlan_priority_map', description = '',
                      vlan_override = False, wlan_member = wlan_member_map)
    
    return dict(wg_cfg_rap = wg_cfg_rap,
                wg_cfg_map = wg_cfg_map)


def define_media_pairs():
    '''
    (wlan priority high, wlan priority low)
    '''
    media_pairs_list = []
    
    media_pairs_list.append(('Voice', 'Voice'))
    media_pairs_list.append(('Video', 'Video'))
    media_pairs_list.append(('Data', 'Data'))
    media_pairs_list.append(('Video', 'Voice'))
    media_pairs_list.append(('Data', 'Voice'))
    media_pairs_list.append(('Data', 'Video'))
    
    return media_pairs_list


def define_chariot_test_cfgs(tcfg, media_pair, com_name, ap_tag):
    _test_cfgs = []
    
    endpoint_pair_list = []
    endpoint_pair_list.append(dict(num_in_temp = FORMAT_NUM[media_pair[0]],
                                   endpoint1_ip = tcfg['test_pc_ip'], 
                                   sta_tag = 'sta_h'))
    
    endpoint_pair_list.append(dict(num_in_temp = FORMAT_NUM[media_pair[1]],
                                   endpoint1_ip = tcfg['test_pc_ip'], 
                                   sta_tag = 'sta_l'))
    
    endpoint_pair_info = {'1': {'wlan_priority': 'high',
                                'media': media_pair[0].lower()},
                          '2': {'wlan_priority': 'low',
                                'media': media_pair[1].lower()}
                          }
    
    chariot_tmp_files = tcfg['chariot_tmp_files']
    
    test_name = 'CB_Remove_Tmp_Files'
    common_name = '[%s] Remove chariot temporary files' % com_name
    _test_cfgs.append(({'filename_list': chariot_tmp_files.values()},
                       test_name, common_name, 1, False))
    
    test_name = 'CB_Chariot_Create_Clone_File'
    common_name = '[%s] Create chariot clone file' % com_name
    _test_cfgs.append(({'endpoint_pair_list': endpoint_pair_list, 
                        'output_filename': chariot_tmp_files['clone_file']}, 
                       test_name, common_name, 2, False))
    
    test_name = 'CB_Chariot_Clone_Test_File'
    common_name = '[%s] Clone chariot test file' % com_name
    _test_cfgs.append(({'template_filename': CHARIOT_THROUGHPUT_TEST,
                        'clone_filename': chariot_tmp_files['clone_file'],
                        'output_filename': chariot_tmp_files['new_test_file']}, 
                        test_name, common_name, 2, False))
    
    test_name = 'CB_Chariot_Run_Test'
    common_name = '[%s] Run chariot test file' % com_name
    _test_cfgs.append(({'tst_filename': chariot_tmp_files['new_test_file'],
                        'res_filename': chariot_tmp_files['result_file_tst']}, 
                        test_name, common_name, 2, False))
    
    test_name = 'CB_Chariot_Format_Test_Result'
    common_name = '[%s] Format chariot test result' % com_name
    _test_cfgs.append(({'res_filename': chariot_tmp_files['result_file_tst'],
                        'output_filename': chariot_tmp_files['result_file_txt']}, 
                        test_name, common_name, 2, False))
    
    test_name = 'CB_Chariot_Get_Throughput_Info'
    common_name = '[%s] Get chariot throughput test info' % com_name
    _test_cfgs.append(({'filename': chariot_tmp_files['result_file_txt']}, 
                        test_name, common_name, 2, False))

    test_name = 'CB_Chariot_Verify_Endpoint_Pair_Priority'
    common_name = '[%s] Verify chariot endpoint pair priority' % com_name
    _test_cfgs.append(({'endpoint_pair_info': endpoint_pair_info, 
                        'ap_tag': ap_tag},
                       test_name, common_name, 2, False))
    
    return _test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Get the station for high priority wlan'    
    test_cfgs.append(({'sta_tag': 'sta_h', 'sta_ip_addr': tcfg['target_sta_h']}, test_name, common_name, 0, False))
  
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Get the station for low priority wlan'
    test_cfgs.append(({'sta_tag': 'sta_l', 'sta_ip_addr': tcfg['target_sta_l']}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the active RAP' 
    test_cfgs.append(({'ap_tag': 'rap', 'active_ap': tcfg['rap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the active MAP' 
    test_cfgs.append(({'ap_tag': 'map', 'active_ap': tcfg['map']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create wlans with different priority'
    test_cfgs.append(({'wlan_cfg_list': tcfg['wlan_cfgs']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
    common_name = 'Remove all wlans out of default wlan group'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = 'Create a wlan group for RAP'
    test_cfgs.append(({'wgs_cfg': tcfg['wgs_cfg']['wg_cfg_rap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = 'Create a wlan group for MAP'
    test_cfgs.append(({'wgs_cfg': tcfg['wgs_cfg']['wg_cfg_map']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the wlan group to radio '%s' of RAP" % tcfg['rap_radio_mode'][0]
    test_cfgs.append(({'active_ap': tcfg['rap'], 
                       'wlan_group_name': tcfg['wgs_cfg']['wg_cfg_rap']['name'], 
                       'radio_mode': tcfg['rap_radio_mode'][0]},
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the wlan group to radio '%s' of MAP" % tcfg['map_radio_mode'][0]
    test_cfgs.append(({'active_ap': tcfg['map'], 
                       'wlan_group_name': tcfg['wgs_cfg']['wg_cfg_map']['name'], 
                       'radio_mode': tcfg['map_radio_mode'][0]},
                       test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = 'Associate the station with high priority wlan RAP'
    test_cfgs.append(({'sta_tag': 'sta_h', 'wlan_cfg': tcfg['wlan_cfgs'][0]}, test_name, common_name, 0, False))    

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = 'Get wifi address of the high priority station RAP'
    test_cfgs.append(({'sta_tag': 'sta_h'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = 'Associate the station with low priority wlan RAP'
    test_cfgs.append(({'sta_tag': 'sta_l', 'wlan_cfg': tcfg['wlan_cfgs'][1]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = 'Get wifi address of the low priority station RAP'
    test_cfgs.append(({'sta_tag': 'sta_l'}, test_name, common_name, 0, False))
    
    for media_pair in tcfg['media_pairs']:
        com_name = 'WLAN Priority - High %s/Low %s - RAP' % (media_pair[0], media_pair[1])
        test_cfgs.extend(define_chariot_test_cfgs(tcfg, media_pair, com_name, 'rap'))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = 'Associate the station with high priority wlan MAP'
    test_cfgs.append(({'sta_tag': 'sta_h', 'wlan_cfg': tcfg['wlan_cfgs'][2]}, test_name, common_name, 0, False))    

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = 'Get wifi address of the high priority station MAP'
    test_cfgs.append(({'sta_tag': 'sta_h'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = 'Associate the station with low priority wlan MAP'
    test_cfgs.append(({'sta_tag': 'sta_l', 'wlan_cfg': tcfg['wlan_cfgs'][3]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = 'Get wifi address of the low priority station MAP'
    test_cfgs.append(({'sta_tag': 'sta_l'}, test_name, common_name, 0, False))
    
    for media_pair in tcfg['media_pairs']:
        com_name = 'WLAN Priority - High %s/Low %s - MAP' % (media_pair[0], media_pair[1])
        test_cfgs.extend(define_chariot_test_cfgs(tcfg, media_pair, com_name, 'map'))
    
    test_name = 'CB_Remove_Tmp_Files'
    common_name = 'Remove chariot temporary files'
    test_cfgs.append(({'filename_list': tcfg['chariot_tmp_files'].values()},
                       test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD after test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
            
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 rap = '',
                 map = '',
                 target_sta_1 = '',
                 target_sta_2 = '',
                 ts_name = '',
                 test_pc_ip = '192.168.0.10',
                )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs['interactive_mode']:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            rap = raw_input("Choose a root AP: ")
            if rap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % rap
            
            else:
                break
        
        while True:
            map = raw_input("Choose a mesh AP: ")
            if rap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % map
            
            else:
                break
        
        test_pc_ip = raw_input("Input the test PC IP address(Enter to remain the default value: 192.168.0.10): ")
        if not test_pc_ip:
            test_pc_ip = attrs['test_pc_ip']
     
        target_sta_1 = testsuite.getTargetStation(sta_ip_list)
        target_sta_2 = testsuite.getTargetStation(sta_ip_list)
        
    else:
        rap = attrs['rap']
        map = attrs['map']
        test_pc_ip = attrs['test_pc_ip']
        target_sta_1 = attrs['target_sta_1']
        target_sta_2 = attrs['target_sta_1']
    
    rap_model = ap_sym_dict[rap]['model']
    rap_radio_mode = lib_Constant.get_radio_mode_by_ap_model(rap_model)
    
    map_model = ap_sym_dict[map]['model']
    map_radio_mode = lib_Constant.get_radio_mode_by_ap_model(map_model)
    
    wlan_cfgs = define_wlan_cfgs()
    wgs_cfg = define_wlangroup_cfg(wlan_cfgs)
    media_pairs = define_media_pairs()
    
    tcfg = dict(rap = rap,
                rap_radio_mode = rap_radio_mode,
                map = map,
                map_radio_mode = map_radio_mode,
                wlan_cfgs = wlan_cfgs,
                wgs_cfg = wgs_cfg,
                target_sta_h = target_sta_1,
                target_sta_l = target_sta_2,
                test_pc_ip = test_pc_ip,
                media_pairs = media_pairs,
                chariot_tmp_files = CHARIOT_TMP_FILES
                )
    
    test_cfgs = define_test_cfgs(tcfg)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Mesh - WLAN Priority Basic Test"

    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether WLAN priority function works well",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
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
    
    