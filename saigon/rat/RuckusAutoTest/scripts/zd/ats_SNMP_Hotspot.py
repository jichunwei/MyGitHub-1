#total case 1, covering 6 mib nodes.

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
    snmp_aaa_cfg = tcfg['snmp_aaa_cfg']
    snmp_aaa_content_cfg = tcfg['snmp_aaa_content_cfg']
    snmp_hotspot_cfg = tcfg['snmp_hotspot_cfg']
    hotspot_cfg = tcfg['hotspot_cfg']
    del_wlan = tcfg['snmp_del_wlan_cfg']
    del_hotspot = tcfg['snmp_del_hotspot_cfg']
    del_aaa = tcfg['snmp_del_aaa_cfg']   
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD'
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
    
##    config_aaa_server
    test_case_name = 'Create an aaa server'
    test_cfgs.extend(create_and_verify(test_case_name,snmp_cfg,snmp_aaa_cfg,0,False))
    
##    modify the content of the aaa_server
    test_case_name = 'Modify content of the aaa server'
    test_cfgs.extend(create_and_verify(test_case_name,snmp_cfg,snmp_aaa_content_cfg,0,False))    
##    config_hotspot
    test_case_name = '[Create and delete a hotspot profile]'
    test_cfgs.extend(create_and_verify(test_case_name,snmp_cfg,snmp_hotspot_cfg,1,False))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'   
    common_name = "%sConfigure aaa server in hotspot profile"%test_case_name
    test_cfgs.append(({'hotspot_conf': hotspot_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Create_Wlans'
    common_name = '%sCreate Wlans via SNMP V3'%test_case_name
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_v3_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'create_wlan_cfg_list': [snmp_wlan_cfg]}, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Create_Station'
    common_name = '%sCreate target station'%test_case_name
    test_cfgs.append(({'sta_ip_addr':tcfg['target_station'],
                       'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station'%test_case_name
    test_cfgs.append(({'sta_tag':'sta_1'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%sStart browser in station'%test_case_name
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'browser_tag':'browser_tag'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sAssociate the station'%test_case_name
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg':wlan_cfg}, test_name, common_name, 2, False))


    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    common_name = '%sPerform Hotspot authentication for client'%test_case_name
    test_cfgs.append(({'sta_tag':'sta_1', 
                       'browser_tag': 'browser_tag',
                       'username': 'ras.eap.user', 
                       'password': 'ras.eap.user',},
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sVerify station pinging to the server succeeds'%test_case_name
    test_cfgs.append(({'sta_tag': 'sta_1',}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = '%sQuit browser in Station for the next test'%test_case_name
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'browser_tag':'browser_tag'}, test_name, common_name, 2, True))
                       
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station after test'%test_case_name
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))

##    delete wlan
    test_case_name = '%sDelete the wlan after test'%test_case_name
    test_cfgs.extend(delete_and_verify(test_case_name,snmp_cfg,del_wlan,2,True))
    
##    delete hotspot profile
    test_case_name = '%sDelete the hotspot profile after test'%test_case_name
    test_cfgs.extend(delete_and_verify(test_case_name,snmp_cfg,del_hotspot,2,True))
    
##    delete aaa server
    test_case_name = 'Delete the aaa server after test'
    test_cfgs.extend(delete_and_verify(test_case_name,snmp_cfg,del_aaa,0,True)) 

    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V%s after test'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg': {'version': snmp_version, 'enabled': True}}, 
                      test_name, common_name, 0, True))  
    return test_cfgs
                          
def create_and_verify(test_case_name,snmp_cfg,mib_nodes,level,is_cleanup):

    tcs_cfgs = []

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '%sSet mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, level, is_cleanup))
                      
###get
    if level == 1:
        level = 2
    test_name = 'CB_SNMP_Get_Values'
    common_name = '%sGet mib values after set'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes},
                      test_name, common_name, level, is_cleanup)) 
                                           
###check

    test_name = 'CB_Verify_SNMP_Values'
    common_name = '%sVerify mib values same with expected'%test_case_name
    tcs_cfgs.append(({'mib_nodes':mib_nodes,'compare_value':True}, 
                      test_name, common_name, level, is_cleanup))
                      
    return tcs_cfgs

def delete_and_verify(test_case_name,snmp_cfg,mib_nodes,level,is_cleanup):
    tcs_cfgs = []

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '%sSet mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, level, is_cleanup))
                      
###get
    
    test_name = 'CB_SNMP_Get_Values'
    common_name = '%sGet mib values after set'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative':True},
                      test_name, common_name, level, is_cleanup)) 
                      
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

    tcfg['snmp_wlan_cfg'] = dict(ssid = 'RAT-SNMP-Hotspot-Test', desc = 'RAT-SNMP-Hotspot-Test', name = 'RAT-SNMP-Hotspot-Test', service_type = 'hotSpotService(3)',
                   auth = 'open(1)', encrypt = 'none-enc(6)', wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                   auth_server_id = '3', wireless_client = 'none(1)', zero_it_activation = 'enable(1)', hotspot_profile_id = '1', service_priority = 'high(1)',
                   accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable', downlink_rate = 'disable',
                   vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                   max_clients_per_ap = '100', web_auth = 'disable(2)')

    tcfg['wlan_cfg'] = dict(ssid = 'RAT-SNMP-Hotspot-Test',type = 'hotspot',auth = 'open', encryption = 'none', username ='ras.eap.user',password = 'ras.eap.user',)
    snmp_del_wlan_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDWLANConfigRowStatus.1','type':'INTEGER','value':'6'},                                 
                                 ]} 
    tcfg['snmp_del_wlan_cfg'] = snmp_del_wlan_cfg[zd_version]
    tcfg['hotspot_cfg'] = {
        'name': "SNMP_TEST",
        'login_page_url': r'http://192.168.0.250/login.html',
        'idle_timeout': None,
        'authentication_server':'snmp_test',
        }
    snmp_hotspot_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDHotspotName.1','type':'STRING','value':'SNMP_TEST'},
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDHotspotRedirectLoginPage.1','type':'STRING','value':r'http://192.168.0.250/login.html'},
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDHotspotRedirectStartURL.1','type':'STRING','value':r'http://192.168.0.252'},
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDHotspotRedirectType.1','type':'INTEGER','value':'2'},
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDHotspotRowStatus.1','type':'INTEGER','value':'4'},
                               ],}
    tcfg['snmp_hotspot_cfg'] = snmp_hotspot_cfg[zd_version]

    snmp_del_hotspot_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-WLAN-CONFIG-MIB','oid':'ruckusZDHotspotRowStatus.1','type':'INTEGER','value':'6'},
                                  ]}
    tcfg['snmp_del_hotspot_cfg'] = snmp_del_hotspot_cfg[zd_version]
    snmp_aaa_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAAConfigName.3','type':'STRING','value':'snmp_test'},
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAAConfigServiceType.3','type':'INTEGER','value':'3'},
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAAConfigRowStatus.3','type':'INTEGER','value':'4'},
                          ]}
    tcfg['snmp_aaa_cfg'] = snmp_aaa_cfg[zd_version]
    
    snmp_del_aaa_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAAConfigRowStatus.3','type':'INTEGER','value':'6'},
                               ]}     
    tcfg['snmp_del_aaa_cfg'] = snmp_del_aaa_cfg[zd_version]

    snmp_aaa_content_cfg = {'9.7':[
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAARadiusBackupControl.3','type':'INTEGER','value':'2'},
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAARadiusPrimarySvrIpAddress.3','type':'STRING','value':'192.168.0.252'},
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAARadiusPrimarySvrPort.3','type':'INTEGER','value':'1812'},
        {'access_type':'rw','model':'RUCKUS-ZD-AAA-MIB','oid':'ruckusZDAAARadiusPrimarySvrPasswd.3','type':'STRING','value':'1234567890'},
                                    ]}                             
    tcfg['snmp_aaa_content_cfg'] = snmp_aaa_content_cfg[zd_version]

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
            ts_name = '%s Hotspot Test - SNMP V%s'%(zd_version,snmp_version)
            ts = testsuite.get_testsuite(ts_name, 'Hotspot Test - SNMP V%s'%snmp_version, combotest=True)
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
