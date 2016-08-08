'''
1.1.9.6    Manage firmware Files Test suite

1.1.9.6.1  Create new fw upload file
1.1.9.6.2  Edit a firmware file
1.1.9.6.3  Delete firmware file
'''

import sys
from pprint import pformat

from libFM_TestSuite import get_local_firmwares, input_builds, \
        make_test_suite, model_map
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = ['01.01.09.06.01', '01.01.09.06.02', '01.01.09.06.03', ]

    tc_templates = [
      # 1.1.9.6.1  Create new fw upload file
      [ 'TCID:%s.%s - Create new fw upload file - %s',
        'FM_ManageFirmwares',
        { 'test_type': 'upload',
          'model':     '%s',
          'filename':  '%s',
        },
      ],
      # 1.1.9.6.2  Edit a firmware file
      [ 'TCID:%s.%s - Edit a firmware file - %s',
        'FM_ManageFirmwares',
        { 'test_type':  'edit',
          'model':      '%s',
          'filename':  '%s',
          'test_model': '%s', # not the edited one
        },
      ],
      # 1.1.9.6.3  Delete firmware file
      [ 'TCID:%s.%s - Delete firmware file - %s',
        'FM_ManageFirmwares',
        { 'test_type': 'delete',
          'model':     '%s',
          'filename':  '%s',
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    fmCfg = tbCfg['FM']
    print 'Getting the list of firmwares...'
    localFws = get_local_firmwares(isFmFwIncluded=False, fmCfg=fmCfg)

    builds = input_builds(models=kwa['models'], localFws=localFws, is_interactive=kwa['is_interactive'])
    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    print 'Selected firmwares:\n%s\n' % pformat([(k, builds[k][1]) for k in builds.keys()])
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                import copy
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                tc[2]['model'] = tc[2]['model'] % model
                tc[2]['filename'] = tc[2]['filename'] % builds[model][1]

                if tc[2].has_key('test_model'):
                    tc[2]['test_model'] = [k for k in model_map.keys() if k != model][0]

                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Manage Firmwares', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

