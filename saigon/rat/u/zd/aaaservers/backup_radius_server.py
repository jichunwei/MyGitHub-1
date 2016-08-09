'''
User's parameters:
@param tc2f:
  - 'configurable'
  - 'primary_timeout',
  - 'primary_reconnect',
  - 'server_outage',
  - 'image_upgrade',
  - 'backup_restore',
  - 'zeroit_activation',
  - 'guestpass_generation',
  - 'admin_auth',

Examples:

TC ZD-183:Failover from Primary to Secondary RADIUS Server
    tea.py u.zd.aaaservers.backup_radius_server tc2f='primary_timeout'

TC ZD-181:Primary/Secondary RADIUS - Configurable
  1. Both Primary and Secondary RADIUS servers have the same IP address
    tea.py u.zd.aaaservers.backup_radius_server tc2f='configurable' negative_condition='same_ip'

  2. IP Address = "0.0.0.0"
    tea.py u.zd.aaaservers.backup_radius_server tc2f='configurable' negative_condition='zero_ip'

  3. IP Address = "255.255.255.255"
    tea.py u.zd.aaaservers.backup_radius_server tc2f='configurable' negative_condition='broadcast_ip'

  4. Only input one IP address
    tea.py u.zd.aaaservers.backup_radius_server tc2f='configurable' negative_condition='missing_ip'

  (5. Valid IP address) <- Skip

  6. Wildcard Characters (ex. "*", "?"...)
    tea.py u.zd.aaaservers.backup_radius_server tc2f='configurable' negative_condition='wildcard'

TC ZD-184:Primary Server Reconnection after Failover
    tea.py u.zd.aaaservers.backup_radius_server tc2f='primary_reconnect'

TC ZD-185:Primary/Secondary RADIUS Availability
    tea.py u.zd.aaaservers.backup_radius_server tc2f='server_outage'

TC ZD-177:Restore previous configuration when Imaged upgrade/downgrade
    tea.py u.zd.aaaservers.backup_radius_server tc2f='image_upgrade'

'''
import logging
import time
import copy

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_server_by_ip_addr,
    create_station_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd import user
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_ruckus_build_access as build_access

auth_list = ['EAP'] # only 802.1x EAP is being tested
encryption_list = ['TKIP', 'AES'] # per test cases requirement
wpa_ver_list = ['WPA', 'WPA2']

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
    'negative_condition': "same_ip", # ["same_ip", "zero_ip", "broadcast_ip",
                                     #  "missing_ip", "wildcard"]
}

server_cfg_kv = {
    'IAS': {
        'server_addr': "192.168.0.250",
        'server_port': "18120",
    },
    'FreeRADIUS': {
         'server_addr': "192.168.0.252",
         'server_port': "1812",
    },
    'FreeRADIUS.2': {
         'server_addr': "192.168.0.242",
         'server_port': "1812",
    }
}

server_cfg = {
    'server_name': "RadiusAuth",
    'server_addr': server_cfg_kv['FreeRADIUS']['server_addr'],
    'server_port': server_cfg_kv['FreeRADIUS']['server_port'],
    'radius_auth_secret': "1234567890",
    'secondary_server_addr': server_cfg_kv['FreeRADIUS.2']['server_addr'],
    'secondary_server_port': server_cfg_kv['FreeRADIUS.2']['server_port'],
    'secondary_radius_auth_secret': "1234567890",
    'primary_timeout': "3", # 3 seconds
    'failover_retries': "2", # 2 times
    'primary_reconnect': "2", # 5 minutes
}

user_cfg = {
    'username': 'ras.eap.user',
    'password': 'ras.eap.user',
}

wlan_cfg = {
    'ssid': "rat-backup-radius-server",
    'auth': auth_list[0],
    'wpa_ver': wpa_ver_list[0],
    'encryption': encryption_list[0],
    'key_index': "" ,
    'key_string': "",
    'username': user_cfg['username'],
    'password': user_cfg['password'],
    'auth_svr': server_cfg['server_name'],
}

upgrade_cfg = {
    'upgrade': {
        'image_file_path': r"D:\Downloads\builds\9.2.0.0\688.tar.gz",
        'force_upgrade': True,
        'rm_data_files': False,
    },
    'downgrade': {
        'build_stream': 'ZD3000_mainline',
        'build_number': '688',
        'image_file_path': r"",
        'force_upgrade': False,
        'rm_data_files': False,
    }
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

default_cfg['user_cfg'] = user_cfg
default_cfg['wlan_cfg'] = wlan_cfg
default_cfg['server_cfg'] = server_cfg
default_cfg['upgrade_cfg'] = upgrade_cfg


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)

    if _cfg['failover_behavior'] == 'service':
        _cfg['servers'] = _config_create_linux_pc(_cfg)
        _config_start_radius_servers(_cfg)

    _cfg['sta'] = _config_create_sta(_cfg)
    _config_remove_sta_wlan(_cfg)

    _cfg['zd'] = _config_create_zd(_cfg)
    _config_create_aaa_server(_cfg)
    _config_create_wlan_on_zd(_cfg)

    return _cfg


def do_test(cfg):
    cfg['errmsg'] = ""

    res = {
        'configurable': _tc_server_configurable_negative,
        'primary_timeout': _tc_primary_server_timeout,
        'primary_reconnect': _tc_primary_server_reconnect,
        'server_outage': _tc_server_outage,
        'image_upgrade': _tc_combination_with_upgrade,
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



def _download_build(build_stream, build_number):
    '''
    '''
    build_url = build_access.get_build_url(build_stream, build_number)

    if not build_url:
        errmsg = 'There is not any URL for the build %s.%s'
        errmsg = errmsg % (build_stream.split('_')[1], build_number)
        raise Exception(errmsg)

    return build_access.download_build(build_url)


def _wait_for_event(timeout):
    logging.info("Waiting %s seconds for Failover/Reconnect/Outage Event..." % timeout)
    time.sleep(timeout)


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
    interim = 0 #int(cfg['wlan_cfg']['interim_update'])
    timeout = (timeout + interim) * 60

    return timeout



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

    server_ip = cfg['server_cfg']['secondary_server_addr']
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


def _config_clear_events(cfg):
    '''
    '''
    cfg['zd'].clear_all_events()


def _config_start_radius_servers(cfg):
    '''
    '''
    for server_ip, server in cfg['servers'].iteritems():
        server.start_radius_server()


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


def _test_upgrade_downgrade(cfg, option = 'upgrade'):
    '''
    '''
    _cfg = cfg['upgrade_cfg'][option]
    try:
        if not _cfg['image_file_path']:
            _cfg['image_file_path'] = _download_build(
                _cfg['build_stream'], _cfg['build_number']
            )

        if _cfg['image_file_path'].endswith(".img"):
            cfg['zd']._upgrade_zd(_cfg['image_file_path'])
            cfg['zd']._check_upgrade_sucess()

        elif _cfg['image_file_path'].endswith(".tar.gz"):
            cfg['zd'].upgrade_sw(
                filename = _cfg['image_file_path'],
                force_upgrade = _cfg['force_upgrade'],
                rm_data_files = _cfg['rm_data_files']
            )

        cfg['passmsg'] = "The '%s' process worked successfully" % option

    except Exception, e:
        cfg['errmsg'] = "[Error in '%s']: %s" % (option, e.message)



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


def _test_check_event(cfg, change = 'failover', server = 'secondary'):
    '''
    change = ['failover', 'reconnect', 'outage']
    server = ['secondary', 'primary']
    '''
    logging.info("Verify All Events/Activities for the '%s' event message" % change)
    cfg['zd'].re_navigate()
    events_log = cfg['zd'].get_events()
    logging.info(events_log)


    #MSG_RADIUS_auth_failover=SSID{id} RADIUS authenticaion server {change} to {server}.
    #SSID[rat-backup-radius-server] RADIUS authenticaion server [failover] to [secondary 192.168.0.250].
    #SSID[rat-backup-radius-server] RADIUS authenticaion server [reconnect] to [primary 192.168.0.252].
    if server in ['secondary']:
        server_ip = cfg['server_cfg']['secondary_server_addr']

    elif server in ['primary']:
        server_ip = cfg['server_cfg']['server_addr']


    pattern1 = cfg['zd'].messages['MSG_RADIUS_auth_failover']
    pattern1 = pattern1.replace('{id}', '[%s]' % cfg['wlan_cfg']['ssid'])
    pattern1 = pattern1.replace('{change}', '[%s]' % change)
    pattern1 = pattern1.replace('{server}', '[%s %s]' % (server, server_ip))

    #MSG_RADIUS_service_outage=Radius server {server} has not responded to multiple requests.  {reason}.
    #Radius server [192.168.0.242] has not responded to multiple requests. [This server may be down or unreachable.].
    pattern2 = cfg['zd'].messages['MSG_RADIUS_service_outage']
    pattern2 = pattern2.replace('{server}', '[%s]' % server_ip)
    pattern2 = pattern2.replace('  {reason}.', '')


    for event in events_log:
        if (change in ['failover', 'reconnect'] and pattern1 in event[-1]) or \
        (change in ['outage'] and pattern2 in event[-1]):
            cfg['passmsg'] = "The '%s' event is generated. " % change
            cfg['passmsg'] = cfg['passmsg'] + event[-1]
            cfg['errmsg'] = ""
            return

    cfg['errmsg'] = "There is no '%s' event message generated when radius server is down" % change


def _cleanup_remove_zd_config(cfg, do_full = False):
    logging.info("Remove all configuration from the Zone Director")
    if not do_full:
        cfg['zd'].remove_all_users()
        cfg['zd'].remove_all_wlan()
        cfg['zd'].remove_all_auth_servers()
        return

    cfg['zd'].remove_all_cfg()



def _tc_primary_server_timeout(cfg):
    '''
    ZD-183:Failover from Primary to Secondary RADIUS Server
    '''
    _config_clear_events(cfg)

    _test_make_failover_event(cfg, 'primary', 'unreachable')

    _wait_for_event(_get_retry_timeout(cfg))
    _test_reconnect_station_to_wlan(cfg)

    _test_check_event(cfg, 'failover', 'secondary')

    _test_make_failover_event(cfg, 'primary', 'reachable')

    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg

    logging.debug(cfg['passmsg'])


def _tc_primary_server_reconnect(cfg):
    '''
    ZD-184:Primary Server Reconnection after Failover
    '''
    _config_clear_events(cfg)
    _test_make_failover_event(cfg, 'primary', 'unreachable')
    _wait_for_event(_get_retry_timeout(cfg))
    _test_reconnect_station_to_wlan(cfg)

    _test_make_failover_event(cfg, 'primary', 'reachable')
    _wait_for_event(_get_reconnect_time(cfg))
    _test_reconnect_station_to_wlan(cfg)

    _test_check_event(cfg, 'reconnect', 'primary')

    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg

    logging.debug(cfg['passmsg'])


def _tc_server_outage(cfg, failover = 'primary'):
    '''
    ZD-185:Primary/Secondary RADIUS Availability
    '''
    _config_clear_events(cfg)
    _test_make_failover_event(cfg, 'primary', 'unreachable')
    _test_make_failover_event(cfg, 'secondary', 'unreachable')
    _wait_for_event(_get_retry_timeout(cfg))
    _wait_for_event(_get_reconnect_time(cfg))
    _test_reconnect_station_to_wlan(cfg)

    _test_check_event(cfg, 'outage', 'primary')
    _test_check_event(cfg, 'outage', 'secondary')

    if failover != 'primary':
        _test_make_failover_event(cfg, 'secondary', 'reachable')
        _test_reconnect_station_to_wlan(cfg)
        _test_check_event(cfg, 'failover', 'secondary')

    if failover != 'secondary':
        _test_make_failover_event(cfg, 'primary', 'reachable')
        _test_reconnect_station_to_wlan(cfg)
        _test_check_event(cfg, 'reconnect', 'primary')


    _test_make_failover_event(cfg, 'primary', 'reachable')
    _test_make_failover_event(cfg, 'secondary', 'reachable')

    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg

    logging.debug(cfg['passmsg'])


def _tc_combination_with_upgrade(cfg):
    '''
    ZD-189:Restore previous configuration when Imaged upgrade/downgrade

    To verify the Backup Radius Server function works properly after
    ZD has been upgraded (9.0 to 9.2 based on default config)
    '''
    _test_upgrade_downgrade(cfg, 'upgrade')
    _tc_primary_server_timeout(cfg)


def _tc_server_configurable_negative(cfg):
    '''
    Primary/Secondary RADIUS - Configurable

    Negative test for invalid IP address. ZD fires an alert if invalid
    IP address is entered.
      1. Both Primary and Secondary RADIUS servers have the same IP address
      2. IP Address = "0.0.0.0"
      3. IP Address = "255.255.255.255"
      4. Only input one IP address
      (5. Valid IP address) <- Skip
      6. Wildcard Characters (ex. "*", "?"...)
    '''
    neg_cfg = {
        'same_ip': cfg['server_cfg']['secondary_server_addr'],
        'zero_ip': '0.0.0.0',
        'broadcast_ip': '255.255.255.255',
        'missing_ip': '',
        'wildcard': '192.168.0.???',
    }

    tmp_cfg = copy.deepcopy(cfg['server_cfg'])
    tmp_cfg.update({
        'server_name': "RadiusAuth-Invalid",
        'server_addr': neg_cfg[cfg['negative_condition']]
    })

    logging.info("Verify ZD fires an alert when invalid Radius config provided")
    try:
        lib.zd.aaa.create_server(cfg['zd'], **tmp_cfg)

    except Exception, e:
        for msg in aaa_static_msg:
            if msg in e.message:
                logging.info("Catch the invalid server settings error [%s]" % e.message)
                return ""

        else:
            logging.info("Catch the error when creating a server [%s]" % e.message)
            return e.message

