'''
1.1.9.5. Factory Reset Testsuite
normal
  1.1.9.5.1 Create new Factory Reset task select by group
  1.1.9.5.2 Create new Factory Reset task select by device
  1.1.9.5.3 By schedule and repeat test cases 1.1.9.5.1-1.1.9.5.2
cancel
  1.1.9.5.4 Cancel the Reset task
result
  1.1.9.5.5 Result of Factory Reset task
FM 8.x
  1.1.9.5.6 Failed task could be restart
'''

import sys
import copy

from libFM_TestSuite import model_map, make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = ['01.01.09.05.01',    '01.01.09.05.02', '01.01.09.05.03.01',
             '01.01.09.05.03.02', '01.01.09.05.04', '01.01.09.05.05', ]

    tc_templates = [
      # 1.1.9.5.1 Create new Factory Reset task select by group
      [ 'TCID:%s.%s - Create new Factory Reset task (select by group) - %s',
        'FM_FactoryReset',
        { 'model': '%s',
          'device_select_by': 'group',
          'schedule': 0,
        },
      ],
      # 1.1.9.5.2 Create new Factory Reset task select by device
      [ 'TCID:%s.%s - Create new Factory Reset task (select by device) - %s',
        'FM_FactoryReset',
        { 'model': '%s',
          'device_select_by': 'device',
          'schedule': 0,
        },
      ],
      # 1.1.9.5.3 By schedule and repeat test cases 1.1.9.5.1-1.1.9.5.2
      [ 'TCID:%s.%s - By schedule provisioning Factory Reset task (by group) - %s',
        'FM_FactoryReset',
        { 'model': '%s',
          'device_select_by': 'group',
          'schedule': 3,
        },
      ],
      [ 'TCID:%s.%s - By schedule provisioning Factory Reset task (by device) - %s',
        'FM_FactoryReset',
        { 'model': '%s',
          'device_select_by': 'device',
          'schedule': 3,
        },
      ],
      # 1.1.9.5.4 Cancel the Reset task
      [ 'TCID:%s.%s - Cancel Factory Reset task - %s',
        'FM_FactoryReset',
        { 'test_type': 'cancel', 'model': '%s', },
      ],
      # 1.1.9.5.5 Result of Factory Reset task
      [ 'TCID:%s.%s - Result of Factory Reset task - %s',
        'FM_FactoryReset',
        { 'test_type': 'result', 'model': '%s', },
      ],
    ]

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                tc[2]['model'] = tc[2]['model'] % model

                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Factory Reset', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

