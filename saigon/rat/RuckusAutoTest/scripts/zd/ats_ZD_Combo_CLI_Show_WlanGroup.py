"""
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

import logging
import time
import copy
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_wlan_cfg_list():
    logging.info('Generate a list of the wlan configuration')
    
    conf = {'ssid': '',
            'auth': 'open',
            'encryption': 'none',
            }
    
    wlan_cfg_list = []
    for i in range(4):
        cfg = copy.deepcopy(conf)
        ssid = "zdcli-wlan-%s-%d" % (time.strftime("%H%M%S"), i)
        cfg['ssid'] = ssid
        wlan_cfg_list.append(cfg)
    
    return wlan_cfg_list
                
                
def define_wlan_group_cfg_list(wlan_cfg_list):
    logging.info('Generate a list of the wlan group configuration')
    
    wlan_list = []
    for i in range(len(wlan_cfg_list)):
        wlan_list.append(wlan_cfg_list[i]['ssid'])
    
    wlan_member = {}
    wlan_member[wlan_list[0]] = {'vlan_override': 'No Change'}
    #wlan_member[wlan_list[1]] = {'vlan_override': 'Untag'}
    wlan_member[wlan_list[1]] = {'vlan_override': 'Tag',
                                 'tag_override': '302',}
                
    wgs_cfg_list = []
    wgs_cfg_list.append(dict(name = 'Default', description = 'Default WLANs for Access Points',
                             vlan_override = True, wlan_member = wlan_member))
    
    name = "zdcli-wlan-group-%s" % time.strftime("%H%M%S")
    wgs_cfg_list.append(dict(name = name, description = '',
                             vlan_override = True, wlan_member = wlan_member))
    
    return wgs_cfg_list
    
    
def define_test_cfg(cfg):
    test_cfgs = []
    
    ex_id = "[WLANGroup configure from GUI, Check from CLI]"
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = '%s1.remove all configuration from ZD' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Get_WlanGroup_All'
    common_name = '%s2.get all wlan group information from ZD via GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '%s3.get all wlan group information from ZD via CLI' % ex_id 
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup_All'
    common_name = '%s4.verify whether the information shown in CLI is the same as in GUI' % ex_id
    test_cfgs.append(({}, test_name, common_name, 1, False))


    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%s5.create wlans via ZD GUI' % ex_id
    test_cfgs.append(( {'wlan_cfg_list':cfg['wlan_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_WlanGroup_By_Name'
    common_name = '%s6.get the default wlan group information from ZD via GUI' % ex_id   
    test_cfgs.append(({'name': 'Default'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_By_Name'
    common_name = '%s7.get the default wlan group information from ZD via CLI' % ex_id   
    test_cfgs.append(({'name': 'Default'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup'
    common_name = '%s8.verify whether the information shown in CLI is the same as in GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Edit_WlanGroup'
    common_name = '%s9.configure the default wlan group in ZD via GUI' % ex_id   
    test_cfgs.append(({'wlan_group': 'Default', 'wgs_cfg': cfg['wgs_cfg_list'][0]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_WlanGroup_By_Name'
    common_name = '%s10.get the default wlan group information from ZD via GUI' % ex_id   
    test_cfgs.append(({'name': 'Default'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_By_Name'
    common_name = '%s11.get the default wlan group information from ZD via CLI' % ex_id   
    test_cfgs.append(({'name': 'Default'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup'
    common_name = '%s12.verify whether the information shown in CLI is the same as in GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = '%s13.create a new wlan group in ZD via GUI' % ex_id   
    test_cfgs.append(({'wgs_cfg': cfg['wgs_cfg_list'][1]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_WlanGroup_All'
    common_name = '%s14.get all wlan group information from ZD via GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '%s15.get all wlan group information from ZD via CLI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup_All'
    common_name = '%s16.verify whether the information shown in CLI is the same as in GUI' % ex_id
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Get_WlanGroup_By_Name'
    common_name = '%s17.get the default wlan group information from ZD via GUI' % ex_id   
    test_cfgs.append(({'name': cfg['wgs_cfg_list'][1]['name']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_By_Name'
    common_name = '%s18.get the default wlan group information from ZD via CLI' % ex_id   
    test_cfgs.append(({'name': cfg['wgs_cfg_list'][1]['name']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup'
    common_name = '%s19.verify whether the information shown in CLI is the same as in GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = '%s20.remove all wlan group from ZD via GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_WlanGroup_By_Name'
    common_name = '%s21.get the default wlan group information from ZD via GUI' % ex_id   
    test_cfgs.append(({'name': cfg['wgs_cfg_list'][1]['name']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_By_Name'
    common_name = '%s22.get the default wlan group information from ZD via CLI' % ex_id   
    test_cfgs.append(({'name': cfg['wgs_cfg_list'][1]['name']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_WlanGroup'
    common_name = '%s23.verify whether the information shown in CLI is the same as in GUI' % ex_id   
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%s24.Open_None: remove all wlans from ZD' % ex_id
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)

    wlan_cfg_list = define_wlan_cfg_list()
    wgs_cfg_list = define_wlan_group_cfg_list(wlan_cfg_list)

    tcfg = {'wlan_cfg_list': wlan_cfg_list,
            'wgs_cfg_list': wgs_cfg_list
            }
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "ZD CLI Show Wlan Group - Combo" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the wlan group information shown is ZD CLI is correct" ,
                                 combotest=True)
    
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
    