
'''
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_station_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig


'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    sta_ip_addr = '192.168.1.11',
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    _cfg['sta'] = create_station_by_ip_addr(default_cfg.pop('sta_ip_addr'))
    return _cfg


def do_test(cfg):
    #arg = tconfig.get_web_auth_params(cfg['zd'], username = 'ras.local.user',
    #                                  password = 'ras.local.user')
    #cfg['sta'].perform_web_auth(arg)

    arg = tconfig.get_guest_auth_params(cfg['zd'], 'ABCDE-ABCDE', True, '')
    cfg['sta'].perform_guest_auth(arg)

    return


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

