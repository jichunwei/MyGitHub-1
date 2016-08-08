'''
Description:
    support: Single band/Dual band AP.
    1). Create a station.
    2). Create an active ap[Single band/Dual band AP].
    3). Create a user account[Local User/LDAP User/AD User/Radius User].
    4). Create a guest policy.
    5). Create a WLAN with/without tunnel-enabled or vlan-enabled.
    6). Verify the guest policy on ZD.
    7). Generate a Guest Pass with the user account.
    8). Associate ssid to station.
    9). Verify the expected subnet by the station be got.
    9). Verify the station info on ZD.
    10).Ping to target server from station befor perform guestpass auth.
    11).Verify the guest policy is corrected.
    12).Perform the guestpass auth with the redirect page from the station.
    13).Ping to target server from station after perform guestpass auth.
        [if it have restricted subnet list, ping the restricted subnet.]
    14).Verify the station info on ZD.
    15).Verify the station traffic is the corrected behavior.

Created on 2011-7-6
@author: jluh@ruckuswireless.com
'''
import re
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

'''
'''
user_cfg_kv = {
    'AD User': {
        'server_name': 'AD User',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'rat.ruckuswireless.com',
        'username': 'ad.user',
        'password': 'ad.user'
    },
    'RADIUS User': {
         'server_name': 'RADIUS User',
         'server_addr': '192.168.0.252',
         'radius_auth_secret': '1234567890',
         'server_port': '1812',
         'username': 'ras.local.user',
         'password': 'ras.local.user'
    },
    'LDAP User': {
         'server_name': 'LDAP User',
         'server_addr': '192.168.0.252',
         'server_port': '389',
         'ldap_search_base': 'dc=example,dc=net',
         'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
         'ldap_admin_pwd': 'lab4man1',
         'username': 'test.ldap.user',
         'password': 'test.ldap.user'
    },
    'Local User': {
        'server_name': 'Local Database',
        'username': 'rat_guest_pass',
        'password': 'rat_guest_pass'
    },
}

wlans_cfg = [('Open System', {'ssid': "open-wlan-guest-%s" % (time.strftime("%H%M%S")),
                              'auth': "open",
                              'wpa_ver': "",
                              'encryption': "none",
                              'sta_auth': "open",
                              'sta_wpa_ver': "",
                              'sta_encryption': "none",
                              'auth_svr': '',
                              'type': 'guest',
                              'key_index': "",
                              'key_string': "",
                              'username': "",
                              'password': "",
                              'ras_addr': "",
                              'ras_port': "",
                              'ras_secret': "",
                              'use_radius': False,
                              'do_tunnel': False,
                              'dvlan': None,
                              'vlan_id': None,
                            }),
#Chico@2014-6-24, WPA not supported yet from 9.8.0.0. ZF-8338
#          ('WPA PSK TKIP', {'ssid': "wpa-tkip-wlan-web-%s" % (time.strftime("%H%M%S")),
#                              'auth': "PSK",
#                              'wpa_ver': "WPA",
#                              'encryption': "TKIP",
#                              'sta_auth': "PSK",
#                              'sta_wpa_ver': "WPA",
#                              'sta_encryption': "TKIP",
#                              'auth_svr': '',
#                              'type': 'guest',                              
#                              'key_index': "",
#                              'key_string': utils.make_random_string(63, "alnum"),
#                              'username': "",
#                              'password': "",
#                              'ras_addr': "",
#                              'ras_port': "",
#                              'ras_secret': "",
#                              'use_radius': False,
#                              'do_tunnel': None,
#                              'dvlan': None,
#                              'vlan_id': None,
#                            }),
#            ('WPA PSK AES', {'ssid': "wpa-aes-wlan-web-%s" % (time.strftime("%H%M%S")),
#                             'auth': "PSK",
#                             'wpa_ver': "WPA",
#                             'encryption': "AES",
#                             'sta_auth': "PSK",
#                             'sta_wpa_ver': "WPA",
#                             'sta_encryption': "AES",
#                             'auth_svr': '',
#                             'type': 'guest',
#                             'key_index': "",
#                             'key_string': utils.make_random_string(63, "alnum"),
#                             'username': "",
#                             'password': "",
#                             'ras_addr': "",
#                             'ras_port': "",
#                             'ras_secret': "",
#                             'use_radius': False,
#                             'do_tunnel': None,
#                             'dvlan': None,
#                             'vlan_id': None,
#                            }),
#            ('WPA PSK Auto - STA WPA TKIP', {'ssid': "wpa-auto-sta-tkip-%s" % (time.strftime("%H%M%S")),
#                                             'auth': "PSK",
#                                             'wpa_ver': "WPA",
#                                             'encryption': "Auto",
#                                             'sta_auth': "PSK",
#                                             'sta_wpa_ver': "WPA",
#                                             'sta_encryption': "TKIP",
#                                             'auth_svr': '',
#                                             'type': 'guest',
#                                             'key_index': "",
#                                             'key_string': utils.make_random_string(63, "alnum"),
#                                             'username': "",
#                                             'password': "",
#                                             'ras_addr': "",
#                                             'ras_port': "",
#                                             'ras_secret': "",
#                                             'use_radius': False,
#                                             'do_tunnel': None,
#                                             'dvlan': None,
#                                             'vlan_id': None,
#                                             }),
#             ('WPA PSK Auto - STA WPA AES', {'ssid': "wpa-auto-sta-aes-%s" % (time.strftime("%H%M%S")),
#                                             'auth': "PSK",
#                                             'wpa_ver': "WPA",
#                                             'encryption': "Auto",
#                                             'sta_auth': "PSK",
#                                             'sta_wpa_ver': "WPA",
#                                             'sta_encryption': "AES",
#                                             'auth_svr': '',
#                                             'type': 'guest',
#                                             'key_index': "",
#                                             'key_string': utils.make_random_string(63, "alnum"),
#                                             'username': "",
#                                             'password': "",
#                                             'ras_addr': "",
#                                             'ras_port': "",
#                                             'ras_secret': "",
#                                             'use_radius': False,
#                                             'do_tunnel': None,
#                                             'dvlan': None,
#                                             'vlan_id': None,
#                                             }),
#            ('WPA2 PSK TKIP', {'ssid': "wpa2-tkip-wlan-web-%s" % (time.strftime("%H%M%S")),
#                               'auth': "PSK",
#                               'wpa_ver': "WPA2",
#                               'encryption': "TKIP",
#                               'sta_auth': "PSK",
#                               'sta_wpa_ver': "WPA2",
#                               'sta_encryption': "TKIP",
#                               'auth_svr': '',
#                               'type': 'guest',
#                               'key_index': "",
#                               'key_string': utils.make_random_string(63, "alnum"),
#                               'username': "",
#                               'password': "",
#                               'ras_addr': "",
#                               'ras_port': "",
#                               'ras_secret': "",
#                               'use_radius': False,
#                               'do_tunnel': None,
#                               'dvlan': None,
#                               'vlan_id': None,
#                              }),
            ('WPA2 PSK AES', {'ssid': "wpa2-aes-wlan-web-%s" % (time.strftime("%H%M%S")),
                              'auth': "PSK",
                              'wpa_ver': "WPA2",
                              'encryption': "AES",
                              'sta_auth': "PSK",
                              'sta_wpa_ver': "WPA2",
                              'sta_encryption': "AES",
                              'auth_svr': '',
                              'type': 'guest',
                              'key_index': "",
                              'key_string': utils.make_random_string(63, "alnum"),
                              'username': "",
                              'password': "",
                              'ras_addr': "",
                              'ras_port': "",
                              'ras_secret': "",
                              'use_radius': False,
                              'do_tunnel': None,
                              'dvlan': None,
                              'vlan_id': None,
                            }),
            ('WPA2 PSK Auto - STA WPA2 TKIP', {'ssid': "wpa2-auto-sta-tkip-%s" % (time.strftime("%H%M%S")),
                                               'auth': "PSK",
                                               'wpa_ver': "WPA2",
                                               'encryption': "Auto",
                                               'sta_auth': "PSK",
                                               'sta_wpa_ver': "WPA2",
                                               'sta_encryption': "TKIP",
                                               'auth_svr': '',
                                               'type': 'guest',
                                               'key_index': "",
                                               'key_string': utils.make_random_string(63, "alnum"),
                                               'username': "",
                                               'password': "",
                                               'ras_addr': "",
                                               'ras_port': "",
                                               'ras_secret': "",
                                               'use_radius': False,
                                               'do_tunnel': None,
                                               'dvlan': None,
                                               'vlan_id': None,
                                             }),
            ('WPA2 PSK Auto - STA WPA2 AES', {'ssid': "wpa2-auto-sta-aes-%s" % (time.strftime("%H%M%S")),
                                              'auth': "PSK",
                                              'wpa_ver': "WPA2",
                                              'encryption': "Auto",
                                              'sta_auth': "PSK",
                                              'sta_wpa_ver': "WPA2",
                                              'sta_encryption': "AES",
                                              'auth_svr': '',
                                              'type': 'guest',
                                              'key_index': "",
                                              'key_string': utils.make_random_string(63, "alnum"),
                                              'username': "",
                                              'password': "",
                                              'ras_addr': "",
                                              'ras_port': "",
                                              'ras_secret': "",
                                              'use_radius': False,
                                              'do_tunnel': None,
                                              'dvlan': None,
                                              'vlan_id': None,
                                              }),
#            ('WPA-Mixed PSK TKIP - STA WPA TKIP', {'ssid': "mixed-tkip-sta-wpa-tkip-%s" % (time.strftime("%H%M%S")),
#                                                   'auth': "PSK",
#                                                   'wpa_ver': "WPA_Mixed",
#                                                   'encryption': "TKIP",
#                                                   'sta_auth': "PSK",
#                                                   'sta_wpa_ver': "WPA",
#                                                   'sta_encryption': "TKIP",
#                                                   'auth_svr': '',
#                                                   'type': 'guest',
#                                                   'key_index': "",
#                                                   'key_string': utils.make_random_string(63, "alnum"),
#                                                   'username': "",
#                                                   'password': "",
#                                                   'ras_addr': "",
#                                                   'ras_port': "",
#                                                   'ras_secret': "",
#                                                   'use_radius': False,
#                                                   'do_tunnel': None,
#                                                   'dvlan': None,
#                                                   'vlan_id': None,
#                                                    }),
#            ('WPA-Mixed PSK TKIP - STA WPA2 TKIP', {'ssid': "mixed-tkip-sta-wpa2-tkip--%s" % (time.strftime("%H%M%S")),
#                                                    'auth': "PSK",
#                                                    'wpa_ver': "WPA_Mixed",
#                                                    'encryption': "TKIP",
#                                                    'sta_auth': "PSK",
#                                                    'sta_wpa_ver': "WPA2",
#                                                    'sta_encryption': "TKIP",
#                                                    'auth_svr': '',
#                                                    'type': 'guest',
#                                                    'key_index': "",
#                                                    'key_string': utils.make_random_string(63, "alnum"),
#                                                    'username': "",
#                                                    'password': "",
#                                                    'ras_addr': "",
#                                                    'ras_port': "",
#                                                    'ras_secret': "",
#                                                    'use_radius': False,
#                                                    'do_tunnel': None,
#                                                    'dvlan': None,
#                                                    'vlan_id': None,
#                                                   }),
            ('WPA-Mixed PSK AES - STA WPA AES', {'ssid': "mixed-aes-sta-wpa-aes-%s" % (time.strftime("%H%M%S")),
                                                 'auth': "PSK",
                                                 'wpa_ver': "WPA_Mixed",
                                                 'encryption': "AES",
                                                 'sta_auth': "PSK",
                                                 'sta_wpa_ver': "WPA",
                                                 'sta_encryption': "AES",
                                                 'auth_svr': '',
                                                 'type': 'guest',
                                                 'key_index': "",
                                                 'key_string': utils.make_random_string(63, "alnum"),
                                                 'username': "",
                                                 'password': "",
                                                 'ras_addr': "",
                                                 'ras_port': "",
                                                 'ras_secret': "",
                                                 'use_radius': False,
                                                 'do_tunnel': None,
                                                 'dvlan': None,
                                                 'vlan_id': None,
                                                }),
            ('WPA-Mixed PSK AES - STA WPA2 AES', {'ssid': "mixed-aes-sta-wpa2-aes-%s" % (time.strftime("%H%M%S")),
                                                 'auth': "PSK",
                                                 'wpa_ver': "WPA_Mixed",
                                                 'encryption': "AES",
                                                 'sta_auth': "PSK",
                                                 'sta_wpa_ver': "WPA2",
                                                 'sta_encryption': "AES",
                                                 'auth_svr': '',
                                                 'type': 'guest',
                                                 'key_index': "",
                                                 'key_string': utils.make_random_string(63, "alnum"),
                                                 'username': "",
                                                 'password': "",
                                                 'ras_addr': "",
                                                 'ras_port': "",
                                                 'ras_secret': "",
                                                 'use_radius': False,
                                                 'do_tunnel': None,
                                                 'dvlan': None,
                                                 'vlan_id': None,
                                                }),
            ('WPA-Mixed PSK Auto - STA WPA TKIP', {'ssid': "mixed-auto-sta-wpa-tkip-%s" % (time.strftime("%H%M%S")),
                                                   'auth': "PSK",
                                                   'wpa_ver': "WPA_Mixed",
                                                   'encryption': "Auto",
                                                   'sta_auth': "PSK",
                                                   'sta_wpa_ver': "WPA",
                                                   'sta_encryption': "TKIP",
                                                   'auth_svr': '',
                                                   'type': 'guest',
                                                   'key_index': "",
                                                   'key_string': utils.make_random_string(63, "alnum"),
                                                   'username': "",
                                                   'password': "",
                                                   'ras_addr': "",
                                                   'ras_port': "",
                                                   'ras_secret': "",
                                                   'use_radius': False,
                                                   'do_tunnel': None,
                                                   'dvlan': None,
                                                   'vlan_id': None,
                                                  }),
            ('WPA-Mixed PSK Auto - STA WPA AES', {'ssid': "mixed-auto-sta-wpa-aes-%s" % (time.strftime("%H%M%S")),
                                                   'auth': "PSK",
                                                   'wpa_ver': "WPA_Mixed",
                                                   'encryption': "Auto",
                                                   'sta_auth': "PSK",
                                                   'sta_wpa_ver': "WPA",
                                                   'sta_encryption': "AES",
                                                   'auth_svr': '',
                                                   'type': 'guest',
                                                   'key_index': "",
                                                   'key_string': utils.make_random_string(63, "alnum"),
                                                   'username': "",
                                                   'password': "",
                                                   'ras_addr': "",
                                                   'ras_port': "",
                                                   'ras_secret': "",
                                                   'use_radius': False,
                                                   'do_tunnel': None,
                                                   'dvlan': None,
                                                   'vlan_id': None,
                                                  }), 
            ('WPA-Mixed PSK Auto - STA WPA2 TKIP', {'ssid': "mixed-auto-sta-wpa2-tkip--%s" % (time.strftime("%H%M%S")),
                                                   'auth': "PSK",
                                                   'wpa_ver': "WPA_Mixed",
                                                   'encryption': "Auto",
                                                   'sta_auth': "PSK",
                                                   'sta_wpa_ver': "WPA2",
                                                   'sta_encryption': "TKIP",
                                                   'auth_svr': '',
                                                   'type': 'guest',
                                                   'key_index': "",
                                                   'key_string': utils.make_random_string(63, "alnum"),
                                                   'username': "",
                                                   'password': "",
                                                   'ras_addr': "",
                                                   'ras_port': "",
                                                   'ras_secret': "",
                                                   'use_radius': False,
                                                   'do_tunnel': None,
                                                   'dvlan': None,
                                                   'vlan_id': None,
                                                  }), 
            ('WPA-Mixed PSK Auto - STA WPA2 AES', {'ssid': "mixed-auto-sta-wpa2-aes-%s" % (time.strftime("%H%M%S")),
                                                   'auth': "PSK",
                                                   'wpa_ver': "WPA_Mixed",
                                                   'encryption': "Auto",
                                                   'sta_auth': "PSK",
                                                   'sta_wpa_ver': "WPA2",
                                                   'sta_encryption': "AES",
                                                   'auth_svr': '',
                                                   'type': 'guest',
                                                   'key_index': "",
                                                   'key_string': utils.make_random_string(63, "alnum"),
                                                   'username': "",
                                                   'password': "",
                                                   'ras_addr': "",
                                                   'ras_port': "",
                                                   'ras_secret': "",
                                                   'use_radius': False,
                                                   'do_tunnel': None,
                                                   'dvlan': None,
                                                   'vlan_id': None,
                                                  }), 
             ]

guest_policy = {'Auth/No TOU/No Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=True,
                                                                              use_tou=False,
                                                                              redirect_url=''),
                                               'guestpass_policy_cfg': dict(),
                                               'generate_guestpass_cfg': dict(),
                                               },
                'Auth/No TOU/Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=True,
                                                                              use_tou=False,
                                                                              redirect_url='http://172.16.10.252/'),
                                            'guestpass_policy_cfg': dict(),
                                            'generate_guestpass_cfg': dict(),
                                           },
                'Auth/TOU/No Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=True,
                                                                              use_tou=True,
                                                                              redirect_url=''),
                                            'guestpass_policy_cfg': dict(),
                                            'generate_guestpass_cfg': dict(),
                                           },
                'Auth/TOU/Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=True,
                                                                              use_tou=True,
                                                                              redirect_url='http://172.16.10.252/'),
                                         'guestpass_policy_cfg': dict(),
                                         'generate_guestpass_cfg': dict(),
                                         },
                'No Auth/No TOU/No Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=False,
                                                                              use_tou=False,
                                                                              redirect_url=''),
                                                  'guestpass_policy_cfg': dict(),
                                                  'generate_guestpass_cfg': dict(),
                                                 },
                'No Auth/No TOU/Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=False,
                                                                              use_tou=False,
                                                                              redirect_url='http://172.16.10.252/'),
                                               'guestpass_policy_cfg': dict(),
                                               'generate_guestpass_cfg': dict(),
                                                 },
                'No Auth/TOU/No Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=False,
                                                                              use_tou=True,
                                                                              redirect_url=''),
                                               'guestpass_policy_cfg': dict(),
                                               'generate_guestpass_cfg': dict(),
                                               },
                'No Auth/TOU/Redirection': {'guestaccess_policy_cfg': dict(use_guestpass_auth=False,
                                                                              use_tou=True,
                                                                              redirect_url='http://172.16.10.252/'),
                                            'guestpass_policy_cfg': dict(),
                                            'generate_guestpass_cfg': dict(),
                                            },
                'Restricted Subnet Access': {'guestaccess_policy_cfg': dict(use_guestpass_auth=True,
                                                                            use_tou=True,
                                                                            redirect_url='http://172.16.10.252/'),
                                            'restricted_subnet_list': [],
                                            'guestpass_policy_cfg': dict(),
                                            'generate_guestpass_cfg': dict()}}

for unit in guest_policy.keys():
    guest_policy[unit]['guestpass_policy_cfg'].update(dict(auth_serv="",
                                                           is_first_use_expired=False,
                                                           valid_day='5'))
    guest_policy[unit]['generate_guestpass_cfg'].update(dict(type="single",
                                                             guest_fullname="Guest-Auth",
                                                             duration="5",
                                                             duration_unit="Days",
                                                             key="",
                                                             wlan="",
                                                             remarks="",
                                                             is_shared="No",
                                                             auth_ser='Local Database',
                                                             username="",
                                                             password=""))
                                                              

def define_input_cfg():
    test_conf = dict(
        zd_ip_addr='192.168.0.2',

        user_cfg={},

        wlan_cfg={},
        
        guest_policy={},

        ap_radio="",

        connection_timed_out=5 * 1000, # in seconds
    )

    return test_conf


def define_test_configuration(tbcfg, input_cfg):
    test_cfgs = []
    dest_ip = '172.16.10.252'
    
    if input_cfg['enabled_tunnel']:
        for wlan_cfg_tuple in input_cfg['wlans_cfg']:
            wlan_cfg_tuple[1]['do_tunnel'] = True
            
    if input_cfg['enabled_vlan']:
        for wlan_cfg_tuple in input_cfg['wlans_cfg']:
            wlan_cfg_tuple[1]['dvlan'] = True
            wlan_cfg_tuple[1]['vlan_id'] = '2'
            
    if input_cfg['conn_mode'].lower() == "l2":
        if input_cfg['enabled_tunnel']:
            if not input_cfg['enabled_vlan']:
                input_cfg['expected_subnet'] = "192.168.0.0"
                for wlan_cfg_tuple in input_cfg['wlans_cfg']:
                    wlan_cfg_tuple[1]['do_tunnel'] = True
            else:
                input_cfg['expected_subnet'] = "20.0.2.0/255.255.255.0"
                for wlan_cfg_tuple in input_cfg['wlans_cfg']:
                    wlan_cfg_tuple[1]['do_tunnel'] = True
                    wlan_cfg_tuple[1]['dvlan'] = True
                    wlan_cfg_tuple[1]['vlan_id'] = '2'                

    elif input_cfg['conn_mode'].lower() == "l3":
        if input_cfg['enabled_tunnel']:
            if not input_cfg['enabled_vlan']:
                input_cfg['expected_subnet'] = "192.168.0.0"
                for wlan_cfg_tuple in input_cfg['wlans_cfg']:
                    wlan_cfg_tuple[1]['do_tunnel'] = True
            else:
                input_cfg['expected_subnet'] = "20.0.2.0/255.255.255.0"
                for wlan_cfg_tuple in input_cfg['wlans_cfg']:
                    wlan_cfg_tuple[1]['do_tunnel'] = True
                    wlan_cfg_tuple[1]['dvlan'] = True
                    wlan_cfg_tuple[1]['vlan_id'] = '2'  
        else:
            if not input_cfg['enabled_vlan']:
                input_cfg['expected_subnet'] = "192.168.33.0"
            else:
                input_cfg['expected_subnet'] = "20.0.2.0/255.255.255.0"
                for wlan_cfg_tuple in input_cfg['wlans_cfg']:
                    wlan_cfg_tuple[1]['dvlan'] = True
                    wlan_cfg_tuple[1]['vlan_id'] = '2'  
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Get the station'
    test_params = {'sta_tag': 'sta1', 'sta_ip_addr': input_cfg['station']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from Zone Director'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the active ap'
    test_params = {'ap_tag': 'active_ap', 'active_ap': input_cfg['active_ap_list'][0]}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    if input_cfg['enabled_tunnel'] == False:
        test_name = 'CB_ZD_Config_AP_Radio'
        common_name = 'Config All APs Radio - Disable WLAN Service'
        test_params = {'ap_tag': 'active_ap', 'cfg_type': 'init', 'all_ap_mac_list': input_cfg['all_aps_mac_list']}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Config_AP_Radio'
        common_name = 'Config Active AP Radio - Enable WLAN Service'
        test_params = {'ap_tag': 'active_ap', 
                       'active_ap_mac': input_cfg['active_aps_mac_list'][0], 
                       'cfg_type': 'config',
                       'ap_cfg': {'wlan_service': True, 'radio': input_cfg['ap_radio']}}
        test_cfgs.append((test_params, test_name, common_name, 0, False))

    if input_cfg['auth_svr'] == 'Local User':
        test_name = 'CB_ZD_Create_Local_User'
        common_name = 'Create Local User'
        test_params = {'username': input_cfg['user_cfg']['username'],
                       'password': input_cfg['user_cfg']['password']}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
                     
    elif input_cfg['auth_svr'] == 'AD User':
        test_name = 'CB_ZD_Create_Authentication_Server'
        common_name = 'Create AD Authentication Server'
        test_params = {'auth_ser_cfg_list': [input_cfg['user_cfg'], ]}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
                
    elif input_cfg['auth_svr'] == 'LDAP User':
        test_name = 'CB_ZD_Create_Authentication_Server'
        common_name = 'Create LDAP Authentication Server'
        test_params = {'auth_ser_cfg_list': [input_cfg['user_cfg'], ]}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
                     
    elif input_cfg['auth_svr'] == 'RADIUS User':
        test_name = 'CB_ZD_Create_Authentication_Server'
        common_name = 'Create RADIUS Authentication Server'
        test_params = {'auth_ser_cfg_list': [input_cfg['user_cfg'], ]}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    
    if input_cfg['enabled_tunnel']:
        input_cfg['guest_policy'] = {'Auth/TOU/Redirection': input_cfg['guest_policy']['Auth/TOU/Redirection']}
        wlan_cfg_list = []
        for wlan_cfgs in input_cfg['wlans_cfg']:
            wlan_cfg_list.append(wlan_cfgs[1])
            
        test_name = 'CB_ZD_Create_Wlan'
        common_name = 'Create all kinds of encryption for the guest wlan'
        test_params = {'wlan_cfg_list': wlan_cfg_list}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
        common_name = 'Uncheck all wlans in the default wlangroup'
        test_params = {}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Create_Empty_Wlan_Group'
        common_name = 'Create an empty wlangroup to assign the needed wlan'
        test_params = {'name': 'GuestAccess-WlanGroup', 'description': 'GuestAccess-WlanGroup'}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = 'Assign the active ap to the wlan group'
        test_params = {'active_ap': input_cfg['active_ap_list'][0],
                       'wlan_group_name': 'GuestAccess-WlanGroup',
                       'radio_mode': input_cfg['ap_radio']}
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Set_GuestAccess_Policy'
        common_name = 'Set the guest-access policy(%s)' % input_cfg['guest_policy'].keys()[0]
        test_params = input_cfg['guest_policy']['Auth/TOU/Redirection']['guestaccess_policy_cfg']
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
    else:
        input_cfg['wlans_cfg'] = [input_cfg['wlans_cfg'][0]]
        
        test_name = 'CB_ZD_Create_Wlan'
        common_name = 'Create a guest wlan'
        test_params = {'wlan_cfg_list': [input_cfg['wlans_cfg'][0][1]]}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
          
    for wlan_cfg_tuple_unit in input_cfg['wlans_cfg']:
        for guest in sorted(input_cfg['guest_policy'].keys()):
            if input_cfg['enabled_tunnel']:
                tcid = '[%s]:' % wlan_cfg_tuple_unit[0]
            else:
                tcid = '[%s]:' % guest
                
            if input_cfg['enabled_tunnel']:
                test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
                common_name = '%sassign the wlan member to the wlangroup[%s]' % (tcid, 'GuestAccess-WlanGroup')
                test_params = {'wlan_name_list': [wlan_cfg_tuple_unit[1]['ssid']], 'wlangroup_name': 'GuestAccess-WlanGroup'}
                test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            if not input_cfg['enabled_tunnel']:
                test_name = 'CB_ZD_Set_GuestAccess_Policy'
                common_name = '%sset the guest-access policy' % tcid
                test_params = input_cfg['guest_policy'][guest]['guestaccess_policy_cfg']
                test_cfgs.append((test_params, test_name, common_name, 1, False))
            
                if guest == 'Restricted Subnet Access':
                    test_name = 'CB_ZD_Set_Guest_Restricted_Subnet_Access'
                    common_name = '%sset the guest restricted subnet access record' % tcid
                    test_params = {'restricted_subnet_list': input_cfg['guest_policy'][guest]['restricted_subnet_list']}
                    test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            input_cfg['guest_policy'][guest]['generate_guestpass_cfg'].update({'wlan': wlan_cfg_tuple_unit[1]['ssid'],
                                                                               'auth_ser': input_cfg['user_cfg']['server_name']})
            generate_guestpass_dict = deepcopy(input_cfg['guest_policy'][guest]['generate_guestpass_cfg'])
             
            test_name = 'CB_ZD_Generate_Guest_Pass'
            common_name = '%sgenerate the guest pass and the expired time' % tcid
            test_params = generate_guestpass_dict
            test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            generate_guestpass_dict = None
            
            test_name = 'CB_ZD_Associate_Station_1'
            common_name = '%sassociate the target station' % tcid
            test_params = {'sta_tag': 'sta1', 'wlan_cfg': wlan_cfg_tuple_unit[1]}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
            common_name = '%sget target station Wifi addresses' % tcid
            test_params = {'sta_tag': 'sta1'}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
                
            #verify the expected subnet in the station.
            if input_cfg['enabled_tunnel']:
                test_name = 'CB_Station_Verify_Expected_Subnet'
                common_name = '%sverify the station can get the expected subnet[%s]' % (tcid, input_cfg['expected_subnet'])
                test_params = {'sta_tag': 'sta1', 'expected_subnet': input_cfg['expected_subnet']}
                test_cfgs.append((test_params, test_name, common_name, 2, False))
            
            radio_mode = input_cfg['ap_radio']
            if radio_mode == 'bg':
                radio_mode = 'g'
                
            if guest != 'Restricted Subnet Access':
                test_name = 'CB_Station_Ping_Dest_Is_Denied'
                common_name = '%sclient ping dest-ip[%s] which is disallow before the guest auth' % (tcid, dest_ip)
                test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
                test_cfgs.append((test_params, test_name, common_name, 2, False))
                
                test_name = 'CB_ZD_Verify_Active_Client_Info'
                common_name = '%sverify the station info which is unauthorized on ZD before the guest auth' % tcid
                test_params = {'sta_tag': 'sta1', 
                               'status': 'Unauthorized',
                               'radio_mode': radio_mode, 
                               'wlan_cfg': wlan_cfg_tuple_unit[1],
                               'ap_tag': 'active_ap'}
                test_cfgs.append((test_params, test_name, common_name, 2, False))
                
                if input_cfg['enabled_tunnel'] == False:
                    test_name = 'CB_ZD_Verify_GuestAccess_Policy'
                    common_name = '%sverify the guestaccess policy on ZD' % tcid
                    test_params = input_cfg['guest_policy'][guest]['guestaccess_policy_cfg']
                    test_cfgs.append((test_params, test_name, common_name, 2, False))
                    
                    test_name = 'CB_ZD_Verify_GuestPass_Policy'
                    common_name = '%sverify the guestpass policy on ZD' % tcid
                    test_params = input_cfg['guest_policy'][guest]['guestpass_policy_cfg']
                    test_cfgs.append((test_params, test_name, common_name, 2, False))
            
            if 'No Auth' in guest:
                no_auth = True
            else:
                no_auth = False
                
            if 'No Redirection' in guest:
                target_url = 'http://172.16.10.252/'
                redirect_url = ''
            else:
                target_url = 'http://www.example.net'
                redirect_url = input_cfg['guest_policy'][guest]['guestaccess_policy_cfg']['redirect_url']
                
            test_name = 'CB_Station_CaptivePortal_Start_Browser'
            common_name = "%screate the station's browser object" % tcid
            test_params = {'sta_tag': 'sta1'}
            test_cfgs.append((test_params, test_name, common_name, 0, False))
                
            test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
            common_name = '%sperform guest authentication' % tcid
            test_params = {'sta_tag': 'sta1', 
                           'no_auth': no_auth, 
                           'use_tou': input_cfg['guest_policy'][guest]['guestaccess_policy_cfg']['use_tou'], 
                           'target_url': target_url, 
                           'redirect_url': redirect_url, 
                           }
            test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            test_name = 'CB_ZD_Verify_Active_Client_Info'
            common_name = '%sverify the station info which is authorized on ZD after the guest auth' % tcid
            test_params = {'sta_tag': 'sta1', 'status': 'Authorized', 'radio_mode': radio_mode,
                           'wlan_cfg': wlan_cfg_tuple_unit[1], 'ap_tag': 'active_ap',
                           'guest_name': input_cfg['guest_policy'][guest]['generate_guestpass_cfg']['guest_fullname'],
                           'use_guestpass_auth': input_cfg['guest_policy'][guest]['guestaccess_policy_cfg']['use_guestpass_auth']}
            test_cfgs.append((test_params, test_name, common_name, 2, False))
                     
            if guest == 'Restricted Subnet Access':
                test_name = 'CB_Station_Ping_Dest_Is_Denied'
                common_name = '%sclient ping ZD[%s] which is disallowed after the guest auth' % (tcid, input_cfg['zd_ip_addr'])
                test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['zd_ip_addr']}
                test_cfgs.append((test_params, test_name, common_name, 2, False))
                
                test_name = 'CB_Station_Ping_Dest_Is_Allowed'
                common_name = '%sclient ping dest-ip[%s] which is allowed after the guest auth' % (tcid, dest_ip)
                test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
                test_cfgs.append((test_params, test_name, common_name, 2, False))
                
                for restricted_subnet in input_cfg['guest_policy'][guest]['restricted_subnet_list']:
                    test_name = 'CB_Station_Ping_Dest_Is_Denied'
                    common_name = '%sclient ping restricted-ip[%s] which is disallowed after the guest auth' % (tcid, restricted_subnet.split('/')[0])
                    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': restricted_subnet.split('/')[0]}
                    test_cfgs.append((test_params, test_name, common_name, 2, False))
            else:
                test_name = 'CB_Station_CaptivePortal_Download_File'
                common_name = '%sdownload the file from the dest url to the station' % tcid
                test_params = {'sta_tag': 'sta1'}
                test_cfgs.append((test_params, test_name, common_name, 2, False))
            
            test_name = 'CB_Station_CaptivePortal_Quit_Browser'
            common_name = "%sclosed the station's browser object" % tcid
            test_params = {'sta_tag': 'sta1'}
            test_cfgs.append((test_params, test_name, common_name, 0, False))
            
            test_name = 'CB_ZD_Verify_Station_In_Tunnel_Mode'
            common_name = '%sverify the station traffic info on tunnel mode' % tcid
            test_params = {'sta_tag': 'sta1', 'active_ap_mac': input_cfg['active_aps_mac_list'][0],
                           'wlan_cfg': wlan_cfg_tuple_unit[1]}
            test_cfgs.append((test_params, test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_Delete_Active_Client'
            common_name = "%sdelete the station from the zone director's currently active clients" % tcid
            test_params = {'sta_tag': 'sta1', 'test_policy': 'guest access',
                           'guest_name': input_cfg['guest_policy'][guest]['generate_guestpass_cfg']['guest_fullname'],
                           'use_guestpass_auth': input_cfg['guest_policy'][guest]['guestaccess_policy_cfg']['use_guestpass_auth'],
                           'wlan_cfg': wlan_cfg_tuple_unit[1]}
            test_cfgs.append((test_params, test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_Remove_Guest_Passes_List'
            common_name = '%sremove all guest passes from zone director to cleanup' % tcid
            test_params = {}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            test_name = 'CB_Station_Remove_All_Wlans'
            common_name = '%sremove the wlan from the station' % tcid
            test_params = {'sta_tag': 'sta1'}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
            
            if input_cfg['enabled_tunnel']:
                test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
                common_name = '%sremove the wlan from the wlangroup[%s]' % (tcid, 'GuestAccess-WlanGroup')
                test_params = {'wgs_cfg': {'name': 'GuestAccess-WlanGroup'}, 'wlan_list': [wlan_cfg_tuple_unit[1]['ssid'], ]}
                test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    if input_cfg['enabled_tunnel'] == False:
        test_name = 'CB_ZD_Config_AP_Radio'
        common_name = 'Config All APs Radio - Enable WLAN Service'
        test_params = {'ap_tag': 'active_ap', 'cfg_type': 'teardown', 'all_ap_mac_list': input_cfg['all_aps_mac_list']}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from Zone Director to Cleanup'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    return test_cfgs


def get_selected_input(depot=[], num=1, prompt=""):
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
    attrs = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = []
    all_aps_mac_list = []
    active_aps_mac_list = []
    enabled_mesh = False
    enabled_tunnel = False
    enabled_vlan = False
    conn_mode = ''

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ") 
        target_sta_radio = testsuite.get_target_sta_radio() 
    else: 
        target_sta = sta_ip_list[attrs["station"][0]] 
        target_sta_radio = attrs["station"][1] 
        
    fit_ap_model = dict() 
    for ap_sym_name, ap_info in ap_sym_dict.items(): 
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            fit_ap_model[ap_sym_name] = ap_info
            if ('Mesh' or 'Root') in ap_info['status']:
                enabled_mesh = True
    
    if attrs["interactive_mode"]:
        try:
            active_ap_list = testsuite.getActiveAp(fit_ap_model)
            print active_ap_list
            if not active_ap_list:
                raise Exception("No found the surpported ap in the testbed env.")
        except:
            raise Exception("No found the surpported ap in the testbed env.")
    else:
        pass
            
    auth_svr = get_selected_input(
                  [user for user in user_cfg_kv.iterkeys()], 1,
                  'Select Authentication User '
                )[0]
                
#    if enabled_mesh:
    if attrs["interactive_mode"]:
        enabled_tunnel = raw_input("Is tunnel mode enabled? [y/n]: ").lower() == "y"
        if enabled_tunnel:
            conn_mode = raw_input("Please enter connection mode [l2/l3]: ")
            if conn_mode not in ['l2', 'l3']:
                raise Exception('Please type the corrected keyword.')
            enabled_vlan = raw_input("Is VLAN tagging enabled? [y/n]: ").lower() == "y"
    else:
        pass
        

    for guest_p in guest_policy:
        guest_policy[guest_p]['guestpass_policy_cfg']['auth_serv'] = user_cfg_kv[auth_svr]['server_name']
        guest_policy[guest_p]['generate_guestpass_cfg']['username'] = user_cfg_kv[auth_svr]['username']
        guest_policy[guest_p]['generate_guestpass_cfg']['password'] = user_cfg_kv[auth_svr]['password']
        if guest_p == 'Restricted Subnet Access':
            guest_policy[guest_p]['restricted_subnet_list'] = ['172.21.0.252/24',
                                                               '172.22.0.252/24',
                                                               '172.23.0.252/24',
                                                               '172.24.0.252/24',
                                                               '172.25.0.252/24', ]
    
    input_cfg = define_input_cfg()
    
    for active_ap in active_ap_list:
        for u_ap in ap_sym_dict.keys():
            ap_mac = ap_sym_dict[u_ap]['mac']
            if u_ap == active_ap:
                active_aps_mac_list.append(ap_mac)
            all_aps_mac_list.append(ap_mac)
        
        if not enabled_mesh:
            ap_sub_model = ap_sym_dict[active_ap]['model'].upper()
            ts_name = 'WLAN Type - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
            if enabled_tunnel and conn_mode == 'l2':
                if not enabled_vlan:
                    ts_name = 'WLAN Type - L2 Tunnel - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
                else:
                    ts_name = 'L2 Tunnel with VLAN - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
            elif enabled_tunnel and conn_mode == 'l3':
                if not enabled_vlan:
                    ts_name = 'WLAN Type - L3 Tunnel - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
                else:
                    ts_name = 'L3 Tunnel with VLAN - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
        else:
            ap_mesh_status = str(re.findall(r'^.*\((.*)\).*', ap_sym_dict[active_ap]['status'])[0])
            ap_sub_model = ap_sym_dict[active_ap]['model'].upper() + '(' + ap_mesh_status + ')'
            
            ts_name = 'Mesh - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
            if enabled_tunnel and conn_mode == 'l2':
                if not enabled_vlan:
                    ts_name = 'Mesh - L2 Tunnel - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
                else:
                    ts_name = 'Mesh - L2 Tunnel with VLAN - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
            elif enabled_tunnel and conn_mode == 'l3':
                if not enabled_vlan:
                    ts_name = 'Mesh - L3 Tunnel - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
                else:
                    ts_name = 'Mesh - L3 Tunnel with VLAN - GuestAccess - %s - %s %s' % (auth_svr, ap_sub_model, target_sta_radio)
        ts = testsuite.get_testsuite(ts_name, ts_name,
                                     interactive_mode=True,
                                     combotest=True,)
    
        fcfg = {'ts_name': ts.name,
                'sta_ip_list': sta_ip_list,
                'ap_sym_name_list': ap_sym_dict.keys(),
               }
        
        input_cfg.update({
            'auth_svr': auth_svr,
            'user_cfg': user_cfg_kv[auth_svr],
            'wlans_cfg': wlans_cfg,
            'enabled_mesh': enabled_mesh,
            'exit_wlan_id': False,
            'enabled_tunnel': enabled_tunnel,
            'enabled_vlan': enabled_vlan,
            'vlan_id': '',
            'expected_subnet': '',
            'conn_mode': conn_mode,
            'guest_policy': guest_policy,
            'ap_radio': target_sta_radio,
            'active_ap_list': active_ap_list,
            'station': target_sta,
            'all_aps_mac_list': all_aps_mac_list,
            'active_aps_mac_list': active_aps_mac_list
            })
        
        test_cfgs = define_test_configuration(fcfg, input_cfg)
        
        test_order = 1
        test_added = 0
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params,
                                     test_order, exc_level, is_cleanup) > 0:
                test_added += 1
    
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

#----------------------------------#
#     Access Method
#----------------------------------#    

if __name__ == "__main__":    
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    
