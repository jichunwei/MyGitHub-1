''' Model independent testcases '''
import copy
import re
import sys

from libFM_TestSuite import make_test_suite, get_testsuitename
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.common.utils import log
from RuckusAutoTest.components.lib.dev_features import FM as fmft


# model_map is in libFM_TestSuite.py
tc_templates = {
    '01.02.02.05': (
      [ 'TCID:%(tcid)s.01 - Filter AP/ZD report can work correctly (AP)',
        'FM_InvFilterView',
        dict(
            report=dict(
                report_cate=fmft.report_cates['device_view'],
                view=fmft.predef_views['aps'],
                report_type=fmft.report_types['aps'],
                generate_btn='report_type',
            ),
            testcase='aps',
        ),
      ],
      [ 'TCID:%(tcid)s.02 - Filter AP/ZD report can work correctly (ZD)',
        'FM_InvFilterView',
        dict(
            report=dict(
                report_cate=fmft.report_cates['device_view'],
                view=fmft.predef_views['zds'],
                report_type=fmft.report_types['zds'],
                generate_btn='report_type',
            ),
            testcase='zds',
        ),
      ],
    ),
    '01.02.02.04': (
      [ 'TCID:%(tcid)s - Save report as xls',
        'FM_InvSaveReport',
        dict(
            report=dict(
                report_cate=fmft.report_cates['device_view'],
                view=fmft.predef_views['aps'],
                report_type=fmft.report_types['aps'],
                #generate_btn='report_type',
                #advanced_ops_btn='report_type',
                #save_report_btn=None, # for clicking on this
            ),
            #report_file='report.xls',
        ),
      ],
    ),

    '01.02.02.01': (
      [ 'TCID:%(tcid)s - All ZoneDirector report',
        'FM_InvFilterView',
        dict(
            report=dict(
                report_cate=fmft.report_cates['device_view'],
                view=fmft.predef_views['zds'],
                report_type=fmft.report_types['zds'],
                generate_btn='report_type',
            ),
            testcase='zds',
        ),
      ],
    ),
    '01.02.02.02': (
      [ 'TCID:%(tcid)s - ZoneDirector Managed APs report',
        'FM_InvFilterView',
        dict(
            report=dict(
                report_cate=fmft.report_cates['device_view'],
                view=fmft.predef_views['zds'],
                report_type=fmft.report_types['zd_ap'],
                generate_btn='report_type',
            ),
            testcase='zd_ap',
        ),
      ],
    ),
    '01.02.02.03': (
      [ 'TCID:%(tcid)s - ZoneDiector associated clients',
        'FM_InvFilterView',
        dict(
            report=dict(
                report_cate=fmft.report_cates['device_view'],
                view=fmft.predef_views['zds'],
                report_type=fmft.report_types['zd_client'],
                generate_btn='report_type',
            ),
            testcase='zd_client',
        ),
      ],
    ),
}


def fill_tc_cfg(tc, cfg):
    tc[0] = tc[0] % cfg
    log(tc[0])
    return tc


def define_ts_cfg(**kwa):
    '''
    kwa:    models, testbed
    return: (testsuite name, testcase configs)
    '''
    test_cfgs = {}
    for tcid in tc_templates:
        for tc_tmpl in tc_templates[tcid]:
            tc = copy.deepcopy(tc_tmpl)
            fill_tc_cfg(tc, dict(tcid = tcid,))
            test_cfgs[re.search('TCID:(.*?) -', tc[0]).group(1)] = tc
    keys = test_cfgs.keys()
    keys.sort()
    return get_testsuitename('fm_inv_reports_fm'), [test_cfgs[k] for k in keys]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    if 'define_ts_cfg' not in _dict: _dict['define_ts_cfg'] = define_ts_cfg
    if 'ignoreModel' not in _dict: _dict['ignoreModel'] = True
    make_test_suite(**_dict)
