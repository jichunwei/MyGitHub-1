'''
1.1.9.8    Manage ZoneDirector Configuration

1.1.9.8.1    Add ZD configuration to FM
1.1.9.8.2    Editable Configuration file list

'''

import sys
import copy

from libFM_TestSuite import model_map, make_test_suite, \
        select_zd_by_model, get_zd_by_models
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zd1k', 'zd3k']

    NOTE: Currently support zd1k only
    - testbed:
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have
    # Currently support 1k only
    tc_id = ['01.01.09.08.01', '01.01.09.08.02',]

    tc_templates = [
      [ 'TCID:%s.%s - Add ZD configuration to FM - %s',
        'FM_ManageZdCfg',
        {
            'zd_ip': '',
            'test_type': 'add', # dhcp, static
        },
      ],
      [ 'TCID:%s.%s - Editable Configuration file list - %s',
        'FM_ManageZdCfg',
        {
            'zd_ip': '',
            'test_type': 'edit', # dhcp, static
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    zds = select_zd_by_model(get_zd_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    print 'Generate testcases for model(s)/ZD(s): %s' \
          % (', '.join(['%s (%s)' % (m, zds[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                #for j in range(len(tc_templates)):
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                tc[2]['zd_ip'] = zds[model]
                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Configure - Manage ZD Configs', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_zd_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

