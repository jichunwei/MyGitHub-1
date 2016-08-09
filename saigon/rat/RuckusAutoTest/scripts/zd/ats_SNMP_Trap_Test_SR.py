#total case 5
import sys
import copy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg,trap_version,sr_conf):

    test_cfgs = []
    zd1_sr_conf = sr_conf['zd1']
    zd2_sr_conf = sr_conf['zd2']

    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd1 before test'
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd2 before test'
    test_cfgs.append(({'target_zd':'zd2'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Enable SNMP Trap V%s via CLI on zd1'%trap_version
    param_cfg = {'snmp_trap_cfg':tcfg['trap_zd_cfg'],'target_zd':'zd1',}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Enable SNMP Trap V%s via CLI on zd2'%trap_version
    param_cfg = {'snmp_trap_cfg':tcfg['trap_zd_cfg'],'target_zd':'zd2',}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = 'Delete all static routes on zd1'
    test_cfgs.append(({'operation': 'delete all','target_zd':'zd1',
                       'parameter': None}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = 'Delete all static routes on zd2'
    test_cfgs.append(({'operation': 'delete all','target_zd':'zd2',
                       'parameter': None}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial Test Environment'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    trap_server_cfg1 = copy.deepcopy(tcfg['trap_server_cfg'])
    trap_server_cfg1['timeout'] = 100
###testcase 1 SmartRedundancyChangetoActive  
    test_case_name = '[SmartRedundancyChangetoActive]' 

    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg1}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Config_SR'
    common_name = '%sConfig Smart Redundancy via CLI on zd1' % (test_case_name)
    param_cfg = dict(sr_conf=zd1_sr_conf,wait_time=30,target_zd='zd1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the traps on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg1,
                       'expect_traps': {'SmartRedundancyChangetoActive':tcfg['snmp_traps']['SmartRedundancyChangetoActive']},
                       }, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%sDisable Smart Redundancy via CLI on zd1' % (test_case_name)
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 2, True))
    
    trap_server_cfg2 = copy.deepcopy(tcfg['trap_server_cfg'])
    trap_server_cfg2['timeout'] = 600
    
#testcase2 
    test_case_name = '[SmartRedundancyActiveDisconnected and SmartRedundancyStandbyDisconnected]' 
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%sEnable Smart Redundancy to do test'% (test_case_name)
    test_cfgs.append(({},test_name,common_name,1,False))

    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg2}, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure an invalid route on zd1' % (test_case_name)
    test_cfgs.append(({'operation': 'add','target_zd':'zd1',
                       'parameter': tcfg['invalid_route1']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure an invalid route on zd2' % (test_case_name)
    test_cfgs.append(({'operation': 'add','target_zd':'zd2',
                       'parameter': tcfg['invalid_route2']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the traps on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg2,
                       'expect_traps': {'SmartRedundancyActiveDisconnected':tcfg['snmp_traps']['SmartRedundancyActiveDisconnected'],
                                        'SmartRedundancyStandbyDisconnected':tcfg['snmp_traps']['SmartRedundancyActiveDisconnected']
                                        },
                       }, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_SR_Disable'
    common_name = '%sDisable Smart Redundancy on the two ZDs' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete the invalid route on zd1' % (test_case_name)
    test_cfgs.append(({'operation': 'delete all','target_zd':'zd1',
                       'parameter': None}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete the invalid route on zd2' % (test_case_name)
    test_cfgs.append(({'operation': 'delete all','target_zd':'zd2',
                       'parameter': None}, test_name, common_name, 2, True))

    trap_server_cfg3 = copy.deepcopy(tcfg['trap_server_cfg'])
    trap_server_cfg3['timeout'] = 600
#testcase3 
    test_case_name = '[SmartRedundancyActiveConnected and SmartRedundancyStandbyConnected]' 

    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg3}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Config_SR'
    common_name = '%sConfig Smart Redundancy via CLI on zd1' % (test_case_name)
    param_cfg = dict(sr_conf=zd1_sr_conf,target_zd='zd1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Config_SR'
    common_name = '%sConfig Smart Redundancy via CLI on zd2' % (test_case_name)
    param_cfg = dict(sr_conf=zd2_sr_conf,target_zd='zd2')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    

    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%sDisable Smart Redundancy via CLI on zd1' % (test_case_name)
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%sDisable Smart Redundancy via CLI on zd2' % (test_case_name)
    test_cfgs.append(({'target_zd':'zd2'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Config_SR'
    common_name = '%sConfig Smart Redundancy via CLI on zd2 again' % (test_case_name)
    param_cfg = dict(sr_conf=zd2_sr_conf,target_zd='zd2')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Config_SR'
    common_name = '%sConfig Smart Redundancy via CLI on zd1 again' % (test_case_name)
    param_cfg = dict(sr_conf=zd1_sr_conf,target_zd='zd1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the traps on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg3,
                       'expect_traps':{'SmartRedundancyActiveConnected':tcfg['snmp_traps']['SmartRedundancyActiveConnected'],
                                       'SmartRedundancyStandbyConnected':tcfg['snmp_traps']['SmartRedundancyStandbyConnected']
                                       },
                       }, 
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%sDisable Smart Redundancy via CLI on zd1 after test' % (test_case_name)
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = '%sDisable Smart Redundancy via CLI on zd2 after test' % (test_case_name)
    test_cfgs.append(({'target_zd':'zd2'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Disable SNMP Trap via CLI on zd1' 
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg'],'target_zd':'zd1'}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Disable SNMP Trap via CLI on zd2' 
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg'],'target_zd':'zd2'}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
      
    return test_cfgs

def test_process_RW(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []
###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '<%s>Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 0, False))
    
    return tcs_cfgs

def define_test_parameters(tbcfg,trap_version,zd1_ipaddr,zd2_ipaddr,zd_version):

    trap_cfg_v3 = dict (server_ip = '192.168.0.252',
             version = 3,
             sec_name = 'ruckus-read',
             auth_protocol = 'MD5',
             auth_passphrase = '12345678',
             priv_protocol = 'DES',
             priv_passphrase = '12345678',
             timeout = 200,
             )
     
    trap_cfg_v2 = dict(server_ip = '192.168.0.252',
             version = 2,
             timeout = 200,
             )

    enable_v2_trap_cfg = {'version': 2,
                          'enabled': True,
                          '1': {'server_ip': '192.168.0.252'},
                          }
    
    enable_v3_trap_cfg = {'version': 3,
                          'enabled': True,
                          '1': {'sec_name': 'ruckus-read',
                                'server_ip': '192.168.0.252',
                                'auth_protocol': 'MD5',
                                'auth_passphrase': '12345678',
                                'priv_protocol': 'DES',
                                'priv_passphrase': '12345678',
                                }
                          }
    disable_trap_cfg = {'enabled': False}
    tcfg = {
            'disable_trap_cfg': disable_trap_cfg,            
            }  

    if trap_version == 2:
        tcfg['trap_server_cfg'] = trap_cfg_v2
        tcfg['trap_zd_cfg'] = enable_v2_trap_cfg
    else:
        tcfg['trap_server_cfg'] = trap_cfg_v3
        tcfg['trap_zd_cfg'] = enable_v3_trap_cfg

    subnet1 = zd1_ipaddr
    subnet1 +='/32'
    temp1 = zd1_ipaddr.split('.')
    gateway1 = temp1[0]+'.'+temp1[1]+'.'+temp1[2]+'.'+'249'
    
    subnet2 = zd2_ipaddr
    subnet2 +='/32'
    temp2 = zd2_ipaddr.split('.')
    gateway2 = temp2[0]+'.'+temp2[1]+'.'+temp2[2]+'.'+'249'
    
    invalid_route1 = {'name':'invalid_route_to_zd2', 'subnet':subnet2, 'gateway':gateway2}
    invalid_route2 = {'name':'invalid_route_to_zd1', 'subnet':subnet1, 'gateway':gateway1}    
    tcfg['invalid_route1'] = invalid_route1
    tcfg['invalid_route2'] = invalid_route2
    
    snmp_v2_traps ={'9.7':{
    'SmartRedundancyActiveConnected':'\[Smart\s*Redundancy\]\s*Peer\s*ZoneDirector\[((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)\]\s*connected,\s*system\s*is\s*in\s*active\s*state\.',
    'SmartRedundancyChangetoActive':'\[Smart\s*Redundancy\]\s*Peer\s*ZoneDirector\[((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)\]\s*not\s*found,\s*system\s*changed\s*to\s*active\s*state\.',
    'SmartRedundancyStandbyConnected':'\[Smart\s*Redundancy\]\s*Peer\s*ZoneDirector\[((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)\]\s*connected,\s*system\s*is\s*in\s*standby\s*state\.',
    'SmartRedundancyActiveDisconnected':'\[Smart\s*Redundancy\]\s*Lost\s*connection\s*to\s*peer\s*ZoneDirector\[((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)\],\s*system\s*is\s*in\s*active\s*state\.',
    'SmartRedundancyStandbyDisconnected':'\[Smart\s*Redundancy\]\s*Lost\s*connection\s*to\s*peer\s*ZoneDirector\[((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)\],\s*system\s*is\s*in\s*standby\s*state\.',
                          }
                    }
    
    snmp_v3_traps ={'9.7':{                    
    'SmartRedundancyChangetoActive':'1.3.6.1.4.1.25053.2.2.1.100',     
    'SmartRedundancyActiveConnected':'1.3.6.1.4.1.25053.2.2.1.101',    
    'SmartRedundancyStandbyConnected':'1.3.6.1.4.1.25053.2.2.1.103',   
    'SmartRedundancyActiveDisconnected':'1.3.6.1.4.1.25053.2.2.1.102', 
    'SmartRedundancyStandbyDisconnected':'1.3.6.1.4.1.25053.2.2.1.104',
                           }
                    }
    
    if trap_version == 2:
        tcfg['snmp_traps'] = snmp_v2_traps[zd_version]
    else:
        tcfg['snmp_traps'] = snmp_v3_traps[zd_version]
        
    return tcfg


def def_sr_conf(zd1_ipaddr,zd2_ipaddr):
    conf = {}
    secret = 'testing'
    conf['zd1'] = {'peer_ip_addr':zd2_ipaddr,'secret':secret}
    conf['zd2'] = {'peer_ip_addr':zd1_ipaddr,'secret':secret}
    
    return conf
         
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    zd1_ipaddr = tbcfg['ZD1']['ip_addr']
    zd2_ipaddr = tbcfg['ZD2']['ip_addr']
    sr_conf = def_sr_conf(zd1_ipaddr,zd2_ipaddr) 
    zd_version_list = ['9.7']       
    trap_version_list = [2,3]
    for zd_version in zd_version_list:
        for trap_version in trap_version_list:   
            tcfg = define_test_parameters(tbcfg,trap_version,zd1_ipaddr,zd2_ipaddr,zd_version)

            ts_name = '%s SR Trap Test - SNMP V%s'%(zd_version,trap_version)
            ts = testsuite.get_testsuite(ts_name, 'SR Trap Test - SNMP V%s'%trap_version, combotest=True)
            test_cfgs = define_test_cfg(tcfg,trap_version,sr_conf)

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

