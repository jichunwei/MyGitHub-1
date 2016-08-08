
import sys
import time
from copy import deepcopy
from random import randint
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(cfg):
 
    test_cfgs = [] 
    radio_mode = cfg['radio_mode']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
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
   #**************************(1) 24 servers add/modify/delete ***********************************************************
    round = 0
    step = 0
    round += 1
    tc_common_name = "radsec works with 24 TLSRadius servers configured"

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Create 24 Radius authentication servers enable TLS' % (tc_common_name, round, step)
    test_cfgs.append(({'server_cfg_list':cfg['tlsradius_auth_cfg_list']}, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s Create wlan with mac auth' % (tc_common_name, round, step)
    test_cfgs.append(({'wlan_conf':cfg['stdmac_wlan_cfg']}, test_name, common_name, 2, False))

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
                       'wlan_cfg': cfg['stdmac_wlan_cfg'],
                       'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Remove aaa server: delete all 24 TLSradius servers' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
            
            
    #**************************(2) dual stack failover  ***********************************************************
    tc_common_name = "radsec works with backup server"    
    round += 1
    step = 0
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Create a Radius auth server with TLS and backup enabled:first invalid, second ipv6.' % (tc_common_name, round, step)
    test_cfgs.append(({'server_cfg_list':[cfg['dual_ras_tls_cfg']]}, test_name, common_name, 1, False))  

    wlan_cfg = deepcopy(cfg['stdmac_wlan_cfg'])
    wlan_cfg.update({'auth_server':cfg['dual_ras_tls_cfg']['server_name']})  
        
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s Create wlan with mac auth' % (tc_common_name, round, step)
    test_cfgs.append(({'wlan_conf':wlan_cfg}, test_name, common_name, 2, False))        
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))    
            
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s Verify client information Authorized status in ZD' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1','ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,'status': 'Authorized'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    step += 1
    common_name = '[%s]%s.%s Delete all aaa  servers' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    return test_cfgs
   
def gen_random_int():
    return randint(1,10000)
        
def define_test_parameters(tbcfg):
    server_ip_addr_err = "2020:db8:1::222"
    server_ip_addr_ipv6 = "2020:db8:1::232" #radius_ipv6_ipaddr

    ras_namebasic = 'TLSRadiussec' 
    
    ras_tls_cfg = {'type': 'radius-auth',
               'server_name' : ras_namebasic,
               'server_addr': server_ip_addr_ipv6,
               'server_port' : '2083',
               'radius_encryption':True,
               'radius_auth_method': 'pap',
                    }     
    tlsradius_auth_cfg_list=[ras_tls_cfg]
    for num in range(1,24):
        server_name = ras_namebasic + '_' + str(num)
        new_ras_tls_cfg = deepcopy(ras_tls_cfg)
        new_ras_tls_cfg.update({'server_name':server_name,
                                'server_addr':'2020:db8:100::%s'%num})
        tlsradius_auth_cfg_list.append(new_ras_tls_cfg)
    
    stdmac_wlan_name = 'TLSradius-stdmac-%s' % (time.strftime("%H%M%S"),)    
    stdmac_wlan_cfg = {"name" : stdmac_wlan_name,
                    "ssid" : stdmac_wlan_name,
                    "auth" : "mac",
                    "encryption" : "none",
                    'auth_server':ras_namebasic,
                    }      
    
    dual_ras_tls_cfg = {'type': 'radius-auth',
                        'server_name' : ras_namebasic,
                        'radius_encryption':True,
                        'backup':True,
                        'server_addr': server_ip_addr_ipv6,
                        'server_port' : '2083',
                        'backup_server_addr': server_ip_addr_err,
                        'backup_server_port' : '2083',
                       }
    
    dcfg = {'tlsradius_auth_cfg_list':tlsradius_auth_cfg_list,
            'stdmac_wlan_cfg':stdmac_wlan_cfg,
            'dual_ras_tls_cfg':dual_ras_tls_cfg,
            }
    
    return dcfg 
            
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ap_sym_dict = tbcfg['ap_sym_dict'] 
    sta_ip_list = tbcfg['sta_ip_list'] 
    
#    if ts_cfg["interactive_mode"]:
#        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
#    else:
#        target_sta = sta_ip_list[ts_cfg["station"][0]]
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ") 
    target_sta_radio = testsuite.get_target_sta_radio()    
    active_ap = active_ap_list[0] 
    
#    ap_tag_list = []
#    for ap_tag in ap_sym_dict:
#        ap_tag_list.append(ap_tag)
    
    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
#            'ap_tag_list':ap_tag_list,
            }
    dcfg = define_test_parameters(tbcfg)
    tcfg.update(dcfg)
    
    test_cfgs = define_test_cfg(tcfg)
    ts_name = 'Radius over TLS works with IPV6'
    ts = testsuite.get_testsuite(ts_name, 'Radius over TLS works with IPV6', combotest=True)
    
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