import logging
import copy
import re
from pprint import pformat

from RuckusAutoTest.common.utils import log_cfg
from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import (
        Ctrl, cfgDataFlow, formatCtrl,
)
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_cfg_value


TabTmpl = "//div[@dojoinsertionindex='%s']"
CommonTab = TabTmpl % '0'

Locators = {
    'WlanTabTmpl': TabTmpl + "//span[1]",

    'WLanCommon': {
        'tab'         : CommonTab,
        'wmode'       : Ctrl(CommonTab + "//select[contains(@id, 'Standard')]", type = 'select'),
        'channel'     : Ctrl(CommonTab + "//select[contains(@id, 'Channel')]", type = 'select'),
        'channel_width': Ctrl(CommonTab + "//select[@name='X_001392_ChannelWidth']", type = 'select'),
        'country_code': Ctrl(CommonTab + "//select[contains(@id, 'RegulatoryDomain')]", type = 'select'),
        'txpower'     : Ctrl(CommonTab + "//select[contains(@name, 'X_001392_TxPwr')]", type = 'select'),
        'prot_mode'   : Ctrl(
            { 'disabled': CommonTab + "//input[@name='X_001392_ProtMode' and @value='none']",
              'cts-only': CommonTab + "//input[@name='X_001392_ProtMode' and @value='cts-only']",
              'rts-cts':  CommonTab + "//input[@name='X_001392_ProtMode' and @value='rts-cts']",
            }, type = 'radioGroup'),

        # locator for DualBand APs: 7962
        'channel_1'     : Ctrl(CommonTab + "//select[contains(@id, 'Channel')]", type = 'select'),
        'channel_width_1': Ctrl(CommonTab + "//select[@name='X_001392_ChannelWidth']", type = 'select'),
        'channel_2'     : Ctrl(CommonTab + "//select[contains(@id, 'Channel')]", type = 'select'),
        'channel_width_2': Ctrl(CommonTab + "//select[@name='X_001392_ChannelWidth']", type = 'select'),

        'edit_btn'    : Ctrl(CommonTab + "//div[@class='dojoButton' and div='Edit Settings']", type = 'button'),
        'back_btn'    : Ctrl(CommonTab + "//div[@class='dojoButton' and div='Back']", type = 'button'),
        'submit_btn'  : Ctrl(CommonTab + "//div[@class='dojoButton' and div='Submit']", type = 'button'),
        'reset_btn'   : Ctrl(CommonTab + "//div[@class='dojoButton' and div='Reset']", type = 'button'),
    },

    # NOTE: get the WLan specific locs from getWLanLoc()
    'WLanTmpl': {
        'edit_btn'    : Ctrl(TabTmpl + "//div[@class='dojoButton' and div='Edit Settings']", type = 'button'),
        'back_btn'    : Ctrl(TabTmpl + "//div[@class='dojoButton' and div='Back']", type = 'button'),
        'submit_btn'  : Ctrl(TabTmpl + "//div[@class='dojoButton' and div='Submit']", type = 'button'),
        'reset_btn'   : Ctrl(TabTmpl + "//div[@class='dojoButton' and div='Reset']", type = 'button'),

        'avail': Ctrl(
            { 'disabled': TabTmpl + "//input[@name='Enable' and @value='Disabled']",
              'enabled' : TabTmpl + "//input[@name='Enable' and @value='Enabled']",
            }, type = 'radioGroup'),
        'broadcast_ssid': Ctrl(
            { 'disabled': TabTmpl + "//input[@name='BeaconAdvertisementEnabled' and @value='Disabled']",
              'enabled' : TabTmpl + "//input[@name='BeaconAdvertisementEnabled' and @value='Enabled']",
            }, type = 'radioGroup'),
        'client_isolation'  : Ctrl(
            { 'disabled': TabTmpl + "//input[@name='X_001392_ClientIsolation' and @value='Disabled']",
              'enabled' : TabTmpl + "//input[@name='X_001392_ClientIsolation' and @value='Enabled']",
            }, type = 'radioGroup'),
        'wlan_name': Ctrl(TabTmpl + "//input[@name='X_001392_NAME']"),
        'wlan_ssid': Ctrl(TabTmpl + "//input[@name='SSID']"),
        'dtim'     : Ctrl(TabTmpl + "//input[@name='X_001392_DtimPeriod']"),
        # FM MR1 version: Removed 'frag_threshold' item
        #'frag_threshold': [TabTmpl + loc['WFragThresChk'], TabTmpl + loc['WFragThresTxt'],
        #                   TabTmpl + loc['WFragThresErrMsg']], #Coi lai its locator
        'rtscts_threshold': Ctrl(TabTmpl + "//input[@name='X_001392_RTSThresh']"),

        'encrypt_method': Ctrl(
            { 'disabled': TabTmpl + "//input[@name='X_001392_EncryptionMethod' and @value='Disabled']",
              'wep'     : TabTmpl + "//input[@name='X_001392_EncryptionMethod' and @value='WEP']",
              'wpa'     : TabTmpl + "//input[@name='X_001392_EncryptionMethod' and @value='WPA']",
            }, type = 'radioGroup'),
        'wep_mode': Ctrl(
            { 'auto'     : TabTmpl + "//input[@name='BasicAuthenticationMode' and @value='AUTO']",
              'open'     : TabTmpl + "//input[@name='BasicAuthenticationMode' and @value='OPEN']",
              'sharedkey': TabTmpl + "//input[@name='BasicAuthenticationMode' and @value='Shared Key']",
            }, type = 'radioGroup'),
        'encryption_len': Ctrl(TabTmpl + "//select[@name='WepEncryptionLevel']", type = 'select'),
        'wep_key_idx'   : Ctrl(TabTmpl + "//select[@name='WepKeyIndex']", type = 'select'),
        'wep_pass'      : Ctrl(TabTmpl + "//input[@name='WEPKey']"),
        'wpa_version': Ctrl(
            { 'wpa' : TabTmpl + "//input[@name='X_001392_WPAVersion' and @value='WPA']",
              'wpa2': TabTmpl + "//input[@name='X_001392_WPAVersion' and @value='WPA2']",
              'auto': TabTmpl + "//input[@name='X_001392_WPAVersion' and @value='WPA-AUTO']",
            }, type = 'radioGroup'),
        'wpa_algorithm': Ctrl(
            { 'auto': TabTmpl + "//input[@name='X_001392_WPAAlgorithm' and @value='AUTO']",
              'tkip': TabTmpl + "//input[@name='X_001392_WPAAlgorithm' and @value='TKIP']",
              'aes' : TabTmpl + "//input[@name='X_001392_WPAAlgorithm' and @value='AES']",
            }, type = 'radioGroup'),
        'auth': Ctrl(
            { 'auto'  : TabTmpl + "//input[@name='X_001392_WPAAuthentication' and @value='AUTO']",
              'psk'   : TabTmpl + "//input[@name='X_001392_WPAAuthentication' and @value='PSK']",
              '802.1x': TabTmpl + "//input[@name='X_001392_WPAAuthentication' and @value='802.1x']",
            }, type = 'radioGroup'),
        'psk_passphrase': Ctrl(TabTmpl + "//input[@name='X_001392_WPAPassphrase']"),
        'radius_nas_id': Ctrl(TabTmpl + "//input[@name='X_001392_8021XNAS_ID']"),
        'auth_ip'      : Ctrl(TabTmpl + "//input[@name='X_001392_8021XAuthServerIP']"),
        'auth_port'    : Ctrl(TabTmpl + "//input[@name='X_001392_8021XAuthServerPort']"),
        'auth_secret'  : Ctrl(TabTmpl + "//input[@name='X_001392_8021XAuthServerSecret']"),
        'acct_ip'      : Ctrl(TabTmpl + "//input[@name='X_001392_8021XAcctServerIP']"),
        'acct_port'    : Ctrl(TabTmpl + "//input[@name='X_001392_8021XAcctServerPort']"),
        'acct_secret'  : Ctrl(TabTmpl + "//input[@name='X_001392_8021XAcctServerSecret']"),
    },
}


WLanOrderedCtrls = [
    dict(
        enter = 'encrypt_method',
        items = [
            'wep_mode', 'encryption_len', 'wep_key_idx', 'wep_pass'
        ],
        exit = '',
    ),
    dict(
        enter = 'encrypt_method',
        items = [
            'wpa_version', 'wpa_algorithm', 'auth', 'psk_passphrase',
            'radius_nas_id', 'auth_ip', 'auth_port', 'auth_secret', 'acct_ip', 'acct_port',
            'acct_secret',
        ],
        exit = '',
    ),
]
# Constant for Wireless Radio 1 and Wireless Radio 2
RADIO_MODE_1 = 1 # 2.4GHz
RADIO_MODE_2 = 2 # 5GHz
# total wlans of a radio mode
TOTAL_WLANS = 8

def get_wlan_locs(wlan = 1):
    """
    This function is to map locator of Provisioning WLAN detail items
    wlan:
        0: Wireless Common,
        1: Wireless 1,
        ...
        8: Wireless 8,
    output:
    - return locator for wlan n
    """
    return formatCtrl(Locators['WLanTmpl'], [wlan])


def _navigate_to_tab(dv, tab = 0, wait_time = 1.5, force = False, radio_mode = RADIO_MODE_1):
    '''
    This function is to each tab of wireless page
    dv: Device View object
    tab:
        0: Wireless Common,
        1: Wireless 1,
        ...
        8: Wireless 8,
    '''
    # go to Details > Wireless page
    wlan_link = {
        RADIO_MODE_1: dv.DETAILS_WIRELESS,
        RADIO_MODE_2: dv.DETAILS_WIRELESS_RD_2,
    }[radio_mode]
    dv.navigate_to(dv.DETAILS, wlan_link, force = force)
    # go to expect tab
    dv.selenium.click_and_wait(Locators['WlanTabTmpl'] % tab, wait_time)

def set_wlan_common(dv, cfg, radio_mode = RADIO_MODE_1):
    return cfgWLANCommon(dv, cfg, radio_mode)

def cfgWLANCommon(dv, cfg, radio_mode=RADIO_MODE_1, timeout=900):
    """
    Note: Osoleted interface. Plz use cfgWLANCommon instead.
    This function is to fill WLAN Common from from items provided "kwa". It only fills
    items which are provided in kwa, ignore missed items.
    Input:
    - dv: device view instance
    - kwa: keyword argument
    cfg_items: a dictionary. It may contain information as below
        {
            'wmode': 'auto, g, b',
            'channel': 'value from 0 to 11; 0: smartselect, 1: channel 1...',
            'country_code': 'AU, AT, ...',
            'txpower': 'max, half, quarter, eighth, min',
            'prot_mode': 'Disabled, CTS-only, RTS-CTS'
        }
    Output:
    It raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.
    """
    cfg_items = copy.deepcopy(cfg)
    logging.info('Configuring Wireless Common')
    log_cfg(cfg)

    s, loc = dv.selenium, Locators['WLanCommon']
    _navigate_to_tab(dv, tab = 0, force = True, radio_mode = radio_mode)
    #s.click_and_wait(loc['edit_btn'])

    ac.set(s, loc, map_cfg_value(cfg_items), ['edit_btn'] + cfg.keys() + ['submit_btn'])
    #s.click_and_wait(loc['submit_btn'])

    return dv.get_task_status(dv.get_task_id(), timeout)

def set_wlan_detail(dv, cfg, radio_mode = RADIO_MODE_1):
    return cfgWLANDet(dv, cfg, radio_mode)

def cfgWLANDet(dv, cfg, radio_mode=RADIO_MODE_1, timeout=900):
    '''
    Note: Obsolete this interface, plz use set_wlan_detail instead.
    This function is to fill WLAN Detail form. It only fills items which are provided
    in kwa, ignore missed items.
    Input:
    dv: Device View instance object
    kwa: a dictionary. It may contain information as below
    - cfg_items:
        1. {
            'wlan_num': 'Detail configuration for wlan_num (from 1 to 8)',
            'avail': 'Disabled, Enabled',
            'broadcast_ssid': 'Disabled, Enabled',
            'client_isolation': 'Disabled, Enabled',
            'wlan_name': 'name of wlan',
            'wlan_ssid': 'name of ssid',
            'dtim': 'Data beacon rate (1-255)',
            # FM MR1 version: Removed 'frag_threshold' item
            #'frag_threshold': 'Fragment Threshold (245-2346',
            'rtscts_threshold': 'RTS / CTS Threshold (245-2346',

            'wep_mode': 'Open, SharedKey, Auto',
            'encryption_len': 'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
            #Wireless 1 WEP Key Index
            'wep_key_idx': 'key index: 1, 2, 3, 4',
            #WEP key password
            'wep_pass': 'password of wep method',
            # confirm textbox is not available on configuration from Device View
            # 'cwep_pass': ' password of wep method (confirm)',

            #WPA Version
            'wpa_version': 'WPA version: WPA, WPA2, Auto',
            #WPA Algorithm
            'wpa_algorithm': 'WPA Algorithm: TKIP, AES, Auto',
            #Authentication
            'auth': 'Authentication: PSK, 802.1x, Auto',
            'psk_passphrase': 'PSK passphrase',
            # confirm textbox is not available on configuration from Device View
            # 'cpsk_passphrase': 'PSK passphrase (confirm)',
            'radius_nas_id': 'Radius NAS-ID',
            'auth_ip': 'Authentication IP address',
            'auth_port': 'Authentication Port',
            'auth_secret': 'Authentication Server Secret',
            # confirm textbox is not available on configuration from Device View
            # 'cauth_secret': 'Authentication Server Secret',
            'acct_ip': 'Accounting IP address',
            'acct_port': 'Accounting Port',
            'acct_secret': 'Accounting Server Secret',
            # confirm textbox is not available on configuration from Device View
            # 'cacct_secret': 'Accounting Server Secret (confirm)'
           }
    Output:
    It raises Exception if any error happens. Otherwise, the WLAN Detail form is filled completely.
    '''
    cfg_items = copy.deepcopy(cfg)
    # get and remove the wlan_num items. Need to remove this item
    # before call "set" function in AutoConfig because this item
    # is not a config item
    wlan = int(cfg_items.pop('wlan_num'))
    # Calculate tab for the wlan respectively
    tab = wlan if wlan <= TOTAL_WLANS else wlan - TOTAL_WLANS
    s, ordered_list, loc = dv.selenium, cfgDataFlow(cfg_items.keys(), WLanOrderedCtrls), get_wlan_locs(tab)

    logging.info('Configuring Wireless %d. Config: %s' % (wlan, pformat(cfg)))

    _navigate_to_tab(dv, tab = tab, force = True, radio_mode = radio_mode)
    ac.set(s, loc, map_cfg_value(cfg_items), ['edit_btn'] + ordered_list)
    s.click_and_wait(loc['submit_btn'].loc)

    # Sometimes got timeout error, increate task timeout
    return dv.get_task_status(dv.get_task_id(), timeout)


def cfgWLAN(dv, wlan, cfg, radio_mode = RADIO_MODE_1):
    cfg.update(dict(wlan_num = wlan))
    return cfgWLANDet(dv, cfg, radio_mode)

def set(dv, cfg, radio_mode = RADIO_MODE_1):
    '''
    This function is to config all things: wlan_common, wlan_1, wlan_2, ..., wlan_16.
    '''
    return cfgAll(dv, cfg, radio_mode)

def remove_unsupported_keys(ks):
    '''
    Unsupported
    '''

def get(dv, cfg_ks, radio_mode = RADIO_MODE_1):
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
    ret_cfg = {}
    for item, ks in cfg_ks.iteritems():
        data = None
        if 'wlan_common' == item:
            data = get_wlan_common(dv, ks, radio_mode)
        else:
            wlan = int(re.search('\d+', item).group(0))
            if 'wlan_num' in ks: ks.remove('wlan_num')
            data = get_wlan_detail(dv, wlan, ks, radio_mode)

        ret_cfg[item] = data

    return ret_cfg


def cfgAll(dv, cfg, radio_mode = RADIO_MODE_1):
    '''
    NOTE: obsoleted interface. Plz use set_all instead.
    This function is to config all things: wlan_common, wlan_1, wlan_2, ..., wlan_8.
    - cfg: a dictionary as below:
        'wlan_common':{
        },
        'wlan_1': {
        },
        ...
        'wlan_8': {
        },
    '''
    for k, v in cfg.iteritems():
        cfg_fn = set_wlan_common if 'wlan_common' == k else set_wlan_detail
        ret, msg = cfg_fn(dv, v, radio_mode)
        if dv.TASK_STATUS_SUCCESS != ret:
            logging.info('Fail to config %s. Error: %s' % (k, v))
            return False

    return True

def get_wlan_common(dv, cfg_ks, radio_mode = RADIO_MODE_1):
    return getWLANCommon(dv, cfg_ks, radio_mode)

def getWLANCommon(dv, cfgKs, radio_mode = RADIO_MODE_1):
    '''
    Note: Obsoleted interface. Plz use get_wlan_common instead.
    This function is to get value of config items of WLAN Common page.
    input:
    - dv: device view object
    - cfgKs: list of items to get values
    Output:
    - return a dictionary result
    '''
    s, loc = dv.selenium, Locators['WLanCommon']

    logging.info('Get Wireless Common Config')
    _navigate_to_tab(dv, tab = 0, radio_mode = radio_mode)
    #s.click_and_wait(loc['edit_btn'])
    cfg = ac.get(s, loc, cfgKs, ['edit_btn'] + cfgKs)

    return map_cfg_value(cfg, False)

def get_wlan_detail(dv, wlan, cfg_ks, radio_mode = RADIO_MODE_1):
    return getWLAN(dv, wlan, cfg_ks, radio_mode)

def getWLAN(dv, wlan, cfgKs, radio_mode = RADIO_MODE_1):
    '''
    Note: Obsoleted interface. Plz use get_wlan_detail instead.
    This function is to get value of config items of WLAN Detail page.
    Input:
    - dv: device view object
    - wlan: wlan to get cfg: 1, 2,..., 8.
    - cfgKs: list of items to get values
    Output:
    - return a dictionary result
    '''
    s = dv.selenium
    logging.info('Get Wireless %s config' % wlan)
    # Calculate tab for the this wlan respectively
    if radio_mode == RADIO_MODE_1 and wlan > TOTAL_WLANS:
        raise Exception('Invalid wlan %s for Radio mode 2.4G' % wlan)

    if radio_mode == RADIO_MODE_2 and wlan <= TOTAL_WLANS:
        raise Exception('Invalid wlan %s for Radio mode 5G' % wlan)

    tab = wlan if wlan <= TOTAL_WLANS else wlan - TOTAL_WLANS
    ordered_list, loc = cfgDataFlow(cfgKs, WLanOrderedCtrls), get_wlan_locs(tab)

    _navigate_to_tab(dv, tab = tab, radio_mode = radio_mode)
    #s.click_and_wait(loc['edit_btn'])
    cfg = ac.get(s, loc, cfgKs, ['edit_btn'] + cfgKs)

    return map_cfg_value(cfg, False)

def get_wlan_detail_2(dv, cfg_ks, radio_mode = RADIO_MODE_1):
    '''
    This function is to get wlan detail of wlan 1 to 16.
    '''
    return getWLANDet(dv, cfg_ks, radio_mode)

def getWLANDet(dv, cfg, radio_mode = RADIO_MODE_1):
    '''
    Note: Obsoleted interface. Plz use get_wlan_detail_2 instead.
    This function is to make back compatibilty with old cfg. The old cfg from
    libFM_TestSuite. The old cfg has wlan_num "item" to identify which wlan.
    Actually, it is a redundant item. Temporarily, let it there. Clean it up
    later.
    Input:
    - dv: device view object
    - cfg: a dictionary of items to get values (it includes wlan_num key)
    Output:
    - return a dictionary result
    '''
    _cfg = copy.deepcopy(cfg)
    wlan = int(_cfg.pop('wlan_num'))
    cfgKs = _cfg.keys()

    return getWLAN(dv, wlan, cfgKs, radio_mode)

def get_country_codes(dv, radio_mode = RADIO_MODE_1):
    '''
    This function is to get all country code in the combo box
    '''
    s, l = dv.selenium, Locators
    unused_items = ['Keep current country settings']

    _navigate_to_tab(dv, tab = 0, force = True, radio_mode = radio_mode)
    s.click_and_wait(l['WLanCommon']['edit_btn'].loc)
    country_codes = s.get_all_options(l['WLanCommon']['country_code'].loc)

    # remove unused items in the list
    for k in unused_items:
        try:
            country_codes.remove(k)
        except Exception:
            pass

    return country_codes

def get_channels(dv, radio_mode = RADIO_MODE_1):
    '''
    This function is to get all country code in the combo box
    '''
    s, l = dv.selenium, Locators
    _navigate_to_tab(dv, tab = 0, force = True, radio_mode = radio_mode)
    s.click_and_wait(l['WLanCommon']['edit_btn'].loc)

    return s.get_all_options(l['WLanCommon']['channel'].loc)

