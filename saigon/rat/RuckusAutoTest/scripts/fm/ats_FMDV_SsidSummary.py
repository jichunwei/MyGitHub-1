'''
Device View Status
3.1.3    4/8/16 SSIDs summary displays in Summary page of FM Device View.

'''

import sys
import copy
from libFM_TestSuite import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models, get_testsuite
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import model_cfg_map2



def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed:
    return:
    - (testsuite name, testcase configs)
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = [
            '03.01.03',
            ]

    multiple_cfg_tcs = ['03.01.03',]
    tc_templates = [
      [ 'TCID:%s.%02d.%s - Verify SSIDs summary display config: "%s" - %s',
        'FMDV_SsidSummary',
        {
            'model': 'ZF2925',
            'cfg': {},
            'ap_ip': '',
            'test_name': 'SSID Summary',
        },
      ],
    ]

    tbcfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbcfg),kwa['is_interactive'])

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        ap_cfg_obj = model_cfg_map2[model.lower()]
        cfgs = ap_cfg_obj.get_wlan_cfgs(is_dv_cfg=True, radio_mode='2.4G')
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                # tcs which need to test a lot cases
                if tc_id[i] in multiple_cfg_tcs:
                    for j, cfg in enumerate(cfgs):
                        tc = copy.deepcopy(tc_templates[i])
                        # filling the template
                        tc[0] = tc[0] % (
                            tc_id[i], j+1, model_map[model],
                            cfg['name'], model.upper()
                        )
                        tc[2]['model'] = model
                        tc[2]['ap_ip'] = aps[model]
                        tc[2]['test_name'] = 'SSID Summary'
                        tc[2]['cfg'] = cfg['cfg']

                        test_cfgs['%s.%02d.%s' % (tc_id[i], (j+1), model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View Status - SSID Summary Display', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
