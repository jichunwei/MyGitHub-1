import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(tcid, ap_model_id, ap_role_id):
    return "TCID:21.01.%02d.%s.%s" % (tcid, ap_model_id, ap_role_id)

def get_common_name(id, description, ap_type):
    return "%s - %s - %s" % (id, description, ap_type)

def defineTestConfiguration(target_station, ap_sym_dict, active_ap_list):
    test_cfgs = []
    restricted_subnets = ["172.21.0.252/32", "172.22.0.252/32", "172.23.0.252/32", "172.24.0.252/32", "172.25.0.252/32", "172.26.0.252/32",
                          "10.0.0.0/24", "10.1.0.0/24", "10.2.0.0/24", "10.3.0.0/24", "10.4.0.0/24", "10.5.0.0/24", "10.6.0.0/24",
                          "10.7.0.0/24", "10.8.0.0/24"]
    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    wep_cfg = dict(auth="open", wpa_ver="", encryption="WEP-128",
                   key_index="1" , key_string=utils.make_random_string(26,"hex"))
    wpa_cfg = dict(auth="PSK", wpa_ver="WPA2", encryption="AES",
                   key_string=utils.make_random_string(random.randint(8,63),"hex"))
    def_test_params = {'target_station': target_station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'A Sampe Hotspot Profile'},
                       'auth_info': {'type':'local', 'username': 'local.username', 'password': 'local.password'}}

    test_params = deepcopy(def_test_params)
    test_cfgs.append((test_params, "ZD_Hotspot_Enable_Disable",
                      (1, "Disable/Enable Hotspot on a WLAN")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'restricted_subnet_list': restricted_subnets[:5]})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (2, "Restricted subnets")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'restricted_subnet_list': restricted_subnets})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (3, "Maximum restricted subnet entries")))

    test_params = deepcopy(def_test_params)
    test_params.update({'testing_feature': 'multiple_profile', 'number_of_wlan': 6})
    test_cfgs.append((test_params, "ZD_Hotspot_Multiple_Profile_Wlan",
                      (4, "Multiple Hotspot profiles on differrent WLANs")))

    test_params = deepcopy(def_test_params)
    test_params.update({'testing_feature': 'single_profile', 'number_of_wlan': 6})
    test_cfgs.append((test_params, "ZD_Hotspot_Multiple_Profile_Wlan",
                      (5, "Single Hotspot profile shared by different WLANs")))

    test_params = deepcopy(def_test_params)
    test_params.update({'wlan_cfg': wep_cfg})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (8, "Hotspot with encryption WEP")))

    test_params = deepcopy(def_test_params)
    test_params.update({'wlan_cfg': wpa_cfg})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (9, "Hotspot with encryption WPA2-AES")))

    test_params = deepcopy(def_test_params)
    test_params.update({'test_feature': 'invalid-username'})
    test_cfgs.append((test_params, "ZD_Hotspot_WrongAuthentication",
                      (10, "Wrong authentication using invalid username - local database")))

    test_params = deepcopy(def_test_params)
    test_params.update({'test_feature': 'invalid-password'})
    test_cfgs.append((test_params, "ZD_Hotspot_WrongAuthentication",
                      (11, "Wrong authentication using invalid password - local database")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'session_timeout':2})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (12, "ZD Session Timeout disabled with Session Timeout enabled on Radius server")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'session_timeout':2})
    test_params['hotspot_cfg'].update({'session_timeout':'2'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (13, "ZD Session Timeout enabled with Session Timeout enabled on Radius server")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_params['hotspot_cfg'].update({'session_timeout':'2'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (14, "ZD Session Timeout enabled with Session Timeout disabled on Radius server")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'walled_garden_list': walled_garden_entries[:3]})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (16, "Walled Garden function")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'walled_garden_list': walled_garden_entries})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (18, "Maximum Walled Garden entries")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (20, "Hotspot authentication with IAS")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.252', 'svr_port':'1812', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (22, "Hotspot authentication with freeradius")))

    test_params = deepcopy(def_test_params)
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (23, "Hotspot authentication with local database")))

    test_params = deepcopy(def_test_params)
    test_params['auth_info'].update({'type':'ad', 'username': 'ad.user', 'password': 'ad.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'389', 'svr_info':'example.net'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (24, "Hotspot authentication with AD")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'start_page': 'http://www.ruckuswireless.com'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (32, "Start page redirect to a URL")))

    test_params = deepcopy(def_test_params)
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (33, "Start page redirect to the original URL")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'logout_page': 'http://192.168.0.250/logout.html'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (44, "UAM Redirected HTTP login/logout URLs")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'logout_page': 'http://192.168.0.250/slogout.html'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (45, "UAM Redirected HTTPS login/logout URLs")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': True})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (48, "Relogin within Idle Timeout threshold with Idle Timeout enabled on Radius server - disabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': True})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (49, "Relogin within Idle Timeout threshold with Idle Timeout enabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': True})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (50, "Relogin within Idle Timeout threshold with Idle Timeout disabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': False})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (51, "Relogin beyond Idle Timeout threshold with Idle Timeout enabled on Radius server - disabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': False})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.timeout.user', 'password': 'rad.timeout.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890', 'idle_timeout':'10'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (52, "Relogin beyond Idle Timeout threshold with Idle Timeout enabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params.update({'relogin_before_timer_expired': False})
    test_params['hotspot_cfg'].update({'idle_timeout':'10'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.250', 'svr_port':'18120', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (53, "Relogin beyond Idle Timeout threshold with Idle Timeout disabled on Radius server - enabled on ZD")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'radius_location_id': 'organization=ruckus-wireless-inc',
                                       'radius_location_name': '880_west_maude_ave_sunnyvale_ca_94085'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.252', 'svr_port':'1812', 'svr_info':'1234567890'})
    test_params['acct_info'].update({'svr_addr':'192.168.0.252', 'svr_port':'1813', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (59, "Accounting server with extra attributes")))

    test_params = deepcopy(def_test_params)
    test_params['hotspot_cfg'].update({'interim_update_interval': '2'})
    test_params['auth_info'].update({'type':'radius', 'username': 'rad.cisco.user', 'password': 'rad.cisco.user',
                                     'svr_addr':'192.168.0.252', 'svr_port':'1812', 'svr_info':'1234567890'})
    test_params['acct_info'].update({'svr_addr':'192.168.0.252', 'svr_port':'1813', 'svr_info':'1234567890'})
    test_cfgs.append((test_params, "ZD_Hotspot_Functionality",
                      (61, "Accounting server update frequency")))

    # Distribute active AP to all the test cases
    test_cfgs_list = []
    for active_ap in active_ap_list:
        active_ap_conf = ap_sym_dict[active_ap]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
        for test_cfg in test_cfgs:
            test_cfg[0]['active_ap'] = active_ap
            test_cfgs_list.append((test_cfg[0], test_cfg[1],
                                  get_common_name(tcid(test_cfg[2][0], ap_model_id, ap_role_id), test_cfg[2][1], ap_type)))

    return test_cfgs_list

def make_test_suite(**kwargs):
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    target_sta = testsuite.getTargetStation(tb_cfg['sta_ip_list'])
    ap_sym_dict = tb_cfg["ap_sym_dict"]
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    ts_name = "WISPr"

    test_cfgs = defineTestConfiguration(target_sta, ap_sym_dict, active_ap_list)
    ts = testsuite.get_testsuite(ts_name, "Verify Hotspot/WISPr feature")

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        print test_params, test_name, common_name
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
