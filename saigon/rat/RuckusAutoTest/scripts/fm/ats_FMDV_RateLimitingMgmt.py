'''
Device View

5    ZF2925 8.0 wireless Authentication
3.1.10    Modify the Rate limiting in Device View
'''

import sys
import copy
import random

from libFM_TestSuite import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models, input_with_default, select_client
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import ZF2925_Cfg, ZF7942_Cfg, ZF2942_Cfg, \
        RAS_USERNAME, RAS_PASSWORD, define_rate_limiting_cfg, define_wlan_det_cfg


def _getRandomListOfUniqeInt(no, max):
    '''
    This function is to get a list of random number. "no" is its
    element; each element is unique and less than "max".
    Output:
    - A list looks like:
        [1, 0, 2, 3, ...]
    '''
    list_num = []
    for i in range(no):
        unique = False
        while not unique:
            new_num = random.randint(0, max - 1)
            if not new_num in list_num:
                unique = True
        list_num.append(new_num)

    return list_num

def define_ts_cfg(**kwa):
    '''
    kwa:
    - models: a list of model, something likes ['zf2925', 'zf7942']
    - testbed:
    return:
    - (testsuite name, testcase configs)
    Note: Some notes for this function.
          The idea is that we try to test rate limiting with different
          authentications. We have tolal 17 type of auths and have to verify rate
          limiting on 8 wlans. We will radomly get 8 type of auths for each wlan
          and verify Rate Limiting of these wlans.
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = [
            '03.05.10',
            ]

    #[id_cfg, tc name]
    # the id_cfg is the key to get cfg from define_wlan_det_cfg function
    tc_params = [
        ['open',                    'Open System'],
        ['wep_open_5_ascii',        'Open-WEP-64-5 ascii'],
        ['wep_open_10_hex',         'Open-WEP-64-10 hex'],
        ['wep_open_13_ascii',       'Open-WEP-128-13 ascii'],
        ['wep_open_26_hex',         'Open-WEP-128-26 hex'],
        ['wep_sharedkey_5_ascii',   'Shared-WEP-64-5-ascii'],
        ['wep_sharedkey_10_hex',    'Shared-WEP-64-10-hex'],
        ['wep_auto_13_ascii',       'Shared-WEP-128-ascii'],
        ['wep_auto_26_hex',         'Shared-WEP-128-hex'],
        ['wpa_tkip_psk',            'WPA-PSK-TKIP'],
        ['wpa_aes_psk',             'WPA-PSK-AES'],
        ['wpa2_tkip_psk',           'WPA2-PSK-TKIP'],
        ['wpa2_aes_psk',            'WPA2-PSK-AES'],
        ['wpa_tkip_802.1x',         'WPA-TKIP'],
        ['wpa_aes_802.1x',          'WPA-AES'],
        ['wpa2_tkip_802.1x',        'WPA2-TKIP'],
        ['wpa2_aes_802.1x',         'WPA2-AES'],
    ]
    tc_templates = [
      [ 'TCID:%s.%s.%02d - Modify the Rate limiting in Device View with "%s" - %s',
        'FMDV_RateLimitingMgmt',
        {
            'ap_ip'    : '192.168.20.171',
            'client_ip': '192.168.1.11',
            'traffic_srv_ip': '192.168.30.252',
            'test_name': 'Rate Limiting cfg: %s with authentication: %s',
            'wlan_cfg' : {},
            'rl_cfg'   : {},
            'rad_cfg'  : {
                'username': RAS_USERNAME,
                'password': RAS_PASSWORD,
            },
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])
    client_ip = select_client(tbCfg,kwa['is_interactive'])
    if(kwa['is_interactive']):
        traffic_srv_ip = input_with_default('Please enter a traffic server ip: ', '192.168.30.252')
    else:
        traffic_srv_ip = tbCfg['FM']['ip_addr']

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))

    test_cfgs = {}
    ENCRYPT_KEY, ENCRYPT_NAME = 0, 1
    for model in kwa['models']:
        #wlan = 0
        ap_cfg_obj = {
            'zf2925': ZF2925_Cfg(),
            'zf2942': ZF2942_Cfg(),
            'zf7942': ZF7942_Cfg(),
        }[model.lower()]
        # Different models may have different no of wlans
        no_wlan = {
            'zf2925': 8,
            'zf2942': 8,
            'zf7942': 8,
        }[model.lower()]
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                # get a random list (no_wlan) of encryption type index in tc_params
                list_encrypt_idx = _getRandomListOfUniqeInt(no_wlan, len(tc_params))
                # get a list (no_wlan) of rate limiting config
                list_ratelimiting_cfg = define_rate_limiting_cfg(dv_cfg=True, no_cfg=no_wlan)

                for j in range(no_wlan):
                    # get index of encryption for wlan "j"
                    encrypt_idx = list_encrypt_idx[j]
                    tc = copy.deepcopy(tc_templates[0])
                    #cfg_id  = tc_params[tc_id[i]][ENCRYPT_KEY]
                    encrypt_type = tc_params[encrypt_idx][ENCRYPT_KEY]
                    ap_cfg_obj.setTestCfg(opt='wlan_det', items={'encrypt_type': encrypt_type})

                    test_cfg = {
                        'dv_cfg': True,
                        'wlan_list': [j + 1],
                        'ap_cfg_obj': ap_cfg_obj,
                    }
                    # filling the template
                    tc[0] = tc[0] % (tc_id[i], model_map[model], j + 1,
                                     list_ratelimiting_cfg[j], model.upper())
                    tc[2]['ap_ip'] = aps[model]
                    tc[2]['client_ip'] = client_ip
                    tc[2]['traffic_srv_ip'] = traffic_srv_ip
                    tc[2]['test_name'] = (tc[2]['test_name'] %
                                         (list_ratelimiting_cfg[j], tc_params[encrypt_idx][ENCRYPT_NAME]))
                    # get test cfg: define_wlan_det_cfg return a list of cfgs. In this case,
                    # its result has only one elemnet with key 'wlan_%d', so we only need
                    # access its first element and get the key ["wlan_%s" % wlan]
                    tc[2]['wlan_cfg'] = define_wlan_det_cfg(**test_cfg)[0]['wlan_%s' % (j + 1)]
                    tc[2]['rl_cfg'] = list_ratelimiting_cfg[j]

                    test_cfgs['%s.%s.%02d' % (tc_id[i], model_map[model], j+1)] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View Status - Rate Limiting Mgmt', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['all_ap_models']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)
