'''
navigating from Dashboard to Reports page and get the detail info

tea.py u.fm.dashboard_to_report fm_ip_addr=192.168.30.252 zd_view_report="dict(view_name='All ZoneDirectors', type='aps', is_conn=True)" get_result=True
tea.py u.fm.dashboard_to_report fm_ip_addr=192.168.30.252 ap_view_report="dict(view_name='All Standalone APs', type='connected')"
tea.py u.fm.dashboard_to_report fm_ip_addr=192.168.30.252 event_report="dict(event_type='AP approv pending', type='zd_event_count')"
'''

import time
import logging
from pprint import pformat

from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env


def _get_result(cfg):
    if cfg['get_result']:
        logging.info('.. Get the result and print out')
        logging.info(pformat(cfg['fm'].lib.rp.get_report_result(cfg['fm'])))


def do_config(cfg):
    p = dict(
        fm_ip_addr = '192.168.20.252',
        zd_view_report=dict(view_name='All ZoneDirectors', type='aps', is_conn=True),
        ap_view_report=dict(view_name='All Standalone APs', type='connected'),
        event_report=dict(event_type='AP approv pending', type='zd_event_count'),
        get_result = True,
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'))
    p['zd_view_report']['fm'] = p['fm']
    p['ap_view_report']['fm'] = p['fm']
    p['event_report']['fm'] = p['fm']
    return p


def do_test(cfg):
    logging.info('Navigating from Dashboard to Reports page')
    logging.debug('Config:\n%s' % pformat(cfg))
    
    logging.info('1. navigate from ZD view table')
    cfg['fm'].lib.dashboard.goto_zd_view_report(**cfg['zd_view_report'])
    _get_result(cfg)
    time.sleep(3)
    
    logging.info('2. navigate from AP view table')
    cfg['fm'].lib.dashboard.goto_ap_view_report(**cfg['ap_view_report'])
    _get_result(cfg)
    time.sleep(3)
    
    logging.info('3. navigate from Events table')
    cfg['fm'].lib.dashboard.goto_event_report(**cfg['event_report'])
    _get_result(cfg)
    time.sleep(3)

    return dict(result='PASS', message='Able to navigate and get result')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
