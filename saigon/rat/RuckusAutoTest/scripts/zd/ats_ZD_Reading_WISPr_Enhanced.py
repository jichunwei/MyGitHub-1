import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:21.01.%02d" % tcid

def get_common_name(id, name):
    return "%s - %s" % (id, name)

def defineTestConfiguration(target_station, active_ap_list):
    test_cfgs = []
    
    restricted_subnets = []
    restricted_subnets.append({'description': 'Restricted subnet - 1',
                              'action': 'Deny',
                              'destination_addr': '172.11.0.252/32',
                              'application': "HTTP",
                              'protocol': '6',
                              'destination_port': '80'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 2',
                              'action': 'Deny',
                              'destination_addr': '172.12.0.252/32',
                              'application': "HTTPS",
                              'protocol': '6',
                              'destination_port': '443'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 3',
                              'action': 'Deny',
                              'destination_addr': '172.13.0.252/32',
                              'application': "FTP",
                              'protocol': '6',
                              'destination_port': '21'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 4',
                              'action': 'Deny',
                              'destination_addr': '172.14.0.252/32',
                              'application': "TELNET",
                              'protocol': '6',
                              'destination_port': '23'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 5',
                              'action': 'Deny',
                              'destination_addr': '172.15.0.252/32',
                              'application': "SMTP",
                              'protocol': '6',
                              'destination_port': '25'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 6',
                              'action': 'Deny',
                              'destination_addr': '172.16.0.252/32',
                              'application': "DNS",
                              'protocol': 'Any',
                              'destination_port': '53'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 7',
                              'action': 'Deny',
                              'destination_addr': '172.17.0.252/32',
                              'application': "DHCP",
                              'protocol': 'Any',
                              'destination_port': '67'
                              })
    restricted_subnets.append({'description': 'Restricted subnet - 8',
                              'action': 'Deny',
                              'destination_addr': '172.18.0.252/32',
                              'application': "SNMP",
                              'protocol': 'Any',
                              'destination_port': '161'
                              })
      
    default_allow_subnet = \
        {'description': '',
         'action': 'Allow',
         'destination_addr': '100.0.10.0/24',
         'application': "Any",
         'protocol': 'Any',
         'destination_port': 'Any'
         }
        
    for idx in range(0, 32 - 8 + 1):
        allow_subnet = default_allow_subnet.copy()
        allow_subnet.update({'description': 'Allowed subnet - %s' % idx,
                             'destination_addr': '100.%s.10.0/24' % idx,
                             })
        
        restricted_subnets.append(allow_subnet)

    
    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    
    wep_cfg = dict(auth = "open", wpa_ver = "", encryption = "WEP-128",
                   key_index = "1" , key_string = utils.make_random_string(26, "hex"))
    wpa_cfg = dict(auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                   key_string = utils.make_random_string(random.randint(8, 63), "hex"))
    
    def_test_params = {'target_station': target_station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'https://192.168.0.250/slogin.html',
                                       'name': 'Hotspot Profile - 1'},
                       'auth_info': {'type':'local', 'username': 'local.username', 'password': 'local.password'}}

    test_params = deepcopy(def_test_params)
    test_cfgs.append((test_params, "ZD_Hotspot_Enable_Disable",
                      get_common_name(tcid(1), "Disable/Enable Hotspot on a WLAN")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'restricted_subnet_list': restricted_subnets[8:9]})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(2), "Restricted subnets")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'restricted_subnet_list': restricted_subnets})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(3), "Maximum restricted subnet entries")))

    test_params = deepcopy(def_test_params)
    test_params.update({'testing_feature': 'multiple_profile', 'number_of_wlan': 6})
    test_cfgs.append((test_params, "ZD_Hotspot_Multiple_Profile_Wlan",
                      get_common_name(tcid(4), "Multiple Hotspot profiles on differrent WLANs")))

    test_params = deepcopy(def_test_params)
    test_params.update({'testing_feature': 'single_profile', 'number_of_wlan': 6})
    test_cfgs.append((test_params, "ZD_Hotspot_Multiple_Profile_Wlan",
                      get_common_name(tcid(5), "Single Hotspot profile shared by different WLANs")))

    test_params = deepcopy(def_test_params)
    test_params.update({'wlan_cfg': wep_cfg})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(8), "Hotspot with encryption WEP")))

    test_params = deepcopy(def_test_params)
    test_params.update({'wlan_cfg': wpa_cfg})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(9), "Hotspot with encryption WPA2-AES")))

    test_params = deepcopy(def_test_params)
    test_params.update({'test_feature': 'invalid-username'})
    test_cfgs.append((test_params, "ZD_Hotspot_WrongAuthentication",
                      get_common_name(tcid(10), "Wrong authentication using invalid username - local database")))

    test_params = deepcopy(def_test_params)
    test_params.update({'test_feature': 'invalid-password'})
    test_cfgs.append((test_params, "ZD_Hotspot_WrongAuthentication",
                      get_common_name(tcid(11), "Wrong authentication using invalid password - local database")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'session_timeout':6})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(12), "ZD Session Timeout disabled with Session Timeout enabled on Radius server")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'session_timeout':6})
    test_params['hotspot_cfg'].update({'session_timeout':'6'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(13), "ZD Session Timeout enabled with Session Timeout enabled on Radius server")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_params['hotspot_cfg'].update({'session_timeout':'6'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(14), "ZD Session Timeout enabled with Session Timeout disabled on Radius server")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'walled_garden_list': walled_garden_entries[:3]})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(16), "Walled Garden function")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'walled_garden_list': walled_garden_entries})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(18), "Maximum Walled Garden entries")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(20), "Hotspot authentication with IAS")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.252', 'svr_port':'1812', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(22), "Hotspot authentication with freeradius")))

    test_params = deepcopy(def_test_params)
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(23), "Hotspot authentication with local database")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'ad', 'username': 'ad.user', 'password': 'ad.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'389', 'svr_info':'example.net'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(24), "Hotspot authentication with AD")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'start_page': 'http://www.ruckuswireless.com'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(32), "Start page redirect to a URL")))

    test_params = deepcopy(def_test_params)
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(33), "Start page ridirect to the original URL")))

#    test_params = deepcopy(def_test_params)
#    test_params['hotspot_cfg'].update({'logout_page': 'https://192.168.0.250/slogout.html'})
#    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
#                      get_common_name(tcid(44), "UAM Redirected HTTP login/logout URLs")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'logout_page': 'https://192.168.0.250/slogout.html'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(45), "UAM Redirected HTTPS login/logout URLs")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': True})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(48), "Relogin within Idle Timeout threshold with Idle Timeout enabled on Radius server - disabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': True})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(49), "Relogin within Idle Timeout threshold with Idle Timeout enabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': True})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(50), "Relogin within Idle Timeout threshold with Idle Timeout disabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': False})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(51), "Relogin beyond Idle Timeout threshold with Idle Timeout enabled on Radius server - disabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': False})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(52), "Relogin beyond Idle Timeout threshold with Idle Timeout enabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': False})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(53), "Relogin beyond Idle Timeout threshold with Idle Timeout disabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'radius_location_id': 'organization=ruckus-wireless-inc',
                                       'radius_location_name': '880_west_maude_ave_sunnyvale_ca_94085'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.252', 'svr_port':'1812', 'svr_info':'1234567890'})
    test_params['acct_info'].update({'svr_addr':'192.168.0.252', 'svr_port':'1813', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(59), "Accounting server with extra attributes")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'interim_update_interval': '2'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.252', 'svr_port':'1812', 'svr_info':'1234567890'})
    test_params['acct_info'].update({'svr_addr':'192.168.0.252', 'svr_port':'1813', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      get_common_name(tcid(61), "Accounting server update frequency")))

    # Distribute active AP to all the test cases
    idx = 0
    total_ap = len(active_ap_list)
    for test_cfg in test_cfgs:
        test_cfg[0]['active_ap'] = sorted(active_ap_list)[idx]
        idx = (idx + 1) % total_ap

    return test_cfgs

def make_test_suite(**kwargs):
    tbi = testsuite.getTestbed2(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    target_sta = testsuite.getTargetStation(tb_cfg['sta_ip_list'])
    ap_sym_dict = tb_cfg["ap_sym_dict"]
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    ts_name = "WISPr"

    test_cfgs = defineTestConfiguration(target_sta, active_ap_list)
    ts = testsuite.get_testsuite(ts_name, "Verify Hotspot/WISPr feature")

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

