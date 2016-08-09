'''
This module is to provide utility functionality for Device Registration page. It
includes Registration Status and Auto Configuration Setup
'''
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_cfg_value
from RuckusAutoTest.common.utils import *
from RuckusAutoTest.common.Ratutils import get_random_int
from RuckusAutoTest.common.excelwrapper import readexcel
import re

Locators = dict(
    tmpl_tbl = Ctrl(
        dict(
            tbl = "//table[@id='Templatelist']",
            nav = "//td[contains(preceding-sibling::td, 'Number of templates')]/table",
        ),
        type = 'ltable',
        cfg = dict(
            hdrs = [
                'template_name', 'created_by', 'created_time', 'model', 'actions'
            ],
            #get = 'iter',
            links = dict(
                view = "//a[contains(.,'View')]",
                edit = "//a[contains(.,'Edit')]",
                delete = "//a[contains(.,'Delete')]",
                copy = "//a[contains(.,'Copy')]",
                export = "//a[contains(.,'Export')]",
            ),
        ),
    ),
    create_new_tmpl = Ctrl(loc = "//div[@id='new-template']/span", type = 'button'),
    new_tmpl_name = Ctrl("//input[@id='newtemplatename']", type = 'text'),
    copy_btn = Ctrl("//input[@id='copy-ok']", type = 'button'),
    cancel_btn = Ctrl("//input[@id='copy-cancel']", type = 'button'),

    cfg_param_tbl = Ctrl("//table[@id='plist']", type = 'htable', cfg = dict(hdrs = [], ignore_case = True)),
    view_tmpl_name = Ctrl("//span[@id='sp-tname']/font[1]", type = 'html'),
    view_persist = Ctrl("//span[@id='sp-tname']/font[2]", type = 'html'),

    # common locator for config tmpl
    form_title = Ctrl("//span[@id='group-name']", type = 'html'),
    template_name = Ctrl("//input[@id='templatename']", "text"),
    product_type = Ctrl(loc = "//select[@id='select-profilelist']", type = 'select'),
    # List check boxes to select cfg in the tempalte
    device_general = Ctrl(loc = "//input[@id='group-0']", type = "check"),
    internet = Ctrl(loc = "//input[@id='group-1']", type = "check"),
    wlan_common = Ctrl(loc = "//input[@id='group-2']", type = "check"),
    wlan_1 = Ctrl(loc = "//input[@id='group-3']", type = "check"),
    wlan_2 = Ctrl(loc = "//input[@id='group-4']", type = "check"),
    wlan_3 = Ctrl(loc = "//input[@id='group-5']", type = "check"),
    wlan_4 = Ctrl(loc = "//input[@id='group-6']", type = "check"),
    wlan_5 = Ctrl(loc = "//input[@id='group-7']", type = "check"),
    wlan_6 = Ctrl(loc = "//input[@id='group-8']", type = "check"),
    wlan_7 = Ctrl(loc = "//input[@id='group-9']", type = "check"),
    wlan_8 = Ctrl(loc = "//input[@id='group-10']", type = "check"),
    mgmt = Ctrl(loc = "//input[@id='group-11']", type = "check"),
    dev_reg_settings = Ctrl(loc = "//input[@id='group-12']", type = "check"),
    vlan_setting = Ctrl(loc = "//input[@id='group-13']", type = "check"),
    # locators for Device General Form
    device_name = Ctrl(loc = "//input[@id='device.name']", type = 'text'),
    device_name_chk = Ctrl(loc = "//input[@id='check-device.name']", type = 'check'),

    temp_update_interval = Ctrl(
        loc = "//input[@id='device.temperatureInterval_value']", type = 'text'
    ), # for ZF2741 only
    temp_update_interval_chk = Ctrl(
        loc = "//input[@id='check-device.temperatureInterval']", type = 'check'
    ), # for ZF2741 only
    temp_update_interval_unit = Ctrl(
        loc = "//select[@id='device.temperatureInterval_unit']", type = 'select'
    ), # for ZF2741 only
    temp_update_interval_unit_chk = Ctrl(
        loc = "//input[@id='check-device.temperatureInterval']", type = 'check'
    ), # for ZF2741 only

    # locators for Wireless Common
    country_code = Ctrl(loc = "//select[@id='WLANCommon.countrycode']", type = 'select'),
    country_code_chk = Ctrl(loc = "//input[@id='check-WLANCommon.countrycode']", type = 'check'),

    wmode = Ctrl(loc = "//select[@id='WLANCommon.mode']", type = 'select'), # for other APs
    wmode_chk = Ctrl(loc = "//input[@id='check-WLANCommon.mode']", type = 'check'), # for other APs

    channel_width = Ctrl(loc = "//select[@id='WLANCommon.channelwidth']", type = 'select'), # for other APs
    channel_width_chk = Ctrl(loc = "//input[@id='check-WLANCommon.channelwidth']", type = 'check'), # for other APs
    channel = Ctrl(loc = "//select[@id='WLANCommon.channel']", type = 'select'), # for other APs
    channel_chk = Ctrl(loc = "//input[@id='check-WLANCommon.channel']", type = 'check'), # for other APs
    #Transmit Power
    txpower_chk = Ctrl(loc = "//input[@id='check-WLANCommon.txpower']", type = 'check'),
    txpower = Ctrl(loc = "//select[@id='WLANCommon.txpower']", type = 'select'),
    prot_mode_chk = Ctrl("//input[@id='check-WLANCommon.protmode']", type = 'check'),
    prot_mode = Ctrl(loc = {
        'disabled': "//input[@id='WLANCommon.protmode.0']",
        'cts-only': "//input[@id='WLANCommon.protmode.1']",
        'rts-cts': "//input[@id='WLANCommon.protmode.2']"
    }, type = 'radioGroup'),

    next_btn = Ctrl(loc = "//input[@id='nextWizard']", type = 'button'),
    save_btn = Ctrl(loc = "//input[@id='nextWizard' and @value='Save']", type = 'button'),
    cancel_cfg_tmpl_btn = Ctrl(loc = "//input[@id='cancel-ap']", type = 'button'),
)
# This "DualBand_Locators" is to define lcoators for additional configs of dualband
# APs (ZF7962...).
# If create a template for a dualband
# APs, we will update the "Locators" with "DualBand_Locators"

DualBand_Locators = dict(
    channel_width_1 = Ctrl(loc = "//select[@id='WLANCommon1.channelwidth']", type = 'select'), # for other APs
    channel_width_1_chk = Ctrl(loc = "//input[@id='check-WLANCommon1.channelwidth']", type = 'check'), # for other APs
    channel_1 = Ctrl(loc = "//select[@id='WLANCommon1.channel']", type = 'select'), # for 7962 (dual band)
    channel_1_chk = Ctrl(loc = "//input[@id='check-WLANCommon1.channel']", type = 'check'), # for 7962 (dual band)

    channel_2 = Ctrl(loc = "//select[@id='WLANCommon2.channel']", type = 'select'), # dual band for radio 5G
    channel_2_chk = Ctrl(loc = "//input[@id='check-WLANCommon2.channel']", type = 'check'), # dualband for 5G
    channel_width_2 = Ctrl(loc = "//select[@id='WLANCommon2.channelwidth']", type = 'select'), # for other APs
    channel_width_2_chk = Ctrl(loc = "//input[@id='check-WLANCommon2.channelwidth']", type = 'check'), # for other APs

    wlan_9 = Ctrl(loc = "//input[@id='group-11']", type = "check"),
    wlan_10 = Ctrl(loc = "//input[@id='group-12']", type = "check"),
    wlan_11 = Ctrl(loc = "//input[@id='group-13']", type = "check"),
    wlan_12 = Ctrl(loc = "//input[@id='group-14']", type = "check"),
    wlan_13 = Ctrl(loc = "//input[@id='group-15']", type = "check"),
    wlan_14 = Ctrl(loc = "//input[@id='group-16']", type = "check"),
    wlan_15 = Ctrl(loc = "//input[@id='group-17']", type = "check"),
    wlan_16 = Ctrl(loc = "//input[@id='group-18']", type = "check"),
    management = Ctrl(loc = "//input[@id='group-19']", type = "check"),
    dev_reg_settings = Ctrl(loc = "//input[@id='group-20']", type = "check"),
    vlan_setting = Ctrl("//input[@id='group-21']", type = "check"),
)
# CONSTANTS FOR THIS LIB
SINGLE_BAND = 0 # for single band APs like 2942, 2925
DUAL_BAND_RD_MODE_1 = 1 # for dual band APs like 7962, radio mode 2.4G
DUAL_BAND_RD_MODE_2 = 2 # for dual band APs like 7962, radio mode 5G

# TODO: Two below params are just to work around for fill_pro_wlan_det_form func
# for dualband APs like 7962. Consider finding out a better solution.
# Plz refer to FlexMaster.fill_pro_wlan_det_form to func for more detail.
RADIO_MODE_1 = 100 # 2.4GHz
RADIO_MODE_2 = 101 # 5GHz

#WIRELESS_2DOT4_G = 1 # 2.4G
#WIRELESS_5_G   = 2 # 5G

def nav_to(obj, force = False):
    obj.navigate_to(obj.PROVISIONING, obj.PROV_CONFIG_TMPLS, force = force)

def search_cfg_tmpl(obj, tmpl_name):
    '''
    Return a dictionary of the first template name matched
    '''
    nav_to(obj, True)
    s, l = obj.selenium, Locators
    tmpl_name_col = l['tmpl_tbl'].cfg['hdrs'][0]
    cfg = dict(tmpl_name_col = tmpl_name)

    return ac_get(
        s, l,
        {'tmpl_tbl': dict(get = '1st', match = {tmpl_name_col:tmpl_name}, op = 'equal')}
    )['tmpl_tbl']

def get_cfg_tmpl_view(obj, tmpl_name):
    '''
    This function is to get detail of cfg template: template name, model, and its
    params in detail.
    Return a dictionary with following items:
        - templatename: cfg template name
        - persist: YES/NO
        - items name and their value
    '''
    s, l = obj.selenium, Locators
    row = search_cfg_tmpl(obj, tmpl_name)
    s.click_and_wait(row['links']['view'])

    data = ac_get(
        s, l,
        dict(cfg_param_tbl = {'no_hdrs':True, 'ignore_case':True},
             view_tmpl_name = {}, view_persist = {})
    )

    data.update(data['cfg_param_tbl'])
    # Add the template name, persist value to the result then delete locator template
    # name of the template "View"
    data['templatename'], data['persist'] = data['view_tmpl_name'], data['view_persist']
    del data['view_tmpl_name'], data['view_persist'], data['cfg_param_tbl']

    return data

def export_cfg_tmpl(obj, tmpl_name):
    '''
    This function is to export a cfg template to excel file and return path of saved
    file.
    '''
    s, l = obj.selenium, Locators
    row = search_cfg_tmpl(obj, tmpl_name)
    s.click_and_wait(row['links']['export'])

    return download_file(tmpl_name + '.xls')

def read_exported_cfg_tmpl(file_path, ignore_case = True):
    '''
    - This function is to read an cfg tmpl exported to excel file.
    - Remove unused item such as: "Parameter Name"
    - Format two items "Template Name", "Persist" to put it in the dictionary format
      like other ones.
    - Format all keys: remove space and lower them
    - Remove unused items
    - Return a dictionary
    '''
    ex_obj = readexcel(file_path)
    iter_f = ex_obj.getiter(ex_obj.worksheets()[0], returnlist = True, strip_list = [' ', ':'])

    result_cfg = {}
    pat = "^(Template Name|Persist)"
    KEY_IDX, VAL_IDX = 0, 1
    for r in iter_f: # each row is a list with two elements
        if re.match(pat, r[KEY_IDX], re.I):
            # Items looks like [u'Template Name:Auto_Cfg_ZF2925_090707.172057', ''],
            # [u'Persist: NO', '']. After this, r will have two elements as normal
            r = r[KEY_IDX].split(':')

        if ignore_case: k = r[KEY_IDX].lower().replace(' ', '')
        result_cfg[k] = r[VAL_IDX]

    # Format the data before return
    # Because value of item "persist" still has a space after split so strip it
    result_cfg['persist'] = result_cfg['persist'].strip(' ')
    # remove unused key
    unused_k = 'parametername'if ignore_case else 'Parameter Name'
    del result_cfg[unused_k]

    return result_cfg

def copy_cfg_tmpl(obj, src_name, dst_name):
    return_row = search_cfg_tmpl(obj, src_name)
    if not return_row:
        raise Exception('Not found template name %s to do copy' % src_name)

    s, l = obj.selenium, Locators
    s.click_and_wait(return_row['links']['copy'])

    ac_set(s, l, dict(new_tmpl_name = dst_name, copy_btn = ''))
    return_row = search_cfg_tmpl(obj, dst_name)

    return True if return_row else False

def create_cfg_tmpl(obj, cfg = {}):
    '''
    NOTE: Obsoleted interface. Use create_cfg_tmpl_2 instead.

    This function is a wrapper function to verify whether a cfg template created
    correctly or not.
    NOTE: Temporarily this function still calls function from FlexMaster.py. It
    will re-factored later
    Input:
    - obj: flexmaster object
    - cfg: a dictionary with params:
        + template_name: name of cfg template
        + template_model: template model
        + options: a dictionary of config option of this template
    '''
    p = dict(
        convert_in_advanced = True
    )
    p.update(cfg)
    obj.create_cfg_template(**p)

# This is to map tiltle on the web UI to key word of cfg
# Constants for title forms
DEVICE_GENERAL = 'Device General'
INTERNET = 'Internet'
WLAN_COMMON = 'Wireless Common'
WLAN_1 = 'Wireless 1'
WLAN_2 = 'Wireless 2'
WLAN_3 = 'Wireless 3'
WLAN_4 = 'Wireless 4'
WLAN_5 = 'Wireless 5'
WLAN_6 = 'Wireless 6'
WLAN_7 = 'Wireless 7'
WLAN_8 = 'Wireless 8'
WLAN_9 = 'Wireless 9'
WLAN_10 = 'Wireless 10'
WLAN_11 = 'Wireless 11'
WLAN_12 = 'Wireless 12'
WLAN_13 = 'Wireless 13'
WLAN_14 = 'Wireless 14'
WLAN_15 = 'Wireless 15'
WLAN_16 = 'Wireless 16'
MGMT = 'Management'
DEV_REG_SETTINGS = 'Device Registration Settings'
VLAN_SETTING = 'VLAN Setting'

def create_cfg_tmpl_2(obj, template_name, template_model, cfg = {}, timeout = 10):
    '''
    + This function is to support creating a cfg template for normal aps like
      2942, 7942 and dualband ap.
    + Temporarily this function still calls old function from FlexMaster.py. It
    will re-factored later.
    Input:
    - obj: flexmaster object
    - template_name: name of cfg template
    - template_model: template model
    - options: a dictionary of config option of this template
    - cfg: a dictionary of configuration to create a cfg template as below:
        {
            'device_general': {Device General items},
            'wlan_common': {wlan common items},
            'wlan_1': {wlan detail items},
            ....
            'wlan_16': {wlan detail items},
        }
    NOTE:
        + Support: Currently support for Device General Form, Wireless Common,
        Wireless 1, ..., Wirelss 16.
        + Not support: Internet form and the other forms.
    '''
    s, l = obj.selenium, copy.deepcopy(Locators)
    _cfg, product_type = copy.deepcopy(cfg), _map_ap_model_to_label(template_model)

    nav_to(obj, force = True)
    # 1. If template_model is in special_models, re-update additional locator
    try:
        additional_locs = {
            'ZF7962': DualBand_Locators,
        }[template_model.upper()]
        l.update(additional_locs)
        logging.info('Update additional locators for this model %s' % template_model)
    except KeyError:
        logging.info('No need to udpate additional locators for this model %s' % template_model)

    # Build config to select configuration options for the first page
    check_box_cfg_opts = dict(
        template_name = template_name,
        product_type = product_type,
    )
    for k in _cfg:
        check_box_cfg_opts[k] = True

    # Tick off check boxes of configuration options and click next to go next cfg form
    time.sleep(3)
    ctrl_order = ['create_new_tmpl', 'template_name', 'product_type'] + _cfg.keys() + ['next_btn']
    ac_set(s, l, check_box_cfg_opts, ctrl_order)

    for t in try_interval(timeout * 60, 3):
        # Get form name first, base on the form name we will get config for that from
        # from "cfg" variable.
        form_name = s.get_text(Locators['form_title'].loc)
        # For dualban aps 7962, its wlan name may be "Wireless 1 (Radio 1)",
        # so we remove unused string "(radio 1)" to make it shortened
        filter_p = '.*(?= \()'
        filter_ret = re.search(filter_p, form_name, re.I)
        form_name = filter_ret.group(0) if filter_ret else form_name
        try:
            set_form_fn, form_cfg = {
                DEVICE_GENERAL.upper() : (set_device_general_form,
                                          dict(obj = obj, cfg = _cfg.get('device_general', {}))),
                INTERNET.upper()       : (obj.fill_pro_internet_form, _cfg.get('internet', {})),
                WLAN_COMMON.upper()    : (set_wlan_common_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_common', {}), template_model = template_model)),
                WLAN_1.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_1', {}), radio_type = RADIO_MODE_1)),
                WLAN_2.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_2', {}), radio_type = RADIO_MODE_1)),
                WLAN_3.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_3', {}), radio_type = RADIO_MODE_1)),
                WLAN_4.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_4', {}), radio_type = RADIO_MODE_1)),
                WLAN_5.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_5', {}), radio_type = RADIO_MODE_1)),
                WLAN_6.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_6', {}), radio_type = RADIO_MODE_1)),
                WLAN_7.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_7', {}), radio_type = RADIO_MODE_1)),
                WLAN_8.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_8', {}), radio_type = RADIO_MODE_1)),
                WLAN_9.upper()         : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_9', {}), radio_type = RADIO_MODE_2)),
                WLAN_10.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_10', {}), radio_type = RADIO_MODE_2)),
                WLAN_11.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_11', {}), radio_type = RADIO_MODE_2)),
                WLAN_12.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_12', {}), radio_type = RADIO_MODE_2)),
                WLAN_13.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_13', {}), radio_type = RADIO_MODE_2)),
                WLAN_14.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_14', {}), radio_type = RADIO_MODE_2)),
                WLAN_15.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_15', {}), radio_type = RADIO_MODE_2)),
                WLAN_16.upper()        : (set_wlan_detail_form,
                                          dict(obj = obj, cfg = _cfg.get('wlan_16', {}), radio_type = RADIO_MODE_2)),
                #MGMT           : (obj.fill_pro_mgmt_form, cfg['wlan_1']), # Not support cfg for this form yet
                #DEV_REG_SETTINGS: # Not support this form yet
                #VLAN_SETTING    : = # Not support this form yet
            }[form_name.upper()]

            logging.info('Config for the form "%s"' % form_name)
            set_form_fn(**form_cfg)
            s.click_and_wait(l['next_btn'].loc)
        except KeyError:
            #TODO: Should not base on Exception to handle flow actions
            # if KeyError exception occurs here, it means it already comes to the "Save" form,
            # call save template function
            obj.save_cfg_template(form_name)
            logging.info('Created config template "%s"' % template_name)
            break

def set_wlan_common_form(obj, cfg = {}, template_model = ''):
    '''
    This function is to set cfg for wlan common for normal aps 2942, 2925
    and dualband aps like 7962.
    - obj: fm instance.
    - cfg: a dictionary of config items for Wireless Common.
    - template_model: It is optional param. We need this param to update additional locators
             for special model like 7962.
             => Specify the exact model "ZF7962" for 7962.
    '''
    s, l = obj.selenium, copy.deepcopy(Locators)
    _cfg = copy.deepcopy(cfg)
    # 1. If template_model is in special_models, re-update additional locator
    try:
        additional_locs = {
            'ZF7962': DualBand_Locators,
        }[template_model.upper()]
        l.update(additional_locs)
        logging.info('Update additional locators for this model %s' % template_model)
    except KeyError:
        logging.info('No nedd to udpate additional locators for this model %s' % template_model)

    # Update check box of configured items to _cfg. Id locator of checkbox of an
    # element has suffix "_chk"
    for k in cfg: _cfg['%s_chk' % k] = True

    ctrl_order = _cfg.keys() #+ ['next_button']
    ac_set(s, l, map_cfg_value(_cfg), ctrl_order)


def set_device_general_form(obj, cfg = {}):
    '''
    Keys for ZF2741 only
    - temp_update_interval: interval to do update for temperature in second
    '''
    #obj.fill_device_general_form(cfg)
    s, l = obj.selenium, copy.deepcopy(Locators)
    _cfg = copy.deepcopy(cfg)

    # If the _cfg has key "temp_update_interval", calculate it to add unit key
    # temp_update_interval_unit
    if _cfg.has_key('temp_update_interval'):
        if int(_cfg['temp_update_interval']) >= 3600:
            _cfg['temp_update_interval'] = float(_cfg['temp_update_interval']) / 3600.0
            _cfg['temp_update_interval_unit'] = 'hour\(s\)'
        elif int(_cfg['temp_update_interval']) >= 60:
            _cfg['temp_update_interval'] = float(_cfg['temp_update_interval']) / 60.0
            _cfg['temp_update_interval_unit'] = 'minute\(s\)'
        else:
            _cfg['temp_update_interval_unit'] = 'second\(s\)'

    # Update check box of configured items to _cfg. Id locator of checkbox of an
    # element has suffix "_chk"
    for k in cfg: _cfg['%s_chk' % k] = True

    ctrl_order = _cfg.keys() #+ ['next_button']
    ac_set(s, l, map_cfg_value(_cfg), ctrl_order)


def set_wlan_detail_form(obj, cfg = {}, radio_type = RADIO_MODE_1):
    '''
    This function is to set config for wlan detail form: Wireless 1, Wireless 2,
    ... Wireless 16.
    - cfg: a dictionary as below. Plz refer RuckusAutoTest.scripts.libFM_TestSuite.AP_Cfg
           to know how to generate this config.
        {
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
            'rate_limiting': 'Rate limiting: Disabled, Enabled',
            'downlink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
            'uplink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
            'encrypt_method': 'Diablded, WEB, WPA',

            'wep_mode': 'Open, SharedKey, Auto',
            'encryption_len': 'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
            #Wireless 1 WEP Key Index
            'wep_key_idx': 'key index: 1, 2, 3, 4',
            #WEP key password
            'wep_pass': 'password of wep method',
            'cwep_pass': ' password of wep method (confirm)',

            #WPA Version
            'wpa_version': 'WPA version: WPA, WPA2, Auto',
            #WPA Algorithm
            'wpa_algorithm': 'WPA Algorithm: TKIP, AES, Auto',
            #Authentication
            'auth': 'Authentication: PSK, 802.1x, Auto',
            'psk_passphrase': 'PSK passphrase',
            'cpsk_passphrase': 'PSK passphrase (confirm)',
            'radius_nas_id': 'Radius NAS-ID',
            'auth_ip': 'Authentication IP address',
            'auth_port': 'Authentication Port',
            'auth_secret': 'Authentication Server Secret',
            'cauth_secret': 'Authentication Server Secret',
            'acct_ip': 'Accounting IP address',
            'acct_port': 'Accounting Port',
            'acct_secret': 'Accounting Server Secret',
            'cacct_secret': 'Accounting Server Secret (confirm)'
        }
    - radio_type: RADIO_MODE_1 -> 2.4GHz
                  RADIO_MODE_2 -> 5GHz
    '''
    obj.fill_pro_wlan_det_form(cfg, radio_type = radio_type)

def verify_cfg_tmpl(obj, cfg = {}):
    '''
    This function is a wrapper function to verify whether a cfg template created
    correctly or not.
    NOTE:
        - Temporarily this function still calls function from FlexMaster.py. It
        - This function is just able to verify model ZF7942, ZF2942, ZF2925 only.

    will re-factored later
    Input:
    - obj: flexmaster object
    - cfg: a dictionary with params:
        + template_name: name of cfg template
        + template_model: template model
        + options: a dictionary of config option of this template
    - convert_in_advanced: True if pass keys of "cfg" with simple format like
        cfg = {
            template_model: ZF2925/ZF2942,
            options = {
                  'device_general':{'device_name': 'Name of Device', 'username': 'Name of Super user',
                                   'password': 'Password of Super user', 'cpassword': 'Confirm password'},
                  'internet': {},
                  'wlan_common': {},
                  'wlan_1': {},
                  ..............
            }
        }
    '''
    p = dict(
        convert_in_advanced = True
    )
    p.update(cfg)
    return obj.verify_cfg_template(**p)

def delete_cfg_tmpl(obj, tmpl_name):
    '''This ifunction is to delete the first matched cfg template'''
    return_row = search_cfg_tmpl(obj, tmpl_name)
    if not return_row:
        raise Exception('Not found template name %s to do delete' % tmpl_name)

    s, l = obj.selenium, Locators
    s.click_and_wait(return_row['links']['delete'])
    s.close_confirmation_dlg()
    return_row = search_cfg_tmpl(obj, tmpl_name)

    return False if return_row else True

def _map_ap_model_to_label(product_type):
    '''
    - product_type: 'ZF2925'|'ZF2942'|'ZF7942'|'ZF7962'
    '''
    return {
        'ZF2925': 'Ruckus ZF2925 Device',
        'ZF2942': 'Ruckus ZF2942 Device',
        'ZF7942': 'Ruckus ZF7942 Device',
        'ZF7962': 'Ruckus ZF7962 Device',
        'ZF2741': 'Ruckus ZF2741 Device',
        'VF2825_1': 'Ruckus VF2825 Device (ruckus01)',
        'VF2825_3': 'Ruckus VF2825 Device (ruckus03)',
        'VF2825_4': 'Ruckus VF2825 Device (ruckus04)',
        'VF7811': 'Ruckus VF7811 Device',
        'VF2811': 'Ruckus VF2811 Device',
    }[product_type.upper()]

def _get_all_select_options(obj, cfg, ctrl_order):
    '''
    This function is to get all select options of a combo box
    @TODO: Consider to write a compound function for get_country_codes and get_channels
    '''

def get_country_codes(obj, template_model):
    '''
    This function is to get all country codes of a product type from config template.
    - obj: fm instance
    - template_model: 'ZF2925'|'ZF2942'|'ZF7962'|...
    return:
    - a list of all options
    '''
    s, l = obj.selenium, Locators
    ctrl_order = ['create_new_tmpl', 'product_type', 'wlan_common', 'next_btn']

    nav_to(obj, True)
    ac_set(s, l, {'wlan_common': True, 'product_type': _map_ap_model_to_label(template_model)}, ctrl_order)

    data = s.get_all_options(l['country_code'].loc)
    # cancel the cfg page
    s.click_and_wait(l['cancel_cfg_tmpl_btn'].loc)

    return data

def get_channels(obj, template_model, radio_mode = SINGLE_BAND):
    '''
    This function is to get all channels of a product type from config template.
    - obj: fm instance
    return:
    - a list of all options
    '''
    s, l = obj.selenium, copy.deepcopy(Locators)
    ctrl_order = ['create_new_tmpl', 'product_type', 'wlan_common', 'next_btn']
    try:
        additional_locs = {
            'ZF7962': DualBand_Locators,
        }[template_model.upper()]
        l.update(additional_locs)
        logging.info('Update additional locators for this model %s' % template_model)
    except KeyError:
        logging.info('No nedd to udpate additional locators for this model %s' % template_model)

    nav_to(obj, True)
    ac_set(
        s, l,
        {'wlan_common': True, 'product_type': _map_ap_model_to_label(template_model)},
        ctrl_order
    )
    channel_loc = {
        SINGLE_BAND: l['channel'].loc,
        DUAL_BAND_RD_MODE_1: l['channel_1'].loc,
        DUAL_BAND_RD_MODE_2: l['channel_2'].loc,
    }[radio_mode]
    data = s.get_all_options(channel_loc)
    # cancel the cfg page
    s.click_and_wait(l['cancel_cfg_tmpl_btn'].loc)

    return data


