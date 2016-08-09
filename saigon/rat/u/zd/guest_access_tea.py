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
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    logging.info('Generate A Single Shared Guest Pass')
    gp_cfg = {
        'guest_fullname': 'Phan Nguyen',
        'is_shared': 'Yes',
        'username': 'marketing.user',
        'password': 'marketing.user',
        'auth_ser': 'RADIUS',
        'wlan': 'RAT-GP',
    }
    pp(lib.zd.ga.generate_shared_guestpass(cfg['zd'], gp_cfg))

    logging.info('Get A Guest Pass By Full Name')
    pp(lib.zd.ga.get_guestpass_by_name(cfg['zd'], 'Phan Nguyen'))

    logging.info('Get All Guest Passes')
    pp(lib.zd.ga.get_all_guestpasses(cfg['zd']))

    cfg['result'] = 'PASS'
    cfg['message'] = 'Guest Pass Functionality Is Working Properly.'

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

