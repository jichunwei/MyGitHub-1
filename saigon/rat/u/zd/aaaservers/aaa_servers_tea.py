'''
Updated by cwang@2010-10-26
tea.py aaa_servers_tea te_root=u.zd.aaaservers
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
    ldap_server = {
        'server_name': 'LDAP',
        'server_addr':'192.168.0.252',
        'server_port':'389',
        'ldap_search_base':'dc=example,dc=net',
        'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
        'ldap_admin_pwd': 'lab4man1'
    },
    radius_server = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.252',
        'radius_auth_secret': '1234567890',
        'server_port': '1812'
    },
    radius_acc_server = {
        'server_name': 'RADIUS Accounting',
        'server_addr': '192.168.0.252',
        'radius_acct_secret': '1234567890',
        'server_port': '1813'
    },
    ad_server = {
        'server_name': 'ACTIVE_DIRECTORY',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'example.net',
    },
)


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    return _cfg


def do_test(cfg):
    logging.info('[TEST 01] Delete all AAA servers')
    pp(lib.zd.aaa.remove_all_servers(cfg['zd']))

    if cfg['ldap_server']:
        logging.info('[TEST 02-] Create an LDAP server: %s' % cfg['ldap_server'])
        pp(lib.zd.aaa.create_server(cfg['zd'], **cfg['ldap_server']))

    if cfg['radius_server']:
        logging.info('[TEST 02-] Create a RADIUS server: %s' % cfg['radius_server'])
        pp(lib.zd.aaa.create_server(cfg['zd'], **cfg['radius_server']))

    if cfg['radius_acc_server']:
        logging.info('[TEST 02-] Create a RADIUS ACCOUTING server: %s' % cfg['radius_acc_server'])
        pp(lib.zd.aaa.create_server(cfg['zd'], **cfg['radius_acc_server']))

    if cfg['ad_server']:
        logging.info('[TEST 02-] Create an AD server: %s' % cfg['ad_server'])
        pp(lib.zd.aaa.create_server(cfg['zd'], **cfg['ad_server']))


    logging.info('[TEST 03] Get all AAA servers')
    pp(lib.zd.aaa.get_auth_server_info_list(cfg['zd']))

    cfg['result'] = 'PASS'
    cfg['message'] = ''
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

