'''
Device View
3.1.5    Internet/WAN parameters
3.1.6    Modify the Device View Internet/WAN status with STATIC IP address
3.1.7    Modify the Device View Internet/WAN status with DYNAMIC IP address
'''

import sys
import copy

from libFM_TestSuite import model_map, make_test_suite, select_ap_by_model, \
        get_aps_by_models
from RuckusAutoTest.common.lib_KwList import as_dict


def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed:
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = ['03.01.05', '03.01.06', '03.01.07', ]

    tc_templates = [
      [ 'TCID:%s.%s - Internet/WAN parameters - %s',
        'FMDV_InternetManager',
        {
            'ap_ip': '',
            'test_name': 'Internet/WAN parameters',
            'test_type': 'display', # dhcp, static
        },
      ],
      [ 'TCID:%s.%s - Modify the Device View Internet/WAN status with STATIC IP address - %s',
        'FMDV_InternetManager',
        {
            'ap_ip': '',
            'test_name': 'Internet/WAN parameters',
            'test_type': 'static', # dhcp, static
        },
      ],
      [ 'TCID:%s.%s - Modify the Device View Internet/WAN status with DYNAMIC IP address - %s',
        'FMDV_InternetManager',
        {
            'ap_ip': '',
            'test_name': 'Internet/WAN parameters',
            'test_type': 'dhcp', # dhcp, static
        },
      ],
    ]

    tbcfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbcfg),kwa['is_interactive'])

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                #for j in range(len(tc_templates)):
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                tc[2]['ap_ip'] = aps[model]
                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View Status - Internet Manager', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
