import copy
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

'''
'''
auth_list = ['EAP'] # only 802.1x EAP is being tested
#encryption_list = ['TKIP', 'AES'] # per test cases requirement
encryption_list = ['AES']
#wpa_ver_list = ['WPA', 'WPA2']
wpa_ver_list = ['WPA2']

server_cfg = {
    'server_name': "RadiusAcct",
    'server_addr': "192.168.0.232",
    'server_port': "1813",
    'radiusd_name': "radiusd1",
    'radius_acct_secret': "1234567890",
    'secondary_server_addr': "192.168.0.222",
    'secondary_server_port': "1646",
    'secondary_radiusd_name': "radiusd2",
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
    'ssid': "rat-backup-acct-server",
    'auth': auth_list[0],
    'wpa_ver': wpa_ver_list[0],
    'encryption': encryption_list[0],
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
    test_cfgs.append(({}, test_name, common_name, 0, clean_up))

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


def _gen_test_cfg_upgrade(name, fcfg, exec_level = 1, clean_up = False):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Upgrade'
    common_name = name
    test_cfgs.append(({'image_file_path': fcfg['image_file_path'],
                       'build_stream': fcfg['build_stream'],
                       'build_number': fcfg['build_number'],
                       'force_upgrade': fcfg['force_upgrade']},
                      test_name, common_name, exec_level, clean_up))

    return test_cfgs


def _gen_test_cfg_verify_backup_acct(name, fcfg, wlan_cfg_list, testcase = "primary_timeout", exec_level = 1):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Verify_Backup_Accounting'
    common_name = name

    test_cfgs.append(({'tc2f': testcase,
                       'server_cfg': server_cfg,
                       'wlan_cfg': wlan_cfg_list[0],
                       'failover_behavior': "service", },
                      test_name, common_name, exec_level, False))

    return test_cfgs


def _gen_test_backup_accounting_with_dataplane(
        name, fcfg, wlan_cfg_list, testcase = "primary_timeout"
    ):
    '''
    '''
    test_cfgs = []
    tc2d = {
        'primary_timeout': "Failover from Primary to Backup Accounting server",
        'primary_reconnect': "Failover from Backup to Primary Accounting server",
        'server_outage': "Primary / Backup Accounting server are gone",
        'image_upgrade': "Restore previous configuration when Imaged upgrade",
    }[testcase]
    name = "[%s] - " % tc2d + testcase
    
    exec_level = 1
    if testcase == "image_upgrade":
        common_name = '%s - Upgrade ZD' % name
        test_cfgs += _gen_test_cfg_upgrade(common_name, fcfg)
        exec_level = 2


    common_name = '%s - Verify Failover event' % name
    test_cfgs += _gen_test_cfg_verify_backup_acct(common_name, fcfg, wlan_cfg_list, testcase, exec_level)

    common_name = '%s - Create target station' % name
    test_cfgs += _gen_test_cfg_station(common_name, fcfg, 2)

    common_name = '%s - Associate target station' % name
    test_cfgs += _gen_test_cfg_associate_station(common_name, fcfg, wlan_cfg_list, 2)

    common_name = '%s - Get target station Wifi addresses' % name
    test_cfgs += _gen_test_cfg_get_sta_wifi(common_name, fcfg, 2)

    common_name = '%s - Client Ping Dest' % name
    test_cfgs += _gen_test_cfg_client_ping(common_name, fcfg, 2)
    
    if testcase == "image_upgrade":
        common_name = '%s - Restore ZD Firmware' % name
        test_cfgs += _gen_test_cfg_upgrade(common_name, fcfg, exec_level, clean_up = True)

    return test_cfgs


def define_test_cfg(cfg, input_cfg):
    fcfg = {
        'sta_ip_list': [],
    }
    fcfg.update(cfg)

    test_cfgs = []

    wlan_cfg = input_cfg['wlan_cfg']
    wlan_cfg_list = _gen_wlan_cfg(wlan_cfg)

    common_name = '%s - Create target station' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_station(common_name, fcfg)


    common_name = '%s - Remove all existing config' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_remove_config(common_name)


    common_name = '%s - Create Local User' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_create_user(
        common_name, input_cfg['user_cfg']
    )

    common_name = '%s - Create Radius authentication server' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_create_server(
        common_name, [input_cfg['server_cfg']]
    )


    common_name = '%s - Create WLANs' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_create_wlan(
        common_name, wlan_cfg_list
    )


    common_name = '%s - Associate target station' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_associate_station(
        common_name, fcfg, wlan_cfg_list,
    )


    common_name = '%s - Get target station Wifi addresses' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_get_sta_wifi(
        common_name, fcfg
    )


    common_name = '%s - Client Ping Dest' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_client_ping(common_name, fcfg)


    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_backup_accounting_with_dataplane(
        common_name, fcfg, wlan_cfg_list, "primary_timeout"
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_backup_accounting_with_dataplane(
        common_name, fcfg, wlan_cfg_list, "primary_reconnect"
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_backup_accounting_with_dataplane(
        common_name, fcfg, wlan_cfg_list, "server_outage"
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_backup_accounting_with_dataplane(
        common_name, fcfg, wlan_cfg_list, "image_upgrade"
    )

    common_name = '%s - Cleanup testing environment' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_remove_config(common_name, clean_up = True)

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

    radiusd_name_default = "radiusd1"
    radiusd_name = raw_input(
        "Accounting Primary Server Radius service [%s]: " %
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
        "Accounting Secondary Server Radius service [%s]: " %
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

    image_file_path = raw_input("ZD Upgrade image_file_path: ")
    image_file_path = image_file_path or ""

    build_stream = raw_input("ZD Upgrade build_stream: ")
    build_stream = build_stream or ""

    build_number = raw_input("ZD Upgrade build_number: ")
    build_number = build_number or ""

    force_upgrade = raw_input("ZD Upgrade force_upgrade (y/n)?: ").lower() == "y"


    input_cfg = define_input_cfg()

    ts_name = 'Backup Accounting server'
    ts = testsuite.get_testsuite(
        ts_name, '%s - Combo Test' % ts_name,
        interactive_mode = True,
        combotest = True,
    )

    fcfg = {
        'ts_name': ts.name,
        'sta_ip_list': sta_ip_list,
        'image_file_path': image_file_path,
        'build_stream': build_stream,
        'build_number': build_number,
        'force_upgrade': force_upgrade,
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

