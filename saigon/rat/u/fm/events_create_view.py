'''
monitor > events page: create a new event view with given config

tea.py u.fm.events_search_n_save fm_ip_addr=192.168.30.252 viewname=abc filter=[['Serial Number', 'Contains', 'ZF']]
'''

import time
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env


def do_config(cfg):
    p = dict(
        fm_ip_addr = '192.168.20.252',
        filter = [['Serial Number', 'Contains', 'ZF']],
        viewname = 'abc',
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'))
    return p


def do_test(cfg):
    logging.info('List of event views:')
    pp(cfg['fm'].lib.event.get_all_views(cfg['fm']))
    time.sleep(3)

    logging.info('Now create a new view')
    cfg['fm'].lib.event.create_view(cfg['fm'], cfg['viewname'], cfg['filter'])

    return dict(result='PASS', message='Able to filter and get result')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
