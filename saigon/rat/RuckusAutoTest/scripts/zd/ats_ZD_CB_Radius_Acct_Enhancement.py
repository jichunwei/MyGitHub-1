import copy
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

'''
'''
auth_method_list = ['open', 'EAP']
#auth_method_list = ['open', 'Shared', 'EAP']
encryption_method_list = ['none', 'WPA2', 'WEP-64', 'WEP-128']
#encryption_method_list = ['none', 'WPA', 'WPA2', 'WEP-64', 'WEP-128']
encryption_algorithm_list = ['AES']
#encryption_algorithm_list = ['TKIP', 'AES']

default_cfg = {
    'zd_ip_addr': "192.168.0.2",
    'shell_key': "!v54! HBVkKSL0EfIDaNhsv55rSVTtTjf5MFh@",
    'sta_ip_addr': "192.168.1.12",
    'server_ip_addr': "192.168.0.252",
    'server_netmask': "255.255.255.0",
    'des_ip': "192.168.0.252",
    'ping_timeout_ms': 150 * 1000,
    'check_status_timeout': 120,
    'failover_behavior': "service", #["service", "config"]
}

server_cfg_kv = {
    'IAS': {
        'server_addr': "192.168.0.240",
        'server_port': "18121",
    },
    'FreeRADIUS': {
         'server_addr': "192.168.0.232",
         'server_port': "1813",
    },
    'FreeRADIUS.2': {
         'server_addr': "192.168.0.252",
         'server_port': "1813",
    }
}

server_cfg = {
    'server_name': "RadiusAcct",
    'server_addr': server_cfg_kv['FreeRADIUS']['server_addr'],
    'server_port': server_cfg_kv['FreeRADIUS']['server_port'],
    'radius_acct_secret': "1234567890",
    'secondary_server_addr': server_cfg_kv['IAS']['server_addr'],
    'secondary_server_port': server_cfg_kv['IAS']['server_port'],
    'secondary_acct_secret': "1234567890",
    'primary_timeout': "3", # 3 seconds
    'failover_retries': "2", # 2 times
    'primary_reconnect': "2", # 5 minutes
}

user_cfg = {
    'username': 'ras.local.user',
    'password': 'ras.local.user',
}

wlan_cfg = {
    'ssid': "rat-radius-acct-enhanced",
    'auth': auth_method_list[1],
    'wpa_ver': encryption_method_list[1],
    'encryption': encryption_algorithm_list[0],
    'key_index': "" ,
    'key_string': "",
    'username': user_cfg['username'],
    'password': user_cfg['password'],
    'acct_svr': server_cfg['server_name'],
    'interim_update': "2" # 5 minutes
}


def _gen_wlan_cfg(fcfg):
    '''
    Adapter method to update each wlan_cfg and generate a list of wlan_cfg
    '''
    wlan_list = []
    wlan_cfg = copy.deepcopy(fcfg)
    ssid = wlan_cfg['ssid'] + '-%s' % time.strftime("%H%M%S")
    wlan_cfg.update({'ssid': ssid})

    wlan_list.append(wlan_cfg)

    return wlan_list


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


def _gen_test_cfg_create_server(name, server_cfg_list):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = name
    test_cfgs.append(({'auth_ser_cfg_list': server_cfg_list},
                        test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_remove_config(name, clean_up = False):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = name
    test_cfgs.append(({'do_full': False}, test_name, common_name, 0, clean_up))

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


def _gen_test_cfg_client_ping(name, fcfg, exec_level = 0):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = name + ' - %s' % 'sta1'
    test_cfgs.append(({'sta_tag': 'sta1',
                       'condition': 'allowed',
                       'target': '172.16.10.252',},
                        test_name, common_name, exec_level, False))

    return test_cfgs


def _gen_test_cfg_get_sta_wifi(name, fcfg, exec_level = 0):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    for i in range(0, len(fcfg['sta_ip_list'])):
        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % (i + 1)
        test_cfgs.append(({'sta_tag': 'sta%s' % (i + 1)},
                          test_name, common_name, exec_level, False))

    return test_cfgs


def _gen_test_cfg_associate_station(name, fcfg, wlan_cfg_list, exec_level = 0):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Associate_Station_1'
    for i in range(len(fcfg['sta_ip_list'])):
        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % (i + 1)

        test_cfgs.append((
            {'wlan_cfg': wlan_cfg_list[0],
             'sta_tag': 'sta%s' % (i + 1)},
             test_name, common_name, exec_level, False)
        )

    return test_cfgs


def _gen_test_cfg_station(name, fcfg, exec_level = 0):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Station'
    for i in range(0, len(fcfg['sta_ip_list'])):
        common_name = name + ' - %s'
        common_name = common_name % ('sta%s' % (i + 1))
        test_cfgs.append(({'sta_ip_addr': fcfg['sta_ip_list'][i],
                           'sta_tag': 'sta%s' % (i + 1)},
                            test_name, common_name, exec_level, False))

    return test_cfgs



def _gen_test_cfg_verify_radius_acct_enhancement(
        name, fcfg, wlan_cfg_list, testcase = "acct_status_type",
        negative_condition = "same_ip"):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Verify_Radius_Acct_Enhancement'
    common_name = name

    test_cfgs.append(({'tc2f': testcase,
                       'server_cfg': server_cfg,
                       'wlan_cfg': wlan_cfg_list[0],
                       'sta_tag': "sta1",
                       'failover_behavior': "service"},
                      test_name, common_name, 1, False))

    return test_cfgs


def _gen_test_verify_radius_acct_enhancement(
        name, fcfg, wlan_cfg_list, testcase = "acct_status_type"
    ):
    '''
    '''
    test_cfgs = []
    tc2d = {
        'acct_status_type': "RADIUS Accounting Status Start",
        'acct_session_time': "RADIUS Accounting Session Time",
        'acct_session_id': "RADIUS Accounting with new Session ID",
        'acct_multi_session_id': "RADIUS Accounting with new Multi-Session ID",
        'acct_ruckus_sta_rssi': "Ruckus-Sta-RSSI",
        'acct_new_interim_update': "Interim setting",
        'acct_backup_accounting': "Backup accounting server",


    }[testcase]
    if name != '':
        common_name = '%s [%s]' % (name, tc2d)
    else:
        common_name = '[%s]' %tc2d
    test_cfgs += _gen_test_cfg_verify_radius_acct_enhancement(
        common_name, fcfg, wlan_cfg_list, testcase
    )

    return test_cfgs


def define_test_cfg(cfg, input_cfg):
    fcfg = {
        'sta_ip_list': [],
    }
    fcfg.update(cfg)

    test_cfgs = []

    wlan_cfg = input_cfg['wlan_cfg']
    wlan_cfg_list = _gen_wlan_cfg(wlan_cfg)
    
    #@author: Liang Aihua,@since: 201-12-1,@change: correct test case name.
    #common_name = '%s - Create target station' % fcfg['ts_name']
    common_name = 'Create target station'
    test_cfgs += _gen_test_cfg_station(common_name, fcfg)


    #common_name = '%s - Remove all existing config' % fcfg['ts_name']
    common_name = 'Remove all existing config'
    test_cfgs += _gen_test_cfg_remove_config(common_name)


    #common_name = '%s - Create Local User' % fcfg['ts_name']
    common_name = 'Create Local User'
    test_cfgs += _gen_test_cfg_create_user(
        common_name, input_cfg['user_cfg']
    )


    #common_name = '%s - Create Radius Accounting server' % fcfg['ts_name']
    common_name = 'Create Radius Accounting server'
    test_cfgs += _gen_test_cfg_create_server(
        common_name, [input_cfg['server_cfg']]
    )


    #common_name = '%s - Create WLANs' % fcfg['ts_name']
    common_name = 'Create WLANs'
    test_cfgs += _gen_test_cfg_create_wlan(
        common_name, wlan_cfg_list
    )


    #common_name = '%s - Associate target station' % fcfg['ts_name']
    common_name = 'Associate target station'
    test_cfgs += _gen_test_cfg_associate_station(
        common_name, fcfg, wlan_cfg_list,
    )


    #common_name = '%s - Get target station Wifi addresses' % fcfg['ts_name']
    common_name = 'Get target station Wifi addresses'
    test_cfgs += _gen_test_cfg_get_sta_wifi(
        common_name, fcfg
    )


    #common_name = '%s - Client Ping Dest' % fcfg['ts_name']
    common_name = 'Client Ping Dest'
    test_cfgs += _gen_test_cfg_client_ping(common_name, fcfg)


    #common_name = '%s - ' % fcfg['ts_name']
    common_name = ''
    test_cfgs += _gen_test_verify_radius_acct_enhancement(
        common_name, fcfg, wlan_cfg_list, "acct_status_type"
    )

    #common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_radius_acct_enhancement(
        common_name, fcfg, wlan_cfg_list, "acct_session_time"
    )

    #@author: Liang Aihua,@since: 2014-12-1,@change: Remove these cases for roaming can't be realized sutomatic.
    #common_name = '%s - ' % fcfg['ts_name']
    #test_cfgs += _gen_test_verify_radius_acct_enhancement(
    #    common_name, fcfg, wlan_cfg_list, "acct_session_id"
    #)

    #common_name = '%s - ' % fcfg['ts_name']
    #test_cfgs += _gen_test_verify_radius_acct_enhancement(
    #    common_name, fcfg, wlan_cfg_list, "acct_multi_session_id"
    #)

    #common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_radius_acct_enhancement(
        common_name, fcfg, wlan_cfg_list, "acct_ruckus_sta_rssi"
    )
    

    #common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_radius_acct_enhancement(
        common_name, fcfg, wlan_cfg_list, "acct_new_interim_update"
    )

    #common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_radius_acct_enhancement(
        common_name, fcfg, wlan_cfg_list, "acct_backup_accounting"
    )

    #common_name = '%s - Cleanup testing environment' % fcfg['ts_name']
    common_name = 'Cleanup testing environment'
    test_cfgs += _gen_test_cfg_remove_config(common_name, True)

    return test_cfgs


def define_input_cfg():
    test_conf = {
        'server_cfg': server_cfg,
        'user_cfg': user_cfg,
        'wlan_cfg': wlan_cfg,
    }

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

    return selection


def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    auth_method = get_selected_input(
        auth_method_list, 1,
        'Select Authentication Method '
    )[0]

    encryption_method = get_selected_input(
        encryption_method_list, 1,
        'Select Encryption Method '
    )[0]

    encryption_algorithm = "none"
    if encryption_method in ['WPA', 'WPA2']:
        encryption_algorithm = get_selected_input(
            encryption_algorithm_list, 1,
            'Select Encryption Algorithm '
        )[0]

    server_addr_default = "192.168.0.252"
    server_addr = raw_input(
        "Accounting Primary Server address [%s]: " %
        server_addr_default
    )
    server_addr = server_addr or server_addr_default

    server_port_default = "1813"
    server_port = raw_input(
        "Accounting Primary Server port [%s]: " %
        server_port_default
    )
    server_port = server_port or server_port_default

    radiusd_name_default = "radiusd"
    radiusd_name = raw_input(
        "Accounting Primary Server radiusd service name [%s]: " %
        radiusd_name_default
    )
    radiusd_name = radiusd_name or radiusd_name_default


    secondary_server_addr_default = "192.168.0.248"
    diff_radiusd = False
    while not diff_radiusd:
        secondary_server_addr = raw_input(
            "Accounting Secondary Server address [%s]: " %
            secondary_server_addr_default
        )
        secondary_server_addr = secondary_server_addr or secondary_server_addr_default

        if secondary_server_addr != server_addr:
            diff_radiusd = True


    secondary_server_port_default = "1813"
    secondary_server_port = raw_input(
        "Accounting Secondary Server port [%s]: " %
        secondary_server_port_default
    )
    secondary_server_port = secondary_server_port or secondary_server_port_default

    secondary_radiusd_name_default = "radiusd2"
    secondary_radiusd_name = raw_input(
        "Accounting Secondary Server radiusd service name [%s]: " %
        secondary_radiusd_name_default
    )
    secondary_radiusd_name = secondary_radiusd_name or secondary_radiusd_name_default


    server_cfg.update({
        'server_addr': server_addr,
        'server_port': server_port,
        'radiusd_name': radiusd_name,
        'secondary_server_addr': secondary_server_addr,
        'secondary_server_port': secondary_server_port,
        'secondary_radiusd_name': secondary_radiusd_name,
    })

    input_cfg = define_input_cfg()

    wlan_cfg = copy.deepcopy(input_cfg['wlan_cfg'])

    wlan_cfg.update({
        'ssid': 'RAT-WLAN-%s-%s' %
                    (auth_method, encryption_method,
                     ),
        'auth': auth_method,
        'encryption': encryption_algorithm,
        'wpa_ver': encryption_method,
    })

    input_cfg.update({
        'wlan_cfg': wlan_cfg,
    })

    #@author: Liang Aihua,@change: correct the test case name,@since: 2014-12-01
    #ts_name = 'Radius Acct Enhancement'
    ts_name = 'Radius Accounting Enhancement'
    ts = testsuite.get_testsuite(
        ts_name, '%s - Combo Test' % ts_name,
        interactive_mode = True,
        combotest = True,
    )

    fcfg = {
        'ts_name': ts.name,
        'sta_ip_list': sta_ip_list,
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

