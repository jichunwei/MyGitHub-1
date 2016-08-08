'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to do generate report from:
    . Reports > Manage Reports > Saved Reports.
#------------------------------------------------------------------------------

Examples to generate report:
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_dv_report_zd_params
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_dv_report_ap_params
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_connectivity_report_zd_params
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_connectivity_report_ap_params
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_provision_report_params
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_events_report_params
tea.py u.fm.generate_report_from_manage_page fm_ip=192.168.30.252 report_param=manage_speed_flex_report_params
'''

import logging
from pprint import pformat
from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components.lib.fm9 import report_mgmt as rp
import _report_mgmt_cfg as rp_cfg
#-------------------------------------------------------------------------------

def _generate_report(cfg):
    '''
    '''
    try:
        res = cfg['generate_fn'](**cfg['fn_params'])
        if res:
            logging.info('Report result:\n%s' % pformat(res))
        else:
            logging.info('There is no data for this report')

        return dict(result='PASS', message='Generated the report successfully')
    except Exception:
        log_trace()
        return dict(result='ERROR', message='Could not Generated the report')


def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        report_param = 'manage_dv_report_zd_params',
        generate_fn = None,
        fn_params = {}
    )
    p.update(cfg)

    cfg_var_name = p.pop('report_param')
    # get the variable name in the string
    cfg_params = eval('rp_cfg.' + cfg_var_name)
    if not isinstance(cfg_params, dict):
        raise Exception('Variable name "%s" must be a dict' % cfg_var_name)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip'))

    p['generate_fn'] = rp.generate_report_from_manage
    # params for the report function accordingly
    p['fn_params'] = dict(
        fm = p['fm'],
        report_options = cfg_params['report_options'],
        filter_options = cfg_params['filter_options'],
        get_result     = cfg_params['get_result'],
    )

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _generate_report(cfg)
    return res


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
