"""
	BandSwitch configuration sanity check for ZF7321, ZF7321-u, etc
    
    expect result: All steps should result properly.
    
    How to:
        1)  Set ZD factory default
        2)  Verify Radio Band info AP configuration and AP group configuration
        3)  Clear all events
        4)  Modify AP radio band to 5G by modifying default AP group info
        5)  Verify AP still joining System Default group and band switch from 2.4G to 5G event is shown on ZD GUI
        6)  Clear all events
        7)  Modify AP radio band to 2.4G by modifying AP specific info
        8)  Verify AP still joining System Default group and band switch from 5G to 2.4G event is shown on ZD GUI
        9)  Clear all events
        10) Reboot AP
        11) Verify no band switch is shown on ZD GUI
        12) Reboot ZD
        13) Verify no band switch is shown on ZD GUI
        14) Delete AP from ZD GUI
        15) Verify AP still joining System Default group and band switch from 2.4G to 5G event is shown on ZD GUI
        16) Set ZD factory default
        17) Create new AP group
        18) Clear all events
        19) Move AP from default to new
        20) Verify AP is in new AP group with band switch still 2.4G, and no band switch is shown on ZD GUI
        21) Verify Radio Band info AP configuration and AP group configuration
        22) Clear all events
        23) Modify AP radio band to 5G by modifying default AP group info
        24) Verify AP still joining new AP group and band switch from 2.4G to 5G event is shown on ZD GUI
		25) Clear all events
		26) Modify AP radio band to 2.4G by modifying new AP group info(override default AP group info)
		27) Verify AP still joining new AP group and band switch from 5G to 2.4G event is shown on ZD GUI
        28) Clear all events
		29) Modify AP radio band to 5G by modifying AP specific info
        30) Verify AP still joining new AP group and band switch from 2.4G to 5G event is shown on ZD GUI
		31) Clear all events
        32) Reboot AP
        33) Verify no band switch is shown on ZD GUI
        34) Reboot ZD
        35) Verify no band switch is shown on ZD GUI
        36) Delete AP from ZD GUI
        37) Verify AP still joining System Default group and band switch from 5G to 2.4G event is shown on ZD GUI
		38) Set ZD factory default to recover test enviroment

Created on 2012-12-20
@author: kevin.tan
"""

import os
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    
    ap_model = cfg['ap_model']
    ap_tag = 'ap_bandswitch'
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    apgrp_default       = 'System Default'
    apgrp_new           = 'APGroup_BandSwitch'


    ####################### TEST CASE I ###############################
    test_case_name = "[Default AP group]"

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sClean environment by setting ZD to factory default' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Verify_Radio_Band'
    common_name = '%sVerify Radio Band of AP and AP group after set ZD factory' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'ap_model': ap_model,
                       'ap_group': apgrp_default,
                       'apgrp_radioband_type': '',
                       'apgrp_radioband_value': '2.4 GHz',
                       'ap_radioband_type': 'reserve',
                       'ap_radioband_value': '2.4 GHz',},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before modify AP group info' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Modify_AP_Group_Info'
    common_name = '%sModify AP %s to radio band 5G in default AP group' % (test_case_name, ap_model)
    test_cfgs.append(({'ap_group': apgrp_default, 'ap_model': ap_model, 'apgrp_radioband': '5 GHz',}, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and band switch 5G event' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_band_switch': 'configure', 'band_switch_new': '5 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before config AP radio' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfig active AP Radio - Band Switch from 5G to 2.4G' % test_case_name
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'radio_band_type': 'override',
                   'radio_band_value': '2.4 GHz',
                   'ap_cfg': {'radio': 'ng', 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and band switch 2.4G event' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_band_switch': 'configure', 'band_switch_new': '2.4 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before AP reboot' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%sReboot active AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and band switch still 2.4G after ap reboot' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_band_switch': 'negative', 'band_switch_new': '2.4 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before ZD reboot' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot'
    common_name = '%sReboot ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and band switch still 2.4G after zd reboot' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_band_switch': 'negative', 'band_switch_new': '2.4 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before deleting AP' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and band switch 5G event after delete AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_band_switch': 'rejoin', 'band_switch_new': '5 GHz'},
                      test_name, common_name, 2, False))


    ####################### TEST CASE II ###############################
    test_case_name = "[New Created AP group]"

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sClean environment by setting ZD to factory default' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = '%sCreate new AP group' % test_case_name
    test_cfgs.append(({'name':apgrp_new, 
                       'description': '%s_Description' % apgrp_new,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before move AP to new group' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from System Default to new AP group' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_default,
                       'move_to_ap_group':apgrp_new, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group and band switch still 2.4G ' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'negative', 'band_switch_new': '2.4 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radio_Band'
    common_name = '%sVerify Radio Band of AP and AP group after move AP group member' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'ap_model': ap_model,
                       'ap_group': apgrp_new,
                       'apgrp_radioband_type': 'reserve',
                       'apgrp_radioband_value': '2.4 GHz',
                       'ap_radioband_type': 'reserve',
                       'ap_radioband_value': '2.4 GHz',},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before modify AP group info to 5G' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Modify_AP_Group_Info'
    common_name = '%sModify AP %s to radio band 5G in default AP group' % (test_case_name, ap_model)
    test_cfgs.append(({'ap_group': apgrp_new, 'ap_model': ap_model, 'apgrp_radioband': '5 GHz',}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group and band switch 5G event' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'configure', 'band_switch_new': '5 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before modify AP group info to 2.4G' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Modify_AP_Group_Info'
    common_name = '%sModify AP %s to radio band 2.4G in new AP group' % (test_case_name, ap_model)
    test_cfgs.append(({'ap_group': apgrp_new, 'ap_model': ap_model, 'apgrp_radioband': '2.4 GHz',}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group and band switch 2.4G event' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'configure', 'band_switch_new': '2.4 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before AP radio band switch' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfig active AP Radio - Band Switch from 2.4G to 5G' % test_case_name
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'radio_band_type': 'override',
                   'radio_band_value': '5 GHz',
                   'ap_cfg': {'radio': 'na', 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group and band switch 5G event again' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'configure', 'band_switch_new': '5 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before AP reboot' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%sReboot active AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group and band switch still 5G after AP reboot' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'negative', 'band_switch_new': '5 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before ZD reboot' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot'
    common_name = '%sReboot ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group and band switch still 5G after ZD reboot' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'negative', 'band_switch_new': '5 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before deleting AP' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining new AP group but band switch is 2.4G when first join' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_new, 'event_band_switch': 'rejoin', 'band_switch_new': '2.4 GHz'},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'Recover to original environment settings at last'
    test_cfgs.append(({},test_name, common_name, 0, True))  

    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
  
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    model = ''
    while(True):
        if ts_cfg["interactive_mode"]:
            target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
            active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        else:
            target_sta = sta_ip_list[ts_cfg["station"][0]]
            if kwargs["targetap"]:
                active_ap_list = sorted(ap_sym_dict.keys())

        model = ap_sym_dict[active_ap_list[0]]['model'].lower() 
        if  model == 'zf7321' or model == 'zf7321-u':
            break
    
        print("Appointed AP is not Band Switch AP(zf7321, zf7321-u), select is again:\n\n\n")

    tcfg = {
            'target_station':'%s' % target_sta,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'ap_model': model,
            }
    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Band Switch for %s" % (model)

    ts = testsuite.get_testsuite(ts_name, "Band Switch" , combotest=True)

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
