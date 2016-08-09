'''
    10 clients rat-open-none, 10-11a/b/g/n/a
    Set channel to 11na
    Check vap/wlan/wlan group/ap/ap->radio/ap group/ap group->ap/system stat num if correct.
    Set channel to 11ng
    Check vap/wlan/wlan group/ap/ap->radio/ap group/ap group->ap/system stat num if correct.
    Destroy 10 clients
    Check vap/wlan/wlan group/ap/ap->radio/ap group/ap group->ap/system stat num if correct.
      
Created on 2013-8-5
@author: cwang@ruckuswireless.com
'''
import time
import sys
from copy import deepcopy

import libZD_TestSuite_ata as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


def build_cfg(aps, wlans, wlangroups):
    #ap-mac, wlan-cfg, wlangroup-cfg, band, channel, clientnum, tcid
    return [(aps[0], wlans[0], wlangroups[0], 2400, 11, 5, "[2.4g clients number.]"),
            (aps[1], wlans[1], wlangroups[1], 5000, 36, 10, "[5g clients number.]"),
            (aps[1], wlans[2], wlangroups[2], 5000, 36, 8, "[5g clients with Default wlan group]"),
            (aps[0], wlans[0], wlangroups[0], 2400, 11, 0, "[no any clients]"), ]

def build_wlan_cfg():
    return [dict(ssid = "RAT-Open-24g-%s" % (time.strftime("%H%M%S")),
                 auth = "open", wpa_ver = "", encryption = "none"),
                 
            dict(ssid = "RAT-Open-5g-%s" % (time.strftime("%H%M%S")),
                 auth = "open", wpa_ver = "", encryption = "none"),
            
            dict(ssid = "RAT-Open-5g-default-%s" % (time.strftime("%H%M%S")),
                 auth = "open", wpa_ver = "", encryption = "none"),
            ]


def build_wlan_group_cfg(wlans):
    return [{'wg_name': 'rat-wg24g-open',              
             'wlan_member': {'%s'%wlans[0]['ssid']: {}}},
             {'wg_name': 'rat-wg5g-open',              
             'wlan_member': {'%s'%wlans[1]['ssid']: {}}},
             {'wg_name':'Default', 
              'wlan_member':{'%s'%wlans[2]['ssid']:{}}}
             ]
    
def build_tcs(aps):
    tcs = []
    
    tcs.append(({},
                'CB_ZD_CLI_Default_AP_Wlan_Groups',
                'Change ap wlan groups to Default',
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

    wlans = build_wlan_cfg()
    wlangroups = build_wlan_group_cfg(wlans)
    cfgs = build_cfg(aps, wlans, wlangroups)    
    for (apmac, wlancfg, wlangroupcfg, band, channel, clientnum, tcid) in cfgs:        
    
        tcs.append(({'wlan_cfg_list':[wlancfg]},
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
                    '%sCreate wlan groups [%s]' % (tcid, wlangroupcfg['wg_name']),
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
        
        tcs.append(({},
                    'CB_ATA_Setup_ENV',
                    '%sSetup ATA ENV, bind with Veriwave.' % tcid,
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
        
        cgname = 'mytest_%ds'% clientnum
        clientg = {'clientname':cgname,                   
                   'ssid':wlancfg['ssid'],
                   'client_type':"802.11a/b/g/n",    
                   'security_type':None,
                   'passphrase':None}
        
        if clientnum !=0:
            tcs.append(({'clientgroups':[clientg]},
                        'CB_ATA_Create_ClientGroups',
                        '%sCreate client groups as count%d' % (tcid, clientnum),
                        2,
                        False
                        ))        
        
        tcs.append(({'clientnum':clientnum},
                    'CB_CLI_Check_Clients',
                    '%sCheck clients from CLI' % tcid,
                    2,
                    False
                    ))
            
        #"[ZD-28925]"    
        #wlan->num-sta, wlan->assoc-stas, wlan->vap->num-sta, 
        #wlan->vap->assoc-stas, ap->num-sta, ap->assoc->stas, 
        #ap->radio->num-sta, ap->radio->assoc-stas, system-> num-sta, 
        #system-> assoc-stas, system-> assoc-stas-d, system->assoc-stas-h, 
        #wlan group->num-sta, wlan group->assoc-stas, ap group->num-sta, 
        #ap group->assoc-stas
        tcs.append(({'wlans':[wlancfg],
                     'wgs':[wlangroupcfg],
                     'clientnum':clientnum,
                     'band':band
                     },                
                    'CB_ATA_Test_Sta_Num',
                    '%sauthorized and associated STAs number counters verification in different level' % tcid,
                    2,
                    False
                    ))
        
        
        if clientnum !=0:
            tcs.append(({'grpname':cgname},
                        'CB_ATA_Destroy_Client_Group',
                        '%sDestroy Client Group%s' % (tcid, cgname) ,
                        2,
                        True
                        ))
    
    
        tcs.append(({},
                    'CB_ATA_Purge_ENV',
                    '%sPurge Ports from veriwave' % tcid,
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
            
    return tcs

    
    
def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Statistic Reporting-Clients-Counter",
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
    
    ts_name_list = [('ATA clients number in different level check.', build_tcs),]
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