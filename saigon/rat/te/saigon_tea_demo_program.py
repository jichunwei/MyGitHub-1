"""
This module will show that we can use FM, ZD and AP in the same test.
Requirement:
    + A testbed that have a FM, ZD and AP. AP is being managed by ZD
    + AP can log in with user admin (username = admin, password = admin) when it is
    being managed by ZD.
    + AP can log in with user super (username = super, password = sp-admin) when it
    is not being managed by ZD

This test will:
    + Initialize FM
    + Initialize ZD
    + Initialize AP with user admin
    + Remove an AP from ZD by delete its record in Configure/Access Points
    + Uncheck "Automatically approve all join requests from APs" option in
    Configure/Access Points page of ZD
    + Reset factory AP
    + Initialize AP with user super
    + Set AP point to FM (in Administration/Management of AP)
    + Check whether AP associate with FM or not.

Examples:

   tea.py saigon_tea_demo_program fm_ip_addr=10.100.0.1 zd_ip_addr=10.100.0.3 ap_ip_addr=10.100.0.4

"""


import logging
import time
from pprint import pformat

from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.FlexMaster import FlexMaster
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import system_zd as ZSYS
import RuckusAutoTest.common.lib_Debug as bugme
from RuckusAutoTest.components.lib.fm import inv_device_mgmt_fm as IDM


def do_config(tcfg):
    sm = SeleniumManager()
    logging.info('Initiate fm %s' % tcfg['fm_ip_addr'])
    fm = create_fm(tcfg, sm)
    logging.info('Initiate zd %s' % tcfg['zd_ip_addr'])
    zd = create_zd(tcfg, sm)

    # initiate AP with user admin
    config_admin = {'ip_addr' : tcfg['ap_ip_addr'], 'username' : 'admin', 'password' : 'admin'}
    logging.info('Initiate ap %s with user admin' % tcfg['ap_ip_addr'])
    ap = RuckusAP(config_admin)

    current_policy = zd.get_ap_policy_approval()
    logging.info('Get current approval policy of zd %s' % str(current_policy))

    return (fm, zd, ap, current_policy)

def do_test(zd, ap, fm, tcfg):
    # get mac address of ap
    mac_addr = ap.base_mac_addr

    # delete this approval ap from zd
    logging.info('Removing ap with mac addr %s from approved table of zd' % str(mac_addr))
    zd.remove_approval_ap(mac_addr=mac_addr)

    # uncheck auto approval
    logging.info('Uncheck automatically approve join request checkbox')
    zd.set_ap_policy_approval(auto_approval = False)

    ap.username = 'super'
    ap.password = 'sp-admin'
    # reset factory ap
    logging.info('Set factory ap %s and re-login with user super' % tcfg['ap_ip_addr'])
    ap.set_factory()

    # set AP point to FM
    url = 'https://%s/intune/server' % tcfg['fm_ip_addr']
    tr069_cfg = {'url' : url}
    logging.info('Set url of ap to %s' % url)
    ap.set_tr069(tr069_cfg)

    # check whether AP is being managed by FM or not
    serial = ap.get_serial()

    time.sleep(60)
    logging.info('Start finding ap with serial %s in FM Manage Device page' % serial)
    idx, data = IDM.find_device_serial(fm, serial)
    if data == None:
        return 'FAIL: Cant find device with serial %s in FM Manage Device page' % serial

    return 'PASS: AP with serial %s has found in FM Manage Device page' % serial

def do_clean_up(ap, zd, fm, current_policy):
    logging.info('Return previous ap policy approval of zd')
    zd.set_ap_policy_approval(current_policy)
    logging.info('Stop FM')
    fm.stop()
    logging.info('Stop ZD')
    zd.stop()


def create_zd(conf, sm):
    cfg = dict(
        ip_addr = '192.168.0.101',
        username = 'admin',
        password = 'admin',
        model = 'zd',
        browser_type = 'firefox',
    )
    cfg.update(conf)
    if conf['zd_ip_addr']:
        cfg['ip_addr'] = conf['zd_ip_addr']
    logging.info("Starting up ZoneDirector [%s]" % cfg['ip_addr'])

    zd = ZoneDirector(cfg)
    zd.start()

    return zd


def create_fm(conf, sm):
    cfg = dict(
        ip_addr = '192.168.30.252',
        username = 'admin@ruckus.com',
        password = 'admin',
        model = 'fm',
        browser_type = 'firefox',
    )
    cfg.update(conf)
    if conf['fm_ip_addr']:
        cfg['ip_addr'] = conf['fm_ip_addr']


    fm = FlexMaster(sm, cfg['browser_type'], cfg['ip_addr'], cfg)
    fm.start()

    return fm




def main(**kwargs):
    tcfg = dict(
        debug=False,
        zd_ip_addr='192.168.0.101',
        fm_ip_addr='192.168.30.252',
        ap_ip_addr='192.168.0.197',
        zd_ip_port='',
        enabled = True
    )

    tcfg.update(kwargs)

    tries = 2
    while tries > 0:
        try:
            bugme.do_trace("TRACE_TE_FM")
            fm, zd, ap, current_policy = do_config(tcfg)

            msg = do_test(zd, ap, fm, tcfg)

            do_clean_up(zd, current_policy)
            return msg

        except:
            tries -= 1
            continue


    #return 'PASS'


