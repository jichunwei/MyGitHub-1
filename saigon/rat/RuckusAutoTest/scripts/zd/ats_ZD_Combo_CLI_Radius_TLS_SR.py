

import sys
import time
import random
from random import randint
import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
 
    test_cfgs = [] 
    step = 0
    round = 0
    round += 1

    test_cfgs = [] 
    radio_mode = cfg['radio_mode']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs on active ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
   
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove all aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
     
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create Radius auth server enable TLS with PAP.'
    test_cfgs.append(({'server_cfg_list':[cfg['ras_tls_cfg']]}, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create Radius accounting server enable TLS with PAP.'
    test_cfgs.append(({'server_cfg_list':[cfg['rastls_acct_cfg']]}, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    #**************************(1)EAP WPA2 wlan***********************************************************
    
    tc_common_name = "Modify AAA type and TLS option"

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers' 
    step += 1
    common_name = '[%s]%s.%s modified AAA type to active directory' % (tc_common_name, round, step)
    test_cfgs.append(({'server_cfg_list':[cfg['ad_cfg']]}, test_name, common_name, 1, False))
       
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Check TLS encryption configurability after modified AAA type to radius TLS enable' % (tc_common_name, round, step)
    test_cfgs.append(({'server_cfg_list':[cfg['ras_tls_cfg']]}, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s create wlan: eap_tls_wpa2' % (tc_common_name, round, step)
    test_cfgs.append(({'wlan_conf':cfg['eap_wlan_cfg']}, test_name, common_name, 2, False))
    

    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['eap_wlan_cfg']}, test_name, common_name, 2, False))
    
            
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','username':cfg['username'],'ap_tag': ap_tag,
                       'wlan_cfg': cfg['eap_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Check TLS encryption configurability after modified Radius encryption TLS disable' % (tc_common_name, round, step)
    test_cfgs.append(({'server_cfg_list':[cfg['ras_cfg']]}, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Check TLS encryption configurability after modified Radius encryption TLS enable' % (tc_common_name, round, step)
    test_cfgs.append(({'server_cfg_list':[cfg['ras_tls_cfg']]}, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['eap_wlan_cfg']}, test_name, common_name, 2, False))
            
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','username':cfg['username'],'wlan_cfg': cfg['eap_wlan_cfg'],
                       'status': 'Authorized','ap_tag': ap_tag,}, test_name, common_name, 2, False))
  
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
  
    #*************************(2)authentication and accounting with SR ; MAC wlan*********************************************************************
    tc_common_name = "Verify TLSRadius authentication with SR failover"

    step = 0
    round += 1

    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s Create wlan :mac' % (tc_common_name, round, step)
    test_cfgs.append(({'wlan_conf':cfg['stdmac_wlan_cfg']}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Reset_Radius_Statistics'
    step += 1
    common_name = '[%s]%s.%sReset Radius statistics by server name before login' %  (tc_common_name, round, step)
    test_cfgs.append(({'server_conf':cfg['rastls_acct_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['stdmac_wlan_cfg']}, test_name, common_name, 2, False))
    
            
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s Verify client information Authorized status in ZD' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','ap_tag': ap_tag,#'username':'should be station mac',# Do not check user here!!! 
                       'wlan_cfg': cfg['stdmac_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Radius_Statistics'
    step += 1
    common_name = '[%s]%s.%sVerify Radius statistics by server name after login' %  (tc_common_name, round, step)
    test_cfgs.append(({'server_conf':cfg['rastls_acct_cfg']}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SR_Failover'
    step += 1
    common_name = '[%s]%s.%s Failover the active ZD' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['stdmac_wlan_cfg']}, test_name, common_name, 2, False))
    
            
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s Verify client information Authorized status in ZD' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','ap_tag': ap_tag,
                       'wlan_cfg': cfg['stdmac_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    #****************************************clean up**************************************************
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd1 before test'
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd2 before test'
    test_cfgs.append(({'target_zd':'zd2'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD'
    common_name = 'Make all aps connect init active zd'
    test_cfgs.append(({'ap_num':2,'from_zd':'zd2','to_zd':'zd1'}, test_name, common_name, 0, True))
    
#    for tag in cfg['ap_tag_list']:
#        test_name = 'CB_ZD_CLI_Wait_AP_Connect'
#        common_name = 'Make sure %s connect init active zd'%tag
#        test_cfgs.append(({'zd_tag':'zdcli1','ap_tag':tag}, test_name, common_name, 0, True))
    test_name = 'CB_ZD_CLI_Wait_AP_Connect'
    #@author: Tan, @bug: zf-14017
    common_name = 'Make sure %s connect init active zd' %cfg['active_ap']
    test_cfgs.append(({'zd_tag':'zdcli1','ap_tag':cfg['active_ap']}, test_name, common_name, 0, True))
    return test_cfgs

def gen_random_int():
    return randint(1,10000)

def define_test_parameters(tbcfg):
    server_ip_addr  = '192.168.0.232'#testsuite.getTestbedServerIp(tbcfg)
    ras_name = 'TLSRadiussec-%s' % (time.strftime("%H%M%S"),)
    ras_acct_name = 'TLSRadiussec-acct-%s' % (time.strftime("%H%M%S"),)
    
    ras_cfg = {'type': 'radius-auth',
               'server_name' : ras_name,
               'server_addr': server_ip_addr,
               'radius_auth_secret': '1234567890',
               'server_port': '1812',
               'radius_encryption':False,
               'radius_auth_method': 'pap',
               }
    
    ras_tls_cfg = {'type': 'radius-auth',
               'server_name' : ras_name,
               'server_addr': server_ip_addr,
               'server_port' : '2083',
               'radius_encryption':True,
               'radius_auth_method': 'pap',
                    }
    rastls_acct_cfg = {'type': 'radius-acct',
               'server_name' : ras_acct_name,
               'server_addr': server_ip_addr,
               'server_port' : '2083',
               'radius_encryption':True,
               'Access Requests':1,
                    }                           
    
    rand_num = gen_random_int()

    eap_wlan_name = 'eap_tls_wpa2'+str(rand_num)
    stdmac_wlan_name = 'stdmac-TLS-std'+str(rand_num)
    eap_username ='ras.eap.user'
    eap_wlan_cfg={"name":eap_wlan_name,
                  "ssid":eap_wlan_name,
                  "auth" : "EAP",
                  'wpa_ver':"WPA2",
                  "encryption" : "AES",
                  'auth_server':ras_name,
                  'acc_server':ras_acct_name,
                  'username':eap_username,
                  'password':eap_username,
                  'sta_wpa_ver':'WPA2',
                  'sta_encryption':'AES',
                  'sta_auth':'EAP',
                  }
    
    stdmac_wlan_cfg = {"name" : stdmac_wlan_name,
                    "ssid" : stdmac_wlan_name,
                    "auth" : "mac",
                    "encryption" : "none",
                    'auth_server':ras_name,
                    'acc_server':ras_acct_name,
                    }
    
    ad_servername = ras_name
    ad_cfg={
               'server_name':ad_servername,
               'type':'ad',
               'server_addr':'192.168.0.250',
               'server_port':'490',
               }
        

    dcfg = { 'eap_wlan_cfg':eap_wlan_cfg,
            'stdmac_wlan_cfg':stdmac_wlan_cfg,
            'ad_cfg':ad_cfg,
            'ras_cfg':ras_cfg,
            'rastls_acct_cfg':rastls_acct_cfg,
            'ras_tls_cfg':ras_tls_cfg,
            'username':eap_username,
            'password':eap_username,
            }
    return dcfg

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed(**kwargs) #server2 ? 
    tbcfg = testsuite.getTestbedConfig(tb)

    sta_ip_list = tbcfg['sta_ip_list'] 
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
#    if ts_cfg["interactive_mode"]:
#        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
#    else:
#        target_sta = sta_ip_list[ts_cfg["station"][0]]
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ") 
    target_sta_radio = testsuite.get_target_sta_radio()    
    active_ap = active_ap_list[0] 
    
#    ap_tag_list = []
#    for tag in ap_sym_dict:
#        tag_list.append(tag)
    
    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            #'ap_tag_list':ap_tag_list
            }
    dcfg = define_test_parameters(tbcfg)
    tcfg.update(dcfg)
    
    test_cfgs = define_test_cfg(tcfg)
    ts_name = 'Radius over TLS works with SR'
    ts = testsuite.get_testsuite(ts_name, 'Radius over TLS works with SR', combotest=True)
    
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