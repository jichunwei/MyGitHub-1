'''
This tea to work with syslog server.
Currently this tea to check function start_syslog_service only.

Examples:
tea.py u.fm.syslog linux_srv_ip=192.168.20.252 action='start'
'''


import logging

from RuckusAutoTest.common.utils import get_cfg_items
from RuckusAutoTest.components import create_server_by_ip_addr, clean_up_rat_env

def _start_syslog(srv_cli):
    try:
        srv_cli.start_syslog()
        res = dict(result='PASS', message='Start syslog successfully')
    except Exception, e:
        res = dict(
            result='ERROR', message='Cannot start syslog. Error: %s' % e.__str__()
        )

    return res

def do_config(cfg):
    p = dict(
        linux_srv_ip = '192.168.20.252',
        user = 'lab',
        password = 'lab4man1',
        root_password = 'lab4man1',
    )
    p.update(cfg)

    p['srv_cli'] = create_server_by_ip_addr(
        p['linux_srv_ip'], p['user'], p['password'], p['root_password']
    )

    return p


def do_test(cfg):
    if cfg['action'] == 'start':
        res = _start_syslog(cfg['srv_cli'])

    return res


def do_clean_up(cfg):
    if cfg['srv_cli']: del cfg['srv_cli']
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
