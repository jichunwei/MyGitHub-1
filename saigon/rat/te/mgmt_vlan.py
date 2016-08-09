"""
This module enable/disable ZD's AP management vlan.

Usage:

   tea.py <mgmt_vlan key/value pair> ...

   where <mgmt_vlan key/value pair> are:

      ip_addr   : ip address of ZoneDirector UI
      username  : username to login ZoneDirector UI
      password  : password to login ZoneDirector UI

      zd_vlan   : dict of zd mgmt_vlan settings; valid values are
                  enabled={True|False}
                  disabled={True|False}

      ap_vlan   : dict of ap mgmt_vlan settings; valid values are
                  enabled={True|False}
                  disabled={True|False}
                  keep={True|False}

      zd_discovery: dict of primary/secondary ZD; valid values are
                  prim_ip=<ip address of primary ZD>
                  sec_ip=<ip address of secondary ZD>
                  disabled={True|False}

      wait4assoc: {True|False}, default if True.
                  if True, it will check all APs are Connected before exit.

Examples:

   # AP mgmt_vlan=302 enabled and invoke debug immediately
   tea.py mgmt_vlan ap_vlan=dict(enabled=True) idebug=True

   # AP mgmt_vlan=302 enabled, ZD mgmt_vlan=301 enabled
   tea.py mgmt_vlan ap_vlan=dict(enabled=True) zd_vlan=dict(enabled=True)

   # AP mgmt_vlan=302 enabled, ZD mgmt_vlan diabled
   tea.py mgmt_vlan ap_vlan=dict(enabled=True) zd_vlan=dict(disabled=True)

   # AP mgmt_vlan disabled, ZD mgmt_vlan=301 enabled
   tea.py mgmt_vlan ap_vlan=dict(disabled=True) zd_vlan=dict(enabled=True)

   # AP mgmt_vlan disabled, ZD mgmt_vlan disabled
   tea.py mgmt_vlan ap_vlan=dict(disabled=True) zd_vlan=dict(disabled=True)

   tea.py mgmt_vlan ap_vlan=dict(enabled=True) debug=True
   tea.py mgmt_vlan ap_vlan=dict(enabled=True,vlan_id=302) debug=True
   tea.py mgmt_vlan ap_vlan=dict(disabled=True) ip_addr=192.168.2.2
   tea.py mgmt_vlan zd_discovery=dict(prim_ip='192.168.0.2') ap_vlan=dict(enabled=True)
   tea.py mgmt_vlan zd_discovery=dict(prim_ip='192.168.0.2') ap_vlan=dict(disabled=True) ip_addr=192.168.2.2

"""

import os
import time
from pprint import pprint, pformat
import logging

import ratenv
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import te_mgmt_vlan_hlp as TE
from RuckusAutoTest.components import NetgearSwitchRouter as NSR
import RuckusAutoTest.common.lib_Debug as bugme

def create_zd(conf):
    logging.info("Starting up ZoneDirector [%s]" % conf['ip_addr'])
    cfg = dict(
        ip_addr = '192.168.0.2',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(conf)

    sm = SeleniumManager()
    zd = ZoneDirector(cfg)
    zd.start()

    return zd


def create_nsr(**kwargs):
    nsr_conf = dict(
        ip_addr = '192.168.0.253',
        username = 'admin',
        password = '',
        enable_password = '',
    )
    nsr_conf.update(kwargs)

    nsr = NSR.NetgearSwitchRouter(nsr_conf)

    return nsr


def need_to_do_ap_mgmt(ap_policy):
    zdd = ap_policy['zd_discovery']
    apv = ap_policy['mgmt_vlan']

    if zdd or apv['enabled'] or apv['keep'] or apv['disabled']:
        return True

    return False


def get_ap_status(zd):
    ap_status = {}

    for ap_info in zd.get_all_ap_info():
        mac = ap_info.pop('mac')
        ap_status[mac] = ap_info

    logging.info("ZD Currently Managed APs Status:\n%s" % (pformat(ap_status, indent = 4)))

    return ap_status


def wait_for_ap_associated(zd, ap_status_0, **kwargs):
    cfg = dict(timeout = 600, pause = 15)
    end_time = time.time() + int(cfg['timeout'])
    pause = int(cfg['pause'])

    while time.time() < end_time:
        aps1 = get_ap_status(zd)
        cnd = len(ap_status_0)

        for mac in ap_status_0.keys():
            if aps1.has_key(mac):
                ap_status_1 = aps1[mac]
                if ap_status_1['status'].startswith('Connected'):
                    cnd -= 1
        if cnd < 1:
            return True

        time.sleep(pause)

    return False


def main(**kwargs):
    mycfg = dict(debug = False, wait4assoc = True, timeout = 600)

    zdcfg = {'ip_addr': '192.168.0.2',
             'username': 'admin',
             'password': 'admin'}

    vlan_conf = {
        'zd_discovery': {},
        'ap_vlan': dict(
            enabled = False,
            disabled = False,
            keep = False,
            vlan_id = 302,
        ),
        'nsr': dict(
            ip_addr = '192.168.0.253',
            username = 'admin',
            password = '',
            enable_password = '',
        ),
        'zd_vlan': dict(
            vlan_id = 0,
            enabled = False,
            disabled = False,
        )
    }

    for k, v in kwargs.items():
        if vlan_conf.has_key(k) and type(v) is dict:
            vlan_conf[k].update(v)
        elif zdcfg.has_key(k):
            zdcfg[k] = v
        elif mycfg.has_key(k):
            mycfg[k] = v

    ap_policy = { 'zd_discovery': vlan_conf['zd_discovery'], 'mgmt_vlan': vlan_conf['ap_vlan'] }

    logging.info("ZD CFG:\n%s", pformat(zdcfg, indent = 4))
    logging.info("ZD AP.mgmt_vlan:\n%s", pformat(ap_policy, indent = 4))

    if mycfg['debug']: bugme.pdb.set_trace()

    zd = create_zd(zdcfg)
    if mycfg['wait4assoc']:
        mycfg['ap.status.0'] = get_ap_status(zd)

    if need_to_do_ap_mgmt(ap_policy):
        TE.MVLAN.set_ap_mgmt_vlan_info(zd, ap_policy)

    ap_mgmt_vlan = TE.MVLAN.get_ap_mgmt_vlan_info(zd)

    # For regression standardized testbed configuration
    # ZD connected to the netgear switch port is always its native_vlan - tagged or untagged
    zd_vlan = vlan_conf['zd_vlan']
    logging.info("ZD ZD.mgmt_vlan:\n%s", pformat(zd_vlan, indent = 4))

    if zd_vlan['enabled']:
        nsr = create_nsr(**vlan_conf['nsr'])
        swp = TE.get_zd_switch_port(zd, nsr)
        zd_mgmt_vlan = TE.tag_zd_mgmt_vlan(zd, nsr, swp['interface'], swp['vlan_id'])

    elif zd_vlan['disabled']:
        nsr = create_nsr(**vlan_conf['nsr'])
        swp = TE.get_zd_switch_port(zd, nsr)
        zd_mgmt_vlan = TE.untag_zd_mgmt_vlan(zd, nsr, swp['interface'], swp['vlan_id'])

    else:
        zd_mgmt_vlan = TE.MVLAN.get_zd_mgmt_vlan_info(zd)

    result = 'PASS'

    if mycfg['wait4assoc'] and mycfg.has_key('ap.status.0'):
        tm_0 = time.time()
        time.sleep(10)
        if not wait_for_ap_associated(zd, mycfg['ap.status.0'], timeout = mycfg['timeout']):
            result = 'FAIL'
        tm_x = int(time.time() - tm_0)

    return (result, {'ap_vlan': ap_mgmt_vlan, 'zd_vlan': zd_mgmt_vlan, 'sec_convergence': tm_x})


