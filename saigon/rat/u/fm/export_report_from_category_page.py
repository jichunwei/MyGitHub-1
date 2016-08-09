'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to do create report from:
    . Reports > Report Categories.
#------------------------------------------------------------------------------

Examples to generate report:
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=dv_report_zd_params
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=dv_report_ap_params
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=connectivity_report_zd_params
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=connectivity_report_ap_params
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=provision_report_params
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=events_report_params
tea.py u.fm.export_report_from_category_page fm_ip=192.168.30.252 cfg=speed_flex_report_params
'''

import logging
import os
from pprint import pformat
from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components.lib.fm9 import report_mgmt as rp
import _report_mgmt_cfg as rp_cfg # cfg file to do export
#-------------------------------------------------------------------------------

def _export_report(cfg):
    '''    '''
    try:
        export_file = cfg['create_fn'](**cfg['fn_params'])
        logging.info('Export the report successfully to %s' % export_file)
        cfg['result_file'] = export_file
        return dict(result='PASS', message='Export the report successfully')
    except Exception, e:
        log_trace()
        return dict(
            result  = 'ERROR',
            message = 'Could not export the report. Error: %s' % e.__str__()
        )


def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        cfg = 'dv_report_zd_params',
        create_fn = None,
        fn_params = {},
        result_file = '',
    )
    p.update(cfg)

    cfg_var_name = p.pop('cfg')
    # get the variable name in the string
    cfg_params = eval('rp_cfg.' + cfg_var_name)
    if not isinstance(cfg_params, dict):
        raise Exception('Variable name "%s" must be a dict' % cfg_var_name)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip'))

    # get the report function according to the input cfg
    p['create_fn'] = dict(
        device_view     = rp.export_device_view_report,
        connectivity    = rp.export_connectivity_report,
        active_firmware = rp.export_active_firmware_report,
        association     = rp.export_association_report,
        provision       = rp.export_provision_report,
        events          = rp.export_events_report,
        speed_flex      = rp.export_speed_flex_report,
    )[cfg_params['report_type']]

    # params for the report function accordingly
    p['fn_params'] = dict(
        fm = p['fm'],
        report_options = cfg_params['report_options'],
        filter_options = cfg_params['filter_options'],
    )

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _export_report(cfg)
    return res


def do_clean_up(cfg):
    try:
        os.remove(cfg['result_file'])
        logging.info('Removed the file %s' % cfg['result_file'])
    except:
        pass

    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
