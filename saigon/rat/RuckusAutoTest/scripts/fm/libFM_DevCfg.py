import random, re, copy

# Default values for authentication
RAS_USERNAME = 'user.eap'
RAS_PASSWORD = '123456'
RAS_NAS_ID = '112'
RAS_ADDR = '192.168.30.252'
RAS_PORT = '1812'
RAS_SECRET = '123456'

ACC_NAS_ID = '113'
ACC_ADDR = '192.168.30.252'
ACC_PORT = '1813'
ACC_SECRET = '123456'


'''
NOTES:
. Don't test the country code now
'''
class AP_Cfg:
    '''OBSOLETE. Plz use Ap_Cfg2'''
    def __init__(self):
        self.model = ''
        # define legal values which an item may have
        self.legal_input_values = {
           'wlan_common': {
                'channel': ['0','1','2','3','4','5','6','7','8','9','10','11'], #0 to 11
                # 'country_code': 'CA',#'AU, AT, ...',
                'txpower': ['max', 'half', 'quarter', 'eighth', 'min'],
                'prot_mode': ['Disabled', 'CTS-only', 'RTS-CTS'],

            },
            'device_general': {
                'device_name': ['RuckusAPAutoTest'], # test this item by default
                #'username': ['test'], # optional
                # NOTE: don't put more than two selection values for items password, cpassword
                # the define_device_general_cfg may cause problem due to get the value radomly
                #'password': ['test'], # optional
                #'cpassword': ['test'], # optional
            },
            'wlan_det': {
                # use the same information for wlan 1 to 8
                'wlan_num': '%d',
                'avail': ['Disabled','Enabled'],
                'broadcast_ssid': ['Disabled','Enabled'],
                'client_isolation': ['Disabled','Enabled'],
                'wlan_name': 'fm_auto_test_%d',
                'wlan_ssid': 'fm_auto_test_%d',
                'dtim': ['200', '255'],
                'rtscts_threshold': ['2000','2346'],
            },
        }
        # define basic AP config to be tested
        self.test_cfg = {
            'wlan_common': {
                'channel': 'any', #0 to 11
                # 'country_code': 'CA',#'AU, AT, ...',
                'txpower': 'max', # if test data plane, please use 'max' value
                'prot_mode': 'any',
            },
            'device_general': {
                'device_name': 'RuckusAPAutoTest', # test this item by default
            },
            'wlan_det': {
                # use the same information for wlan 1 to 8
                'wlan_num': '%d',
                'avail': 'Enabled',
                'broadcast_ssid': 'Enabled',
                'client_isolation': 'Enabled',
                'wlan_name': 'fm_auto_test_%d',
                'wlan_ssid': 'fm_auto_test_%d',
                'dtim': '200',
                'rtscts_threshold': '2000',
                # other items such as rate_limiting, aunthentication are configured in define_wlan_det_cfg
                'get_rate_limiting': True,
                'encrypt_type': 'WPA',
            },
        }


    def __del__(self):
        del self.legal_input_values
        del self.test_cfg


    def _get_cfg_tmpl(self, item, keys=None):
        '''
        This function is to get tmpl cfg create config template function
        (FlexMaster.create_cfg_template). It use
        - item: may be following values:
            + device_general
            + wlan_common
            + wlan_1
            + wlan_2
        - keys: it may be following data type.
            + None: return all key in the "item" from legal_input_values.
                E.g: item='device_general', keys=None
                => return a cfg tmpl as below
                'device_general': {
                     'device_name': 'RuckusAP',
                     'username': 'test',
                     'password': 'test',
                     'cpassword': 'test',
                }
            + A list: it will get config for elements in the cfg only.
            + A dictionary: it means cfg contains key and expect data for that key
              so no need to get other keys for this cfg template.
              E.g: item = device_general, keys={'device_name': 'RuckusAP'}
              => return the tmpl cfg as below:
                  'device_general': {'device_name': 'RuckusAP'}
        '''
        tmpl_cfg = {}
        if isinstance(keys, dict) and len(keys) > 0:
            # if keys a dict, tmpl cfg contains only element provided in the dict
            tmpl_cfg = copy.deepcopy(keys)
        elif isinstance(keys, list) and len(keys) > 0:
            data = None
            for k in keys:
                v = self.legal_input_values[item][k]
                data = v[random.randint(0, len(v)-1)] if isinstance(v, list) else v
                tmpl_cfg[k] = data
        elif keys is None or len(keys) == 0:
            # keys is None, get all elements of "item" in legal_input_values
            # If any key exists in self.test_cfg, get its value from self.legal_input_values
            input_cfg = self.test_cfg[item]
            data = None
            for k, v in input_cfg.iteritems():
                # if v is list get data randomly from the list, else get v
                data = v[random.randint(0, len(v)-1)] if isinstance(v, list) else v
                tmpl_cfg[k] = data

        return {item: tmpl_cfg}

    def get_device_general_cfg_tmpl(self, keys=None):
        '''
        Get tmpl cfg for device general
        Return:
        - Return a dict of template configs for Device General like
            {'device_general': {}}
        '''
        return self._get_cfg_tmpl(item='device_general', keys=keys)

    def get_wlan_common_cfg_tmpl(self, keys=None):
        '''
        Get tmpl cfg for wlan common
        Return:
        - Return a dict of template configs for Wlan Common like
            {'wlan_common': {}}
        '''
        return self._get_cfg_tmpl(item='wlan_common', keys=keys)

    def get_wlan_det_cfg_tmpl(self, wlan_list=[1], encrypt_type=None, dv_cfg=False):
        '''
        This function is temporarily using interface the same "define_wlan_det_cfg"
        function. Please refer to define_wlan_det_cfg to know its params and its output in detail.

        @TODO: Will enhance this function to use _get_cfg_tmpl function later.
        Return:
        - Return a list of template configs for Wlan Detail
        '''
        return define_wlan_det_cfg(
            **dict(ap_cfg_obj=self, wlan_list=wlan_list, encrypt_type=encrypt_type, dv_cfg=dv_cfg
        ))

    def setTestCfg(self, **kwa):
        '''
        kwa:
        - opt: name of cfg option to set: wlan_common, device_general...
        - items: a dictionary of items of this cfg option to set a new value for test config

        '''
        _kwa = {}
        _kwa.update(kwa)

        self.test_cfg[_kwa['opt']].update(_kwa['items'])

    def setLegalInputValues(self, **kwa):
        '''
        kwa:
        - opt: name of cfg option to set: wlan_common, device_general...
        - items: a dictionary of items of this cfg option to set legal input valuess
        '''
        _kwa = {}
        _kwa.update(kwa)
        self.legal_input_values[_kwa['opt']].update(_kwa['items'])


class ZF2925_Cfg(AP_Cfg):
    '''
    OBSOLETE. Plz use ZF2925_Cfg2
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg.__init__(self)
        self.model = 'zf2925'
        # set legal values for wmode of 2925 WLAN Common
        cfg = {
            'opt': 'wlan_common',
            'items': {
                'wmode': ['auto', '11g'], # version 8.x removed '11b' mode
            }
        }
        self.setLegalInputValues(**cfg)

        # set test value for wmode of 2925 WLAN Common
        cfg = {
            'opt': 'wlan_common',
            'items': {
                'wmode': 'any',
            }
        }
        self.setTestCfg(**cfg)
        # modify wlan detail to make it verify all authentication types: WEP, WPA
        cfg = {
            'opt': 'wlan_det',
            'items': {
                'encrypt_type': 'all',
            }
        }
        self.setTestCfg(**cfg)


class ZF2942_Cfg(AP_Cfg):
    '''
    OBSOLETE. Plz use ZF2942_Cfg2
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg.__init__(self)
        self.model = 'zf2942'
        # set legal values for wmode of 2942 WLAN Common
        cfg = {
            'opt': 'wlan_common',
            'items': {
                'wmode': ['auto', '11g'], #version 8.0 has removed '11b'
            }
        }
        self.setLegalInputValues(**cfg)

        # set test value for wmode of 2942 WLAN Common
        cfg = {
            'opt': 'wlan_common',
            'items': {
                'wmode': 'any',
            }
        }
        self.setTestCfg(**cfg)

        # modify wlan detail to make it verify all authentication types: WEP, WPA
        cfg = {
            'opt': 'wlan_det',
            'items': {
                'encrypt_type': 'all',
            }
        }
        self.setTestCfg(**cfg)


class ZF7942_Cfg(AP_Cfg):
    '''
    OBSOLETE. Plz use ZF7942_Cfg2
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg.__init__(self)
        self.model = 'zf7942'
        cfg = {
            'opt': 'wlan_det',
            'items': {
                'encrypt_type': 'all',
            }
        }
        self.setTestCfg(**cfg)
        cfg = {
            'opt': 'wlan_common',
            'items': {
                'channel_width': ['20', '40'], #version 8.0 has removed '11b'
            }
        }
        self.setLegalInputValues(**cfg)
        # TODO: We have a bug 9460 about change "Cannot channel and channel width at the same time"
        # So temporarily, we don't verify "channel width" item
        # cfg = {
        #    'opt': 'wlan_common',
        #    'items': {
        #        'channel_width': 'any',
        #    }
        #}
        #self.setTestCfg(**cfg)


class ZF7962_Cfg(AP_Cfg):
    '''
    OBSOLETE. Plz use ZF7962_Cfg2
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg.__init__(self)
        self.model = 'zf7942'
        cfg = {
            'opt': 'wlan_det',
            'items': {
                'encrypt_type': 'all',
            }
        }
        # update specific 7962 items for wlan_common
        NO_CHANNELS = 165
        cfg = {
                'channel_1': ['0','1','2','3','4','5','6','7','8','9','10','11'],
                'channel_2': ['0', '36','40','44','48'],#many countrycodes don't have channels:'52','100','104','108','153','157','161','165'],
                'channel_width_1': ['20', '40'],
                'channel_width_2': ['20', '40'], #version 8.0 has removed '11b'
                'country_code': ['AT', 'CA', 'FR', 'ID', 'JP', 'TW', 'CH', 'SE', 'GB', 'US', ],
                #'txpower': ['max', 'half', 'quarter', 'eighth', 'min'],
                #'prot_mode': ['Disabled', 'CTS-only', 'RTS-CTS'],

            }
        self.legal_input_values['wlan_common'].update(cfg)
        # dtim key is not available on 7962, remove it
        del self.legal_input_values['wlan_det']['dtim']
        del self.test_cfg['wlan_det']['dtim']
        del self.legal_input_values['wlan_common']['channel']
        del self.test_cfg['wlan_common']['channel']
        del self.legal_input_values['wlan_common']['txpower']
        del self.test_cfg['wlan_common']['txpower']
        del self.legal_input_values['wlan_common']['prot_mode']
        del self.test_cfg['wlan_common']['prot_mode']


class ZF2741_Cfg(AP_Cfg):
    '''
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg.__init__(self)
        self.model = 'zf2741'
        cfg = {
            'opt': 'wlan_det',
            'items': {
                'encrypt_type': 'all',
            }
        }
        self.setTestCfg(**cfg)

        self.legal_input_values['device_general']['temp_update_interval'] = [
            '40', '600', '5400' # unit: in second
        ]
        # Temporarily, remove out "temp_update_interval" item. Will support it later
        #self.test_cfg['device_general']['temp_update_interval'] = 'any'


def define_device_general_cfg(**kwa):
    '''
    OBSOLETE: Plz use define_device_general_cfg_2
    To difine Device General items.
    kwa:
    - 'device_name': True if want to get this info, False if otherwise
    - 'username': True if want to get this info, False if otherwise
    - 'password': True if want to get this info, False if otherwise
    - 'cpassword': it depends on 'password'
    - 'all': True if want to get all items
    - ap_cfg_obj: ap config object
    '''
    _kwa = {
        'all': False,  # temporarily not support this para
        'ap_cfg_obj': None,
    }
    _kwa.update(kwa)

    opt = 'device_general'
    # get test config from ap config object
    test_cfg = _kwa['ap_cfg_obj'].test_cfg[opt]
    # get legal input values from ap_cfg object
    legal_input_values = _kwa['ap_cfg_obj'].legal_input_values[opt]

    list_ret_cfg = [] # just in case want to return a list of cfgs to test wlan_common
    cfg = {}
    for k in test_cfg.iterkeys():
        #if _kwa['all'] or _kwa[k]:
        # get random value from legal input values for this item
        #random_val = legal_input_values[k][random.randint(0, len(legal_input_values[k])-1)]
        cfg[k] = cfg[k] = test_cfg[k] if test_cfg[k].lower() != 'any' else \
                    legal_input_values[k][random.randint(0, len(legal_input_values[k])-1)]# get randomly

    list_ret_cfg.append({opt:cfg})
    return list_ret_cfg


def define_wlan_common_cfg(**kwa):
    '''
    OBSOLETE: Use define_wlan_common_cfg_2 instead.
    To difine wlan common items.
    kwa:
    'wmode': True if want to get this info, False if otherwise,
    - 'channel': True if want to get this info, False if otherwise,
    - 'channel_width': True if want to get this info, False if otherwise,
    # David talked to me that, TDC FM team agree doesn't need to test country coe
    # so I (Hieu Phan) commented it out.
    # 'country_code': 'CA',#'AU, AT, ...',
    - 'txpower': True if want to get this info, False if otherwise,
    - 'prot_mode': True if want to get this info, False if otherwise,
    - 'all': True if want to get all items,
    - assoc_test: True: set txpower to "max". Otherwise, let it random. It is to make sure
                  laptop client can associate successfully
    - ap_cfg_obj: instance to hold AP config object
    '''
    _kwa = {
        'all': False,  # temporarily not support this para
        'assoc_test': None,  # temporarily not support this para
        'ap_cfg_obj': None,
        'dv_cfg': False,
    }
    # update 'all', 'model' and assoc_test from kwa
    _kwa.update(kwa)

    opt = 'wlan_common'
    # get test config from ap config object
    test_cfg = _kwa['ap_cfg_obj'].test_cfg[opt]

    # TODO: We have a bug 9460 and another one relate to change "channel, channel width,
    # and 'wireless mode' at the same time on Device View.
    # So temporarily, if this config is to config AP from Device View, we don't verify "channel width",
    # "wmode" items.
    if _kwa['dv_cfg']:
        remove_items = ['channel_width', 'wmode']
        for k in remove_items:
            if test_cfg.has_key(k): del test_cfg[k]

    # get legal input values from ap_cfg object
    legal_input_values = _kwa['ap_cfg_obj'].legal_input_values[opt]

    list_ret_cfg = [] # just in case want to return a list of cfgs to test wlan_common
    cfg = {}
    for k in test_cfg.iterkeys():
        #if _kwa['all'] or _kwa[k]:
        # get random value from legal input values for this item
        #random_val = legal_input_values[k][random.randint(0, len(legal_input_values[k])-1)]
        cfg[k] = test_cfg[k] if test_cfg[k].lower() != 'any' else \
                    legal_input_values[k][random.randint(0, len(legal_input_values[k])-1)]# get randomly

    list_ret_cfg.append({opt:cfg})
    return list_ret_cfg


def define_rate_limiting_cfg(**kwa):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    To define Rate Limiting items
    kwa:
    - uplink: True if want to get this info, False if otherwise,
    - downlink: it denpends on uplink
    Output:
    - For dv_cfg = True:
        -> a list of dictionary which has no_cfg elements.
            [
                {'uplink': '100kbps', 'downlink': '50mbps'},
                {'uplink': '250kbps', 'downlink': '20mbps'},
                .............
                {'uplink': '50mbps', 'downlink': '100kbps'},
            ]
    - For dv_cfg = False:
        + Uplink = True: return a dict as below
        -> {
                'rate_limiting': 'Enabled',
                'uplink': a random value of a list rate limiting threshold,
                'downlink': a symmetric value of uplink in the rate limiting threshold list,
           }
        + Uplink = False: return a dict as below with only one element
        -> {
                'rate_limiting': 'Disabled',
           }

    '''
    _kwa = {
        'uplink': False,
        'downlink': False,
        'dv_cfg': False, # if this cfg is for Device View, don't include
                         # "rate_limiting"
        'no_cfg': 1, # number of cfgs to get.
                     # use this param only if dv_cfg is True. Default is 1, maximum: 8

    }
    _kwa.update(kwa)
    _kwa['downlink'] = _kwa['uplink']

    rate = [
        '100kbps', '250kbps', '500kbps', '1mbps', '2mbps',
        '5mbps', '10mbps', '20mbps', '50mbps',
    ]
    rate_len = len(rate)

    if _kwa['dv_cfg']:
        items = []
        for i in range(_kwa['no_cfg']):
            #cfg = copy.deepcopy(val)
            idx = i if i < rate_len else rate_len - 1
            items.append(dict(
                        uplink = rate[idx],
                        downlink = rate[rate_len - idx - 1],
                  ))
    else:
        items = {}
        idx = random.randint(0, rate_len - 1)
        if _kwa['uplink']:
            # if uplink is True, it means rate limiting is enabled
            items['rate_limiting'] = 'Enabled' # 'rate_limiting': 'Enabled',#Disabled, Enabled
            items.update(dict(
                              uplink = rate[idx],
                              downlink = rate[rate_len - idx - 1], # reversed value of uplink
                        ))
        else:
            # if uplink is False, it means rate limiting is Disabled
            items['rate_limiting'] = 'Disabled'

    return items


def _define_wep_cfg(**kwa):
    '''
    To define items for three WEP mode: 'Open', 'SharedKey', 'Auto'
    kwa:
    - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
              (confirm password)
    - mode: 'Open', 'SharedKey', 'Auto'
    - encryption_len: 5, 10, 13, 26
    - kex_idx: key_index for this wlan

    output:
    return the following keys and theirs config items:
        wep_open_5_ascii, wep_open_10_hex, wep_open_13_ascii, wep_open_26_hex
        wep_sharedkey_5_ascii, wep_sharedkey_10_hex, wep_sharedkey_13_ascii, wep_sharedkey_26_hex
        wep_auto_5_ascii, wep_auto_10_hex, wep_auto_13_ascii, wep_auto_26_hex
    '''
    _kwa = {
        'dv_cfg': False,
        'mode': 'Auto',
        'encryption_len': 5,
        'key_idx': 1, # 1 as default
    }
    _kwa.update(kwa)

    modes = ['Open', 'SharedKey', 'Auto']
    if not _kwa['mode'] in modes:
        raise Exception('Mode "%s" is not in "%s"' % (_kwa['mode'], modes))

    encryption_lens = [5, 10, 13, 26]
    if not _kwa['encryption_len'] in encryption_lens:
        raise Exception('Encryption len "%s" is not in "%s"' % (_kwa['encryption_len'], encryption_lens))

    wep_pass = {
        5: '12345',
        10: '12345ABCDE',
        13: '1234567890abc',
        26: '1234567890abcdef1234567890',
    }[_kwa['encryption_len']]

    wep_type_list = {}

    # Define WEP items
    type = 'wep_%s_%d_%s' % \
           (_kwa['mode'].lower(),
            _kwa['encryption_len'],
            'ascii' if _kwa['encryption_len'] in [5, 13] else 'hex')

    det = {
        'encrypt_method': 'WEP', # 'Disabled', 'WEP', ''
        'wep_mode': _kwa['mode'],#'Open, SharedKey, Auto',
        'encryption_len': '%s' % _kwa['encryption_len'],#'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
        #Wireless 1 WEP Key Index
        'wep_key_idx': '%d' % _kwa['key_idx'],#'key index: 1, 2, 3, 4',
        #WEP key password
        'wep_pass': wep_pass,#'password of wep method',
        'cwep_pass': wep_pass,#'password of wep method (confirm)',
    }

    # if this config is for Device View, remove cwep_pass item
    if _kwa['dv_cfg']:
        del det['cwep_pass']

    return {type: det}


def _define_wep_list_cfg(**kwa):
    '''
    To define all type of config for WEP
    kwa:
    - mode: 'all': default get all modes.
    '''
    _kwa = {
        'dv_cfg': False,
        'mode': 'all',
    }
    _kwa.update(kwa)
    # Define config for WEP authentication
    wep_type_list_cfg = {}
    encryption_lens = [5, 10, 13, 26]

    wep_modes = ['Open', 'SharedKey', 'Auto'] if _kwa['mode'].lower() == 'all' else [_kwa['mode']]
    for mode in wep_modes:
        for i in range(0, len(encryption_lens)):
            wep_type_list_cfg.update(
                _define_wep_cfg(
                    mode=mode, encryption_len=encryption_lens[i], key_idx=i+1, dv_cfg=_kwa['dv_cfg']
            ))
    '''
    if _kwa['mode'].lower() == 'all':
        wep_modes = ['Open', 'SharedKey', 'Auto']
        for mode in wep_modes:
            for i in range(0, len(encryption_lens)):
                wep_type_list_cfg.update(_define_wep_cfg(mode=mode, encryption_len=encryption_lens[i], key_idx=i+1))
    else:
        for len in encryption_lens:
            wep_type_list_cfg.update(_define_wep_cfg(mode=_kwa['mode'], encryption_len=len))
    '''
    return wep_type_list_cfg


def _define_wpa_cfg(**kwa):
    '''
    To define items for WPA, WPA2
    kwa:
    - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
              (confirm password)
    - 'version': WPA, WPA2, Auto,
    - 'algorithm': TKIP, AES, Auto,
    - 'auth': PSK, 802.1x, Auto, # Authentication
    Constant:
    RAS_NAS_ID = '111'
    RAS_ADDR = '192.168.0.124'
    RAS_PORT = '1863'
    RAS_SECRET = '123456'

    output:
    - Return the following keys and theirs items
        wpa_tkip_psk,  wpa_tkip_auto,  wpa_tkip_802.1x
        wpa_aes_psk,   wpa_aes_auto,   wpa_aes_802.1x
        wpa_auto_psk,  wpa_auto_auto,  wpa_auto_802.1x
        wpa2_tkip_psk, wpa2_tkip_auto, wpa2_tkip_802.1x
        wpa2_aes_psk,  wpa2_aes_auto,  wpa2_aes_802.1x
        wpa2_auto_psk, wpa2_auto_auto, wpa2_auto_802.1x
        auto_tkip_psk, auto_tkip_auto, auto_tkip_802.1x
        auto_aes_psk,  auto_aes_auto,  auto_aes_802.1x
        auto_auto_psk, auto_auto_auto, auto_auto_802.1x
    '''
    _kwa = {
        'version': 'WPA',
        'algorithm': 'TKIP',
        'auth': 'PSK',
    }
    _kwa.update(kwa)

    versions = ['WPA', 'WPA2', 'Auto']
    if not _kwa['version'] in versions:
        raise Exception('WPA version "%s" is not in "%s"' % (_kwa['version'], versions))

    algorithms = ['TKIP', 'AES', 'Auto']
    if not _kwa['algorithm'] in algorithms:
        raise Exception('WPA algorthm "%s" is not in "%s"' % (_kwa['algorithm'], algorithms))

    auths = ['PSK', '802.1x', 'Auto']
    if not _kwa['auth'] in auths:
        raise Exception('Authentication "%s" is not in "%s"' % (_kwa['auth'], auths))

    '''
    #Authentication
    'auth': 'PSK', #'Authentication: PSK, 802.1x, Auto',
    'psk_passphrase': 'abcdefghijk',#'PSK passphrase',
    'cpsk_passphrase': 'abcdefghijk',#'PSK passphrase (confirm)',
    '''
    # define items for PSK authentication
    auth_psk = {
        'psk_passphrase': 'abcdefghijk',#'PSK passphrase',
        'cpsk_passphrase': 'abcdefghijk',#'PSK passphrase (confirm)',
    }

    # define items for 802.1x authentication
    auth_8021x = { #'Authentication: PSK, 802.1x, Auto',
        #'psk_passphrase': 'abcdefghijk',#'PSK passphrase',
        #'cpsk_passphrase': 'abcdefghijk',#'PSK passphrase (confirm)',
        'radius_nas_id': RAS_NAS_ID,#'Radius NAS-ID',
        'auth_ip': RAS_ADDR,#'Authentication IP address',
        'auth_port': RAS_PORT,#'Authentication Port',
        'auth_secret': RAS_SECRET,#'Authentication Server Secret',
        'cauth_secret': RAS_SECRET,#'Authentication Server Confirm Secret',

        # Just put them here to avoid error when create a config provisioning template
        'acct_ip': ACC_ADDR,#Accounting IP address',
        'acct_port': ACC_PORT,#'Accounting Port',
        'acct_secret': ACC_SECRET, #'Accounting Server Secret',
        'cacct_secret': ACC_SECRET, #'Accounting Server Secret (confirm)'
    }

    # define items for Auto authentication
    auth_auto = dict(auth_psk)
    auth_auto.update(auth_8021x)

    auth_items = {
        'PSK': auth_psk,
        '802.1x': auth_8021x,
        'Auto': auth_auto,
    }[_kwa['auth']]

    det = {
        'encrypt_method': 'WPA',#'Disabled, WEP, WPA',
        'wpa_version': _kwa['version'],#'WPA version: WPA, WPA2, Auto',
        'wpa_algorithm': _kwa['algorithm'],#'WPA Algorithm: TKIP, AES, Auto',
        'auth': _kwa['auth'],
    }

    det.update(auth_items)

    # if this conifig is for Device View, remove some "confirm" items like: 'cpsk_passphrase'
        # 'cauth_secret', 'cacct_secret'
    if _kwa['dv_cfg']:
        removed_items = ['cpsk_passphrase', 'cacct_secret', 'cauth_secret']
        for k in removed_items:
            if det.has_key(k): del det[k]

    type = '%s_%s_%s' % (_kwa['version'].lower(), _kwa['algorithm'].lower(), _kwa['auth'].lower())
    return {type: det}


def _define_wpa_list_cfg(**kwa):
    '''
    To define all kind of configs for versions WPA, WPA2 and Auto
    kwa:
    - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
              (confirm password)
    - version: WPA, WPA2, Auto, all
    Output:
    - Return a dictionary of all type of WPA encryptions
    '''
    _kwa = {
        'dv_cfg': False,
        'version': 'all', # Default get all versions
    }
    _kwa.update(kwa)
    wpa_type_list_cfg = {}
    # Define config for WPA authentication
    wpa_algorithms = ['TKIP', 'AES', 'Auto']
    wpa_auths = ['PSK', '802.1x', 'Auto']

    if _kwa['version'].lower() == 'all':
        wpa_versions = ['WPA', 'WPA2', 'Auto']
        for ver in wpa_versions:
            for algor in wpa_algorithms:
                for auth in wpa_auths:
                    wpa_type_list_cfg.update(_define_wpa_cfg(version=ver, algorithm=algor, auth=auth, dv_cfg=_kwa['dv_cfg']))
    else:
        for algor in wpa_algorithms:
            for auth in wpa_auths:
                wpa_type_list_cfg.update(_define_wpa_cfg(version=_kwa['version'], algorithm=algor, auth=auth, dv_cfg=_kwa['dv_cfg']))

    return wpa_type_list_cfg


def put_encrypt_list_to_wlans(**kwa):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    kwa:
    - wlan_list: list of wlans to spread out the encrypt items into wlans.
                 1 as default to avoid problem if put WEP encryption types into wlans since
                 WEP use four key index only. It may be [1,2], [3,4], [5,6], [1,3,5,7], [2,4,6,8] ...
    - encrypt_list: a list of encryptions type. This may have only one element or a lot of
                    elements if encrypt_list are element of WEP or WPA.
                    Remember to pass a list for this para
    - ap_cfg_obj: object to hold ap test config
    '''
    _kwa = {
        'dv_cfg': False,
        'wlan_list': [1], # wlans to put encryption list into it
        'encrypt_list': [],
        'max_wlan': 8,
        'ap_cfg_obj': None,
    }
    _kwa.update(kwa)

    is_open_system = True if len(_kwa['encrypt_list']) < 1 else False

    # get list items for wlan_det config
    test_cfg = copy.deepcopy(_kwa['ap_cfg_obj'].test_cfg['wlan_det'])
    get_rate_limiting = False if _kwa['dv_cfg'] else test_cfg['get_rate_limiting']

    # remove two items aren't belong to wlan detail
    k = 'get_rate_limiting'
    test_cfg.pop(k)
    k = 'encrypt_type'
    test_cfg.pop(k)

    # each element of this list_cfg is a dictionary of wlans
    list_cfgs = []
    idx = 0
    #from_wlan, to_wlan = 1, no_wlan
    while True:
        wlan = {}
        # The idea is that we rotate to put the encryption list into all 8 wlans
        # to have a chance to verify all wlans pages. However, if users only want
        # to put into 4 wlans for WEP encryption list, we will put encryption list
        # into wlan 1 to 4 first then next loop put to wlan 5 to 8. Hence, we have
        # to control start wlan and end wlan for each "for" loop
        for i in range(len(_kwa['wlan_list'])):
            cfg = copy.deepcopy(test_cfg)
            cfg['wlan_num'] = cfg['wlan_num'] % _kwa['wlan_list'][i]
            cfg['wlan_name'] = cfg['wlan_name'] % _kwa['wlan_list'][i]
            cfg['wlan_ssid'] = cfg['wlan_ssid'] % _kwa['wlan_list'][i]

            # update rate limiting items if user configures rate limiting
            if get_rate_limiting: cfg.update(define_rate_limiting_cfg(uplink=True))
            if not is_open_system: cfg.update(_kwa['encrypt_list'][idx])

            key = 'wlan_%d' % _kwa['wlan_list'][i]
            wlan.update({key:cfg})
            idx +=1
            # if not configure for Open system and idx is out of bound of 'encrypt_list', break
            if not is_open_system and idx >= len(_kwa['encrypt_list']): break

        # update
        list_cfgs.append(wlan)

        # if these wlans for Open system, break
        if is_open_system or idx >= len(_kwa['encrypt_list']): break

    return list_cfgs


def define_all_web_encrypt_cfg(**kwa):
    '''
    To difine all Web authentication configs: Open, WEP, WPA, and WPA2.
    kwa:
    - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
              (confirm password)
    '''
    auth_type_list = {}

    # open system
    type = 'open'
    det = {
        'encrypt_method': 'Disabled',
    }
    auth_type_list.update({type: det})

    # Define config for WEP authentication
    auth_type_list.update(_define_wep_list_cfg(**kwa))

    # Define config for WPA authentication
    auth_type_list.update(_define_wpa_list_cfg(**kwa))

    return auth_type_list


def define_wlan_det_cfg(**kwa):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    To define config for WLAN 1 to 8. This function will define following items:
    Rate Limiting, Authentication and other items such as DTIM, Threshold,
    Wireless SSID, Wireless Name... of WLAN pages.
    kwa:
    - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
              (confirm password)
    - ap_cfg_obj: object to hold ap test config
    - wlan_list: a list of wlans. Specify this para if want to verify 1 wlan.
                 This para is only used for cases: Test Open system and
                 test only 1 authentication
    - encrypt_type: open: get configs for Open system without encryption.
                    wep:  get configs for WEP encryption. It rotates to put the configs into 4 wlans.
                          Because we cannot use duplicated key index so use only 4 wlans.
                    wpa:  get configs for WPA encryption. It rotates to put the configs into 8 wlans.
                    wpa2: get configs for WPA2 encryption. It rotates to put the configs into 8 wlans.
                    all:  will get all encryption types. It rotates to put the configs into 8 wlans
                          Only using this value if want to test all encryption types and it will not
                          care about the wlan_no parameter.
                          Please refer to _define_wpa_cfg(), _define_wep_cfg() to know keys for encrypt_type

    Ex to use this function to define group of cfgs to test Open, WEP, WPA, WPA2
    1. Open system for 4 wlans: 1, 3, 5, 7 with Rate Limiting enabled
    => define_wlan_det_cfg(wlan_list=[1,3,5,7], get_rate_limiting=True)

    2. Open system for 4 wlans: 1, 3, 5, 7 with Rate Limiting Disabled
    => define_wlan_det_cfg(wlan_list=[1,3,5,7], get_rate_limiting=False)

    3. WEP encryption, Rate Limiting enabled:
    => define_wlan_det_cfg(get_rate_limiting=True, encrypt_type='wep')
    Note: Currently,
        Rotate to put WEP/Open encryptions into wlan 1,2,3,4
        Rotate to put WEP/SharedKey encryptions into wlan 5,6,7,8
        Rotate to put WEP/Auto encryptions into wlan 1,2,3,4

        The intention is try to verify all 8 wlan.

    4. WEP encryption, Rate Limiting disabled:
    => define_wlan_det_cfg(get_rate_limiting=False, encrypt_type='wep')

    5. WPA encryption, Rate Limiting enabled:
    => define_wlan_det_cfg(get_rate_limiting=False, encrypt_type='wpa')
    Note: Currently,
        Rotate to put WPA encryptions into all 8 wlans

    6. WPA2 encryption, Rate Limiting enabled:
    => define_wlan_det_cfg(get_rate_limiting=False, encrypt_type='wpa2')
    Note: Currently,
        Rotate to put WPA2 encryptions into all 8 wlans
    '''
    _kwa = {
        'dv_cfg': False,
        'wlan_list': [1], # default
        'encrypt_type': None,
        'ap_cfg_obj': None,
    }
    _kwa.update(kwa)

    list_wlan_cfgs = []
    ap_cfg_obj = _kwa['ap_cfg_obj']
    test_cfg = _kwa['ap_cfg_obj'].test_cfg['wlan_det']
    encrypt_type = _kwa['encrypt_type'] if _kwa['encrypt_type'] else test_cfg['encrypt_type']

    #if _kwa['encrypt_type'].lower() in combination_items:
    # use open system
    if encrypt_type.lower() == 'open':
        cfg = {
            'dv_cfg': _kwa['dv_cfg'],
            'wlan_list': _kwa['wlan_list'],
            #'get_rate_limiting': get_rate_limiting,
            'encrypt_list': [],
            'ap_cfg_obj': ap_cfg_obj,
        }
        for x in put_encrypt_list_to_wlans(**cfg): list_wlan_cfgs.append(x)
    elif re.match(r'^open.*|^wep_.*|^wpa_.*|^wpa2_.*', encrypt_type, re.I):
        # print 'Got one config'
        # get only one encryption of either wep or wpa
        all_encrypt_cfgs = define_all_web_encrypt_cfg(dv_cfg=_kwa['dv_cfg'])
        # test only one wlan
        cfg = {
            'dv_cfg': _kwa['dv_cfg'],
            'wlan_list': _kwa['wlan_list'],
            #'get_rate_limiting': get_rate_limiting,
            'encrypt_list': [all_encrypt_cfgs[encrypt_type]], # get only one encryption type
            'ap_cfg_obj': ap_cfg_obj,
        }
        for x in put_encrypt_list_to_wlans(**cfg): list_wlan_cfgs.append(x)
    elif re.match(r'^wep|^wpa$|^wpa2$|^all$', encrypt_type, re.I):
        #if _kwa['encrypt_type'].lower()=='all' or _kwa['encrypt_type'].lower() =='wep':
        if re.match(r'^all$|^wep$', encrypt_type, re.I):
            # get config for encryption type WEP/Open
            encrypt_list = _define_wep_list_cfg(mode='Open', dv_cfg=_kwa['dv_cfg'])

            cfg = {
                'dv_cfg': _kwa['dv_cfg'],
                'wlan_list': [1,2,] if len(_kwa['wlan_list'])<=1 else _kwa['wlan_list'],
                #'get_rate_limiting': get_rate_limiting,
                'encrypt_list': encrypt_list.values(),
                'ap_cfg_obj': ap_cfg_obj,
            }
            #list_wlan_cfgs.append(put_encrypt_list_to_wlans(**cfg))
            for x in put_encrypt_list_to_wlans(**cfg): list_wlan_cfgs.append(x)

            # get config for encryption type WEP/SharedKey
            encrypt_list = _define_wep_list_cfg(mode='SharedKey', dv_cfg=_kwa['dv_cfg'])
            cfg = {
                'dv_cfg': _kwa['dv_cfg'],
                'wlan_list': [5,6,] if len(_kwa['wlan_list'])<=1 else _kwa['wlan_list'],
                #'get_rate_limiting':get_rate_limiting,
                'encrypt_list': encrypt_list.values(),
                'ap_cfg_obj': ap_cfg_obj,
            }
            #list_wlan_cfgs.append(put_encrypt_list_to_wlans(**cfg))
            for x in put_encrypt_list_to_wlans(**cfg): list_wlan_cfgs.append(x)

            # get config for encryption type WEP/Auto
            encrypt_list = _define_wep_list_cfg(mode='Auto', dv_cfg=_kwa['dv_cfg'])
            cfg = {
                'dv_cfg': _kwa['dv_cfg'],
                'wlan_list': [3,4,] if len(_kwa['wlan_list'])<=1 else _kwa['wlan_list'],
                #'get_rate_limiting':get_rate_limiting,
                'encrypt_list': encrypt_list.values(),
                'ap_cfg_obj': ap_cfg_obj,
            }
            #list_wlan_cfgs.append(put_encrypt_list_to_wlans(**cfg))
            for x in put_encrypt_list_to_wlans(**cfg): list_wlan_cfgs.append(x)

        # wpa includes versions wpa and wpa2
        if re.match(r'^all$|^wpa$', encrypt_type, re.I):
            # get config for encryption type WPA
            encrypt_list = _define_wpa_list_cfg(version='all', dv_cfg=_kwa['dv_cfg'])
            cfg = {
                'dv_cfg': _kwa['dv_cfg'],
                'wlan_list': [7,8] if len(_kwa['wlan_list'])<=1 else _kwa['wlan_list'],
                #'get_rate_limiting':get_rate_limiting,
                'encrypt_list': encrypt_list.values(),
                'ap_cfg_obj': ap_cfg_obj,
            }
            #list_wlan_cfgs.append(put_encrypt_list_to_wlans(**cfg))
            for x in put_encrypt_list_to_wlans(**cfg): list_wlan_cfgs.append(x)

    return list_wlan_cfgs


def define_ap_cfg(**kwa):
    '''
    OBSOLETE: Please use get_ap_test_cfg
    kwa:
    - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
              (confirm password)
    - ap_cfg_obj: to hold test ap config
    '''
    _kwa = {
        'dv_cfg': False,
        'ap_cfg_obj': None,
        'wlan_list': [1],
    }
    _kwa.update(kwa)

    raw_test_cfg = []
    max_len = 0

    # if this config is for Device View, remove rate_limiting_item
    if _kwa['dv_cfg'] and _kwa['ap_cfg_obj'].test_cfg.has_key('wlan_det'):
        cfg = {
            'opt': 'wlan_det',
            'items': {
                'get_rate_limiting': False,
            }
        }
        _kwa['ap_cfg_obj'].setTestCfg(**cfg)

    for k in _kwa['ap_cfg_obj'].test_cfg.iterkeys():
        #print 'k: %s' % k
        cfg = {
            'device_general': define_device_general_cfg(**_kwa),
            'wlan_common': define_wlan_common_cfg(**_kwa),
            'wlan_det': define_wlan_det_cfg(**_kwa),
        }[k]# return a list of cfg for "k" option

        # each item of raw_test_cfg will be a list
        raw_test_cfg.append(cfg)
        # get the max len of config option
        if max_len < len(cfg): max_len = len(cfg)

    list_test_cfg = []
    idx = 0

    while idx < max_len:
        test_cfg = {}
        # each element of raw_test_cfg is a list of dictionary element
        for cfg in raw_test_cfg:
            if idx < len(cfg):
                test_cfg.update(cfg[idx])

        list_test_cfg.append(test_cfg)
        idx +=1

    return list_test_cfg


class AP_Cfg2:
    def __init__(self):
        self.model = ''
        # define legal values which an item may have
        # NOTE: Set the first value as the defailt value.
        self.legal_input_values = {
           'device_general': {
                'device_name': ['RuckusAP', 'RuckusAPAutoTest'], # test this item by default
                #'username': ['test'], # optional
                # NOTE: don't put more than two selection values for items password, cpassword
                # the define_device_general_cfg may cause problem due to get the value radomly
                #'password': ['test'], # optional
                #'cpassword': ['test'], # optional
           },
           'wlan_common': {
                'channel': ['0','1','2','3','4','5','6','7','8','9','10','11'], #0 to 11
                # 'country_code': 'CA',#'AU, AT, ...',
                'txpower': ['max', 'half'],#, 'quarter', 'eighth', 'min'],
                'prot_mode': ['Disabled', 'CTS-only', 'RTS-CTS'],

            },
            'wlan_det': {
                # use the same information for wlan 1 to 8
                'wlan_num': '%d',
                'avail': ['Disabled','Enabled'],
                'broadcast_ssid': ['Disabled','Enabled'],
                'client_isolation': ['Disabled','Enabled'],
                'wlan_name': 'fm_auto_test_%d',
                'wlan_ssid': 'fm_auto_test_%d',
                'dtim': ['1', '10', '100', '300'],
                'rtscts_threshold': ['2346', '2000'],
                # rate limiting cfg
            },
        }
        # general keys for each wlan 1, 2,..
        self.general_wlan_keys = {
            'wlan_num': '%s',
            'avail': 'Enabled',
            'broadcast_ssid': 'Enabled',
            'client_isolation': 'Enabled',
            'wlan_name': 'fm_auto_test_%s',
            'wlan_ssid': 'fm_auto_test_%s',
            'dtim': '10',
            'rtscts_threshold': '2000',
        }


    def _get_sample_cfg(self,
            cfg_name='device_general', is_dv_cfg=False, get_original_cfg=False
        ):
        '''
        To get cfg for device_general and wlan_common
        . cfg_name: device_general, wlan_common
        . is_dv_cfg: True if get cfg for Device View
        '''
        sample_cfg, name = {}, ''
        for k, v in self.legal_input_values[cfg_name].iteritems():
            # if get_default_cfg=True, get the first value of list
            val_idx = 0 if get_original_cfg else random.randint(0, len(v)-1)
            # if v is list get data randomly from the list, else get v
            sample_cfg[k] = v[val_idx] if isinstance(v, list) else v
            name = name + k if name == '' else name + ', ' + k

        return dict(name = name, cfg = {cfg_name:sample_cfg})


    def get_device_general_cfg(self, is_dv_cfg=False):
        '''
        '''
        return self._get_sample_cfg('device_general', is_dv_cfg)


    def get_original_device_general_cfg(self, is_dv_cfg=False):
        '''
        to get manufacturing original cfg for device_general
        '''
        # no need to return name of cfg, return cfg only
        return self._get_sample_cfg('device_general', is_dv_cfg, True)['cfg']


    def get_wlan_common_cfg(self, is_dv_cfg=False):
        '''
        '''
        return self._get_sample_cfg('wlan_common', is_dv_cfg)


    def get_original_wlan_common_cfg(self, is_dv_cfg=False):
        '''
        to get manufacturing original cfg for wireless common
        '''
        return self._get_sample_cfg('wlan_common', is_dv_cfg, True)['cfg']


    def _generate_a_wep_cfg(self,
            mode='Auto', encryption_len=5, key_idx=1, is_dv_cfg=False
        ):
        '''
        To define a cfg for three WEP mode: 'Open', 'SharedKey', 'Auto'
        kwa:
        . mode: 'Open', 'SharedKey', 'Auto'
        . encryption_len: 5, 10, 13, 26
        . kex_idx: key_index for this wlan
        . is_dv_cfg:
            True: This config is for Device View so no return cwep_pass
                  (confirm password)
            False: Template Config, require confirm pass

        Output: {key_name: config dict}

        return the following keys and theirs config items:
            wep_open_5_ascii, wep_open_10_hex, wep_open_13_ascii, wep_open_26_hex
            wep_sharedkey_5_ascii, wep_sharedkey_10_hex, wep_sharedkey_13_ascii, wep_sharedkey_26_hex
            wep_auto_5_ascii, wep_auto_10_hex, wep_auto_13_ascii, wep_auto_26_hex
        '''
        modes, encryption_lens = ['Open', 'SharedKey', 'Auto'], [5, 10, 13, 26]
        wep_pass = {
            5: '12345',
            10: '12345ABCDE',
            13: '1234567890abc',
            26: '1234567890abcdef1234567890',
        }[encryption_len]
        #wep_pass = ''.join(random.sample('0123456789abcdef0123456789', encryption_len)).replace(' ', '')

        key_name = 'wep_%s_%d_%s' % (
                        mode.lower(),
                        encryption_len,
                        'ascii' if encryption_len in [5, 13] else 'hex'
                    )

        cfg = {
            'encrypt_method': 'WEP', # 'Disabled', 'WEP', ''
            'wep_mode': mode,#'Open, SharedKey, Auto',
            'encryption_len': str(encryption_len),#'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
            #Wireless 1 WEP Key Index
            'wep_key_idx': str(key_idx),#'key index: 1, 2, 3, 4',
            #WEP key password
            'wep_pass': wep_pass,#'password of wep method',
        }

        # if this config is not for Device View, add confirm cwep_pass
        if not is_dv_cfg: cfg['cwep_pass'] = wep_pass

        return dict(name=key_name, cfg=cfg)


    def _generate_all_wep_cfgs(self, is_dv_cfg=False):
        '''
        To generate all type of configs for WEP
        . is_dv_cfg:
            True: This config is for Device View so no return cwep_pass
                  (confirm password)
            False: Template Config, require confirm pass
        . Return: List of config with format below
            [
                {key_1: cfg_1},
                {key_2: cfg_2},
                ....
            ]
        '''
        wep_modes, encryption_lens = ['Open', 'SharedKey', 'Auto'], [5, 10, 13, 26]

        all_wep_cfgs = []
        for mode in wep_modes:
            key_idx = 0
            for encryption_len in encryption_lens:
                key_idx = key_idx+1 if key_idx<4 else 0 # Need check this??
                all_wep_cfgs.append(
                    self._generate_a_wep_cfg(mode, encryption_len, key_idx, is_dv_cfg)
                )

        return all_wep_cfgs


    def _generate_a_wpa_cfg(self,
            version='WPA', algorithm='TKIP', auth='PSK', is_dv_cfg=False
        ):
        '''
        To define items for WPA, WPA2
        kwa:
        - dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
                  (confirm password)
        - 'version': WPA, WPA2, Auto,
        - 'algorithm': TKIP, AES, Auto,
        - 'auth': PSK, 802.1x, Auto, # Authentication
        Constant:
        RAS_NAS_ID = '111'
        RAS_ADDR = '192.168.0.124'
        RAS_PORT = '1863'
        RAS_SECRET = '123456'

        output:
        - Return the following keys and theirs items
            wpa_tkip_psk,  wpa_tkip_auto,  wpa_tkip_802.1x
            wpa_aes_psk,   wpa_aes_auto,   wpa_aes_802.1x
            wpa_auto_psk,  wpa_auto_auto,  wpa_auto_802.1x
            wpa2_tkip_psk, wpa2_tkip_auto, wpa2_tkip_802.1x
            wpa2_aes_psk,  wpa2_aes_auto,  wpa2_aes_802.1x
            wpa2_auto_psk, wpa2_auto_auto, wpa2_auto_802.1x
            auto_tkip_psk, auto_tkip_auto, auto_tkip_802.1x
            auto_aes_psk,  auto_aes_auto,  auto_aes_802.1x
            auto_auto_psk, auto_auto_auto, auto_auto_802.1x
        '''
        versions, algorithms = ['WPA', 'WPA2', 'Auto'], ['TKIP', 'AES', 'Auto']
        auths = ['PSK', '802.1x', 'Auto']
        '''
        #Authentication
        'auth': 'PSK', #'Authentication: PSK, 802.1x, Auto',
        'psk_passphrase': 'abcdefghijk',#'PSK passphrase',
        'cpsk_passphrase': 'abcdefghijk',#'PSK passphrase (confirm)',
        '''
        # define items for PSK authentication
        auth_psk = {
            'psk_passphrase': 'abcdefghijk',#'PSK passphrase',
            'cpsk_passphrase': 'abcdefghijk',#'PSK passphrase (confirm)',
        }

        # define items for 802.1x authentication
        auth_8021x = { #'Authentication: PSK, 802.1x, Auto',
            'radius_nas_id': RAS_NAS_ID,#'Radius NAS-ID',
            'auth_ip': RAS_ADDR,#'Authentication IP address',
            'auth_port': RAS_PORT,#'Authentication Port',
            'auth_secret': RAS_SECRET,#'Authentication Server Secret',
            'cauth_secret': RAS_SECRET,#'Authentication Server Confirm Secret',

            # Just put them here to avoid error when create a config provisioning template
            'acct_ip': ACC_ADDR,#Accounting IP address',
            'acct_port': ACC_PORT,#'Accounting Port',
            'acct_secret': ACC_SECRET, #'Accounting Server Secret',
            'cacct_secret': ACC_SECRET, #'Accounting Server Secret (confirm)'
        }

        # define items for Auto authentication
        auth_auto = dict(auth_psk)
        auth_auto.update(auth_8021x)

        # specific keys for an authentication type
        auth_items = {
            'PSK': auth_psk,
            '802.1x': auth_8021x,
            'Auto': auth_auto,
        }[auth]

        # common keys for wpa config
        cfg = {
            'encrypt_method': 'WPA',#'Disabled, WEP, WPA',
            'wpa_version': version,#'WPA version: WPA, WPA2, Auto',
            'wpa_algorithm': algorithm,#'WPA Algorithm: TKIP, AES, Auto',
            'auth': auth,
        }

        cfg.update(auth_items)

        # if this conifig is for Device View, remove some "confirm" items like:
        # 'cpsk_passphrase', 'cauth_secret', 'cacct_secret'
        if is_dv_cfg:
            removed_items = ['cpsk_passphrase', 'cacct_secret', 'cauth_secret']
            for k in removed_items:
                if k in cfg: del cfg[k]

        key_name = '%s_%s_%s' % (version.lower(), auth.lower(), algorithm.lower())

        return dict(name=key_name, cfg=cfg)


    def _generate_all_wpa_cfgs(self, is_dv_cfg=False):
        '''
        To generate all kind of configs for versions WPA, WPA2 and Auto
        kwa:
        - is_dv_cfg: False/True. If True, this config is for Device View so no return cwep_pass
                  (confirm password)
        - version: WPA, WPA2, Auto, all
        Return: List of config with format below
            [
                {key_1: cfg_1},
                {key_2: cfg_2},
                ....
            ]
        '''
        # Define config for WPA authentication
        wpa_algorithms  = ['TKIP', 'AES', 'Auto']
        wpa_auths       = ['PSK', '802.1x', 'Auto']
        wpa_versions    = ['WPA', 'WPA2', 'Auto']

        wpa_cfgs = []
        for version in wpa_versions:
            for auth in wpa_auths:
                for algor in wpa_algorithms:
                    wpa_cfgs.append(
                        self._generate_a_wpa_cfg(version, algor, auth, is_dv_cfg)
                    )

        return wpa_cfgs


    def generate_rate_limiting_cfgs(self, is_dv_cfg=False):
        '''
        Generate Rate Limiting cfgs
        kwa:
        - uplink: True if want to get this info, False if otherwise,
        - downlink: it denpends on uplink
        Output:
        - For dv_cfg = True:
            -> a list of dictionary which has no_cfg elements.
                [
                    {'uplink': '100kbps', 'downlink': '50mbps'},
                    {'uplink': '250kbps', 'downlink': '20mbps'},
                    .............
                    {'uplink': '50mbps', 'downlink': '100kbps'},
                ]
        - For dv_cfg = False:
            + Uplink = True: return a dict as below
            -> {
                    'rate_limiting': 'Enabled',
                    'uplink': a random value of a list rate limiting threshold,
                    'downlink': a symmetric value of uplink in the rate limiting threshold list,
               }
            + Uplink = False: return a dict as below with only one element
            -> {
                    'rate_limiting': 'Disabled',
               }

        '''
        rates = [
            '250kbps', '500kbps', '1mbps', '2mbps',
            '5mbps', '10mbps', '20mbps', '50mbps',
        ]
        rt_cfgs, rate_len = [], len(rates)

        for i in range(rate_len):
            cfg = {}
            if not is_dv_cfg: cfg['rate_limiting'] = 'Enabled'
            cfg.update(dict(
                uplink = rates[i],
                downlink = rates[rate_len - i - 1],
            ))
            key_name = 'rate limit' #% (cfg['uplink'], cfg['downlink'])

            rt_cfgs.append(dict(name=key_name, cfg=cfg))

        return rt_cfgs


    def get_wlan_cfgs(self,
            is_dv_cfg=False, radio_mode='2.4G', get_rate_limiting=True,
        ):
        '''
        A wlan config includes:
            general_wlan_keys + encrypt_keys + rate_limiting_keys (optional)
        . get_rate_limiting: get config keys for rate limiting or not.
        . is_dv_cfg: config for device view or config template.
        '''
        wlan_list = [1, 2, 3, 4, 5, 6, 7, 8] \
                    if radio_mode == '2.4G' else \
                    [9, 10, 11, 12, 13, 14, 15, 16]

        encrypt_list = [
            dict(name='open', cfg=dict(encrypt_method='Disabled'))
        ]
        # Get wep cfgs list
        encrypt_list.extend(self._generate_all_wep_cfgs(is_dv_cfg))
        # Get wpa cfgs list
        encrypt_list.extend(self._generate_all_wpa_cfgs(is_dv_cfg))

        # get rate limiting cfgs
        rt_cfgs = None \
                  if not get_rate_limiting or is_dv_cfg else \
                  self.generate_rate_limiting_cfgs(is_dv_cfg)

        cfgs, max_no_cfg = [], len(encrypt_list)
        for i in range(max_no_cfg):
            cfg      = copy.deepcopy(self.general_wlan_keys)
            encrypt  = encrypt_list[i % max_no_cfg]
            wlan_idx = wlan_list[i % len(wlan_list)]
            rt       = rt_cfgs[i % len(rt_cfgs)] if rt_cfgs else None

            # update commn keys
            cfg['wlan_num'] = str(wlan_idx)
            cfg['wlan_name'] = 'fm_auto_test_' + str(wlan_idx)
            cfg['wlan_ssid'] = 'fm_auto_test_' + str(wlan_idx)
            # update specific keys for authen cfg
            cfg.update(encrypt['cfg'])
            # udpate cfg for rate limiting
            if rt: cfg.update(rt['cfg'])
            # define key_name
            key_name = 'wlan %s' % wlan_idx + ', encrypt: ' + encrypt['name'] \
                       + (', ' + rt['name'] if rt else '')

            cfgs.append(dict(name=key_name, cfg={('wlan_%s' % wlan_idx):cfg}))

        return cfgs


    def get_original_wlan_cfg(self, wlan_num, is_dv_cfg=False):
        '''
        get default config for a wlan
        '''
        ori_cfg = self._get_sample_cfg('wlan_det', is_dv_cfg, True)['cfg']['wlan_det']
        ori_cfg['wlan_num'] = str(wlan_num)
        ori_cfg['wlan_name'] = "Wireless %s" % wlan_num
        ori_cfg['wlan_ssid'] = "Wireless %s" % wlan_num
        ori_cfg['encrypt_method'] = 'Disabled'

        if not is_dv_cfg: ori_cfg['rate_limiting'] = 'Disabled'

        return {'wlan_%s' % wlan_num: ori_cfg}


    def get_original_cfgs(self, cfg_keys, is_dv_cfg=False):
        '''
        . cfg_keys: a list of keys: device_general, wlan_common, wlan_1, wlan_2,...
        . return dict of a manufacturing cfgs
        '''
        ori_cfgs = {}
        for k in cfg_keys:
            no = re.search('[0-9]+', k)
            if no:
                 get_fn = self.get_original_wlan_cfg
                 params = dict(wlan_num=no.group(0), is_dv_cfg=is_dv_cfg)
            else:
                get_fn, params = dict(
                    device_general = (self.get_original_device_general_cfg, dict(is_dv_cfg=is_dv_cfg)),
                    wlan_common = (self.get_original_wlan_common_cfg, dict(is_dv_cfg=is_dv_cfg)),
                )[k]
            ori_cfgs.update(get_fn(**params))

        return ori_cfgs


class ZF2925_Cfg2(AP_Cfg2):
    '''
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg2.__init__(self)
        self.model = 'zf2925'
        # set legal values for wmode of 2942 WLAN Common
        self.legal_input_values['wlan_common'].update({
                'wmode': ['auto', '11g'], #version 8.0 has removed '11b'
        })


class ZF2942_Cfg2(AP_Cfg2):
    '''
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg2.__init__(self)
        self.model = 'zf2942'
        # set legal values for wmode of 2942 WLAN Common
        self.legal_input_values['wlan_common'].update({
                'wmode': ['auto', '11g'], #version 8.0 has removed '11b'
        })


class ZF7942_Cfg2(AP_Cfg2):
    '''
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg2.__init__(self)
        self.model = 'zf7942'
        self.legal_input_values['wlan_common'].update({
                'channel_width': ['20', '40'],
        })


class ZF7962_Cfg2(AP_Cfg2):
    '''
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg2.__init__(self)
        self.model = 'zf7962'
        # update specific 7962 items for wlan_common
        NO_CHANNELS = 165
        cfg = {
                'channel_1': ['0','1','2','3','4','5','6','7','8','9','10','11'],
                'channel_2': ['0', '36','40','44','48'],#many countrycodes don't have channels:'52','100','104','108','153','157','161','165'],
                'channel_width_1': ['20', '40'],
                'channel_width_2': ['20', '40'], #version 8.0 has removed '11b'
                'country_code': ['US', 'AT', 'CA', 'FR', 'ID', 'JP', 'TW', 'CH', 'SE', 'GB',],
                #'txpower': ['max', 'half', 'quarter', 'eighth', 'min'],
                #'prot_mode': ['Disabled', 'CTS-only', 'RTS-CTS'],

            }
        self.legal_input_values['wlan_common'].update(cfg)

        del self.legal_input_values['wlan_common']['channel']
        # Not support key txpower and prot_mode in 7962
        del self.legal_input_values['wlan_common']['txpower']
        del self.legal_input_values['wlan_common']['prot_mode']
        # dtim key is not available on 7962, remove it
        del self.legal_input_values['wlan_det']['dtim']        #
        del self.general_wlan_keys['dtim']



class ZF2741_Cfg2(AP_Cfg2):
    '''
    Temporarily, don't add utility functions for this class. Add them later if needed
    '''
    def __init__(self):
        AP_Cfg2.__init__(self)
        self.model = 'zf2741'
        self.legal_input_values['device_general']['temp_update_interval'] = [
            '40', '600', '5400' # unit: in second
        ]


# A global Model - Config map -------------------------------
# TODO: check back, do we need instances of those classes?
# OBSOLETE. Please use model_cfg_map2
model_cfg_map = {
    'zf2925': ZF2925_Cfg(),
    'zf2942': ZF2942_Cfg(),
    'zf2741': ZF2741_Cfg(),
    'zf7942': ZF7942_Cfg(),
}

model_cfg_map2 = {
    'zf2925': ZF2925_Cfg2(),
    'zf2942': ZF2942_Cfg2(),
    'zf2741': ZF2741_Cfg2(),
    'zf7942': ZF7942_Cfg2(),
    'zf7962': ZF7962_Cfg2(),
}

#==============================================================================
# These functions are to replace functions define_device_general_cfg,
# define_wlan_common_cfg
# Will make create cfg function simple asap
def define_device_general_cfg_2(model='ZF7962', ks=[]):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    Define config template for wlan common
    '''
    ap_cfg_obj = {
        'ZF2741': ZF2741_Cfg(),
        'ZF2925': ZF2925_Cfg(),
        'ZF2942': ZF2942_Cfg(),
        'ZF7942': ZF7942_Cfg(),
        'ZF7962': ZF7962_Cfg(),
    }[model.upper()]

    return ap_cfg_obj.get_device_general_cfg_tmpl(ks)

def define_wlan_common_cfg_2(
        model='ZF7962',
        ks_rd_1=['country_code', 'channel_1', 'channel_width_1'],
        ks_rd_2=['country_code', 'channel_2', 'channel_width_2']
    ):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    NOTE: Should make this function as a method of AP_Cfg object.
    Define config template for wlan common
    '''
    ap_cfg_obj = ZF7962_Cfg()

    return ap_cfg_obj.get_wlan_common_cfg_tmpl(ks_rd_1), ap_cfg_obj.get_wlan_common_cfg_tmpl(ks_rd_2)

def define_wep_cfg(model='ZF7962', wlan_rd_1=[2,4,6,8], wlan_rd_2=[10,12,14,16],
        encrypt_type=[
            'wep_open_5_ascii', 'wep_open_10_hex',
            'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
        ]
    ):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    NOTE: Should make this function as a method of AP_Cfg object.

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
    #total_cfg = {}
    # disable rate limiting, it is another story no need to verify it here.
    dal_cfg_obj.test_cfg['wlan_det']['get_rate_limiting'] = False
    # define cfg to test wep for radio 2.4GH
    idx, wep_rd_1_cfg = 0, {}
    for wlan in wlan_rd_1:
        if idx >= len(encrypt_type): idx = 0
        wep_rd_1_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(wlan_list=[wlan], encrypt_type=encrypt_type[idx])[0]
        )
        idx += 1
    #total_cfg.update(wep_rd_1_cfg)

    # define cfg to test wep for radio 5GH
    idx, wep_rd_2_cfg = 0, {}
    for wlan in wlan_rd_2:
        if idx >= len(encrypt_type): idx = 0
        wep_rd_2_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(wlan_list=[wlan], encrypt_type=encrypt_type[idx])[0]
        )
        idx += 1
    #total_cfg.update(wep_rd_2_cfg)

    #return total_cfg
    return wep_rd_1_cfg, wep_rd_2_cfg

def define_wpa_cfg(model, wlan_rd_1=[1,2,3,4,5,6,7,8], wlan_rd_2=[9,10,11,12,11,12,13,14,15,16],
        encrypt_type=[
            'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
            'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
        ]
    ):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    NOTE: Need to enhance this script to support single band model 2925, 2942...
          Should make this function as a method of AP_Cfg object.

    This function is to return two WEP cfg. One is for 2.4G, the
    other for 5G.
   - model: Currently not use this param
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
    # total_cfg = {}
    # disable rate limiting, it is another story no need to verify it here.
    dal_cfg_obj.test_cfg['wlan_det']['get_rate_limiting'] = False
    # define cfg to test wep for radio 2.4GH
    idx, wpa_rd_1_cfg = 0, {}
    for wlan in wlan_rd_1:
        if idx >= len(encrypt_type): idx = 0
        wpa_rd_1_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(wlan_list=[wlan], encrypt_type=encrypt_type[idx])[0]
        )
        idx += 1
    # total_cfg.update(wpa_rd_1_cfg)

    # define cfg to test wep for radio 2.4GH
    idx, wpa_rd_2_cfg = 0, {}
    for wlan in wlan_rd_2:
        if idx >= len(encrypt_type): idx = 0
        wpa_rd_2_cfg.update(
            # get the first element of returned list
            dal_cfg_obj.get_wlan_det_cfg_tmpl(wlan_list=[wlan], encrypt_type=encrypt_type[idx])[0]
        )
        idx += 1
    # total_cfg.update(wpa_rd_2_cfg)

    #return total_cfg
    return wpa_rd_1_cfg, wpa_rd_2_cfg

def get_ap_test_cfg_tmpl(models=['ZF7962'], radio_mode='2.4G'):
    '''
    OBSOLETE: Plz use AP_Cfg2ZF2925_Cfg
    NOTE: Currently, only support for Dalmatian (7962) only
          Should make this function as a method of AP_Cfg object.

    This function is to get a list of test cfg template for each model. It will
    return following configs for earch model.
    - models: a list of models to get test data. Ex: ['ZF2925', 'ZF2942', 'ZF7942']
    Return: a dict with structure of returned data as below
    {
        'ZF2925': [
            { # cfg for device_general
                'cfg_name': 'Device General',
                'cfg': {device_general: {test items for device_general}}
            },
            { # cfg for Wlan Common
                'cfg_name': 'Wlan Common',
                'cfg': {wlan_common: {test items for wlan_common}}
            },
            { # cfg for Wlan Detail with WEP encryptions 'wep_open_5_ascii',
              # 'wep_open_10_hex', 'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
              # for wlans 2,4,6,8
                'cfg_name': 'encryption type %s on wlans %s',
                'cfg': {
                    wlan_2: {test items for wlan_2},
                    wlan_4: {test items for wlan_2},
                    wlan_6: {test items for wlan_2},
                    wlan_8: {test items for wlan_8},
                }
            },
            { # cfg for Wlan Detail with WPA encryptions
              # 'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
              # 'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
              # for wlans 1 to 8
                'cfg_name': 'encryption type %s on wlans %s',
                'cfg': {
                    wlan_1: {test items for wlan_1},
                    wlan_2: {test items for wlan_2},
                    ....
                    wlan_8: {test items for wlan_8},
                }
            },
        ],

        'ZF2942': [
            # the same ZF2925
        ],
        ...
    }
    '''
    test_cfg, aggr_cfgs = {}, {}
    CFG_1_RD1_IDX = 0
    CFG_2_RD1_IDX = 1
    CFG_1_RD2_IDX = 2
    CFG_2_RD2_IDX = 3
    # Define test config for each model
    for model in models:
        test_cfg[model.upper()] = [
            dict(cfg_name='', cfg={}),
            dict(cfg_name='', cfg={}),
            dict(cfg_name='', cfg={}),
            dict(cfg_name='', cfg={}),
        ] # just to init number of elements of the list

        # get test config template for Device General and put it into the first element
        test_cfg[model.upper()][CFG_1_RD1_IDX] = (dict(
                cfg_name = 'Device General',
                cfg = define_device_general_cfg_2(model)
        ))
        test_cfg[model.upper()][CFG_1_RD2_IDX] = (dict(
                cfg_name = 'Device General',
                cfg = define_device_general_cfg_2(model)
        ))
        # get test config template for Wlan Common and update it into the first element too.

        cfg_rd_1, cfg_rd_2 = define_wlan_common_cfg_2(model)
        # update config for radio 2.4G
        test_cfg[model.upper()][CFG_1_RD1_IDX]['cfg_name'] += ', Wlan Common'
        test_cfg[model.upper()][CFG_1_RD1_IDX]['cfg'].update(cfg_rd_1)
        # pprint(test_cfg)
        # print '*'*40
        test_cfg[model.upper()][CFG_1_RD2_IDX]['cfg_name'] += ', Wlan Common'
        test_cfg[model.upper()][CFG_1_RD2_IDX]['cfg'].update(cfg_rd_2)
        # pprint(test_cfg)

        # get test config template for Wlan Detail WEP cfg for 2.4G and 5G
        wlan_rd_1, wlan_rd_2 = [2,4,6,8], [10,12,14,16]
        wep_encrypt_type = [
            'wep_open_5_ascii', 'wep_open_10_hex',
            'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex'
        ]
        cfg_rd_1, cfg_rd_2 = define_wep_cfg(
            model, wlan_rd_1, wlan_rd_2, wep_encrypt_type
        )

        test_cfg[model.upper()][CFG_1_RD1_IDX]['cfg_name'] +=\
         ', Encryption type %s on wlans %s' % (wep_encrypt_type, wlan_rd_1)
        test_cfg[model.upper()][CFG_1_RD1_IDX]['cfg'].update(cfg_rd_1)
        test_cfg[model.upper()][CFG_1_RD2_IDX]['cfg_name'] +=\
         ', Encryption type %s on wlans %s' % (wep_encrypt_type, wlan_rd_2)
        test_cfg[model.upper()][CFG_1_RD2_IDX]['cfg'].update(cfg_rd_2)

        # get test config template for Wlan Detail WPA cfg for radio 2.4G and 5G
        wlan_rd_1, wlan_rd_2 = [1,2,3,4,5,6,7,8], [9,10,11,12,11,12,13,14,15,16]
        wpa_encrypt_type = [
            'wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk', 'wpa_aes_802.1x',
            'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk', 'wpa2_aes_802.1x',
        ]
        cfg_rd_1, cfg_rd_2 = define_wpa_cfg(model, wlan_rd_1, wlan_rd_2, wpa_encrypt_type)

        test_cfg[model.upper()][CFG_2_RD1_IDX]['cfg_name'] =\
                'Encryption type %s on wlans %s' % (wpa_encrypt_type, wlan_rd_1)
        test_cfg[model.upper()][CFG_2_RD1_IDX]['cfg'].update(cfg_rd_1)
        test_cfg[model.upper()][CFG_2_RD2_IDX]['cfg_name'] =\
                'Encryption type %s on wlans %s' % (wpa_encrypt_type, wlan_rd_2)
        test_cfg[model.upper()][CFG_2_RD2_IDX]['cfg'].update(cfg_rd_2)

        aggr_cfgs.update({
                model.upper():
                    [test_cfg[model.upper()][CFG_1_RD1_IDX], test_cfg[model.upper()][CFG_2_RD1_IDX]]
                }\
                if radio_mode.upper() == '2.4G' else \
               {
                model.upper():
                    [test_cfg[model.upper()][CFG_1_RD2_IDX], test_cfg[model.upper()][CFG_2_RD2_IDX]]
               }
        )
    return aggr_cfgs


