'''
User's parameters:
@param tc2f:
  - 'vlan_connectivity',
  - 'client_list',
  - 'client_details',
  - or other TC names being developed

@param active_ap_mac_list:
  - list of active APs MAC Addr.
  - for TCs using Same AP, this list must have only ONE MAC Addr entry
  - for TCs using Different APs, provide only TWO MAC Addr entries
  - for TCs with 5.0G, provide two APs that support 5.0G

@param ap_radio:
  - AP Radio under test: 'ng' for 2.4G, 'na' for 5.0G.

@param same_wlan:
  - True if using Same WLAN
  - False if using Different WLAN

@param sta_ip_list:
  - list of stations under test, must be at least TWO, but currently two
  stations are being verified connectivity.


Examples:

TC12.1.2
    '2.4G - Clients have different Dynamic VLAN ID - Same AP and Same WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:1f:41:26:47:f0'] ap_radio='ng' same_wlan=True sta_ip_list=['192.168.1.11','192.168.1.12']

TC12.1.3
    '2.4G - Clients have different Dynamic VLAN ID - Same AP and different WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:1f:41:26:47:f0'] ap_radio='ng' same_wlan=False

TC12.1.4
    '2.4G - Clients have different Dynamic VLAN ID - Different AP and same WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['04:4f:aa:0c:b0:e0','00:1f:41:26:47:f0'] ap_radio='ng' same_wlan=True

TC12.1.5
    '2.4G - Clients have different Dynamic VLAN ID - Different AP and different WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:25:c4:13:a7:f0','00:1f:41:26:47:f0'] ap_radio='ng' same_wlan=False

TC12.1.6
    '5G - Clients have different Dynamic VLAN ID - Same AP and Same WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:24:82:26:44:90'] ap_radio='na' same_wlan=True

TC12.1.7
    '5G - Clients have different Dynamic VLAN ID - Same AP and different WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:24:82:26:44:90'] ap_radio='na' same_wlan=False

TC12.1.8
    '5G - Clients have different Dynamic VLAN ID - Different AP and same WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:25:c4:13:a7:f0','00:24:82:26:44:90'] ap_radio='na' same_wlan=True

TC12.1.9
    '5G - Clients have different Dynamic VLAN ID - Different AP and different WLAN'
    tea.py u.zd.dvlan_tea tc2f='vlan_connectivity' active_ap_mac_list=['00:25:c4:13:a7:f0','00:24:82:26:44:90'] ap_radio='na' same_wlan=False

TC12.1.15
    'Client List'
    tea.py u.zd.dvlan_tea tc2f='client_list' active_ap_mac_list=['00:25:c4:13:a7:f0'] ap_radio='ng' sta_ip_list=['192.168.1.11']

TC12.1.16
    'Detailed View of Client'
    tea.py u.zd.dvlan_tea tc2f='client_details' active_ap_mac_list=['00:25:c4:13:a7:f0'] ap_radio='ng' sta_ip_list=['192.168.1.11']

TC12.1.25
    'Backup/Restore'
    tea.py u.zd.dvlan_tea tc2f='backup_restore' active_ap_mac_list=['00:1f:41:26:47:f0'] ap_radio='ng' same_wlan=False sta_ip_list=['192.168.1.11','192.168.1.12']

'''

import copy
import time
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_zd_cli_by_ip_addr,
    create_ruckus_ap_by_ip_addr,
    create_station_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components import Helpers as lib

auth_list = ['EAP'] # only 802.1x EAP is being tested
encryption_list = ['TKIP', 'AES'] # per test cases requirement
wpa_ver_list = ['WPA', 'WPA2']
tunnel_mode = False

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
}

default_cfg = dict(
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

    active_ap_mac_list = [
        '00:1f:41:26:47:f0',
        '00:25:c4:13:a7:f0',
    ],

    sta_ip_list = ['192.168.1.11', '192.168.1.12'],

    ap_radio = radio['2.4'],

    same_wlan = True,

    connection_timed_out = 5 * 1000, # in seconds

)


def _get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = _get_default_cfg()
    _cfg.update(cfg)

    _cfg['zd'] = create_zd_by_ip_addr(_cfg.pop('zd_ip_addr'))

    _cfg.update(_create_ap(_cfg))

    _cfg['server'] = _create_aaa_server(_cfg)

    _create_wlan(_cfg)

    _create_station(_cfg)

    return _cfg


def do_test(cfg):
    cfg['result'] = {}

    return {
        'vlan_connectivity': _tc_vlan_connectivity,
        'client_list': _tc_client_list,
        'client_details': _tc_client_details,
        'backup_restore': _tc_backup_restore,
    }[cfg['tc2f']](cfg)


def do_clean_up(cfg):
    lib.zd.wlan.delete_all_wlans(cfg['zd'])
    lib.zd.aaa.remove_all_servers(cfg['zd'])
    _config_ap_enable_wlan_service(cfg)
    clean_up_rat_env()


def main(**kwa):
    res = None
    tcfg = None

    input_cfg = {}
    input_cfg.update(kwa)
    default_cfg.update(input_cfg)

    try:
        tcfg = do_config(default_cfg)
        res = do_test(tcfg)

    finally:
        do_clean_up(tcfg)

    return res


def _create_aaa_server(cfg):
    '''
    Creates FreeRADIUS authentication server
    - Name: FreeRADIUS
    - Type: RADIUS
    - IP Address: 192.168.0.252
    - Port: 1812
    - Shared Secret: 1234567890
    '''
    cfg['server'] = lib.zd.aaa.create_server(
                        cfg['zd'], **cfg['server_cfg']
                    )

    return cfg


def _create_wlan(cfg):
    '''
    '''
    cfg['wlan_list'] = []
    for i in range(0, len(users_vlan_kv)):
        wlan_cfg = copy.deepcopy(cfg['wlan_cfg'])
        ssid = wlan_cfg['ssid'] + '-%s' % time.strftime("%H%M%S")
        wlan_cfg.update({'ssid': ssid})
        lib.zd.wlan.create_wlan(cfg['zd'], wlan_cfg)

        cfg['wlan_list'].append(ssid)

    return cfg


def _create_ap(cfg):
    '''
    '''
    aps = lib.zd.aps.get_all_ap_briefs(cfg['zd'])

    cfg['aps'] = []
    cfg['active_aps'] = []
    for ap_mac, ap_info in aps.iteritems():
        ap = create_ruckus_ap_by_ip_addr(
                 ap_info['ip'],
                 cfg['zd'].username,
                 cfg['zd'].password,
             )
        cfg['aps'].append(ap)

        if ap.base_mac_addr in cfg['active_ap_mac_list']:
            cfg['active_aps'].append(ap)

    return cfg


def _config_ap_disable_wlan_service(cfg):
    '''
    '''
    for ap in cfg['aps']:
        _config_ap_wlan_service(cfg, ap.base_mac_addr, wlan_service = False)


def _config_ap_enable_wlan_service(cfg):
    '''
    '''
    for ap in cfg['aps']:
        _config_ap_wlan_service(cfg, ap.base_mac_addr, wlan_service = True)


def _config_ap_wlan_service(cfg, ap_mac_addr, radio = None,
                            wlan_service = False):
    '''
    '''
    cfg_set = {'radio': '', 'channel': '', 'wlan_service': wlan_service}
    supported_radio = lib.zd.ap.get_supported_radio(cfg['zd'], ap_mac_addr)

    for r in supported_radio:
        if not radio:
            cfg_set.update({'radio': r, 'wlan_service': wlan_service})

        elif r == radio:
            cfg_set.update({'radio': radio, 'wlan_service': wlan_service})

        lib.zd.ap.cfg_ap(cfg['zd'], ap_mac_addr, cfg_set)


def _create_station(cfg):
    '''
    '''
    cfg['sta_kv'] = {}
    for sta_ip in cfg['sta_ip_list']:
        sta = create_station_by_ip_addr(sta_ip)
        cfg['sta_kv'].update({sta_ip: sta})

    return cfg


def _config_station(cfg):
    '''
    '''
    for sta in cfg['sta_kv'].itervalues():
        _remove_station_wlan(cfg, sta)

    return cfg


def _remove_station_wlan(cfg, sta):
    logging.info("Remove all WLAN profiles on the remote station")
    sta.remove_all_wlan()

    logging.info("Make sure the target station %s disconnects "
                 "from wireless network" % sta.get_ip_addr())

    error_msg = "The station did not disconnect "\
                "from wireless network within %d seconds"

    _check_sta_connection(cfg, sta, "disconnected",
                          cfg['connection_timed_out'], error_msg)

    return cfg


def _associate_client(cfg, sta, wlan_cfg):
    logging.info("Configure a WLAN with SSID %s on the target station %s" %
                 (wlan_cfg['ssid'], sta.get_ip_addr()))
    sta.cfg_wlan(wlan_cfg)

    logging.info("Make sure the station associates to the WLAN")

    error_msg = "The station didn't associate to the wireless network "\
                "after %d seconds"

    _check_sta_connection(cfg, sta, "connected",
                          cfg['connection_timed_out'], error_msg)

    logging.info("Renew IP address of the wireless adapter "
                 "on the target station")
    sta.renew_wifi_ip_address()

    logging.info("Get IP and MAC addresses of the wireless adapter "
                 "on the target station %s" % sta.get_ip_addr())

    start_time = time.time()

    while time.time() - start_time < cfg['connection_timed_out']:
        sta_wifi_ip_addr, sta_wifi_mac_addr = sta.get_wifi_addresses()

        if sta_wifi_mac_addr and sta_wifi_ip_addr \
        and sta_wifi_ip_addr != "0.0.0.0" \
        and not sta_wifi_ip_addr.startswith("169.254"):
            break

        time.sleep(1)

    return cfg


def _check_sta_connection(cfg, sta, status, timeout, error_msg):
    start_time = time.time()
    while True:
        if status == sta.get_current_status():
            return True

        time.sleep(1)
        if time.time() - start_time > timeout:
            errmsg = error_msg % timeout
            raise Exception(errmsg)


def _config_sta_wlan(cfg, sta_ip = '0.0.0.0', ssid = '', vlan_id = '10'):
    '''
    '''
    sta = cfg['sta_kv'][sta_ip]

    wlan_cfg = copy.deepcopy(cfg['wlan_cfg'])
    wlan_cfg.update({'username': users_vlan_kv[vlan_id]['username'],
                     'password': users_vlan_kv[vlan_id]['password']})
    wlan_cfg.update({'ssid': ssid})

    _associate_client(cfg, sta, wlan_cfg)

    return sta


def _check_traffic(cfg, sta_ip, dest_ip, cond = 'allowed', timeout = 10):
    logging.info("Ping to %s from the target station %s" %
                 (dest_ip, sta_ip))

    err_msg = ''
    sta = cfg['sta_kv'][sta_ip]

    ping_result = sta.ping(dest_ip, timeout * 1000)

    if cond == 'disallowed':
        if ping_result.find("Timeout") != -1:
            logging.info('Ping FAILED. Correct behavior.')

        else:
            logging.info('Ping OK. Incorrect behavior.')
            err_msg = 'The target station could send traffic'

    elif cond == 'allowed':
        if ping_result.find("Timeout") != -1:
            logging.info('Ping FAILED. Incorrect behavior.')
            err_msg = 'The target station could not send traffic'

        else:
            logging.info('Ping OK. Correct behavior.')

    return err_msg


def _check_connectivity(cfg):
    '''
    '''
    ### Check the connectivity ###
    # sta1 can reach Internet (172.16.10.252 in VLAN50 in this case)
    sta1_ip_addr = cfg['sta_ip_list'][0]
    dest_cfg = {
        'ip_addr': '172.16.10.252',
        'cond': 'allowed',
    }
    err_msg = _check_traffic(cfg, sta1_ip_addr, dest_cfg['ip_addr'],
                             dest_cfg['cond'])

    if err_msg:
        cfg['result'] = 'FAIL'
        return cfg['result']

    # and sta1 can reach sta2 since they are on different VLANs but have
    # VLAN routing enabled
    sta2 = cfg['sta_kv'][cfg['sta_ip_list'][1]]
    dest_cfg = {
        'ip_addr': sta2.get_wifi_addresses()[0],
        'cond': 'allowed',
    }
    err_msg = _check_traffic(cfg, sta1_ip_addr, dest_cfg['ip_addr'],
                             dest_cfg['cond'])

    if err_msg:
        cfg['result'] = 'FAIL'
        return cfg['result']

    cfg['result'] = 'PASS'

    return cfg['result']


def _tc_vlan_connectivity(cfg):
    '''
    '''
    _config_station(cfg)

    _config_ap_disable_wlan_service(cfg)

    for ap_mac_addr in cfg['active_ap_mac_list']:
        _config_ap_wlan_service(cfg, ap_mac_addr, cfg['ap_radio'],
                                wlan_service = True)

    ### Associate two stations to the same WLAN ###
    # sta1 to VLAN10, sta2 to VLAN20
    sta1_ip = cfg['sta_ip_list'][0]
    sta2_ip = cfg['sta_ip_list'][1]

    if cfg['same_wlan']:
        ssid1 = ssid2 = cfg['wlan_list'][0]

    else:
        ssid1 = cfg['wlan_list'][0]
        ssid2 = cfg['wlan_list'][1]

    cfg[sta1_ip] = _config_sta_wlan(cfg, sta1_ip, ssid1, vlan_id = '10')
    cfg[sta2_ip] = _config_sta_wlan(cfg, sta2_ip, ssid2, vlan_id = '20')

    cfg['result'] = _check_connectivity(cfg)

    return cfg


def _tc_client_list(cfg):
    '''
    '''
    _config_station(cfg)

    _config_ap_disable_wlan_service(cfg)

    for ap_mac_addr in cfg['active_ap_mac_list']:
        _config_ap_wlan_service(cfg, ap_mac_addr, cfg['ap_radio'],
                                wlan_service = True)

    sta1_ip = cfg['sta_ip_list'][0]

    ssid = cfg['wlan_list'][0]

    cfg[sta1_ip] = _config_sta_wlan(cfg, sta1_ip, ssid, vlan_id = '10')

    sta1 = cfg['sta_kv'][cfg['sta_ip_list'][0]]

    sta_info = lib.zd.cac.get_client_brief_by_mac_addr(
                   cfg['zd'], sta1.get_wifi_addresses()[1])

    if sta_info['vlan'] == '10':
        cfg['result'] = 'PASS'

    else:
        cfg['result'] = 'FAIL'

    return cfg['result']


def _tc_client_details(cfg):
    '''
    '''
    _config_station(cfg)

    _config_ap_disable_wlan_service(cfg)

    for ap_mac_addr in cfg['active_ap_mac_list']:
        _config_ap_wlan_service(cfg, ap_mac_addr, cfg['ap_radio'],
                                wlan_service = True)

    sta1_ip = cfg['sta_ip_list'][0]

    ssid = cfg['wlan_list'][0]

    cfg[sta1_ip] = _config_sta_wlan(cfg, sta1_ip, ssid, vlan_id = '10')

    sta1 = cfg['sta_kv'][cfg['sta_ip_list'][0]]

    sta_info = lib.zd.cac.get_client_detail_by_mac_addr(
                   cfg['zd'], sta1.get_wifi_addresses()[1]
               )

    if sta_info['vlan'] == '10':
        cfg['result'] = 'PASS'

    else:
        cfg['result'] = 'FAIL'

    return cfg['result']


def _tc_backup_restore(cfg):
    '''
    '''
    _tc_vlan_connectivity(cfg)

    backup_path = lib.zd.bkrs.backup(cfg['zd'])
    restore_path = backup_path

    rs_cfg = {'restore_file_path': restore_path,
              'restore_type':'restore_everything',
              'timeout': 200,
              'reboot_timeout': 120}

    cfg['zd'].selenium_mgr.start_dlg_manager(cfg['zd'].conf['browser_type'])
    lib.zd.bkrs.restore(cfg['zd'], **rs_cfg)
    cfg['zd'].selenium_mgr.shutdown_dlg_manager()

    return _tc_vlan_connectivity(cfg)
