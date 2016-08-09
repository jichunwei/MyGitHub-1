""" 
Created on 2014-06
@author: chen.tao@odc-ruckuswireless.com
"""

import sys
import random
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_wlan_cfg(): 

    key_string_wpa2 = utils.make_random_string(random.randint(8, 63), "hex")
    wlan_cfg = {
                'ssid': 'Application_Visibility_OPEN', 
                'type': 'standard', 
                'auth': 'PSK', 
                'wpa_ver': 'WPA2',
                'encryption': 'AES', 
                'key_index': '', 
                'key_string': key_string_wpa2,
                'sta_auth': 'PSK', 
                'sta_wpa_ver': 'WPA2', 
                'sta_encryption': 'AES', 
                'enable_application_visibility': True
                }
    return wlan_cfg

def define_test_cfg(cfg,enable_tunnel):
    test_cfgs = []

    target_ip_addr = '172.16.10.252' 
    target_addr_for_denial_policy = 'www.example.net'
    
    sta_tag = 'sta1'
    sta_radio_mode = 'ng'
    wlan_cfg = define_wlan_cfg()
    case_name_suffix = ''
    if enable_tunnel:
        wlan_cfg['do_tunnel'] = True
        case_name_suffix = '_with_tunnel'
    
    #@author: Tan ,@change: add two steps 
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD'
    test_cfgs.append(({'for_upgrade_test': False},test_name, common_name, 0, False))
          
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create Root AP'
    test_cfgs.append(({'active_ap':cfg['active_ap1'],
                       'ap_tag': 'AP_01'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create Mesh AP'
    test_cfgs.append(({'active_ap':cfg['active_ap2'],
                       'ap_tag': 'AP_02'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Setting up mesh ap AP_02'
    test_cfgs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_02',
                       'test_option': 'form_mesh_mesh_acl'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Application_Visibility_Init_Env'
    common_name = 'Try to delete all application visibility rules.'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, False))    
                       
#testcase 1

    test_case_name = '[user_app_mesh%s]'%case_name_suffix 

    user_app_rule_cfg = {'rule_description':'user_app_mesh',
                         'dest_ip':target_ip_addr,
                         'dest_port':'12345',
                         'netmask':'255.255.255.0',
                         'protocol':'udp'}

    test_name = 'CB_ZD_CLI_Add_User_Defined_App'
    common_name = '%s Add a user app.'% (test_case_name)
    test_params = {'user_app_cfg':[user_app_rule_cfg],
                     'negative': False,}
    test_cfgs.append((test_params,test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate WLAN on ZD'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                      }, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Get_BSSID'
    common_name = '%sGet BSSID for Mesh AP'% (test_case_name)
    test_cfgs.append(({'wlan_cfg':wlan_cfg,'ap_tag':'AP_02',
                       'ap_radio': '802.11g/n',
                      }, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID'
    common_name = '%sAssociate the station to the WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'wlan_ssid': wlan_cfg['ssid'],
                       'ap_tag': 'AP_02',
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': 'AP_02',
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify station pings to the server successfully'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Server_Start_Iperf'
    common_name = '%sStart iperf server on linux PC'% (test_case_name)
    test_cfgs.append(({'server_addr':'',
                       'test_udp': True,
                       'packet_len':'',
                       'bw':'',
                       'timeout':'',
                       'tos':'',
                       'multicast_srv':False,
                       'port':12345 }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Start_Iperf'
    common_name = '%sStart iperf client and send traffic to server'% (test_case_name)
    test_cfgs.append(({'sta_tag':sta_tag,
                       'server_addr':target_ip_addr,
                       'test_udp': True,
                       'packet_len':'',
                       'bw':'',
                       'timeout':60,
                       'tos':'',
                       'multicast_srv':False,
                       'port':12345 }, test_name, common_name, 2, False))
    
    test_name = 'CB_Server_Stop_Iperf'
    common_name = '%sStop iperf server on linux PC'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Stop_Iperf'
    common_name = '%sStop iperf client on station'% (test_case_name)
    test_cfgs.append(({'sta_tag':sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Application_Visibility_Info'
    common_name = '%sVerify application info in Monitor Clients page'% (test_case_name)
    test_cfgs.append(({'application_description':'user_app_mesh'}, test_name, common_name, 2, False)) 
                                  
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs from ZD'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Del_User_Defined_App'
    common_name = '%s Delete all user apps.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))   

#testcase 2

    test_case_name = '[port_mapping_open_mesh%s]'%case_name_suffix  

    port_mapping_rule_cfg = {'rule_description':'port_mapping_mesh','protocol':'udp','port':'54321'}

    test_name = 'CB_ZD_CLI_Add_Port_Mapping_Policy'
    common_name = '%s Add a port mapping rule.'% (test_case_name)
    test_params = {'port_mapping_cfg':[port_mapping_rule_cfg],}
    test_cfgs.append((test_params,test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate WLAN on ZD'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                      }, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Get_BSSID'
    common_name = '%sGet BSSID for Mesh AP'% (test_case_name)
    test_cfgs.append(({'wlan_cfg':wlan_cfg,'ap_tag':'AP_02',
                       'ap_radio': '802.11g/n',
                      }, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID'
    common_name = '%sAssociate the station to the WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'wlan_ssid': wlan_cfg['ssid'],
                       'ap_tag': 'AP_02',
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': 'AP_02',
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify station pings to the server successfully'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Server_Start_Iperf'
    common_name = '%sStart iperf server on linux PC'% (test_case_name)
    test_cfgs.append(({'server_addr':'',
                       'test_udp': True,
                       'packet_len':'',
                       'bw':'',
                       'timeout':'',
                       'tos':'',
                       'multicast_srv':False,
                       'port':54321 }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Start_Iperf'
    common_name = '%sStart iperf client and send traffic to server'% (test_case_name)
    test_cfgs.append(({'sta_tag':sta_tag,
                       'server_addr':target_ip_addr,
                       'test_udp': True,
                       'packet_len':'',
                       'bw':'',
                       'timeout':'',
                       'tos':60,
                       'multicast_srv':False,
                       'port':54321 }, test_name, common_name, 2, False))
    
    test_name = 'CB_Server_Stop_Iperf'
    common_name = '%sStop iperf server on linux PC'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Stop_Iperf'
    common_name = '%sStop iperf client on station'% (test_case_name)
    test_cfgs.append(({'sta_tag':sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Application_Visibility_Info'
    common_name = '%sVerify application info in Monitor Clients page'% (test_case_name)
    test_cfgs.append(({'application_description':'port_mapping_mesh',}, test_name, common_name, 2, False)) 
                                  
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs from ZD'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Del_Port_Mapping_Policy'
    common_name = '%s Delete all port mapping policies.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))
    
#testcase 3

    test_case_name = '[denial_policy_mesh%s]'%case_name_suffix 

    denial_policy_cfg = {'policy_description': 'test_app_denial_policy',
                         'policy_name': 'test_app_denial_policy',
                         'rules': [{'application': 'Port', 'rule_description': 80, 'rule_id': 1},
                                   {'application': 'HTTP hostname', 'rule_description': 'www.example.net', 'rule_id': 2}]}

    test_name = 'CB_ZD_CLI_Add_App_Denial_Policy'
    common_name = '%s Add a denial policy.'% (test_case_name)
    test_params = {'denial_policy_cfg':[denial_policy_cfg],}
    test_cfgs.append((test_params,test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate WLAN on ZD'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                      }, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Get_BSSID'
    common_name = '%sGet BSSID for Mesh AP'% (test_case_name)
    test_cfgs.append(({'wlan_cfg':wlan_cfg,'ap_tag':'AP_02',
                       'ap_radio': '802.11g/n',
                      }, test_name, common_name, 2, False))

    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID'
    common_name = '%sAssociate the station to the WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'wlan_ssid': wlan_cfg['ssid'],
                       'ap_tag': 'AP_02',
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': 'AP_02',
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sVerify station pinging to the server succeeds'%(test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag, 'dest_ip': target_addr_for_denial_policy,}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Connect_To_Server_Port'
    common_name = "%sVerify station connecting to server's port succeeds"%(test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag, 'server_ip': '172.16.10.252','dest_port':80}, test_name, common_name, 2, False))  
    
    #edit wlan to enable denial policy
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '%sEdit wlan, to select a denial policy' % test_case_name
    param_cfg = {'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': {'application_denial_policy':'test_app_denial_policy'}} 
    test_cfgs.append((param_cfg,test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = '%sVerify station pinging to the server fails'%(test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag, 'dest_ip': target_addr_for_denial_policy,}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Connect_To_Server_Port'
    common_name = "%sVerify station connecting to server's port fails"%(test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag, 'server_ip': '172.16.10.252','dest_port':80,'negative':True}, test_name, common_name, 2, False))    

                                  
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station'% (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs from ZD'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Del_App_Denial_Policy'
    common_name = '%s Delete all denial policies.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True)) 
#clean_up 
                    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect all active APs as Root'
    test_params = {'ap_list': ['AP_01', 'AP_02'],
                       'test_option': 'reconnect_as_root'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station for the next test'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_CLI_Application_Visibility_Init_Env'
    common_name = 'Try to delete all application visibility rules for next test.'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, True))   
    
    
    #@author: Tan @change: add step
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to disable mesh'
    test_cfgs.append(({},test_name, common_name, 0, False)) 
    return test_cfgs


def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_duplicated_common_name(test_cfgs):
    common_name_list = []
    duplicate_flag = False
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if common_name in common_name_list:
            duplicate_flag = False
            print '####################'
            print common_name
            print '####################'
        else:
            common_name_list.append(common_name)
    return duplicate_flag
  
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
        print '\nOnly the following AP models support application visibility:'
        print '  1.ZF-7762-AC,ZF-7762-S-AC'
        print '  2.ZF-7782,ZF-7782-s,ZF-7782-n,ZF-7782-e'
        print '  3.ZF-7982'
        print '  4.sc8800-s-ac,sc8800-s'
        print '  5.ZF-7055'
        print '  6.ZF-7352'
        print '  7.ZF-7372,ZF-7372-e'
        print '  8.ZF-7781-m,ZF-7781cm'
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        #target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    #active_ap = active_ap_list[0]
    if len(active_ap_list) < 2:
        raise Exception("Need two active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]  
    active_ap2 = active_ap_list[1]

    tcfg = {
            'target_station':'%s' % target_sta,
            'active_ap1':active_ap1,
            'active_ap2':active_ap2,
            'all_ap_mac_list': all_ap_mac_list,
            }

    tunnel_mode = raw_input("\n\
Do you want to enable tunnel to do test?\n\
  1. Yes\n\
  2. No\n\
Default selection is 2.Input your choice:")

    if tunnel_mode != '1':
        enable_tunnel = False
    else: enable_tunnel = True
            
    test_cfgs = define_test_cfg(tcfg,enable_tunnel)   

    check_max_length(test_cfgs)
    check_duplicated_common_name(test_cfgs)
    ts_suffix = ''
    if enable_tunnel: ts_suffix = ' - tunneled'
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Application_Visibility - Mesh%s"%ts_suffix

    ts = testsuite.get_testsuite(ts_name, "Application_Visibility - Mesh%s"%ts_suffix , combotest=True)

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
