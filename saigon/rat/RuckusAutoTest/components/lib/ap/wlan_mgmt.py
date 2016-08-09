import logging, copy, re
from pprint import pformat

from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import (
        Ctrl, cfgDataFlow, formatCtrl,
)

from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_cfg_value

'''
Define API function for wirless manager on AP web UI. Currently, we need get method only.
'''
# TabTmpl for wireless band 2.4G
TabTmpl = "//a[contains(@href,'/cWireless.asp?wifi=0&subp=%s')]"
# TabTmpl for wireless band 5G
TabTmpl_5G = "//a[contains(@href,'/cWireless.asp?wifi=1&subp=%s')]"
#CommonTab = TabTmpl % 'Common'
Locators = dict(
    # Link to go WLAN Common page
    # Common: %s = 'Common'
    # WLAN 1: %s = tab0
    # WLAN 2: %s = tab1
    # WLAN 3: %s = tab2
    # WLAN 4: %s = tab3
    # WLAN 5: %s = tab4
    # WLAN 6: %s = tab5
    # WLAN 7: %s = tab6
    # WLAN 8: %s = tab7
    #parent_page = "//a[contains(@href,'/cWireless.asp?wifi=0&subp=%s')]",
    #CommonTab =
    WlanTabTmpl = TabTmpl,
    WlanTabTmpl_5G = TabTmpl_5G,
    WLanCommon = dict(
        wmode = Ctrl("//select[@id='freqband']", type = 'select'),
        channel = Ctrl("//select[@id='channel']", type = 'select'),
        channel_width = Ctrl("//select[@id='channelwidth']", type = 'select'),
        country_code = Ctrl("//select[@id='countrycode']", type = 'select'),
        edit_common_btn = Ctrl("//input[@id='advancedsettings']", 'button', dict(wait=5)),
        back_link = Ctrl("//a[contains(@href, 'wireless.asp')]", 'button', dict(wait=5)),
        # need to click edit_common_btn to see value of txpower and prot_mode
        txpower = Ctrl("//select[@id='txpower']", type = 'select'),
        # In this case, key is a value of prot_mode, will consider to let it a dictionary or a list.
        prot_mode = Ctrl({
                           'disabled': "//input[@id='modeD']",
                           'cts-only': "//input[@id='modeC']",
                           'rts-cts' : "//input[@id='modeRC']",
                    }, type = 'radioGroup'),
    ),
    # Items for WLAN detail

    #'IsDeviceConnected': "//div[@id='content']",
    #'ConnectedDevicesTbl': "//div[@id='content']/table[2]",
    # Link to go to wlan 1 to 8
    #'HomePageTmpl': "//a[contains(@href,'/cWireless.asp?wifi=0&subp=tab%d')]",
    WLanDet = dict(
        # It is a link to go back after entering "Edit Threshold Setting", "Rate Limiting Setting" page
        threshold_btn = Ctrl("//input[@id='advancedsettings']", 'button', dict(wait=5)),
        ratelimiting_btn = Ctrl("//input[@id='trafficsettings']", 'button', dict(wait=5)),
        back_link = Ctrl("//a[contains(@href, 'wireless.asp')]", 'button', dict(wait=5)),
        update_btn = Ctrl("//input[@id='submit-button']", 'button', dict(wait=5)),

        avail = Ctrl({
                'disabled': "//input[@id='wireless-n']",
                'enabled': "//input[@id='wireless-y']",
               }, type = 'radioGroup'),

        broadcast_ssid = Ctrl({
                             'disabled': "//input[@id='broadcast-n']",
                             'enabled': "//input[@id='broadcast-y']",
                         }, type = 'radioGroup'),
        # This option is not available on WebUI
        #'client_isolation': {'Disabled': self.l[p_node + 'WIsolationDRd'],
        #                     'Enabled': self.l[p_node + 'WIsolationERd']},
        wlan_name = Ctrl("//input[@id='wlan-tabname']", type = 'text'),
        wlan_ssid = Ctrl("//input[@id='ssid']", type = 'text'),

        # Beacon interval, FM doesn't have this items
        beacon_int = Ctrl("//input[@id='beacon']", type = 'text'),
        dtim = Ctrl("//input[@id='dtim']", type = 'text'),
        # FM MR1 version: Removed 'frag_threshold' item
        #'frag_threshold'   : self.l[p_node + 'WFragThresTxt'], #Coi lai its locator
        rtscts_threshold = Ctrl("//input[@id='rtscts']", type = 'text'),
        # Up/Down link for rate limiting
        downlink = Ctrl("//select[@id='downlink']", type = 'select'),
        uplink = Ctrl("//select[@id='uplink']", type = 'select'),

        encrypt_method = Ctrl("//select[@id='securitymode']", type = 'select'),
        #'Open, SharedKey, Auto',
        wep_mode = Ctrl({
                       'open': "//input[@id='wep-auth-open']",
                       'sharedkey': "//input[@id='wep-auth-shared']",
                       'auto': "//input[@id='wep-auth-auto']",
                   }, type = 'radioGroup'),
        encryption_len = Ctrl("//select[@id='wepkeylen']", type = 'select'),
        # Key Entry Method
        key_entry_method = Ctrl(dict(
                               hexa = "//input[@id='keymethod-hex']",
                               ascii = "//input[@id='keymethod-ascii']",
                           ), type = 'radioGroup'),
        # Wireless 1 WEP Key Index
        wep_key_idx = Ctrl("//select[@id='defkeyidx']", type = 'select'),
        # [Checkbox loc, passphrase, passphrase (confirm)]
        wep_passphrase = Ctrl("//input[@id='weppassphrase']", type = 'text'),
        # the wep_pass is the wep_key password
        wep_pass = Ctrl("//input[@id='wepkey']", type = 'text'),
        generate_btn = Ctrl("//input[@id='generatebtn']", type = 'button'),

        #WPA Version
        wpa_version = Ctrl(dict(
                        wpa = "//input[@id='wpa-version-wpa']", #WPA
                        wpa2 = "//input[@id='wpa-version-wpa2']", #WPA2
                        auto = "//input[@id='wpa-version-auto']", #Auto
                      ), type = 'radioGroup'),
        #Authentication: PSK, 802.1x, Auto
        auth = Ctrl({
                   'psk'   : "//input[@id='wpa-auth-psk']", #PSK
                   '802.1x': "//input[@id='wpa-auth-1x']", #802.1x
                   'auto'  : "//input[@id='wpa-auth-auto']", # Auto
               }, type = 'radioGroup'),
        psk_passphrase = Ctrl("//input[@id='wpapassphrase']", type = 'text'),
        #WPA Algorithm: : TKIP, AES, Auto,
        wpa_algorithm = Ctrl(dict(
                            tkip = "//input[@id='wpa-alg-tkip']", #TKIP
                            aes = "//input[@id='wpa-alg-aes']", #AES
                            auto = "//input[@id='wpa-alg-auto']", #Auto
                        ), type = 'radioGroup'),

        radius_nas_id = Ctrl("//input[@id='wpa_nas_id']", type = 'text'),
        # Each ip textbox needs to be put in order so use list for this item
        auth_ip = Ctrl([
                    "//input[@id='auth-ip0']", # ip textbox 1
                    "//input[@id='auth-ip1']", # ip textbox 2
                    "//input[@id='auth-ip2']", # ip textbox 3
                    "//input[@id='auth-ip3']", # ip textbox 4
                  ], type = 'ipGroup'),
        auth_port = Ctrl("//input[@id='auth-port']", type = 'text'),
        auth_secret = Ctrl("//input[@id='auth-secret']", type = 'text'),
        # FM UI has the confirm item for "authentication secret" but AP WebUI doesn't have it
        cauth_secret = Ctrl("//input[@id='auth-secret']", type = 'text'),

        acct_ip = Ctrl([
                    "//input[@id='acct-ip0']",
                    "//input[@id='acct-ip1']",
                    "//input[@id='acct-ip2']",
                    "//input[@id='acct-ip3']",
                  ], type = 'ipGroup'),
        acct_port = Ctrl("//input[@id='acct-port']", type = 'text'),
        #[Checkbox loc, server secret, server secret (confirm)]
        acct_secret = Ctrl("//input[@id='acct-secret']", type = 'text'),
        # FM UI has the confirm item for "account secret" but AP WebUI doesn't have it
        cacct_secret = Ctrl("//input[@id='acct-secret']", type = 'text'),
    )
)

# CONSTANTS FOR THIS LIB
SINGLE_BAND = 0 # for normal APs like 2925, 2942, 7942
DUAL_BAND_RD_MODE_1 = 1 # Dual band AP like 7962, radio mode 2.4GHz
DUAL_BAND_RD_MODE_2 = 2 # Dual band AP like 7962, radio mode 5GHz
# Number of wlans of a radio ode for standard APs 2942, 7942..
NO_STD_WLANS = 8

def get_wlan_locs(wlan = 1):
    """
    This function is to map locator of Provisioning WLAN detail items
    wlan:
        WLAN 1 => %s = tab0
        WLAN 2 => %s = tab1
        ...
        WLAN 8 => %s = tab7
    output:
    - return locator for wlan n
    """
    tab = ['tab%d' % (i - 1) for i in range(1, 9) if wlan == i]

    return formatCtrl(Locators['WLanTmpl'], tab)

#WlanCommonOrderedCtrls = [
#    'edit_common_btn', 'txpower', 'prot_mode', 'back_link'
#]

def _get_wlan_common_ordered_items(cfg):
    '''
    This function is to set ordered item into a flow. A flow mean that to access an
    item we need to go through front item first. The reason is that there some items
    like threshod, rate limiting... only be accessible if we click a button like
    Edit Setting or Edit Common Setting button.
    Ordered items for wlan common:
        Ctrl items
            edit_common_btn
            back_link
        Items need to be in order:
            'txpower', 'prot_mode'
    kwa:
    - cfg_items: items to configure WLAN Common
    '''
    cfg_items = copy.deepcopy(cfg)

    # ordered group items
    ordered_groups = [
        # flow to access "items" can be described as:
        # 1. Click "head" to see "items"
        # 2. => See "items" for this pgae
        # 3. Click "tail" to back the main page.
        # First ordered group
        dict(
            enter = 'edit_common_btn',
            items = ['txpower', 'prot_mode'],
            exit = 'back_link',
        ),
    ]

    return cfgDataFlow(cfg_items, ordered_groups)


def _get_wlan_det_ordered_items(cfg):
    '''
    This function is to set ordered item into a flow. A flow mean that to access an
    item we need to go through front item first. The reason is that there some items
    like threshod, rate limiting... only be accessible if we click a button like
    Edit Setting or Edit Common Setting button.
    Ordered items for wlan common:
        Ctrl items
            threshold_btn
            ratelimiting_btn
            back_link
        Items need to be in order:
            beacon_int
            dtim
            rtscts_threshold
            downlink
            uplink
    kwa:
    - cfg_items: a list of items to configure WLAN Detail
    '''
    cfg_items = copy.deepcopy(cfg)
    # ordered group items
    ordered_groups = [
        # flow to access "items" can be described as:
        # 1. Click "enter" to see "items"
        # 2. => See "items" for this pgae
        # 3. Click "exit" to back the main page.
        # First group
        dict(
                enter = 'threshold_btn',
                items = ['beacon_int', 'dtim', 'rtscts_threshold'],
                exit = 'back_link',
        ),
        dict(
                enter = 'ratelimiting_btn',
                items = ['downlink', 'uplink'],
                exit = 'back_link',
        ),
    ]

    return cfgDataFlow(cfg_items, ordered_groups)


def _navigate_to_tab(ap, tab = 0, wait_time = 4.5, force = True, radio_type = SINGLE_BAND):
    '''
    This function is to each tab of wireless page
    ap: AP web UI object
    tab:
        0: Wireless Common,
        1: Wireless 1,
        2: Wireless 2,
        ...
        8: Wireless 8,
    radio_type: SINGLE_BAND | DUAL_BAND_RD_MODE_1 | DUAL_BAND_RD_MODE_2
    '''
    wireless_5g = None
    try:
        wireless_5g = ap.CONFIG_WIRELESS_5G
    except:
        pass
    main_page, wlan_tab = {
        SINGLE_BAND: (ap.CONFIG_WIRELESS, Locators['WlanTabTmpl']), # For single band AP
        DUAL_BAND_RD_MODE_1: (ap.CONFIG_WIRELESS, Locators['WlanTabTmpl']), # For dualband AP 2.4G mode
        DUAL_BAND_RD_MODE_2: (wireless_5g, Locators['WlanTabTmpl_5G']), # For dualband AP 5G mode
    }[radio_type]
    # go to Details > Wireless page
    ap.navigate_to(ap.MAIN_PAGE, main_page, force = force)
    # go to expect tab
    _tab = ['Common'] if tab == 0 else ['tab%d' % (i - 1) for i in range(1, 9) if tab == i]

    #print 'tab loc: %s' % (Locators['WlanTabTmpl'] % tuple(_tab))
    ap.selenium.click_and_wait(wlan_tab % tuple(_tab), wait_time)


def convert_key_input_wlan_common_cfg_fm_ap(cfg_ks, to_ap = True, convert_to = SINGLE_BAND):
    '''
    This function is to convert fm keys to ap keys and vice versa
    - cfg_ks: source keys to convert
    - cfg_type: type of the source keys is SINGLE_BAND or DUAL_BAND_RD_MODE_1 or
                DUAL_BAND_RD_MODE_2.
    - to_ap: + True: convert from fm keys to ap keys.
             + False: convert from ap keys to fm keys.
    '''
    #ap_ks = ['channel', 'channel_width']
    #fm_single_band_ks = ['channel', 'channel_width']
    #fm_dual_band_rd_mode_1_ks = ['channel_1', 'channel_width_2']
    #fm_dual_band_rd_mode_2_ks = ['channel_2', 'channel_width_2']

    # fm_keys <-> ap_keys
    fm_to_ap_map_ks = {
        'channel': 'channel',
        'channel_width': 'channel_width',
        'channel_1': 'channel',
        'channel_width_1': 'channel_width',
        'channel_2': 'channel',
        'channel_width_2': 'channel_width',
    }
    ap_to_fm_map_ks = {
        SINGLE_BAND: {
            'channel': 'channel',
            'channel_width': 'channel_width',
        },
        DUAL_BAND_RD_MODE_1: {
            'channel': 'channel_1',
            'channel_width': 'channel_width_1',
        },
        DUAL_BAND_RD_MODE_2: {
            'channel': 'channel_2',
            'channel_width': 'channel_width_2',
        },
    }[convert_to]

    map_ks = {
        True: fm_to_ap_map_ks,
        False: ap_to_fm_map_ks,
    }[to_ap]

    _cfg_ks = []
    for idx, cfg_k in enumerate(cfg_ks):
        if cfg_k in map_ks.keys():
            cfg_k = map_ks[cfg_k]
        _cfg_ks.append(cfg_k)

    return _cfg_ks


def convert_key_input_wlan_det_cfg_fm_ap(cfg_ks, to_ap = True):
    '''
    There are some difference between FM input config and AP config.
    E.g: item WEP on FM is maped to two items on AP:
        FM                   AP
        "64 bit 5 ascii"  -> 1. Encryption Strength: 64 bit (10 hex digits/ 5 ascii keys)
                             2. Key Entry Method:
    - cfg_ks: a list of config item keys for a wlan
    output:
    return a dictionary config of AP
    '''
    _cfg_ks = copy.deepcopy(cfg_ks)
    ap_keys = ['key_entry_method', 'encryption_len']
    fm_keys = ['encryption_len']
    # items are not available on AP web ui
    ap_unsupported_items = ['client_isolation']
    # convert FM items to AP items
    if to_ap:
        if fm_keys[0] in _cfg_ks:
            _cfg_ks.append(ap_keys[0])
        # remove un-supported items on AP
        for k in ap_unsupported_items:
            if k in _cfg_ks:_cfg_ks.remove(k)

    # convert AP items to FM items
    elif to_ap == False and ap_keys[0] in _cfg_ks:
        _cfg_ks.remove(ap_keys[0])

    return _cfg_ks


def _filter_data(raw_data, filtered_data, new_data, op):
    '''
    This function is to filter the "filtered_data" in "raw_data". If the
    raw_data has "filtered_data" by sastifying operator "op", it will remove
    "filtered_data" in "raw_data" and insert the new "new_data" into "raw_data"
    then return the updated one.
    the "new_data" data.
    - raw_data: a dictionary of items
    - filtered_data: a dictionary of items to filter
    - new_data:  a dictionary to replace for the "filtered_data".
    - op: operator for the filter. Currently, support "contain" operator only

    Output:
    return the updated one or None
    Define operator:
    - contain:
    Which following condition
        1. Keys and Values of "filtered_data" are in raw_data
        => return
    '''
    cfg = copy.deepcopy(raw_data) # to avoid manipulating the raw_data
    raw_keys = cfg.keys()
    # Becaue there are some values in "regular" format so put all values in a string
    # to use "re.match" to compare. Each elment is separated by a dot '.'
    #raw_values = string.join(cfg.values(), '.')
    raw_values = cfg.values()
    #print '-'*70
    #print 'raw_values: %s' % raw_values
    #print 'raw_keys: %s' % raw_keys
    #print 'filtered_data: %s' % filtered_data.values()
    result = {
        'contain': [filter(lambda v: v in raw_keys, filtered_data.keys()),
                    filter(lambda v: [v for item in raw_values if re.match(v, item)], filtered_data.values())],
                    # filter(lambda v: re.match(v, raw_values), filtered_data.values())
    }[op]

    #['Common'] if tab==0 else ['tab%d' %(i-1) for i in range(1,9) if tab ==i]
    #filter(lambda v: [v for item in raw_values if re.match(v, raw_values)], filtered_data.values())

    #print 'result: %s' % result
    #result[0] and result[1] and
    # after filtering if len of result is equal to len of filtered_data, it means the raw_data
    # contain the filtered_data
    if len(result[0]) == len(filtered_data) and len(result[1]) == len(filtered_data):
        # remove filtered_data items in cfg
        for k in filtered_data.iterkeys(): del cfg[k]
        # update the new_data into cfg
        cfg.update(new_data)
        print 'cfg: %s' % cfg
        return cfg

    return None

def convert_value_wlan_common_cfg_fm_ap(cfg_items, to_fm = True, convert_to = SINGLE_BAND):
    '''
    This function is to convert a cfg from AP cfg to FM cfg and vice versa.
    convert keys and values also.
    - cfg_items: a dictionary of fm items or ap items,
    - toFM: + True: Convert ap items to fm items. In this case, have to provide
                    fm keys (fm_ks). Because for dualband AP, keys of ap and fm
                    are different.
                    E.g 1:
                        ap_values = {'channel': '01', 'channel_width': '20MHz'}
                        fm_keys = ['channel_1', 'channel_width_1']
                        => fm_values = {'channel_1': '01', 'channel_width_1': '20MHz'}
                    E.g 2:
                        ap_values = {'channel': '01', 'channel_width': '20MHz'}
                        fm_keys = ['channel_2', 'channel_width_2']
                        => fm_values = {'channel_2': '01', 'channel_width_2': '20MHz'}

            + False: convert fm items to ap items
    '''
    ret_cfg = {}
    src_ks = cfg_items.keys()
    dst_ks = convert_key_input_wlan_common_cfg_fm_ap(src_ks, to_ap = False, convert_to = convert_to)\
             if to_fm else\
             convert_key_input_wlan_common_cfg_fm_ap(src_ks, to_ap = True, convert_to = convert_to)

    for idx, k in enumerate(src_ks):
            ret_cfg[dst_ks[idx]] = cfg_items[k]

    return ret_cfg

def convert_value_wlan_det_cfg_fm_ap(cfg_items, toFM = True):
    '''
    Fortunately, all values of combobox are passed by using regular expression.
    All values differences are overcomed by this way except of difference of WEP.
    So currently we only need to convert for WEP value but leave some place holder
    E.g: item WEP on FM is maped to two items on AP:
        FM (Encryption len)      AP (Key Entry Method, Encryption Strength)
        "64 bit 5 ascii"    <->  1. (ascii, 64 bit (10 hex digits/ 5 ascii keys))
        "64 bit 10 hex"     <->  2. (hex, 64 bit (10 hex digits/ 5 ascii keys))
        "128 bit 13 ascii"  <->  3. (ascii, 128 bit (26 hex digits/ 13 ascii keys))
        "128 bit 26 ascii"  <->  4. (hex, 128 bit (26 hex digits/ 13 ascii keys))

    - toFM: True/False. If True, value input cfg is AP cfg, convert it from AP values
            to FM values. Else, value cfg is FM cfg, convert from FM values to AP values
    - cfg_items: a dictionary contains key/value of wlan detail
    output:
    - Return a dictionary converted config of FM/AP if it needs to changed else return
    original config

    More info:
    AP WLAN detail config: items need to be converted on AP
        - encryption_len: ['.*64.*[bB]it.*5.*([aA]scii|ASCII).*', '.*128.*[bB]it.*13.*([aA]scii|ASCII).*']
        - key_entry_method: ['hexa', 'ascii'],

    FM WLAN detail config: items need to be converted on FM
        - encryption_len:
            '.*64.*[bB]it.*5.*([aA]scii|ASCII).*', # 64bit 5 ascii keys
            '.*64.*[bB]it.*10.*([hH]ex|HEX).*', # 64bit 10hex digits
            '.*128.*[bB]it.*13.*([aA]scii|ASCII).*', # 128bit 13 ascii keys
            '.*128.*[bB]it.*26.*([hH]ex|HEX).*', # 128bit 26 hex digits
    '''
    # note that we only use a part of string in "encryption_len" combobox
    # e.g: the full value in the combobox "64 bit (10 hex digits/ 5 ascii keys)"
    # but we only use '.*64.*[bB]it.*5.*([aA]scii|ASCII).*' for regurlar expression
    # to keep it compatible with this value from FM UI. The shortened string will
    # not cause any wrong until now
    cfg = copy.deepcopy(cfg_items)

    # a list of a pair of key/values on AP
    ap_data_list = [
        dict(
                encryption_len = '.*64.*[bB]it.*5.*([aA]scii|ASCII).*',
                key_entry_method = 'hexa',
            ),
        dict(
                encryption_len = '.*64.*[bB]it.*5.*([aA]scii|ASCII).*',
                key_entry_method = 'ascii',
            ),
        dict(
                encryption_len = '.*128.*[bB]it.*13.*([aA]scii|ASCII).*',
                key_entry_method = 'hexa',
            ),
        dict(
                encryption_len = '.*128.*[bB]it.*13.*([aA]scii|ASCII).*',
                key_entry_method = 'ascii'
            ),
    ]

    # a list of a pair of key/values on FM
    fm_data_list = [
        dict(
             encryption_len = '64 bit 10 hex digits', # 64bit 10hex digits
        ),
        dict(
             encryption_len = '64bit 5 ascii keys', # 64bit 5 ascii keys
        ),
        dict(
             encryption_len = '128bit 26 hex digits', # 128bit 26 hex digits
        ),
        dict(
             encryption_len = '128bit 13 ascii keys', # 128bit 13 ascii keys
        ),
    ]

    # items are not available on AP web ui
    ap_unsupported_items = ['client_isolation']
    # if convert cfg from FM to AP, remove unsupport items on AP
    if toFM == False:
        for k in ap_unsupported_items:
            if k in cfg: del cfg[k]

    # If toFM = True => convert from AP to FM: filtered_list is AP cfg, new_data_list is FM cfg
    # else toFM = False => convert from FM to AP: filtered_list is AP cfg, new_data_list is FM cfg
    filtered_list, new_data_list = (ap_data_list, fm_data_list) if toFM else (fm_data_list, ap_data_list)

    logging.info('Converting WLAN Detail cfg: \n%s' % pformat(cfg))
    new_cfg, msg = None, 'Nothing needs to be converted'
    for i in range(0, len(filtered_list)):
        new_cfg = _filter_data(cfg, filtered_list[i], new_data_list[i], 'contain')
        if new_cfg:
            msg = 'New cfg: \n%s' % pformat(new_cfg)
            break

    logging.info(msg)

    return new_cfg if new_cfg else cfg


def convert_value_cfg_fm_ap(cfg_items, toFM = True):
    '''
    Fortunately, all values of combobox are passed by using regular expression.
    All values differences are overcomed by this way except of difference of WEP #1.
    So currently we only need to convert for WEP value but leave some place holder
    E.g: item WEP on FM is maped to two items on AP:
        FM (Encryption len)      AP (Key Entry Method, Encryption Strength)
        "64 bit 5 ascii"    <->  1. (ascii, 64 bit (10 hex digits/ 5 ascii keys))
        "64 bit 10 hex"     <->  2. (hex, 64 bit (10 hex digits/ 5 ascii keys))
        "128 bit 13 ascii"  <->  3. (ascii, 128 bit (26 hex digits/ 13 ascii keys))
        "128 bit 26 ascii"  <->  4. (hex, 128 bit (26 hex digits/ 13 ascii keys))
    kwa:
    - toFM: True/False. If True, convert from FM values to AP values. Else convert
            from AP values to FM values
    - cfg_items: it looks like below:
        {
            'wlan_common': {
                items for wlan common
            },
            'wlan_1': {
                items for wlan 1
            },
            'wlan_2': {
                items for wlan 2
            },
            ...
        }
    Of course, if toFM = True, cfg_items is FM cfg. Else toFM = False, cfg_items is AP cfg
    output:
    return a dictionary config of FM/AP
    '''
    cfg = copy.deepcopy(cfg_items)
    for k in cfg.iterkeys():
        converted_cfg = {
            #'wlan_common': place holder,
            'wlan_1': convert_value_wlan_det_cfg_fm_ap,
            'wlan_2': convert_value_wlan_det_cfg_fm_ap,
            'wlan_3': convert_value_wlan_det_cfg_fm_ap,
            'wlan_4': convert_value_wlan_det_cfg_fm_ap,
            'wlan_5': convert_value_wlan_det_cfg_fm_ap,
            'wlan_6': convert_value_wlan_det_cfg_fm_ap,
            'wlan_7': convert_value_wlan_det_cfg_fm_ap,
            'wlan_8': convert_value_wlan_det_cfg_fm_ap,
        }[k](cfg_items[k], toFM)

        cfg[k] = converted_cfg

    return cfg

def get_wlan_common(ap, cfg_ks, fm_return = True, fm_key = False, radio_type = SINGLE_BAND):
    return getWLANCommon(ap, cfg_ks, fm_return = fm_return, fm_key = fm_key, radio_type = radio_type)

def getWLANCommon(ap, cfg_ks, fm_return = True, fm_key = False, radio_type = SINGLE_BAND):
    '''
    Note: Obsoleted interface. Plz use get_wlan_common instead.
    This function is to get value of config items of WLAN Common page.
    input:
    - ap: ap web ui object
    - cfg_ks: list of items to get values
    - fm_return: a place holder. There is no difference between AP and
                 FM UI for the WLAN Common now.
    - fm_key: look at getWLAN for its meaning
    - radio_type: refer to getWLAN
    Output:
    - return a dictionary result
    '''
    if fm_key:
        cfg_ks = convert_key_input_wlan_common_cfg_fm_ap(cfg_ks, to_ap = True, convert_to = radio_type)

    s, ordered_list, loc = ap.selenium, _get_wlan_common_ordered_items(cfg_ks), Locators['WLanCommon']

    logging.info('Get Wireless Common Config')
    _navigate_to_tab(ap, tab = 0, force = True, radio_type = radio_type)
    cfg = ac.get(s, loc, cfg_ks, ordered_list)
    # if fm_retrurn = True, we will return the output in input simple cfg
    if fm_return:
        converted_cfg = convert_value_wlan_common_cfg_fm_ap(cfg, fm_return, radio_type)
        if converted_cfg: cfg = map_cfg_value(converted_cfg, toSelect = False)

    return cfg

def get_wlan_detail(ap, wlan, cfg_ks, fm_return = True, fm_key = False, radio_type = SINGLE_BAND):
    return getWLAN(ap, wlan, cfg_ks, fm_return = fm_return, fm_key = fm_key, radio_type = radio_type)

def getWLAN(ap, wlan, cfg_ks, fm_return = True, fm_key = False, radio_type = SINGLE_BAND):
    '''
    Note: Obsoleted interface. Plz use get_wlan_detail instead.
    This function is to get value of config items of WLAN Detail page.
    IMPORTANT NOTE:
          Before calling this function, plz make sure that you are
          using keys of AP > Wlan Detail not keys of FM > Wlan Detail.
          It is due to wlan detail of AP and FM has a few of differences
          and we must convert from FM wlan detail keys to AP wlan detail keys.
    Input:
    - ap: AP web ui object
    - wlan: wlan to get cfg: 1, 2,..., 8 (16 for dualband ap).
      NOTE: With dualband aps like 7962 model, it has 16 wlans from wlan 1 to 16. It
            is organized as below:
            1. 8 first wlans belong to radio 1 (2.4G), their tab locator look like
                //a[contains(@href,'/cWireless.asp?wifi=0&subp=WLAN_ID')]
                WLAN_ID value is from 0 to 7.

            2. 8 second wlans belong to radio 2 (5G), their tab locator look like
                //a[contains(@href,'/cWireless.asp?wifi=1&subp=WLAN_ID')]
                WLAN_ID value is also from 0 to 7.

            => Only their wifi value is different. Hence, to navigate to wlans of
            radio 2 (5G), we simply do as below to identify wlan tab.
                if wlan > 8:
                    wlan = wlan - 8

    - cfg_ks: list of items to get values
    - fm_return: return in FM config
    - fm_key: True if cfg_ks are keys for fm. False if cfg_ks are keys for AP.
              NOTE: Because fm keys have some keys which are different from AP
                    keys so this param to support that if user pass keys of fm
                    it will help to convert to ap keys
    - radio_type: This param has following values:
                  SINGLE_BAND: if ap is normal aps like 2942, 7942, 2925
                  DUAL_BAND_RD_MODE_1: if ap is dualband ap like 7962 and its radio is 2.4G
                  DUAL_BAND_RD_MODE_2: if ap is dualband ap like 7962 and its radio is 5G
    Output:
    - return a dictionary result
    '''
    s, _cfg_ks = ap.selenium, copy.deepcopy(cfg_ks)
    logging.info('Get Config of Wireless %d' % wlan)
    if fm_key:
        _cfg_ks = convert_key_input_wlan_det_cfg_fm_ap(_cfg_ks, to_ap = True)

    ordered_list, loc = _get_wlan_det_ordered_items(_cfg_ks), Locators['WLanDet'] #

    # NOTE: sometimes, an strange error happens. After navigating to a wlan successfully,
    # click an "Edit" button to get sub-item, somehow it goes to a sub-item of
    # wlan common not wlan detail. Hence, increase a sleep time here to avoid the error

    # Enhance to support wlan 9 to 16. Recaculat wlan tab idx if wlan > 8
    if wlan > NO_STD_WLANS: wlan = wlan - NO_STD_WLANS

    _navigate_to_tab(ap, tab = wlan, force = True, radio_type = radio_type)
    cfg = ac.get(s, loc, _cfg_ks, ordered_list)
    if fm_return:
        converted_cfg = convert_value_wlan_det_cfg_fm_ap(cfg, toFM = True)
        cfg = map_cfg_value(converted_cfg, toSelect = False)

    return cfg


def getWLANDet(ap, cfg, fm_return = True, fm_key = False, radio_type = SINGLE_BAND):
    '''
    This function is to make back compatibilty with old cfg. The old cfg from
    libFM_TestSuite. The old cfg has wlan_num "item" to identify which wlan.
    Actually, it is a redundant item. Temporarily, let it there. Clean it up
    later.
    Input:
    - ap: device view object
    - cfg: a dictionary of items to get values
    - fm_key: look at getWLAN for its meaning
    - radio_type: refer to getWLAN
    Output:
    - return a dictionary result
    '''
    _cfg = copy.deepcopy(cfg)
    wlan = int(_cfg.pop('wlan_num'))
    cfg_ks = convert_key_input_wlan_det_cfg_fm_ap(_cfg.keys(), to_ap = True)
    return getWLAN(ap, wlan, cfg_ks, fm_return, radio_type)


def get_country_codes(ap, radio_type = SINGLE_BAND):
    '''
    This function is to get all country code of a radio
    - radio_type:
        1. SINGLE_BAND: Single band APs like 2942, 2925, 7942, radio mode 2.4G
        2. DUAL_BAND_RD_MODE_1: Dualband AP like 7962, radio mode 2.4G
        3. DUAL_BAND_RD_MODE_1: Dualband AP like 7962, radio mode 5G
    return:
    - a list of all country codes
    '''
    s, l = ap.selenium, Locators

    _navigate_to_tab(ap, tab = 0, force = True, radio_type = radio_type)

    return s.get_all_options(l['WLanCommon']['country_code'].loc)

def get_channels(ap, radio_type = SINGLE_BAND):
    '''
    This function is to get all channel of a radio
    - radio_type: SINGLE_BAND --> 2.4G
                 WIRELESS_5_G --> 5G
    return:
    - a list of all country codes
    '''
    s, l = ap.selenium, Locators

    _navigate_to_tab(ap, tab = 0, force = True, radio_type = radio_type)

    return s.get_all_options(l['WLanCommon']['channel'].loc)

def get(ap, cfg_ks, fm_return = True, fm_key = False, radio_type = SINGLE_BAND):
    '''
    This function is to get config of wlan common and wlan 1 to 16.
    Input:
    - dv: Device View instance
    - cfg_ks: a dictionary as below:
        {
            'wlan_common': [list of keys to get from Wlan Common],
            'wlan_1': [list of keys to get from Wlan 1],
            'wlan_2': [list of keys to get from Wlan 2],
            ....
            'wlan_16': [list of keys to get from Wlan 16],
        }
    '''
    ret_cfg, _cfg_ks = {}, copy.deepcopy(cfg_ks)

    for item, ks in _cfg_ks.iteritems():
        data = {}
        if 'wlan_common' == item:
            data = get_wlan_common(
                        ap, ks, fm_return = fm_return, fm_key = fm_key, radio_type = radio_type
                   )
        else:
            wlan = int(re.search('\d+', item).group(0))
            if 'wlan_num' in ks: ks.remove('wlan_num')
            data = get_wlan_detail(
                        ap, wlan, ks, fm_return = fm_return, fm_key = fm_key, radio_type = radio_type
                   )
        ret_cfg[item] = data

    return ret_cfg

