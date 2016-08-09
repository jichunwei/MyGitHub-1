'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to support following functions in Reports > Manage Reports > Saved Reports
 . query
 . edit
 . delete
#------------------------------------------------------------------------------

Examples to do other functions: query, edit, delete
tea.py u.fm.query_edit_delete_report fm_ip=192.168.30.252 action=query
tea.py u.fm.query_edit_delete_report fm_ip=192.168.30.252 action=edit
tea.py u.fm.query_edit_delete_report fm_ip=192.168.30.252 action=delete
'''

import logging
from pprint import pformat
from RuckusAutoTest.common.utils import log_trace, get_unique_name
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components.lib.fm9 import report_mgmt as rp
import _report_mgmt_cfg as rp_cfg
#-------------------------------------------------------------------------------

def _create_report(cfg):
    '''
    '''
    msg = None
    try:
        res = cfg['create_fn'](**cfg['fn_params'])
        logging.info('Created report successfully')
        if cfg['fn_params']['get_result']:
            logging.info('Report result:\n %s' % pformat(res))
    except Exception, e:
        log_trace()
        msg = 'Could not create the report. Error: %s' % e.__str__()

    return msg

def _query_report(cfg):
    ''''''
    try:
        res = rp.query_report(cfg['fm'], cfg['fn_params']['report_name'])

        if res:
            logging.info('Query result: \n%s' % pformat(res))
        else:
            logging.info('No data found')
        return dict(result='PASS', message='Query the report successfully')
    except Exception, e:
        return dict(
            result  = 'ERROR',
            message = 'Error while querying report. Error:%s' % e.__str__()
        )

def _delete_report(cfg):
    ''''''
    try:
        rp.delete_report(cfg['fm'], cfg['fn_params']['report_name'])
        return dict(result='PASS', message='Delete the report successfully')
    except Exception, e:
        return dict(
            result  = 'ERROR',
            message = 'Error while delete the report. Error:%s' % e.__str__()
        )

def _edit_report(cfg):
    ''''''
    try:
        res = rp.edit_all_report_attributes(**cfg['new_fn_params'])
        if res:
            logging.info(
                'Result of new report %s: \n%s' %
                (cfg['new_fn_params']['new_name'], pformat(res))
            )
        else:
            logging.info(
                'The new report %s has no data' % cfg['new_fn_params']['new_name']
            )
        return dict(result='PASS', message='Edit the report successfully')
    except Exception, e:
        return dict(
            result  = 'ERROR',
            message = 'Error while querying report. Error:%s' % e.__str__()
        )

def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        action = 'query',
        create_fn = rp.create_report_from_manage_page,
        fn_params = {},
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip'))
    cfg_params = rp_cfg.manage_dv_report_ap_params

    # params for the report function accordingly
    p['fn_params'] = dict(
        fm = p['fm'],
        report_name = get_unique_name(cfg_params['report_type']),
        report_options = cfg_params['report_options'],
        filter_options = cfg_params['filter_options'],
        save_cfg       = cfg_params['save_cfg'],
        get_result     = False,
    )
    if p['action'] == 'edit':
        new_cfg_params = rp_cfg.manage_dv_report_zd_params
        p['new_fn_params'] = dict(
            fm = p['fm'],
            report_name = p['fn_params']['report_name'],
            new_name    = 'new_' + p['fn_params']['report_name'],
            report_options = new_cfg_params['report_options'],
            filter_options = new_cfg_params['filter_options'],
            save_cfg       = new_cfg_params['save_cfg'],
            get_result     = True,
        )

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _create_report(cfg)
    if res: return dict(result='ERROR', message = res)

    test_fn = dict(
        query = _query_report,
        delete = _delete_report,
        edit = _edit_report,
    )[cfg['action']]

    res = test_fn(cfg)
    return res


def do_clean_up(cfg):
    try:
        if cfg['action'] == 'edit':
            rp.delete_report(cfg['fm'], cfg['new_fn_params']['report_name'])
        else:
            rp.delete_report(cfg['fm'], cfg['fn_params']['report_name'])
    except:
        pass

    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
