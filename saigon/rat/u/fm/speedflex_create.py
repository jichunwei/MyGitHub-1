'''
. create a speedflex
. run it, dump the result to output
. save it so it can be accessed later

tea.py u.fm.speedflex_create fm_ip_addr=192.168.30.252
        sf_cfg = dict(
            is_uplink = True, is_downlink = True,
            src = dict(view = 'All Standalone APs', ips=['192.168.20.200']),
            dest = dict(view = 'All ZoneDirectors',
                        ips=['192.168.0.202', '192.168.0.199']),
        )
        sf_name = 'super_cuteo'
        schedule_cfg = dict(
            frequency = 'Daily',
            time = '10:00',
            period = 'PM',
            email = 'cuteo@cuteo.com'
        )

'''

import time
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
        sf_cfg = dict(
            is_uplink = True, is_downlink = True,
            src = dict(view = 'All Standalone APs', ips=['192.168.20.200']),
            dest = dict(view = 'All ZoneDirectors',
                        ips=['192.168.0.202', '192.168.0.199']),
        ),
        sf_name = 'super_cuteo',
        schedule_cfg = dict(
            frequency = 'Daily',
            time = '10:00',
            period = 'PM',
            email = 'cuteo@cuteo.com'
        )
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'))
    return p


def do_test(cfg):
    fm = cfg['fm']

    logging.info('Create a Speedflex')
    fm.lib.speedflex.create_speedflex(fm, cfg['sf_cfg'])

    logging.info('Now run that speedflex and dump the result')
    pp(fm.lib.speedflex.run_speedflex(fm))

    logging.info('Save the speedflex config for later usage')
    fm.lib.speedflex.save_speedflex(fm, cfg['sf_name'], cfg['schedule_cfg'])

    return dict(result='PASS', message='')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
