"""Common commands used in test's config command
"""
import time
import logging
import random
import re

from RuckusAutoTest.components.Station import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

# self.target_station = tconfig.get_target_station(conf['target_station'], self.testbed.components['Station'])
def get_target_station(target_station_ip_addr, station_list, **kwargs):
    cfg = {'check_status_timeout': 60, 'remove_all_wlan': True}
    cfg.update(kwargs)
    for station in station_list:
        if station.get_ip_addr() == target_station_ip_addr:
            # Found the target station
            if cfg['remove_all_wlan']:
                logging.info("Remove all WLAN profiles on the target station %s" % station.get_ip_addr())
                station.remove_all_wlan()
                logging.info("Make sure the target station %s disconnects from wireless network" %
                             station.get_ip_addr())
                start_time = time.time()
                while True:
                    if station.get_current_status() == "disconnected":
                        break
                    time.sleep(1)
                    if time.time() - start_time > cfg['check_status_timeout']:
                        raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                        cfg['check_status_timeout'])
            else:
                logging.info("WLAN profiles on the target station %s are unknown." % station.get_ip_addr())
            return station

    # did not find target_station's ip_addr from the station_list
    return None

# self.active_ap = tconfig.get_testbed_active_ap(self.testbed, conf['active_ap'])
# self.target_ap = tconfig.get_testbed_active_ap(self.testbed, conf['target_ap'], 'TargetAP')
def get_testbed_active_ap(testbed, active_ap_macAddr, announce_name = 'ActiveAP'):
    ap_macAddr = testbed.get_ap_mac_addr_by_sym_name(active_ap_macAddr)
    ap = get_active_ap(ap_macAddr, testbed.components['AP'])
    if ap:
        logging.info('%s(%s) found in testbed with mac=%s' % (announce_name, active_ap_macAddr, ap.get_base_mac()))
    return ap

# self.active_ap = get_active_ap(conf['active_ap'], self.testbed.components['AP'])
def get_active_ap(active_ap_macAddr, ap_list, announce_name = 'ActiveAP'):
    active_ap_macAddr = active_ap_macAddr.upper()
    # Find the active AP object
    ap_mac_list = []
    # print "Managed AP object list: %s" % ap_list
    for ap in ap_list:
        if isinstance(ap, RuckusAP) or type(ap.__class__) == type(RuckusAP):
            ap_mac_list.append(ap.get_base_mac())
            if ap.get_base_mac().upper() == active_ap_macAddr:
                return ap

    # did not find active_ap_macAddr from the ap_list
    logging.info("Did not find mac address of %s(%s) from testbed's managed AP: %s." % (announce_name, active_ap_macAddr, ap_mac_list))
    return None

# tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout=self.check_status_timeout)
def remove_all_wlan_from_station(station, **kwargs):
    cfg = {'check_status_timeout': 60}
    cfg.update(kwargs)

    logging.info("Remove all WLAN profiles on the remote station %s" % station.get_ip_addr())
    station.remove_all_wlan()

    logging.info("Make sure the target station disconnects from the wireless networks")
    start_time = time.time()
    while True:
        if station.get_current_status() == "disconnected":
            break
        time.sleep(1)
        if time.time() - start_time > cfg['check_status_timeout']:
            raise Exception("The station did not disconnect from wireless network within %d seconds" %
                            cfg['check_status_timeout'])

# tconfig.create_auth_server(self.testbed.components['ZoneDirector'], **self.conf)
def create_auth_server(zd, server_name = "", **kwargs):
    cfg = {}
    cfg.update(kwargs)
    if server_name:
        cfg['server_name'] = server_name
    if cfg.has_key('secret'):
        zd.create_radius_server(cfg['server'], cfg['port'], cfg['secret'], cfg['server_name'])
    elif cfg.has_key('domain'):
        zd.create_ad_server(cfg['server'], cfg['port'], cfg['domain'], cfg['server_name'])
    elif cfg['server_name'] == "Local Database":
        zd.create_user(cfg['user'], cfg['password'])

def define_wlans_configuration():
    wlan_conf_list = []
    # Open - None
    wlan_conf_list.append(dict(auth = "open", encryption = "none"))

    # Open-WEP-128
    wlan_conf_list.append(dict(auth = "open", encryption = "WEP-128",
                      key_index = "1" , key_string = utils.make_random_string(26, "hex")))

    # Shared-WEP-64
    wlan_conf_list.append(dict(auth = "shared", encryption = "WEP-64",
                      key_index = "1" , key_string = utils.make_random_string(10, "hex")))

    # Shared-WEP-128
    wlan_conf_list.append(dict(auth = "shared", encryption = "WEP-128",
                      key_index = "3" , key_string = utils.make_random_string(26, "hex")))

    # WPA-PSK-TKIP
    wlan_conf_list.append(dict(auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                      sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex")))

    # WPA-PSK-AES
    wlan_conf_list.append(dict(auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                      sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex")))

    # WPA2-PSK-TKIP
    wlan_conf_list.append(dict(auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                      sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex")))

    # WPA2-PSK-AES
    wlan_conf_list.append(dict(auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                      sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex")))

    return sorted(wlan_conf_list)

def get_wlan_profile(profile_name):
    """
    """
    #
    # Define wlan configuration
    #

    default_wlan_conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
                         'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
                         'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
                         'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '',
                         'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    open_none = default_wlan_conf.copy()
    open_none.update({'ssid':'Open-None', 'auth':'open', 'encryption':'none'})

    mac_none = default_wlan_conf.copy()
    mac_none.update({'ssid':'MAC-None', 'auth':'mac', 'encryption':'none'})

    open_wep_64 = default_wlan_conf.copy()
    open_wep_64.update({'ssid':'Open-Wep-64', 'auth':'open', 'encryption':'WEP-64',
                        'key_index':'1' , 'key_string':utils.make_random_string(10, "hex")})

    open_wep_128 = default_wlan_conf.copy()
    open_wep_128.update({'ssid':'Open-Wep-128', 'auth':'open', 'encryption':'WEP-128',
                        'key_index':'1' , 'key_string':utils.make_random_string(26, "hex")})

    shared_wep_64 = default_wlan_conf.copy()
    shared_wep_64.update({'ssid':'Shared-Wep-64', 'auth':'share', 'encryption':'WEP-64',
                        'key_index':'1' , 'key_string':utils.make_random_string(10, "hex")})

    shared_wep_128 = default_wlan_conf.copy()
    shared_wep_128.update({'ssid':'Shared-Wep-128', 'auth':'share', 'encryption':'WEP-128',
                        'key_index':'1' , 'key_string':utils.make_random_string(26, "hex")})

    wpa_psk_tkip = default_wlan_conf.copy()
    wpa_psk_tkip.update({'ssid':'WPA-PSK-TKIP', 'auth':'PSK', 'encryption':'TKIP',
                         'wpa_ver':'WPA', 'key_string':utils.make_random_string(random.randint(8, 63), "hex")})

    wpa_psk_aes = default_wlan_conf.copy()
    wpa_psk_aes.update({'ssid':'WPA-PSK-AES', 'auth':'PSK', 'encryption':'AES',
                        'wpa_ver':'WPA', 'key_string':utils.make_random_string(random.randint(8, 63), "hex")})

    wpa2_psk_tkip = default_wlan_conf.copy()
    wpa2_psk_tkip.update({'ssid':'WPA2-PSK-TKIP', 'auth':'PSK', 'encryption':'TKIP',
                          'wpa_ver':'WPA2', 'key_string':utils.make_random_string(random.randint(8, 63), "hex")})

    wpa2_psk_aes = default_wlan_conf.copy()
    wpa2_psk_aes.update({'ssid':'WPA2-PSK-AES', 'auth':'PSK', 'encryption':'AES',
                         'wpa_ver':'WPA2', 'key_string':utils.make_random_string(random.randint(8, 63), "hex")})

    set_of_32_open_none_wlans = []
    for idx in range(0, 32):
        wlan = open_none.copy()
        wlan['ssid'] = '%s-wlan%2d' % (wlan['ssid'], idx + 1)
        set_of_32_open_none_wlans.append(wlan)

    set_of_2_open_none_wlans = []
    for idx in range(0, 2):
        wlan = open_none.copy()
        wlan['ssid'] = '%s-wlan%2d' % (wlan['ssid'], idx + 1)
        set_of_2_open_none_wlans.append(wlan)

    wlan_profiles = dict(default_wlan_conf = [default_wlan_conf],
                         open_none = [open_none],
                         mac_none = [mac_none],
                         open_wep_64 = [open_wep_64],
                         open_wep_128 = [open_wep_128],
                         shared_wep_64 = [shared_wep_64],
                         shared_wep_128 = [shared_wep_128],
                         wpa_psk_tkip = [wpa_psk_tkip],
                         wpa_psk_aes = [wpa_psk_aes],
                         wpa2_psk_tkip = [wpa2_psk_tkip],
                         wpa2_psk_aes = [wpa2_psk_aes],

                         set_of_32_open_none_wlans = set_of_32_open_none_wlans,
                         set_of_2_open_none_wlans = set_of_2_open_none_wlans
                     )

    return wlan_profiles[profile_name]

def get_bw_symbol(rate_unit):
    if re.match(r"\s*kbps", rate_unit.lower(), re.I):
        return r"\s*[kK]bps"
    elif re.match(r"\s*mbps", rate_unit.lower(), re.I):
        return r"\s*[mM]bps"
    else:
        return None

def calculate_rate_value(rate, error_margin):
    rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", rate, re.I)
    if not rate_obj:
        raise Exception("Invalid rate litmit value (%s)" % rate)
    if re.match(r"(^kbps)", rate_obj.group(2), re.I):
        ratelimit_mbps = float(rate_obj.group(1)) / 1000.0
    else:
        ratelimit_mbps = float(rate_obj.group(1))
    return ratelimit_mbps * (1.0 + error_margin)

def generate_l3_l4_rule_set(dst_ip_mask, dst_port = '33333'):
    rule_set = []

    rule_set.append({'dst_addr': 'Any', 'application': 'Any', 'protocol': 'Any', 'dst_port': 'Any'})
    rule_set.append({'dst_addr': 'Any', 'application': 'Any', 'protocol': 'Any', 'dst_port': str(dst_port)})
    rule_set.append({'dst_addr': 'Any', 'application': 'Any', 'protocol': '1', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'Any', 'protocol': '6', 'dst_port': str(dst_port)})
    rule_set.append({'dst_addr': 'Any', 'application': 'Any', 'protocol': '17', 'dst_port': str(dst_port)})
    rule_set.append({'dst_addr': 'Any', 'application': 'HTTP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'HTTPS', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'FTP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'SSH', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'TELNET', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'SMTP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'DNS', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'DHCP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': 'Any', 'application': 'SNMP', 'protocol': '', 'dst_port': ''})

    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'Any', 'protocol': 'Any', 'dst_port': 'Any'})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'Any', 'protocol': 'Any', 'dst_port': str(dst_port)})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'Any', 'protocol': '1', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'Any', 'protocol': '6', 'dst_port': str(dst_port)})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'Any', 'protocol': '17', 'dst_port': str(dst_port)})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'HTTP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'HTTPS', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'FTP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'SSH', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'TELNET', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'SMTP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'DNS', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'DHCP', 'protocol': '', 'dst_port': ''})
    rule_set.append({'dst_addr': dst_ip_mask, 'application': 'SNMP', 'protocol': '', 'dst_port': ''})

    return rule_set

def make_tcp_dump_arg_from_acl(rule):
    """ Build the argument string which is passed to the tcpdump utility on the Linux PC
        to sniff packets
        The given rule must be a dictionary with keys and values defined in the function generate_l3_l4_rule_set()
    """
    app_2_str = {'HTTP'  : 'ip proto 6 and dst port 80',
                 'HTTPS' : 'ip proto 6 and dst port 443',
                 'FTP'   : 'ip proto 6 and dst port 21',
                 'SSH'   : 'ip proto 6 and dst port 22',
                 'TELNET': 'ip proto 6 and dst port 23',
                 'SMTP'  : 'ip proto 6 and dst port 25',
                 'DNS'   : 'dst port 53',
                 'DHCP'  : 'dst port 67',
                 'SNMP'  : 'dst port 161'}
    args = []

    if rule['dst_addr'] != 'Any':
        # dst_addr must be in format net_addr/mask_in_bit_length
        # this processing makes sure that the net_addr does not have bit 1 in the host section
        # ZD allows this but tcpdump does not
        ip, mask = rule['dst_addr'].split('/')
        ip = utils.get_network_address(ip, mask)
        dst_net = '%s/%s' % (ip, mask)
        args.append('dst net %s' % dst_net)

    if rule['application'] in ['Any', '']:
        if rule['protocol'] == '1':
            args.append('ip proto 1')
        elif rule['protocol'] in ['6', '17']:
            args.append('ip proto %s' % rule['protocol'])
            if rule['dst_port'] not in ['Any', '']:
                args.append('dst port %s' % rule['dst_port'])
        elif rule['protocol'] in ['Any', '']:
            if rule['dst_port'] not in ['Any', '']:
                args.append('dst port %s' % rule['dst_port'])
    elif rule['application'] in app_2_str.keys():
        args.append(app_2_str[rule['application']])

    return " and ".join(args)


def get_web_auth_params(zd, username, password):
    '''
    A utility method to get the Web Authentication parameters
    Params changing across ZD's builds are defined in ZDFeatureUpdate

    # web authentication parameters for ZD 9.0.0.0 production
    'web_auth_params': {
        'target_url': 'http://www.example.net/',
        'login_url': 'https://%s/user/user_login_auth.jsp',
        'user_login_auth': {
            'username':'testuser',
            'password': 'testuser',
            'ok': "Log In",
        },
        'activate_url': 'https://%s/user/_allowuser.jsp'
    },
    '''

    web_auth_params = zd.info['web_auth_params']
    user_login_auth = web_auth_params.pop('user_login_auth')
    user_login_auth.update({
        'username': username,
        'password': password,
    })
    web_auth_params.update({
        'user_login_auth': user_login_auth
    })

    return web_auth_params

def get_guest_auth_params(zd, guest_pass, use_tou, redirect_url):
    '''
    A utility method to get the guest pass authentication parameters
    Params changing across ZD's builds are defined in ZDFeatureUpdate

    # guest pass authentication parameters for ZD 9.0.0.0 production
    'guest_auth_params': {
        'target_url': 'http://www.example.net/',
        'redirect_url': '',
        'guest_auth_cfg': {
            'guest_pass': '',
            'use_tou': False,
        },
        'guest_login_url': '%s/user/guest_login.jsp',
        'guest_login': {
            'key': '',
            'ok': 'Login',
         },
         'guest_tou_url': '%s/user/guest_tou.jsp',
         'guest_tou': {
            'ok': 'Accept and Continue',
         },
        'activate_url': '%s/user/_allowguest.jsp'
        'msg_guestpass_is_invalid': 'This is an invalid Guest Pass',
        'msg_guestpass_welcome_page': 'Welcome to the Guest Access login page',
        'msg_guestpass_tou_review': 'Please review the terms of use',
    },
    '''

    guest_auth_params = zd.info['guest_auth_params']

    redirect_url = guest_auth_params.pop('redirect_url')

    guest_auth_cfg = guest_auth_params.pop('guest_auth_cfg')
    guest_auth_cfg.update({
        'guest_pass': guest_pass,
        'use_tou': use_tou,
    })

    guest_login = guest_auth_params.pop('guest_login')
    guest_login.update({
        'key': guest_pass,
    })

    guest_auth_params.update({
        'redirect_url': redirect_url,
        'guest_auth_cfg': guest_auth_cfg,
        'guest_login': guest_login,
    })

    return guest_auth_params

