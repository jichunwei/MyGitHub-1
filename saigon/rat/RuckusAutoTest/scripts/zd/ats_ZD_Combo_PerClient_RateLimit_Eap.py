"""
Verify per client rate limit configuration integrated with EAP wlan rate limiting option

    Verify rate limit configuration in AP shell and wlan, 
    - Send zing traffic, and rate of 50% is between the range [>min_rate, <=allowed_rate]
       min_rate=default is 0
       allowed_rate= rate_limit_mbps * (1.0 + margin_of_error), margin_of_error is 0.2 by default
    - Rate limit range is from 0.10mbps to 20.00mbps step is 0.25mbps excpet value 0.10mbps-0.25mpbs.
    - Coverage: uplink and downlink rate limit is same, uplink     
    
    expect result: All steps should result properly.
    
    
Created on 2012-08-30
@author: west.li
"""

import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

check_wlan_timeout = 5


def define_test_cfg(cfg):
    test_cfgs = []
    
    #initiate parameters
    ras_cfg = cfg['ras_cfg']
    target_ip_addr = cfg['target_ping_ip_addr']
    radio_mode = cfg['radio_mode']
    rate_cfg_list = _def_rate_limit_cfg_list()
    sta_tag = 'sta%s' % radio_mode
    ap_tag = cfg['active_ap_list'][0]
    wlan_cfg=cfg['wlan_cfg']
    auth=cfg['auth']
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    #Station    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    #create ap and bind ap with the specified wlan
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % (ap_tag)
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create WLAN group: %s" % (cfg['wg_cfg']['name']) 
    test_cfgs.append(({'wgs_cfg': cfg['wg_cfg'],'add_wlan':False}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Single_Wlan'
    common_name = "Create WLAN : %s" % (wlan_cfg['ssid']) 
    test_cfgs.append(({'wlan_cfg': wlan_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_Wlan_On_Wlan_Group'
    common_name = "assign WLAN %s to group: %s" % (wlan_cfg['ssid'],cfg['wg_cfg']['name']) 
    test_cfgs.append(({'wlan_list':[wlan_cfg['ssid']],'wgs_cfg': cfg['wg_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the WLAN group to radio '%s' of AP: %s" % (radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': cfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, False))  
    if auth.lower()!='eap':
        test_name = 'CB_ZD_Rename_File_On_Linux_Server'
        common_name = "backup file users before test" 
        test_cfgs.append(({'src_name':'users','dst_name':'users.bak.west','folder':'/etc/raddb'}, test_name, common_name, 0, False))
        
    for rate_cfg in rate_cfg_list:
        test_case_name=rate_cfg['case_name']%auth
        edit_wlan_cfg=_define_wlan_cfg(rate_cfg['uplink_rate_limit'],rate_cfg['downlink_rate_limit'],auth,ras_cfg['server_name'],
                                       rate_cfg['tunnel'], rate_cfg['vlan_id'],rate_cfg['user'],rate_cfg['user'],rate_cfg['filename'])
          
        test_name = 'CB_ZD_Edit_Wlan'
        common_name = "%sedit WLAN : %s" % (test_case_name,edit_wlan_cfg['ssid']) 
        test_cfgs.append(({'wlan_ssid':edit_wlan_cfg['ssid'],'new_wlan_cfg': edit_wlan_cfg}, test_name, common_name, 1, False))
        
        if auth.lower()!='eap':
            test_name = 'CB_ZD_Rename_File_On_Linux_Server'
            common_name = "%slet file %s become file users" %(test_case_name,edit_wlan_cfg['filename'])
            test_cfgs.append(({'src_name':edit_wlan_cfg['filename'],'dst_name':'users','folder':'/etc/raddb'}, test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_Restart_Service'
            common_name = "%srestart radius server let ratelimt take effect" %test_case_name
            test_cfgs.append(({'service':'radiusd'}, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_Associate_Station_1'
        common_name = "%sassociate sta with wlan %s" % (test_case_name,edit_wlan_cfg['ssid']) 
        test_cfgs.append(({'wlan_cfg': edit_wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, False))
         
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet wifi address of the station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
           
        test_name = 'CB_ZD_Verify_AP_PerClient_RateLimit'
        common_name = '%sVerify per client rate limiting in AP' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag,
                           'ssid': edit_wlan_cfg['ssid'],
                           'sta_tag': sta_tag,
                           'client_ul_rate':rate_cfg['uplink_str_in_ap'],
                           'client_dl_rate':rate_cfg['downlink_str_in_ap'],
                           },
                           test_name, common_name, 2, False))

        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client without rate limit can ping a target IP' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': '192.168.0.252'}, test_name, common_name, 2, False))
            
        if rate_cfg['user']!='ras.nolimit':  
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '%sSend downlink zing traffic and verify traffic rate' % (test_case_name)
            test_cfgs.append(({'rate_limit': rate_cfg['expected_downlink_max_rate'],
                               'margin_of_error': rate_cfg['margin_of_error'],
                               'link_type': 'down',
                               'sta_tag': sta_tag}, test_name, common_name, 2, False))
            
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '%sSend uplink zing traffic and verify traffic rate' % (test_case_name)
            test_cfgs.append(({'rate_limit': rate_cfg['expected_uplink_max_rate'],
                               'margin_of_error': rate_cfg['margin_of_error'],
                               'link_type': 'up',
                               'sta_tag': sta_tag,
                               'ssid': edit_wlan_cfg['ssid']}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove all wlans from station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
        
        if auth.lower()!='eap':
            test_name = 'CB_ZD_Rename_File_On_Linux_Server'
            common_name = "%srestore file %s after case finished" %(test_case_name,edit_wlan_cfg['filename'])
            test_cfgs.append(({'src_name':'users','dst_name':edit_wlan_cfg['filename'],'folder':'/etc/raddb'}, test_name, common_name, 2, True))
            
            timeout=10#min
            test_name = 'CB_Scaling_Waiting'
            common_name = "%swait %d minute to let mac auth timeout" %(test_case_name,timeout)
            test_cfgs.append(({'timeout':timeout*60}, test_name, common_name, 2, True))
            
    if auth.lower()!='eap':
        test_name = 'CB_ZD_Rename_File_On_Linux_Server'
        common_name = "restore file users after test" 
        test_cfgs.append(({'src_name':'users.bak.west','dst_name':'users','folder':'/etc/raddb'}, test_name, common_name, 0, True))
        
        test_name = 'CB_ZD_Restart_Service'
        common_name = "restart radius server after restore file users" 
        test_cfgs.append(({'service':'radiusd'}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign default WLAN group to radio '%s' of AP: %s" % (radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': 'Default', 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_Wlan_Group'
    common_name = "remove wlan group %s" % (cfg['wg_cfg']['name'])
    test_params = {'wg_name': cfg['wg_cfg']['name'],}
    test_cfgs.append((test_params, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_Wlan'
    common_name = "remove wlan %s" % (edit_wlan_cfg['ssid'])
    test_params = {'wlan_name': edit_wlan_cfg['ssid'],}
    test_cfgs.append((test_params, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = 'remove Authentication Server from ZD'
    param_cfg = dict(auth_ser_name_list = [ras_cfg['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    return test_cfgs


def _def_rate_limit_cfg_list():
    '''
    uplink and downlink rate limit is between 0.10mbps - 20.00mbps.
    '''
    rate_cfg_list = []
    #for no limit case
    cfg={'user':'ras.nolimit',
         'uplink_rate_limit':'Disabled',
         'downlink_rate_limit':'Disabled',
         'uplink_str_in_ap':'n/a',
         'downlink_str_in_ap':'n/a',
         'margin_of_error':0.2,
         'vlan_id':'1',
         'tunnel':False,
         'case_name':'[%s-both wlan and radius no limit]',
         'filename':'users.nolimit'
         }
    rate_cfg_list.append(cfg)
    
    #for 250kbps/250kbps case
    cfg={'user':'ras.250kbps',
         'uplink_rate_limit':'Disabled',
         'downlink_rate_limit':'Disabled',
         'uplink_str_in_ap':'250kbps',
         'downlink_str_in_ap':'250kbps',
         'expected_uplink_max_rate':'0.25mbps',
         'expected_downlink_max_rate':'0.25mbps',
         'margin_of_error':0.2,
         'vlan_id':'1',
         'tunnel':False,
         'case_name':'[%s-wlan no limit,radius has ratelimit]',
         'filename':'users.250kbps'
         }
    rate_cfg_list.append(cfg)
    
    #for 526kbps/751kbps case
    cfg={'user':'ras.ul.526.dl.751kbps',
         'uplink_rate_limit':'Disabled',
         'downlink_rate_limit':'Disabled',
         'uplink_str_in_ap':'750kbps',
         'downlink_str_in_ap':'1000kbps',
         'expected_uplink_max_rate':'0.75mbps',
         'expected_downlink_max_rate':'1.00mbps',
         'margin_of_error':0.2,
         'vlan_id':'2',
         'tunnel':False,
         'case_name':'[%s-wlan vlan enable,radius has ratelimit]',
         'filename':'users.ul.526.dl.751kbps'
         }
    rate_cfg_list.append(cfg)

    #for ras.20mbps case
    cfg={'user':'ras.20mbps',
         'uplink_rate_limit':'Disabled',
         'downlink_rate_limit':'Disabled',
         'uplink_str_in_ap':'20000kbps',
         'downlink_str_in_ap':'20000kbps',
         'expected_uplink_max_rate':'20.00mbps',
         'expected_downlink_max_rate':'20.00mbps',
         'margin_of_error':0.2,
         'vlan_id':'1',
         'tunnel':True,
         'case_name':'[%s-wlan tunnel enable,radius has ratelimit]',
         'filename':'users.20mbps'
         }
    rate_cfg_list.append(cfg)

    #for ras.22mbps case
    cfg={'user':'ras.22mbps',
         'uplink_rate_limit':'Disabled',
         'downlink_rate_limit':'Disabled',
         'uplink_str_in_ap':'30000kbps',
         'downlink_str_in_ap':'30000kbps',
         'expected_uplink_max_rate':'20.00mbps',
         'expected_downlink_max_rate':'20.00mbps',
         'margin_of_error':0.2,
         'vlan_id':'2',
         'tunnel':True,
         'case_name':'[%s-wlan tunnel and vlan enable,radius has ratelimit]',
         'filename':'users.22mbps'
         }
    rate_cfg_list.append(cfg)
    
    #for ras.15000kbps case
    cfg={'user':'ras.ul.15m.dl.16mbps',
         'uplink_rate_limit':'10.00mbps',
         'downlink_rate_limit':'10.00mbps',
         'uplink_str_in_ap':'15000kbps',
         'downlink_str_in_ap':'16000kbps',
         'expected_uplink_max_rate':'15.00mbps',
         'expected_downlink_max_rate':'16.00mbps',
         'margin_of_error':0.2,
         'vlan_id':'',
         'tunnel':False,
         'case_name':'[%s-both wlan and radius has ratelimit]',
         'filename':'users.ul.15m.dl.16mbps'
         }
    rate_cfg_list.append(cfg)
    
    return rate_cfg_list    

def _define_wlan_cfg(uplink_rate_limit='Disabled', downlink_rate_limit='Disabled', auth='eap',auth_svr = '', do_tunnel=False, vlan_id='',username = "ras.eap.user", password = "ras.eap.user",filename=''):
    wlan_cfg = dict(ssid='eap-rate-limit', auth=auth, encryption="none")
    
    wlan_cfg['uplink_rate_limit'] = uplink_rate_limit
    wlan_cfg['downlink_rate_limit'] = downlink_rate_limit
    
    wlan_cfg['username'] = username
    wlan_cfg['password'] = password
    
    if auth_svr:
        wlan_cfg['auth_svr'] = auth_svr

    if do_tunnel:
        wlan_cfg['do_tunnel'] = do_tunnel
    
    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id #In 9.4 LCS version, default vlan_id is 1, but other versions have null default vlan_id
    if auth=='eap' or auth=='EAP':
        wlan_cfg['wpa_ver']         = 'WPA2'
        wlan_cfg['sta_wpa_ver']     = 'WPA2'
        wlan_cfg['sta_auth']        = 'EAP'
        wlan_cfg['encryption']      = 'AES'
        wlan_cfg['sta_encryption']  = 'AES'
    wlan_cfg['filename']  = filename
    return wlan_cfg


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

    target_sta_radio = 'na'
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        auth_idx = raw_input("Select wlan Auth Method: [1(eap)/2(mac)/3(maceap)]: ")
        if auth_idx=='1':
            auth='EAP'
        elif auth_idx=='2':
            auth='mac'
        elif auth_idx=='3':
            auth='maceap'
        else:
            print 'only 1 2 or 3 is acceptable!'
            return
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    server_ip_addr  = testsuite.getTestbedServerIp(tbcfg)

    target_ping_ip_addr = server_ip_addr

    
    ras_name = 'radius_for_eap'
    radius_auth_method = 'pap'
    wg_cfg = {
        'name': 'eap-ratelimit-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for eap per client rate limit test',
        'vlan_override': False,
        'wlan_member': {},
        }
    wlan_cfg=_define_wlan_cfg()
    tcfg = {'ras_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1812',
                    'server_name' : ras_name,
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': radius_auth_method,
                    },
            'wg_cfg':wg_cfg,
            'wlan_cfg':wlan_cfg,
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'auth':auth,
            }
    
    test_cfgs = define_test_cfg(tcfg)
    

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "PerClient Rate Limiting-%s" % auth


    ts = testsuite.get_testsuite(ts_name, "Verify PerClient rate limit" , combotest=True)

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
