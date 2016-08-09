#miss 27 cases
#now 59 cases in total

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg,snmp_version,mib_list):
    test_cfgs = []

    snmp_cfg = tcfg['snmp_cfg']
    snmp_agent_cfg = tcfg['set_snmp_agent_cfg']
    snmp_cfg.update(snmp_agent_cfg)
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V%s'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, 
                      test_name, common_name, 0, False))

    for item in mib_list:       
        test_case_name = item['oid'].split('.')[0]
        access_type = item['access_type']
        mib_nodes = []
        mib_nodes.append(item)
        if item.get('default_value') and item['default_value']:
            flag = 1
        else:
            flag = 0
        if access_type == 'rw':
            ### flag:whether set to default value or not
            if item.get('default_value') and item['default_value']:
                flag = 1
            else:
                flag = 0
            test_cfgs.extend(test_process_RW(test_case_name,snmp_cfg,mib_nodes,flag))
        elif access_type == 'ro':
            test_cfgs.extend(test_process_RO(test_case_name,snmp_cfg,mib_nodes))
        elif access_type == 'wo':
            test_cfgs.extend(test_process_WO(test_case_name,snmp_cfg,mib_nodes))

    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V%s after test'%snmp_version
    test_cfgs.append(({'snmp_agent_cfg': {'version': snmp_version, 'enabled': False}}, 
                      test_name, common_name, 0, True))  
    
    return test_cfgs
    
def test_process_RO(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []
    
###get
    
    test_name = 'CB_SNMP_Get_Values'
    common_name = '[%s]Get mib values'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes},
                      test_name, common_name, 1, False))
###check

    test_name = 'CB_Verify_SNMP_Values'
    common_name = '[%s]Verify mib values'%test_case_name
    tcs_cfgs.append(({'mib_nodes':mib_nodes}, 
                      test_name, common_name, 2, False))

###set(negative test)

    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values should fail.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': True}, 
                      test_name, common_name, 2, False))

    return tcs_cfgs
                          
def test_process_RW(test_case_name,snmp_cfg,mib_nodes,flag):

    tcs_cfgs = []

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 1, False))
                      
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
    #temp = {}
    temp = deepcopy(mib_nodes[0])    
    for value_type in type_dict.keys():
        if not value_type == temp['type']:
            temp['type'] = value_type
            test_name = 'CB_SNMP_Set_Values'
            common_name = '[%s]Set mib values with invalid type <%s> should fail.'%(test_case_name,value_type)
            tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp],'negative': True}, test_name, common_name, 2, False))
###set invalid value
    #temp2 = {}
    temp2 = deepcopy(mib_nodes[0])       

    invalid_value_list = temp2['invalid_value_list']   
    for invalid_value in invalid_value_list:
        temp2['value'] = invalid_value
        test_name = 'CB_SNMP_Set_Values'
        common_name = '[%s]Set mib values with invalid value <%s> should fail.'%(test_case_name,invalid_value)
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp2],'negative': True}, 
                      test_name, common_name, 2, False))

    if flag:
        temp3 = deepcopy(mib_nodes[0])
        temp3['value'] = temp3['default_value']
        temp3.pop('default_value') 
        test_name = 'CB_SNMP_Set_Values'
        common_name = '[%s]Set to default value.'%test_case_name
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp3],'negative': False}, 
                      test_name, common_name, 2, True))                          
    return tcs_cfgs

def test_process_WO(test_case_name,snmp_cfg,mib_nodes):

    tcs_cfgs = []

###set

    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 1, False))

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

    temp = deepcopy(mib_nodes[0])    
    for value_type in type_dict.keys():
        if not value_type == temp['type']:
            temp['type'] = value_type
            test_name = 'CB_SNMP_Set_Values'
            common_name = '[%s]Set mib values with invalid type <%s> should fail.'%(test_case_name,value_type)
            tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp],'negative': True}, test_name, common_name, 2, False))
###set invalid value

    temp2 = deepcopy(mib_nodes[0])       

    invalid_value_list = temp2['invalid_value_list']   
    for invalid_value in invalid_value_list:
        temp2['value'] = invalid_value
        test_name = 'CB_SNMP_Set_Values'
        common_name = '[%s]Set mib values with invalid value <%s> should fail.'%(test_case_name,invalid_value)
        tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':[temp2],'negative': True}, 
                      test_name, common_name, 2, False))

###set to default value
    test_name = 'CB_SNMP_Set_Values'
    common_name = '[%s]Set mib values.'%test_case_name
    tcs_cfgs.append(({'snmp_cfg':snmp_cfg,'mib_nodes':mib_nodes,'negative': False}, 
                      test_name, common_name, 2, True))
                      
    return tcs_cfgs
    
def define_test_parameters(tbcfg,snmp_version):
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
    
    if snmp_version ==2:
    
        tcfg = {'snmp_cfg': snmp_cfg,
                'set_snmp_agent_cfg': set_snmp_agent_cfg_v2,
                }
    else:
        tcfg = {'snmp_cfg': snmp_cfg,
                'set_snmp_agent_cfg': set_snmp_agent_cfg_v3,
                }        
    
    return tcfg
def get_mib_list(zd_version):
    mib_list = [
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIPAddr.0','type':'IpAddress','value':'1.1.1.1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemMaxSta.0','type':'Gauge32','value':'1'},
## ZF-4507:be careful with the following two items,write-only        
        {'zd_version':['9.7'],'access_type':'wo','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemSystemAdminName.0','type':'STRING',
         'value':'admin','invalid_value_list':['123xyz','~!@#$%','abcdefghijklmnopqrstuvwxyzabcdefg']},  
        {'zd_version':['9.7'],'access_type':'wo','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemAdminPassword.0','type':'STRING','value':'admin',
         'value':'admin','invalid_value_list':['adm','adminadminadminadminadminadminadm']},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatus.0','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemPeerConnectedStatus.0','type':'INTEGER','value':'1'},
        
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemNEId.0','type':'STRING','value':'1','default_value':'0',
         'invalid_value_list':['12345678901234567890123456789012345678901234567890123456789012345']},  
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemManufacturer.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemSoftwareName.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemMemorySize.0','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemFlashFreeSize.0','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemMgmtVlanID.0','type':'Gauge32','value':'1'},
##CPUModel is not defined in mib file    
        #@ZJ 20140924  ZF-10165   
        #{'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemCPUModel.0','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemCPUModel.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemtCPUSpeed.0','type':'Gauge32','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemtFlashModel.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemtMemModel.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStartTime.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemCurrentTime.0','type':'STRING','value':'1'},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemAPFirmwareServer.0','type':'IpAddress',
         'value':'1.1.1.1','default_value':'0.0.0.0','invalid_value_list':['300.1.1.1','1.1.1.',]},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemAPConfigServer.0','type':'IpAddress',
         'value':'1.1.1.1','default_value':'0.0.0.0','invalid_value_list':['300.1.1.1','1.1.1.',]},

## ZF-4675: be careful with the following 3 items,makes snmp process crash
        #@attention: chen.tao Since 2013-11-27, to fix bug ZF-6330
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIDSAllowedESSID.0','type':'STRING',
         'value':'ruckus-wireless','default_value':'00',
        'invalid_value_list':['123456789012345678901234567890123']},
#attention@author:Chico,@bug:ZF-9078,@summary: add option to select version, mib_list needs updating when new version of SNMP mib changed. Check example of ruckusZDSystemIDSAllowBSSID.    
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIDSAllowBSSID.0','type':'STRING',
         'value':'1','default_value':'00',
        'invalid_value_list':['123456789012345678901234567890123']},
        {'zd_version':['9.8'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIDSAllowBSSID.0','type':'STRING',
         'value':'01','default_value':'00',
        'invalid_value_list':['123456789012345678901234567890123']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIDSAllowOUI.0','type':'STRING',
         'value':'1','default_value':'00',
        'invalid_value_list':['123456789012345678901234567890123']},
        {'zd_version':['9.8'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemIDSAllowOUI.0','type':'STRING',
         'value':'01','default_value':'00',
        'invalid_value_list':['123456789012345678901234567890123']},
#attention@author:Chico,@bug:ZF-9078,@summary: add option to select version, mib_list needs updating when new version of SNMP mib changed. Check example of ruckusZDSystemIDSAllowBSSID.
        #@attention: chen.tao Since 2013-11-27, to fix bug ZF-6330
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemBandwidthUtilValve.0','type':'Gauge32',
         'value':'1','default_value':'90','invalid_value_list':['0','101']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemDropPacketRateValve.0','type':'Gauge32',
         'value':'1','default_value':'90','invalid_value_list':['0','101']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemCPUUtilValve.0','type':'Gauge32',
         'value':'1','default_value':'0','invalid_value_list':['0','101']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemMemUtilValve.0','type':'Gauge32',
         'value':'1','default_value':'0','invalid_value_list':['0','101']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemOnlineStaValve.0','type':'Gauge32',
         'value':'1','default_value':'0','invalid_value_list':[]},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemACLocationLongitude.0','type':'STRING',
         'value':'1','default_value':'0','invalid_value_list':['123456789012345678901234567890123']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemACLocationLatitude.0','type':'STRING',
         'value':'1','default_value':'0','invalid_value_list':['123456789012345678901234567890123']},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemDHCPServer.0','type':'INTEGER','value':'1'},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDAPCPUvalve.0','type':'Gauge32',
         'value':'1','default_value':'0','invalid_value_list':['101']},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDAPMemoryvalve.0','type':'Gauge32',
         'value':'1','default_value':'0','invalid_value_list':['101']},
##ZF-4507
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDHeartBeatStatus.0','type':'INTEGER',
         'value':'1','default_value':'0','invalid_value_list':[]},
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDHeartBeatPeriod.0','type':'Gauge32',
         'value':'1','default_value':'5','invalid_value_list':['0','10001']},
         
        {'zd_version':['9.7'],'access_type':'rw','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStpStatus.0','type':'INTEGER',
         'value':'1','default_value':'2','invalid_value_list':['3']}, 
                  
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsNumAP.0','type':'Gauge32','value':'2'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsNumSta.0','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsNumRogue.0','type':'Gauge32','value':'205'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsNumRogueKnown.0','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalRxPkts.0','type':'Counter64','value':'1705334'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalRxBytes.0','type':'Counter64','value':'392828596'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalRxMulticast.0','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxPkts.0','type':'Counter64','value':'124800'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxBytes.0','type':'Counter64','value':'27035149'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxMulticast.0','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxFail.0','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxRetry.0','type':'Counter64','value':'11378'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsCPUUtil.0','type':'Gauge32','value':'12'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsMemoryUtil.0','type':'Gauge32','value':'44'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsNumRegisteredAP.0','type':'Gauge32','value':'2'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalAssocFail.0','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalRxErrFrm.0','type':'Counter64','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxDroppedPkt.0','type':'Counter64','value':'11378'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxErrFrm.0','type':'Counter64','value':'11378'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsWLANTotalTxDroppedFrm.0','type':'Counter64','value':'11378'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsLanTxRate.0','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsLanRxRate.0','type':'Gauge32','value':'0'},
        {'zd_version':['9.7'],'access_type':'ro','model':'RUCKUS-ZD-SYSTEM-MIB','oid':'ruckusZDSystemStatsAllNumSta.0','type':'Gauge32','value':'0'},
        
        ]
    change_mib_list = []
    copy_mib_list = deepcopy(mib_list)
    for mib_node in copy_mib_list:
        if zd_version in mib_node['zd_version']:
            change_mib_list.append(mib_node)
            mib_list.remove(mib_node)
    
    if not mib_list:
        return change_mib_list
    
    if change_mib_list:
        copy_mib_list = deepcopy(mib_list)
        for change_mib_node in change_mib_list:
            for mib_node in copy_mib_list:
                    if change_mib_node['oid'] == mib_node['oid']:
                        mib_list.remove(mib_node)
            mib_list.append(change_mib_node)
    return mib_list

def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

#attention@author:Chico,@bug:ZF-9078,@summary: add option to select version, mib_list needs updating when new version of SNMP mib changed. Check example of ruckusZDSystemIDSAllowBSSID.
    prompt = '''
    Please specific which version index of ZD SNMP:
        1) 9.7
        2) 9.8
    '''
    zd_version_index = int(raw_input(prompt))
    if zd_version_index not in range (1,3):
        zd_version_index = 1
        
    zd_version_cfg = {1:'9.7',
                      2:'9.8'}
    zd_version = zd_version_cfg[zd_version_index]
 
    snmp_version_list = [2,3]
    mib_list = get_mib_list(zd_version)
    for snmp_version in snmp_version_list:    
        tcfg = define_test_parameters(tbcfg,snmp_version)
        ts_name = '%s System Information Test - SNMP V%s'%(zd_version,snmp_version)
        ts = testsuite.get_testsuite(ts_name, 'System Information Test - SNMP V%s'%snmp_version, combotest=True)
        test_cfgs = define_test_cfg(tcfg,snmp_version,mib_list)

        test_order = 1
        test_added = 0
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1

            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
#attention@author:Chico,@bug:ZF-9078,@summary: add option to select version, mib_list needs updating when new version of SNMP mib changed. Check example of ruckusZDSystemIDSAllowBSSID.

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    
