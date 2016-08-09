'''
Test cases coverage:
    + Restricted subnets
    + Maximum restricted subnet entries
    
Created on 2011-9-2
@author: serena.tan@ruckuswireless.com
'''


import sys
import copy
import re
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


#--------------------------   Test Step builder    ---------------#
class TestStepBuilder:
    #######################################
    #         Access Methods              #
    #######################################
    @classmethod
    def build_station_pre_steps(cls, **kwargs):
        param_dict = {'active_ap': '',
                      'wlan_cfg': '',
                      'wlan_group_name': '',
                      'target_station': '',                  
                      'radio': '',
                      'sta_tag': 'sta_1',
                      'tcid': ''               
                     }
        param_dict.update(kwargs)
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        sta_tag = param_dict['sta_tag']
        tcid = param_dict['tcid']
        
        EXEC_LEVEL = 2   
        test_cfgs = []

        param_cfg = dict(active_ap = param_dict['active_ap'],
                         wlan_group_name = param_dict['wlan_group_name'], 
                         radio_mode = param_dict['radio'])
        
        common_name = '%sAssign AP radio %s to %s'
        common_name = common_name % (param_dict['tcid'], param_cfg['radio_mode'], param_cfg['wlan_group_name'])
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Assign_AP_To_Wlan_Groups', 
                          common_name,
                          1, 
                          False))
        
        test_cfgs.append(({'sta_tag': sta_tag, 
                           'wlan_cfg': wlan_cfg}, 
                          'CB_ZD_Associate_Station_1', 
                          '%sAssociate the station' % tcid, 
                          EXEC_LEVEL, 
                          False))    
        
        test_cfgs.append(({'sta_tag': sta_tag}, 
                          'CB_ZD_Get_Station_Wifi_Addr_1', 
                          '%sGet station wifi address' % tcid, 
                          EXEC_LEVEL, 
                          False))   
        
        test_cfgs.append(({'sta_tag': sta_tag,
                          'condition': 'disallowed',
                          'target': '172.126.0.252',},
                          'CB_ZD_Client_Ping_Dest', 
                          '%sStation ping a target IP before auth' % tcid, 
                          EXEC_LEVEL, 
                          False))        
    
        return test_cfgs
    
    @classmethod
    def build_station_post_steps(cls, **kwargs):
        param_dict = {'radio': None,
                      'active_ap': None,
                      'tcid': ''                           
                     }
        param_dict.update(kwargs)
        radio = param_dict['radio']
        active_ap = param_dict['active_ap']
        test_cfgs = []
        
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = 'Default', 
                         radio_mode = radio) 
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Assign_AP_To_Wlan_Groups', 
                          '%sAssign AP radio %s to Default wlan group' % (param_dict['tcid'], radio), 
                          2, 
                          True))
 
        return test_cfgs
    
    @classmethod
    def build_station_check_steps(cls, **kwargs):
        param_dict = {'active_ap': '',
                      'wlan_cfg': '',
                      'wlan_group_name': '',
                      'target_station': '',
                      'target_ip': '',
                      'radio': None,
                      'chk_radio': False,
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',
                      'hotspot_cfg': None,
                      'tcid': '',
                     }
        param_dict.update(kwargs)
        hotspot_cfg = copy.deepcopy(param_dict['hotspot_cfg'])
                
        EXEC_LEVEL = 2       
        test_cfgs = []
        kwargs = dict(EXEC_LEVEL = EXEC_LEVEL, 
                      wlan_cfg = copy.deepcopy(param_dict['wlan_cfg']), 
                      hotspot_cfg = hotspot_cfg, 
                      sta_tag = param_dict['sta_tag'], 
                      ap_tag = param_dict['ap_tag'], 
                      tcid = param_dict['tcid'], 
                      chk_radio = param_dict['chk_radio'], 
                      radio = param_dict['radio'])
        test_cfgs.extend(TestStepBuilder._build_hotspot_station(**kwargs))
        
        return test_cfgs
        
    @classmethod
    def build_station_ping_step(cls, **kwargs):
        EXEC_LEVEL = 2
        param_dict = {'sta_tag': 'sta_1',
                      'target_ip': '',
                      'condition': 'allowed',
                      'tcid': ''                           
                     }
        param_dict.update(kwargs)    
        sta_tag = param_dict['sta_tag']
        target_ip = param_dict['target_ip']
        condition = param_dict['condition']
        
        return[({'sta_tag': sta_tag,
                 'condition': condition,
                 'target': target_ip,},
                 'CB_ZD_Client_Ping_Dest', 
                 '%sStation ping target IP after auth' % param_dict['tcid'], 
                 EXEC_LEVEL, 
                 False)
               ]
        
    #######################################
    #         Protected Methods           #
    #######################################  
    @classmethod
    def _build_hotspot_station(cls,
                               EXEC_LEVEL = 2, 
                               wlan_cfg = None, 
                               hotspot_cfg = None, 
                               sta_tag = 'sta_1', 
                               ap_tag = 'tap',
                               tcid = '',
                               chk_radio = False,
                               radio = None):    
        test_cfgs = []            
        param_cfg = {'wlan_cfg': wlan_cfg, 
                     'chk_empty': False, 
                     'status': 'Unauthorized',
                     'chk_radio': chk_radio,
                     'radio_mode': radio,
                     'sta_tag': sta_tag,
                     'ap_tag': ap_tag,                 
                     }
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          '%sVerify station info before hotspot auth' % tcid, 
                          EXEC_LEVEL, 
                          False)) 
        
        test_cfgs.append(({'sta_tag': sta_tag},
                          'CB_Station_CaptivePortal_Start_Browser',
                          '%sOpen authentication web page' % tcid,
                          EXEC_LEVEL,
                          False,
                          ))
        
        param_cfgs = {'sta_tag': sta_tag}
        for k, v in hotspot_cfg['auth_info'].items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                          '%sPerform Hotspot authentication' % tcid, 
                          EXEC_LEVEL, 
                          False)) 
        
        username = hotspot_cfg['auth_info']['username']    
        param_cfg = {'wlan_cfg': wlan_cfg, 
                     'chk_empty': False, 
                     'status': 'Authorized',
                     'chk_radio': chk_radio,
                     'radio_mode': radio,
                     'sta_tag': sta_tag,
                     'ap_tag': ap_tag,
                     'username': username}

        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          '%sVerify station info after hotspot auth' % tcid, 
                          EXEC_LEVEL, 
                          False))
        
        test_cfgs.append(({'sta_tag': sta_tag},
                          'CB_Station_CaptivePortal_Download_File',
                          '%sDownload files from server' % tcid,
                          EXEC_LEVEL,
                          False))        

        test_cfgs.append(({'sta_tag': sta_tag},
                           'CB_Station_CaptivePortal_Quit_Browser',
                           '%sClose Authentication browser' % tcid,
                           EXEC_LEVEL, 
                           False))
            
        return test_cfgs       
    
    
#----------------------    Test step builder END      ---------------#


OPEN_NONE_INDEX  = 0
def define_wlans():
    wlan_cfg_list = []
    # Open-None
    wlan_cfg_list.append(dict(ssid = "RAT-Open-None-%s" % (time.strftime("%H%M%S")), 
                              auth = "open", encryption = "none", web_auth = None, 
                              type = 'hotspot' ))
    
    return wlan_cfg_list


def define_test_params(target_station):
    cfg = dict()
    cfg['target_station'] = target_station
    cfg['target_ip'] = '172.126.0.252'
    cfg['hotspot_cfg'] = {'login_page': 'https://192.168.0.250/slogin.html', 
                          'name': 'A Sampe Hotspot Profile'}
    
    cfg['local_server'] = {'username': 'local.username',
                           'password': 'local.password'}
    
    restricted_subnets = []
    restricted_subnets.append({'description': 'Restricted subnet - 1',
                              'type': 'Deny',
                              'destination_address': '172.11.0.252/32',
                              'application': "HTTP",
                              'protocol': '6',
                              'destination_port': '80'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 2',
                              'type': 'Deny',
                              'destination_address': '172.12.0.252/32',
                              'application': "HTTPS",
                              'protocol': '6',
                              'destination_port': '443'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 3',
                              'type': 'Deny',
                              'destination_address': '172.13.0.252/32',
                              'application': "FTP",
                              'protocol': '6',
                              'destination_port': '21'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 4',
                              'type': 'Deny',
                              'destination_address': '172.14.0.252/32',
                              'application': "TELNET",
                              'protocol': '6',
                              'destination_port': '23'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 5',
                              'type': 'Deny',
                              'destination_address': '172.15.0.252/32',
                              'application': "SMTP",
                              'protocol': '6',
                              'destination_port': '25'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 6',
                              'type': 'Deny',
                              'destination_address': '172.16.0.252/32',
                              'application': "DNS",
                              'protocol': 'Any',
                              'destination_port': '53'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 7',
                              'type': 'Deny',
                              'destination_address': '172.17.0.252/32',
                              'application': "DHCP",
                              'protocol': 'Any',
                              'destination_port': '67'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 8',
                              'type': 'Deny',
                              'destination_address': '172.18.0.252/32',
                              'application': "SNMP",
                              'protocol': 'Any',
                              'destination_port': '161'
                              })
      
    default_allow_subnet = \
        {'description': '',
         'type': 'Allow',
         'destination_address': '100.0.10.0/24',
         'application': "Any",
         'protocol': 'Any',
         'destination_port': 'Any'
         }
        
    for idx in range(0, 32 - 8 + 1):
        allow_subnet = default_allow_subnet.copy()
        allow_subnet.update({'description': 'Allowed subnet - %s' % idx,
                             'destination_address': '100.%s.10.0/24' % idx,
                             })
        restricted_subnets.append(allow_subnet)
    
    cfg['restricted_subnet_list'] = restricted_subnets
    
    return cfg


def build_sta_hot_cfg(test_params, server_name='local_server'):
    return dict(hotspot_profile_name = test_params['hotspot_cfg']['name'],
                auth_info = test_params[server_name],
                station_ip = test_params['target_station'])


def build_test_cases(target_station, target_station_radio, active_ap):
    test_params = define_test_params(target_station)
    sta_hotspot_cfg = build_sta_hot_cfg(test_params, server_name = 'local_server')
    
    wlans = define_wlans()
    wlans[OPEN_NONE_INDEX]['hotspot_profile'] = sta_hotspot_cfg['hotspot_profile_name']
    
    sta_tag = target_station
    ap_tag = active_ap
    
    user_cfg = {'username': 'local.username', 'password': 'local.password'}
        
    test_cfgs = []
    EXEC_LEVEL = 0
    
    test_cfgs.append(({'sta_tag': sta_tag, 'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the target station', 
                       EXEC_LEVEL, 
                       False))
     
    test_cfgs.append(({'ap_tag': ap_tag, 'active_ap': active_ap}, 
                      'CB_ZD_Create_Active_AP', 
                      'Get the active AP', 
                      EXEC_LEVEL, 
                      False)) 
    
    test_cfgs.append(({},
                      'CB_ZD_Remove_All_Config', 
                      'Remove all configuration from ZD', 
                      EXEC_LEVEL, 
                      False))
    
    test_cfgs.append((user_cfg, 
                      'CB_ZD_Create_Local_User', 
                      'Create a local user', 
                      EXEC_LEVEL, 
                      False))

    
    hotspot_service = copy.deepcopy(test_params['hotspot_cfg'])
    hotspot_service['restricted_subnet_list'] = test_params['restricted_subnet_list'][8:9]
    param_cfg = dict(hotspot_profiles_list = [hotspot_service])
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_Hotspot_Profiles', 
                      'Create a hotspot service', 
                      EXEC_LEVEL, 
                      False))
    
    test_cfgs.append((dict(wlan_cfg_list = copy.deepcopy(wlans)), 
                      'CB_ZD_Create_Wlans', 
                      'Create a hotspot WLAN',
                      EXEC_LEVEL, 
                      False))
        
    test_cfgs.append(({}, 
                      'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group',
                      'Remove all wlans from Default wlan group', 
                      EXEC_LEVEL,
                      False))
    
    wlans_copy = copy.deepcopy(wlans)
    OPEN_WLANGROUP = 'open_none_wlangroup_1'        
    param_cfg = dict(wlangroups_map = {OPEN_WLANGROUP:wlans_copy[OPEN_NONE_INDEX]['ssid']})
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLAN group and WLAN in pair', 
                      EXEC_LEVEL, 
                      False)) 
    
    tcid = '[Hotspot with restricted subnets]'
    EXEC_LEVEL = 2 
    param_dict = {'active_ap': active_ap,
                  'wlan_cfg': wlans_copy[OPEN_NONE_INDEX],
                  'wlan_group_name': OPEN_WLANGROUP,
                  'target_station': target_station,
                  'target_ip': test_params['target_ip'],
                  'radio': target_station_radio,
                  'chk_radio': False,
                  'sta_tag': sta_tag,
                  'ap_tag': ap_tag,
                  'hotspot_cfg': sta_hotspot_cfg,
                  'tcid': tcid,
                } 
    
    test_cfgs.extend(TestStepBuilder.build_station_pre_steps(**param_dict))
    test_cfgs.extend(TestStepBuilder.build_station_check_steps(**param_dict))
    test_cfgs.extend(TestStepBuilder.build_station_ping_step(**param_dict))
    
    target_ip_list = []
    for restricted_subnet in test_params['restricted_subnet_list'][8:9]:
        target_ip_list.append(restricted_subnet['destination_address'])
        
    param_cfg = dict(target_ip_list = target_ip_list, sta_tag = sta_tag) 
    test_cfgs.append((param_cfg, 
                      'CB_Station_Ping_Targets', 
                      '%sPing Targets and check if are not allowed' % tcid, 
                       EXEC_LEVEL, 
                       False))
    
    test_cfgs.extend(TestStepBuilder.build_station_post_steps(**param_dict))
        
    tcid = '[Hotspot Maximum restricted subnets]'
        
    hotspot_cfg = test_params['hotspot_cfg'].copy()
    hotspot_cfg['restricted_subnet_list'] = copy.deepcopy(test_params['restricted_subnet_list'])
    param_cfg = dict(hotspot_profiles_list = [hotspot_cfg])
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Edit_Hotspot_Profiles', 
                      '%sEdit existing hotspot service' % tcid, 
                      1, 
                      False))
    
    param_dict = {'active_ap': active_ap,
                  'wlan_cfg': wlans_copy[OPEN_NONE_INDEX],
                  'wlan_group_name': OPEN_WLANGROUP,
                  'target_station': target_station,
                  'target_ip': test_params['target_ip'],
                  'radio': target_station_radio,
                  'chk_radio': False,
                  'sta_tag': sta_tag,
                  'ap_tag': ap_tag,
                  'hotspot_cfg': sta_hotspot_cfg,
                  'tcid': tcid,
                  }    
    
    test_cfgs.extend(TestStepBuilder.build_station_pre_steps(**param_dict))
    test_cfgs.extend(TestStepBuilder.build_station_check_steps(**param_dict))
    test_cfgs.extend(TestStepBuilder.build_station_ping_step(**param_dict))
    
    target_ip_list = []
    for restricted_subnet in test_params['restricted_subnet_list']:
        target_ip_list.append(restricted_subnet['destination_address'])
        
    param_cfg = dict(sta_tag = sta_tag, target_ip_list = target_ip_list) 
    test_cfgs.append((param_cfg, 
                      'CB_Station_Ping_Targets', 
                      '%sPing Targets and check if are not allowed' % tcid, 
                       EXEC_LEVEL, 
                       False))
    
    test_cfgs.extend(TestStepBuilder.build_station_post_steps(**param_dict))

    test_cfgs.append(({},
                      'CB_ZD_Remove_All_Config', 
                      'Remove all configuration from ZD to clean up', 
                      0, 
                      True))
    return test_cfgs


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_station = (0, "ng"),
                 ts_name = ""
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an active AP: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            
            else:
                break
            
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio() 
        
    else:
        active_ap = attrs["active_ap"]
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if target_sta_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, target_sta_radio)
        return

    test_cfgs = build_test_cases(sta_ip_addr, target_sta_radio, active_ap)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        active_ap_status = ap_sym_dict[active_ap]['status']
        active_ap_role = ''
        res = re.search('Connected \((.+)\)', active_ap_status, re.I)
        if res:
            active_ap_role = ' - %s' % res.group(1).split(' ')[0]
        
        ts_name = "Reading WISPr Restricted Subnets - %s" % target_sta_radio    
        #ts_name = "Reading WISPr Restricted Subnets - %s%s - %s" % (active_ap_model, active_ap_role, target_sta_radio)

    ts = testsuite.get_testsuite(ts_name, 
                                 'Verify Reading WISPr Restricted Subnets',
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest = True)

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
