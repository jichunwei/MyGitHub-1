import copy
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

'''
'''
auth_list = ['EAP'] # only 802.1x EAP is being tested
encryption_list = ['Auto', 'AES'] # per test cases requirement #Chico, 2015-5-13, no support WPA/TKIP any more
wpa_ver_list = ['WPA2',]
tunnel_mode = False
ap_tag = 'ap_dvlan'

server_cfg_kv = {
    'IAS': {
        'server_name': 'IAS',
        'server_addr': '192.168.0.250',
        'radius_auth_secret': '1234567890',
        'server_port': '18120',
    },
    'FreeRADIUS': {
         'server_name': 'FreeRADIUS',
         'server_addr': '192.168.0.252',
         'radius_auth_secret': '1234567890',
         'server_port': '1812',
    }
}

radio = {'2.4': 'ng', '5.0': 'na'}

users_vlan_kv = {
    '10':
        {'username': 'finance.user',
         'password': 'finance.user',
        },

    '20':
        {'username': 'marketing.user',
         'password': 'marketing.user',
        },

    '512':
        {'username': 'vlan512.user',
         'password': 'vlan512.user',
        },

    '1024':
        {'username': 'vlan1024.user',
         'password': 'vlan1024.user',
        },

    '2048':
        {'username': 'vlan2048.user',
         'password': 'vlan2048.user',
        },

    '4069':
        {'username': 'vlan4069.user',
         'password': 'vlan4069.user',
        },
}


def _gen_wlan_cfg(fcfg):
    '''
    Adapter method to update each wlan_cfg and generate a list of wlan_cfg
    '''
    wlan_list = []
    for i in range(2): #two WLANs
        wlan_cfg = copy.deepcopy(fcfg)
        ssid = wlan_cfg['ssid'] + '-%s' % time.strftime("%H%M%S")
        time.sleep(1)
        wlan_cfg.update({'ssid': ssid})

        wlan_list.append(wlan_cfg)

    return wlan_list


def _gen_test_cfg_restore(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Restore'
    common_name = name
    test_cfgs.append(({},test_name, common_name, 2, False))

    return test_cfgs


def _gen_test_cfg_backup(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Backup'
    common_name = name
    test_cfgs.append(({},test_name, common_name, 1, False))

    return test_cfgs


def _gen_test_cfg_client_reconnect(name, wlan_cfg_list, same_wlan, fcfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Client_Reconnect'
    common_name = name + ' - sta1'
    test_cfgs.append(({'sta_tag': 'sta1',
                       'ssid': wlan_cfg_list[0]['ssid'],},
                        test_name, common_name, 2, False))

    if 2 == len(fcfg['sta_ip_list']):
        test_name = 'CB_ZD_Client_Reconnect'
        common_name = name + ' - sta2'
        
        if same_wlan:
            ssid = wlan_cfg_list[0]['ssid']
        else:
            ssid = wlan_cfg_list[1]['ssid']
        test_cfgs.append(({'sta_tag': 'sta2',
                           'ssid': ssid,},
                            test_name, common_name, 2, False))
                     

    return test_cfgs


def _gen_test_cfg_verify_client(name, vlan_list, fcfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Verify_Active_Client'
    common_name = name + ' - Brief info - sta1'
    test_cfgs.append(({'sta_tag': 'sta1',
                       'info_cat': 'brief',
                       'expected_info': {'vlan': vlan_list[0]},},
                        test_name, common_name, 2, False))


    if 2 == len(fcfg['sta_ip_list']):
        test_name = 'CB_ZD_Verify_Active_Client'
        common_name = name + ' - Detail info - sta2'
        test_cfgs.append(({'sta_tag': 'sta2',
                           'info_cat': 'detail',
                           'expected_info': {'vlan': vlan_list[1]},},
                            test_name, common_name, 2, False))

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


def _gen_test_cfg_client_ping(name, fcfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = name + ' - %s' % 'sta1'
    test_cfgs.append(({'sta_tag': 'sta1',
                       'condition': 'allowed',
                       'target': '172.16.10.252',},
                        test_name, common_name, 2, False))

    if 2 == len(fcfg['sta_ip_list']):
        common_name = name + ' - %s' % 'sta2'
        test_cfgs.append(({'sta_tag': 'sta2',
                           'condition': 'allowed',
                           'target': 'sta1',},
                            test_name, common_name, 2, False))

    return test_cfgs


def _gen_test_cfg_server_ping(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Server_Ping_Client'
    common_name = name + ' - %s' % 'sta1'
    test_cfgs.append(({'condition': 'allowed',
                       'target': 'sta1',},
                        test_name, common_name, 2, False))

    return test_cfgs



def _gen_test_cfg_get_sta_wifi(name, fcfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    for i in range(0, len(fcfg['sta_ip_list'])):
        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % (i + 1)
        test_cfgs.append(({'sta_tag': 'sta%s' % (i + 1)},
                          test_name, common_name, 2, False))

    return test_cfgs


def _gen_test_cfg_associate_station(name, fcfg, wlan_cfg_list,
                                    same_wlan = True,
                                    vlan_list = ['10', '20']):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Associate_Station_1'
    for i in range(len(fcfg['sta_ip_list'])):
        common_name = name + ' - %s'
        common_name = common_name % 'sta%s' % (i + 1)

        if i != 0 and same_wlan is False:
            wcfg = copy.deepcopy(wlan_cfg_list[i])
        else:
            wcfg = copy.deepcopy(wlan_cfg_list[0])

        wcfg.update({
            'username': users_vlan_kv[vlan_list[i]]['username'],
            'password': users_vlan_kv[vlan_list[i]]['password']}
        )

        if i == 0:
            test_level = 1
        else:
            test_level = 2
        test_cfgs.append((
            {'wlan_cfg': wcfg,
             'sta_tag': 'sta%s' % (i + 1)},
             test_name, common_name, test_level, False)
        )

    return test_cfgs


def _gen_test_cfg_ap_radio(name, fcfg, ap_radio = 'ng'):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = name + ' - Disable WLAN Service'
    test_cfgs.append(({'all_ap_mac_list': fcfg['ap_mac_list'],
                       'cfg_type': 'init'},
                        test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = name + ' - Enable WLAN Service - Radio mode %s' % ap_radio
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg': {'radio': ap_radio,
                                  'wlan_service': True
                                  },
                       'cfg_type': 'config',
                        },
                        test_name, common_name, 0, False))

    return test_cfgs


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


def _gen_test_cfg_ap_policy(name, max_clients = 100, cfg_type = 'init'):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Config_AP_Policy'
    test_cfgs.append(({'ap_tag': ap_tag,
                       'max_clients': max_clients,
                       'cfg_type': cfg_type},
                      test_name, name, 0, False))

    return test_cfgs


def _gen_test_cfg_active_ap(name, fcfg):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Create_Active_AP'
    test_cfgs.append(({'active_ap': fcfg['ap_sym_name_list'][0],
                       'ap_tag': ap_tag},
                        test_name, name, 0, False))

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

    common_name = 'Remove all configuration'
    test_cfgs += _gen_test_cfg_remove_config(common_name)


    common_name = 'Create target station'
    test_cfgs += _gen_test_cfg_station(common_name, fcfg)


    common_name = 'Create active AP'
    test_cfgs += _gen_test_cfg_active_ap(
                     common_name, fcfg,
                 )


    common_name = 'Config AP Policy - Backup AP Policy'
    test_cfgs += _gen_test_cfg_ap_policy(
                     common_name, cfg_type = 'init'
                 )


    client_num = len(fcfg['sta_ip_list'])
    common_name = 'Config AP Policy - Limit %s clients per AP ' % client_num
    test_cfgs += _gen_test_cfg_ap_policy(
                     common_name, max_clients = client_num, cfg_type = 'config'
                 )


    common_name = 'Create Radius authentication server'
    test_cfgs += _gen_test_cfg_create_server(
                     common_name, [input_cfg['server_cfg']]
                 )


    common_name = 'Create WLANs'
    test_cfgs += _gen_test_cfg_create_wlan(
                    common_name, wlan_cfg_list
                 )


    common_name = 'Config AP Radio'
    test_cfgs += _gen_test_cfg_ap_radio(
                     common_name, fcfg,
                     input_cfg['ap_radio']
                 )


    test_name = '[DVLAN client association]'

    common_name = '%sAssociate target station' % test_name
    test_cfgs += _gen_test_cfg_associate_station(
                     common_name, fcfg,
                     wlan_cfg_list,
                     input_cfg['same_wlan'],
                     input_cfg['vlan_list']
                 )


    common_name = '%sGet target station Wifi addresses' % test_name
    test_cfgs += _gen_test_cfg_get_sta_wifi(
                     common_name, fcfg
                 )


    common_name = '%sClient Ping Destination' % test_name
    test_cfgs += _gen_test_cfg_client_ping(common_name, fcfg)


    common_name = '%sServer Ping Station' % test_name
    test_cfgs += _gen_test_cfg_server_ping(common_name)


    common_name = '%sVerify Active Client' % test_name
    test_cfgs += _gen_test_cfg_verify_client(
                     common_name,
                     input_cfg['vlan_list'],fcfg
                 )

    test_name = '[DVLAN backup restore]'

    common_name = '%sPerform ZD Backup' % test_name
    test_cfgs += _gen_test_cfg_backup(common_name)


    step_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD after backing up' % test_name
    test_cfgs.append(({}, step_name, common_name, 2, False))


    common_name = '%sPerform ZD Restore' % test_name
    test_cfgs += _gen_test_cfg_restore(common_name)


    for i in range(len(fcfg['sta_ip_list'])):
        step_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove all WlANs from sta%s' % (test_name, (i+1))
        test_cfgs.append(({'sta_tag': 'sta%s' % (i+1)}, step_name, common_name, 2, False))
    

    common_name = '%sAssociate target station' % test_name
    test_cfgs += _gen_test_cfg_associate_station(
                     common_name, fcfg,
                     wlan_cfg_list,
                     input_cfg['same_wlan'],
                     input_cfg['vlan_list']
                 )


    common_name = '%sGet target station Wifi addresses' % test_name
    test_cfgs += _gen_test_cfg_get_sta_wifi(
                     common_name, fcfg
                 )

    common_name = '%sClient Ping Dest' % test_name
    test_cfgs += _gen_test_cfg_client_ping(common_name, fcfg)


    common_name = '%sServer Ping Station' % test_name
    test_cfgs += _gen_test_cfg_server_ping(common_name)


    common_name = '%sVerify Active Client' % test_name
    test_cfgs += _gen_test_cfg_verify_client(
                     common_name,
                     input_cfg['vlan_list'],
                     fcfg
                 )

    common_name = 'Config AP Policy - Restore AP Policy'
    test_cfgs += _gen_test_cfg_ap_policy(
                     common_name, cfg_type = 'teardown'
                 )

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config AP Radio - Enable WLAN Service of all APs'
    test_cfgs.append(({'cfg_type': 'teardown',
                       'all_ap_mac_list': fcfg['ap_mac_list']}, 
                       test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA server setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    return test_cfgs

def define_input_cfg():
    test_conf = dict(
        zd_ip_addr = '192.168.0.2',

        server_cfg = server_cfg_kv['FreeRADIUS'],

        wlan_cfg = {
            'ssid': 'RAT-WLAN-%s-%s-%s' %
                        (auth_list[0], encryption_list[0],
                         wpa_ver_list[0],
                         ),
            'auth': auth_list[0],
            'encryption': encryption_list[0],
            'wpa_ver': wpa_ver_list[0],
            'auth_svr': server_cfg_kv['FreeRADIUS']['server_name'],
            'username': users_vlan_kv['10']['username'],
            'password': users_vlan_kv['10']['password'],
            'key_string': '',
            'dvlan': True,
            'do_tunnel': tunnel_mode,
        },

        sta_ip_list = ['192.168.1.11', '192.168.1.12'],

        ap_radio = radio['2.4'],

        same_wlan = False,

        vlan_list = ['10', '20'],

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

    return selection


def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    ap_mac_list = tbcfg['ap_mac_list']

    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    target_sta_radio = testsuite.get_target_sta_radio()

    aaa_server = get_selected_input(
                  [server for server in server_cfg_kv.iterkeys()], 1,
                  'Select AAA Server '
                )[0]

    encryption = get_selected_input(
                     encryption_list, 1,
                     'Select Encryption '
                 )[0]
    wpa_ver = get_selected_input(
                  wpa_ver_list, 1,
                  'Select WPA version '
              )[0]
    tunnel_mode = raw_input("Tunnel mode (y/n)?: ").lower() == "y"
    same_wlan = raw_input("Same WLAN (y/n)?: ").lower() == "y"

    vlan_list = get_selected_input(
                  [vlan for vlan in users_vlan_kv.iterkeys()], 2,
                  'Select VLAN ID '
                )

    input_cfg = define_input_cfg()
    wlan_cfg = copy.deepcopy(input_cfg['wlan_cfg'])

    wlan_cfg.update({
        'ssid': 'RAT-WLAN-%s-%s-%s' %
                    (auth_list[0], encryption,
                     wpa_ver,
                     ),
        'auth': auth_list[0],
        'encryption': encryption,
        'wpa_ver': wpa_ver,
        'auth_svr': server_cfg_kv[aaa_server]['server_name'],
        'username': users_vlan_kv[vlan_list[0]]['username'],
        'password': users_vlan_kv[vlan_list[0]]['password'],
        'key_string': '',
        'dvlan': True,
        'do_tunnel': tunnel_mode,
    })
    #Chico, 2015-5-15, fix bug ZF-12507, remove TKIP
    station_encryption_list=['AES','TKIP']
    if wlan_cfg['encryption']=='Auto':
        import random
        wlan_cfg.update(sta_encryption=station_encryption_list[random.randrange(len(station_encryption_list))])
    #Chico, 2015-5-15, fix bug ZF-12507, remove TKIP

    input_cfg.update({
        'server_cfg': server_cfg_kv[aaa_server],
        'wlan_cfg': wlan_cfg,
        'ap_radio': target_sta_radio,
        'same_wlan': same_wlan,
        'vlan_list': vlan_list,
        'encryption': encryption,
        'wpa_ver': wpa_ver,
    })

    ts_name = 'DVLAN - %s' % target_sta_radio
    ts = testsuite.get_testsuite(ts_name, ts_name,
                                 interactive_mode = True,
                                 combotest = True,)

    fcfg = {
        'ts_name': ts.name,
        'sta_ip_list': sta_ip_list,
        'ap_sym_name_list': active_ap_list,
        'ap_mac_list': ap_mac_list,
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

