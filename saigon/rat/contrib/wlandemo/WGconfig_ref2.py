import time
import logging

import WGconfig_cfgLib_ref2 as BCLIB
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector

###
### Testbed data base
###
# provide the name of wlan-group
mytb = {'wgs_name': 'MultiWgsHelpQaWorkOnRuckus'}
#mytb['wlans'] = ['open-none','share-wep128','eap-wpa-tkip', 'eap-wpa-aes', 'eap-wpa2-tkip','eap-wpa2-aes','open-wep64','open-wep128']
# 6 wlans and encryption modes; please refer to defaultWlanConfigParams for details
mytb['wlans'] = ['open-wep128', 'share-wep128', 'eap-wpa-tkip', 'eap-wpa-aes', 'eap-wpa2-tkip', 'eap-wpa2-aes']


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

    BCLIB.create_wlans(zd, mytb)
    #BCLIB.create_wlan_group(zd, mytb)

    BCLIB.create_multi_wlan_groups(zd, mytb)
    BCLIB.align_wlan_group_sn_wlan(zd, mytb)

    return zd


# configure every AP on ZD w/ different WlanGroup
def do_test(zd, **kwargs):
    fcfg = dict(debug = False, sleep = 1, repeat = 300)
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
#   tea.py contrib.wlandemo.Wgconfig_ref repeat = 1 do_cleanup = False
#   tea.py bugs.bug6099 repeat=50 debug=True
#   tea.py bugs.bug6099 ip_addr=192.168.2.2
#
def main(**kwargs):
    fcfg = dict(debug = False, repeat = 1, sleep = 1, do_config = True, do_cleanup = True)
    fcfg.update(kwargs)

    sm = SeleniumManager()
    fcfg.update({'selenium_mgr': sm})

    zd = do_cfg(**fcfg)
    try:
        do_test(zd, **fcfg)
        if fcfg['do_cleanup']:
            do_cleanup(zd, debug = fcfg['debug'])

    except Exception, ex:
        sm.shutdown()
        return ('FAIL', mytb, {'error': ex.message})

    sm.shutdown()
    return ('PASS', mytb)

