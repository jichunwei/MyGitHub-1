import sys
import copy

from libFM_TestSuite import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models
from RuckusAutoTest.common.lib_KwList import as_dict
from libFM_DevCfg import ZF2741_Cfg, ZF2925_Cfg, ZF2942_Cfg, ZF7942_Cfg, ZF7962_Cfg
from libFM_DevCfg import get_ap_test_cfg_tmpl
'''
IMPORTANT NOTE: Currently, this test suite is just to support 7962 only. We have
                to change define_wep_cfg, define_wpa_cfg functions to support
                other models

1.2.3.13    Auto configuration test for ZF7962 by AP8.1
'''

def define_ts_cfg(**kwa):
    '''
    This function is to generate testsuites for following test cases:
    1.2.3.13    Auto configuration test for ZF7962 by AP8.1    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = ['01.02.03.13.01', '01.02.03.13.02']

    complex_cfg_tcs = []

    tc_templates = [
        # 1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
        # 1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
        # 1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)
        [ 'TCID:%s.%02d.%s - Auto configuration test 2.4GHz- %s',
          'FM_AutoCfgTest_2',
          {
            'test_name': '',
            'radio_mode': '2.4G',
            'ap_ip': 'AP ip',
            'model': 'AP model',
            'device_group': 'All Standalone APs',
            'input_cfg': {},
          },
        ],
        [ 'TCID:%s.%02d.%s - Auto configuration test 5GHz- %s',
          'FM_AutoCfgTest_2',
          {
            'test_name': '',
            'radio_mode': '5G',
            'ap_ip': 'AP ip',
            'model': 'AP model',
            'device_group': 'All Standalone APs',
            'input_cfg': {},
          },
        ],
    ]
    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    test_cfgs = {}
    for model in kwa['models']:
        # get config for this model
        model_cfg = {
            'zf7962': ZF7962_Cfg(),
        }[model.lower()]
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                cfgs = get_ap_test_cfg_tmpl(kwa['models'], tc_templates[i][2]['radio_mode'])
                for j in range(len(cfgs[model.upper()])):
                    tc = copy.deepcopy(tc_templates[i])
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], (j+1), model_map[model], model.upper())
                    tc[2]['model'] = model.upper()
                    tc[2]['ap_ip'] = aps[model]
                    # List options
                    tc[2]['test_name'] = cfgs[model.upper()][j]['cfg_name']
                    tc[2]['input_cfg'] = cfgs[model.upper()][j]['cfg']

                    test_cfgs['%s.%02d.%s' % (tc_id[i], (j+1), model_map[model])] = tc


    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Auto Configuration Test ZF7962', [test_cfgs[k] for k in keys]

def define_device_type():
    '''
    .  List of device type
    '''
    return ['dual_band']

if __name__ == '__main__':
    '''
    IMPORTANT NOTE: Currently, this test suite is just to support 7962 only. We have
                    to change define_wep_cfg, define_wpa_cfg functions to support
                    other models
    '''
    # make sure, at least, define_ts_cfg config is in the dict
    print '*'*80
    print 'NOTE: This test suite is just to support model ZF7962 only'
    print '*'*80
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

