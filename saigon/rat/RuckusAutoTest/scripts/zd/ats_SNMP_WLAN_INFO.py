#total case 44+60+45+15+22+27=213

import sys
import copy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg,snmp_version,mib_list):
    test_cfgs = []
    wlan_cfg = tcfg['wlan_cfg']

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs from CLI.'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V3 to create wlan'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_v3_cfg']}, 
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_SNMP_Create_Wlans'
    common_name = 'Create Wlans via SNMP V3'
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_v3_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'create_wlan_cfg_list': [wlan_cfg]}, test_name, common_name, 0, False))    

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':tcfg['target_station'],
                       'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    sta_wlan_cfg = dict(ssid = 'RAT-Open-None-SNMP-Test', auth = 'open', encryption = 'none')
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = 'Associate the station'
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg':sta_wlan_cfg}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = 'Verify station pinging to the server succeeds'
    test_cfgs.append(({'sta_tag': 'sta_1',}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    snmp_cfg = tcfg['snmp_cfg']
    if snmp_version == 2:
        snmp_agent_cfg = tcfg['set_snmp_agent_v2_cfg']
    else:
        snmp_agent_cfg = tcfg['set_snmp_agent_v3_cfg']
    snmp_cfg.update(snmp_agent_cfg)    
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V%s'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg':snmp_agent_cfg}, 
                      test_name, common_name, 0, False))

    for item in mib_list:   
        test_case_name = item['oid']
        access_type = item['access_type']
        mib_nodes = []
        mib_nodes.append(item)
        if access_type == 'rw':
            test_cfgs.extend(test_process_RW(test_case_name,snmp_cfg,mib_nodes))
        if access_type == 'ro':
            test_cfgs.extend(test_process_RO(test_case_name,snmp_cfg,mib_nodes))
        if access_type == 'wo':
            test_cfgs.extend(test_process_WO(test_case_name,snmp_cfg,mib_nodes))

    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V%s after test'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg': {'version': snmp_version, 'enabled': False}}, 
                      test_name, common_name, 0, True))  

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs from CLI after test.'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station after test'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, True))
    
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
                      test_name, common_name, 1, False))
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

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 2, False))
                      
###get
    
    test_name = 'CB_SNMP_Get_Values'
    common_name = '[%s]Get mib values after set'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes},
                      test_name, common_name, 1, False)) 
                                           
###check

    test_name = 'CB_Verify_SNMP_Values'
    common_name = '[%s]Verify mib values same with expected'%test_case_name
    tcs_cfgs.append(({'mib_nodes':mib_nodes,'compare_value':True}, 
                      test_name, common_name, 2, False))
                      
#type_list = ['a','u','i','U','I','o','s','x','b','h','t','d','F','D']

    type_dict = {'INTEGER':'i',
                 'Gauge32':'u', 
                 'Timeticks':'t', 
                 'IpAddress':'a',
                 'OBJID':'o', 
                 'STRING':'s', 
                 'HEX STRING':'x',
                 'DECIMAL STRING':'d', 
                 'BITS':'b',
                 'Gauge64':'U', 
                 'signed int64':'I', 
                 'float':'F',
                 'double':'D'}


###set(negative test)

###set invalid type
    temp = {}
    temp = copy.deepcopy(mib_nodes[0])    
    for value_type in type_dict.keys():
        if not value_type == temp['type']:
            temp['type'] = value_type
            test_name = 'CB_SNMP_Set_Values'
            common_name = '[%s]Set mib values with invalid type <%s> should fail.'%(test_case_name,value_type)
            tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp],'negative': True}, test_name, common_name, 2, False))
###set invalid value
    temp2 = {}
    temp2 = copy.deepcopy(mib_nodes[0])       

    invalid_value_list = temp2['invalid_value_list']   
    for invalid_value in invalid_value_list:
        temp2['value'] = invalid_value
        test_name = 'CB_SNMP_Set_Values'
        common_name = '[%s]Set mib values with invalid value <%s> should fail.'%(test_case_name,invalid_value)
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp2],'negative': True}, 
                      test_name, common_name, 2, False))
                      
    return tcs_cfgs

def test_process_WO(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 2, False))

    type_dict = {'INTEGER':'i',
                 'Gauge32':'u', 
                 'Timeticks':'t', 
                 'IpAddress':'a',
                 'OBJID':'o', 
                 'STRING':'s', 
                 'HEX STRING':'x',
                 'DECIMAL STRING':'d', 
                 'BITS':'b',
                 'Gauge64':'U', 
                 'signed int64':'I', 
                 'float':'F',
                 'double':'D'}


###set(negative test)

###set invalid type
    temp = {}
    temp = copy.deepcopy(mib_nodes[0])    
    for value_type in type_dict.keys():
        if not value_type == temp['type']:
            temp['type'] = value_type
            test_name = 'CB_SNMP_Set_Values'
            common_name = '[%s]Set mib values with invalid type <%s> should fail.'%(test_case_name,value_type)
            tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp],'negative': True}, test_name, common_name, 2, False))
###set invalid value
    temp2 = {}
    temp2 = copy.deepcopy(mib_nodes[0])       

    invalid_value_list = temp2['invalid_value_list']   
    for invalid_value in invalid_value_list:
        temp2['value'] = invalid_value
        test_name = 'CB_SNMP_Set_Values'
        common_name = '[%s]Set mib values with invalid value <%s> should fail.'%(test_case_name,invalid_value)
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp2],'negative': True}, 
                      test_name, common_name, 2, False))
                      
    return tcs_cfgs
    
def define_test_parameters(tbcfg,snmp_version,target_sta,target_sta_radio):
    set_snmp_agent_cfg_v2 = {'version': 2,
                          'enabled': True,
                          'ro_community': 'public',
                          'rw_community': 'private',
                          'contact': 'support@ruckuswireless.com',
                          'location': 'shenzhen',
                         }
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

    tcfg['set_snmp_agent_v2_cfg'] = set_snmp_agent_cfg_v2
    tcfg['set_snmp_agent_v3_cfg'] = set_snmp_agent_cfg_v3

    tcfg['wlan_cfg'] = dict(ssid = 'RAT-Open-None-SNMP-Test', desc = 'RAT-Open-None-SNMP-Test', name = 'RAT-Open-None-SNMP-Test', service_type = 'standardUsage(1)',
                   auth = 'open(1)', encrypt = 'none-enc(6)', wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                   auth_server_id = '1', wireless_client = 'none(1)', zero_it_activation = 'enable(1)', service_priority = 'high(1)',
                   accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable', downlink_rate = 'disable',
                   vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                   max_clients_per_ap = '100', web_auth = 'disable(2)')
    
    return tcfg

def get_mib_list(zd_version):
    mib_list = [               
                
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANSSID','type':'STRING','value':'"New Name"'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDescription','type':'STRING','value':'"New Name"'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAuthentication','type':'STRING','value':'open'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANEncryption','type':'STRING','value':'none'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANIsGuest','type':'INTEGER','value':'2'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANSSIDBcastDisable','type':'INTEGER','value':'2'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVlanID','type':'INTEGER','value':'1'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRateLimitingUp','type':'STRING','value':'DISABLE'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRateLimitingDown','type':'STRING','value':'DISABLE'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANTunnelWLAN','type':'INTEGER','value':'2'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANNumVAP','type':'Gauge32','value':'3'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANNumSta','type':'Gauge32','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRxPkts','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRxBytes','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANTxPkts','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANTxBytes','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAuthTotal','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAuthResp','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAuthSuccessTotal','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAuthFail','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAssocTotal','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAssocResp','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANReassocReq','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANReassocResp','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAssocSuccess','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAssocFail','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAssocDenied','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDiassocAbnormal','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDiassocCapacity','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDiassocLeave','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDiassocMisc','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRxByteRate','type':'Gauge32','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANTxByteRate','type':'Gauge32','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRxDataFrameOnLan','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANRxByteOnLan','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANTxByteOnLan','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDownDropFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDownRetxFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDownTotalFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANDownTotalErrFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANUpTotalFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANUpDropFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANUpRetxFrame','type':'Counter64','value':'0'}, 
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANNAME','type':'STRING','value':'New Name'},                 
                                   
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMacAddr','type':'STRING','value':'68:92:34:c:68:80'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPDescription','type':'STRING','value':'ap'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPStatus','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPModel','type':'STRING','value':'zf2741'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPSerialNumber','type':'STRING','value':'191055005841'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPUptime','type':'Timeticks','value':'4765100'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPSWversion','type':'STRING','value':'9.7.0.0.148'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPHWversion','type':'STRING','value':'11.0.0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIPAddr','type':'IpAddress','value':'192.168.32.225'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPNumRadios','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPNumVAP','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPNumSta','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPNumRogues','type':'Gauge32','value':'122'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPConnectionMode','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMeshEnable','type':'INTEGER','value':'2'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMeshHops','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMeshType','type':'INTEGER','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXByte','type':'Counter32','value':'2137067'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXPkt','type':'Counter32','value':'23348'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXPktErr','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXPKTSucc','type':'Counter32','value':'23348'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsTXByte','type':'Counter32','value':'5036630'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsTXPkt','type':'Counter32','value':'33655'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMemUtil','type':'INTEGER','value':'11388'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMemTotal','type':'Gauge32','value':'29380'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPCPUUtil','type':'INTEGER','value':'8'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPFWSize','type':'Gauge32','value':'917504'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPFWAvail','type':'Gauge32','value':'4288835584'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMultipleVlanCapability','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAP11bCapable','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAP11gCapable','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMultiModeAccessStatus','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPEthStateChange','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPSyncConf','type':'INTEGER','value':'2'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPUpgrade','type':'INTEGER','value':'2'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPFirstJoinTime','type':'STRING','value':'"Thu Aug  1 02:23:08 2013"'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLastBootTime','type':'STRING','value':'"Wed Jul 31 13:36:14 2013"'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLastUpgradeTime','type':'STRING','value':'"Thu Aug  1 02:23:08 2013"'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLastConfSyncTime','type':'STRING','value':'"Thu Aug  1 02:23:08 2013"'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXPKTBcast','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXPKTMcast','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXPKTUcast','type':'Counter32','value':'23348'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsTXPKTBcast','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsTXPKTMcast','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsTXPKTUcast','type':'Counter32','value':'33655'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsDropped','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPTxFrameDropped','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPTxFrameError','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPCoverageTech','type':'INTEGER','value':'3'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPStaTxBytes','type':'Counter32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPStaRxBytes','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPNetmask','type':'IpAddress','value':'255.255.255.0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPGateway','type':'IpAddress','value':'192.168.32.253'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPDNS1','type':'IpAddress','value':'192.168.0.252'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPDNS2','type':'IpAddress','value':'0.0.0.0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPTotalUser','type':'Gauge32','value':'100'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsRXByteRate','type':'Counter32','value':'22'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPLANStatsTXByteRate','type':'Counter32','value':'51'},
        
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAPMacAddr','type':'STRING','value':'68:92:34:c:68:80'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRadioIndex','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRadioType','type':'INTEGER','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsChannel','type':'Gauge32','value':'11'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxPower','type':'INTEGER','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsMeshEnable','type':'INTEGER','value':'2'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsNumVAP','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsNumSta','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAvgStaRSSI','type':'INTEGER','value':'55'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRxPkts','type':'Counter64','value':'1404745'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRxBytes','type':'Counter64','value':'156550069'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRxMulticast','type':'Counter64','value':'1297'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxPkts','type':'Counter64','value':'483281'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxBytes','type':'Counter64','value':'53443952'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxMulticast','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxFail','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxRetries','type':'Counter64','value':'28610'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsPowerMgmt','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsMaxSta','type':'Gauge32','value':'100'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsFrameErrorRate','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsFrameRetryRate','type':'Gauge32','value':'591'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsMonitoredTime','type':'Timeticks','value':'334365'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTotalAssocTime','type':'Counter64','value':'1499'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAuthReq','type':'Counter64','value':'4'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAuthResp','type':'Counter64','value':'4'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAuthSuccess','type':'Counter64','value':'4'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAuthFail','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAssocReq','type':'Counter64','value':'3'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAssocResp','type':'Counter64','value':'3'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsReassocReq','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsReassocResp','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAssocSuccess','type':'Counter64','value':'3'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAssocFail','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAssocDenied','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsDiassocAbnormal','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsDiassocCapacity','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsDiassocLeave','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsDiassocMisc','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsResourceUtil','type':'Gauge32','value':'25'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRxSignalFrm','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTxSignalFrm','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsTotalSignalFrm','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsAntennaGain','type':'Gauge32','value':'7'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsBeaconPeriod','type':'Gauge32','value':'100'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsRTSThreshold','type':'Gauge32','value':'2346'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPRadioStatsFragThreshold','type':'Gauge32','value':'2346'},
                
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapBSSID','type':'STRING','value':'68:92:34:c:68:88'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapPAPAddr','type':'STRING','value':'68:92:34:c:68:80'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapSSID','type':'STRING','value':'"New Name"'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapLanRxBytes','type':'Counter64','value':'17937'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapLanTxBytes','type':'Counter64','value':'166792'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanRxBytes','type':'Counter64','value':'166792'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanTxBytes','type':'Counter64','value':'17937'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanRxErrorPkt','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanRxUnicastPkt','type':'Counter64','value':'939'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanTxUnicastPkt','type':'Counter64','value':'179'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanRxPkt','type':'Counter64','value':'939'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanRxDropPkt','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanTxErrPkt','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanTxPkt','type':'Counter64','value':'179'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANVapWlanTxDropPkt','type':'Counter64','value':'0'},
        
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPMac','type':'STRING','value':'68:92:34:c:68:80'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfIndex','type':'INTEGER','value':'5'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfDescr','type':'STRING','value':'eth0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfType','type':'INTEGER','value':'6'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfMtu','type':'INTEGER','value':'1500'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfSpeed','type':'STRING','value':'100'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfPhysAddress','type':'STRING','value':'68:92:34:0C:68:83'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfAdminStatus','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfOperStatus','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfInOctets','type':'Counter32','value':'52257722'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfInUcastPkts','type':'Counter32','value':'496995'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfInNUcastPkts','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfInDiscards','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfInErrors','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfInUnknownProtos','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfOutOctets','type':'Counter32','value':'56312279'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfOutUcastPkts','type':'Counter32','value':'502136'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfOutNUcastPkts','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfOutDiscards','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfOutErrors','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfName','type':'STRING','value':'eth0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANAPIfNameDefined','type':'STRING','value':'0'},
                
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaMacAddr','type':'STRING','value':'14:cf:92:e:d7:fb'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaAPMacAddr','type':'STRING','value':'c4:10:8a:20:df:40'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaBSSID','type':'STRING','value':'c4:10:8a:20:df:4c'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaSSID','type':'STRING','value':'wlanwlan'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaUser','type':'STRING','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRadioType','type':'INTEGER','value':'4'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaChannel','type':'Gauge32','value':'149'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaIPAddr','type':'IpAddress','value':'192.168.0.200'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaAvgRSSI','type':'INTEGER','value':'54'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRxPkts','type':'Counter32','value':'2339'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRxBytes','type':'Counter64','value':'148628'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaTxPkts','type':'Counter32','value':'1600'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaTxBytes','type':'Counter64','value':'202607'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRetries','type':'Counter32','value':'3'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaAssocTime','type':'Timeticks','value':'317800'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRxError','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaTxSuccess','type':'Counter32','value':'1597'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANSta11bgReassoc','type':'Counter32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaAssocTimestamp','type':'STRING','value':'"Fri Aug 16 07:27:52 2013"'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRetryBytes','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaSNR','type':'INTEGER','value':'54'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaRxDrop','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaTxDrop','type':'Counter32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaTxError','type':'Counter32','value':'3'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaVlanID','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaAuthMode','type':'STRING','value':'OPEN'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-WLAN-MIB','oid':'ruckusZDWLANStaSignalStrength','type':'INTEGER','value':'-41'},
        ]
    for mib_node in mib_list:
        if zd_version not in mib_node['zd_version']:
            mib_list.remove(mib_node)   

    return mib_list
          
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

    zd_version_list = ['9.7']
    snmp_version_list = [2,3]
    for zd_version in zd_version_list:
        mib_list = get_mib_list(zd_version)
        for snmp_version in snmp_version_list:
            tcfg = define_test_parameters(tbcfg,snmp_version,target_sta,target_sta_radio)
            ts_name = '%s WLAN INFO SNMP V%s'%(zd_version,snmp_version)
            ts = testsuite.get_testsuite(ts_name, 'WLAN INFO SNMP V%s'%snmp_version, combotest=True)
            test_cfgs = define_test_cfg(tcfg,snmp_version,mib_list)

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