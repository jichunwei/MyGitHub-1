'''
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib


'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    mac = '00:1f:41:26:47:f0',#'00:22:7f:3d:d7:60'
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    logging.info('[TEST 01] Get all details of an AP by MAC Addr: %s' % cfg['mac'])

    logging.info('[TEST 01.01] Get each table-specific detail. AP MAC Addr: %s' % cfg['mac'])
    logging.info('[TEST 01.01.01] General table: get_ap_detail_general_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_general_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.02] Info table: get_ap_detail_info_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_info_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.03] Radio table: get_ap_detail_radio_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_radio_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.04] WLANs table: get_ap_detail_wlans_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_wlans_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.05] Neighbor APs table: get_ap_detail_neighbor_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_neighbor_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.06] Uplink table: get_ap_detail_uplink_ap_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_uplink_ap_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.07] Uplink History table: get_ap_detail_uplink_aps_history_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_uplink_aps_history_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.08] Downlinks table: get_ap_detail_downlink_aps_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_downlink_aps_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.01.09] MeshTree Uplink/Downlinks tables: get_ap_detail_mesh_tree_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_mesh_tree_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 01.02] Get all at once: get_ap_detail_by_mac_addr')
    pp(lib.zd.aps.get_ap_detail_by_mac_addr(cfg['zd'], cfg['mac']))

    logging.info('[TEST 02] Get all details of ALL APs. This could take up to 1 minute per AP')
    pp(lib.zd.aps.get_all_ap_details(cfg['zd']))

    cfg['result'] = 'PASS'
    cfg['message'] = ''
    return cfg


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)

    res = None
    try:
        res = do_test(tcfg)

    except Exception, ex:
        print ex.message

    do_clean_up(tcfg)

    return res

'''
pydev debugger: starting
[UserExit] model fix_test_param DOES not exist, function ignored at [Sat May 22 13:58:58 2010].
2010-05-22 13:58:59,979 INFO     [TEA.Module u.zd.aps_details_tea] tcfg:
{'u.zd.aps_details_tea': None}
2010-05-22 13:58:59,979 DEBUG    Creating the Selenium Manager
2010-05-22 13:59:04,979 INFO     Creating Zone Director component [192.168.0.2]
2010-05-22 13:59:04,979 DEBUG    {'browser_type': 'firefox',
 'config': {'password': 'admin', 'username': 'admin'},
 'https': True,
 'ip_addr': '192.168.0.2',
 'selenium_mgr': <RuckusAutoTest.common.SeleniumControl.SeleniumManager instance at 0x0235A5D0>}
2010-05-22 13:59:25,026 DEBUG    Updating info in RuckusAutoTest.components.lib.zd.guest_access_zd module to the version 8.2.0.0
2010-05-22 13:59:25,026 DEBUG    Updating const in RuckusAutoTest.components.lib.zd.guest_access_zd module to the version 8.2.0.0
2010-05-22 13:59:25,026 DEBUG    Updating _log_to_the_page in RuckusAutoTest.components.lib.zd.guest_access_zd module to the version 8.2.0.0
2010-05-22 13:59:25,026 DEBUG    Updating xlocs in RuckusAutoTest.components.lib.zd.control_zd module to the version 8.0.0.0
2010-05-22 13:59:25,026 DEBUG    Updating LOCATORS_SPEEDFLEX in RuckusAutoTest.components.lib.zd.speedflex_zd module to the version 9.0.0.99
2010-05-22 13:59:25,026 DEBUG    Updating LOCATORS_CFG_WLANS in RuckusAutoTest.components.lib.zd.wlan_zd module to the version 9.0.0.99
2010-05-22 13:59:25,026 DEBUG    Updating info in RuckusAutoTest.components.ZoneDirector class instance to the version 8.2.0.0
2010-05-22 13:59:25,026 DEBUG    Updating info in RuckusAutoTest.components.ZoneDirector class instance to the version 9.0.0.99
2010-05-22 13:59:25,026 INFO     [TEST 01] Get all details of an AP by MAC Addr: 00:24:82:0a:e7:d0
2010-05-22 13:59:25,026 INFO     [TEST 01.01] Get each table-specific detail. AP MAC Addr: 00:24:82:0a:e7:d0
2010-05-22 13:59:25,026 INFO     [TEST 01.01.01] General table: get_ap_detail_general_by_mac_addr
{'description': u'',
 'devname': u'Mesh1',
 'firmware_version': u'9.0.0.99.519',
 'ip': u'192.168.0.195',
 'mac': u'00:24:82:0a:e7:d0',
 'model': u'zf2942',
 'serial_number': u'520801006384'}

2010-05-22 13:59:49,276 INFO     [TEST 01.01.02] Info table: get_ap_detail_info_by_mac_addr
{'num_sta': u'0',
 'status': u'Connected (Mesh AP, 1 hop)',
 'tunnel_mode': u'L2',
 'uptime': u'3h 5m',
 'wlan_id': u''}

2010-05-22 14:00:11,838 INFO     [TEST 01.01.03] Radio table: get_ap_detail_radio_by_mac_addr
 {'airtime': u'0.0/0.0/0.0/0.0',
 'bgscan': u'Enabled',
 'channel': u'6',
 'channelization': u'',
 'mcast': u'1.27',
 'noisefloor': u'0',
 'num_sta': u'0',
 'phyerr': u'0',
 'retries': u'5.41 / 0.00',
 'rx': u'769K/137M',
 'tx': u'9.95K/1.48M',
 'tx_power': u'100%',
 'wlangroup': u'Default'}
2010-05-22 14:00:39,994 INFO     [TEST 01.01.04] WLANs table: get_ap_detail_wlans_by_mac_addr
{u'rat-test-ap-detail': {u'bssid': u'00:24:82:0a:e7:d9',
                         u'radio_type': u'802.11b/g',
                         u'wlan': u'rat-test-ap-detail'}}

2010-05-22 14:01:01,072 INFO     [TEST 01.01.05] Neighbor APs table: get_ap_detail_neighbor_by_mac_addr
{u'00:22:7f:3d:d7:60': {u'mac': u'00:22:7f:3d:d7:60',
                        u'mesh_uplink_rc': u'N/A (Different radio type)',
                        u'radio_channel': u'1',
                        u'rssi': u'99%'},
 u'00:24:82:0a:e6:70': {u'mac': u'00:24:82:0a:e6:70',
                        u'mesh_uplink_rc': u'35.0 (Connected)',
                        u'radio_channel': u'6',
                        u'rssi': u'99%'}}

2010-05-22 14:01:22,604 INFO     [TEST 01.01.06] Uplink table: get_ap_detail_uplink_ap_by_mac_addr
{'ap': u'00:24:82:0a:e6:70',
 'assoc': u'2010/05/22  10:57:27',
 'desc': u'',
 'retries': u'0.00 pkts',
 'rssi': u'99%',
 'rx': u'10.3K pkts / 762K bytes',
 'tx': u'2.15K pkts / 438K bytes',
 'type': u'Wireless'}
2010-05-22 14:01:47,119 INFO     [TEST 01.01.07] Uplink History table: get_ap_detail_uplink_aps_history_by_mac_addr
{}
2010-05-22 14:02:07,072 INFO     [TEST 01.01.08] Downlinks table: get_ap_detail_downlink_aps_by_mac_addr
{}
2010-05-22 14:02:46,651 INFO     [TEST 01.01.09] MeshTree Uplink/Downlinks tables: get_ap_detail_mesh_tree_by_mac_addr
{'downlink': {},
 'uplink': {'ap': u'00:24:82:0a:e6:70',
            'assoc': u'2010/05/22  10:57:27',
            'desc': u'',
            'retries': u'0.00 pkts',
            'rssi': u'99%',
            'rx': u'10.4K pkts / 768K bytes',
            'tx': u'2.17K pkts / 443K bytes',
            'type': u'Wireless'}}
2010-05-22 14:04:01,713 INFO     [TEST 01.02] Get all at once: get_ap_detail_by_mac_addr
{'downlink': {},
 'general': {'description': u'',
             'devname': u'Mesh1',
             'firmware_version': u'9.0.0.99.519',
             'ip': u'192.168.0.195',
             'mac': u'00:24:82:0a:e7:d0',
             'model': u'zf2942',
             'serial_number': u'520801006384'},
 'info': {'num_sta': u'0',
          'status': u'Connected (Mesh AP, 1 hop)',
          'tunnel_mode': u'L2',
          'uptime': u'3h 10m',
          'wlan_id': u''},
 'neighbor': {u'00:22:7f:3d:d7:60': {u'mac': u'00:22:7f:3d:d7:60',
                                     u'mesh_uplink_rc': u'N/A (Different radio type)',
                                     u'radio_channel': u'1',
                                     u'rssi': u'99%'},
              u'00:24:82:0a:e6:70': {u'mac': u'00:24:82:0a:e6:70',
                                     u'mesh_uplink_rc': u'35.0 (Connected)',
                                     u'radio_channel': u'6',
                                     u'rssi': u'99%'}},
 'radio': {'airtime': u'41.7/19.0/18.7/4.3',
           'bgscan': u'Enabled',
           'channel': u'6',
           'channelization': u'',
           'mcast': u'1.26',
           'noisefloor': u'-93',
           'num_sta': u'0',
           'phyerr': u'678',
           'retries': u'5.53 / 0.00',
           'rx': u'788K/140M',
           'tx': u'10.8K/1.58M',
           'tx_power': u'100%',
           'wlangroup': u'Default'},
 'uplink': {'ap': u'00:24:82:0a:e6:70',
            'assoc': u'2010/05/22  10:57:27',
            'desc': u'',
            'retries': u'0.00 pkts',
            'rssi': u'99%',
            'rx': u'10.5K pkts / 772K bytes',
            'tx': u'2.19K pkts / 446K bytes',
            'type': u'Wireless'},
 'wlans': {u'rat-test-ap-detail': {u'bssid': u'00:24:82:0a:e7:d9',
                                   u'radio_type': u'802.11b/g',
                                   u'wlan': u'rat-test-ap-detail'}}}
2010-05-22 14:09:01,792 INFO     [TEST 02] Get all details of ALL APs. This could take up to 1 minute per AP
{u'00:22:7f:3d:d7:60': {'downlink': {},
                        'general': {'description': u'',
                                    'devname': u'Root2',
                                    'firmware_version': u'9.0.0.99.546',
                                    'ip': u'192.168.0.199',
                                    'mac': u'00:22:7f:3d:d7:60',
                                    'model': u'zf7942',
                                    'serial_number': u'490801009148'},
                        'info': {'num_sta': u'0',
                                 'status': u'Connected (Root AP)',
                                 'tunnel_mode': u'L2',
                                 'uptime': u'19h 13m',
                                 'wlan_id': u''},
                        'neighbor': {u'00:24:82:0a:e6:70': {u'mac': u'00:24:82:0a:e6:70',
                                                            u'mesh_uplink_rc': u'N/A (Different radio type)',
                                                            u'radio_channel': u'6',
                                                            u'rssi': u'99%'},
                                     u'00:24:82:0a:e7:d0': {u'mac': u'00:24:82:0a:e7:d0',
                                                            u'mesh_uplink_rc': u'N/A (Different radio type)',
                                                            u'radio_channel': u'6',
                                                            u'rssi': u'99%'}},
                        'radio': {'airtime': u'22.4/9.4/11.3/2.1',
                                  'bgscan': u'Enabled',
                                  'channel': u'1',
                                  'channelization': u'20',
                                  'mcast': u'0.00',
                                  'noisefloor': u'-88',
                                  'num_sta': u'0',
                                  'phyerr': u'101',
                                  'retries': u'3.49 / 0.00',
                                  'rx': u'3.72M/652M',
                                  'tx': u'249K/73.1M',
                                  'tx_power': u'100%',
                                  'wlangroup': u'Default'},
                        'uplink': {'ap': u'',
                                   'assoc': u'0',
                                   'desc': u'',
                                   'retries': u'',
                                   'rssi': u'',
                                   'rx': u'',
                                   'tx': u'',
                                   'type': u''},
                        'wlans': {u'rat-test-ap-detail': {u'bssid': u'00:22:7f:3d:d7:69',
                                                          u'radio_type': u'802.11g/n',
                                                          u'wlan': u'rat-test-ap-detail'}}},
 u'00:22:7f:3d:d8:f0': {'downlink': {},
                        'general': {'description': u'',
                                    'devname': u'Mesh2',
                                    'firmware_version': u'9.0.0.99.546',
                                    'ip': u'192.168.0.198',
                                    'mac': u'00:22:7f:3d:d8:f0',
                                    'model': u'zf7942',
                                    'serial_number': u'490801008917'},
                        'info': {'num_sta': u'0',
                                 'status': u'Disconnected (2010/05/22  10:50:29)',
                                 'tunnel_mode': u'L2',
                                 'uptime': u'0s',
                                 'wlan_id': u''},
                        'neighbor': {},
                        'radio': {'airtime': u'N/A',
                                  'bgscan': u'Enabled',
                                  'channel': u'1',
                                  'channelization': u'20',
                                  'mcast': u'0',
                                  'noisefloor': u'N/A',
                                  'num_sta': u'0',
                                  'phyerr': u'N/A',
                                  'retries': u'0 / 0',
                                  'rx': u'0.00/0.00',
                                  'tx': u'0.00/0.00',
                                  'tx_power': u'0.00000149%',
                                  'wlangroup': u'Default'},
                        'uplink': {'ap': u'',
                                   'assoc': u'0',
                                   'desc': u'',
                                   'retries': u'',
                                   'rssi': u'',
                                   'rx': u'',
                                   'tx': u'',
                                   'type': u''},
                        'wlans': {}},
 u'00:24:82:0a:e6:70': {'downlink': {u'00:24:82:0a:e7:d0': {u'ap': u'00:24:82:0a:e7:d0',
                                                            u'description': u'',
                                                            u'first_assoc': u'2010/05/22  10:55:58',
                                                            u'rssi': u'99%',
                                                            u'total_rx_bytes': u'467K',
                                                            u'total_tx_bytes': u'726K',
                                                            u'type': u'Wireless'}},
                        'general': {'description': u'',
                                    'devname': u'Root1',
                                    'firmware_version': u'9.0.0.99.519',
                                    'ip': u'192.168.0.196',
                                    'mac': u'00:24:82:0a:e6:70',
                                    'model': u'zf2942',
                                    'serial_number': u'520801007212'},
                        'info': {'num_sta': u'0',
                                 'status': u'Connected (Root AP)',
                                 'tunnel_mode': u'L2',
                                 'uptime': u'3h 33m',
                                 'wlan_id': u''},
                        'neighbor': {u'00:22:7f:3d:d7:60': {u'mac': u'00:22:7f:3d:d7:60',
                                                            u'mesh_uplink_rc': u'N/A (Different radio type)',
                                                            u'radio_channel': u'1',
                                                            u'rssi': u'99%'},
                                     u'00:24:82:0a:e7:d0': {u'mac': u'00:24:82:0a:e7:d0',
                                                            u'mesh_uplink_rc': u'18.0 (Connected)',
                                                            u'radio_channel': u'6',
                                                            u'rssi': u'99%'}},
                        'radio': {'airtime': u'37.2/14.3/20.9/2.6',
                                  'bgscan': u'Enabled',
                                  'channel': u'6',
                                  'channelization': u'',
                                  'mcast': u'0.0102',
                                  'noisefloor': u'-95',
                                  'num_sta': u'0',
                                  'phyerr': u'119',
                                  'retries': u'4.96 / 0.00',
                                  'rx': u'908K/165M',
                                  'tx': u'23.2K/2.89M',
                                  'tx_power': u'100%',
                                  'wlangroup': u'Default'},
                        'uplink': {'ap': u'',
                                   'assoc': u'0',
                                   'desc': u'',
                                   'retries': u'',
                                   'rssi': u'',
                                   'rx': u'',
                                   'tx': u'',
                                   'type': u''},
                        'wlans': {u'rat-test-ap-detail': {u'bssid': u'00:24:82:0a:e6:79',
                                                          u'radio_type': u'802.11b/g',
                                                          u'wlan': u'rat-test-ap-detail'}}},
 u'00:24:82:0a:e7:d0': {'downlink': {},
                        'general': {'description': u'',
                                    'devname': u'Mesh1',
                                    'firmware_version': u'9.0.0.99.519',
                                    'ip': u'192.168.0.195',
                                    'mac': u'00:24:82:0a:e7:d0',
                                    'model': u'zf2942',
                                    'serial_number': u'520801006384'},
                        'info': {'num_sta': u'0',
                                 'status': u'Connected (Mesh AP, 1 hop)',
                                 'tunnel_mode': u'L2',
                                 'uptime': u'3h 16m',
                                 'wlan_id': u''},
                        'neighbor': {u'00:22:7f:3d:d7:60': {u'mac': u'00:22:7f:3d:d7:60',
                                                            u'mesh_uplink_rc': u'N/A (Different radio type)',
                                                            u'radio_channel': u'1',
                                                            u'rssi': u'99%'},
                                     u'00:24:82:0a:e6:70': {u'mac': u'00:24:82:0a:e6:70',
                                                            u'mesh_uplink_rc': u'35.0 (Connected)',
                                                            u'radio_channel': u'6',
                                                            u'rssi': u'99%'}},
                        'radio': {'airtime': u'34.7/15.7/16.0/3.3',
                                  'bgscan': u'Enabled',
                                  'channel': u'6',
                                  'channelization': u'',
                                  'mcast': u'1.25',
                                  'noisefloor': u'-93',
                                  'num_sta': u'0',
                                  'phyerr': u'689',
                                  'retries': u'5.66 / 0.00',
                                  'rx': u'814K/144M',
                                  'tx': u'11.9K/1.74M',
                                  'tx_power': u'100%',
                                  'wlangroup': u'Default'},
                        'uplink': {'ap': u'00:24:82:0a:e6:70',
                                   'assoc': u'2010/05/22  10:57:27',
                                   'desc': u'',
                                   'retries': u'0.00 pkts',
                                   'rssi': u'99%',
                                   'rx': u'10.8K pkts / 792K bytes',
                                   'tx': u'2.28K pkts / 469K bytes',
                                   'type': u'Wireless'},
                        'wlans': {u'rat-test-ap-detail': {u'bssid': u'00:24:82:0a:e7:d9',
                                                          u'radio_type': u'802.11b/g',
                                                          u'wlan': u'rat-test-ap-detail'}}}}
2010-05-22 14:12:16,994 DEBUG    Clean up the Selenium Manager
2010-05-22 14:12:17,104 INFO     [TEA.Module u.zd.aps_details_tea] Result:
{   'mac': '00:24:82:0a:e7:d0',
    'message': '',
    'result': 'PASS',
    'u.zd.aps_details_tea': None,
    'zd': <RuckusAutoTest.components.ZoneDirector.ZoneDirector2 instance at 0x0235A648>,
    'zd_ip_addr': '192.168.0.2'}
2010-05-22 14:12:17,104 INFO     Close logging file D:\phannt\saigon\runlog\tea_u.zd.aps_details_tea\log_tea_u.zd.aps_details_tea_201005221358.txt
'''