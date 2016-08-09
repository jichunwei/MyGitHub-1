import sys
import copy
import random

from libFM_TestSuite import model_map, make_test_suite, select_ap_by_model, \
        get_aps_by_models,  get_testsuite
from RuckusAutoTest.common.lib_KwList import as_dict
from RuckusAutoTest.scripts.fm.libFM_DevCfg import ZF7962_Cfg


'''
3.6.1.1.2    The AP Country Code list via Device View should be consist with wireless radio 1 2.4GHz by standalone AP
3.6.1.2.2    The AP Channel List via Device View should be consist with standalone AP with wireless radio 1 2.4GHz.
3.6.1.4    Change the AP channel via Device View with wireless radio 1 2.4GHz mode.
3.6.1.6    Change the AP Country Code via Device View with wireless radio 1 2.4GHz mode
3.6.1.8    Change the AP channel band width to 20MHz via Device View with wireless radio 1 2.4GHz mode
3.6.1.10    Change the AP channel band width to 40MHz via Device View with wireless radio 1 2.4GHz mode.
3.6.1.12    Enable the Wireless Interface availability via Device View with wireless radio 1 2.4GHz mode
3.6.1.14    Enable the Wireless Broadcast SSID via Device View with wireless radio 1 2.4GHz mode
3.6.1.16    Change the Wireless encryption to WEP via Device View with wireless radio 1 2.4GHz mode
3.6.1.18    Change the Wireless encryption to WPA via Device View with wireless radio 1 2.4GHz mode

3.6.2.1.2    The AP Country Code list via Device View should be consist with wireless radio 2 for 5GHz  by standalone AP
3.6.2.2.2    The AP Channel List via Device View should be consist with standalone AP with wireless radio 2 for 5GHz.
3.6.2.4    Change the AP channel via Device View with radio mode for 5GHz only
3.6.2.6    Change the AP Country Code via Device View with wireless radio 2 for 5GHz.
3.6.2.8    Change the AP channel band width to 20MHz via Device View with wireless radio 2 for 5GHz
3.6.2.10    Change the AP channel band width to 40MHz via Device View with wireless radio 2 for 5GHz
3.6.2.12    Enable the Wireless Interface availability via Device View with wireless radio 2 5GHz mode
3.6.2.14    Enable the Wireless Broadcast SSID via Device View with wireless radio 2 5GHz mode
3.6.2.16    Change the Wireless encryption to WEP via Device View with wireless radio 2 5GHz mode
3.6.2.18    Change the Wireless encryption to WPA via Device View with wireless radio 2 5GHz mode
'''
# Be careful: If change value of these two contants, plz also change in the test
# script FM_Check_CountryCode_Channel_Match
COUNTRY_CODE = 'Country Code'
CHANNEL = 'Channel'


def define_wep_cfg(wlan_rd_1=[2,4,6,8], wlan_rd_2=[10,12,14,16],
        encrypt_type=[
            'wep_open_5_ascii', 'wep_open_10_hex',
            'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
        ]
    ):
    '''
    This function is to return two WEP cfg. One is for 2.4G, the
    other for 5G.
   - wlan_rd_1: list of wlans to test for radio 1. Default is 4.
   - wlan_rd_2: list of wlans to test for radio 2. Default is 4.
   - encrypt_type: list of wep encryption type to test for wlan_rd_1/wlan_rd_2
        NOTE for encrypt_type:
            xxx_5_ascii: its key idx is 1
            xxx_10_hex: its key idx is 2
            xxx_13_ascii: its key idx is 3
            xxx_26_hex: its key idx is 4
        Hence, be careful to select wep encryption to use for your cfg tmpl. It
        may cause unexpected error if its key is duplicated
    '''
    dal_cfg_obj = ZF7962_Cfg()
    # disable rate limiting, it is another story no need to verify it here.
    dal_cfg_obj.test_cfg['wlan_det']['get_rate_limiting'] = False
    # define cfg to test wep for radio 2.4GH
    idx, wep_rd_1_cfg = 0, {}
    for wlan in wlan_rd_1:
        if idx >= len(encrypt_type): idx = 0
        wep_rd_1_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type=encrypt_type[idx], dv_cfg=True
            )[0]
        )
        idx += 1
    # define cfg to test wep for radio 2.4GH
    idx, wep_rd_2_cfg = 0, {}
    for wlan in wlan_rd_2:
        if idx >= len(encrypt_type): idx = 0
        wep_rd_2_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type=encrypt_type[idx], dv_cfg=True
            )[0]
        )
        idx += 1

    return wep_rd_1_cfg, wep_rd_2_cfg

def define_wpa_cfg(
        wlan_rd_1=[1,2,3,4,5,6,7,8], wlan_rd_2=[9,10,11,12,11,12,13,14,15,16],
        encrypt_type=[
            'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
            'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
        ]
    ):
    '''
    This function is to return two WEP cfg. One is for 2.4G, the
    other for 5G.
   - wlan_rd_1: list of wlans to test for radio 1. Default is 4.
   - wlan_rd_2: list of wlans to test for radio 2. Default is 4.
   - encrypt_type: list of wep encryption type to test for wlan_rd_1/wlan_rd_2
        NOTE for encrypt_type:
            xxx_5_ascii: its key idx is 1
            xxx_10_hex: its key idx is 2
            xxx_13_ascii: its key idx is 3
            xxx_26_hex: its key idx is 4
        Hence, be careful to select wep encryption to use for your cfg tmpl. It
        may cause unexpected error if its key is duplicated
    '''
    dal_cfg_obj = ZF7962_Cfg()
    # disable rate limiting, it is another story no need to verify it here.
    dal_cfg_obj.test_cfg['wlan_det']['get_rate_limiting'] = False
    # define cfg to test wep for radio 2.4GH
    idx, wpa_rd_1_cfg = 0, {}
    for wlan in wlan_rd_1:
        if idx >= len(encrypt_type): idx = 0
        wpa_rd_1_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type=encrypt_type[idx], dv_cfg=True
            )[0]
        )
        idx += 1

    # define cfg to test wep for radio 2.4GH
    idx, wpa_rd_2_cfg = 0, {}
    for wlan in wlan_rd_2:
        if idx >= len(encrypt_type): idx = 0
        wpa_rd_2_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type=encrypt_type[idx], dv_cfg=True
            )[0]
        )
        idx += 1

    return wpa_rd_1_cfg, wpa_rd_2_cfg

def define_broadcast_cfg(wlan_rd_1=[1,3,5,7], wlan_rd_2=[9,11,13,15]):
    '''
    This function is to return two enable broadcast cfg. One is for 2.4G, the
    other for 5G.
    '''
    dal_cfg_obj = ZF7962_Cfg()
    # disable rate limiting, it is another story no need to verify it here.
    dal_cfg_obj.test_cfg['wlan_det']['get_rate_limiting'] = False
    # define cfg to test enable broadcast ssid for radio 2.4GH
    broadcast_ssid_rd_1_cfg = {}
    for wlan in wlan_rd_1:
        broadcast_ssid_rd_1_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type='open', dv_cfg=True
            )[0]
        )

    # define cfg to test enable broadcast ssid for radio 5GH
    broadcast_ssid_rd_2_cfg = {}
    for wlan in wlan_rd_2:
        broadcast_ssid_rd_2_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(
                wlan_list=[wlan], encrypt_type='open', dv_cfg=True
            )[0]
        )

    return broadcast_ssid_rd_1_cfg, broadcast_ssid_rd_2_cfg


def define_ts_cfg(**kwa):
    '''
    kwa:
   - models: a list of model, something likes ['zf2925', 'zf7942']
    @TODO: Will restructure this function by new way to define ts later
    '''
    # put a 'None' value for the test which this model don't have
    tc_id = [
            # 2.4G
            '03.06.01.01.02', '03.06.01.02.02',
            '03.06.01.04', '03.06.01.06', '03.06.01.08', '03.06.01.10',
            '03.06.01.12', '03.06.01.14', '03.06.01.16', '03.06.01.18',

            # 5G
            '03.06.02.01.02', '03.06.02.02.02',
            '03.06.02.04', '03.06.02.06', '03.06.02.08', '03.06.02.10',
            '03.06.02.12', '03.06.02.14', '03.06.02.16', '03.06.02.18',
            ]

    sample_channel_1 = ['0','1','2','3','6','7','8','10','11']
    sample_channel_2 = ['0','36','40','44','48',]
    sample_country_code = ['AT', 'CA', 'FR', 'ID', 'JP', 'TW', 'CH', 'SE', 'GB', 'US',]

    dal_cfg = ZF7962_Cfg()

    idx = random.randint(0, len(sample_channel_1)-1)
    channel_1 = sample_channel_1[idx]
    pre_channel_1 = sample_channel_1[idx-1] # channel for pre-config

    idx = random.randint(0, len(sample_channel_2)-1)
    channel_2 = sample_channel_2[idx]
    pre_channel_2 = sample_channel_2[idx-1]

    idx = random.randint(0, len(sample_country_code)-1)
    country_code = sample_country_code[idx]
    pre_country_code = sample_country_code[idx-1]

    channel_width_no_1 = '20' # should rename it to more meaningful name
    channel_width_no_2 = '40'

    broadcast_wlan_rd_1, broadcast_wlan_rd_2 = [1,3,5,7],[9,11,13,15]
    broadcast_ssid_rd_1_cfg, broadcast_ssid_rd_2_cfg = define_broadcast_cfg(broadcast_wlan_rd_1, broadcast_wlan_rd_2)

    wep_wlan_rd_1, wep_wlan_rd_2 = [2,4,6,8], [10,12,14,16]
    wep_encrypt_type = [
        'wep_open_5_ascii', 'wep_open_10_hex',
        'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
    ]
    wep_rd_1_cfg, wep_rd_2_cfg = define_wep_cfg(wep_wlan_rd_1, wep_wlan_rd_2, wep_encrypt_type)

    wpa_wlan_rd_1, wpa_wlan_rd_2 = [1,2,3,4,5,6,7,8], [9,10,11,12,11,12,13,14,15,16]
    wpa_encrypt_type = [
        'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
        'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
    ]
    wpa_rd_1_cfg, wpa_rd_2_cfg = define_wpa_cfg(wpa_wlan_rd_1, wpa_wlan_rd_2, wpa_encrypt_type)

    # get config to test 03.06.01.11 and 03.06.02.11 get_wlan_det_cfg_tmpl
    tc_templates = [
      #2.4G tcs
      [ 'TCID:%s.%s - Check consistency Country Code list between Device View and '
        ' standalone AP for 2.4GHz - %s',
        'FMDV_Check_CountryCode_Channel_Match',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'verify_item': COUNTRY_CODE,
            'test_name': 'Check consistency Country Code list between Device View '
                         'and standalone AP for 2.4GHz',#'Name of template'
        },
      ],
      [ 'TCID:%s.%s - Check consistency Channel list between Device View and '
        ' standalone AP for 2.4GHz - %s',
        'FMDV_Check_CountryCode_Channel_Match',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'verify_item': CHANNEL,
            'test_name': 'Check consistency Channel list between Device View '
                         'and standalone AP for 2.4GHz',#'Name of template'
        },
      ],
      [ 'TCID:%s.%s - Change the AP channel via Device View for 2.4GHz mode - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Change channel of 2.4G to "%s" via Device View' % channel_1,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_1=channel_1)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_1=pre_channel_1)
            ),
        },
      ],
      [ 'TCID:%s.%s - Change the AP Country Code via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Change country code of 2.4G to "%s" via Device View' % country_code,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(country_code=country_code)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(country_code=pre_country_code)
            ),
        },
      ],
      [ 'TCID:%s.%s - Change the AP channel band width to 20MHz via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Change channel width of 2.4G to "%s" via Device View' % channel_width_no_1,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_1=channel_width_no_1)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_1=channel_width_no_2)
            ),
        },
      ],
      [ 'TCID:%s.%s - Change the AP channel band width to 40MHz via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Change channel width of 2.4G to "%s" via Device View' % channel_width_no_2,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_1=channel_width_no_2)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_1=channel_width_no_1)
            ),
        },
      ],
      [ 'TCID:%s.%s - Enable the Wireless Interface availability via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Enable the Wireless Interface availability on wlans %s '
                         'via Device View' % broadcast_wlan_rd_1,
            'input_cfg': broadcast_ssid_rd_1_cfg,
        },
      ],
      [ 'TCID:%s.%s - Enable the Wireless Broadcast SSID via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Enable the Wireless Broadcast SSID on wlans %s via '
                         'Device View' % broadcast_wlan_rd_1,
            'input_cfg': broadcast_ssid_rd_1_cfg,
        },
      ],
      [ 'TCID:%s.%s - Change the Wireless encryption to WEP via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Enable encryption type %s on wlans %s via Device View' %\
                         (wep_encrypt_type, wep_wlan_rd_1),
            'input_cfg': wep_rd_1_cfg,
        },
      ],
      [ 'TCID:%s.%s - Change the Wireless encryption to WPA via Device View for 2.4GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '2.4G',
            'ap_ip': '',
            'test_name': 'Enable encryption type %s on wlans %s via Device View' %\
                         (wpa_encrypt_type, wpa_wlan_rd_1),
            'input_cfg': wpa_rd_1_cfg,
        },
      ],


      # 5G tcs
      [ 'TCID:%s.%s - Check consistency Country Code list between Device View and '
        'standalone AP for 5GHz - %s',
        'FMDV_Check_CountryCode_Channel_Match',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'verify_item': COUNTRY_CODE,
            'test_name': 'Check consistency Country Code list between Device View '
                         'and standalone AP for 5GHz',#'Name of template'
        },
      ],
      [ 'TCID:%s.%s - Check consistency Channel list between Device View and '
        'standalone AP for 5GHz - %s',
        'FMDV_Check_CountryCode_Channel_Match',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'verify_item': CHANNEL,
            'test_name': 'Check consistency Channel list between Device View '
                         'and standalone AP for 5GHz',#'Name of template'
        },
      ],
      [ 'TCID:%s.%s - Change the AP channel via Device View for 5GHz mode - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Change to channel of 5G to "%s" via Device View' % channel_2,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_2=channel_2)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_2=pre_channel_2)
            ),
        },
      ],
      [ 'TCID:%s.%s - Change the AP Country Code via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Change country code of 5G to "%s" via Device View' % country_code,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(country_code=country_code)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(country_code=pre_country_code)
            ),
        },
      ],
      [ 'TCID:%s.%s - Change the AP channel width to 20MHz via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Change channel width of 5G to "%s" via Device View' % channel_width_no_1,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_2=channel_width_no_1)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_2=channel_width_no_2)
            ),
        },
      ],
      [ 'TCID:%s.%s - Change the AP channel width to 40MHz via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Change channel width of 5G to "%s" via Device View' % channel_width_no_2,
            'input_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_2=channel_width_no_2)
            ),
            'pre_cfg': dal_cfg.get_wlan_common_cfg_tmpl(
                keys = dict(channel_width_2=channel_width_no_1)
            ),
        },
      ],
      [ 'TCID:%s.%s - Enable the Wireless Interface availability via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Enable the Wireless Interface availability on wlans %s '
                         'via config template' % broadcast_wlan_rd_2,
            'input_cfg': broadcast_ssid_rd_2_cfg,
        },
      ],
      [ 'TCID:%s.%s - Enable the Wireless Broadcast SSID via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Enable the Wireless Broadcast SSID on wlans %s via '
                         'Device View' % broadcast_wlan_rd_2,
            'input_cfg': broadcast_ssid_rd_2_cfg,
        },
      ],
      [ 'TCID:%s.%s - Change the Wireless encryption to WEP via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Enable encryption type %s on wlans %s via Device View' %\
                         (wep_encrypt_type, wep_wlan_rd_2),
            'input_cfg': wep_rd_2_cfg,
        },
      ],
      [ 'TCID:%s.%s - Change the Wireless encryption to WPA via Device View for 5GHz - %s',
        'FMDV_Dalmatian_CfgUpgrade',
        {
            'model': 'ZF7962',
            'radio_mode': '5G',
            'ap_ip': '',
            'test_name': 'Enable encryption type %s on wlans %s via Device View' %\
                         (wpa_encrypt_type, wpa_wlan_rd_2),
            'input_cfg': wpa_rd_2_cfg,
        },
      ],
    ]
    tbCfg = eval(kwa['testbed'].config)
    aps = select_ap_by_model(get_aps_by_models(kwa['models'], tbCfg),kwa['is_interactive'])

    print 'Generate testcases for model(s)/ZD(s): %s' \
          % (', '.join(['%s (%s)' % (m, aps[m]) for m in kwa['models']]))
    test_cfgs = {}

    for model in kwa['models']:
        for i in range(len(tc_id)):
            if tc_id[i]: # not None
                #for j in range(len(tc_templates)):
                tc = copy.deepcopy(tc_templates[i])
                # filling the template
                tc[0] = tc[0] % (tc_id[i], model_map[model], model.upper())
                if 'ap_ip' in tc[2]: tc[2]['ap_ip'] = aps[model]
                test_cfgs['%s.%s' % (tc_id[i], model_map[model])] = tc

    # sort the dict and return as a list
    keys = test_cfgs.keys()
    keys.sort()
    return 'Device View - Dalmatian Config', [test_cfgs[k] for k in keys]


def define_device_type():
    return ['dual_band']

if __name__ == '__main__':
    _dict = dict(
                 define_ts_cfg = define_ts_cfg,
                 define_device_type = define_device_type,
                 )
    _dict.update(as_dict( sys.argv[1:] ))
    make_test_suite(**_dict)


