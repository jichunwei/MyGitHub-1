'''
1.1.9.4. Reboot Testsuite

normal
  1.1.9.4.1 Create new reboot task select by AP group
  1.1.9.4.2 Create new reboot task select by device
  1.1.9.4.4 By schedule and repeat test cases 1.1.9.4.1-1.1.9.4.3
cancel
  1.1.9.4.5 Cancel the reboot task
result
  1.1.9.4.6 Result of reboot task
FM 8.x
  1.1.9.4.3 Create new reboot task select by ZD group
  1.1.9.4.7 Failed task could be restart
'''

import sys
import copy

from libFM_TestSuite import (
        model_map, make_test_suite, select_ap_by_model, get_aps_by_models,
        get_testsuitename, filter_tcs, sort_tcfg, get_tcid
)
from RuckusAutoTest.common.lib_KwList import as_dict
#from RuckusAutoTest.common.utils import log


tc_templates = {
    '01.01.09.04.01': (
        [ 'TCID:%(tcid)s.%(model_id)02d - Create new reboot task (select by group) - %(model)s',
          'FM_ApReboot',
          { 'model': '%(model)s',
            'device_select_by': 'group',
            'schedule': 0,
          },
        ],
    ),
    '01.01.09.04.02': (
        [ 'TCID:%(tcid)s.%(model_id)02d - Create new reboot task (select by device) - %(model)s',
          'FM_ApReboot',
          { 'model': '%(model)s',
            'device_select_by': 'device',
            'schedule': 0,
          },
        ],
    ),
    '01.01.09.04.04': (
        [ 'TCID:%(tcid)s.01.%(model_id)02d - By schedule provisioning reboot task (by group) - %(model)s',
          'FM_ApReboot',
          { 'model': '%(model)s',
            'device_select_by': 'group',
            'schedule': 3,
          },
        ],
        [ 'TCID:%(tcid)s.02.%(model_id)02d - By schedule provisioning reboot task (by device) - %(model)s',
          'FM_ApReboot',
          { 'model': '%(model)s',
            'device_select_by': 'device',
            'schedule': 3,
          },
        ],
    ),
    '01.01.09.04.05': (
        [ 'TCID:%(tcid)s.%(model_id)02d - Cancel reboot task - %(model)s',
          'FM_ApReboot',
          { 'test_type': 'cancel', 'model': '%(model)s', },
        ],
    ),
    '01.01.09.04.06': (
        [ 'TCID:%(tcid)s.%(model_id)02d - Result of reboot task - %(model)s',
          'FM_ApReboot',
          { 'test_type': 'result', 'model': '%(model)s', },
        ],
    ),
}


tcs = tc_templates.keys()
filtered_tcs = {}


def fill_tc_cfg(tc, cfg):
    tc[0] = tc[0] % cfg
    #log(tc[0])
    tc_cfg = tc[2]
    tc_cfg['model'] = tc_cfg['model'] % cfg
    return tc


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed
    return:
    - (testsuite name, testcase configs)
    '''
    tbcfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbcfg),kwa['is_interactive'])

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model, tcid in filter_tcs(kwa['models'], tcs, filtered_tcs):
        for tc_tmpl in tc_templates[tcid]:
            tc = copy.deepcopy(tc_tmpl)
            fill_tc_cfg(
                tc,
                dict(
                    tcid = tcid,
                    model_id = int(model_map[model]),
                    model = model.upper(),
                )
            )
            test_cfgs[get_tcid(tc[0])] = tc
    return get_testsuitename('prov_reboot'), sort_tcfg(test_cfgs)


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

