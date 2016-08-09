'''
monitor > events page: filtering the events page according to the given config
and download as xls and cvs files

tea.py u.fm.events_search_n_save fm_ip_addr=192.168.30.252 filter=[['Serial Number', 'Contains', 'ZF']]
'''

import time
import logging

from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env


def do_config(cfg):
    p = dict(
        fm_ip_addr = '192.168.20.252',
        filter = [['Serial Number', 'Contains', 'ZF']],
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'))
    return p


def do_test(cfg):
    logging.info('Filter and get the detail')
    cfg['fm'].lib.event.get_all_events_by_filter(cfg['fm'], cfg['filter'])
    time.sleep(3)

    logging.info('Now save the result as xls and csv files')
    cfg['fm'].lib.event.export_events_to_file(cfg['fm'], filetype='xls')
    cfg['fm'].lib.event.export_events_to_file(cfg['fm'], filetype='csv')

#    pp(cfg['fm'].lib.event.get_all_views(cfg['fm']))
#    cfg['fm'].lib.event.create_view(cfg['fm'], 'cuteo', cfg['filter'])

    return dict(result='PASS', message='Able to filter and get result')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
