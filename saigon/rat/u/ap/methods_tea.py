'''
'''

import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib


'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = dict(
    ip_addr = '192.168.0.195',
    username='admin',
    password='admin',
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['ap'] = create_ruckus_ap_by_ip_addr(default_cfg.pop('ip_addr'),
                                             default_cfg.pop('username'),
                                             default_cfg.pop('password'))
    return _cfg


def do_test(cfg):

    pp(cfg['ap'].get_wlan_list())

    pp(cfg['ap'].get_wlan_info_dict())

    pp(cfg['ap'].get_mesh_info())

    pp(cfg['ap'].get_mesh_info_dict())

    return


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res

