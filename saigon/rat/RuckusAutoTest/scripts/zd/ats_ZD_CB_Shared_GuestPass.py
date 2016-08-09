import copy
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

'''
'''
server_cfg_kv = {
    'AD': {
        'server_name': 'AD',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'rat.ruckuswireless.com',
    },
    'RADIUS': {
         'server_name': 'RADIUS',
         'server_addr': '192.168.0.252',
         'radius_auth_secret': '1234567890',
         'server_port': '1812',
    },
    'LDAP': {
         'server_name': 'LDAP',
         'server_addr': '192.168.0.252',
         'server_port': '389',
         'ldap_search_base': 'dc=example,dc=net',
         'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
         'ldap_admin_pwd': 'lab4man1',
    },
    'Local Database': {
        'server_name': 'Local Database',
    },
}

users_auth_kv = {
    'AD':
        {'username': 'ad.user',
         'password': 'ad.user'
        },

    'RADIUS':
        {'username': 'marketing.user',
         'password': 'marketing.user'
        },

    'LDAP':
        {'username': 'test.ldap.user',
         'password': 'test.ldap.user'
        },

    'Local Database':
        {'username': 'rat_guest_pass',
         'password': 'rat_guest_pass'
        },
}


def _gen_wlan_cfg(fcfg):
    wlan_list = []
    wlan_cfg = copy.deepcopy(fcfg)
    ssid = wlan_cfg['ssid'] + '-%s' % time.strftime("%H%M%S")
    time.sleep(1)
    wlan_cfg.update({'ssid': ssid})
    wlan_list.append(wlan_cfg)

    return wlan_list


def _gen_test_cfg_station(name, fcfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Station'
    for i in range(0, len(fcfg['sta_ip_list'])):
        common_name = name + ' - %s'
        common_name = common_name % ('sta%s' % (i + 1))
        test_cfgs.append(({'sta_ip_addr': fcfg['sta_ip_list'][i],
                           'sta_tag': 'sta%s' % (i + 1)},
                            test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_get_sta_wifi(name, fcfg, multi_login = False):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    for i in range(0, len(fcfg['sta_ip_list'])):
        if not multi_login:
            sta_id = 1
            if 0 < i:
                break

        else:
            sta_id = i + 1

        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % sta_id
        test_cfgs.append(({'sta_tag': 'sta%s' % sta_id},
                          test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_associate_station(name, fcfg, wlan_cfg_list,
                                    multi_login = False):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Associate_Station_1'
    for i in range(len(fcfg['sta_ip_list'])):
        if not multi_login:
            sta_id = 1
            if 0 < i:
                break

        else:
            sta_id = i + 1

        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % sta_id

        wlan_cfg = copy.deepcopy(wlan_cfg_list[0])
        test_cfgs.append(({'wlan_cfg': wlan_cfg,
                           'sta_tag': 'sta%s' % sta_id},
                           test_name, common_name, 0, False)
        )

    return test_cfgs


def _gen_test_cfg_create_server(name, server_cfg_list):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = name
    test_cfgs.append(({'auth_ser_cfg_list': server_cfg_list},
                      test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_remove_config(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = name
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_create_wlan(name, wlan_cfg_list):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Wlans'
    common_name = name
    test_cfgs.append(({'wlan_cfg_list': wlan_cfg_list},
                      test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_create_user(name, user_cfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Local_User'
    common_name = name
    test_cfgs.append(({'username': user_cfg['username'],
                       'password': user_cfg['password']},
                      test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_generate_cvs_profile(name, user_cfg, wlan_cfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Generate_GuestPass_CSV_Profile'
    common_name = name
    test_cfgs.append(({'username': user_cfg['username'],
                       'wlan_cfg': wlan_cfg},
                      test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_enable_shared_guest_pass(name, wlan, auth_svr):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Enable_Shared_Guest_Pass'
    common_name = name
    test_cfgs.append(({'wlan': wlan,
                       'auth_ser': auth_svr,
                       'username': users_auth_kv[auth_svr]['username'],
                       'password': users_auth_kv[auth_svr]['password']},
                      test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_verify_shared_guest_pass(name, wlan_cfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Verify_Shared_Guest_Pass'
    common_name = name
    test_cfgs.append(({'wlan_cfg': wlan_cfg,},
                       test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_download_guest_pass_profile(name, auth_svr):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Download_GuestPasses_Record'
    common_name = name
    test_cfgs.append(({'username': users_auth_kv[auth_svr]['username'],
                       'password': users_auth_kv[auth_svr]['password'],},
                       test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_parse_guest_pass_csv(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Parse_Guest_Passes_Record_File'
    common_name = name
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_verify_user(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Verify_Local_User'
    common_name = name
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_perform_guest_auth(name, fcfg, multi_login = False):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Perform_GuestPass_Authentication'
    for i in range(len(fcfg['sta_ip_list'])):
        if not multi_login:
            sta_id = 1
            if 0 < i:
                break

        else:
            sta_id = i + 1

        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % sta_id
        test_cfgs.append(({'sta_tag': 'sta%s' % sta_id},
                           test_name, common_name, 0, False)
        )

    return test_cfgs


def define_test_cfg(cfg, input_cfg):
    fcfg = {
        'sta_ip_list': [],
        'ap_sym_name_list': []
    }
    fcfg.update(cfg)

    test_cfgs = []

    wlan_cfg = input_cfg['wlan_cfg']
    wlan_cfg_list = _gen_wlan_cfg(wlan_cfg)

    common_name = '%s - Create Target Station' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_station(common_name, fcfg)


    common_name = '%s - Remove All Existing Config' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_remove_config(common_name)
    
    if input_cfg['auth_svr'] == 'Local Database':   
        common_name = '%s - Create Local User' % fcfg['ts_name']
        test_cfgs += _gen_test_cfg_create_user(
                         common_name, input_cfg['user_cfg']
                     )
    elif input_cfg['auth_svr'] == 'AD':
        common_name = '%s - Create AD Authentication Server' % fcfg['ts_name']
        test_cfgs += _gen_test_cfg_create_server(
                         common_name, [input_cfg['server_cfg']]
                     )
    elif input_cfg['auth_svr'] == 'LDAP':
        common_name = '%s - Create LDAP Authentication Server' % fcfg['ts_name']
        test_cfgs += _gen_test_cfg_create_server(
                         common_name, [input_cfg['server_cfg']]
                     )
    elif input_cfg['auth_svr'] == 'RADIUS':   
        common_name = '%s - Create RADIUS Authentication Server' % fcfg['ts_name']
        test_cfgs += _gen_test_cfg_create_server(
                         common_name, input_cfg['server_cfg']
                     )


    common_name = '%s - Create WLANs' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_create_wlan(
                    common_name, wlan_cfg_list
                 )


    input_cfg['use_profile'] = True
    common_name = '%s - Generate GuestPass CSV Profile' % fcfg['ts_name']
    if input_cfg.has_key('use_profile'):
        test_cfgs += _gen_test_cfg_generate_cvs_profile(
                         common_name, input_cfg['user_cfg'], wlan_cfg_list[0]
                     )


    common_name = '%s - Generate Shared GuestPass' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_enable_shared_guest_pass(
                     common_name, wlan_cfg_list[0]['ssid'],
                     input_cfg['auth_svr']
                 )


    common_name = '%s - Verify Shared GuestPass' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_verify_shared_guest_pass(
                     common_name, wlan_cfg_list[0]
                 )


    common_name = '%s - Download GuestPass Records' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_download_guest_pass_profile(
                     common_name, input_cfg['auth_svr']
                 )


    common_name = '%s - Parse GuestPass Records' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_parse_guest_pass_csv(
                     common_name
                 )


    common_name = '%s - Associate Target Station' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_associate_station(
                     common_name, fcfg, wlan_cfg_list,
                     input_cfg['multi_login']
                 )


    common_name = '%s - Perform Guest Authentication' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_perform_guest_auth(
                     common_name, fcfg, input_cfg['multi_login']
                 )


    common_name = '%s - Get Target Station Wifi Addresses' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_get_sta_wifi(
                     common_name, fcfg, input_cfg['multi_login']
                 )


    common_name = '%s - Cleanup testing environment' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_remove_config(common_name)

    return test_cfgs


def define_input_cfg():
    test_conf = dict(
        zd_ip_addr = '192.168.0.2',

        server_cfg = server_cfg_kv['RADIUS'],

        wlan_cfg = {
            'ssid': 'RAT-WLAN-GUESTPASS',
            'auth': 'open',
            'encryption': 'none',
            'type': 'guest',
        },

        multi_login = False,

        sta_ip_list = ['192.168.1.11', '192.168.1.12'],

        connection_timed_out = 5 * 1000, # in seconds
    )

    return test_conf

def get_selected_input(depot = [], num = 1, prompt = ""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select option: "

    selection = []
    for i in range(num):
        id = raw_input(prompt + '%s/%s: ' % (i + 1, num))
        try:
            val = depot[int(id)]

        except:
            val = ""

        if val:
            selection.append(val)
            
        if num == 1:
            break

    return selection


def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    auth_svr = get_selected_input(
                  [server for server in server_cfg_kv.iterkeys()], 1,
                  'Select Authentication Server '
                )[0]

    multi_login = raw_input("Multi-user Login (y/n)?: ").lower() == "y"


    input_cfg = define_input_cfg()
    wlan_cfg = copy.deepcopy(input_cfg['wlan_cfg'])


    input_cfg.update({
        'auth_svr': auth_svr,
        'server_cfg': server_cfg_kv[auth_svr],
        'wlan_cfg': wlan_cfg,
        'user_cfg': {'username': users_auth_kv[auth_svr]['username'],
                     'password': users_auth_kv[auth_svr]['password']
                     },
        'multi_login': multi_login,
    })

    ts_name = 'Shared Guest Pass Combination'
    ts = testsuite.get_testsuite(ts_name, 'Shared Guest Pass Combination',
                                 interactive_mode = True,
                                 combotest = True,)

    fcfg = {
        'ts_name': ts.name,
        'sta_ip_list': sta_ip_list,
        'ap_sym_name_list': active_ap_list,
    }

    test_cfgs = define_test_cfg(fcfg, input_cfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params,
                                 test_order, exc_level, is_cleanup) > 0:
            test_added += 1

        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)

