'''
This is the unit tests for control_zd

Examples
tea.py u.zd.control_zd_tea
'''

import copy
import logging

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


def _test_reboot_zd(cfg):
    logging.info('[TEST] Restart the ZoneDirector')

    try:
        lib.zd.admin.reboot_zd(cfg['zd'])

    except Exception, e:
        cfg['result'] = 'FAIL'
        cfg['message'] = e.message

    cfg['result'] = 'PASS'
    cfg['message'] = ''

    return cfg


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    return _test_reboot_zd(cfg)


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res

