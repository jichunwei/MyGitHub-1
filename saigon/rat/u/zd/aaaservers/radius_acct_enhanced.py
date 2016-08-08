'''
User's parameters:
@param tc2f:
  - 'acct_status_type',
  - 'acct_session_time',
  - 'acct_session_id',
  - 'acct_multi_session_id',
  - 'acct_ruckus_sta_rssi',
  - 'acct_new_interim_update',
  - 'acct_backup_accounting',

Examples:

TC ZD-2757:RADIUS Accounting with new Session ID
    tea.py u.zd.aaaservers.radius_acct_enhanced tc2f='acct_session_id'

'''
import logging
import time
import re

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_server_by_ip_addr,
    create_station_by_ip_addr,
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd import user
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers as lib

default_cfg = {
    'zd_ip_addr': "192.168.0.2",
    'shell_key': '!v54! HBVkKSL0EfIDaNhsv55rSVTtTjf5MFh@',
    'sta_ip_addr': "192.168.1.12",
    'server_ip_addr': "192.168.0.232",
    'server_netmask': "255.255.255.0",
    'des_ip': "192.168.0.232",
    'ping_timeout_ms': 150 * 1000,
    'check_status_timeout': 120,
    'failover_behavior': "service", #["service", "config"]
}

server_cfg = {
    'server_name': "RadiusAcct",
    'server_addr': "192.168.0.232",
    'server_port': "1813",
    'radius_acct_secret': "1234567890",
    'secondary_server_addr': "192.168.0.240",
    'secondary_server_port': "18121",
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
    'auth': "EAP", 'wpa_ver': "WPA", 'encryption': "TKIP",
    'key_index': "" , 'key_string': "",
    'username': user_cfg['username'],
    'password': user_cfg['password'],
    'acct_svr': server_cfg['server_name'],
    'interim_update': "2" # 5 minutes
}

aaa_static_msg = [
    "Primary Server and Secondary Server must be different",
    "cannot be empty",
    "not a valid IP address",
    "Request Timeout must be a number",
    "Max Number of Retries must be a number",
    "Reconnect Primary must be a number",
    "Port is not a valid port number",
]

ACCT_PATTERNS = {
    'acct_status_interim_update':
        "(?P<attr>Acct-Status-Type)\(\d{1,}\): (?P<value>Alive|Interim-Update)\(\d{1,}\)",

    'acct_status_start':
        "(?P<attr>Acct-Status-Type)\(\d{1,}\): (?P<value>Start)\(\d{1,}\)",

    'acct_status_stop':
        "(?P<attr>Acct-Status-Type)\(\d{1,}\): (?P<value>Stop)\(\d{1,}\)",

    'acct_session_time':
        "(?P<attr>Acct-Session-Time)\(\d{1,}\): (?P<value>\d{1,})",

    'acct_session_id':
        "(?P<attr>Acct-Session-Id)\(\d{1,}\): (?P<value>\w{1,}-\w{1,})",

    'acct_multi_session_id':
        "(?P<attr>Acct-Multi-Session-Id)\(\d{1,}\): (?P<value>\w{1,})",

    'vendor_specific':
        "(?P<attr>Unknown-Attribute): (?P<value>0{1,6}\w{1,})",
}

default_cfg['user_cfg'] = user_cfg
default_cfg['wlan_cfg'] = wlan_cfg
default_cfg['server_cfg'] = server_cfg


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)

    _cfg['server'] = _config_create_linux_pc(_cfg)

    _cfg['sta'] = _config_create_sta(_cfg)
    _config_remove_sta_wlan(_cfg)

    _cfg['zd'] = _config_create_zd(_cfg)
    _config_create_aaa_server(_cfg)
    _config_create_wlan_on_zd(_cfg)
    _config_create_local_user(_cfg)

    return _cfg


def do_test(cfg):
    cfg['errmsg'] = ""

    res = {
        'acct_status_type': _tc_verify_attr_acct_status_type,
        'acct_session_time': _tc_verify_attr_acct_session_time,
        'acct_session_id': _tc_verify_attr_acct_session_id,
        'acct_multi_session_id': _tc_verify_attr_acct_multi_session_id,
        'acct_ruckus_sta_rssi': _tc_verify_attr_ruckus_sta_rssi,
        'acct_new_interim_update': _tc_verify_new_interim_update,
        'acct_backup_accounting': _tc_verify_backup_accounting,
    }[cfg['tc2f']](cfg)

    if cfg['errmsg']:
        cfg['result'] = "FAIL"
        return cfg

    cfg['result'] = "PASS"
    return cfg


def do_clean_up(cfg):
    _config_remove_sta_wlan(cfg)
    _cleanup_remove_zd_config(cfg)


def main(**kwa):
    # update info for server_cfg
    for key in kwa.keys():
        if key in server_cfg:
            server_cfg[key] = kwa[key]

    tcfg = do_config(kwa)
    res = None
    try:
        res = do_test(tcfg)

    finally:
        do_clean_up(tcfg)

    return (res['result'], res['errmsg'])


def _get_retry_timeout(cfg):
    '''
    '''
    timeout = int(cfg['server_cfg']['primary_timeout'])
    timeout = timeout * int(cfg['server_cfg']['failover_retries'])

    return timeout


def _get_reconnect_time(cfg):
    '''
    For Accounting Server Failover,
      reconnect_time = primary_reconnect + interim_update
    '''
    timeout = int(cfg['server_cfg']['primary_reconnect'])
    interim = int(cfg['wlan_cfg']['interim_update'])
    timeout = (timeout + interim) * 60

    return timeout


def _get_interim_update_time(cfg):
    '''
    '''
    interim = int(cfg['wlan_cfg']['interim_update'])
    timeout = interim * 60

    return timeout


def _wait_for_event(timeout, event = ""):
    '''
    '''
    logging.info("Waiting %s seconds for %s event..." % (timeout, event))
    time.sleep(timeout)


def _config_create_zd(cfg):
    '''
    '''
    cfg['zd'] = create_zd_by_ip_addr(cfg['zd_ip_addr'])
    cfg['zd_cli'] = create_zd_cli_by_ip_addr(shell_key = cfg['shell_key'])
    cfg['zd'].init_messages_bundled(cfg['zd_cli'])

    return cfg['zd']


def _config_create_linux_pc(cfg):
    '''
    '''
    cfg['servers'] = {}
    server_ip = cfg['server_cfg']['server_addr']
    cfg['servers'].update({server_ip: create_server_by_ip_addr(server_ip)})

    return cfg['servers']


def _config_create_sta(cfg):
    '''
    '''
    cfg['sta'] = create_station_by_ip_addr(cfg['sta_ip_addr'])

    return cfg['sta']


def _config_remove_zd_cfg(cfg):
    '''
    '''
    logging.info("Remove all configuration from the Zone Director")
    cfg['zd'].remove_all_cfg()


def _config_remove_sta_wlan(cfg):
    '''
    '''
    tconfig.remove_all_wlan_from_station(
        cfg['sta'], check_status_timeout = cfg['check_status_timeout']
    )


def _config_create_aaa_server(cfg):
    '''
    '''
    logging.info("Configure Radius Server with backup support enable")
    try:
        lib.zd.aaa.create_server(cfg['zd'], **cfg['server_cfg'])

    except Exception, e:
        for msg in aaa_static_msg:
            if msg in e.message:
                logging.info("Catch the invalid server settings error [%s]" % e.message)
                return ''

        else:
            logging.info("Catch the error when creating a server [%s]" % e.message)
            return e.message


def _config_create_wlan_on_zd(cfg):
    '''
    '''
    logging.info("Configure a WLAN with SSID [%s] on the Zone Director" %
                 cfg['wlan_cfg']['ssid'])
    lib.zd.wlan.create_wlan(cfg['zd'], cfg['wlan_cfg'])
    time.sleep(10)


def _config_create_local_user(cfg):
    '''
    '''
    user_cfg = {
        'username': cfg['user_cfg']['username'],
        'password': cfg['user_cfg']['password'],
        'confirm_password': cfg['user_cfg']['password'],
    }
    user.create_user(cfg['zd'], user_cfg)


def _config_start_tshark_capture_packets(cfg):
    '''
    /usr/sbin/tshark -f "udp port 1813" -i eth0 -w /tmp/tshark_capture.pcap
    '''
    server_ip = cfg['current_server_ip']
    server = cfg['servers'][server_ip]
    server_interface = server.get_interface_name_by_ip(server_ip)
    server_port = cfg['current_server_port']

    server.cmd("pkill tcpdump")

    cap_file = "/tmp/tshark_capture.pcap"
    server.cmd("rm -f %s" % cap_file)

    cap_filter = "udp port %s" % server_port
    cap_inf = "%s" % server_interface
    cap_file = "/tmp/tshark_capture.pcap"
    cmd = "/usr/sbin/tshark -f '%s' -i %s -w %s &" % (cap_filter, cap_inf, cap_file)
    server.cmd(cmd)

    cfg['is_sniffing'] = True


def _config_read_tshark_captured_packets(cfg):
    '''
    /usr/sbin/tshark -nVr /tmp/tshark_capture.pcap | grep "AVP:"
    '''
    server_ip = cfg['current_server_ip']
    server = cfg['servers'][server_ip]

    cap_file = "/tmp/tshark_capture.pcap"
    cmd = "/usr/sbin/tshark -nVr %s" % (cap_file)
    packets_captured = server.cmd(cmd)

    return packets_captured


def _config_set_default_acct_server(cfg, server = 'primary'):
    '''
    '''
    cfg['current_server_ip'] = cfg['server_cfg']['server_addr']
    cfg['current_server_port'] = cfg['server_cfg']['server_port']


def _config_swap_interim_update(cfg, interim_update = 3):
    '''
    '''
    cfg['wlan_cfg']['interim_update'], interim_update = \
        interim_update, cfg['wlan_cfg']['interim_update']

    return interim_update


def _test_find_acct_packets(cfg, patterns_list = [], filter_string = ''):
    '''
    '''
    acct_trap_packets = []

    packets_captured = _config_read_tshark_captured_packets(cfg)
    logging.debug(packets_captured)

    for packet in packets_captured:
        for pattern in patterns_list:
            matcher = re.compile(pattern).search(packet)
            if matcher:
                result = matcher.groupdict()
                acct_trap_packets.append(result)

    # finish checking all packets and all patterns
    return acct_trap_packets


def _test_start_radius(cfg, server_ip):
    '''
    '''
    server = cfg['servers'][server_ip]
    server.start_radius_server()


def _test_stop_radius(cfg, server_ip):
    '''
    '''
    server = cfg['servers'][server_ip]
    server.stop_radius_server()


def _test_edit_aaa_cfg(cfg, server = 'primary', config = 'reachable'):
    '''
    '''
    tmp_port = 1234
    new_cfg = {
        'primary': {
            'server_addr': cfg['server_cfg']['server_addr'],
            'server_port': {
                'reachable': cfg['server_cfg']['server_port'],
                'unreachable': tmp_port,
            }[config],
        },
        'secondary': {
            'secondary_server_addr': cfg['server_cfg']['secondary_server_addr'],
            'secondary_server_port': {
                'reachable': cfg['server_cfg']['secondary_server_port'],
                'unreachable': tmp_port,
            }[config],
        }
    }

    lib.zd.aaa.edit_server(cfg['zd'], cfg['server_cfg']['server_name'], new_cfg[server])


def _test_make_failover_event(cfg, server = 'primary', config = 'reachable'):
    '''
    '''
    if cfg['failover_behavior'] == "config":
        return _test_edit_aaa_cfg(cfg, server, config)

    elif cfg['failover_behavior'] == "service":
        return {
            'reachable': _test_start_radius,
            'unreachable': _test_stop_radius,
        }[config](cfg, {'primary': cfg['server_cfg']['server_addr'],
                        'secondary': cfg['server_cfg']['secondary_server_addr'],
                       }[server]
                  )


def _test_assoc_station_with_ssid(cfg):
    '''
    '''
    cfg['errmsg'] = tmethod.assoc_station_with_ssid(
        cfg['sta'], cfg['wlan_cfg'],
        cfg['check_status_timeout']
    )


def _test_get_sta_wifi_ip(cfg):
    '''
    '''
    res, val1, val2 = tmethod.renew_wifi_ip_address(
        cfg['sta'], cfg['check_status_timeout']
    )

    if not res:
        raise Exception(val2)

    cfg['sta_wifi_ip_addr'] = val1
    cfg['sta_wifi_mac_addr'] = val2.lower()


def _test_reconnect_station_to_wlan(cfg):
    '''
    '''
    _config_remove_sta_wlan(cfg)
    _test_assoc_station_with_ssid(cfg)

    _test_get_sta_wifi_ip(cfg)
    _test_stat_connectivity(cfg)


def _test_stat_connectivity(cfg):
    '''
    '''
    cfg['errmsg'] = tmethod.client_ping_dest_is_allowed(
        cfg['sta'], cfg['des_ip'],
        ping_timeout_ms = cfg['ping_timeout_ms']
    )


def _test_acct_when_client_roaming(cfg, patterns_list):
    '''
    '''
    _config_set_default_acct_server(cfg)

    _config_start_tshark_capture_packets(cfg)

    _test_reconnect_station_to_wlan(cfg)


    # before roaming
    acct_trap_packets = _test_find_acct_packets(cfg, patterns_list)
    session_id_prior_roaming = acct_trap_packets

    _config_start_tshark_capture_packets(cfg)

    # roaming
    _test_make_client_roam(cfg)


    # after roaming
    acct_trap_packets = _test_find_acct_packets(cfg, patterns_list)
    session_id_after_roaming = acct_trap_packets

    return session_id_prior_roaming, session_id_after_roaming


def _test_make_client_roam(cfg):
    '''
    '''
    clients = lib.zd.cac.get_all_clients_briefs(cfg['zd'])
    for client_info in clients.itervalues():
        ap_mac_addr = client_info['ap']
        lib.zd.aps.reboot_ap_by_mac_addr(cfg['zd'], ap_mac_addr)

    time.sleep(30)


def _test_verify_session_id(
        cfg, session_id_prior_roaming, session_id_after_roaming
    ):
    '''
    '''
    if not session_id_prior_roaming or not session_id_after_roaming:
        cfg['errmsg'] = "Not all Session ID are captured"
        logging.debug(cfg['errmsg'])
        return False

    session_id_list = session_id_prior_roaming
    session_id_list.extend(session_id_after_roaming)

    count = 0
    for i in range(1, len(session_id_list)):
        if session_id_list[i] != session_id_list[i - 1]:
            count += 1

    if count == 0:
        cfg['errmsg'] = "No new Session ID generated"
        logging.debug(cfg['errmsg'])
        return False

    return True


def _test_verify_multi_session_id(
        cfg, session_id_prior_roaming, session_id_after_roaming
    ):
    '''
    '''
    if not session_id_prior_roaming or not session_id_after_roaming:
        cfg['errmsg'] = "Not all Multi Session ID are captured"
        logging.debug(cfg['errmsg'])
        return False

    session_id_list = session_id_prior_roaming
    session_id_list.extend(session_id_after_roaming)

    for i in range(1, len(session_id_list)):
        if session_id_list[i] != session_id_list[i - 1]:
            cfg['errmsg'] = "Not all Multi Session ID are the same"
            logging.debug(cfg['errmsg'])
            return False

    return True


def _test_verify_interim_update(cfg, acct_trap_packets, periods, interval):
    '''
    '''
    session_time_list = []

    for packet in acct_trap_packets:
        if packet['attr'] == "Acct-Session-Time":
            session_time_list.append(int(packet['value']))

    session_time_list = session_time_list[-periods:]
    logging.debug(session_time_list)
    cfg['session_time_list'] = session_time_list

    for i in range(1, len(session_time_list)):
        if session_time_list[i] - session_time_list[i - 1] != interval:
            cfg['errmsg'] = "Not all Interim-Update are correct"
            logging.debug(cfg['errmsg'])
            return False

    return True


def _cleanup_remove_zd_config(cfg, do_full = False):
    logging.info("Remove all configuration from the Zone Director")
    if not do_full:
        cfg['zd'].remove_all_users()
        cfg['zd'].remove_all_wlan()
        cfg['zd'].remove_all_auth_servers()
        return

    cfg['zd'].remove_all_cfg()


def _tc_verify_attr_acct_status_type(cfg):
    '''
    '''
    _config_set_default_acct_server(cfg)

    _config_start_tshark_capture_packets(cfg)

    _test_reconnect_station_to_wlan(cfg)

    patterns_list = [
        ACCT_PATTERNS['acct_status_start'],
    ]
    acct_trap_packets = _test_find_acct_packets(cfg, patterns_list)

    logging.debug(acct_trap_packets)

    if not acct_trap_packets:
        cfg['errmsg'] = "Accounting Status Start was not captured"
        logging.debug(cfg['errmsg'])

    if cfg['errmsg']:
        return cfg

    cfg['passmsg'] = "Accounting Status Start was captured"
    logging.debug(cfg['passmsg'])


def _tc_verify_attr_acct_session_time(cfg, periods = 3, reconnect_sta = True):
    '''
    '''
    _config_set_default_acct_server(cfg)

    _config_start_tshark_capture_packets(cfg)

    if reconnect_sta:
        _test_reconnect_station_to_wlan(cfg)

    patterns_list = [
        ACCT_PATTERNS['acct_status_interim_update'],
        ACCT_PATTERNS['acct_session_time'],
    ]

    interval = _get_interim_update_time(cfg)
    timeout = periods * interval
    _wait_for_event(timeout, "Interim-Update")

    acct_trap_packets = _test_find_acct_packets(cfg, patterns_list)

    _test_verify_interim_update(cfg, acct_trap_packets, periods, interval)

    if cfg['errmsg']:
        return cfg

    cfg['passmsg'] = "All Accounting Interim-Update are correct"
    logging.debug(cfg['passmsg'])


def _tc_verify_attr_acct_session_id(cfg):
    '''
    '''
    patterns_list = [
        ACCT_PATTERNS['acct_session_id'],
    ]

    session_id_prior_roaming, session_id_after_roaming = \
        _test_acct_when_client_roaming(cfg, patterns_list)

    _test_verify_session_id(
        cfg, session_id_prior_roaming, session_id_after_roaming
    )

    if cfg['errmsg']:
        return cfg

    cfg['passmsg'] = "New Session ID is generated when roaming"
    logging.debug(cfg['passmsg'])


def _tc_verify_attr_acct_multi_session_id(cfg):
    '''
    '''
    patterns_list = [
        ACCT_PATTERNS['acct_multi_session_id'],
    ]

    session_id_prior_roaming, session_id_after_roaming = \
        _test_acct_when_client_roaming(cfg, patterns_list)

    _test_verify_multi_session_id(
        cfg, session_id_prior_roaming, session_id_after_roaming
    )

    if cfg['errmsg']:
        return cfg

    cfg['passmsg'] = "All Multi Session IDs are the same"
    logging.debug(cfg['passmsg'])


def _tc_verify_attr_ruckus_sta_rssi(cfg, periods = 1):
    '''
    '''
    _config_set_default_acct_server(cfg)

    _config_start_tshark_capture_packets(cfg)

    _test_reconnect_station_to_wlan(cfg)

    patterns_list = [
        ACCT_PATTERNS['vendor_specific'],
    ]

    interval = _get_interim_update_time(cfg)
    timeout = periods * interval
    _wait_for_event(timeout, "Interim-Update")

    acct_trap_packets = _test_find_acct_packets(cfg, patterns_list)

    if not acct_trap_packets:
        cfg['errmsg'] = "Ruckus-Sta-RSSI was not captured"
        logging.debug(cfg['errmsg'])

    if cfg['errmsg']:
        return cfg

    cfg['passmsg'] = "Ruckus-Sta-RSSI was captured"
    logging.debug(cfg['passmsg'])


def _tc_verify_new_interim_update(cfg, periods = 3):
    '''
    client-side only as we don't change server's configuration
    '''
    interim_update = _config_swap_interim_update(cfg)

    lib.zd.wlan.edit_wlan(cfg['zd'], cfg['wlan_cfg']['ssid'], cfg['wlan_cfg'])

    _tc_verify_attr_acct_session_time(cfg, periods)

    _config_swap_interim_update(cfg, interim_update)

    lib.zd.wlan.edit_wlan(cfg['zd'], cfg['wlan_cfg']['ssid'], cfg['wlan_cfg'])

    if cfg['errmsg']:
        return cfg

    logging.debug(cfg['passmsg'])


def _tc_verify_backup_accounting(cfg, periods = 3):
    '''
    client-side only as we don't change server's configuration
    '''
    _tc_verify_attr_acct_session_time(cfg, periods)
    session_time_list_prior_outage = cfg['session_time_list']

    _test_make_failover_event(cfg, 'primary', 'unreachable')
    _wait_for_event(_get_retry_timeout(cfg), "Accounting Primary Failover")

    _test_make_failover_event(cfg, 'primary', 'reachable')
    _wait_for_event(_get_reconnect_time(cfg), "Accounting Primary Reconnect")

    _tc_verify_attr_acct_session_time(cfg, periods, False)
    session_time_list_after_reconnect = cfg['session_time_list']

    session_time_last_outage = session_time_list_prior_outage[-1:][0]
    session_time_first_reconnect = session_time_list_after_reconnect[0]

    if session_time_first_reconnect <= session_time_last_outage:
        cfg['errmsg'] = "Acct-Session-Time is not incremented after reconnection"
        logging.debug(cfg['errmsg'])

    if cfg['errmsg']:
        return cfg

    cfg['passmsg'] = "Acct-Session-Time is incremented after reconnection"
    logging.debug(cfg['passmsg'])

