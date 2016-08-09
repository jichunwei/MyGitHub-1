import sys
import random

from libFM_TestSuite  import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import model_cfg_map


'''
NOTE: Phase 4 tc
- Currently, this test suite is just to do add config params for 1 tc 1.1.9.2.2
only.
- If have free time, move all things from addtestsuite_FM_CfgUpgrade to this script.
1.1.9.2.2    Create new task to ZF2741
1.1.9.2.4    Create configuration upgrade task with schedule for ZF2741
'''
def define_device_general_cfg(model='ZF2741', ks=[]):
    '''
    Define config template for wlan common
    '''
    ap_cfg_obj = model_cfg_map[model.lower()]

    return ap_cfg_obj.get_device_general_cfg_tmpl(ks)

def define_wlan_common_cfg(model='ZF2741', ks=[]):
    '''
    Define config template for wlan common
    '''
    ap_cfg_obj = model_cfg_map[model.lower()]

    return ap_cfg_obj.get_wlan_common_cfg_tmpl(ks)

def define_wep_cfg(
        model='ZF2741',
        wlan_rd_1=[2,4,6,8],
        encrypt_type=[
            'wep_open_5_ascii', 'wep_open_10_hex',
            'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
        ]
    ):
    '''
    This function is to return two WEP cfg.
   - wlan_rd_1: list of wlans to test for radio 1. Default is 4.
   - encrypt_type: list of wep encryption type to test for wlan_rd_1/wlan_rd_2
        NOTE for encrypt_type:
            xxx_5_ascii: its key idx is 1
            xxx_10_hex: its key idx is 2
            xxx_13_ascii: its key idx is 3
            xxx_26_hex: its key idx is 4
        Hence, be careful to select wep encryption to use for your cfg tmpl. It
        may cause unexpected error if its key is duplicated
    '''
    ap_cfg_obj = model_cfg_map[model.lower()]
    if model.upper() == 'ZF2925':
        ap_cfg_obj.setTestCfg(opt='wlan_det', items = dict(get_rate_limiting=False))

    # define cfg to test wep for radio 2.4GH
    idx, wep_rd_1_cfg = 0, {}
    for wlan in wlan_rd_1:
        if idx >= len(encrypt_type): idx = 0
        wep_rd_1_cfg.update(
            # get the first element of returned list
            ap_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type=encrypt_type[idx], dv_cfg=False
            )[0]
        )
        idx += 1

    return wep_rd_1_cfg

def define_wpa_cfg(
        model='ZF2741',
        wlan_rd_1=[1,2,3,4,5,6,7,8],
        encrypt_type=[
            'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
            'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
        ]
    ):
    '''
    This function is to return two WEP cfg.
   - wlan_rd_1: list of wlans to test for radio 1. Default is 4.
   - encrypt_type: list of wep encryption type to test for wlan_rd_1/wlan_rd_2
        NOTE for encrypt_type:
            xxx_5_ascii: its key idx is 1
            xxx_10_hex: its key idx is 2
            xxx_13_ascii: its key idx is 3
            xxx_26_hex: its key idx is 4
        Hence, be careful to select wep encryption to use for your cfg tmpl. It
        may cause unexpected error if its key is duplicated
    '''
    ap_cfg_obj = model_cfg_map[model.lower()]
    if model.upper() == 'ZF2925':
        ap_cfg_obj.setTestCfg(opt='wlan_det', items = dict(get_rate_limiting=False))

    # define cfg to test wep for radio 2.4GH
    idx, wpa_rd_1_cfg = 0, {}
    for wlan in wlan_rd_1:
        if idx >= len(encrypt_type): idx = 0
        wpa_rd_1_cfg.update(
            # get the first element of returned list
            ap_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type=encrypt_type[idx], dv_cfg=False
            )[0]
        )
        idx += 1

    return wpa_rd_1_cfg

def get_test_cfgs(models):
    '''
    This function is to get a list of test cfg template for each model. It will
    return following configs for earch model.
    - models: a list of models to get test data
    Return: Structure of returned data as below
    {
        'ZF7962': [
            #element 1: Config for Radio 2.4G
            {
                'cfg_name': 'Device Gerneral, Wlan Common, Encryption type on wlans...',
                'cfg': {
                    'device_general': {items: device_name for Device General},
                    'wlan_common': {
                        items: country_code, channel_1, channel_width_1 for Radio 1
                    },
                    'wlan_2': {
                        items: enable wireless, wep encryption type
                    },
                    'wlan_4': {
                        items: enable wireless, wep encryption type
                    },
                    'wlan_6': {
                        items: enable wireless, wep encryption type
                    },
                    'wlan_8': {
                        items: enable wireless, wep encryption type
                    },
                }
            },
            #element 2: Config 1 for Radio 2.4G
            {
                'cfg_name': 'Device Gerneral, Wlan Common, Encryption type on wlans...',
                'cfg': {
                    'wlan_1': {
                        items: enable wireless, wpa encryption type
                    },
                    'wlan_2': {
                        items: enable wireless, wpa encryption type
                    },
                    ...
                    'wlan_8': {
                        items: enable wireless, wpa encryption type
                    },
                }
            },
            #element 3: Config template 1 for Radio 5G
            {
                'cfg_name': 'Device Gerneral, Wlan Common, Encryption type on wlans...',
                'cfg': {
                    'device_general': {items: device_name for Device General},
                    'wlan_common': {
                        items: country_code, channel_2, channel_width_2 for Radio 2
                    },
                    'wlan_10': {
                        items: enable wireless, wep encryption type
                    },
                    'wlan_12': {
                        items: enable wireless, wep encryption type
                    },
                    'wlan_14': {
                        items: enable wireless, wep encryption type
                    },
                    'wlan_16': {
                        items: enable wireless, wep encryption type
                    },
                }
            },
            #element 4: Config template 2 for Radio 5G
            {
                'cfg_name': 'Device Gerneral, Wlan Common, Encryption type on wlans...',
                'cfg': {
                    'wlan_9': {
                        items: enable wireless, wpa encryption type
                    },
                    'wlan_10': {
                        items: enable wireless, wpa encryption type
                    },
                    ...
                    'wlan_16': {
                        items: enable wireless, wpa encryption type
                    },
                }
            }
    }
    '''
    test_cfg = {}
    # Define test config for each model
    for model in models:
        test_cfg[model.upper()] = []
        # get test config template for Device General
        test_cfg[model.upper()].append(dict(
            cfg_name = 'Device General',
            cfg = define_device_general_cfg(model)
        ))
        # get test config template for Wlan Common
        test_cfg[model.upper()].append(dict(
            cfg_name = 'Wlan Common',
            cfg = define_wlan_common_cfg(model)
        ))
        # get test config template for Wlan Detail WEP cfg
        wep_wlan = [2,4,6,8]
        wep_encrypt_type = [
            'wep_open_5_ascii', 'wep_open_10_hex',
            'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
        ]
        test_cfg[model.upper()].append(dict(
            cfg_name = 'Encryption type %s on wlans %s' % (wep_wlan, wep_encrypt_type),
            cfg = define_wep_cfg(model, wep_wlan, wep_encrypt_type)
        ))

        # get test config template for Wlan Detail WPA cfg
        wpa_wlan = [1,2,3,4,5,6,7,8]
        wpa_encrypt_type = [
            'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
            'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
        ]
        test_cfg[model.upper()].append(dict(
            cfg_name = 'encryption type %s on wlans %s' % (wpa_wlan, wpa_encrypt_type),
            cfg = define_wpa_cfg(model, wpa_wlan, wpa_encrypt_type)
        ))

        return test_cfg

def define_ts_cfg(**kwa):
    '''
    This function is to generate testsuites for following test cases:
    1.1.9.2.2    Create new task to ZF2741
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = ['01.02.03.13.01', '01.02.03.13.02']

    complex_cfg_tcs = []

    tc_templates = [
      # 1.1.9.2.2        Create a new configuration task to Group
      # 1.1.9.2.2        Create a new configuration task to Group - ZF2942
      # 1.1.9.2.4        Create a new configuration task to Group - ZF7942
      [ 'TCID:%s.%02d.%s - Create new task to - %s',
        'FM_CfgUpgrade_2',
        {
            'test_type': 'create',
            'test_name': 'Create config upgrade task for %s',
            'model': 'AP model',
            'provision_to': dict(
                device = 'ap ip', # or group = 'Group name'
            ),
            'input_cfg': {},
            'schedule': 0,
        },
      ],
      # 1.1.9.2.10       Select by device to be provisioned configuration
      [ 'TCID:%s.%s - Create configuration upgrade task with schedule - %s',
        'FM_CfgUpgrade_2',
        {
            'test_type': 'Create',
            'test_name': 'Create config upgrade task with schedule for %s',
            'model': 'AP model',
            'provision_to': dict(
                device = 'ap ip', # or group = 'Group name'
            ),
            'input_cfg': {},
            'schedule': 10,
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    print 'Generate testcases for model(s): %s' % ', '.join(kwa['models'])
    # get test cfgs for each all test models
    cfgs = get_test_cfgs(kwa['models'])
    test_cfgs = {}
    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                import copy
                # tcs which need to test a lot cases
                if tc_id[i] in multiple_cfg_tcs:
                    for j in range(len(cfgs[model.upper()])):
                        tc = copy.deepcopy(tc_templates[i])
                        # filling the template
                        tc[0] = tc[0] % (tc_id[i], (j+1), model_map[model], model.upper())
                        tc[2]['model'] = model.upper()
                        tc[2]['ap_ip'] = tc[2]['provision_to']['device'] = aps[model]
                        # List options
                        tc[2]['test_name'] = tc[2]['test_name'] % cfgs[model.upper()][j]['cfg_name']
                        tc[2]['input_cfg'] = cfgs[model.upper()][j]['cfg']
                        test_cfgs['%s.%02d.%s' % (tc_id[i], (j+1), model_map[model])] = tc
                else:
                    tc = copy.deepcopy(tc_templates[i])
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                    tc[2]['model'] = model.upper()
                    tc[2]['ap_ip'] = tc[2]['provision_to']['device'] = aps[model]
                    idx = random.randint(0, len(cfgs)-1)
                    tc[2]['test_name'] = tc[2]['test_name'] % cfgs[model.upper()][idx]['cfg_name']
                    tc[2]['input_cfg'] = cfgs[model.upper()][idx]['cfg']

                    test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Provisioning - Configuration Upgrade ZF2741', [test_cfgs[k] for k in keys]

def define_device_type():
    return ['zf2741']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    print '*'*80
    print 'NOTE: This test suite is just to support model ZF2741 only'
    print '*'*80
    make_test_suite(**_dict)

