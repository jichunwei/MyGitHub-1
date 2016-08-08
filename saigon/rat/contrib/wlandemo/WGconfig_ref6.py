import time
import logging

import WGconfig_cfgLib_ref3 as BCLIB
import defaultWlanConfigParams_ref2 as DWCFG
from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC as RPC
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector


###
### Testbed data base
###
# provide the name of wlan-group
mytb = {'wgs_name': 'MultiWgsHelpQaWorkOnRuckus'}
#mytb['wlans'] = ['open-none','share-wep128','eap-wpa-tkip', 'eap-wpa-aes', 'eap-wpa2-tkip','eap-wpa2-aes','open-wep64','open-wep128']
# 6 wlans and encryption modes; please refer to defaultWlanConfigParams for details
mytb['wlans'] = ['psk-wpa2-tkip-zeroIT-Dpsk-T', 'psk-wpa2-tkip-zeroIT-T', 'psk-wpa2-aes', 'psk-wpa2-tkip', 'share-wep128', 'open-wep128']
acl_conf = {'acl_name':'TestForFun', 'description':'L2AccessControl', 'allowed_access': True, 'mac_list':['00:00:00:00:11:00']}

def create_zd(conf):
    cfg = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(conf)

    logging.info("Starting up ZoneDirector [%s]" % cfg['ip_addr'])

    zd = ZoneDirector(cfg)
    zd.start()

    return zd

#Test client association w/ ZD in round robin fashion w/ different wlans detected by remote station/CPE
#This method can test whatever wlans are configured on ZD
def do_station_test(**kwargs):
    fcfg = dict(sta_ip_addr = '192.168.1.10', sleep = 15, repeat = 1, debug = False)
    fcfg.update(kwargs)
    halt(fcfg['debug'])
    sta = RPC(dict(sta_ip_addr = fcfg['sta_ip_addr']))
    sta.do_cmd('get_current_status')
    sta.do_cmd('remove_all_wlan')
    for r in range(1, int(fcfg['repeat']) + 1):
        for wlan_id in mytb['wlans']:
            sta.do_cmd('check_ssid', {'ssid': wlan_id})
            wlan_conf = DWCFG.get_cfg(wlan_id)
            sta.cfg_wlan(wlan_conf)
            time.sleep(fcfg['sleep'])
            sta.get_current_status()
            wlan_ip = sta.get_wifi_addresses()
            client_ip = wlan_ip[0]
            sta.ping(client_ip, timeout_ms = 3000)
            sta.do_cmd('remove_all_wlan')

    return 0

def halt(debug = False):
    if debug:
        import pdb
        pdb.set_trace()

def do_cfg(**kwargs):
    fcfg = dict(debug = False, do_config = True, username = 'admin', password = 'admin')
    fcfg.update(kwargs)
    halt(fcfg['debug'])

    zd = create_zd(fcfg)
    if not fcfg['do_config']:
        return zd

    try:
        BCLIB.remove_wlan_config(zd)
    except:
        pass
    BCLIB.create_l2_acl_policy(zd, acl_conf, num_of_acl = 10)
    BCLIB.create_wlans(zd, mytb)
    #BCLIB.create_wlan_group(zd, mytb)

    BCLIB.create_multi_wlan_groups(zd, mytb)
    BCLIB.align_wlan_group_sn_wlan(zd, mytb)

    return zd

# configure every AP on ZD w/ different WlanGroup
def do_test(zd, **kwargs):
    fcfg = dict(debug = False, sleep = 3, repeat = 1)
    fcfg.update(kwargs)

    halt(fcfg['debug'])

    wgs_list = BCLIB.get_wlan_groups_list(zd)

    ap_xs_list = BCLIB.get_ap_xs_info(zd)

    for p in range(1, int(fcfg['repeat']) + 1):
        for wgs_name in wgs_list:
            desc = "Update %03d wgs=%s" % (p, wgs_name)
            for ap_xs0 in ap_xs_list:
                ap_xs1 = BCLIB.update_ap_xs_info(zd, ap_xs0, desc, wgs_name)
                time.sleep(fcfg['sleep'])
        #wgs_name = 'Default'
        #desc = "Update %03d wgs=%s" % (p, wgs_name)
        #for ap_xs0 in ap_xs_list:
        #    ap_xs1 = BCLIB.update_ap_xs_info(zd, ap_xs0, desc, wgs_name)
        #    time.sleep(fcfg['sleep'])
    return 0

def do_cleanup(zd, debug = False):
    halt(debug)
    BCLIB.remove_wlan_config(zd)

# Usage:
#
#   tea.py contrib.wlandemo.WGconfig_ref repeat = 1 do_cleanup = False
#   tea.py bugs.bug6099 repeat=50 debug=True
#   tea.py bugs.bug6099 ip_addr=192.168.2.2
#
def main(**kwargs):
    fcfg = dict(debug = False, repeat = 1, sleep = 10, do_config = True, do_cleanup = False)
    fcfg.update(kwargs)

    sm = SeleniumManager()
    fcfg.update({'selenium_mgr': sm})

    zd = do_cfg(**fcfg)
    try:
        do_test(zd, **kwargs)
        do_station_test(**kwargs)
        if fcfg['do_cleanup']:
            do_cleanup(zd, debug = fcfg['debug'])

    except Exception, ex:
        sm.shutdown()
        return ('FAIL', mytb, {'error': ex.message})

    sm.shutdown()
    return ('PASS', mytb)

