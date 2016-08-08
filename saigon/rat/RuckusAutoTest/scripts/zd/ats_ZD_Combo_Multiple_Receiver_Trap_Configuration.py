'''
Description:
  This test suite is used to verify the configuration of Multiple SNMP trap servers via CLI and GUI including enable/disable, format, server ip, etc.
    
  How to test:
  1. Enable/Disable snmp trap via GUI and CLI
  2. Set snmp format to SNMPv2 and SNMPv3
  3. Configure two SNMP V2 trap servers via GUI
  4. Configure two SNMP V2 trap servers via CLI
  5. Configure two SNMP V3 trap servers via GUI
  6. Configure two SNMP V3 trap servers via CLI
  7. Verfiy the snmp trap info got via CLI and GUI is the same
  8. Configure two SNMP V3 trap servers and verify the snmp trap configuration still existing after reboot ZD
  
Created on 2012-6-2
@author: zoe.huang@ruckuswireless.com

'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'Clean environment by setting ZD to factory default'
    test_cfgs.append(({},test_name, common_name, 0, False))  
    
    #1. SNMP trap enable/disable via GUI and CLI

    test_case_name = '[SNMP trap enable/disable] '
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sEnable SNMP Trap via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sEnable SNMP Trap via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['default_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sDisable SNMP Trap via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
 

    #2. SNMP trap format set to V2 and V3

    test_case_name = '[SNMP trap format] '
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap_Format'
    common_name = '%sSet trap format to SNMPv2' % test_case_name
    param_cfg = {'version': tcfg['enable_v2_trap_cfg']['version']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap_Format'
    common_name = '%sSet trap format to SNMPv3' % test_case_name
    param_cfg = {'version': tcfg['enable_v3_trap_cfg']['version']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    

    #3. SNMPv2 Trap server config from ZD Web UI

    test_case_name = '[SNMPv2 Trap server config from ZD Web UI] '
        
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv2 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv2 trap servers are configured successfully via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))


    #4. SNMPv2 Trap server config from ZD CLI

    test_case_name = '[SNMPv2 Trap server config from ZD CLI] '
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv2 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv2': '2'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sConfigure two SNMPv2 Trap servers via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap info via CLI' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify two SNMPv2 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMP Trap info' % test_case_name
    param_cfg = {'snmpv2': '2'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sDisable SNMP Trap' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    

    #5. SNMPv3 Trap server config from ZD Web UI
     
    test_case_name = '[SNMPv3 Trap server config from ZD Web UI] '
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv3 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv3 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))    

    #6. SNMPv3 Trap server config from ZD CLI
 
    test_case_name = '[SNMPv3 Trap server config from ZD CLI] '
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv3 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sConfigure two SNMPv3 Trap servers via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap info via CLI' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify two SNMPv3 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMP Trap info' % test_case_name
    param_cfg = {'snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sDisable SNMP Trap' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
 
    #7. Config synchronization between ZD CLI and Web UI
    test_case_name = '[Config synchronization between ZD CLI and Web UI] '
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv2 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap info via CLI' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMPv2 Trap Info between GUI Get and CLI Get' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
    
    #8. SNMP trap config existing after reboot zd
    test_case_name = '[SNMP trap config existing after reboot zd] '
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv3 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv3 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%sReboot ZD via CLI' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI after reboot ZD' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv3 trap servers still exist after reboot ZD' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))   
    
    
    return test_cfgs

    
def define_test_parameters(tbcfg, trap_server_ip_1, trap_server_ip_2):
    
    default_v2_trap_cfg = {'version': 2,
                           'enabled': True,
                           '1': {'server_ip':trap_server_ip_1},
                          }
    
    enable_v2_trap_cfg = {'version': 2,
                           'enabled': True,
                           '1': {'server_ip':trap_server_ip_1},
                           '2': {'server_ip':trap_server_ip_2},
                          }
    enable_v3_trap_cfg = {'version': 3,
                          'enabled': True,
                          '1': {'sec_name': 'ruckus-read1',
                              'server_ip': trap_server_ip_1,
                              'auth_protocol': 'MD5',
                              'auth_passphrase': '12345678',
                              'priv_protocol': 'DES',
                              'priv_passphrase': '12345678',
                              },
                          '2': {'sec_name': 'ruckus-read2',
                              'server_ip': trap_server_ip_2,
                              'auth_protocol': 'SHA',
                              'auth_passphrase': '12345678',
                              'priv_protocol': 'AES',
                              'priv_passphrase': '12345678',
                              }
                          }
    
    disable_trap_cfg = {'enabled': False}
    enable_trap_cfg = {'enabled': True}
        
    tcfg = {
            'default_v2_trap_cfg': default_v2_trap_cfg,
            'enable_v2_trap_cfg': enable_v2_trap_cfg,
            'enable_v3_trap_cfg': enable_v3_trap_cfg,
            'disable_trap_cfg': disable_trap_cfg,
            'enable_trap_cfg': enable_trap_cfg,
            }
    
    return tcfg

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


def create_test_suite(**kwargs):    
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ts_name = 'Multiple trap receivers - Configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify enable/disable, format, multiple server ip can be set for SNMP Trap via CLI and GUI', combotest=True)
    
    trap_server_ip_1 = raw_input("Please input ipv4 addr of dhcp server[192.168.0.252]: ")
    if not trap_server_ip_1:
        trap_server_ip_1 = '192.168.0.252'
    trap_server_ip_2 = raw_input("Please input ipv6 addr of dhcp server[2020:db8:1::252]: ")   
    if not trap_server_ip_2:
        trap_server_ip_2 = '2020:db8:1::252'

    
    tcfg = define_test_parameters(tbcfg, trap_server_ip_1, trap_server_ip_2)    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
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
    create_test_suite(**_dict)
    
