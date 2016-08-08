import sys
import copy
import re
from random import randint

from libFM_TestSuite  import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import model_cfg_map2


'''
@ TODO: Will change this file to use a new solution of adding testsuite
1.1.9.2.1        Create a new configuration task to Group - ZF295
1.1.9.2.2        Create a new configuration task to Group - ZF2942
1.1.9.2.4        Create a new configuration task to Group - ZF7942

1.1.9.2.10       Select by device to be provisioned configuration
1.1.9.2.11.01    By schedule provisioning configuration task to APs (By Group)
1.1.9.2.11.02    By schedule provisioning configuration task to APs (By Device)
1.1.9.2.12       Cancel provisioning task
1.1.9.2.13       Upgrade status and result
1.1.9.2.14       Update Audit log report
1.1.9.2.15       Configuration Upgrade: Failed task could be restart
'''

def get_restore_cfg(cfg_obj, cfg_keys):
    '''
    . cfg_obj: config object.
    . cfg_keys: a list of keys: device_general, wlan_common, wlan_1, wlan_2,...
    .
    '''
    ori_cfgs = {}
    for k in cfg_keys:
        no = re.search('[0-9]+', k)
        if no:
             get_fn = cfg_obj.get_original_wlan_cfg
             params = dict(wlan_num=no.group(0), is_dv_cfg=False)
        else:
            get_fn, params = dict(
                device_general = (cfg_obj.get_original_device_general_cfg, dict(is_dv_cfg=False)),
                wlan_common = (cfg_obj.get_original_wlan_common_cfg, dict(is_dv_cfg=False)),
            )[k]

        pprint(params)
        ori_cfgs.update(get_fn(**params))

    return ori_cfgs


def define_ts_cfg(**kwa):
    '''
    This function is to generate testsuites for following test cases:
    1.1.9.2.1        Create a new configuration task to Group

    1.1.9.2.10       Select by device to be provisioned configuration
    1.1.9.2.11.01    By schedule provisioning configuration task to APs (By Group)
    1.1.9.2.11.02    By schedule provisioning configuration task to APs (By Device)

    And some tcs just requires simiple config to do test
    1.1.9.2.12       Cancel provisioning task
    1.1.9.2.13       Upgrade status and result
    1.1.9.2.14       Update Audit log report
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    '''
    # put a 'None' value for the test which this model don't have

    tc_id = [
            '01.01.09.02.01', '01.01.09.02.10', '01.01.09.02.11.01',
            '01.01.09.02.11.02',
            '01.01.09.02.12', '01.01.09.02.13', '01.01.09.02.14',
            '01.01.09.02.15',
            ]
    # tcs which have to test only one complex config
    complex_cfg_tcs = [
        '01.01.09.02.01', '01.01.09.02.11.01', '01.01.09.02.11.02',
    ]
    # tcs which only need simple config to test
    simple_cfg_tcs = [
        '01.01.09.02.12', '01.01.09.02.13', '01.01.09.02.14'
    ]
    # tc which need to test with a lot of different complex input cfgs
    multiple_cfg_tcs = [
        '01.01.09.02.10'
    ]
    new_tcs = [
        '01.01.09.02.15'
    ]
    # Define a simple config to test these tcs
    simple_cfg = {
        'device_general': {'device_name': 'RuckusAPTest'}
    }

    tc_templates = [
      # 1.1.9.2.1        Create a new configuration task to Group
      # 1.1.9.2.2        Create a new configuration task to Group - ZF2942
      # 1.1.9.2.4        Create a new configuration task to Group - ZF7942
      [ 'TCID:%s.%s - Create a config task to Group - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'normal',
            'model': 'AP model',
            'device_select_by': 'group',
            'options': {},
            'schedule': 0,
        },
      ],
      # 1.1.9.2.10       Select by device to be provisioned configuration
      [ 'TCID:%s.%02d.%s - Provision config (By Device). Config: %s - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'normal',
            'model': 'AP model',
            'device_select_by': 'device',
            'options': {},
            'schedule': 0,
        },
      ],
      # 1.1.9.2.11.01    By schedule provisioning configuration task to APs (By Group)
      [ 'TCID:%s.%s - Schedule to provision config (By Group) - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'normal',
            'model': 'AP model',
            'device_select_by': 'group',
            'options': {},
            'schedule': 13,
        },
      ],
      # 1.1.9.2.11.02    By schedule provisioning configuration task to APs (By Device)
      [ 'TCID:%s.%s - Schedule to provision config (By Device) - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'normal',
            'model': 'AP model',
            'device_select_by': 'device',
            'options': {},
            'schedule': 13,
        },
      ],
      ##############Following test cases just require simple config to do the test
       # 1.1.9.2.12       Cancel provisioning task
      [ 'TCID:%s.%s - Cancel provisioning task - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'cancel',
            'model': 'AP model',
            'device_select_by': 'device',
            'options': {},
            'schedule': 20,
        },
      ],
      # 1.1.9.2.13       Upgrade status and result
      [ 'TCID:%s.%s - Upgrade task status and result - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'status',
            'model': 'AP model',
            'device_select_by': 'device',
            'options': {},
            'schedule': 0,
        },
      ],
      # 1.1.9.2.14       Update Audit log report
      [ 'TCID:%s.%s - Update Audit log report - %s',
        'FM_CfgUpgrade',
        {
            'test_type': 'update_log',
            'model': '%s',
            'device_select_by': 'device',
            'options': {},
            'schedule': 20,
        },
      ],
      # 1.1.9.2.15    Configuration Upgrade: Failed task could be restarted
      [ 'TCID:%s.%s - Restart failed task - %s',
        'FM_CfgUpgrade_2',
        dict(
            ap_ip = 'ap ip',
            model = 'AP model',
            input_cfg = {},
            test_type = 'restart',
            schedule = 0, # O to perform now, > 0 to perform later,
            provision_to = dict(
                device = 'ap ip', # or group = 'Group name'
            ),
        ),
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    test_cfgs = {}
    for model in kwa['models']:
        # get config for this model
        ap_cfgs =[]
        ap_cfg_obj = model_cfg_map2[model.lower()]
        ap_cfgs.append(ap_cfg_obj.get_device_general_cfg(is_dv_cfg=False))
        ap_cfgs.append(ap_cfg_obj.get_wlan_common_cfg(is_dv_cfg=False))
        ap_cfgs.extend(ap_cfg_obj.get_wlan_cfgs(is_dv_cfg=False))

        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                # tcs which need to test a lot cases
                if tc_id[i] in multiple_cfg_tcs:
                    for idx, cfg in enumerate(ap_cfgs):
                        tc = copy.deepcopy(tc_templates[i])
                        # filling the template
                        tc[0] = tc[0] % (
                            tc_id[i], (idx+1), model_map[model],
                            cfg['name'], model.upper()
                        )
                        tc[2]['model'] = model.upper()
                        # List options
                        tc[2]['options'].update(cfg['cfg'])
                        tc[2]['restore_cfg'] = ap_cfg_obj.get_original_cfgs(
                                                   cfg['cfg'].keys(), False
                                               )
                        test_cfgs['%s.%02d.%s' % (
                            tc_id[i], (idx+1), model_map[model])
                        ] = tc
                else:
                    tc = copy.deepcopy(tc_templates[i])
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                    tc[2]['model'] = model.upper()
                    if tc_id[i] in complex_cfg_tcs:
                        tc[2]['options']= ap_cfgs[randint(0, len(ap_cfgs)-1)]['cfg']
                        tc[2]['restore_cfg'] = ap_cfg_obj.get_original_cfgs(
                                                    tc[2]['options'].keys(), False
                                               )
                    elif tc_id[i] in simple_cfg_tcs:
                        tc[2]['options'] = simple_cfg
                        tc[2]['restore_cfg'] = ap_cfg_obj.get_original_cfgs(
                                                    simple_cfg.keys(), False
                                               )
                    elif tc_id[i] in new_tcs:
                        tc[2]['ap_ip'] = tc[2]['provision_to']['device'] = aps[model]
                        tc[2]['input_cfg'] = ap_cfgs[randint(0, len(ap_cfgs)-1)]['cfg']
                        tc[2]['restore_cfg'] = ap_cfg_obj.get_original_cfgs(
                                                    tc[2]['input_cfg'].keys(), False
                                               )
                    else:
                        print "Cannot find any config fo the test case %s" % tc_id[i]
                        exit(1)

                    test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Configuration Upgrade', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

