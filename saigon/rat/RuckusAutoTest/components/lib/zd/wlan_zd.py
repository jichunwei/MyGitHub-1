import logging
import re
import time
import os
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.components.lib.zd import control_zd as control_zd
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga

from RuckusAutoTest.common.DialogHandler import (
    DialogManager, BaseDialog,
)
from RuckusAutoTest.common import lib_Constant as constant

CONST_VALUE = dict(
    const_auth_method_open = 'open',
    const_auth_method_shared = 'shared',
    const_auth_method_eap = 'EAP',
    const_encryption_method_none = 'none',
    const_encryption_method_wpa = 'WPA',
    const_encryption_method_wpa2 = 'WPA2',
    const_encryption_method_wep64 = 'WEP-64',
    const_encryption_method_wep128 = 'WEP-128',
    const_algorithm_tkip = 'TKIP',
    const_algorithm_aes = 'AES',
    const_wep_index1 = '1',
    const_wep_index2 = '2',
    const_wep_index3 = '3',
    const_wep_index4 = '4'
)

LOCATORS_CFG_WLANS = dict(
    # Configure -> WLANs
    wlan_tbl = "//table[@id='wlan']",
    wlan_tbl_nav = "//table[@id='wlan']/tfoot",
    clone_wlan = "//table[@id='wlan']//tr/td[text()='%s']/../td/span[text()='Clone']",
    edit_wlan = "//table[@id='wlan']//tr/td[text()='%s']/../td/span[text()='Edit']",
    create_wlan = "//span[@id='new-wlan']",

    ssid_name_textbox = "//input[@id='name']",
    #cwang@2010-11-1, behavior change after 9.1.0.0.9
    ssid_textbox = "//input[@id='ssid']",
    description_textbox = "//input[@id='description']",

    usage_standard_radio = "//input[@id='usage-user']",
    usage_guest_radio = "//input[@id='usage-guest']",
    usage_wispr_radio = "//input[@id='usage-wispr']",
    usage_autonomous_radio = "//input[@id='usage-autonomous']",

    open_radio = "//input[@id='auth_open']",
    shared_radio = "//input[@id='auth_shared']",
    eap_radio = "//input[@id='auth_eap']",
    mac_radio = "//input[@id='auth_mac']",
    maceap_radio = "//input[@id='auth_maceap']",

    none_radio = "//input[@id='enc_none']",
    wpa_radio = "//input[@id='enc_wpa']",
    wpa2_radio = "//input[@id='enc_wpa2']",
    wpa_mixed_radio = "//input[@id='enc_wpa_mixed']",
    wep64_radio = "//input[@id='enc_wep64']",
    wep128_radio = "//input[@id='enc_wep128']",

    tkip_radio = "//input[@id='wpa-cipher-tkip']",
    aes_radio = "//input[@id='wpa-cipher-aes']",
    auto_radio = "//input[@id='wpa-cipher-auto']",
    passphrase_textbox = "//input[@id='psk']",

    wepkey_index_radio = "//input[@id='wepidx%s']",
    wepkey_textbox = "//input[@id='wep-key']",

    web_auth_checkbox = "//input[@id='do-redirect']",
    client_isolation_checkbox = r"//input[@id='isolation-subnet']",
    #client_isolation_checkbox = "//input[@id='do-guestPcy']",
    #add by louis 2010-11-2 for 9.1 wireless client isolation radio button.
    client_isolation_none_radio = "//input[@id='isolation-none']",
    client_isolation_local_radio = "//input[@id='isolation-local']",
    client_isolation_full_radio = "//input[@id='isolation-subnet']",

    # add by louis on 2010-11-2, for 9.1 priority.
    priority_high_radio = "//input[@id='wlan-pri-high']",
    priority_low_radio = "//input[@id='wlan-pri-low']",
    # end add

    zeroit_checkbox = "//input[@id='do-prov']",
    dynamic_psk_checkbox = "//input[@id='do-dynpsk']",

    authsvr_eap_select = "//select[@id='authsvr-eap']",
    authsvr_web_select = "//select[@id='authsvr-web']",
    authsvr_mac_select = "//select[@id='authsvr-radius']",
    authsvr_maceap_select = "//select[@id='authsvr-radius']",

    hotspot_option = "//select[@id='hotspot-select']",

    advanced_options_anchor = "//tr[@id='cat-advanced']//a[@href='#']",
    acctsvr_option = "//select[@id='acctsvr-eap']",
    acctsvr_interim_textbox = "//input[@id='acctsvr-interim']",
    acl_option = "//select[@id='acl-list']",
    l34_acl_option = "//select[@id='policy-list']",
    l34_ipv6_acl_option = "//select[@id='policy6-list']",
    uplink_rate_option = "//select[@id='uplink-preset']",
    downlink_rate_option = "//select[@id='downlink-preset']",
    mcast_filter_option = "//input[@id='do-mcast-filter']",#chentao 2014-03-25
    do_vlan_checkbox = "//input[@id='do-vlan']",
    vlan_id_textbox = "//input[@id='vlan-id']",
    do_dvlan_checkbox = "//input[@id='do-dvlan']",
    do_beacon_checkbox = "//input[@id='do-beacon']",
    do_tunnel_checkbox = "//input[@id='do-tunnelmode']",
    
    #Sean@2012-12-11, add Proxy ARP checkbox for 9.5
    do_proxy_arp_checkbox = "//input[@id='do-parp']",
    
    #louis@2010-11-03, add background scan, load balancing and max clients
    bgscan_checkbox = "//input[@id='do-bgscan']",
    load_balancing_checkbox = "//input[@id='do-balance']",
    max_clients_textbox = "//input[@id='max-client']",

    check_all_checkbox = "//input[@id='wlan-sall']",
    total_wlans_span = "//table[@id='wlan']//div[@class='actions']/span",
    wlan_checkbox = r"//tr[td='%s']//input[@name='wlan-select']",

    show_more_button = "//input[@id='showmore-wlan']",
    ok_button = "//input[@id='ok-wlan']",
    cancel_button = "//input[@id='cancel-wlan']",
    delete_button = "//input[@id='del-wlan']",
    #cwang@2010-9-30, append wlan search box.
    wlan_search_textbox = r"//table[@id='wlan']//span[@class='other-act']/input[1]",

    #PHANNT@20091015 - Dynamic PSK Batch Generation
    batch_dpsk_wlan_target_option = "//select[@id='batch-dpsk-wlans']",
    batch_dpsk_number_create_textbox = "//input[@id='dpsk-num']",
    batch_dpsk_role_target_option = "//select[@id='batch-dpsk-roles']",
    batch_dpsk_profile_file_textbox = "//input[@id='filename-uploadbatchdpsk']",
    batch_dpsk_generate_button = "//input[@id='apply-batch-dpsk']",
    batch_dpsk_download_button = "//td[@id='batch-dpsk-old']//a[@href='#']",
    #An Nguyen@Mar 2012, added the dynamic vlan textbox for DPSK batch generation
    batch_dpsk_dynamic_vlan_textbox = "//input[@id='dpsk-vlan-id']",
    auto_del_expire_dpsk_checkbox = r"//input[@id='auto-del-expire-dpsk']",
    
    loc_batch_dpsk_msg_span = "//span[@id='msg-batch-dpsk']",
    loc_uploadbatchdpsk_msg_span = "//span[@id='uploaded-uploadbatchdpsk']",
    loc_uploadbatchdpsk_error_span = "//span[@id='error-uploadbatchdpsk']",
    psk_expiration = "//select[@id='expire']",
    psk_apply_button = "//input[@id='apply-dpsk']",
    #Zero-IT Activation
    zero_it_authentication_server = "//select[@id='zeroit-authsvr']",
    zero_it_apply_button = "//input[@id='apply-zeroit']",

    #WLAN service schedule.
    wlan_service_schedule_off_raido = "//input[@id='wlan-off']",
    wlan_service_schedule_on_raido = "//input[@id='wlan-on']",
    wlan_service_schedule_specific_radio = "//input[@id='wlan-timebase']",
    wlan_service_schedule_timebase_td = "//td[@d='%s' and @t='%s']",
    wlan_service_schedule_timebase_state_td = "//td[@d='%s' and @t='%s' and @state='%s']",
    
    #Inactivity Timeout
    inactivity_timeout_textbox = r"//input[@id='max-idle-timeout']",

    #Grace Period
    grace_period_checkbox = r"//input[@id='do-grace-period-sets']",
    grace_period_textbox = r"//input[@id='grace-period-sets']",

    #Option82
    loc_option82_checkbox = r"//input[@id='option82']",
    
    #Jane.Guo@2013-5-7 add Force DHCP check box and timeout textbox
    loc_force_dhcp_checkbox = r"//input[@id='force-dhcp']",
    loc_force_dhcp_timeout_textbox = r"//input[@id='force-dhcp-timeout']",
    
    #Sean@2012-9-4, add Client Fingerprinting check box
    loc_fingerprinting_checkbox = r"//input[@id='sta-info-extraction']",

    loc_authstats_checkbox = r"//input[@id='authstats']",
    loc_do_wmm_ac_checkbox = r"//input[@id='do-wmm-ac']",
    loc_zero_it_auth_server = r"//select[@id='zeroit-authsvr']",
    save_dpsk = r"//a[@onclick='saveBatchDpsk()']",
    #An Nguyen@Dec2012 added the DHCP relay option loc
    loc_do_dhcp_relay_checkbox = r"//input[@id='do-dhcprelay']",
    loc_select_dhcp_relay_svr_dropbox = r"//select[@id='dhcpsvrs']",
    application_visibility_checkbox = r"//input[@id='avp-enabled']",#chen.tao 2014-6-25
    application_denial_policy_select = r"//select[@id='deny-rulelist']",#chen.tao 2014-6-25
)

LOCATORS_MON_WLANS = dict(
    wlan_tbl_loc = "//table[@id='wlansummary']",
    wlan_tbl_nav_loc = "//table[@id='wlansummary']/tfoot",
	client_tbl_loc = "//table[@id='client']",
    client_tbl_nav_loc = "//table[@id='client']/tfoot",
    wlan_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
	enter_wlan_detail="//tr[td[1]='%s']//a",#%wlan_name
    wlan_link = r"//table[@id='wlansummary']//../a[text()='%s']",
    wlan_detail_loc = dict(ssid = r"//td[@id='ssid']",
                           auth = r"//td[@id='authentication']",
                           encryption = r"//td[@id='encryption']",
                           clients = r"//td[@id='clients']",
                           bgscan = r"//td[@id='bgscan']",
                           rxPkts = r"//td[@id='rxPkts']",
                           rxBytes = r"//td[@id='rxBytes']",
                           txPkts = r"//td[@id='txPkts']",
                           txBytes = r"//td[@id='txBytes']"
                         ),
)

tbl_id = dict(
    wlan_summary = 'wlansummary',
    client = 'client'
)

def _nav_to_mon(zd):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN)

###
##
## WLAN OPTIONs
##
###

def get_wlan_client_info_by_mac(zd,wlan_name,sta_mac):
    '''
    return
    {'ap': u'50:a7:33:2e:42:e0',
     'authMethod': u'OPEN',
     'bssid': u'50:a7:33:6e:42:e8',
     'channel': u'11',
     'channelization': u'20',
     'dvcinfo': u'Windows XP',
     'firstAssoc': u'2012/10/17  14:38:33',
     'hostname': u'tb3-sta2',
     'ip': u'192.168.0.147',
     'ipv6': u'',
     'mac': u'00:15:af:ed:94:3b',
     'radio-type': u'802.11g/n',
     'retries': u'746 pkts',
     'rx': u'97 pkts / 13K bytes',
     'signal': u'99%',
     'tx': u'3.5K pkts / 331K bytes',
     'user': u'',
     'vlan': u'1',
     'wlan': u'west.test'}
    '''
    _enter_wlan_detail_page_by_name(zd,wlan_name)
    return _get_client_info_by(zd,{'mac':sta_mac})

def get_wlan_brief_by_name(zd,name, verbose = False):
    '''
    return
    {'authentication': 'open',
     'encryption': 'none',
     'essid': 'new_wlan_19811',
     'name': 'new_wlan_19811',
     'num_sta': '1'}
    '''
    return _get_wlan_brief_by(zd, {'name':name})

def _enter_wlan_detail_page_by_name(zd,wlan_name):
    locators=LOCATORS_MON_WLANS
    _nav_to_mon(zd)
    loc=locators['enter_wlan_detail']%wlan_name
    zd.s.click_and_wait(loc)

def _get_client_info_by(zd, match, verbose = False):
    '''
    '''
    locators=LOCATORS_MON_WLANS
    client_info = wgt.get_first_row_by(
        zd.s, locators['client_tbl_loc'],
        locators['client_tbl_nav_loc'], match,
        filter = locators['wlan_tbl_filter_txt'] % tbl_id['client'],
        verbose = verbose,
    )

    return client_info

def _get_wlan_brief_by(zd, match, verbose = False):
    '''
    '''
    locators=LOCATORS_MON_WLANS
    _nav_to_mon(zd)
    info = wgt.get_first_row_by(
        zd.s, locators['wlan_tbl_loc'],
        locators['wlan_tbl_nav_loc'], match,
        filter = locators['wlan_tbl_filter_txt'] % tbl_id['wlan_summary'],
        verbose = verbose,
    )

    return info

def get_server_list_when_creat_web_auth_wlan(zd, pause = 1):
    xlocs = LOCATORS_CFG_WLANS
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    zd.s.click_and_wait(xlocs['create_wlan'])
    if not zd.s.is_checked(xlocs['web_auth_checkbox']):
        zd.s.click_and_wait(xlocs['web_auth_checkbox'])
    list = zd.s.get_select_options(xlocs['authsvr_web_select'])
    zd.s.click_and_wait(xlocs['cancel_button'])
    return list

def get_zeroit_auth_server_list(zd, pause = 1):
    xlocs = LOCATORS_CFG_WLANS
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)
    return zd.s.get_select_options(xlocs['loc_zero_it_auth_server'])


    
def create_wlan(zd, wlan_conf, pause = 1, is_nav = True, get_alert=True):
    """
    Create a new wlan base on the configuration parameter
    Input: zd: the Zone Director object
           wlan_conf: dictionary of wlan configuration parameters, ex: {'ssid':'', 'encryption':'', 'wpa_ver':''...}
    . is_nav: this param to support config wlan group on ZD template in
      FlexMaster. If do this from FM, don't navigate to ZD > WLANs page.
    """
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    if wlan_conf.get('type') == 'guest':
        logging.info("Create default guest access profile")
        ga.create_default_guestaccess_policy(zd)
        ga.remove_restricted_subnet_entry(zd, 4)
        ga.remove_restricted_subnet_entry(zd, 3)
        ga.remove_restricted_subnet_entry(zd, 2)
    
    xlocs = LOCATORS_CFG_WLANS
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)

    try:
        #@author: yuyanan @since: 2014-8-22 bug:zf-9578 optimize:Element is not visible: "//input[@id='name']"']
        try_count = 10
        flag = 0
        while try_count > 0:
            try_count = try_count-1
            logging.info('click create wlan button retry count:%s'%try_count)
            zd.s.click_and_wait(xlocs['create_wlan'])
            if not zd.s.is_visible(xlocs['ssid_name_textbox']):
                continue
            else:
                flag = 1
                break
        if not flag:
            msg = 'create wlan dialog do not open cause create wlan fail!'
            raise Exception(msg)
           
        _set_wlan_cfg(zd, wlan_conf,get_alert=get_alert)
        logging.info('WLAN [%s] has been created successfully' % wlan_conf['ssid'])
    except Exception, e:
        msg = '[WLAN %s could not be created]: %s' % (wlan_conf['ssid'], e.message)
        logging.info(msg)
        raise Exception(msg)


def create_multi_wlans(zd, wlan_conf_list, pause = 1):
    """
    Create a list of wlans base on the parameter
    Input: zd: the Zone Director object
           wlan_conf_list: list of wlan configuration to be created
    """
    xlocs = LOCATORS_CFG_WLANS

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    for wlan_conf in wlan_conf_list:
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        if wlan_conf.get('type') == 'guest':
            logging.info("Create default guest access profile")
            ga.create_default_guestaccess_policy(zd)
            ga.remove_all_restricted_subnet_entries(zd)
            
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)
        try:
            if zd.s.is_visible(xlocs['create_wlan']):
                zd.s.click_and_wait(xlocs['create_wlan'])
            else:
                raise Exception('The "Create New" button is disabled')
            
            try:
                _set_wlan_cfg(zd, wlan_conf)
        
            except:
                zd.logout()
                time.sleep(pause)
                zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
                time.sleep(pause)
                zd.s.click_and_wait(xlocs['create_wlan'])

                _set_wlan_cfg(zd, wlan_conf)
                
            logging.info('Wlan %s is created successfully' % wlan_conf['ssid'])
            time.sleep(pause)

        except Exception, e:
            msg = '[Wlan %s could not be created]: %s' % (wlan_conf['ssid'], e)
            logging.info(msg)
            raise Exception(msg)


def clone_wlan(zd, ssid, new_wlan_conf, pause = 1):
    """
    Clone an existing Wlan base on the ssid and the new configuration parameters
    Input: zd: Zone Director object
           ssid: the name of the wlan will be configured
           new_wlan_conf: the expected setting will be apply
    """
    xlocs = LOCATORS_CFG_WLANS
    clone_button = xlocs['clone_wlan'] % ssid

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    while zd.s.is_visible(xlocs['show_more_button']):
        zd.s.click_and_wait(xlocs['show_more_button'])
        time.sleep(pause)

    if zd.s.is_element_present(clone_button):
        zd.s.click_and_wait(clone_button)
        time.sleep(pause)
        try:
            _set_wlan_cfg(zd, new_wlan_conf)
            logging.info('Clone from WLAN [%s] successfully' % ssid)

        except:
            logging.info('Could not clone from WLAN [%s]' % ssid)
            raise
    else:
        raise Exception('The WLAN [%s] does not exist' % ssid)


def edit_wlan(zd, ssid, new_wlan_conf, pause = 1,get_alert=True,clear_search_box = True):
    """
    Edit an existing Wlan base on the ssid and the new configuration parameters
    Input: zd: Zone Director object
           ssid: the name of the wlan will be configured
           new_wlan_conf: the expected setting will be apply
    """
    xlocs = LOCATORS_CFG_WLANS
    edit_button = xlocs['edit_wlan'] % ssid

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    #cwang@2010-9-30, update for scaling testing.
    try:
        zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = False)
    except Exception, e:
        logging.debug(e.message)
        zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = True)
#        raise Exception('Element [%s] not found' % xlocs['wlan_search_textbox'])

    try:

        while zd.s.is_visible(xlocs['show_more_button']):
            zd.s.click_and_wait(xlocs['show_more_button'])
            time.sleep(pause)

        if zd.s.is_element_present(edit_button):
            zd.s.click_and_wait(edit_button)
            time.sleep(pause)
            try:
                _set_wlan_cfg(zd, new_wlan_conf, False, get_alert=get_alert)
                logging.info('WLAN [%s] is editted successfully' % ssid)

            except:
                logging.info('WLAN [%s] could not be editted' % ssid)
                raise
        else:
            raise Exception('The WLAN [%s] does not exist' % ssid)

    finally:
        if clear_search_box:
            zd._fill_search_txt(xlocs['wlan_search_textbox'], '')

#added by west.li
#del a wlan in zd
def del_wlan(zd, ssid,pause = 1):
    """
    delete an existing Wlan base on the ssid
    """
    xlocs = LOCATORS_CFG_WLANS
    check_box=xlocs['wlan_checkbox'] % ssid

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    try:
        zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = False)
    except Exception, e:
        logging.debug(e.message)
        zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = True)

    try:
        while zd.s.is_visible(xlocs['show_more_button']):
            zd.s.click_and_wait(xlocs['show_more_button'])
            time.sleep(pause)

        if zd.s.is_element_present(check_box):
            zd._delete_element(check_box, xlocs['delete_button'], "one wlan")
            logging.info('WLAN [%s] is delted successfully' % ssid)
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception(msg_alert)
        else:
            raise Exception('The WLAN [%s] does not exist' % ssid)

    finally:
        zd._fill_search_txt(xlocs['wlan_search_textbox'], '')


def edit_multi_wlans(zd, wlan_name_list, configuration, pause = 1):
    """
    Edit multi wlans to use the same configuration. Not apply to 'ssid' which could not be same.
    Input: zd: Zone Director object
           wlan_name_list: list ssid of the wlans will be editted
           configuration: the dictionary of wlan configuration will be applied
    """
    xlocs = LOCATORS_CFG_WLANS

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    while zd.s.is_visible(xlocs['show_more_button']):
        zd.s.click_and_wait(xlocs['show_more_button'])
        time.sleep(pause)

    for wlan_name in wlan_name_list:
        edit_button = xlocs['edit_wlan'] % wlan_name
        if not zd.s.is_element_present(edit_button):
            raise Exception('The wlan [%s] does not exist' % wlan_name)

        zd.s.click_and_wait(edit_button)
        time.sleep(pause)
        try:
            _set_wlan_cfg(zd, configuration, False)
            logging.info('Wlan %s is editted successfully' % wlan_name)
            time.sleep(pause)

        except:
            raise


def delete_all_wlans(zd, pause = 1):
    """
    Remove all configured wlans out of the WLANs table
    Input: zd: Zone Directot object
    """
    logging.info('remove wlan in zd %s' % zd.ip_addr)
    xlocs = LOCATORS_CFG_WLANS
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    total_wlans = int(zd._get_total_number(xlocs['total_wlans_span'], 'WLAN'))
    if total_wlans == 0:
        logging.info("There is no wlan in the table")
        return

    while total_wlans:
        a = xlocs['check_all_checkbox']
        zd._delete_element(a, xlocs['delete_button'], "all wlans")
        if (zd.s.is_alert_present(5)):
            msg_alert = zd.s.get_alert()
            raise Exception(msg_alert)

        total_wlans = int(zd._get_total_number(xlocs['total_wlans_span'], 'WLAN'))

    logging.info("Delete all wlans successfully")


def get_wlan_list(zd, pause = 10):
    """
    Return the Wlan name list on the Wlan table of Zone Director
    """
    xlocs = LOCATORS_MON_WLANS
    zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN)
    if not zd._wait_for_element(xlocs['wlan_tbl_nav_loc'], pause):
        raise Exception('Not find element [%s]' % xlocs['wlan_tbl_nav_loc'])

    wlan_list = []
    wlan_list = wgt.get_tbl_rows(zd.s, xlocs['wlan_tbl_loc'], xlocs['wlan_tbl_nav_loc'])

    #Modified by Serena Tan, 2010.12.6. Behavior change after Toronto 9.1.0.0.17
#    wlan_name_list = [wlan['names_essids'] for wlan in wlan_list]
    wlan_name_list = []
    for wlan in wlan_list:
        if wlan.has_key('names_essids'):
            wlan_name_list.append(wlan['names_essids'])
        else:
            wlan_name_list.append(wlan['name'])

    return wlan_name_list


def get_wlan_cfg_list(zd, pause = 1):
    """
    Return the WLAN cfg list on WLAN table of ZOne Director.
    """
    xlocs = LOCATORS_MON_WLANS
    zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN)
    time.sleep(pause)

    wlan_list = []
    wlan_list = wgt.get_tbl_rows(zd.s, xlocs['wlan_tbl_loc'], xlocs['wlan_tbl_nav_loc'])
    return wlan_list

def get_wlan_cfg_list_2(zd, is_nav = True):
    """
    . to get the WLAN cfg list on WLAN table from Configure > WLANs page. It is
    to support to verify provisioning result of ZD template from FM.
    . is_nav: this param to support get wlan cfg list on ZD template from
              FlexMaster. If do this from FM, don't navigate.
    """
    l = LOCATORS_CFG_WLANS
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(0.5)

    wlan_list = wgt.get_tbl_rows(zd.s, l['wlan_tbl'], l['wlan_tbl_nav'])

    return wlan_list

def download_generated_dpsk_record(zd, filename = None, filename_re = None, pause = 1):
    xlocs = LOCATORS_CFG_WLANS
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    loc = xlocs['batch_dpsk_download_button']
    try:
        return _download_single_file(zd, loc, filename, filename_re)

    except:
        raise


def generate_multiple_dpsk(zd, dpsk_conf, pause = 1):
    conf = {'psk_expiration': None,
            'wlan': None,
            'number_of_dpsk': None,
            'profile_file': None,
            'repeat': False,
            'expected_response_time': 10,
            'vlan': '',
            'role' : None
            }

    conf.update(dpsk_conf)
    if conf['psk_expiration'] is not None:
        #Chico, 2014-12-4, ZF-11024
        try:
            new_wlan_cfg = {'ssid':conf['wlan'], 'dpsk_expiration':conf['psk_expiration']}
            edit_wlan(zd, conf['wlan'], new_wlan_cfg)
        except:
            zd.set_dynamic_psk_cfg(conf['psk_expiration'])
        #Chico, 2014-12-4, ZF-11024
        
    xlocs = LOCATORS_CFG_WLANS
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    if conf['wlan'] is not None:
        zd.s.select_option(xlocs['batch_dpsk_wlan_target_option'], conf['wlan'])

    if conf['role'] is not None:
        zd.s.select_option(xlocs['batch_dpsk_role_target_option'], conf['role'])

    while True:
        if conf['number_of_dpsk']:
            zd.s.type_text(xlocs['batch_dpsk_number_create_textbox'], conf['number_of_dpsk'])
        
            #@since: Mar 2012, An Nguyen, added the option to configure the dynamic vlan.
            if conf['vlan']:
                zd.s.type_text(xlocs['batch_dpsk_dynamic_vlan_textbox'], conf['vlan'])

        elif conf['profile_file']:
            zd.s.type_text(xlocs['batch_dpsk_profile_file_textbox'], conf['profile_file'])
            _wait_for_processing(zd, LOCATORS_CFG_WLANS['loc_uploadbatchdpsk_msg_span'], \
                               'Uploading', conf['expected_response_time'], pause)
            time.sleep(pause * 2 + 10)
            
            #An Nguyen, an.nguyen@ruckuswireless.com 
            #@since: July 2012 to add the step to verify the invalid file
            msg = zd.s.get_text(LOCATORS_CFG_WLANS['loc_uploadbatchdpsk_error_span'])
            if 'The profile has been uploaded' not in msg:
                raise Exception(msg)
            
        zd.s.click(xlocs['batch_dpsk_generate_button'])
        _wait_for_processing(zd, LOCATORS_CFG_WLANS['loc_batch_dpsk_msg_span'], 'Processing', \
                             conf['expected_response_time'], pause * 2)

        if not conf['repeat']:
            break


def set_psk_expiration(zd, option, pause = 1, is_nav = True):
    '''
    . get psk expiration
    . is_nav: this param to support set psk  on ZD template from
              FlexMaster. If do this from FM, don't navigate.
    '''
    xlocs = LOCATORS_CFG_WLANS
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)

    zd.s.select_option(xlocs['psk_expiration'], option)
    zd.s.click_and_wait(xlocs['psk_apply_button'])


def get_psk_expiration(zd, pause = 1, is_nav = True):
    '''
    . get psk expiration
    . is_nav: this param to support get psk info on ZD template from
              FlexMaster. If do this from FM, don't navigate.
    '''
    xlocs = LOCATORS_CFG_WLANS
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)

    return zd.s.get_selected_option(xlocs['psk_expiration'])


def auto_del_expire_dpsk_enabled(zd, pause = 1, is_nav = True):
    xlocs = LOCATORS_CFG_WLANS
    check_box = xlocs['auto_del_expire_dpsk_checkbox']
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)
    if zd.s.is_checked(check_box):
        return True
    else:
        return False

def enable_auto_del_expire_dpsk(zd, pause = 1, is_nav = True):
    xlocs = LOCATORS_CFG_WLANS
    check_box = xlocs['auto_del_expire_dpsk_checkbox']
    button = xlocs['psk_apply_button']
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)
    zd.s.click_if_not_checked(check_box)
    zd.s.click_and_wait(button)
    
def disable_auto_del_expire_dpsk(zd, pause = 1, is_nav = True):
    xlocs = LOCATORS_CFG_WLANS
    check_box = xlocs['auto_del_expire_dpsk_checkbox']
    button = xlocs['psk_apply_button']
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)
    zd.s.click_if_checked(check_box)
    zd.s.click_and_wait(button)


def set_zeroit_auth_server(zd, server, pause = 1, is_nav = True):
    '''
    '''
    xlocs = LOCATORS_CFG_WLANS
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)

    zd.s.select_option(xlocs['zero_it_authentication_server'], server)
    zd.s.click_and_wait(xlocs['zero_it_apply_button'])


def get_zeroit_auth_server(zd, pause = 1, is_nav = True):
    '''
    '''
    xlocs = LOCATORS_CFG_WLANS
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)

    return zd.s.get_selected_value(xlocs['zero_it_authentication_server'])


def _wait_for_processing(zd, loc, msg, expected_response_time = 20, pause = 2,):
    start_time = time.time()
    
    while True:
        if time.time() - start_time > expected_response_time:
            raise Exception('ZD took over %s seconds to perform the action.' % expected_response_time)

        if zd.s.is_visible(loc):
            msg_batch_dpsk = zd.s.get_text(loc)

            if msg in msg_batch_dpsk:
                time.sleep(pause)
                continue     
        break

    if zd.s.is_alert_present(5):
        alertMsg = zd.s.get_alert()
        if len(alertMsg) > 0:
            raise Exception(alertMsg)

    # increase the pause time to wait for ZD internal process
    #time.sleep(pause * 2 + 10)


def _set_wlan_cfg(zd, wlan_conf, is_create = True, get_alert=True):
    """
    Editing wlan configuration using input paramters. The WLAN configuration dialog is supposed to be
    displayed before calling this function.
    @param zd: the reference to the Zone Director object
    @param wlan_conf: a dictionary contains configuration of a WLAN
    """
    if is_create == True:
        conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
            'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
            'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None, 'do_service_schedule':None,
            'acl_name': '', 'l3_l4_acl_name': '', 'l3_l4_ipv6_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '', 'dvlan': None,
            'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'do_proxy_arp': None, 'acct_svr': '', 'interim_update': None, 'priority': None, 'fingerprinting': None,
            'inactivity_timeout': None, 'do_grace_period': None, 'grace_period': None, 'option82':None, 'force_dhcp':None, 'force_dhcp_timeout':None,
            'ignore_unauth_stats':None, 'dpsk_expiration':None,'enable_application_visibility':None,'application_denial_policy':None,
            }
    else:
        conf={}
    
    conf.update(wlan_conf)
    
    if conf.has_key('auth') and conf['auth'] == 'PSK':
        conf['auth'] = 'open'
    locs = LOCATORS_CFG_WLANS

    if conf.has_key('ssid') and conf['ssid'] is not None:
        zd.s.type_text(locs['ssid_name_textbox'], conf['ssid'])
        #cwang@2010-11-1, behavior change after 9.1.0.0.9
        
        if zd.s.is_element_present(locs['ssid_textbox']):
            if conf.has_key('name') and conf['name'] is not None:
                zd.s.type_text(locs['ssid_textbox'], conf['name'])
            else:
                zd.s.type_text(locs['ssid_textbox'], conf['ssid'])

    if conf.has_key('description') and conf['description'] is not None:
        zd.s.type_text(locs['description_textbox'], conf['description'])

    if conf.has_key('type'):
        if  conf['type'] == 'standard':
            zd.s.click_and_wait(locs['usage_standard_radio'])

        elif conf['type'] == 'guest':
            zd.s.click_and_wait(locs['usage_guest_radio'])

        elif conf['type'] == 'hotspot':
            zd.s.click_and_wait(locs['usage_wispr_radio'])
            if conf.has_key('hotspot_profile') and conf['hotspot_profile']:
                zd.s.select_option(locs['hotspot_option'], conf['hotspot_profile'])
                zd.s.click_and_wait(locs['hotspot_option'])

        elif conf['type'] == 'autonomous':
            zd.s.click_and_wait(locs['usage_autonomous_radio'])

    if conf.has_key('auth') and conf['auth']:
        zd.s.click_and_wait(locs['%s_radio' % conf['auth'].lower()])

    if conf.has_key('wpa_ver') and conf['wpa_ver']:
        zd.s.click_and_wait(locs['%s_radio' % conf['wpa_ver'].lower()])
        if conf.has_key('encryption'):
            if conf['encryption'] in ['TKIP', 'AES', 'Auto']:
                zd.s.click_and_wait(locs['%s_radio' % conf['encryption'].lower()])

        if conf.has_key('key_string'):
            if conf['key_string'] and zd.s.is_visible(locs['passphrase_textbox']):
                zd.s.type_text(locs['passphrase_textbox'], conf['key_string'])

    elif conf.has_key('encryption') and conf['encryption'] in ['WEP-64', 'WEP-128']:
        x = conf['encryption'].replace('-', '').lower()
        zd.s.click_and_wait(locs['%s_radio' % x])
        if conf.has_key('key_index') and conf['key_index']:
            zd.s.click_and_wait(locs['wepkey_index_radio'] % conf['key_index'])

        if conf.has_key('key_string') and conf['key_string'] and zd.s.is_visible(locs['wepkey_textbox']):
            zd.s.type_text(locs['wepkey_textbox'], conf['key_string'])

    elif conf.has_key('encryption') and conf['encryption'] == 'none':
        zd.s.click_and_wait(locs['none_radio'])

    if conf.has_key('do_webauth') and conf['do_webauth'] is not None:
        is_checked = zd.s.is_checked(locs['web_auth_checkbox'])
        if conf['do_webauth'] and not is_checked or not conf['do_webauth'] and is_checked:
            zd.s.click_and_wait(locs['web_auth_checkbox'])

    if conf.has_key('auth_svr') and conf['auth_svr']:
        if conf.has_key('auth') and (conf['auth'] == 'EAP' or conf['auth'] == 'eap'):
            x = locs['authsvr_eap_select']

        elif conf.has_key('auth') and (conf['auth'] == 'mac' or conf['auth'] == 'maceap' ):
            x = locs['authsvr_mac_select']

        else:
            x = locs['authsvr_web_select']

        zd.s.select_option(x, conf['auth_svr'])
        zd.s.click_and_wait(x)

    if conf.has_key('do_isolation') and conf['do_isolation'] is not None:
        xpath_by_mode = {
            'none': locs['client_isolation_none_radio'],
            'local': locs['client_isolation_local_radio'],
            'full': locs['client_isolation_full_radio'],
        }
        # for 9.0, 9.1, 9.2... that have [none, local, full] isolation radio buttons
        if conf['do_isolation'] in xpath_by_mode.keys():
            zd.s.click_if_not_checked(xpath_by_mode[conf['do_isolation']])

        # prior to 9.0 (only has a checkbox)
        else:
            if conf['do_isolation']:
                zd.s.click_if_not_checked(locs['client_isolation_checkbox'])

            else:
                zd.s.click_if_checked(locs['client_isolation_checkbox'])

    if conf.has_key('do_zero_it') and conf['do_zero_it'] is not None:
        is_checked = zd.s.is_checked(locs['zeroit_checkbox'])
        if conf['do_zero_it'] and not is_checked or not conf['do_zero_it'] and is_checked:
            zd.s.click_and_wait(locs['zeroit_checkbox'])

    if conf.has_key('do_dynamic_psk') and conf['do_dynamic_psk'] is not None:
        if not zd.s.is_visible(locs['dynamic_psk_checkbox']):
            raise Exception('The dynamic psk checkbox is not visible')
        is_checked = zd.s.is_checked(locs['dynamic_psk_checkbox'])
        if conf['do_dynamic_psk'] and not is_checked or not conf['do_dynamic_psk'] and is_checked:
            zd.s.click_and_wait(locs['dynamic_psk_checkbox'])

    if conf.has_key('priority'):
        if conf['priority'] == 'high' and zd.s.is_element_present(locs['priority_high_radio']):
            zd.s.click_if_not_checked(locs['priority_high_radio'])

        elif conf['priority'] == 'low' and zd.s.is_element_present(locs['priority_low_radio']):
            zd.s.click_if_not_checked(locs['priority_low_radio'])
            
    if conf.has_key('dpsk_expiration') and conf['dpsk_expiration'] is not None:
        zd.s.select_option(zd.info['loc_cfg_wlans_dynpsk_expire_option'], conf['dpsk_expiration'])

    # Advanced configuration
    _set_wlan_advanced_cfg(zd, conf)

    zd.s.click_and_wait(locs['ok_button'])

    # If an alert of wrong configuration(ex: wrong wlan name, duplicated name...) appears,
    # click the Cancel button
    if get_alert:
        zd.s.get_alert(locs['cancel_button'])


def _set_wlan_advanced_cfg(zd, conf, pause = 2.0):
    locs = LOCATORS_CFG_WLANS

    zd.s.click_and_wait(locs['advanced_options_anchor'])

    if conf.has_key('acct_svr') and conf['acct_svr']:
        zd.s.select_option(locs['acctsvr_option'], conf['acct_svr'])
        zd.s.click_and_wait(locs['acctsvr_option'])

    if conf.has_key('interim_update') and conf['interim_update'] is not None:
        zd.s.type_text(locs['acctsvr_interim_textbox'], conf['interim_update'])

    if conf.has_key('acl_name') and conf['acl_name']:
        zd.s.select_option(locs['acl_option'], conf['acl_name'])

    if conf.has_key('l3_l4_acl_name') and conf['l3_l4_acl_name']:
        zd.s.select_option(locs['l34_acl_option'], conf['l3_l4_acl_name'])
    
    if conf.has_key('l3_l4_ipv6_acl_name') and conf['l3_l4_ipv6_acl_name']:
        zd.s.select_option(locs['l34_ipv6_acl_option'], conf['l3_l4_ipv6_acl_name'])
    #chen.tao 2014-6-25    
    if conf.has_key('enable_application_visibility') and conf['enable_application_visibility']:
        zd.s.click_if_not_checked(locs['application_visibility_checkbox'])

    #chen.tao 2014-6-25    
    if conf.has_key('application_denial_policy') and conf['application_denial_policy']:
        zd.s.select_option(locs['application_denial_policy_select'], conf['application_denial_policy'])
    if conf.has_key('uplink_rate_limit') and conf['uplink_rate_limit']:
        zd.s.select_option(locs['uplink_rate_option'], conf['uplink_rate_limit'])
        zd.s.click_and_wait(locs['uplink_rate_option'])

    if conf.has_key('downlink_rate_limit') and conf['downlink_rate_limit']:
        zd.s.select_option(locs['downlink_rate_option'], conf['downlink_rate_limit'])
        zd.s.click_and_wait(locs['downlink_rate_option'])
    if conf.has_key('mcast_filter') and conf['mcast_filter']:
        zd.s.click_if_not_checked(locs['mcast_filter_option'])
    else:
        zd.s.click_if_checked(locs['mcast_filter_option']) 
    if conf.has_key('vlan_id'):
        vlan_id = conf.get('vlan_id')
        if vlan_id:
            #Update for 9.4 change remove enable vlan checkbox.
            if zd.s.is_element_present(locs['do_vlan_checkbox']):
                zd.s.click_if_not_checked(locs['do_vlan_checkbox'], 0.5)
            zd.s.type_text(locs['vlan_id_textbox'], conf['vlan_id'])
        
        else:
            if zd.s.is_element_present(locs['do_vlan_checkbox']):
                zd.s.click_if_checked(locs['do_vlan_checkbox'], 0.5)
            zd.s.type_text(locs['vlan_id_textbox'], '1')

    if conf.get('dvlan') != None:
        if not zd.s.is_editable(locs['do_dvlan_checkbox']):
            raise Exception('The dvlan checkbox is disable')
        is_checked = zd.s.is_checked(locs['do_dvlan_checkbox'])
        if conf['dvlan'] and not is_checked or not conf['dvlan'] and is_checked:
            zd.s.click_and_wait(locs['do_dvlan_checkbox'])        

    if conf.has_key('do_hide_ssid') and conf['do_hide_ssid'] is not None:
        is_checked = zd.s.is_checked(locs['do_beacon_checkbox'])
        if conf['do_hide_ssid'] and not is_checked or not conf['do_hide_ssid'] and is_checked:
            zd.s.click_if_not_checked(locs['do_beacon_checkbox'])

    if conf.has_key('do_tunnel') and conf['do_tunnel'] is not None:
        is_checked = zd.s.is_checked(locs['do_tunnel_checkbox'])
        if conf['do_tunnel'] and not is_checked:
            zd.s.click_if_not_checked(locs['do_tunnel_checkbox'])
        elif not conf['do_tunnel'] and is_checked:
            zd.s.click_if_checked(locs['do_tunnel_checkbox'])

    if conf.has_key('do_proxy_arp') and conf['do_proxy_arp'] is not None:
        is_checked = zd.s.is_checked(locs['do_proxy_arp_checkbox'])
        if conf['do_proxy_arp'] and not is_checked:
            zd.s.click_if_not_checked(locs['do_proxy_arp_checkbox'])
        elif not conf['do_proxy_arp'] and is_checked:
            zd.s.click_if_checked(locs['do_proxy_arp_checkbox'])

    if conf.has_key('inactivity_timeout') and conf['inactivity_timeout'] is not None:
        zd.s.type_text(locs['inactivity_timeout_textbox'], conf['inactivity_timeout'])
        
    if conf.has_key('do_service_schedule') and conf['do_service_schedule'] is not None:
        schedule = conf['do_service_schedule']
        _set_wlan_service_schedule(zd, schedule)
        logging.info('wlan service schedule %s setting is successful' % schedule)

    if conf.has_key('do_grace_period'):
        if conf['do_grace_period'] == True:
            zd.s.click_if_not_checked(locs['grace_period_checkbox'])
            if conf['grace_period'] is not None:
                zd.s.type_text(locs['grace_period_textbox'], conf['grace_period'])
    
        elif conf['do_grace_period'] == False:
            zd.s.click_if_checked(locs['grace_period_checkbox'])
            
        else:#@author: anzuo, @change: 9.9 grace period is enabled by default when create wlan
            zd.s.click_if_checked(locs['grace_period_checkbox'])

    if conf.has_key('option82') and conf['option82'] is not None:
        option82 = conf['option82']
        if option82:
            zd.s.click_if_not_checked(locs['loc_option82_checkbox'])
        else:
            zd.s.click_if_checked(locs['loc_option82_checkbox'])
    
    #Jane.Guo@2013-5-7 add Force DHCP
    if conf.has_key('force_dhcp') and conf['force_dhcp'] is not None:
        force_dhcp = conf['force_dhcp']
        if force_dhcp:
            zd.s.click_if_not_checked(locs['loc_force_dhcp_checkbox'])
        else:
            zd.s.click_if_checked(locs['loc_force_dhcp_checkbox'])
            
    if conf.has_key('force_dhcp_timeout') and conf['force_dhcp_timeout'] is not None:
        zd.s.type_text(locs['loc_force_dhcp_timeout_textbox'], conf['force_dhcp_timeout'])
            
    if conf.has_key('do_wmm_ac'):
        if conf['do_wmm_ac'] == True:
            zd.s.click_if_not_checked(locs['loc_do_wmm_ac_checkbox'])
        elif conf['do_wmm_ac'] == False:
            zd.s.click_if_checked(locs['loc_do_wmm_ac_checkbox'])

    if conf.has_key('fingerprinting') and conf['fingerprinting'] is not None:
        fingerprinting = conf['fingerprinting']
        if fingerprinting:
            zd.s.click_if_not_checked(locs['loc_fingerprinting_checkbox'])
        else:
            zd.s.click_if_checked(locs['loc_fingerprinting_checkbox'])
    if conf.has_key('max_client') and conf['max_client']:
        zd.s.type_text(locs['max_clients_textbox'], conf['max_client'])
    
    if conf.has_key('ignore_unauth_stats') and conf['ignore_unauth_stats'] is not None:
        ignore_unauth_stats = conf.get('ignore_unauth_stats')
        if ignore_unauth_stats:
            zd.s.click_if_not_checked(locs['loc_authstats_checkbox'])
        else:
            zd.s.click_if_checked(locs['loc_authstats_checkbox'])
    
    #An Nguyen@Dec2012 added the step to configure the DHCP relay option on WLAN
    if conf.has_key('dhcp_relay_svr'):
        _config_dhcp_relay_option(zd, conf['dhcp_relay_svr'])
        

def _download_single_file(zd, loc, filename = None, filename_re = None, pause = 30):
    try:
        # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
        dlg_mgr = DialogManager()
        dlg1 = BaseDialog(title = None, text = "", button_name = "", key_string = "{PAUSE 3} %s {ENTER}")
        dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "", key_string = "%{F4}")

        dlg_mgr.add_dialog(dlg1)
        dlg_mgr.add_dialog(dlg2)

        if filename is not None:
            # Make the path to the file, which is supposed to be saved on the Desktop of the current logged in user
            file_path = os.path.join(constant.save_to, filename)

            # Remove it if it is existing
            if os.path.isfile(file_path):
                os.remove(file_path)

        elif filename_re is not None:
            dlg1.set_title_re("Opening %s" % filename_re)

        dlg_mgr.start()
        zd.s.click_and_wait(loc)
        time.sleep(5)

        if filename_re is not None:
            m = re.search("Opening (%s)" % filename_re, dlg1.get_title())
            if m: filename = m.groups()[0]#Chico, 2015-8-11, filename is tuple here (u'batch_dpsk_081115_10_10.csv',)

            file_path = os.path.join(constant.save_to, filename)
            #chen.tao 2015-01-06, to resolve the download path problem
            #if it is downloaded to another folder, then copy to the target folder
            try:
                if not os.path.isfile(file_path):
                    import shutil
                    file_path_desktop = os.path.join(os.path.expanduser('~'), r"Desktop\%s" % filename)
                    shutil.copy(file_path_desktop,file_path) 
            except:
                pass
        # Wait until the file is saved
        t0 = time.time()
        while time.time() - t0 < pause:
            if os.path.isfile(file_path): break

        if os.path.isfile(file_path):
            return file_path

    except:
        logging.info("Unable to download and save the file to [%s]" % file_path)
        raise

    finally:
        # Regardless what has happened, stop the dialog handlers
        time.sleep(5)
        dlg_mgr.shutdown()
        time.sleep(2)

def get_all_wlan_conf_detail(zd, wlan_name_list, pause = 1, is_nav = True):
    xlocs = LOCATORS_CFG_WLANS
    wlans_cfg = {}
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)

    while zd.s.is_visible(xlocs['show_more_button']):
        zd.s.click_and_wait(xlocs['show_more_button'])

    for wlan_name in wlan_name_list:
        edit_button = xlocs['edit_wlan'] % wlan_name
        if not zd.s.is_element_present(edit_button):
            raise Exception('The wlan [%s] does not exist' % wlan_name)

        zd.s.click_and_wait(edit_button)
        time.sleep(pause)
        try:
            wlans_cfg[wlan_name] = _get_wlan_conf_detail(zd, wlan_name)
            zd.s.click_and_wait(xlocs['cancel_button'])
            logging.info('Get Wlan %s configuration successfully' % wlan_name)
            time.sleep(pause)

        except:
            raise
    return wlans_cfg


def get_wlan_info_detail(zd, wlan_name, pause = 1):
    """
    Get WLAN Information indcator.
    @param zd: The Zone Dirctor instance.
    @param wlan_name: ssid name.   
    """
    xlocs = LOCATORS_MON_WLANS
    zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN, force=True)
    time.sleep(pause)
    try:
        zd._fill_search_txt(xlocs['wlan_tbl_filter_txt'] % tbl_id['wlan_summary'], wlan_name, is_refresh = False)

    except Exception, e:
        logging.debug(e.message)
        zd._fill_search_txt(xlocs['wlan_tbl_filter_txt'] % tbl_id['wlan_summary'], wlan_name, is_refresh = True)
    
    wlan_info = {}
    a_link = xlocs['wlan_link'] % wlan_name
    zd.s.click_and_wait(a_link)
    time.sleep(pause)
    try:
        wlan_info = _get_wlan_info_detail(zd, wlan_name)        
        logging.info('Get Wlan %s information successfully' % wlan_name)        
    except:
        raise
    finally:
        zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN, force=True)
        time.sleep(pause)
        
    return wlan_info
    

##############
#add by louis for get wlan config info from ZD GUI.

def get_wlan_conf_detail(zd, wlan_name, pause = 1, is_nav = True):
    """
    Get WLAN configuration parameter
    Input: zd: the Zone Director object
           wlan_name: WLAN name which are getted.
           is_nav: this param to support config wlan group on ZD template in
    """
    xlocs = LOCATORS_CFG_WLANS
    edit_button = xlocs['edit_wlan'] % wlan_name
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
        time.sleep(pause)

    try:
        zd._fill_search_txt(xlocs['wlan_search_textbox'], wlan_name, is_refresh = False)

    except Exception, e:
        logging.debug(e.message)
        zd._fill_search_txt(xlocs['wlan_search_textbox'], wlan_name, is_refresh = True)

    wlan_cfg = {}
    if zd.s.is_element_present(edit_button):
        zd.s.click_and_wait(edit_button)
        wlan_cfg = _get_wlan_conf_detail(zd, wlan_name)
        zd.s.click_and_wait(xlocs['cancel_button'])

    return wlan_cfg


def _get_wlan_info_detail(zd, wlan_name):
    wlan_info = {}
    locs = LOCATORS_MON_WLANS['wlan_detail_loc']
    for item in locs:
        wlan_info[item] = zd.s.get_text(locs[item])
        
    wlan_info['name'] = wlan_name
    return wlan_info
    

def _get_wlan_conf_detail(zd,wlan_name):
    wlan_conf = {}
    locs = LOCATORS_CFG_WLANS
    wlan_conf['name'] = wlan_name
    wlan_conf['ssid'] = zd.s.get_value(locs['ssid_textbox'])

    wlan_conf['description'] = zd.s.get_value(locs['description_textbox'])

    type_level = dict(
                      usage_standard_radio =locs['usage_standard_radio'],
                      usage_guest_radio = locs['usage_guest_radio'],
                      usage_wispr_radio = locs['usage_wispr_radio']
                      )
    type_radio = zd.s.get_radio_group_value(type_level)
    if type_radio == "usage_standard_radio":
        type = "standard-usage"
    elif type_radio == "usage_guest_radio":
        type = "guest-access"
    else:
        type = "hotspot"

    wlan_conf['type'] = type

    authentication_type = dict(
                              open_radio = locs['open_radio'],
                              shared_radio = locs['shared_radio'],
                              eap_radio = locs['eap_radio'],
                              mac_radio = locs['mac_radio'],
                              maceap_radio = locs['maceap_radio']
                              )

    auth_radio = zd.s.get_radio_group_value(authentication_type)
    if auth_radio == 'open_radio':
        auth = 'open'
    elif auth_radio =='shared_radio':
        auth = 'shared'
    elif auth_radio == 'eap_radio':
        auth = 'dot1x-eap'
    elif auth_radio == 'mac_radio':
        auth ='mac'
    else:
        auth = 'maceap'

    wlan_conf['auth'] = auth

    encryption_type = dict(
                           none_radio = locs['none_radio'],
                           wpa_radio = locs['wpa_radio'],
                           wpa2_radio = locs['wpa2_radio'],
                           wpa_mixed_radio = locs['wpa_mixed_radio'],
                           wep64_radio = locs['wep64_radio'],
                           wep128_radio = locs['wep128_radio']
                           )

    encryption_radion = zd.s.get_radio_group_value(encryption_type)
    if encryption_radion == 'none_radio':
        encryption = 'none'
    elif encryption_radion == 'wpa_radio':
        encryption = 'wpa'
    elif encryption_radion == 'wpa2_radio':
        encryption ='wpa2'
    elif encryption_radion == 'wpa_mixed_radio':
        encryption = 'wpa-mixed'
    elif encryption_radion == 'wep64_radio':
        encryption = 'wep-64'
    else:
        encryption = 'wep-128'

    wlan_conf['encryption'] = encryption

    if encryption in ['wpa','wpa2','wpa-mixed']:
        algorithm_type = dict(
                              tkip_radio = locs['tkip_radio'],
                              aes_radio = locs['aes_radio'],
                              auto_radio = locs['auto_radio']
                              )
        algorithm_radio = zd.s.get_radio_group_value(algorithm_type)
        if algorithm_radio == 'tkip_radio':
            algorithm = 'tkip'
        elif algorithm_radio == 'aes_radio':
            algorithm = 'aes'
        else:
            algorithm = 'auto'
        wlan_conf['algorithm'] = algorithm
        passphrase = zd.s.get_value(locs['passphrase_textbox'])
        wlan_conf['passphrase'] = passphrase
    elif (encryption in ['wep-64','wep-128']) and (wlan_conf['auth'] in ['open','shared','mac']):
        wep_key_index_loc = locs['wepkey_index_radio']
        wep_key_index = 0
        for i in range(1,5):
            loc = wep_key_index_loc % i
            if zd.s.is_checked(loc):
                wep_key_index = i
                break;
        wep_key = zd.s.get_value(locs['wepkey_textbox'])

        wlan_conf['wep_key_index'] = wep_key_index
        wlan_conf['wep_key'] = wep_key

    if type == 'standard-usage':
        if auth in['open','shared']:
            if zd.s.is_checked(locs['web_auth_checkbox']):
                wlan_conf['web_auth'] = 'Enabled'
                wlan_conf['auth_server'] = zd.s.get_selected_label(locs['authsvr_web_select'])
            else:
                wlan_conf['web_auth'] = 'Disabled'
                wlan_conf['auth_server'] = 'Disabled'
        else:
            wlan_conf['auth_server'] = zd.s.get_selected_label(locs['authsvr_web_select'])

        if zd.s.is_checked(locs['zeroit_checkbox']):
            wlan_conf['zero_it'] = 'Enabled'
        else:
            wlan_conf['zero_it'] = 'Disabled'

    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#    client_isolation_type = dict(
#                                client_isolation_none_radio = locs['client_isolation_none_radio'],
#                                client_isolation_local_radio = locs['client_isolation_local_radio'],
#                                client_isolation_full_radio = locs['client_isolation_full_radio']
#                                )
#    isolation = zd.s.get_radio_group_value(client_isolation_type)
#    if isolation == 'client_isolation_none_radio':
#        client_isolation = 'None'
#    elif isolation == 'client_isolation_local_radio':
#        client_isolation = 'Local'
#    else:
#        client_isolation = 'Full'
#
#    wlan_conf['client_isolation'] = client_isolation

    priority_level = dict(
                          priority_high_radio = locs['priority_high_radio'],
                          priority_low_radio = locs['priority_low_radio']
                          )
    if zd.s.get_radio_group_value(priority_level) == 'priority_high_radio':
        wlan_conf['priority'] = 'High'
    else:
        wlan_conf['priority'] = 'Low'

    zd.s.click_and_wait(locs['advanced_options_anchor'])

    wlan_conf['acc_server'] = zd.s.get_selected_label(locs['acctsvr_option'])
    if wlan_conf['acc_server'] !=  'Disabled':
        wlan_conf['interim'] = zd.s.get_value(locs['acctsvr_interim_textbox'])

    wlan_conf['l2acl'] = zd.s.get_selected_label(locs['acl_option'])
    wlan_conf['l3acl'] = zd.s.get_selected_label(locs['l34_acl_option'])
    wlan_conf['l3acl_ipv6'] = zd.s.get_selected_label(locs['l34_ipv6_acl_option'])

    wlan_conf['rate_limit_uplink'] = zd.s.get_selected_label(locs['uplink_rate_option'])
    wlan_conf['rate_limit_downlink'] = zd.s.get_selected_label(locs['downlink_rate_option'])
    
    if zd.s.is_element_present(locs['do_vlan_checkbox']):
        if zd.s.is_checked(locs['do_vlan_checkbox']):
            wlan_conf['vlan'] = 'Enabled'
            wlan_conf['vlan_id'] = zd.s.get_value(locs['vlan_id_textbox'])
        else:
            wlan_conf['vlan'] = 'Disabled'
    else:
        #Update for 9.4 change remove enable vlan checkbox.
        wlan_conf['vlan'] = 'Enabled'
        wlan_conf['vlan_id'] = zd.s.get_value(locs['vlan_id_textbox'])
    
    if zd.s.is_checked(locs['do_dvlan_checkbox']):
        wlan_conf['dvlan'] = 'Enabled'
    else:
        wlan_conf['dvlan'] = 'Disabled'

    if zd.s.is_checked(locs['do_beacon_checkbox']):
        wlan_conf['hide_ssid'] = 'Enabled'
    else:
        wlan_conf['hide_ssid'] = 'Disabled'

    if zd.s.is_checked(locs['do_tunnel_checkbox']):
        wlan_conf['tunnel_mode'] = 'Enabled'
    else:
        wlan_conf['tunnel_mode'] = 'Disabled'

    #add bgscanning and load balancing logic.
    # if bgscan is enabled, load balancing is disabled.
    if zd.s.is_checked(locs['bgscan_checkbox']):
        wlan_conf['bgscan'] = 'Disabled'
        if zd.s.is_checked(locs['load_balancing_checkbox']):
            wlan_conf['load_balance'] = 'Disabled'
        else:
            wlan_conf['load_balance'] = 'Enabled'
    else:
        wlan_conf['bgscan'] = 'Enabled'
        wlan_conf['load_balance'] = 'Disabled'

    wlan_conf['max_clients'] = zd.s.get_value(locs['max_clients_textbox'])

    if zd.s.is_element_present(locs['grace_period_checkbox']):
        if zd.s.is_checked(locs['grace_period_checkbox']):
            wlan_conf['grace_period'] = zd.s.get_value(locs['grace_period_textbox'])
        
        else:
            wlan_conf['grace_period'] = 'Disabled'

    if zd.s.is_checked(locs['loc_option82_checkbox']):
        wlan_conf['option82'] = 'Enabled'
    else:
        wlan_conf['option82'] = 'Disabled'
    
    #@author: Jane.Guo for Force DHCP
    #loc_force_dhcp_timeout_textbox = r"//input[@id='force-dhcp-timeout']",
    if zd.s.is_element_present(locs['loc_force_dhcp_checkbox']):
        if zd.s.is_checked(locs['loc_force_dhcp_checkbox']):
            wlan_conf['force_dhcp'] = 'Enabled'
        else:
            wlan_conf['force_dhcp'] = 'Disabled'
    
    if zd.s.is_element_present(locs['loc_force_dhcp_timeout_textbox']):
        wlan_conf['force_dhcp_timeout'] = zd.s.get_value(locs['loc_force_dhcp_timeout_textbox'])
                
    if zd.s.is_checked(locs['loc_authstats_checkbox']):
        wlan_conf['authstats'] = 'Enabled'
    else:
        wlan_conf['authstats'] = 'Disabled' 
    
    return wlan_conf



def _clear_all_wlan_service_schedule(zd):
    locs = LOCATORS_CFG_WLANS
    _timebase = {'0':range(1, 97),
                 '1':range(1, 97),
                 '2':range(1, 97),
                 '3':range(1, 97),
                 '4':range(1, 97),
                 '5':range(1, 97),
                 '6':range(1, 97),
                 }

    logging.info('Try to clear all the wlan service schedule')
    for x, values in _timebase.items():
        for y in values:
            if zd.s.is_element_present(locs['wlan_service_schedule_timebase_state_td'] % (x, y, '0')):
                logging.info('clean up d=%s, t=%s successfully' % (x, y))
            else:
                zd.s.mouse_down(locs['wlan_service_schedule_timebase_td'] % (x, y))
                zd.s.mouse_up(locs['wlan_service_schedule_timebase_td'] % (x, y))
                if zd.s.is_element_present(locs['wlan_service_schedule_timebase_state_td'] % (x, y, '0')):
                    logging.info('clean up d=%s, t=%s successfully' % (x, y))
                else:
                    raise Exception('clean up d=%s, t=%s unsuccessfully' % (x, y))

    logging.info('All of wlan service specific schedule have been removed.')



def _set_wlan_service_schedule(zd, schedule={}):
    _schedule = {'on':False,
                'off':True,
                'specific':None,
                #{'0':range(1, 97),
                #'1':range(1, 97),
                #'2':range(1, 97),
                #'3':range(1, 97),
                #'4':range(1, 97),
                #'5':range(1, 97),
                #'6':range(1, 97),
                #}
                }
    _schedule.update(schedule)
    logging.info(_schedule)
    locs = LOCATORS_CFG_WLANS
    if _schedule['on']:
        zd.s.click(locs['wlan_service_schedule_on_raido'])
    elif _schedule['off']:
        zd.s.click(locs['wlan_service_schedule_off_raido'])
    elif _schedule['specific']:
        zd.s.click(locs['wlan_service_schedule_specific_radio'])
        _timebase = {}
        _timebase.update(_schedule['specific'])
        #clear up all fristly.
        _clear_all_wlan_service_schedule(zd)
        logging.info('Start to set specific time')
        for x, values in _timebase.items():
            for y in values:
                if zd.s.is_element_present(locs['wlan_service_schedule_timebase_state_td'] % (x, y, '0')):
                    zd.s.mouse_down(locs['wlan_service_schedule_timebase_td'] % (x, y))
                    zd.s.mouse_up(locs['wlan_service_schedule_timebase_td'] % (x, y))
                    time.sleep(.2)
                    if zd.s.is_element_present(locs['wlan_service_schedule_timebase_state_td'] % (x, y, '1')):
                        logging.info('set d=%s, t=%s successfully' % (x, y))
                    else:
                        raise Exception('set d=%s, t=%s unsuccessfully' % (x, y))
    else:
        raise Exception('Unknown parameters %s' % _schedule)

def set_wlan_max_clients_number(zd,wlan_name,number):
    cfg={'max_client':number}
    edit_wlan(zd,wlan_name,cfg)


def get_wlan_max_clients_number(zd,ssid,pause=1):
    xlocs = LOCATORS_CFG_WLANS
    edit_button = xlocs['edit_wlan'] % ssid

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    time.sleep(pause)


    try:
        zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = False)
    except Exception, e:
        logging.debug(e.message)
        zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = True)


    while zd.s.is_visible(xlocs['show_more_button']):
        zd.s.click_and_wait(xlocs['show_more_button'])
        time.sleep(pause)

    if zd.s.is_element_present(edit_button):
        zd.s.click_and_wait(edit_button)
    else:
        return -1
    
    time.sleep(pause)
    zd.s.click_and_wait(xlocs['advanced_options_anchor'])
    number=zd.s.get_value(xlocs['max_clients_textbox'])
    zd.s.click_and_wait(xlocs['cancel_button'])
    return number

def _config_dhcp_relay_option(zd, dhcp_relay_name = None):
    xlocs = LOCATORS_CFG_WLANS
    if not zd.s.is_element_visible(xlocs['loc_do_dhcp_relay_checkbox']):
        raise Exception('The option for DHCP Relay is not visible to configure')
    
    if not dhcp_relay_name:
        zd.s.click_if_checked(xlocs['loc_do_dhcp_relay_checkbox'])
    else:
        zd.s.click_if_not_checked(xlocs['loc_do_dhcp_relay_checkbox'])
        zd.s.select_option(xlocs['loc_select_dhcp_relay_svr_dropbox'], dhcp_relay_name)

#
# FEATURE UPDATE SESSION
#
def download_dpsk_record(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    save_to = constant.save_to
    save_button = LOCATORS_CFG_WLANS['save_dpsk']
    file_path = control_zd.download_single_file(zd, save_button, filename_re='.+.csv', save_to=save_to)
    logging.debug('The current file save at %s' % file_path)
    if not file_path:
        logging.error("save file fail! the file is empty")
        return False
    return True

feature_update = {
}

# two mainline builds prior to 9.0.0.0 production
# these can be removed any time when we no longer test mainline builds of 9.0
