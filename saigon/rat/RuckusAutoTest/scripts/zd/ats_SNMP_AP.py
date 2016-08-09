#total case 1+1=2

import sys
import copy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg,snmp_version):
    test_cfgs = []
    snmp_wlan_cfg = tcfg['snmp_wlan_cfg']
    wlan_cfg = tcfg['wlan_cfg']
    snmp_cfg = copy.deepcopy(tcfg['snmp_cfg'])
    snmp_agent_cfg = copy.deepcopy(tcfg['set_snmp_agent_v3_cfg'])
    snmp_cfg.update(snmp_agent_cfg)

    del_wlan = tcfg['snmp_del_wlan_cfg']
    ap_info = tcfg['ap_info']
    ap_reboot = tcfg['ap_reboot']
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V3 to create wlan'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_v3_cfg']}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SNMP_Create_Wlans'
    common_name = 'Create Wlans via SNMP V3'
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_v3_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'create_wlan_cfg_list': [snmp_wlan_cfg]}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':tcfg['target_station'],
                       'sta_tag': 'sta_1'}, test_name, common_name, 0, False)) 
   
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag':'sta_1'}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = 'Associate the station'
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg':wlan_cfg}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = 'Verify station pinging to the server succeeds'
    test_cfgs.append(({'sta_tag': 'sta_1','dest_ip': '172.16.10.252',}, test_name, common_name, 0, False))
         
    test_case_name = "Check ap info"
    test_cfgs.extend(test_process_RO(test_case_name,snmp_cfg,ap_info))
     
##   reboot all aps
    test_case_name = "Reboot all aps"
    test_cfgs.extend(test_process_RW(test_case_name,snmp_cfg,ap_reboot))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = '[%s]Verify station pinging to the server fails'%(test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_1', 'dest_ip': '172.16.10.252',}, test_name, common_name, 2, False))
                           
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]Remove all WlANs from station after test'%(test_case_name)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))

##    delete wlan
    test_cfgs.extend(delete_and_verify(snmp_cfg,del_wlan))

    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V%s after test'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg': {'version': snmp_version, 'enabled': True}}, 
                      test_name, common_name, 0, True))  
    return test_cfgs
                          
def test_process_RO(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []

###walk to get oid
    for mib_node in mib_nodes:
        test_name = 'CB_SNMP_WALK'
        common_name = '[%s]SNMP WALK %s'%(test_case_name,mib_node['oid'])
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[mib_node]},
                          test_name, common_name, 1, False))    
###get
    
    test_name = 'CB_SNMP_Get_Values'
    common_name = '[%s]Get mib values'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'oid_from_carrierbag':True,},
                      test_name, common_name, 2, False))
###check

    test_name = 'CB_Verify_SNMP_Values'
    common_name = '[%s]Verify mib values'%test_case_name
    tcs_cfgs.append(({'mib_nodes':mib_nodes,'oid_from_carrierbag':True,'clear_carrierbag':False,}, 
                      test_name, common_name, 2, False))

###set(negative test)

    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values should fail.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': True,'oid_from_carrierbag':True,}, 
                      test_name, common_name, 2, False))

    return tcs_cfgs

def test_process_RW(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []

###walk to get oid
    for mib_node in mib_nodes:
        test_name = 'CB_SNMP_WALK'
        common_name = '[%s]SNMP WALK %s'%(test_case_name,mib_node['oid'])
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[mib_node]},
                          test_name, common_name, 1, False))    

###set
    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'oid_from_carrierbag':True,'single_set':True,}, 
                      test_name, common_name, 2, False))

    return tcs_cfgs
def delete_and_verify(snmp_cfg,mib_nodes):
    tcs_cfgs = []

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = 'Set mib values.'
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 0, True))
                      
###get
    
    test_name = 'CB_SNMP_Get_Values'
    common_name = 'Get mib values after set'
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative':True},
                      test_name, common_name, 0, True)) 
                      
    return tcs_cfgs
def define_test_parameters(tbcfg,snmp_version,target_sta,target_sta_radio,zd_version):

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
        
    tcfg = {'snmp_cfg': snmp_cfg,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,                
            }

    tcfg['set_snmp_agent_v3_cfg'] = set_snmp_agent_cfg_v3      

    tcfg['snmp_wlan_cfg'] = dict(ssid = 'RAT-Open-None-SNMP-Test', desc = 'RAT-Open-None-SNMP-Test', name = 'RAT-Open-None-SNMP-Test', service_type = 'standardUsage(1)',
                   auth = 'open(1)', encrypt = 'none-enc(6)', wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                   auth_server_id = '1', wireless_client = 'none(1)', zero_it_activation = 'enable(1)', service_priority = 'high(1)',
                   accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable', downlink_rate = 'disable',
                   vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                   max_clients_per_ap = '100', web_auth = 'disable(2)')

    tcfg['wlan_cfg'] = dict(ssid = 'RAT-Open-None-SNMP-Test',auth = 'open', encryption = 'none',)
    snmp_del_wlan_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDWLANConfigRowStatus.1','type':'INTEGER','value':'6'},
                                ]
                         }   
    tcfg['snmp_del_wlan_cfg'] = snmp_del_wlan_cfg[zd_version]
     
    ap_info = {'9.7':[
        {'access_type':'ro','model':'RUCKUS-ZD-AP-MIB','oid':'ruckusZDAPConfigAPModel','type':'STRING','value':'zf2741'}                       
                       ]
               }                        
    tcfg['ap_info'] = ap_info[zd_version]

    ap_reboot = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-AP-MIB','oid':'ruckusZDAPConfigRebootNow','type':'INTEGER','value':'1'}                         
                         ]
                 }
    tcfg['ap_reboot'] = ap_reboot[zd_version]
    
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
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        
    zd_version_list = ['9.7']    
    snmp_version_list = [3]
    for zd_version in zd_version_list:
        for snmp_version in snmp_version_list:      
            tcfg = define_test_parameters(tbcfg,snmp_version,target_sta,target_sta_radio,zd_version)
            ts_name = '%s AP Test - SNMP V%s'%(zd_version,snmp_version)
            ts = testsuite.get_testsuite(ts_name, 'AP Test - SNMP V%s'%snmp_version, combotest=True)
            test_cfgs = define_test_cfg(tcfg,snmp_version)

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
