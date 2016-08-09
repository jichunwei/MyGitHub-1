import sys
import copy

from libFM_TestSuite import model_map, make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict


'''
1.1.7.3.2.1    Validate consistency about product type, template and model type
1.1.7.3.2.3    User can stop auto configuration task
1.1.7.3.2.4    User can re-start auto configuration task after stop auto configuration task


Detail AP configuration for templates returned from getAPCfgTemplate() function
    {
        'zf2925'[{config_1}, {config_2}, {config_3}, {config_4}],
        'zf2942'[{config_1}, {config_2}, {config_3}, {config_4}],
        'zf7942'[{config_1}, {config_2}, {config_3}, {config_4}],
    }
    Detail for config_1: Device General (complex), WLAN Common, WLAN 1 to 4, Rate Limiting
    Detail for config_2: Device General (simple), WLAN Common, WLAN 5 to 8, Rate Limiting
    Detail for config_3: Device General (simple), WLAN Common, WLAN 1 to 8, No Rate Limiting
    Detail for config_4: WLAN 1 to 8, No Rate Limiting
'''


def define_ts_cfg(**kwa):
    '''
    This function is to generate testsuites for following test cases:
    1.1.7.3.2.1    Validate consistency about product type, template and model type
    1.1.7.3.2.3    User can stop auto configuration task
    1.1.7.3.2.4    User can re-start auto configuration task after stop auto configuration task

    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = ['01.01.07.03.02.01', '01.01.07.03.02.03', '01.01.07.03.02.04',]
    # Define a simple config to test these tcs
    simple_cfg = {
        'device_general': {'device_name': 'RuckusAP_AutoCfgTest'}
    }

    tc_templates = [
      # 1.1.7.3.2.1    Validate consistency about product type, template and model type
      [ 'TCID:%s.%s - Validate consistency about product type, template and model type - %s',
        'FM_AutoCfgRuleCreatedTest',
        {
            'test_type': 'validateInputData',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'options': '', #simple_cfg,
        },
      ],
      # 1.1.7.3.2.3    User can stop auto configuration task
      [ 'TCID:%s.%s - User can stop auto configuration task - %s',
        'FM_AutoCfgRuleCreatedTest',
        {
            'test_type': 'stop_auto_cfg_rule',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'options': '', #simple_cfg,
        },
      ],
      # 1.1.7.3.2.4    User can re-start auto configuration task after stop auto configuration task
      [ 'TCID:%s.%s - User can re-start auto configuration task after stop auto configuration task - %s',
        'FM_AutoCfgRuleCreatedTest',
        {
            'test_type': 'restart_auto_cfg_rule',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'options': '', #simple_cfg,
        },
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
                tc[2]['options'] = simple_cfg

                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Auto Cfg Created Test', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)



