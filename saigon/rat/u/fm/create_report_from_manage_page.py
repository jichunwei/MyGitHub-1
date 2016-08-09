'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to do create report from:
    . Reports > Manage Reports > Saved Reports
#------------------------------------------------------------------------------

Examples to generate report:
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_dv_report_zd_params
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_dv_report_ap_params
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_connectivity_report_zd_params
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_connectivity_report_ap_params
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_provision_report_params
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_events_report_params
tea.py u.fm.create_report_from_manage_page fm_ip=192.168.30.252 cfg=manage_speed_flex_report_params
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

def _find_report(cfg):
    ''''''
    res = rp.find_report(cfg['fm'], cfg['fn_params']['report_name'])
    if res:
        return dict(result='PASS', message='Found the created report')
    else:
        return dict(
            result  = 'ERROR',
            message = 'Not found the created report: %s' % \
                    cfg['fn_params']['report_name']
        )

def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        cfg = 'manage_dv_report_zd_params',
        create_fn = None,
        fn_params = {}
    )
    p.update(cfg)

    cfg_var_name = p.pop('cfg')
    # get the variable name in the string
    cfg_params = eval('rp_cfg.' + cfg_var_name)
    if not isinstance(cfg_params, dict):
        raise Exception('Variable name "%s" must be a dict' % cfg_var_name)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip'))

    p['create_fn'] = rp.create_report_from_manage_page

    # params for the report function accordingly
    p['fn_params'] = dict(
        fm = p['fm'],
        report_name    = get_unique_name(cfg_params['report_type']),
        report_options = cfg_params['report_options'],
        filter_options = cfg_params['filter_options'],
        save_cfg       =  cfg_params['save_cfg'],
        get_result     = False,
    )

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _create_report(cfg)
    if res: return dict(result='ERROR', message = res)

    res = _find_report(cfg)

    return res


def do_clean_up(cfg):
    try:
        rp.delete_report(cfg['fm'], cfg['fn_params']['report_name'])
    except:
        pass

    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
