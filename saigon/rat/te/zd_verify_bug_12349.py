'''
This script verify bug #12349 with different vlan id and tunnel mode enable
Requirements
+ zd, server, station
+ vlan config on server
+ vlan config on switch
Test
+ Clear all configuration on ZoneDirector
+ Create a wlan Open-None with tunnel enable and input vlan_id
+ Associate client from client to server
+ Get client IP address
+ Clear route to client on server.
+ Ping from server to client. return result.

Examples
   tea.py zd_verify_bug_12349 zd_ip_addr=192.168.0.2 sta_ip_addr=192.168.1.11 target_ip_addr=20.2.0.249 vlan_id=2
   tea.py zd_verify_bug_12349 zd_ip_addr=192.168.0.2 sta_ip_addr=192.168.1.11 target_ip_addr=20.10.2.249 vlan_id=512
   tea.py zd_verify_bug_12349 zd_ip_addr=192.168.0.2 sta_ip_addr=192.168.1.11 target_ip_addr=20.14.83.249 vlan_id=3677
'''


import logging
import time
from pprint import pformat

from RuckusAutoTest.common.utils import log
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC
from RuckusAutoTest.components.LinuxPC import LinuxPC
import RuckusAutoTest.common.lib_Debug as bugme

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.components import Helpers as lib


def create_zd(cfg = {}):
    p = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    p.update(cfg)
    if 'zd_ip_addr' in cfg:
        p['ip_addr'] = cfg['zd_ip_addr']

    logging.info('Creating Zone Director [%s]' % p['ip_addr'])
    log(p, 'zd cfg')
    zd = ZoneDirector(p)
    zd.start()
    zd.remove_all_cfg()
    return zd


def create_sta(cfg):
    p = dict(sta_ip_addr = '192.168.1.11')
    p.update(cfg)
    logging.info('Creating Station [%s]' % p['sta_ip_addr'])
    log(p, 'station cfg')
    sta = RemoteStationWinPC(p)
    sta.remove_all_wlan()
    return sta


def create_srv(cfg):
    p = dict(ip_addr = '192.168.0.252')
    p.update(cfg)
    logging.info('Creating Server [%s]' % p['ip_addr'])
    log(p, 'srv cfg')
    return LinuxPC(p)


def get_wlan_cfg(cfg = {}):
    p = dict(
        auth = 'open',
        encryption = 'none',
        ssid = 'rat-test-bug-12349',
        vlan_id = 2,
        do_tunnel = True,
    )
    p.update(cfg)
    return p


def config(tcfg):
    wlan_cfg = {'vlan_id': 2}
    wlan_cfg['vlan_id'] = tcfg['vlan_id']
    return dict(
        zd = create_zd(tcfg),
        sta = create_sta(tcfg),
        srv = create_srv(tcfg),
        wlan = get_wlan_cfg(wlan_cfg),
        target_ip_addr = tcfg['target_ip_addr']
    )


def test(cfg):
    zd, sta, srv = cfg['zd'], cfg['sta'], cfg['srv']

    logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % cfg['wlan']['ssid'])
    lib.zd.wlan.create_wlan(zd, cfg['wlan'])

    tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")
    logging.info('Config, associate the client')
    sta.cfg_wlan(cfg['wlan'])
    logging.info(sta.get_current_status())    
    tmethod.renew_wifi_ip_address(sta, 360)
    logging.info('Ping from client to server')
    errmsg = tmethod.client_ping_dest_is_allowed(sta, cfg['target_ip_addr'])
    if errmsg:
        return 'FAIL: ping fail from client to server'

    logging.info('Get client IP address')
    sta_ip = sta.get_ip_config()['ip_addr']

    logging.info('Clear the arp on server and ping back')
    logging.info(srv.cmd('/sbin/arp -d %s' % sta_ip))
    logging.info(srv.cmd('/sbin/arp -d %s' % sta_ip))
    tmethod8.pause_test_for(10, "Wait for the arp entry is removed")

    # either empty or 'incomplete'
    logging.info(srv.cmd('/sbin/arp'))
    ping_result = srv.cmd('ping %s -c 4' % sta_ip)
    logging.info(ping_result)
    
    # return fail if can ping from server to client
    if "Unreachable" in ping_result:
        return 'FAIL: ping fail from server to client'        
    return 'PASS: ping successful from switch to client with vlan'

def clean_up(cfg):
    logging.info('Remove the wlan')
    cfg['zd'].stop()


def main(**cfg):
    default_cfg = dict(
        debug=False,
        zd_ip_addr='192.168.0.2',
        sta_ip_addr = '192.168.1.10',
        target_ip_addr = '20.0.2.249', 
        vlan_id =  2
    )
    default_cfg.update(cfg)    
    tcfg = config(default_cfg)
    msg = test(tcfg)
    clean_up(tcfg)

    tcfg['zd'].destroy()
    return msg

