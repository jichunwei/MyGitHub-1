"""
This module will show that we can use FM and ZD in the same test.
This test will:
    + Initialize FM
    + Initialize ZD
    + Set NetworkManagement' FlexMaster attributes of Zone Director
    + Check whether Zone Director appear in Manage Device page of FM or not

Examples:

   tea.py zd_reg zd_ip_addr=192.168.0.101 fm_ip_addr=192.168.30.252

"""


import logging
from pprint import pformat

from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.FlexMaster import FlexMaster
from RuckusAutoTest.components.lib.zd import system_zd as ZSYS
import RuckusAutoTest.common.lib_Debug as bugme
from RuckusAutoTest.components.lib.fm import inv_device_mgmt_fm as IDM

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

    logging.info("Starting up FlexMaster [%s]" % cfg['ip_addr'])


    fm = FlexMaster(sm, cfg['browser_type'], cfg['ip_addr'], cfg)
    fm.start()

    return fm


def set_network_management(fm_mgmt, zd):
    try:
        ZSYS.set_fm_mgmt_info(zd, fm_mgmt)
        return 'successful'

    except Exception:
        import traceback
        print "\n\n%s" % ('!' * 68)
        ex = traceback.format_exc()
        print ex
        return 'not successful'


def get_fm_manage_device(fm):
    try:
        IDM.set_view(fm, 'All ZoneDirectors')
        result = IDM.get_tbl(fm, 'view_tbl', {})
        return result
    except Exception:
        import traceback
        print "\n\n%s" % ('!' * 68)
        ex = traceback.format_exc()
        print ex


def main(**kwargs):
    tcfg = dict(
        debug = False,
        zd_ip_addr = '192.168.0.101',
        fm_ip_addr = '192.168.30.252',
        zd_ip_port = '',
        enabled = True
    )

    tcfg.update(kwargs)

    tries = 2
    while tries > 0:
        try:
            bugme.do_trace("TRACE_TE_FM")
            # initiate FM and ZD
            sm = SeleniumManager()
            fm = create_fm(tcfg, sm)
            zd = create_zd(tcfg, sm)

            # set Network Management for ZD
            fm_mgmt_2 = set_network_management(tcfg, zd)
            logging.info("Set Network Management for ZD %s: %s" % (tcfg['zd_ip_addr'], pformat(fm_mgmt_2, 4, 120)))

            # get info from ManageDevice view of FM
            manage_device_result = get_fm_manage_device(fm)

            # verify serial number btw ZD and info get from FM
            serial_from_zd = zd._get_serial_number()
            logging.info("Get serial of ZD from ZD object: %s" % serial_from_zd)
            serial_from_fm = manage_device_result[0]['serial']
            logging.info("Get serial of ZD from FM Manage Device view: %s" % serial_from_fm)

        except:
            tries -= 1
            continue

        if serial_from_fm != serial_from_zd:
            return ('FAIL',)

        else:
            return ('PASS',)

