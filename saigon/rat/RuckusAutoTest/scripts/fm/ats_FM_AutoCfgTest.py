import sys
import copy
import random

from libFM_TestSuite import model_map, make_test_suite
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import model_cfg_map, define_ap_cfg

'''
1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)
1.1.7.3.1.4    Auto configuration test for VF2825
1.1.7.3.1.5    Auto configuration test for VF7811
1.1.7.3.1.6    Auto configuration test for VF2741
1.1.7.3.1.7    Pre-registeration data test by Tag name
1.1.7.3.1.8    Auto configuration priority check
1.1.7.3.1.9    Already registrer AP test
1.1.7.3.1.10.1    Create a device group base on "Serial number" then Device group select this one  and repeat test case 1.1.7.3.1.1 - 1.1.7.3.1.6


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
    1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
    1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
    1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)
    1.1.7.3.1.4    Auto configuration test for VF2825
    1.1.7.3.1.5    Auto configuration test for VF7811
    1.1.7.3.1.6    Auto configuration test for VF2741

    1.1.7.3.1.7    Pre-registeration data test by Tag name
    1.1.7.3.1.8    Auto configuration priority check
    1.1.7.3.1.9    Already registrer AP test
    1.1.7.3.1.10    Create a device group base on "Serial number" then Device group select this one  and repeat test case 1.1.7.3.1.1 - 1.1.7.3.1.6
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = ['01.01.07.03.01.01', '01.01.07.03.01.07', '01.01.07.03.01.08',
             '01.01.07.03.01.09', '01.01.07.03.01.10']

    complex_cfg_tcs = ['01.01.09.02.01', '01.01.09.02.02', '01.01.09.02.04','01.01.09.02.10', '01.01.09.02.11.01',
                       '01.01.09.02.11.02', ]
    simple_cfg_tcs = ['01.01.09.02.12', '01.01.09.02.13', '01.01.09.02.14']

    # Define a simple config to test these tcs
    simple_cfg = {
        'device_general': {'device_name': 'RuckusAP_PriorityCheck'}
    }

    tc_templates = [
      # 1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
      # 1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
      # 1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)
      [ 'TCID:%s - Auto configuration test - %s',
        'FM_AutoCfgTest',
        {
            'test_type': 'normal',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'options': {},
        },
      ],
      # 1.1.7.3.1.7    Pre-registeration data test by Tag name
      [ 'TCID:%s - Pre-registeration data test by Tag name - %s',
        'FM_AutoCfgTest',
        {
            'test_type': 'pre-Registration',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'tag': '',
        },
      ],
      # 1.1.7.3.1.8    Auto configuration priority check
      [ 'TCID:%s - Auto configuration priority check - %s',
        'FM_AutoCfgTest',
        {
            'test_type': 'priorityCheck',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'options': {},
            'ex_options': {},
        },
      ],
      # 1.1.7.3.1.9    Already registrer AP test
      [ 'TCID:%s - Already registered AP test - %s',
        'FM_AutoCfgTest',
        {
            'test_type': 'registeredAp',
            'model': '%s',
            'device_group': 'All Standalone APs',
            'options': {},
        },
      ],
      # 1.1.7.3.1.10    Create a device group base on "Serial number" then Device group select this one
      [ 'TCID:%s - Create a device group base on "Serial number" then Device group select this one - %s',
        'FM_AutoCfgTest',
        {
            'test_type': 'serialBase',
            'model': '%s',
            # This test requires a Device Group created base on device serial so we let
            # the test script creates the Device Group
            # 'device_group': '',
            'options': {},
        },
      ],
    ]

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    NORMAL_TESTCASES = ['normal', 'registeredAp', 'serialBase']
    tag_map = {
        'zf2741': 'ShengZhen',
        'zf2925': 'Sunnyvale',
        'zf2942': 'Taipei',
        'zf7942': 'Ho Chi Minh',
    }
    #test_type_map = {
    #    'registeredAp': CONFIG_2,
    #    'normal': CONFIG_3,
    #    'priorityCheck': CONFIG_4,
    #}
    test_cfgs = {}
    for model in kwa['models']:
        # get config for this model
        model_cfg = model_cfg_map[model.lower()]
        # Because the CPU of AP 2925 is too weak, whenever we provion with a lot
        # of cfg especially Rate Limiting, it causes the CPU usare is very hight
        # in a long time (> 50 minute). Hence, we ignore very the Rate Limiting on
        # 2925 model
        if model.lower() == 'zf2925':
            model_cfg.setTestCfg(opt='wlan_det', items = dict(get_rate_limiting = False))
        cfg_map = define_ap_cfg(ap_cfg_obj=model_cfg)
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model.upper())
                tc[2]['model'] = tc[2]['model'] % model
                # NOTE: We have four configurations for each model. We don't use the
                # one of each model. Because it is complex config (change username and
                # password of device so it requires that we have to do some special things
                # for this test.
                # And we want each type of test will do auto config different configurations
                test_cfg = cfg_map[random.randint(0, len(cfg_map)-1)]
                if tc[2]['test_type'] == 'registeredAp': # in NORMAL_TESTCASES:
                    tc[2]['options'] = simple_cfg
                elif tc[2]['test_type'] == 'normal': # in NORMAL_TESTCASES:
                    tc[2]['options'] = test_cfg
                elif tc[2]['test_type'] == 'serialBase':
                    tc[2]['options'] = test_cfg
                elif tc[2]['test_type'] == 'priorityCheck':
                    # Beside the first config "options", this test requires extra config options
                    # for the second auto config rule
                    tc[2]['options'] = test_cfg
                    tc[2]['ex_options']= simple_cfg
                elif tc[2]['test_type'] == 'pre-Registration':
                    tc[2]['tag'] = tag_map[model]
                else:
                    print "Cannot find any config for the test case %s" % tc_id[i]
                    exit(1)

                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Auto Configuration Test', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['single_band']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)



