'''
Device View

5    ZF2925 8.0 wireless Authentication
5.1    Open System
5.2.1    Open-WEP-64-5 ascii
5.2.2    Open-WEP-64-10 hex
5.3.1    Open-WEP-128-13 ascii
5.3.2    Open-WEP-128-26 hex
5.4    Shared-WEP-64
5.5    Shared-WEP-128
5.6    WPA-PSK-TKIP
5.7    WPA-PSK-AES
5.8    WPA2-PSK-TKIP
5.9    WPA2-PSK-AES
5.10    WPA-TKIP
5.11    WPA-AES
5.12    WPA2-TKIP
5.13    WPA2-AES

'''

import sys
import copy

from libFM_TestSuite import model_map, make_test_suite, \
        select_ap_by_model, get_aps_by_models, select_client,\
        input_with_default
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import ZF2925_Cfg, ZF7942_Cfg, ZF2942_Cfg, \
        RAS_USERNAME, RAS_PASSWORD, RAS_ADDR, RAS_NAS_ID, RAS_PORT, RAS_SECRET, \
        define_wlan_det_cfg
from RuckusAutoTest.scripts.fm.libFM_DevCfg import model_cfg_map



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
            '05.01', '05.02.01', '05.02.02', '05.03.01', '05.03.02', '05.04.01', '05.04.02',
            '05.05.02', '05.05.02', '05.06', '05.07', '05.08', '05.09', '05.10', '05.11',
            '05.12', '05.13',
            ]

    '''
5.1    Open System
5.2.1    Open-WEP-64-5-ascii
5.2.2    Open-WEP-64-10-hex
5.3.1    Open-WEP-128-13-ascii
5.3.2    Open-WEP-128-26-hex
5.4.1    Shared-WEP-64-5-ascii
5.4.2    Shared-WEP-64-10-hex
5.5.1    Shared-WEP-128-ascii
5.5.2    Shared-WEP-128-hex
5.6    WPA-PSK-TKIP
5.7    WPA-PSK-AES
5.8    WPA2-PSK-TKIP
5.9    WPA2-PSK-AES
5.10    WPA-TKIP
5.11    WPA-AES
5.12    WPA2-TKIP
5.13    WPA2-AES
        wep_open_5_ascii            wpa_tkip_psk
        wep_open_10_hex             wpa_tkip_auto
        wep_open_13_ascii           wpa_tkip_802.1x
        wep_open_26_hex
                                    wpa_aes_psk
        wep_sharedkey_5_ascii       wpa_aes_auto
        wep_sharedkey_10_hex        wpa_aes_802.1x
        wep_sharedkey_13_ascii
        wep_sharedkey_26_hex        wpa_auto_psk
            wpa_auto_auto
        wep_auto_5_ascii            wpa_auto_802.1x
        wep_auto_10_hex
        wep_auto_13_ascii           wpa2_tkip_psk
        wep_auto_26_hex             wpa2_tkip_auto
                                    wpa2_tkip_802.1x

                                    wpa2_aes_psk
                                    wpa2_aes_auto
                                    wpa2_aes_802.1x

                                    wpa2_auto_psk
                                    wpa2_auto_auto
                                    wpa2_auto_802.1x

                                    auto_tkip_psk
                                    auto_tkip_auto
                                    auto_tkip_802.1x

                                    auto_aes_psk
                                    auto_aes_auto
                                    auto_aes_802.1x

                                    auto_auto_psk
                                    auto_auto_auto
                                    auto_auto_802.1x


    '''
    #[id_cfg, tc name]
    # the id_cfg is the key to get cfg from define_wlan_det_cfg function
    tc_params = {
        '05.01': ['open',                       'Open System'],
        '05.02.01': ['wep_open_5_ascii',        'Open-WEP-64-5 ascii'],
        '05.02.02': ['wep_open_10_hex',         'Open-WEP-64-10 hex'],
        '05.03.01': ['wep_open_13_ascii',       'Open-WEP-128-13 ascii'],
        '05.03.02': ['wep_open_26_hex',         'Open-WEP-128-26 hex'],
        '05.04.01': ['wep_sharedkey_5_ascii',   'Shared-WEP-64-5-ascii'],
        '05.04.02': ['wep_sharedkey_10_hex',    'Shared-WEP-64-10-hex'],
        '05.05.01': ['wep_auto_13_ascii',       'Shared-WEP-128-ascii'],
        '05.05.02': ['wep_auto_26_hex',         'Shared-WEP-128-hex'],
        '05.06': ['wpa_tkip_psk',               'WPA-PSK-TKIP'],
        '05.07': ['wpa_aes_psk',                'WPA-PSK-AES'],
        '05.08': ['wpa2_tkip_psk',              'WPA2-PSK-TKIP'],
        '05.09': ['wpa2_aes_psk',               'WPA2-PSK-AES'],
        '05.10': ['wpa_tkip_802.1x',            'WPA-TKIP-802.1X'],
        '05.11': ['wpa_aes_802.1x',             'WPA-AES-802.1X'],
        '05.12': ['wpa2_tkip_802.1x',           'WPA2-TKIP-802.1X'],
        '05.13': ['wpa2_aes_802.1x',            'WPA2-AES-802.1X'],
    }
    print "PLEASE ENTER REQUIRED INFORMATION FOR 802.1X AUTHEN"
    if(kwa['is_interactive']):
        ras_ip = input_with_default('Please enter Radius server IP', RAS_ADDR)
        ras_nas_id = input_with_default('Please enter Radius NAS-ID', RAS_NAS_ID)
        ras_port = input_with_default('Please enter Radius port', RAS_PORT)
        ras_secret = input_with_default('Please enter Radius secret', RAS_SECRET)
    else:
        ras_ip = RAS_ADDR
        ras_nas_id = RAS_NAS_ID
        ras_port = RAS_PORT
        ras_secret = RAS_SECRET

    ras_cfg = {
        'radius_nas_id': ras_nas_id,#'Radius NAS-ID',
        'auth_ip': ras_ip,#'Authentication IP address',
        'auth_port': ras_port,#'Authentication Port',
        'auth_secret': RAS_SECRET,#'Authentication Server Secret',
    }

    tc_templates = [
      [ 'TCID:%s.%s - Wireless Authentication: "%s" - %s',
        'FMDV_WlanManager',
        {
            'ap_ip'    : '192.168.20.171',
            'client_ip': '192.168.1.11',
            'test_name': '',
            'cfg'      : '',
            'rad_cfg'  : {
                'username': input_with_default('Please enter Radius user ', RAS_USERNAME) \
                            if kwa['is_interactive'] else RAS_USERNAME ,
                'password': input_with_default('Please enter pass for this user', RAS_PASSWORD)\
                            if kwa['is_interactive'] else RAS_PASSWORD,
            },
        },
      ],
    ]

    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])
    client_ip = select_client(tbCfg, kwa['is_interactive'])

    print 'Generate testcases for model(s)/AP(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}
    for model in kwa['models']:
        wlan = 0
        ap_cfg_obj = model_cfg_map[model.lower()]
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                tc = copy.deepcopy(tc_templates[0])
                cfg_id, tc_name = tc_params[tc_id[i]][0], tc_params[tc_id[i]][1]
                # print 'cfg_id: %s' % cfg_id
                wlan = wlan+1 if wlan < 8 else 1
                ap_cfg_obj.setTestCfg(opt='wlan_det', items={'encrypt_type': cfg_id})

                test_cfg = {
                    'dv_cfg': True,
                    'wlan_list': [wlan], # default
                    'ap_cfg_obj': ap_cfg_obj,
                    #'encrypt_type': cfg_id,
                }
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], tc_name, model.upper())
                tc[2]['ap_ip'] = aps[model]
                tc[2]['client_ip'] = client_ip
                tc[2]['test_name'] = tc_name,
                # get test cfg: define_wlan_det_cfg return a list of cfgs. In this case,
                # its result has only one elemnet with key 'wlan_%d', so we only need
                # access its first element and get the key ["wlan_%s" % wlan]
                tc[2]['cfg'] = define_wlan_det_cfg(**test_cfg)[0]['wlan_%s' % wlan]
                # If authen type is 802.1x, re-update its authen info from user's input
                # Actually, this is just work around for this test suite. The change should
                # be implemented in libFM_DevCfg.
                if '802.1x' in cfg_id:
                    tc[2]['cfg'].update(ras_cfg)
                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View Status - Wireless Authentication', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['single_band']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)

