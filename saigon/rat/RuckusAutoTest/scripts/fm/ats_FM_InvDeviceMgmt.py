''' Model independent testcases '''

import sys
import copy
import re

from libFM_TestSuite import make_test_suite, get_testsuitename
from RuckusAutoTest.common.utils import log
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.components.lib.dev_features import FM as fmft


# model_map is in libFM_TestSuite.py
tc_templates = {
    '01.02.01.06': (
      [ 'TCID:%(tcid)s - Make sure "Edit view" can change device group search criteria',
        'FM_InvEditView',
        dict(
            view=dict(
                device_cate=fmft.device_cate['aps'],
                attr1=fmft.attrs['ip'],
                op1=fmft.ops['starts_with'],
                value_txt1='192.168', # all local aps, unless there's a change
                view_name='local_aps', # must match with saved_view
                view_desc='local_aps',
            ),
            saved_view='local_aps',
            updated_view=dict(
                device_cate=fmft.device_cate['aps'],
                attr1=fmft.attrs['ip'],
                op1=fmft.ops['starts_with'],
                value_txt1='192.168',

                combine_lnk1='and',
                attr2=fmft.attrs['model'],
                op2=fmft.ops['equals'],
                value_cb2='ZF7942', # check this on tb before adding in
                #update_view_name='local_aps', # for edit view name
            ),
            model='ZF7942',
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
    return get_testsuitename('fm_inv_devicemgmt'), [test_cfgs[k] for k in keys]


if __name__ == '__main__':
    _dict = as_dict( sys.argv[1:] )
    # make sure, at least, define_ts_cfg config is in the dict
    if 'define_ts_cfg' not in _dict: _dict['define_ts_cfg'] = define_ts_cfg
    if 'ignoreModel' not in _dict: _dict['ignoreModel'] = True
    make_test_suite(**_dict)
