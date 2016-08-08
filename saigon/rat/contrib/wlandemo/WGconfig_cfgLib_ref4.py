import logging
import time

import defaultWlanConfigParams_ref3 as DWCFG
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as WGS
from RuckusAutoTest.components.lib.zd import wlan_zd as WLN
from RuckusAutoTest.components.lib.zd import access_points_zd as APX
from RuckusAutoTest.components.lib.zd import access_control_zd as ACL


def get_ap_mac_list(zd):
    mac_list = [apinfo['mac'] for apinfo in zd.get_all_ap_info()]

    return mac_list

def get_ap_xs_info(zd):
    ap_xs_list = [dict(mac = ap['mac'], model = ap['model'], radio = get_ap_radio_type(ap['model'])) \
                  for ap in zd.get_all_ap_info()]

    return ap_xs_list

def get_ap_radio_type(ap_model):
    if ap_model in ['zf7962', 'zf7762']:
        return ['ng', 'na']
    elif ap_model in ['zf7942', ]:
        return ['ng']
    return ['bg']


def update_ap_xs_info(zd, ap_xs, description, wgs_name):
    ap_rp = {}

    for radio in ap_xs['radio']:
        ap_rp[radio] = dict(wlangroups = wgs_name)

    APX.cfg_wlan_groups_by_mac_addr(zd, ap_xs['mac'], ap_rp, description)
    ap_xs_info = APX.get_cfg_info_by_mac_addr(zd, ap_xs['mac'])

    return ap_xs_info

def update_ap_xs_info_ch(zd, ap_xs, description, wgs_name):
    ap_rp = {}
    for radio in ap_xs['radio']:
        ap_rp[radio] = dict(wlangroups = wgs_name, channel = '1') # set all APs channels to channel number you prefer instead of auto
    APX.cfg_wlan_groups_by_mac_addr(zd, ap_xs['mac'], ap_rp, description)
    ap_xs_info = APX.get_cfg_info_by_mac_addr(zd, ap_xs['mac'])
    return ap_xs_info

def create_wlans(zd, mytb):
    for wlan_id in mytb['wlans']:
        try:
            wlan_cfg = DWCFG.get_cfg(wlan_id)
            create_wlan(zd, wlan_cfg)
            print "Wlan %s [ssid %s] created" % (wlan_id, wlan_cfg['ssid'])
        except Exception, e:
            print "WlanConfig named %s cannot be created:\n%s" % (wlan_id, e.message)

def create_wlan_group(zd, mytb):
    wlan_cfg = DWCFG.get_cfg(mytb['wlans'][0])
    WGS.create_wlan_group(zd, mytb['wgs_name'], wlan_cfg['ssid'])

def create_multi_wlan_groups(zd, mytb):
    #wlan_cfg = DWCFG.get_cfg(mytb['wlans'][3])
    ssid_list = get_ssid_list(zd, mytb)
    _create_multi_wlan_groups(zd, mytb['wgs_name'], ssid_list, num_of_wgs = 2, description = 'AutomationIsfuntoolforQATeam', pause = 1.0)

def align_wlan_group_sn_wlan(zd, mytb):
    ssid_list = get_ssid_list(zd, mytb)
    #WGS.cfg_wlan_group_members(zd, mytb['wgs_name'], ssid_list, True)
    # no WLAN belong to Default WlanGrup
    WGS.cfg_wlan_group_members(zd, 'Default', ssid_list, False)

#put all configured into a list
def get_wlan_groups_list(zd):
    wgs_list = WGS.get_wlan_groups_list(zd)
    return wgs_list

def get_ssid_list(zd, mytb):
    ssid_list = []
    for wlan_id in mytb['wlans']:
        wlan_cfg = DWCFG.get_cfg(wlan_id)
        ssid_list.append(wlan_cfg['ssid'])
    return ssid_list

def remove_wlan_config(zd):
    WGS.remove_wlan_groups(zd, get_ap_mac_list(zd))
    zd.remove_all_cfg()

# A Method of creating fake MAC in ACL policy
def create_mac_list(acl_conf, num_of_mac = 5):
    if num_of_mac > 1:
        for i in range(num_of_mac):
            for j in range(num_of_mac):
                new_mac = "00:00:00:00:11:%0x%0x" % (i, j + 1)
                acl_conf['mac_list'].append(new_mac)
    else:
        pass

    return acl_conf

# A method of creating L2ACL policy from 1 to Maximum
def create_l2_acl_policy(zd, acl_conf, num_of_acl = 1):
    ACL.delete_all_l2_acl_policies(zd, pause = 1)
    create_mac_list(acl_conf)
    if num_of_acl == 1:
        ACL.create_l2_acl_policy(zd, acl_conf, pause = 1)
        logging.info("Create [acl_name %s] with [mac_addr %s]" % (acl_conf['acl_name'], acl_conf['mac_list']))
    else:
        for c in range(num_of_acl):
            acl_conf['acl_name'] = "%s-%d" % (acl_conf['acl_name'], c + 1)
            logging.info("Create [acl_name %s] with [mac_addr %s]" % (acl_conf['acl_name'], acl_conf['mac_list']))
            ACL.create_l2_acl_policy(zd, acl_conf, pause = 1)
            acl_conf['acl_name'] = 'TestForFun'

# A method of creating L3L4ACL policy from 1 to Maximum
def create_l3_acl_policy(zd, acl_conf, num_of_acl = 1):
    ACL.delete_all_l3_acl_policies(zd, pause = 1)
    # pprint(acl_conf)
    if num_of_acl == 1:
        ACL.create_l3_acl_policy(zd, acl_conf, pause = 1)
        logging.info("Create [acl_name %s] with [rules]" % (acl_conf['name']))
    else:
        for c in range(num_of_acl):
            acl_conf['name'] = "%s-%d" % (acl_conf['name'], c + 1)
            logging.info("Create [acl_name %s] with [rules]" % (acl_conf['name']))
            ACL.create_l3_acl_policy(zd, acl_conf, pause = 1)
            acl_conf['name'] = 'TestForFunL3ACL'


# Create a series Wlan Group & check all Wlans in each WlanGroup; new method recommened by Alex
#
def _create_multi_wlan_groups(zd, wlan_group, wlan_name, check_VLAN_override = False, description = '', num_of_wgs = 1, pause = 1.0):
    xloc = WGS.LOCATORS_CFG_WLANGROUPS
    logging.info("Create %d WLAN Group(s) with-memeber [wlan %s]" % (num_of_wgs, wlan_name))

    # zd.do_login()
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    for i in range(num_of_wgs):
        wgs_name = "%s-%d" % (wlan_group, i + 1)
        if num_of_wgs == 1:
            wgs_name = wlan_group
        logging.info("Create [wlangroup %s] with-memeber [wlan %s]" % (wgs_name, wlan_name))
        if not zd.s.is_visible(xloc['create_new']):
            msg = "Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported"
            raise Exception("Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported")

        zd.s.click_and_wait(xloc['create_new'])
        zd.s.type_text(xloc['edit_name'], wgs_name)
        zd.s.type_text(xloc['edit_description'], description)
        if check_VLAN_override:
            zd.s.check(xloc['edit_member_vlan_override'])
        else:
            zd.s.uncheck(xloc['edit_member_vlan_override'])
        if type(wlan_name) is list:
            for wlan in wlan_name:
                zd.s.check(xloc['edit_member_vlan_wlan'] % wlan)
        else:
            zd.s.check(xloc['edit_member_vlan_wlan'] % (wlan_name))

        zd.s.click_and_wait(xloc['edit_OK'])
        time.sleep(pause)


def create_wlan(zd, wlan_conf, pause = 1):
    """
    Create a new wlan base on the configuration parameter
    Input: zd: the Zone Director object
           wlan_conf: dictionary of wlan configuration parameters, ex: {'ssid':'', 'encryption':'', 'wpa_ver':''...}
    """
    xlocs = WLN.LOCATORS_CFG_WLANS

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    try:
        zd.s.click_and_wait(xlocs['create_wlan'])
        _set_wlan_cfg(zd, wlan_conf)
        logging.info('WLAN [%s] has been created successfully' % wlan_conf['ssid'])

    except Exception, e:
        msg = '[WLAN %s could not be created]: %s' % (wlan_conf['ssid'], e.message)
        logging.info(msg)
        raise Exception(msg)


def _set_wlan_cfg(zd, wlan_conf):
    """
    Setting wlan configuration using input paramters. The WLAN configuration dialog is supposed to be
    displayed before calling this function.
    @param zd: the reference to the Zone Director object
    @param wlan_conf: a dictionary contains configuration of a WLAN
    """
    conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
            'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
            'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
            'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '', 'dvlan': False,
            'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    conf.update(wlan_conf)
    if conf['auth'] == 'PSK':
        conf['auth'] = 'open'
    locs = WLN.LOCATORS_CFG_WLANS

    if conf['ssid'] is not None:
        zd.s.type_text(locs['ssid_name_textbox'], conf['ssid'])
    if conf['description'] is not None:
        zd.s.type_text(locs['description_textbox'], conf['description'])

    if conf['type'] == 'standard':
        zd.s.click_and_wait(locs['usage_standard_radio'])
    elif conf['type'] == 'guest':
        zd.s.click_and_wait(locs['usage_guest_radio'])
    elif conf['type'] == 'hotspot':
        zd.s.click_and_wait(locs['usage_wispr_radio'])
        if conf['hotspot_profile']:
            zd.s.select_option(locs['hotspot_option'], conf['hotspot_profile'])
            zd.s.click_and_wait(locs['hotspot_option'])

    if conf['auth']:
        zd.s.click_and_wait(locs['%s_radio' % conf['auth'].lower()])

    if conf['wpa_ver']:
        zd.s.click_and_wait(locs['%s_radio' % conf['wpa_ver'].lower()])
        if conf['encryption'] in ['TKIP', 'AES']:
            zd.s.click_and_wait(locs['%s_radio' % conf['encryption'].lower()])
        if conf['key_string']:
            zd.s.type_text(locs['passphrase_textbox'], conf['key_string'])
    elif conf['encryption'] in ['WEP-64', 'WEP-128']:
        x = conf['encryption'].replace('-', '').lower()
        zd.s.click_and_wait(locs['%s_radio' % x])
        if conf['key_index']:
            zd.s.click_and_wait(locs['wepkey_index_radio'] % conf['key_index'])
        if conf['key_string']:
            zd.s.type_text(locs['wepkey_textbox'], conf['key_string'])
    elif conf['encryption'] == 'none':
        zd.s.click_and_wait(locs['none_radio'])

    if conf['do_webauth'] is not None:
        is_checked = zd.s.is_checked(locs['web_auth_checkbox'])
        if conf['do_webauth'] and not is_checked or not conf['do_webauth'] and is_checked:
            zd.s.click_and_wait(locs['web_auth_checkbox'])

    if conf['auth_svr']:
        if conf['auth'] == 'EAP':
            x = locs['authsvr_eap_select']
        elif conf['auth'] == 'mac':
            x = locs['authsvr_mac_select']
        else:
            x = locs['authsvr_web_select']
        zd.s.select_option(x, conf['auth_svr'])
        zd.s.click_and_wait(x)

    if conf['do_isolation'] is not None:
        is_checked = zd.s.is_checked(locs['client_isolation_checkbox'])
        if conf['do_isolation'] and not is_checked or not conf['do_isolation'] and is_checked:
            zd.s.click_and_wait(locs['client_isolation_checkbox'])

    if conf['do_zero_it'] is not None:
        is_checked = zd.s.is_checked(locs['zeroit_checkbox'])
        if conf['do_zero_it'] and not is_checked or not conf['do_zero_it'] and is_checked:
            zd.s.click_and_wait(locs['zeroit_checkbox'])

    if conf['do_dynamic_psk'] is not None:
        is_checked = zd.s.is_checked(locs['dynamic_psk_checkbox'])
        if conf['do_dynamic_psk'] and not is_checked or not conf['do_dynamic_psk'] and is_checked:
            zd.s.check(locs['dynamic_psk_checkbox'])

    # Advanced configuration
    _set_wlan_advanced_cfg(zd, conf)

    zd.s.click_and_wait(locs['ok_button'])

    # If an alert of wrong configuration(ex: wrong wlan name, duplicated name...) appears,
    # click the Cancel button
    zd.s.get_alert(locs['cancel_button'])


def _set_wlan_advanced_cfg(zd, conf, pause = 2.0):
    locs = WLN.LOCATORS_CFG_WLANS
    zd.s.click_and_wait(locs['advanced_options_anchor'])

    if conf['acct_svr']:
        zd.s.select_option(locs['acctsvr_option'], conf['acct_svr'])
        zd.s.click_and_wait(locs['acctsvr_option'])
    if conf['interim_update'] is not None:
        zd.s.type_text(locs['acctsvr_interim_textbox'], conf['interim_update'])
    if conf['acl_name']:
        zd.s.select_option(locs['acl_option'], conf['acl_name'])
    if conf['l3_l4_acl_name']:
        zd.s.select_option(locs['l34_acl_option'], conf['l3_l4_acl_name'])
    if conf['uplink_rate_limit']:
        zd.s.select_option(locs['uplink_rate_option'], conf['uplink_rate_limit'])
        zd.s.click_and_wait(locs['uplink_rate_option'])
    if conf['downlink_rate_limit']:
        zd.s.select_option(locs['downlink_rate_option'], conf['downlink_rate_limit'])
        zd.s.click_and_wait(locs['downlink_rate_option'])
    if conf['vlan_id'] is not None:
        zd.s.click_and_wait(locs['do_vlan_checkbox'])
        time.sleep(pause)
        zd.s.type_text(locs['vlan_id_textbox'], conf['vlan_id'])
    if conf['dvlan']:
        zd.s.click_and_wait(locs['do_dvlan_checkbox'])
    if conf['do_hide_ssid'] is not None:
        is_checked = zd.s.is_checked(locs['do_beacon_checkbox'])
        if conf['do_hide_ssid'] and not is_checked or not conf['do_hide_ssid'] and is_checked:
            zd.s.check(locs['do_beacon_checkbox'])
    if conf['do_tunnel'] is not None:
        is_checked = zd.s.is_checked(locs['do_tunnel_checkbox'])
        if conf['do_tunnel'] and not is_checked or not conf['do_tunnel'] and is_checked:
            zd.s.check(locs['do_tunnel_checkbox'])

