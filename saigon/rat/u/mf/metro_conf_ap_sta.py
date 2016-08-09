'''
Tea program for METRO basic Tikona case
'''
from ratenv import *
import copy
import logging
import time
from pprint import pformat as pp
from RuckusAutoTest.components import clean_up_rat_env
from RuckusAutoTest.components.lib.mf import metro_wireless as wlan
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components import (create_metro_by_model,create_ruckus_ap_by_ip_addr,create_zd_by_ip_addr,
                                       create_station_by_ip_addr, create_server_by_ip_addr)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    a = dict(ip_zd = '192.168.0.2',ip_ap = '192.168.0.202', 
             ip_srv ='192.168.0.252', ip_sta ='192.168.1.11', ip_mm = '192.168.0.200')
    a.update(cfg)
    sta = create_station_by_ip_addr(a['ip_sta'])
    zd = create_zd_by_ip_addr(a['ip_zd'])
    srv = create_server_by_ip_addr(a['ip_srv'])
    mm = create_metro_by_model(ip_addr=a['ip_mm'])
    mm.start()
    b = dict (sta=sta , zd=zd, mm=mm, srv=srv)    
    sta.remove_all_wlan()
    return b

def _create_metro_bridge(metro):
    # prerequisite for this test case: MM needs to connect its WAN to remote AP first 
    cfg = dict (auth='PSK', encryption ='TKIP', wpa_ver='WPA',ssid = 'b_beverly', key_string='1234567890')
    if (0):
        # the test case should check if rat7211 is not exist then create it
        wlan.set_ssid(metro,'rat7211','wan')
        time.sleep(5)
        wlan.set_encryption_open(metro,'wan')
        time.sleep(5)
    wlan.set_wlan1_mode(metro,'bridge')
    time.sleep(10)
    wlan.set_wireless_state_en(metro,'wlan1')
    time.sleep(10)
    wlan.set_ssid(metro,cfg['ssid'],'wlan1')
    time.sleep(10)
    wlan.set_encryption_psk(metro,'wlan1','bridgebeverly')
    time.sleep(10)
    return dict(auth=cfg['auth'], encryption =cfg['encryption'], wpa_ver=cfg['wpa_ver'],ssid =cfg['ssid'], key_string=cfg['key_string'])

def _create_metro_route(metro):
    # prerequisite for this test case: MM needs to connect its WAN to remote AP first 
    cfg = dict (auth='PSK', encryption ='TKIP', wpa_ver='WPA',ssid = 'r_beverly', key_string='1234567890')
    if (0):
        # the test case should check if rat7211 is not exist then create it
        wlan.set_ssid(metro,'rat7211','wan')
        time.sleep(5)
        wlan.set_encryption_open(metro,'wan')
        time.sleep(5)
    wlan.set_wlan1_mode(metro,'route')
    time.sleep(20)
    wlan.set_wireless_state_en(metro,'wlan1')
    time.sleep(30)
    wlan.set_ssid(metro,cfg['ssid'],'wlan1')
    time.sleep(20)
    wlan.set_encryption_psk(metro,'wlan1','routebeverly')
    time.sleep(20)
    return dict(auth=cfg['auth'], encryption =cfg['encryption'], wpa_ver=cfg['wpa_ver'],ssid =cfg['ssid'], key_string=cfg['key_string'])

    
def _create_zd_wlan(zd):
    wlan_cfg = dict(auth='EAP', encryption ='AES', wpa_ver = 'WPA2',ssid = 'rat7211wpa', 
                    auth_svr='Local Database',username='angela',password='angela')
    try:
        lib.zd.wlan.create_wlan(zd, wlan_cfg)
    except:
        # for now, we assume the zd error is due to wlan on remote AP already exist as a prerequisite 
        # suggest to VLAN tag the MM ethernet port (LAN side) so we can control it without the need of MM's WAN link 
        # use some ip other than 30.x on MM's LAN side
        pass

    
def do_test(conf):
    mf = {}
    _create_zd_wlan(conf['zd'])
    wlan_cfg = _create_metro_route(conf['mm'])
    conf['sta'].cfg_wlan(wlan_cfg)
    tmethod.renew_wifi_ip_address(conf['sta'], 360)
    error = tmethod.client_ping_dest_is_allowed(conf['sta'],conf['srv'].ip_addr)
    if error: 
        return ('fail', error)
    else:
        return ('pass','congrat')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    component_list = do_config(kwa)
    res = do_test(component_list)
    logging.info(pp(res))

    return res

