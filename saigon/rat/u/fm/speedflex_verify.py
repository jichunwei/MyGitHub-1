'''
try this after using speedflex_create.py
. find the speedflex item on the saved speedflex list
. get the result of that run and verify it against defined values

tea.py u.fm.speedflex_verify fm_ip_addr=192.168.30.252
        sf_name = 'super_cuteo'

'''

import logging
from pprint import pprint as pp

from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env


def do_config(cfg):
    '''
     On this ex., running speedflex from a standalone AP to a ZD managed's AP
     . stand alone AP: 192.168.20.200
     . ZD (192.168.0.202)'s AP: 192.168.0.199
    '''
    p = dict(
        fm_ip_addr = '192.168.30.252',
        sf_name = 'super_cuteo',
        from_device = 'ap',
        to_device = 'zd_ap',
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'))
    return p


def do_test(cfg):
    fm = cfg['fm']

    logging.info('Get the Speedflex result')
    sf_result = fm.lib.speedflex.get_speedflex_result(fm, cfg['sf_name'])
    pp(sf_result)

    logging.info('Parse the result so that it can be compared')
    fm.lib.speedflex.parse_result(sf_result)
    pp(sf_result)

    logging.info('Now verify that with defined values')
    r = fm.lib.speedflex.verify(sf_result, cfg['from_device'], cfg['to_device'])
    pp(r)

    if r:
        return dict(result='PASS', message='')

    return dict(result='FAIL', message='')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
