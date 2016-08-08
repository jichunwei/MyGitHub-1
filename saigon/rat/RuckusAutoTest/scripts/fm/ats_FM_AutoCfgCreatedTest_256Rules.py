import sys
import copy

from libFM_TestSuite import make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict


'''
1.1.7.3.2.2    Create many auto configuration rule and check all of rules can work properly



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
    1.1.7.3.2.2    Create many auto configuration rule and check all of rules can work properly

    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = ['01.01.07.03.02.02']
    # Define a simple config to test these tcs
    simple_cfg = {
        'device_general': {'device_name': 'RuckusAP_AutoCfgStressTest'}
    }

    tc_templates = [
      # 1.1.7.3.2.1    Validate consistency about product type, template and model type
      [ 'TCID:%s - Create many auto configuration rule and check all of rules can work properly',
        'FM_AutoCfgRuleCreatedTest',
        {
            'test_type': 'stressTest',
            'no_rule': 20,
            #'model': '%s',
            #'device_group': 'All Standalone APs',
            '2925_options': simple_cfg,
            '2942_options': simple_cfg,
            '7942_options': simple_cfg,
            '7962_options': simple_cfg,
        },
      ],
    ]

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])

    test_cfgs = {}
    tc = copy.deepcopy(tc_templates[0])
    # filling the template
    #tc[0] = tc[0] % (tc_map[model][i], model_map[model], model.upper())
    #tc[2]['model'] = tc[2]['model'] % model
    tc[0] = tc[0] % (tc_id[0])
    test_cfgs['%s' % (tc_id[0])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Auto Cfg Created Test - Stress Test', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)


