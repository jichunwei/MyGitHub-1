'''
This is the unit tests for control_zd

Examples
tea.py u.zd.control_zd_tea
'''

import copy
import logging
from pprint import pprint as pp

import hotshot, hotshot.stats

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


def _test_re_navigate(cfg):
    logging.info('[TEST] Re-navigate to the current tab/menu')

    logging.info("get_snmp_agent_info()")
    cfg['current_snmp_agent_cfg'] = lib.zd.sys.get_snmp_agent_info(cfg['zd'])

    logging.info("set_snmp_agent_info()")
    lib.zd.sys.set_snmp_agent_info(cfg['zd'], cfg['current_snmp_agent_cfg'])

    logging.info("re_navigate()")
    cfg['zd'].re_navigate()

    logging.info("set_snmp_agent_info()")
    cfg['current_snmp_agent_cfg'] = lib.zd.sys.get_snmp_agent_info(cfg['zd'])

    logging.info("current_snmp_agent_cfg:")
    pp(cfg['current_snmp_agent_cfg'])

    cfg['result'] = 'PASS'
    cfg['message'] = ''

    return cfg

def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    return _test_re_navigate(cfg)


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)

    # setup profile
    profile = hotshot.Profile("re_navigate_tea.bin")
    res = profile.runcall(do_test, tcfg)
    profile.close()

    do_clean_up(tcfg)

    # analyze profile data and print out
    stats = hotshot.stats.load("re_navigate_tea.bin")
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats()

    return res

