#total case 8

import sys
import copy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg,trap_version):

    test_cfgs = []

    wlan_cfg = tcfg['wlan_cfg']
    sta_wlan_cfg = dict(ssid = 'snmp_trap_test', auth = 'open', encryption = 'none')
    radio_mode = tcfg['radio_mode']

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs from CLI.'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = 'Create WLAN from CLI.'
    test_cfgs.append(({'wlan_conf':wlan_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station sta1'
    test_cfgs.append(({'sta_ip_addr':tcfg['target_station'][0],
                       'sta_tag': 'sta_1'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station sta2'
    test_cfgs.append(({'sta_ip_addr':tcfg['target_station'][1],
                       'sta_tag': 'sta_2'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Enable SNMP Trap V%s with Default Config from CLI'%trap_version
    param_cfg = {'snmp_trap_cfg':tcfg['trap_zd_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': tcfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':tcfg['active_ap_list'][0],
                       'ap_tag': 'ap_01'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': 'ap_01',
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }   
    test_cfgs.append((test_params, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_Cfg_Event_Log_Level'
    common_name = 'Set event log level to high - show more'
    param_cfg = {'log_level':'high'}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))


    trap_server_cfg1 = copy.deepcopy(tcfg['trap_server_cfg'])
    trap_server_cfg1['timeout'] = 300
###testcase 1 'ClientJoin','ClientDisconnect'  
    test_case_name = '[ClientJoin and ClientDisconnect]' 

    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg1}, 
                      test_name, common_name, 1, False))
  
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sAssociate the station sta1' % (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg':sta_wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station after test'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))   

    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the trap on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg1,
                       'expect_traps': {'ClientJoin':tcfg['snmp_traps']['ClientJoin'],
                                        'ClientDisconnect':tcfg['snmp_traps']['ClientDisconnect'],}
                       }, 
                      test_name, common_name, 2, True))
  
### testcase 2 'ClientJoinFailed'
    test_case_name = '[ClientJoinFailed]'

    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset max client number to 1'%test_case_name
    test_cfgs.append(({'set_type':'Min'}, test_name, common_name, 1, False))

    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg1}, 
                      test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sAssociate the station sta1' % (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg':sta_wlan_cfg}, test_name, common_name, 2, False))  
  
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sAssociate the station sta2' % (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_2','wlan_cfg':sta_wlan_cfg,'negative_test':True,}, test_name, common_name, 2, False))  

    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the trap on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg1,
                       'expect_traps': {'ClientJoinFailed':tcfg['snmp_traps']['ClientJoinFailed'],},}, 
                      test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station sta1 after test'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station sta2 after test'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_2'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset max client number to max'%test_case_name
    test_cfgs.append(({'set_type':'Max'}, test_name, common_name, 1, False))        
    
###testcase 3    'APSystemWarmStartTrap' ,'APAvailableStatusTrap'
    test_case_name = "[APSystemWarmStartTrap and APAvailableStatusTrap]"
##  enable trap server
    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':tcfg['trap_server_cfg']}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%sReboot AP to get trigger the trap'% (test_case_name)
    test_cfgs.append(({'ap_tag': 'ap_01',
                       'reboot': 'by zd'}, test_name, common_name, 2, False))

    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the traps on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':tcfg['trap_server_cfg'],
                       'expect_traps': {'APSystemWarmStartTrap':tcfg['snmp_traps']['APSystemWarmStartTrap'] ,
                                        'APAvailableStatusTrap':tcfg['snmp_traps']['APAvailableStatusTrap'] ,
                                        },
                       }, 
                      test_name, common_name, 2, True))

###testcase 4    'APLostHeartbeatTrap' , 'APLostTrap'
    test_case_name = "[APLostHeartbeatTrap and APLostTrap]"  
    
    trap_server_cfg2 = copy.deepcopy(tcfg['trap_server_cfg'])
    trap_server_cfg2['timeout'] = 1800

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete all static routes'% (test_case_name)
    test_cfgs.append(({'operation': 'delete all',
                       'parameter': None}, test_name, common_name, 1, False)) 
 
    test_name = 'CB_Server_Start_SNMPTrap_Server'
    common_name = '%sEnable SNMP trap server on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg2}, 
                      test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure an invalid route to AP'% (test_case_name)
    test_cfgs.append(({'operation': 'add',
                       'parameter': None, 'ap_tag': 'ap_01'}, test_name, common_name, 2, False))   

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sWait active AP status changed to disconnected' % (test_case_name)
    test_cfgs.append(({'ap_tag': 'ap_01', 'expected_status':'disconnected'}, test_name, common_name, 2, False))

    test_name = 'CB_Server_Check_Trap_Items'
    common_name = '%sCheck the traps on server'% (test_case_name)
    test_cfgs.append(({'snmp_trap_cfg':trap_server_cfg2,
                       'expect_traps': {'APLostHeartbeatTrap':tcfg['snmp_traps']['APLostHeartbeatTrap'], 
                                        'APLostTrap':tcfg['snmp_traps']['APLostTrap'],},
                       }, 
                      test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete all static routes after test'% (test_case_name)
    test_cfgs.append(({'operation': 'delete all',
                       'parameter': None}, test_name, common_name, 2, True))
        
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Disable SNMP Trap via CLI' 
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': tcfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Cfg_Event_Log_Level'
    common_name = 'Set event log level to default - medium'
    param_cfg = {'log_level':'medium'}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs from CLI after test.'
    test_cfgs.append(({}, test_name, common_name, 0, True))
      
    return test_cfgs

def test_process_RW(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []
###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '<%s>Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 0, False))
    
    return tcs_cfgs

def define_test_parameters(tbcfg,trap_version,zd_version):

    set_snmp_agent_cfg_v3 = {'version': 3,
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
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
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
    tcfg = {'snmp_cfg': snmp_cfg, 
            'disable_trap_cfg': disable_trap_cfg,            
            }

    tcfg['set_snmp_agent_v3_cfg'] = set_snmp_agent_cfg_v3      

    if trap_version == 2:
        tcfg['trap_server_cfg'] = trap_cfg_v2
        tcfg['trap_zd_cfg'] = enable_v2_trap_cfg
    else:
        tcfg['trap_server_cfg'] = trap_cfg_v3
        tcfg['trap_zd_cfg'] = enable_v3_trap_cfg
    tcfg['ap_reboot'] = [
        {'access_type':'rw','model':'RUCKUS-ZD-AP-MIB','oid':'ruckusZDAPConfigRebootNow.1','type':'INTEGER','value':'1'}                         
                         ]
    wlan_cfg = {
        'ssid': "snmp_trap_test" ,
        'name':"snmp_trap_test" ,
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
    tcfg['wlan_cfg'] = wlan_cfg
    
    snmp_v2_traps ={'9.7':{
    #chen.tao @2013-11-18, to fix ZF-6084
    #'APSystemWarmStartTrap':'AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*warm\s*boot\s*successfully,last\s*reboot\sreason\s*\[.+\]\.',
    'APSystemWarmStartTrap':'AP\[.*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*warm\s*boot\s*successfully,last\s*reboot\sreason\s*\[.+\]\.',
    #'APLostHeartbeatTrap':'AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*heartbeats\s*lost',
    'APLostHeartbeatTrap':'AP\[.*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*heartbeats\s*lost',
    'APAvailableStatusTrap':'AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*is\s*online',
    #'APLostTrap':'Lost\s*contact\s*with\s*AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    'APLostTrap':'Lost\s*contact\s*with\s*AP\[.*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    #'ClientJoin':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*joins\s*WLAN\[.+\]\s*from\s*AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    'ClientJoin':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*joins\s*WLAN\[.+\]\s*from\s*AP\[.*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    #'ClientDisconnect':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*disconnects\s*from\s*WLAN\[.+\]\s*at\s*AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    'ClientDisconnect':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*disconnects\s*from\s*WLAN\[.+\]\s*at\s*AP\[.*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    #'ClientJoinFailed':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*fails\s*to\s*join\s*WLAN\[.+\]\s*from\s*AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    'ClientJoinFailed':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*fails\s*to\s*join\s*WLAN\[.+\]\s*from\s*AP\[.*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    'ClientJoinFailedAPBusy':'User\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*is\s*refused\s*access\s*to\s*WLAN\[.+\]\s*from\s*AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*because\s*there\s*are\s*too\s*many\s*users\s*on\s*that\s*AP,\s*WLAN,\s*or\s*Radio\.',
    'MSG_VAP_upd':'WLAN\[.+\]\s*with\s*BSSID\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]\s*configuration\s*has\s*been\s*updated\s*on\s*radio\s*\[.+\]\s*of\s*AP\[([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\]',
    #chen.tao @2013-11-18, to fix ZF-6084
                          }
                    }
    
    snmp_v3_traps ={'9.7':{
    'APSystemWarmStartTrap':'1.3.6.1.4.1.25053.2.2.1.32',              
    'APLostHeartbeatTrap':'1.3.6.1.4.1.25053.2.2.1.6',                 
    'APAvailableStatusTrap':'1.3.6.1.4.1.25053.2.2.1.35',              
    'APLostTrap':'1.3.6.1.4.1.25053.2.2.1.5',                          
    'ClientJoin':'1.3.6.1.4.1.25053.2.2.1.60',                         
    'ClientDisconnect':'1.3.6.1.4.1.25053.2.2.1.63',                   
    'ClientJoinFailed':'1.3.6.1.4.1.25053.2.2.1.61',                   
    'ClientJoinFailedAPBusy':'1.3.6.1.4.1.25053.2.2.1.62',             
    'MSG_VAP_upd':'1.3.6.1.4.1.25053.2.2.1.33',                        
                           }
                    }
    
    if trap_version == 2:
        tcfg['snmp_traps'] = snmp_v2_traps[zd_version]
    else:
        tcfg['snmp_traps'] = snmp_v3_traps[zd_version]
    return tcfg

          
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = sorted(ap_sym_dict.keys())
    all_ap_mac_list = tbcfg['ap_mac_list']
    target_sta_radio = testsuite.get_target_sta_radio() 
            
    zd_version_list = ['9.7']    
    trap_version_list = [2,3]
    for zd_version in zd_version_list:
        for trap_version in trap_version_list:    
            tcfg = define_test_parameters(tbcfg,trap_version,zd_version)
            tcfg['active_ap_list'] = active_ap_list
            tcfg['target_station'] = sta_ip_list
            tcfg['all_ap_mac_list'] = all_ap_mac_list
            tcfg['radio_mode'] = target_sta_radio
            ts_name = '%s Trap Test - SNMP V%s'%(zd_version,trap_version)
            ts = testsuite.get_testsuite(ts_name, 'Trap Test - SNMP V%s'%trap_version, combotest=True)
            test_cfgs = define_test_cfg(tcfg,trap_version)

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

