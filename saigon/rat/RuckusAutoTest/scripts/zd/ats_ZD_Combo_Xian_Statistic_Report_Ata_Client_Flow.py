'''
Create control Flow to check rx/tx packages, bytes etcs with different WLANs.

Created on Nov 4, 2013
@author: cwang@ruckuswireless.com
'''
import time
import sys
from copy import deepcopy

import libZD_TestSuite_ata as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

from contrib.wlandemo import defaultWlanConfigParams as KK

def ids(aps):  #wlan, apmac, wlangroup, command name, time[mins], band, channel, clientcfg  
    params = []
    wlan = KK.get_cfg('open-none')
    wlangroups = [{'wg_name': 'rat-wg24g-open',              
                   'wlan_member': {}},
                   {'wg_name': 'rat-wg5g-open',              
                    'wlan_member': {}},
                    {'wg_name':'Default', 
                     'wlan_member':{}}]
    
    ccfg = {'ssid':wlan.get('ssid'), 
            'clientname':"c_%s" % wlan.get('ssid'),
            'client_type':'802.11a/b/g/n',
            'security_type':None,
            'passphrase':None}
    wg = deepcopy(wlangroups[1])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}}) 
    params.append((wlan, aps[0], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 5000, 36, ccfg))
    
    wlan = KK.get_cfg('open-wep64')
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname':"c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':'WEP-Open-40',
             'passphrase':wlan.get("key_string"),             
           }
    wg = deepcopy(wlangroups[0])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})    
    params.append((wlan, aps[0], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 2400, 11, ccfg))
    
    wlan = KK.get_cfg('open-wep128')
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname':"c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':'WEP-Open-128',
             'passphrase':wlan.get("key_string"),             
           }
    
    wg = deepcopy(wlangroups[1])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})    
    params.append((wlan, aps[0], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 5000, 36, ccfg))
    
    wlan = KK.get_cfg('psk-wpa-tkip')
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname':"c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':'WPA-PSK',                          
             'passphrase':wlan.get("key_string")
           }
    
    wg = deepcopy(wlangroups[1])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})
    params.append((wlan, aps[0], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 5000, 36, ccfg))
    
    wlan = KK.get_cfg('psk-wpa-aes')
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname':"c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':'WPA-PSK-AES',                  
             'passphrase':wlan.get("key_string")
           }
    wg = deepcopy(wlangroups[0])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})    
    params.append((wlan, aps[1], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 2400, 11, ccfg))
    
    wlan = KK.get_cfg('psk-wpa2-tkip')
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname':"c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':'WPA2-PSK-TKIP',          
             'passphrase':wlan.get("key_string")
           }
    wg = deepcopy(wlangroups[1])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})    
    params.append((wlan, aps[1], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 5000, 36, ccfg))
    
    wlan = KK.get_cfg('psk-wpa2-aes')
    ccfg = {'ssid':wlan.get('ssid'), 
            'clientname':"c_%s" % wlan.get('ssid'),
            'client_type':'802.11a/b/g/n',
            'security_type':'WPA2-PSK',                          
            'passphrase':wlan.get("key_string")
           }
    wg = deepcopy(wlangroups[0])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})    
    params.append((wlan, aps[1], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 2400, 11, ccfg))
    
#    wlan = KK.get_cfg('eap-wpa-tkip')
    wlan = {'ssid': 'eap-wpa-tkip-ras', 
            'key_string': '', 
            'key_index': '', 
            'auth': 'dot1x-eap', 
            'use_radius': True, 
            'encryption': 'TKIP', 
            'wpa_ver': 'WPA',
            'auth_server':'RADIUS'
            }
    
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname':"c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':"WPA-PEAP-MSCHAPv2",
             'identity':'ras.eap.user',  
             'password':'ras.eap.user',
             'passphrase':None        
           }
    
    wg = deepcopy(wlangroups[1])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})
    params.append((wlan, aps[1], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 5000, 36, ccfg))
    
    
    
    wlan = {'ssid': 'eap-wpa2-aes', 
            'key_string': '', 
            'key_index': '', 
            'auth': 'dot1x-eap', 
            'use_radius': True, 
            'encryption': 'AES', 
            'wpa_ver': 'WPA2',
            'auth_server':'RADIUS'
            }
    ccfg = {'ssid':wlan.get('ssid'), 
             'clientname': "c_%s" % wlan.get('ssid'),
             'client_type':'802.11a/b/g/n',
             'security_type':"WPA2-PEAP-MSCHAPv2",
             'identity':'ras.eap.user',  
             'password':'ras.eap.user', 
             'passphrase':None
           }
    wg = deepcopy(wlangroups[0])
    wg.update({'wlan_member':{wlan.get('ssid'):{}}})
    params.append((wlan, aps[1], wg, '[Traffic with %s]' % wlan.get('ssid'), 3, 2400, 11, ccfg))
    
    return params


def build_aaa():
    return {'server_name': 'RADIUS',
            'server_addr': '192.168.0.252',
            'radius_secret': '1234567890',
            'server_port': '1812',
            'type':'radius-auth'
            }
    
def build_tcs(aps):
    tcs = []
    
    tcs.append(({},
                'CB_ZD_CLI_Default_AP_Wlan_Groups',
                'Change AP wlan groups to Default',
                0,
                False))
        
    
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_All_WLAN_Groups', 
                'Remove All WLAN Groups', 
                0, 
                False))
                  
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_All_AAA_Servers',
                "Remove all AAA Servers",
                0,
                False
                ))
    
    aaa = build_aaa()
    tcs.append(({'server_cfg_list':[aaa]},
                'CB_ZD_CLI_Configure_AAA_Servers',
                'Create AAA Servers',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ATA_Setup_ENV',
                'Setup ATA ENV, bind with Veriwave.',
                0,
                False
                ))
    
    tcs.append(({'servers':[{'servername':'testserver'}]},
                'CB_ATA_Create_Servers',
                'Create Test Server',
                0,
                False
                )) 
        
    for wlan, apmac, wlangroupcfg, tcid, wait, band, channel, ccfg in ids(aps):
         tcs.append(({'wlan_cfg_list':[wlan]},
                    'CB_ZD_CLI_Create_Wlans',
                    '%sCreate Wlans' % tcid,
                    1,
                    False))
         
         tcs.append(({'wg_name': 'Default',        
                     'wlan_member': {}},
                     'CB_ZD_CLI_Set_Default_WLAN_Groups',
                     '%sSet Default WLAN Groups, wlan members to None' % tcid,
                     2,
                     False
                    ))
        
    
         tcs.append(({'wlan_group_cfg_list':[wlangroupcfg]},
                    'CB_ZD_CLI_Create_WLAN_Groups',
                    '%sCreate wlan groups %s' % (tcid, wlangroupcfg['wg_name']),
                    2,
                    False
                    ))  
         
         cfg = {'mac_addr': '%s' % apmac}
         if band == 5000:                                    
            cfg.update({'radio_na': {'wlangroups': '%s' % wlangroupcfg['wg_name'],
                                     'channel': channel}})                                            
            cfg.update({'radio_bg': {'wlangroups': 'Default'}})
        
         if band == 2400:
            cfg.update({'radio_bg': {'wlangroups': '%s' % wlangroupcfg['wg_name'],
                                     'channel': channel}})                                            
            cfg.update({'radio_na': {'wlangroups': 'Default'}})
                    
         tcs.append(({'ap_cfg':cfg},
                    'CB_ZD_CLI_Configure_AP',
                    '%sConfigure AP' % tcid,
                    2,
                    False
                    ))
                          
         
         tcs.append(({'channel':channel,
                     'band':band,},
                     'CB_ATA_Set_Channel',
                     '%sSet band%s channel%s' % (tcid, band, channel),
                     2,
                     False
                    ))
        
         tcs.append(({"clients":[ccfg]},
                     'CB_ATA_Create_Clients',
                     '%sCreate Clients' % tcid,
                     2,
                     False
                     ))                  
         
         tcs.append(({'flowname':"f_%s" % wlan.get('ssid'),   
                      'servername':'testserver',   
                      'clientname':ccfg.get("clientname")                
                      },
                     'CB_ATA_Create_Flow',
                     '%sCreate Flow' % tcid,
                     2,
                     False))
         
         tcs.append(({'flowname':"f_%s" % wlan.get('ssid')},
                     'CB_ATA_Start_Flow',
                     '%sStart Flow' % tcid,
                     2,
                     False
                     ))
         
         tcs.append(({'timeout': wait * 60},
                     'CB_AP_Wait_For',
                     '%sWait for traffic' % tcid,
                     2,
                     False
                     ))
         
         
         tcs.append(({'flowname':"f_%s" % wlan.get('ssid')},
                     'CB_ATA_Stop_Flow',
                     '%sStop Flow' % tcid,
                     2,
                     False
                     ))
         
         tcs.append(({'timeout':90},
                     'CB_AP_Wait_For',
                     '%sWait for statistic report trigger timeout' % tcid,
                     2,
                     False
                     ))
         
         tcs.append(({},
                     'CB_ZD_Pull_XML_File',
                     '%s pull xml from ZD' % tcid, 
                     2, 
                     False
                     ))
         
         tcs.append(({'flowname':"f_%s" % wlan.get('ssid')},
                     'CB_ATA_Get_Flow_Info',
                     '%sGet flow %s' % (tcid, wlan.get('ssid')),
                     2,
                     False 
                     ))
         
         tcs.append(({'flowname':"f_%s" % wlan.get('ssid'),
                      'ssid':wlan.get('ssid'),
                      'apmac':apmac,
                      },
                     'CB_ATA_Test_Flow',
                     '%sCheck flow Info from XML and CLI' % (tcid),
                     2,
                     False
                     ))
         
         tcs.append(({'flowname':"f_%s" % wlan.get('ssid')},
                      'CB_ATA_Destroy_Flow',
                      '%sDestroy Flow%s' % (tcid, wlan.get('ssid')),
                      2,
                      True
                     ))
         
         tcs.append(({},
                    'CB_ZD_CLI_Default_AP_Wlan_Groups',
                    '%sDefault ap wlan groups' % tcid,
                    2,
                    True
                    ))
    
         tcs.append(({}, 
                    'CB_ZD_CLI_Remove_All_WLAN_Groups', 
                    '%sClean All WLAN Groups' % tcid, 
                    2, 
                    True))
                  
         tcs.append(({}, 
                    'CB_ZD_CLI_Remove_Wlans', 
                    '%sClean all WLANs' % tcid, 
                    2, 
                    True))   
         


    tcs.append(({},
                'CB_ZD_CLI_Remove_All_AAA_Servers',
                "Delete all AAA Servers",
                0,
                True
                ))
    
    tcs.append(({'servers':[{'servername':'testserver'}]},
                'CB_ATA_Destroy_Servers',
                'Destroy Test Server',
                0,
                True
                )) 
    
    tcs.append(({},
                'CB_ATA_Purge_ENV',
                'Purge ATA ENV, debind with Veriwave.',
                0,
                True
                ))    
        
    return tcs


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Statistic Reporting-Client-Flow-Encryption-Types",
                 target_station = (0, "ng"),
                 tbtype='ZD_ATA_Stations'
                 )
    attrs.update(kwargs)    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
        
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if len(all_aps_mac_list) == 0:
        raise Exception("No APs in your testbed.")
    
    if len(all_aps_mac_list) < 2:
        raise Exception("Need at least 2 APs with dual band")
    
    def get_model_by_mac(ap_sym_dict, mac):
        for tag, apcfg in ap_sym_dict.items():
            if apcfg['mac'] == mac:
                return apcfg['model']
        raise Exception("Not found ap %s" % mac)
        
    aps = []
    for mac in all_aps_mac_list:
        ap_model = get_model_by_mac(ap_sym_dict, mac)
        lib_Constant.is_ap_support_dual_band(ap_model)
        aps.append(mac)
    
    if len(aps) < 2:
        raise Exception("2 dual APs required.")
    
    ts_name_list = [('ATA client traffic with different encryption types.', build_tcs),]
    cfg = {}

    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(aps)
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
            
def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)


