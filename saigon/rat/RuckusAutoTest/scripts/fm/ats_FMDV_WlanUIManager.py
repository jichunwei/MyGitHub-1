'''
3    Device View status in FM
3.1    Detail of ZF2925 8.0
3.1.8    Modify the wireless common parameters in Device View of FM
3.1.9    Modify the wireless parameters in Device View of FM

'''

import sys
import copy

from libFM_TestSuite import model_map, make_test_suite, select_ap_by_model, \
        get_aps_by_models
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
            '03.01.08', '03.01.09',
            ]

    multiple_cfg_tcs = ['03.01.09',]
    tc_templates = [
      [ 'TCID:%s.%s - Modify wlan common. Config: %s - %s',
        'FMDV_WlanUIManager',
        {
            'model': 'ZF2925',
            'cfg': {},
            'backup_cfg': {},
            'ap_ip': '',
        },
      ],
      [ 'TCID:%s.%02d.%s - Modify wlan detail. Config: %s - %s',
        'FMDV_WlanUIManager',
        {
            'model': 'ZF2925',
            'cfg': {},
            'ap_ip': '',
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        ap_cfg_obj = model_cfg_map2[model.lower()]
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                # tcs which need to test a lot cases
                if tc_id[i] in multiple_cfg_tcs:
                    wlan_cfgs = ap_cfg_obj.get_wlan_cfgs(is_dv_cfg=True, radio_mode='2.4G')
                    for j, cfg in enumerate(wlan_cfgs):
                        tc = copy.deepcopy(tc_templates[i])
                        # filling the template
                        tc[0] = tc[0] % (tc_id[i], j+1, model_map[model], cfg['name'], model.upper())
                        tc[2]['ap_ip'] = aps[model]
                        tc[2]['cfg'] = cfg['cfg']
                        tc[2]['model'] = model
                        test_cfgs['%s.%02d.%s' % (tc_id[i], (j+1), model_map[model])] = tc
                else:
                    tc = copy.deepcopy(tc_templates[i])
                    cfg = ap_cfg_obj.get_wlan_common_cfg(is_dv_cfg=True)
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], model_map[model], cfg['name'], model.upper())
                    tc[2]['ap_ip'] = aps[model]
                    tc[2]['cfg'] = cfg['cfg']
                    tc[2]['backup_cfg'] = ap_cfg_obj.get_wlan_common_cfg(is_dv_cfg=True)['cfg']
                    tc[2]['model'] = model
                    test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc
    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View Status - WLAN UI Manager', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

