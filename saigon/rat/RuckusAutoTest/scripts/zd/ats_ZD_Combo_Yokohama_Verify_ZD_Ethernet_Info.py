"""
Verify ZD Ethernet port information shown on ZD GUI/ZD CLI/SNMP
    
    expect result: All steps should result properly.
    
    How to:
        1) Verify ZD Ethernet info on ZD GUI
        2) Verify ZD Ethernet info on ZD CLI
        3) Verify ZD Ethernet info by SNMP v2 and v3
        4) Reboot ZD
        5) Repeat step 1)-4)
        6) Set ZD factory default
        7) Repeat step 1)-4)

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

    snmp_cfg_v2 = cfg['snmp_cfg_v2']
    snmp_cfg_v3 = cfg['snmp_cfg_v3']
    snmp_agent_cfg_v2 = cfg['snmp_agent_cfg_v2']
    snmp_agent_cfg_v3 = cfg['snmp_agent_cfg_v3']
    
    test_case_name = '[ZD Ethernet info normally]'
    test_name = 'CB_ZD_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on GUI' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on ZD CLI' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on SNMP' % (test_case_name)
    test_cfgs.append(({
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))


    test_case_name = '[ZD Ethernet info on GUI after ZD reboot]'
    test_name = 'CB_ZD_Reboot'
    common_name = '%sReboot ZD' % (test_case_name)
    test_cfgs.append(({},test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on GUI' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_case_name = '[ZD Ethernet info on CLI after ZD reboot]'
    test_name = 'CB_ZD_CLI_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on ZD CLI ' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_case_name = '[ZD Ethernet info on SNMP after ZD reboot]'
    test_name = 'CB_ZD_SNMP_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on SNMP' % (test_case_name)
    test_cfgs.append(({
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))


    test_case_name = '[ZD Ethernet info after set ZD factory]'
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%ssetting ZD to factory default' % (test_case_name)
    test_cfgs.append(({},test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on GUI]' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on ZD CLI]' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Verify_ZD_Ethernet_Info'
    common_name = '%sVerify ZD Ethernet info on SNMP]' % (test_case_name)
    test_cfgs.append(({
                       'snmp_cfg_v2': snmp_cfg_v2, 'snmp_agent_cfg_v2': snmp_agent_cfg_v2,
                       'snmp_cfg_v3': snmp_cfg_v3, 'snmp_agent_cfg_v3': snmp_agent_cfg_v3,
                       }, test_name, common_name, 2, False))

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
        ts_name = "ZD Ethernet Info Verification"

    ts = testsuite.get_testsuite(ts_name, "ZD Ethernet Info Verification" , combotest=True)

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
