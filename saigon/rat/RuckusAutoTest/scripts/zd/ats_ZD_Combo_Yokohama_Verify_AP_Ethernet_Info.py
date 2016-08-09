"""
Verify AP Ethernet port information shown on ZD GUI/ZD CLI/SNMP
    
    expect result: All steps should result properly.
    
    How to:
        1) Verify AP Ethernet info on ZD GUI
        2) Verify AP Ethernet info on ZD CLI
        3) Verify AP Ethernet info by SNMP v2 and v3
        4) Reboot ZD
        5) Repeat step 1)-4)
        6) Set ZD factory default
        7) Repeat step 1)-4)
        8) Reboot AP
        9) Repeat step 1)-4)
        10) Delete AP
        11) Repeat step 1)-4)
        12) Disable AP interface in L3 switch
        13) Repeat step 1)-4)
        13) Enable AP interface in L3 switch
        14) Repeat step 1)-4)

Created on 2013-01-20
@author: kevin.tan
"""


import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []

    ap_tag = 'aptag'
    ap_status = cfg['ap_status']
    
    snmp_cfg_v2 = cfg['snmp_cfg_v2']
    snmp_cfg_v3 = cfg['snmp_cfg_v3']
    snmp_agent_cfg_v2 = cfg['snmp_agent_cfg_v2']
    snmp_agent_cfg_v3 = cfg['snmp_agent_cfg_v3']

    port_status = 'enable'
    if ap_status == 'mesh':
        port_status = 'disable'

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_case_name = '[AP Ethernet info normally]'
    test_name = 'CB_ZD_Verify_AP_Detail_Info'
    common_name = '%sVerify info on GUI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on ZD CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on SNMP' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status, 
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))

    test_case_name = '[AP Ethernet info after ZD reboot]'
    test_name = 'CB_ZD_Reboot'
    common_name = '%sReboot ZD' % (test_case_name)
    test_cfgs.append(({},test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Verify_AP_Detail_Info'
    common_name = '%sVerify info on GUI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on ZD CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on SNMP' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status, 
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))

    test_case_name = '[AP Ethernet info after set ZD factory]'
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%ssetting ZD to factory default' % (test_case_name)
    test_cfgs.append(({},test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Verify_AP_Detail_Info'
    common_name = '%sVerify info on GUI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on ZD CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on SNMP' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status,
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))


    test_case_name = '[AP Ethernet info after AP reboot]'
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%sReboot active AP' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 1, False))

    test_name = 'CB_ZD_Verify_AP_Detail_Info'
    common_name = '%sVerify info on ZD GUI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on ZD CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on SNMP' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status,
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))


    test_case_name = '[AP Ethernet info after AP deleted]'
    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 1, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining ZD again' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Detail_Info'
    common_name = '%sVerify info on ZD GUI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on ZD CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
    common_name = '%sVerify info on SNMP' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'port_status': port_status,
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))


    if ap_status != 'mesh':
        test_case_name = '[AP Ethernet info after AP interface disabled enabled]'
        test_name = 'CB_ZD_Disable_AP_Interface'
        common_name = '%sDisable AP interface port of active AP' % test_case_name
        test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 1, False))
    
        test_name = 'CB_ZD_Verify_AP_Detail_Info'
        common_name = '%sVerify info on ZD GUI' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'port_status': 'disable'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
        common_name = '%sVerify info on ZD CLI' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'port_status': 'disable'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
        common_name = '%sVerify info on SNMP' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'port_status': 'disable', 'interface': 'disable',
                           'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                           'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                           }, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Enable_AP_Interface'
        common_name = '%sEnable AP interface port of active AP' % test_case_name
        test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_AP_Detail_Info'
        common_name = '%sVerify info on GUI again' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'port_status': 'enable'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_CLI_Verify_AP_Ethernet_Info'
        common_name = '%sVerify info on ZD CLI again' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'port_status': 'enable'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_SNMP_Verify_AP_Ethernet_Info'
        common_name = '%sVerify info on SNMP again' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag, 'port_status': 'enable',
                           'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                           'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                           }, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Enable_AP_Interface'
        common_name = '%sEnable AP interface port of active AP at last' % test_case_name
        test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, True))

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
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    active_ap = active_ap_list[0]
    ap_model = ap_sym_dict[active_ap]['model']
    if 'mesh' in ap_sym_dict[active_ap]['status'].lower():
        ap_status = 'mesh' 
    else:
        ap_status = 'non mesh' 

    snmp_agent_cfg_v3 = {'version': 3,
                          'enabled': True,
                          'ro_sec_name': 'ruckus-read',
                          'ro_auth_protocol': 'MD5',
                          'ro_auth_passphrase': '12345678',
                          'ro_priv_protocol': 'DES',
                          'ro_priv_passphrase': '12345678',
                          'rw_sec_name': 'ruckus-write',
                          'rw_auth_protocol': 'MD5',
                          'rw_auth_passphrase': '12345678',
                          'rw_priv_protocol': 'DES',
                          'rw_priv_passphrase': '12345678',
                         }
    
    snmp_agent_cfg_v2 = {'version': 2,
                          'enabled': True,
                          'ro_community': 'public',
                          'rw_community': 'private',
                          'contact': 'support@ruckuswireless.com',
                          'location': 'shenzhen',
                         }
    
    snmp_cfg_v3 = {'ip_addr': tbcfg['ZD']['ip_addr'],
                'version': 3,
                'timeout': 20,
                'retries': 3,}
    
    snmp_cfg_v2 = {'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}

    tcfg = {
            'active_ap':active_ap,
            'ap_model': ap_model,
            'ap_status': ap_status,
            'snmp_cfg_v2': snmp_cfg_v2,
            'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
            'snmp_cfg_v3': snmp_cfg_v3,
            'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
        }
    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "AP Ethernet Info Verification - %s" % ap_model
        if ap_status == 'mesh':
            ts_name = "%s Mesh" % ts_name

    ts = testsuite.get_testsuite(ts_name, "AP Ethernet Info Verification" , combotest=True)

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
