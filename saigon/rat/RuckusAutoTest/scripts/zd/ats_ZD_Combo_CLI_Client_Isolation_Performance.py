"""
Performance test(3 tcs)
    maximum whitelist entries
    add whitelist profile and max whitelist profile
    64 ssid
    
Created on 2013-7-24
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Entry-1",
            "ssid" : "Rqa-auto-RAT-CI-Entry-1",
            "auth" : "open",
            "encryption" : "none",
            'isolation_per_ap' : True,
            'isolation_across_ap' : True,
            'white_list' : 'White-Entry-1',
            }

default_ip = {'switch' : '192.168.0.253',
              'server' : '192.168.0.252',
              }

def build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2, max_num):
    tcs = []

    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Remove all WLANs', 
                0, 
                False))

    tcs.append(({}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                'Remove all white lists', 
                0, 
                False))
  
    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': sta1_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 1', 
                   0, 
                   False))
    
    tc_name = '[%s MAC only]' % max_num
    wl_cfg_all = _generate_white_list(max_num, max_num)
    wl_lists = _genereate_wl_list(wl_cfg_all)
                        
    tcs.append(({'wl_cfg_all': wl_cfg_all}, 
                'CB_ZD_CLI_Edit_White_Lists_Batch', 
                '%sAdd white list' % tc_name, 
                1, 
                False))
    
    tcs.append(({'white_lists':wl_lists}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                '%sDelete white list' %tc_name, 
                2, 
                True))
    #------------------

    tc_name = '[%s MAC and IP]' % max_num
    wl_cfg_all = _generate_white_list(max_num, 0)
    wl_lists = _genereate_wl_list(wl_cfg_all)
                        
    tcs.append(({'wl_cfg_all': wl_cfg_all}, 
                'CB_ZD_CLI_Edit_White_Lists_Batch', 
                '%sAdd white list' % tc_name, 
                1, 
                False))
    
    tcs.append(({'white_lists':wl_lists}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                '%sDelete white list' %tc_name, 
                2, 
                True))
    #-------------------------
    middle_max = int(max_num/2)
    tc_name = '[%s ssid, %s MAC, %s MAC and IP]'%(max_num,middle_max,max_num-middle_max)
    wl_cfg_all = _generate_white_list(max_num, middle_max)
    wl_lists = _genereate_wl_list(wl_cfg_all)
    wlan_cfg_list = _genereate_wlan(max_num, wl_lists)
    if max_num>25:
        wlan_cfg_one = wlan_cfg_list[25] #Max 27 wlans in wlan group
    else:
        wlan_cfg_one = wlan_cfg_list[max_num-1]
    wlan_name_list = []
    for wlan in wlan_cfg_list:
        wlan_name_list.append(wlan['name'])
                        
    tcs.append(({'wl_cfg_all': wl_cfg_all}, 
                'CB_ZD_CLI_Edit_White_Lists_Batch', 
                '%sAdd white list' % tc_name, 
                1, 
                False))
    
    
    tcs.append(({'wlan_cfg_list':wlan_cfg_list}, 
                'CB_ZD_CLI_Create_Wlans', 
                '%sAdd Wlans' %tc_name, 
                2, 
                False))
    
    if wl_cfg_all[wlan_cfg_one['white_list']]['1'].get('ip'):
        rule_type = "MACandIP"
    else:
        rule_type = "MAC"
    
    tcs.append(({'white_list_name':wlan_cfg_one['white_list'],
              'rule_no':str(max_num),
              'rule_type': rule_type,
              'value_type':'switch',
              'ip_tag': default_ip['switch']
              },
            'CB_ZD_CLI_Edit_White_List_Special',
            '%sAdd rule for gateway from CLI' % tc_name,
            2,
            False))

    tcs.append(({'white_list_name':wlan_cfg_one['white_list'],
                  'rule_no':str(max_num-1),
                  'rule_type': rule_type,
                  'value_type':'server',
                  'ip_tag': default_ip['server']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sAdd rule for server from CLI' % tc_name,
                2,
                False))    

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg_one,
                 'wlan_ssid': wlan_cfg_one['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Gateway is Allowed' % tc_name, 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'wlan_name_list': wlan_name_list}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sDelete all wlans' %tc_name, 
                2, 
                True))     

    tcs.append(({'white_lists':wl_lists}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                '%sDelete all white lists' %tc_name, 
                2, 
                True))
    #----------------------
    
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                True))

    tcs.append(({}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                'Remove all white lists for cleanup ENV', 
                0, 
                True))
        
    return tcs

def _genereate_wlan(num, wl_lists):
    all_cfg = []
    base_name = 'Rqa-auto-RAT-CI-Perf-'
    for i in range(1, num+1):
        wlan_cfg = deepcopy(ci_wlan1_cfg)
        name = base_name+ str(i)
        wlan_cfg.update({'name':name,
                         'ssid':name,
                         'white_list':wl_lists[i-1],
                         })
        all_cfg.append(wlan_cfg)
    
    return all_cfg  

def _generate_white_list(num, mac_num):
    """
        wl_cfg_all= {'list1':{
                  '1':{
                    'mac':'aa:bb:11:22:33:44',
                    'ip':'192.168.0.6'
                     },
                  '2':{
                    'mac':'aa:bb:11:22:33:45',
                    'ip':'192.168.0.7'
                }
          }
    """
    all_cfg = {}
    for i in range(1,num+1):
        white_list_name = 'List' + str(i)
        if i <= mac_num:
            rule_conf = _generate_rule(num, i, 'MAC')
        else:
            rule_conf = _generate_rule(num, i, 'MACandIP')
        all_cfg[white_list_name] = rule_conf
    
    return all_cfg

def _generate_rule(num, idx, rule_type):
    
    base_mac = "aa:bb:cc:11:" + str(100-idx)+":"
    base_ip = "111.111." + str(idx) + "."
    rule_conf = {}
    for i in range(1,num+1):
        mac = base_mac + str(100-i)
        ip = base_ip + str(i)
        if rule_type == 'MAC':
            rule_conf[str(i)] = {'mac':mac}
        elif rule_type == 'MACandIP':
            rule_conf[str(i)] = {'mac':mac,'ip':ip}
    
    return rule_conf

def _genereate_wl_list(wl_cfg_all):
    wl_list = []
    for white_list in wl_cfg_all:
        wl_list.append(white_list)
    
    return wl_list

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation Performance"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
        
    ts_name = attrs['testsuite_name']
    sta1_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the first wireless station: ")
    sta2_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the second wireless station: ")
    
    if not sta1_ip_addr or not sta2_ip_addr:
        raise Exception("Get station fail, sta1: %s, sta2: %s" % (sta1_ip_addr,sta2_ip_addr))
    
    if sta1_ip_addr == sta2_ip_addr:
        raise Exception("Please select different station")

    ap_sym_dict = tbcfg['ap_sym_dict']
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    if len(active_ap_list) < 2:
        raise Exception("Need two active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    active_ap2 = active_ap_list[1]

    max_num = raw_input("Please input white list number between 1 to 64, default is [64]")
    if not max_num:
        max_num = 64
    elif max_num == 0 or max_num > 64:
        max_num = 64
    else:
        max_num = int(max_num)
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation Performance", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2, max_num)

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
    