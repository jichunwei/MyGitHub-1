'''
Usage:

lib.zd.sys.get_all_mgmt_access_ctrls(zd)

-- create here!
lib.zd.sys.create_mgmt_access_ctrl(zd, dict()) # if no item in the table yet

cfg = dict(name='cuteo', restriction='subnet', ip_addr=['192.168.0.0','24'])
lib.zd.sys.create_mgmt_access_ctrl(zd, cfg)

--- get
lib.zd.sys.get_mgmt_access_ctrl(zd, 'cuteo')

--- delete
lib.zd.sys.delete_mgmt_access_ctrls(zd, ['cuteo'])

--- edit
lib.zd.sys.edit_mgmt_access_ctrl(zd, 'New Name', cfg)

--- clone
lib.zd.sys.clone_mgmt_access_ctrl(zd, 'cuteo', dict(name='cuteo2'))


lib.zd.sys.get_device_ip_settings(zd)
ip_cfg = dict(
    ip_alloc = 'manual',
    ip_addr = '192.168.0.2',
    netmask = '255.255.255.0',
    gateway = '192.168.0.253',
    pri_dns = '192.168.30.252',
#    vlan = '301',
)

ami_cfg = dict(
    ami_ip_addr = '192.168.0.202',
    ami_netmask = '255.255.255.0',
    ami_vlan = '301',
)

lib.zd.sys.set_device_ip_settings(zd, ip_cfg)

lib.zd.sys.enable_additional_mgmt_if(zd, False)
lib.zd.sys.enable_additional_mgmt_if(zd, True)
lib.zd.sys.set_additional_mgmt_if(zd, ami_cfg)

'''

import time
import logging
import types
import re
import copy

from RuckusAutoTest.common import lib_Constant as CONST
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt


#Default vlan for zd device ip settings: before 9.4 it is empty, after 9.4 it is 1.
#DEFAULT_ZD_VLAN_ID = ""

#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_mgmt_access_ctrls(zd):
    '''
    . get all the mgmt access ctrls table and put into dict
    return
    . a list of dict
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)
    return wgt.get_tbl_rows(zd.s, xloc['tbl']['tbl'], xloc['tbl']['nav'])


def get_mgmt_access_ctrl(zd, name):
    '''
    . get the detail of a mgmt access ctrl
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)

    zd.s.safe_click(xloc['edit_btn'] % name)
    cfg = _get_mgmt_access_ctrl_item(zd)
    nav_to(zd, force = True)

    return cfg


def create_mgmt_access_ctrl(zd, cfg):
    '''
    cfg:
    . name
    . restriction: (single, range, subnet)
    . ip_addr
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)
    zd.s.click_and_wait(xloc['create_btn'])
    _set_mgmt_access_ctrl_item(zd, cfg)
    zd.s.click_and_wait(xloc['ok_btn'])


def delete_mgmt_access_ctrls(zd, names):
    '''
    . delete the mgmt access ctrls in the given names list
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)
    for n in names:
        zd.s.safe_click(xloc['select_chk'] % n)

    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['delete_btn'])


def delete_all_mgmt_access_ctrls(zd):
    '''
    TODO: check for the enabling of delete button -- for the case where there is
    no item on the list, the delete button is disabled
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)
    zd.s.safe_click(xloc['select_all_chk'])
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['delete_btn'])


def edit_mgmt_access_ctrl(zd, name, cfg):
    '''
    cfg: refer to create_mgmt_access_ctrl
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)
    zd.s.safe_click(xloc['edit_btn'] % name)
    _set_mgmt_access_ctrl_item(zd, cfg)
    zd.s.click_and_wait(xloc['ok_btn'])


def clone_mgmt_access_ctrl(zd, name, cfg):
    '''
    cfg: refer to create_mgmt_access_ctrl
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']

    nav_to(zd)
    zd.s.safe_click(xloc['clone_btn'] % name)
    _set_mgmt_access_ctrl_item(zd, cfg)
    zd.s.click_and_wait(xloc['ok_btn'])

def get_all_static_routes(zd):
    '''
    . get all the static routes table and put into dict
    return
    . a list of dict
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)
    return wgt.get_tbl_rows(zd.s, xloc['tbl']['tbl'], xloc['tbl']['nav'])


def get_static_route(zd, name):
    '''
    . get the detail of a static route
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)

    zd.s.safe_click(xloc['edit_btn'] % name)
    cfg = _get_static_route_item(zd)
    nav_to(zd, force = True)

    return cfg


def create_static_route(zd, cfg):
    '''
    cfg:
    . name
    . subnet
    . gateway
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)
    zd.s.click_and_wait(xloc['create_btn'])
    if type(cfg) is list:
        for n in cfg:
            _set_static_route_item(zd, n)
            zd.s.click_and_wait(xloc['ok_btn'])
    else:
        _set_static_route_item(zd, cfg)
        zd.s.click_and_wait(xloc['ok_btn'])


def delete_static_route(zd, names):
    '''
    . delete the static routes in the given names list
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)
    if type(names) is list:
        for n in names:
            zd.s.safe_click(xloc['select_chk'] % n)
    else:
        zd.s.safe_click(xloc['select_chk'] % names)

    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['delete_btn'])


def delete_all_static_routes(zd):
    '''
    TODO: check for the enabling of delete button -- for the case where there is
    no item on the list, the delete button is disabled
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)
    zd.s.safe_click(xloc['select_all_chk'])
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['delete_btn'])


def edit_static_route(zd, name, cfg):
    '''
    cfg: refer to create_static_route
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)
    zd.s.safe_click(xloc['edit_btn'] % name)
    _set_static_route_item(zd, cfg)
    zd.s.click_and_wait(xloc['ok_btn'])


def clone_static_route(zd, name, cfg):
    '''
    cfg: refer to create_static_route
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']

    nav_to(zd)
    zd.s.safe_click(xloc['clone_btn'] % name)
    _set_static_route_item(zd, cfg)
    zd.s.click_and_wait(xloc['ok_btn'])

def get_zd_ip_type(zd):
    """
    """
    nav_to(zd)
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    
    
def get_device_ip_settings(zd, ip_type = CONST.IPV4):
    '''
    Get device IP settings. 
    If version is 4, return ipv4 information.
    If version is 6, return ipv4 and ipv6 information.
    '''
    nav_to(zd)
    return _get_device_ip_settings(zd, ip_type)

def set_device_ip_settings(zd, cfg, ip_type = CONST.IPV4, l3sw = None):
    '''
    Set device ip settings:
    If version is 4, cfg dict is:
       ip_alloc: ipv4 setting mode: manual/dhcp.
           . manual: ip_addr, netmask, gateway, pri_dns, sec_dns, vlan
           . dhcp: vlan only
       ip_addr: ipv4 address.
       netmask: ipv4 net mask.
       gateway: ipv4 gateway.
       pri_dns: ipv4 primary dns.
       sec_dns: ipv4 secondary dns.
       vlan: ipv4 vlan.
    If verstion is 6, cfg dict is:
       ip_version: ipv4, ipv6, dualstack.
       vlan: vlan id.
       ipv4 :
           ip_alloc: ipv4 setting mode: manual/dhcp.
           ip_addr: ipv4 address.
           netmask: ipv4 net mask.
           gateway: ipv4 gateway.
           pri_dns: ipv4 primary dns.
           sec_dns: ipv4 secondary dns.
       ipv6:
           ipv6_alloc: ipv6 setting mode: manual/auto.
           ipv6_addr: ipv6 address.
           ipv6_prefix_len: ipv6 prefix len.
           ipv6_gateway: ipv6 gateway.
           ipv6_pri_dns: ipv6 primary dns.
           ipv6_sec_dns: ipv6 secondary dns.
    
    If change IP mode, zd will show confirmation and restart.
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    
    nav_to(zd)
    zd.s.choose_ok_on_next_confirmation()
    
    if ip_type == CONST.IPV4:
        #For version is 4, we only set ipv4 configurations.
        #If version can be set and current ip version is ipv6, need to set it as ipv4.
        if zd.s.is_element_present(xloc['ipv6_support_chk']):
            cur_ip_version = _get_device_ip_version(zd)
            if cur_ip_version == CONST.IPV6:
                ip_version = CONST.IPV4
                _set_device_ip_version(zd, ip_version)
                
        _set_device_ip_settings(zd, cfg, l3sw)
    #@author: Jane.Guo @since: 2013-0604 fix bug:add dual stack
    elif ip_type == CONST.IPV6 or ip_type == CONST.DUAL_STACK:
        #For version is 6, we will set ip version, ipv4 and ipv6 configuration.
        if cfg.get('ip_version'):
            ip_version = cfg.get('ip_version').lower()
        else:
            ip_version = ip_type
                
        _set_device_ip_version(zd, ip_version)
        
        #Set IPV6 configurations.            
        if ip_version in [CONST.IPV6,CONST.DUAL_STACK]:
            if cfg.has_key(CONST.IPV6):
                ipv6_cfg = cfg[CONST.IPV6]
            else:
                ipv6_cfg = {'ipv6_alloc': 'auto'}
                
            _set_device_ipv6_settings(zd, ipv6_cfg)
            
            #Set IPV4 configurations.   
            if ip_version == CONST.DUAL_STACK:
                if cfg.has_key(CONST.IPV4):
                    ipv4_cfg = cfg[CONST.IPV4]
                    if cfg.has_key('vlan'):
                        ipv4_cfg['vlan'] = cfg['vlan']
                    _set_device_ip_settings(zd, ipv4_cfg, l3sw)
            else:
                zd.s.click_and_wait(xloc['apply_btn'])             
        
    else:
        raise Exception("IP type %s is incorrect." % ip_type)
     

    #If IP mode is changed, zd will restart.
    if zd.s.is_confirmation_present():        
        _prompt = zd.s.get_confirmation()
        logging.info('Confirmation:"%s"' % _prompt)
        if re.search('Changing IP mode will restart ZoneDirector.*', _prompt, re.I):
            _wait_zd_restart(zd)
    
    time.sleep(5)

def enable_additional_mgmt_if(zd, enabled = True):
    '''
    . enable or disable the additional management interface
    NOTE:
      . this function is used separately and do not needed to be called
        prior to set_additional_mgmt_if
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']

    nav_to(zd)
    if _set_device_ip_setting_enable_ami(zd, enabled):
        zd.s.click_and_wait(xloc['ami_apply_btn'])


def set_additional_mgmt_if(zd, cfg):
    '''
    . set the additional mgmt if
      . open the panel if needed
    cfg:
    . ami_ip_addr, ami_netmask, ami_vlan
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']

    nav_to(zd)
    _set_device_ip_settings(zd, cfg)
    zd.s.click_and_wait(xloc['ami_apply_btn'])
    time.sleep(5)

def get_ntp_config(zd):
    """
    Get ntp config:
    Output: { 'Enabled':  True,
              'Address': 'ntp.ruckus.com'}
    """
    ntp_cfg = {}
    nav_to(zd)

    ntp_cfg['Enabled'] = zd.s.is_checked(zd.info['loc_cfg_system_time_ntp_checkbox'])

    if zd.s.is_element_present(zd.info['loc_cfg_system_time_ntp_textbox']):
        ntp_cfg['Address'] = zd.s.get_value(zd.info['loc_cfg_system_time_ntp_textbox'])

    return ntp_cfg

#-----------------------------------------------------------------------------
LOCATOR_CFG_SYSTEM_NETWORKMGMT = dict(
    zd_ipaddr_textbox = r"//input[contains(@id,'ip')]",
    zd_netmask_textbox = r"//input[contains(@id,'netmask')]",
    zd_gateway_textbox = r"//input[contains(@id,'gateway')]",
    zd_pri_dns_textbox = r"//input[contains(@id,'dns1')]",
    zd_sec_dns_textbox = r"//input[contains(@id,'dns2')]",
    zd_vlan_textbox = r"//input[contains(@id,'mgmt-vlan')]",
    zd_ip_apply_button = r"//input[contains(@id,'apply-mgmt-ip')]",

#@Author: chen.tao@odc-ruckuswireless.com Since 2013-9-26 to change the xpath of network_mgmt_icon_collapse
#    network_mgmt_icon_collapse = r"//tr[@id='cat-network-mgmt']//img[@id='icon' and @src='images/collapse.png']",
    network_mgmt_icon_collapse = r"//tr[@id='cat-network-mgmt']//img[@id='mgmt-icon']",
#@Author: chen.tao@odc-ruckuswireless.com Since 2013-9-26 to change the xpath of network_mgmt_icon_collapse
    network_mgmt_icon_expand = r"//tr[@id='cat-network-mgmt']//img[@id='icon' and @src='images/expand.png']",
    network_mgmt_click = r"//tr[@id='cat-network-mgmt']//a",
    # FlexMaster
    FM_enable_mgmt_checkbox = r"//input[@id='by-fm']",
    FM_url_textbox = r"//input[@id='fmurl' and @name='fmurl']",
    FM_interval_textbox = r"//input[@id='inform-interval' and @name='inform-interval']",
    FM_apply = r"//input[@id='apply-acsurl']",
    FM_status = r"//p[@id='fm_status']//span[@id='succstatus']",
    FM_refresh = r"//p[@id='fm_status']//input[@id='reinform']",
    # SNMP Agent
    SNMP_v2_enable_agent_checkbox = r"//input[@id='snmp']",
    SNMP_v2_contact_textbox = r"//input[@id= 'snmp-sys-contact']",
    SNMP_v2_location_textbox = r"//input[@id= 'snmp-sys-location']",
    SNMP_v2_ro_community_textbox = r"//input[@id= 'snmp-ro']",
    SNMP_v2_rw_community_textbox = r"//input[@id= 'snmp-rw']",
    SNMP_v2_agent_apply = r"//input[@id= 'apply-snmp']",
    # SNMP Agent for SNMPV3
    SNMP_v3_enable_agent_checkbox = r"//input[@id='snmpv3']",
    SNMP_v3_ro_user_textbox = r"//input[@id='ro-user']",
    SNMP_v3_ro_auth_drodpown = r"//select[@id='ro-auth']",
    SNMP_v3_ro_auth_pass_textbox = r"//input[@id='ro-authPP']",
    SNMP_v3_ro_privacy_drodpown = r"//select[@id='ro-priv']",
    SNMP_v3_ro_privacy_pass_textbox = r"//input[@id='ro-privPP']",
    SNMP_v3_rw_user_textbox = r"//input[@id='rw-user']",
    SNMP_v3_rw_auth_drodpown = r"//select[@id='rw-auth']",
    SNMP_v3_rw_auth_pass_textbox = r"//input[@id='rw-authPP']",
    SNMP_v3_rw_privacy_drodpown = r"//select[@id='rw-priv']",
    SNMP_v3_rw_privacy_pass_textbox = r"//input[@id='rw-privPP']",
    SNMP_v3_agent_apply = r"//input[@id='apply-snmpv3']",

    # SNMP Trap
    SNMP_enable_trap_checkbox = r"//input[@id= 'snmp-trap']",
    SNMP_trap_format_dropdown = "//select[@id='snmp-trap-format']",
    SNMP_trap_v2_server_textbox = r"//input[@id= 'snmp-trap-ip%s']",
    SNMP_trap_v3_checkbox = r"//input[@id= 'cb%s']",
    SNMP_trap_v3_user_textbox = r"//input[@id='user%s']",
    SNMP_trap_v3_server_textbox = r"//input[@id='snmp-trapv3-ip%s']",
    SNMP_trap_v3_auth_drodpown = r"//select[@id='auth%s']",
    SNMP_trap_v3_auth_pass_textbox = r"//input[@id='authPP%s']",
    SNMP_trap_v3_privacy_drodpown = r"//select[@id='priv%s']",
    SNMP_trap_v3_privacy_pass_textbox = r"//input[@id='priv%sPP']",
    SNMP_trap_apply = r"//input[@id= 'apply-snmp-trap']",
    
    #Log Settings
    log_level = dict(
        show_more = r"//input[@id='high']",
        warning_and_critical = r"//input[@id='medium']",
        critical_events_only = r"//input[@id='high']",
    ),
    enable_remote_syslog = r"//input[@id='enable-remote-log']",
    remote_syslog_ip = r"//input[@id='remote-log-server']",
    syslog_apply = r"//input[@id='apply-log']",
    
    syslog_advanced_setting_collapse = r"//img[@id='icon-syslog-adv' and @src='images/collapse.png']",
    syslog_advanced_setting_expand = r"//img[@id='icon-syslog-adv' and @src='images/expand.png']",
    syslog_advanced_setting_click = r"//img[@id='icon-syslog-adv']/../a",
    
    zd_facility_name = r"//select[@id='remote-log-fac']",
    zd_priority_level = r"//select[@id='remote-log-pri']",
    ap_facility_name = r"//select[@id='remote-log-ap-fac']",
    ap_priority_level = r"//select[@id='remote-log-ap-pri']",

    # Device IP Settings
    dev_ip_settings = dict(
        ip_alloc = dict( # ip address allocation type
            manual = "//input[@id='manual']",
            dhcp = "//input[@id='dhcp']",
        ),
        ip_addr = "//input[@id='ip']",
        netmask = "//input[@id='netmask']",
        gateway = "//input[@id='gateway']",
        pri_dns = "//input[@id='dns1']",
        sec_dns = "//input[@id='dns2']",
        vlan = "//input[@id='mgmt-vlan']",

        apply_btn = "//input[@id='apply-mgmt-ip']",

        # Additional Management Interface: ami
        ami_btn_visibled = "//p[@id='show-config-addif']", # check for visibility
        ami_btn = "//p[@id='show-config-addif']//a[contains(.,'click here')]",
        ami_enabled_chk = "//input[@id='enable-addif']",

        ami_ip_addr = "//input[@id='addif-ip']",
        ami_netmask = "//input[@id='addif-netmask']",
        #ami_vlan = "//input[@id='addif-vlan-id']",
        ami_vlan = "//input[@id='addif-vlan']",
        
        ami_enable_gateway = "//input[@id='enable-addif-gateway']",
        ami_gateway = "//input[@id='addif-gateway']",
        
        ami_apply_btn = "//input[@id='apply-addif']",

        # add xpath for ipv6.
        ipv6_support_chk = "//input[@id='ipv6-support']",
        ip_version = dict (
            dualstack = "//input[@id='dualmode']",
            ipv6 = "//input[@id='ipv6mode']",
            ),
        ipv6_alloc = dict ( #ipv6 allocation type
            manual = "//input[@id='manual-ipv6']",
            auto = "//input[@id='autoconfig']"
            ),
        ipv6_addr = "//input[@id='ipv6']",
        ipv6_prefix_len = "//input[@id='prefixlength']",
        ipv6_gateway = "//input[@id='gateway-ipv6']",
        ipv6_pri_dns = "//input[@id='dns1-ipv6']",
        ipv6_sec_dns = "//input[@id='dns2-ipv6']",
        
        ami_ipv6_enabled_chk = "//input[@id='enable-addif-ipv6']",
        ami_ipv6_addr = "//input[@id='addif-ipv6']",
        ami_ipv6_prefix_len = "//input[@id='addif-ipv6-prefixlength']",
        ami_ipv6_enable_gateway = "//input[@id='enable-addif-ipv6-gateway']",
        ami_ipv6_gateway = "//input[@id='addif-ipv6-gateway']",
             
    ),

    # Management Access Control
    mgmt_access_ctrl = dict(
        tbl = dict(
            tbl = "//table[@id='mgmtipacl']",
            nav = "", # no nav implemented
        ),
        select_all_chk = "//input[@id='mgmtipacl-sall']",
        select_chk = "//tr[./td='%s']/td/input[@name='mgmtipacl-select']",
        create_btn = "//span[@id='new-mgmtipacl']",
        edit_btn = "//tr[./td='%s']/td/span[contains(@id,'edit-mgmtipacl-')]",
        clone_btn = "//tr[./td='%s']/td/span[contains(@id,'clone-mgmtipacl-')]",

        name = "//input[@id='ip-acl-name']",
        # radio button group
        restriction = dict(
            single = "//input[@id='type_single']",
            range = "//input[@id='type_range']",
            subnet = "//input[@id='type_subnet']",
        ),
        # according to restriction type
        ip_addr = dict(
            single = "//input[@id='single-addr1']",
            range = ["//input[@id='range-addr1']",
                     "//input[@id='range-addr2']",],
            subnet = ["//input[@id='subnet-addr1']",
                      "//input[@id='subnet-addr2']",],
        ),
        # buttons
        ok_btn = "//input[@id='ok-mgmtipacl']",
        delete_btn = "//input[@id='del-mgmtipacl']",
    ),

    # Static Route
    static_route = dict(
        tbl = dict(
            tbl = "//table[@id='route']",
            nav = "", # no nav implemented
        ),
        select_all_chk = "//input[@id='route-sall']",
        select_chk = "//tr[./td='%s']/td/input[@name='route-select']",
        create_btn = "//span[@id='new-route']",
        edit_btn = "//tr[./td='%s']/td/span[contains(@id,'edit-route-')]",
        clone_btn = "//tr[./td='%s']/td/span[contains(@id,'clone-route-')]",
        delete_btn = "//input[@id='del-route']",

        name = "//input[@id='route-name']",
        subnet = "//input[@id='route-subnet']",
        gateway = "//input[@id='route-gateway']",
        # buttons
        ok_btn = "//input[@id='ok-route']",
        cancel_btn = "//input[@id='cancel-route']",
    ),
)


def nav_to(zd, force = True):
    #zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM, force=True)
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM, force=force)
    time.sleep(5) # this page is loaded twice


def get_fm_mgmt_info(zd, debug = False, timeout = 120):
    endtime = time.time() + timeout
    while time.time() < endtime:
        try:
            return _get_fm_mgmt_info(zd)
        except:
            time.sleep(1)
    raise Exception('Can not get NetworkManagement FlexMaster Info.')

def _get_fm_mgmt_info(zd, debug = False):
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    fm_mgmt = {}
    nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(0.5)
    fm_mgmt['enabled'] = zd.s.is_checked(xloc['FM_enable_mgmt_checkbox'])
    fm_mgmt['url'] = zd.s.get_value(xloc['FM_url_textbox'])
    fm_mgmt['interval'] = zd.s.get_value(xloc['FM_interval_textbox'])
    try:
        zd.s.click_and_wait(xloc['FM_refresh'])
        fm_mgmt['status'] = zd.s.get_text(xloc['FM_status'])
    except:
        pass

    return fm_mgmt

def set_fm_mgmt_info(zd, fm_mgmt_dict, debug = False):
    fm_mgmt = dict(enabled = False)
    fm_mgmt.update(fm_mgmt_dict)
    logging.info('set FM mgmt: %s' % str(fm_mgmt))
    nav_to(zd)
    try:
        _set_fm_mgmt_info(zd, fm_mgmt, debug)
    except Exception, e:
        # try one more time; in case of enable was not taken effect after 0.5 seconds
        logging.info('[ReTry setFlexMasterAttrs] [onMsg "%s"]' % e.message)
        zd.refresh()
        loadtime_open = zd.conf['loadtime_open1'] if zd.conf.has_key('loadtime_open1') else 10000
        zd.s.wait_for_page_to_load(loadtime_open)
        _set_fm_mgmt_info(zd, fm_mgmt, debug)
    return get_fm_mgmt_info(zd)

def _set_fm_mgmt_info(zd, fm_mgmt, debug = False):
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])

    if fm_mgmt['enabled']:
        zd.s.is_element_present(xloc['FM_enable_mgmt_checkbox'])
        zd.s.click_if_not_checked(xloc['FM_enable_mgmt_checkbox'])
        time.sleep(0.5)
        for _k in ['url', 'interval']:
            if fm_mgmt.has_key(_k) and (type(fm_mgmt[_k]) is not types.NoneType):
                _lid = "FM_" + _k + "_textbox"
                zd.s.type_text(xloc[_lid], str(fm_mgmt[_k]))
    else:
        zd.s.is_element_present(xloc['FM_enable_mgmt_checkbox'])
        zd.s.click_if_checked(xloc['FM_enable_mgmt_checkbox'])
    time.sleep(0.5)
    zd.s.click_and_wait(xloc['FM_apply'])

def _is_editable(zd, locator, pause = 0.5, tries = 3):
    while tries > 0:
        if zd.s.is_editable(locator):
            return True
        tries -= 1
        time.sleep(pause)
    return False

def get_snmp_agent_info(zd, pause = 0.5):
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_agent_info = dict()
    nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)

    snmp_agent_info['enabled'] = zd.s.is_checked(xloc['SNMP_v2_enable_agent_checkbox'])
    snmp_agent_info['version'] = '2'
    snmp_agent_info['ro_community'] = zd.s.get_value(xloc['SNMP_v2_ro_community_textbox'])
    snmp_agent_info['rw_community'] = zd.s.get_value(xloc['SNMP_v2_rw_community_textbox'])
    snmp_agent_info['contact'] = zd.s.get_value(xloc['SNMP_v2_contact_textbox'])
    snmp_agent_info['location'] = zd.s.get_value(xloc['SNMP_v2_location_textbox'])

    return snmp_agent_info

def set_snmp_agent_info(zd, snmp_agent_cfg, pause = 0.5):
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_agent_info = dict(
        enabled = False,
        contact = "",
        location = "",
        ro_community = "",
        rw_community = ""
    )
    snmp_agent_info.update(snmp_agent_cfg)
    nav_to(zd, force = True)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)
    is_enable = zd.s.is_checked(xloc['SNMP_v2_enable_agent_checkbox'])
    if snmp_agent_info['enabled']:
        if not is_enable:
            zd.s.click_and_wait(xloc['SNMP_v2_enable_agent_checkbox'])
            time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v2_contact_textbox'], snmp_agent_info['contact'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v2_location_textbox'], snmp_agent_info['location'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v2_ro_community_textbox'], snmp_agent_info['ro_community'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v2_rw_community_textbox'], snmp_agent_info['rw_community'])
        time.sleep(pause)
        zd.s.click_and_wait(xloc['SNMP_v2_agent_apply'])

    else:
        if is_enable:
            zd.s.click_and_wait(xloc['SNMP_v2_enable_agent_checkbox'])
            time.sleep(pause)
            zd.s.click_and_wait(xloc['SNMP_v2_agent_apply'])

    time.sleep(pause * 3)    
    if zd.s.is_alert_present(5):        
        _alert = zd.s.get_alert()
                
        if re.search('No greater than .* characters.*', _alert, re.I) or re.search('.* cannot be empty.*', _alert, re.I):
            return _alert
        else:
            raise Exception(_alert)


def get_snmp_agent_v3_info(zd, pause = 0.5):
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_agent_info = dict()
    nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)
    
    snmp_agent_info['enabled'] = zd.s.is_checked(xloc['SNMP_v3_enable_agent_checkbox'])
    snmp_agent_info['ro_sec_name'] = zd.s.get_value(xloc['SNMP_v3_ro_user_textbox'])
    snmp_agent_info['ro_auth_protocol'] = zd.s.get_value(xloc['SNMP_v3_ro_auth_drodpown'])
    snmp_agent_info['ro_auth_passphrase'] = zd.s.get_value(xloc['SNMP_v3_ro_auth_pass_textbox'])
    snmp_agent_info['ro_priv_protocol'] = zd.s.get_value(xloc['SNMP_v3_ro_privacy_drodpown'])
    snmp_agent_info['ro_priv_passphrase'] = zd.s.get_value(xloc['SNMP_v3_ro_privacy_pass_textbox'])
    snmp_agent_info['rw_sec_name'] = zd.s.get_value(xloc['SNMP_v3_rw_user_textbox'])
    snmp_agent_info['rw_auth_protocol'] = zd.s.get_value(xloc['SNMP_v3_rw_auth_drodpown'])
    snmp_agent_info['rw_auth_passphrase'] = zd.s.get_value(xloc['SNMP_v3_rw_auth_pass_textbox'])
    snmp_agent_info['rw_priv_protocol'] = zd.s.get_value(xloc['SNMP_v3_rw_privacy_drodpown'])
    snmp_agent_info['rw_priv_passphrase'] = zd.s.get_value(xloc['SNMP_v3_rw_privacy_pass_textbox'])

    return snmp_agent_info

def set_snmp_agent_v3_info(zd, snmp_agent_cfg, pause = 0.5):
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_agent_info = dict(
        enabled = False,
        ro_sec_name='',
        ro_auth_protocol='',
        ro_auth_passphrase='',
        ro_priv_protocol='',
        ro_priv_passphrase='',
        rw_sec_name='',
        rw_auth_protocol='',
        rw_auth_passphrase='',
        rw_priv_protocol='',
        rw_priv_passphrase='',
    )

    snmp_agent_info.update(snmp_agent_cfg)
    nav_to(zd, force = True)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)
    is_enable = zd.s.is_checked(xloc['SNMP_v3_enable_agent_checkbox'])
    if snmp_agent_info['enabled']:
        if not is_enable:
            zd.s.click_and_wait(xloc['SNMP_v3_enable_agent_checkbox'])
            time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v3_ro_user_textbox'], snmp_agent_info['ro_sec_name'])
        time.sleep(pause)
        zd.s.select(xloc['SNMP_v3_ro_auth_drodpown'], snmp_agent_info['ro_auth_protocol'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v3_ro_auth_pass_textbox'], snmp_agent_info['ro_auth_passphrase'])
        time.sleep(pause)
        zd.s.select(xloc['SNMP_v3_ro_privacy_drodpown'], snmp_agent_info['ro_priv_protocol'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v3_ro_privacy_pass_textbox'], snmp_agent_info['ro_priv_passphrase'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v3_rw_user_textbox'], snmp_agent_info['rw_sec_name'])
        time.sleep(pause)
        zd.s.select(xloc['SNMP_v3_rw_auth_drodpown'], snmp_agent_info['rw_auth_protocol'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v3_rw_auth_pass_textbox'], snmp_agent_info['rw_auth_passphrase'])
        time.sleep(pause)
        zd.s.select(xloc['SNMP_v3_rw_privacy_drodpown'], snmp_agent_info['rw_priv_protocol'])
        time.sleep(pause)
        zd.s.type_text(xloc['SNMP_v3_rw_privacy_pass_textbox'], snmp_agent_info['rw_priv_passphrase'])
        time.sleep(pause)

        zd.s.click_and_wait(xloc['SNMP_v3_agent_apply'])

    else:
        if is_enable:
            zd.s.click_and_wait(xloc['SNMP_v3_enable_agent_checkbox'])
            time.sleep(pause)
            zd.s.click_and_wait(xloc['SNMP_v3_agent_apply'])

    time.sleep(pause * 3)
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        
        err_ptn_list = ['.* cannot be empty.*',
                        '.* has to be no less than .* and no greater than .* characters.*',                        
                        '.* can only contain between .* and .* characters.*'
                        ]
        
        is_match_err = False
        for ptn in err_ptn_list:
            if re.search(ptn, _alert, re.I):
                is_match_err = True
                break    
        
        if is_match_err:
            return _alert
        else:            
            raise Exception(_alert)

def get_snmp_trap_info(zd, pause = 0.5):
    '''
    Get snmp trap information.
    For the original, return: 
        
    
    For version 2:
    {'version': '2'
     'enabled': True,
     'server_info': {'1': {'server_ip':'192.168.0.2'}},
    } 
    For version 3:
    {'version': '3'
     'enabled': True,
     'server_info': {'1': {'sec_name': '', 'server_ip': 192.168.0.2,
                         'auth_protocol': 'MD5','auth_passphrase': '12345678',
                         'priv_protocol': 'AES','priv_passphrase': '12345678'
                         }
                  }
                        
     }
     Or for disabled:
     {'enabled': False}     
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_trap_info = dict()
    nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)
    
    snmp_trap_info['enabled'] = zd.s.is_checked(xloc['SNMP_enable_trap_checkbox'])
    
    if snmp_trap_info['enabled']:
        if zd.s.is_element_present(xloc['SNMP_trap_format_dropdown']) and zd.s.is_visible(xloc['SNMP_trap_format_dropdown']):
            #With format text box.
            snmp_trap_info['version'] = zd.s.get_value(xloc['SNMP_trap_format_dropdown'])
            
            #Updated, support multi trap servers, maximum is 4.
            if snmp_trap_info['version'] == '2':
                v2_loc_temp_server_ip = xloc['SNMP_trap_v2_server_textbox']
                server_ip_dict = {}
                for index in range(1,5):
                    server_loc = v2_loc_temp_server_ip % index
                    if zd.s.is_element_present(server_loc) and zd.s.is_visible(server_loc):
                        server_ip = zd.s.get_value(server_loc)
                        if server_ip:
                            server_ip_dict[str(index)] = {'server_ip': server_ip}
                snmp_trap_info.update(server_ip_dict)
            else:
                v3_loc_temp_user = xloc['SNMP_trap_v3_user_textbox']
                v3_loc_temp_server_ip = xloc['SNMP_trap_v3_server_textbox']
                v3_loc_temp_auth = xloc['SNMP_trap_v3_auth_drodpown']
                v3_loc_temp_auth_pass = xloc['SNMP_trap_v3_auth_pass_textbox']
                v3_loc_temp_privacy = xloc['SNMP_trap_v3_privacy_drodpown']
                v3_loc_temp_privacy_pass = xloc['SNMP_trap_v3_privacy_pass_textbox']
                v3_loc_temp_select = xloc['SNMP_trap_v3_checkbox']
                
                v3_server_info_dict = {}
                for index in range(1,5):
                    select_loc = v3_loc_temp_select % index
                    user_loc = v3_loc_temp_user % index
                    server_ip_loc = v3_loc_temp_server_ip % index
                    auth_loc = v3_loc_temp_auth % index
                    auth_pass_loc = v3_loc_temp_auth_pass % index
                    privacy_loc = v3_loc_temp_privacy % index
                    privacy_pass_loc = v3_loc_temp_privacy_pass % index
                                   
                    if (zd.s.is_element_present(select_loc) and zd.s.is_visible(select_loc) and zd.s.is_checked(select_loc)) \
                       or (not zd.s.is_element_present(select_loc) and zd.s.is_element_present(user_loc) and zd.s.is_visible(user_loc)):
                        v3_server_info = {}
                        v3_server_info['sec_name'] = zd.s.get_value(user_loc)
                        v3_server_info['server_ip']= zd.s.get_value(server_ip_loc)
                        v3_server_info['auth_protocol'] = zd.s.get_value(auth_loc)
                        v3_server_info['auth_passphrase'] = zd.s.get_value(auth_pass_loc)
                        v3_server_info['priv_protocol'] = zd.s.get_value(privacy_loc)
                        v3_server_info['priv_passphrase'] = zd.s.get_value(privacy_pass_loc)
                        
                        v3_server_info_dict[str(index)] = v3_server_info
                    
                    if v3_server_info_dict:
                        snmp_trap_info.update(v3_server_info_dict)
        else:
            #No trap format select box, only get snmpv2 information.
            index = 1
            loc = xloc['SNMP_trap_v2_server_textbox'] % index 
            snmp_trap_info['version'] = '2'
            snmp_trap_info['server_ip'] = zd.s.get_value(loc)
    else:
        pass
        '''
        #For disabled, keep snmpv2 trap information. In order to compare previous version - no snmpv3.
        index = 1
        loc = xloc['SNMP_trap_v2_server_textbox'] % index
        snmp_trap_info['version'] = '2'
        if zd.s.is_element_displayed(loc):
            snmp_trap_info['server_ip'] = [zd.s.get_value(loc)]
        '''

    return snmp_trap_info

def set_snmp_trap_info(zd, snmp_trap_cfg, pause = 0.5):
    '''
    Enable snmp trap and set format as snmp v2. Default is versino 2.
    For 9.3 version, support at most 4 trap severs.
    Input: 
    For version 2:
    {'version': '2'
     'enabled': True,
     '1': {'server_ip':'192.168.0.2'} Or 'server_ip':'192.168.0.2'
    } 
    For version 3:
    {'version': '3'
     'enabled': True,
     '1': {'sec_name': '', 'server_ip': 192.168.0.2,
           'auth_protocol': 'MD5','auth_passphrase': '12345678',
           'priv_protocol': 'AES','priv_passphrase': '12345678'}
     }
     Or for disabled:
     {'enabled': False}
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_trap_info = dict(
        enabled = False,
        server_ip = None,
        version = 2,        
    )
    
    snmp_trap_info.update(snmp_trap_cfg)
    
    #Open network management layer.
    nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)
    
    #Enable/disable trap.    
    is_enable = zd.s.is_checked(xloc['SNMP_enable_trap_checkbox'])
    if is_enable != snmp_trap_info['enabled']:
        zd.s.click_and_wait(xloc['SNMP_enable_trap_checkbox'])
        time.sleep(pause)
        
    if snmp_trap_info['enabled']:
        
        if zd.s.is_element_present(xloc['SNMP_trap_format_dropdown']) and zd.s.is_visible(xloc['SNMP_trap_format_dropdown']):
            #If trap format is displayed, set trap version.
            zd.s.select(xloc['SNMP_trap_format_dropdown'], 'SNMPv%s' % snmp_trap_info['version'])
            time.sleep(pause)
            
        if snmp_trap_info.get('server_ip') != None:
            #For only snmpv2, and pass server_ip.
            trap_server_info = {}
            trap_server_info['server_ip'] = snmp_trap_info.pop('server_ip')
            if snmp_trap_info.has_key('sec_name'):
                trap_server_info['sec_name'] = snmp_trap_info.pop('sec_name')
            if snmp_trap_info.has_key('auth_protocol'):
                trap_server_info['auth_protocol'] = snmp_trap_info.pop('auth_protocol')
            if snmp_trap_info.has_key('auth_passphrase'):
                trap_server_info['auth_passphrase'] = snmp_trap_info.pop('auth_passphrase')
            if snmp_trap_info.has_key('priv_protocol'):
                trap_server_info['priv_protocol'] = snmp_trap_info.pop('priv_protocol')
            if snmp_trap_info.has_key('priv_passphrase'):
                trap_server_info['priv_passphrase'] = snmp_trap_info.pop('priv_passphrase')
                
            trap_cfg_dict = {}
            trap_cfg_dict.update(snmp_trap_info)
            trap_cfg_dict['1'] = trap_server_info
            
        else:
            trap_cfg_dict = snmp_trap_info
            
        if str(snmp_trap_info['version']) == '2':
            v2_loc_temp_server_ip = xloc['SNMP_trap_v2_server_textbox']
            for index in range(1,5):
                server_loc = v2_loc_temp_server_ip % index
                if zd.s.is_element_present(server_loc) and zd.s.is_visible(server_loc):
                    if trap_cfg_dict.has_key(str(index)):
                        trap_cfg = trap_cfg_dict[str(index)]
                        server_ip = trap_cfg['server_ip']
                    else:
                        server_ip = ''
                    zd.s.type_text(server_loc, server_ip)
                    time.sleep(pause)
        else:
            v3_loc_temp_user = xloc['SNMP_trap_v3_user_textbox']
            v3_loc_temp_server_ip = xloc['SNMP_trap_v3_server_textbox']
            v3_loc_temp_auth = xloc['SNMP_trap_v3_auth_drodpown']
            v3_loc_temp_auth_pass = xloc['SNMP_trap_v3_auth_pass_textbox']
            v3_loc_temp_privacy = xloc['SNMP_trap_v3_privacy_drodpown']
            v3_loc_temp_privacy_pass = xloc['SNMP_trap_v3_privacy_pass_textbox']
            v3_loc_temp_select = xloc['SNMP_trap_v3_checkbox']
            
            for index in range(1,5):
                select_loc = v3_loc_temp_select % (index)
                user_loc = v3_loc_temp_user % (index)
                server_ip_loc = v3_loc_temp_server_ip % (index)
                auth_loc = v3_loc_temp_auth % (index)
                auth_pass_loc = v3_loc_temp_auth_pass % (index)
                privacy_loc = v3_loc_temp_privacy % (index)
                privacy_pass_loc = v3_loc_temp_privacy_pass % (index)
                
                if zd.s.is_element_present(select_loc) and zd.s.is_visible(select_loc):
                    if trap_cfg_dict.has_key(str(index)):
                        zd.s.click_if_not_checked(select_loc)
                        
                        trap_cfg = trap_cfg_dict[str(index)]
                        zd.s.type_text(user_loc, trap_cfg['sec_name'])
                        time.sleep(pause)
                        zd.s.type_text(server_ip_loc, trap_cfg['server_ip'])
                        time.sleep(pause)
                        zd.s.select(auth_loc, trap_cfg['auth_protocol'])
                        time.sleep(pause)
                        zd.s.type_text(auth_pass_loc, trap_cfg['auth_passphrase'])
                        time.sleep(pause)
                        zd.s.select(privacy_loc, trap_cfg['priv_protocol'])
                        time.sleep(pause)
                        zd.s.type_text(privacy_pass_loc, trap_cfg['priv_passphrase'])
                        time.sleep(pause)
                    else:
                        #Disable the trap server which will not displayed in CLI and SNMP result.
                        zd.s.click_if_checked(select_loc)
        
    time.sleep(pause)
    zd.s.click_and_wait(xloc['SNMP_trap_apply'])

    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        err_ptn_list = ['.* cannot be empty.*',
                        '.* has to be no less than .* and no greater than .* characters.*',                        
                        '.* can only contain between .* and .* characters.*',
                        '.* is not a valid IP address.*',
                        'IP address is the same : [.*].'
                        ]
        
        is_match_err = False
        for ptn in err_ptn_list:
            if re.search(ptn, _alert, re.I):
                is_match_err = True
                break    
        
        if is_match_err:
            return _alert
        else:
            raise Exception(_alert)
        
def enable_disable_snmp_trap(zd, snmp_trap_cfg, pause = 0.5):
    '''
    Just Enable and disnable snmp trap, not set 
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    snmp_trap_info = dict(
        enabled = False,
       
    )    
    snmp_trap_info.update(snmp_trap_cfg)
    
    #Open network management layer.
    nav_to(zd)
    if zd.s.is_element_present(xloc['network_mgmt_icon_collapse']):
        zd.s.click_and_wait(xloc['network_mgmt_click'])
    time.sleep(pause)
    
    #Enable/disable trap.    
    is_enable = zd.s.is_checked(xloc['SNMP_enable_trap_checkbox'])
    if is_enable != snmp_trap_info['enabled']:
        zd.s.click_and_wait(xloc['SNMP_enable_trap_checkbox'])
        time.sleep(pause)
        
    zd.s.click_and_wait(xloc['SNMP_trap_apply'])

    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        err_ptn_list = ['.* cannot be empty.*',
                        '.* has to be no less than .* and no greater than .* characters.*',                        
                        '.* can only contain between .* and .* characters.*',
                        '.* is not a valid IP address.*',
                        'IP address is the same : [.*].'
                        ]
        
        is_match_err = False
        for ptn in err_ptn_list:
            if re.search(ptn, _alert, re.I):
                is_match_err = True
                break    
        
        if is_match_err:
            return _alert
        else:
            raise Exception(_alert)

def change_zd_ipaddr(zd, zd_ip_cfg):
    ip_cfg_dict = dict(ip_addr='192.168.0.2',
                       netmask='255.255.255.0',
                       gateway='192.168.0.253',
                       pri_dns='192.168.0.252',
                       sec_dns='')
    ip_cfg_dict.update(zd_ip_cfg)
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    zd.do_login()
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    if zd.get_ip_cfg_status() != "static":
        zd._set_ip_cfg_status("static")
        time.sleep(2)

    if ip_cfg_dict['ip_addr']:
        logging.info("Set the system ip address to '%s'" % ip_cfg_dict['ip_addr'])
        zd.s.type_text(xloc['zd_ipaddr_textbox'], ip_cfg_dict['ip_addr'])

    if ip_cfg_dict['netmask']:
        logging.info("Set the system netmask to '%s'" % ip_cfg_dict['netmask'])
        zd.s.type_text(xloc['zd_netmask_textbox'], ip_cfg_dict['netmask'])

    if ip_cfg_dict['gateway']:
        logging.info("Set the system default gateway to '%s'" % ip_cfg_dict['gateway'])
        zd.s.type_text(xloc['zd_gateway_textbox'], ip_cfg_dict['gateway'])

    if ip_cfg_dict['pri_dns']:
        logging.info("Set the system primary dns to '%s'" % ip_cfg_dict['pri_dns'])
        zd.s.type_text(xloc['zd_pri_dns_textbox'], ip_cfg_dict['pri_dns'])

    if ip_cfg_dict['sec_dns']:
        logging.info("Set the system secondary dns to '%s'" % ip_cfg_dict['sec_dns'])
        zd.s.type_text(xloc['zd_sec_dns_textbox'], ip_cfg_dict['sec_dns'])

    zd.s.click_and_wait(xloc['zd_ip_apply_button'])
    time.sleep(2)
    if zd.s.is_alert_present():
        raise Exception (zd.s.get_alert())
    zd.selenium_mgr.shutdown()

def change_zd_vlan(zd, zd_vlan_cfg):
    vlan_cfg_dict = dict(
                         vlan =''
                       )
    vlan_cfg_dict.update(zd_vlan_cfg)
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    #zd.do_login()
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)

    if vlan_cfg_dict['vlan']:
        logging.info("Set the system vlan to '%s'" % vlan_cfg_dict['vlan'])
        zd.s.type_text(xloc['zd_vlan_textbox'], vlan_cfg_dict['vlan'])

    zd.s.click_and_wait(xloc['zd_ip_apply_button'])
    time.sleep(2)
    if zd.s.is_alert_present():
        raise Exception (zd.s.get_alert())
    zd.selenium_mgr.shutdown()

def set_syslog_info(zd, cfg, is_nav = True):
    '''
    . to set Log Settings
    . cfg = dict(
        log_level = 'show_more', #'warning_and_critical' | 'critical_events_only'
        enable_remote_syslog = True, # False
        remote_syslog_ip = 'ip of syslog server',
     )
    . is_nav: this param to support set Log Settings info on ZD
              template from FlexMaster. If do this from FM, don't navigate.
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    _cfg = dict(
        log_level = 'show_more',
        enable_remote_syslog = False,
    )
    _cfg.update(cfg)

    if is_nav:
        nav_to(zd)
        time.sleep(0.5)

    zd.s.click_and_wait(xloc['log_level'][_cfg['log_level']])
    if _cfg['enable_remote_syslog']:
        zd.s.click_if_not_checked(xloc['enable_remote_syslog'])
        zd.s.type_text(xloc['remote_syslog_ip'], _cfg['remote_syslog_ip'])
        #An Nguyen, added the step to support edit the advance syslog setting
        _set_advance_syslog(zd, **_cfg)
    else:
        zd.s.click_if_checked(xloc['enable_remote_syslog'])

    zd.s.click_and_wait(xloc['syslog_apply'])

def get_syslog_info(zd, is_nav = True):
    '''
    to get syslog settings
    . is_nav: this param to support set Log Settings info on ZD
              template from FlexMaster. If do this from FM, don't navigate.

    return cfg:
    dict(
        log_level = 'show_more', #'warning_and_critical' | 'critical_events_only'
        enable_remote_syslog = True, # False
        remote_syslog_ip = 'ip of syslog server',
     )
    '''
    l, cfg = LOCATOR_CFG_SYSTEM_NETWORKMGMT, dict()

    if is_nav:
        nav_to(zd)
        time.sleep(1)

    cfg['log_level'] = zd.s.get_radio_group_value(l['log_level'], 5)
    cfg['enable_remote_syslog'] = zd.s.is_checked(l['enable_remote_syslog'])
    if cfg['enable_remote_syslog']:
        cfg['remote_syslog_ip'] = zd.s.get_value(l['remote_syslog_ip'])
    
    #An Nguyen, Added the step to support get the advance syslog setting
    try:
        adv_cfg = _get_advance_syslog_setting(zd)
        cfg.update(adv_cfg)
    except Exception, e:
        logging.debug('[ZD WebUI] Can not get the advance syslog setting: %s' % e.message)
        
    return cfg


#-----------------------------------------------------------------------------
#  PRIVATE METHODS
#-----------------------------------------------------------------------------
def _get_mgmt_access_ctrl_item(zd):
    '''
    . get the detail after opening the detail by clicking on edit
    . return the values
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']
    cfg = dict(
        name = zd.s.get_value(xloc['name']),
    )

    for k, loc in xloc['restriction'].iteritems():
        if zd.s.is_checked(loc):
            cfg['restriction'] = k


    if cfg['restriction'] == 'single':
        cfg['ip_addr'] = zd.s.get_value(xloc['ip_addr'][cfg['restriction']])
    else:
        cfg['ip_addr'] = [
            zd.s.get_value(xloc['ip_addr'][cfg['restriction']][0]),
            zd.s.get_value(xloc['ip_addr'][cfg['restriction']][1]),
        ]

    return cfg


def _set_mgmt_access_ctrl_item(zd, cfg):
    '''
    input
    . cfg: name, restriction, ip_addr
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['mgmt_access_ctrl']
    k = 'name'
    if k in cfg:
        zd.s.type_text(xloc[k], cfg[k])

    k = 'restriction'
    if k in cfg:
        zd.s.click_if_not_checked(xloc[k][cfg[k]])

    k = 'ip_addr'
    if k in cfg:
        if cfg['restriction'] == 'single':
            zd.s.type_text(xloc[k]['single'], cfg[k])

        else:
            zd.s.type_text(xloc[k][cfg['restriction']][0], cfg[k][0])
            zd.s.type_text(xloc[k][cfg['restriction']][1], cfg[k][1])

def _get_static_route_item(zd):
    '''
    . get the detail after opening the detail by clicking on edit
    . return the values
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']
    cfg = dict(
        name = zd.s.get_value(xloc['name']),
        subnet = zd.s.get_value(xloc['subnet']),
        gateway = zd.s.get_value(xloc['gateway']),
    )

    return cfg


def _set_static_route_item(zd, cfg):
    '''
    input
    . cfg: name, subnet, gateway
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['static_route']
    for k in cfg:
        zd.s.type_text(xloc[k], cfg[k])

def _get_device_ip_settings(zd, ip_type):
    '''
    Get all device ip information: ipv4 and ipv6.
    For vesrion is 4, only return ipv4 cfg:
        'ip_alloc': 'dhcp',
        'ip_addr': '192.168.0.2',
        'netmask': '255.255.255.0',
        'gateway': '192.168.0.253',
        'pri_dns': '192.168.0.252',
        'sec_dns': '',
        'vlan': '',
    For version is 6, return ipv4 and ipv6 cfg:
      'ip_version': 'dualstack',
      'vlan': '',
      'ipv4':  {'ip_alloc': 'dhcp',
                'ip_addr': '192.168.0.2',
                'netmask': '255.255.255.0',
                'gateway': '192.168.0.253',
                'pri_dns': '192.168.0.252',
                'sec_dns': '',},
      'ipv6':  {'ipv6_alloc': 'manual',
                'ipv6_addr': '2020:db8:1::2',
                'ipv6_prefix_len': '64',
                'ipv6_gateway': '2020:db8:1::251',
                'ipv6_pri_dns': '',
                'ipv6_sec_dns': ''},
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    cfg = {}
    
    if ip_type == CONST.IPV4:
        ipv4_cfg = _get_device_ipv4_cfg(zd)
        cfg = ipv4_cfg
    elif ip_type == CONST.IPV6:
        ipv4_cfg = {}
        ipv6_cfg = {}       
        ip_version = _get_device_ip_version(zd)
        cfg ['ip_version'] = ip_version
        
        if ip_version in [CONST.IPV4, CONST.DUAL_STACK]:
            ipv4_cfg = _get_device_ipv4_cfg(zd)
            cfg['vlan'] = ipv4_cfg.pop('vlan')
        else:
            cfg['vlan'] = zd.s.get_value(xloc['vlan'])
            
        if ip_version in [CONST.IPV6, CONST.DUAL_STACK]:
            ipv6_cfg = _get_device_ipv6_cfg(zd)
        
        cfg[CONST.IPV4] = ipv4_cfg
        cfg[CONST.IPV6] = ipv6_cfg
    else:
        raise Exception("IP type %s is incorrect." % ip_type)
    
    return cfg

def _get_device_ipv4_cfg(zd):
    '''
    Get device ip setting, ipv4 configuration.
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    #Get IPV4 settings.
    ks = ['ip_addr', 'netmask', 'gateway', 'pri_dns', 'sec_dns', 'vlan']
    ipv4_cfg = {}
    for k, loc in xloc['ip_alloc'].iteritems():
        if zd.s.is_checked(loc):
            ipv4_cfg['ip_alloc'] = k
            break
            
    # if the 'click here' is not visible and "Enabled Mgmt If" is checked
    # then get the details of additional mgmt interface boxes
    if not zd.s.is_element_present(xloc['ami_btn_visibled'], 1) or not zd.s.is_element_displayed(xloc['ami_btn_visibled'], 1):
        if zd.s.is_checked(xloc['ami_enabled_chk']):
            ks += ['ami_ip_addr', 'ami_netmask', 'ami_vlan']

    for k in ks:
        ipv4_cfg[k] = zd.s.get_value(xloc[k])
    
    return ipv4_cfg        
        
def _get_device_ipv6_cfg(zd):
    '''
    Get device IPV6 config.
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    #Get IPV6 settings.
    ipv6_ks = ['ipv6_addr','ipv6_prefix_len','ipv6_gateway','ipv6_pri_dns','ipv6_sec_dns']
    
    ipv6_cfg = {}
    for k in ipv6_ks:
        if zd.s.is_element_present(xloc[k]):
            ipv6_cfg[k] = zd.s.get_value(xloc[k])

    for k, loc in xloc['ipv6_alloc'].iteritems():
        if zd.s.is_element_present(loc):
            if zd.s.is_checked(loc):
                ipv6_cfg['ipv6_alloc'] = k
                break
            
    return ipv6_cfg
                
def _get_device_ip_version(zd):
    '''
    Get device ip version.
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    #Get IP veresion, which is added after ipv6 support.
    ip_version = CONST.IPV4
    if zd.s.is_element_present(xloc['ipv6_support_chk']):
        if zd.s.is_checked(xloc['ipv6_support_chk']):
            for k, loc in xloc['ip_version'].iteritems():
                if zd.s.is_checked(loc):
                    ip_version = k
                    break
                
    return ip_version.lower()

def _set_device_ip_version(zd, ip_version):
    '''
    Set ZD ip versions: ipv4, ipv6, dualstack.
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    
    if ip_version == CONST.IPV4:
        zd.s.click_if_checked(xloc['ipv6_support_chk'])
        time.sleep(4)
    else:
        zd.s.click_if_not_checked(xloc['ipv6_support_chk'])
        zd.s.click_if_not_checked(xloc['ip_version'][ip_version])
        
def _set_device_ipv6_settings(zd, ipv6_cfg):
    '''
    Set device ipv6 settings:
     ipv6_alloc: mauanl/auto
     For manual, set ipv6_addr, ipv6_prefix_len, ipv6_gateway, ipv6_pri_dns, ipv6_sec_dns items.     
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']
    
    k = 'ipv6_alloc'
    if k in ipv6_cfg:
        zd.s.click_if_not_checked(xloc[k][ipv6_cfg[k]])
        
    ipv6_alloc = ipv6_cfg[k]
    if ipv6_alloc == 'manual':
        ks = ['ipv6_addr', 'ipv6_prefix_len', 'ipv6_gateway', 'ipv6_pri_dns', 'ipv6_sec_dns']
        for k in ks:
            if ipv6_cfg.get(k):
                zd.s.type_text(xloc[k], ipv6_cfg[k])
            
def _wait_zd_restart(zd, time_out = 2000):
    '''
    Wait for zd retarted successfully.
    '''
    start_reboot_time = time.time()
    while True:
        waiting_time = time.time() - start_reboot_time
        if waiting_time > time_out:
            raise Exception('Could not login again to Zone Director after %s seconds' % waiting_time)
        else:
            time.sleep(30)
            if not zd.s.is_text_present("Restarting"):                                
                try:
                    zd.do_login()            
                    break
                except Exception, ex:
                    logging.warning('Exception:%s' % ex.message)
    
def _set_device_ip_settings(zd, cfg, l3sw = None):
    '''
    use cases:
    . main items:
      . manual: all main items
      . dhcp: vlan only
    . enable/disable additional interface: ami_enabled_chk
    . filling additional items: ami_*
    cfg:
    . ip_alloc, ip_addr, netmask, gateway, pri_dns, sec_dns, vlan: basic items
    . ami_ip_addr, ami_netmask, ami_vlan: additional items
    . ami_enabled_chk: is used in disabling additional interface case
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']

    k = 'ip_alloc'
    if k in cfg:
        zd.s.click_if_not_checked(xloc[k][cfg[k]])
        
        ip_alloc = cfg['ip_alloc'].lower()
    
        if ip_alloc == 'manual':
#            ks = ['ip_addr', 'netmask', 'gateway', 'pri_dns', 'sec_dns', 'vlan']
            ks = ['ip_addr', 'netmask', 'gateway', 'pri_dns', 'sec_dns']
            for k in ks:
                if cfg.get(k):
                    zd.s.type_text(xloc[k], cfg[k])

    zd.s.click_and_wait(xloc['apply_btn']) #apply first, new added
    zd.login()
    nav_to(zd)
    k = 'vlan'
    if k in cfg:
        old_vlan_id = zd.s.get_value(xloc[k])
        
        #@author: Anzuo, if cfg has no vlan ID, don't set vlan in SW
        if cfg[k] != old_vlan_id and cfg[k] != '':
            #L3 Switch Untagged to Tagged
            zd_mac = zd.mac_addr
            port = l3sw.mac_to_interface(zd_mac)
        
            logging.info("Set system interface manage VLAN %s" % (cfg[k],))

            nav_to(zd)
            zd.s.type_text(xloc[k], cfg[k])
            zd.s.click_and_wait(xloc['apply_btn'])

            time.sleep(10)
            l3sw.add_interface_to_vlan(port,cfg[k],tagging = True)
            time.sleep(40)

            zd.login()
            nav_to(zd)
    else:
        old_vlan_id = zd.s.get_value(xloc[k])
        #Jacky_Luh @ 2012-05-16
        if old_vlan_id != '' and old_vlan_id != '1':
            zd_mac = zd.mac_addr
            port = l3sw.mac_to_interface(zd_mac)

            logging.info("Remove system interface manage VLAN %s" % (old_vlan_id,))

            nav_to(zd)            
            zd.s.type_text(xloc[k], '')
            zd.s.click_and_wait(xloc['apply_btn'])
            
            try:
                old_vlan_idx = zd.s.get_value(xloc[k])
                if old_vlan_idx != '' or old_vlan_idx != '1':
                    nav_to(zd)            
                    zd.s.type_text(xloc[k], '1')
                    zd.s.click_and_wait(xloc['apply_btn'])
            except:
                pass
            
            time.sleep(2)
            l3sw.remove_interface_from_vlan(port,str(int(old_vlan_id)))
            l3sw.add_interface_to_vlan(port,str(int(old_vlan_id)),tagging = False)
            time.sleep(40)
               
            zd.login()
            nav_to(zd)            
            
    # the user want to enabled or disabled the addtional mgmt interface
    # NOTE: no validation btw this and ami_* is performed in this function
    k = 'ami_enabled_chk'
    if k in cfg:
        _set_device_ip_setting_enable_ami(zd, cfg[k])

    # if one of this param is in the cfg
    # then setting the additional mgmt if
    ami_ks = ['ami_ip_addr', 'ami_netmask', 'ami_vlan']
    if __is_in(ami_ks, cfg.keys()):
        _set_device_ip_setting_enable_ami(zd, True)
        time.sleep(0.5)
        for k in ami_ks:
            if k in cfg:
                zd.s.type_text(xloc[k], cfg[k])
        return


def _set_device_ip_setting_enable_ami(zd, enabled = True):
    '''
    return
    . True if check on the 'Enable Management Interface' checkbox
    . False on other cases
    '''
    xloc = LOCATOR_CFG_SYSTEM_NETWORKMGMT['dev_ip_settings']

    if zd.s.is_element_present(xloc['ami_btn_visibled'], 1):
        # if disabled and 'click here' is visible
        # then it is in correct state, do nothing
#        if not enabled and zd.s.is_element_displayed(xloc['ami_btn_visibled'], 1):
        if not enabled and zd.s.is_element_visible(xloc['ami_btn_visibled'], 1):

            return False

        # if 'click here' is visible then click to open additional mgmt if
#        if zd.s.is_element_displayed(xloc['ami_btn_visibled'], 1):
        if zd.s.is_element_visible(xloc['ami_btn_visibled'], 1):

            zd.s.click_and_wait(xloc['ami_btn'])

    if (enabled and zd.s.is_checked(xloc['ami_enabled_chk'])) or \
       (not enabled and not zd.s.is_checked(xloc['ami_enabled_chk'])):
        return False

    zd.s.click_and_wait(xloc['ami_enabled_chk'], 1)
    return True

def _set_advance_syslog(zd, **kwargs):
    """
    This method support to config the advance option of zd syslog feature
    @author: An Nguyen, Feb 2013
    """
    xlocs = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    adv_opt = ['zd_facility_name', 'zd_priority_level', 'ap_facility_name', 'ap_priority_level']
    adv_cfg = {'pause': 1}
    adv_cfg.update(kwargs)
    
    if zd.s.is_element_present(xlocs['syslog_advanced_setting_collapse']):
        zd.s.click_and_wait(xlocs['syslog_advanced_setting_click'])
        time.sleep(adv_cfg['pause'])
        
    for key in adv_opt:
        if adv_cfg.get(key) is not None:
            zd.s.select_value(xlocs[key], adv_cfg[key])

def _get_advance_syslog_setting(zd): 
    res = {'zd_facility_name': None,
           'zd_priority_level': None,
           'ap_facility_name': None,
           'ap_priority_level': None}
    
    xlocs = LOCATOR_CFG_SYSTEM_NETWORKMGMT
    for key in res.keys():
        try:
            res[key] = zd.s.get_selected_value(xlocs[key])
        except Exception, e:
            res[key] = e.message
    
    return res

##################################################################################
LOCATOR_CFG_SYSTEM_COUNTRY_CODE = {
    'country_code_listbox': '//select[@id="countrycode"]',
    'optimization_for_compatibility_radio': '//input[@id="opt-cmptb"]',
    'optimization_for_interoperability_radio': '//input[@id="opt-intprb"]',
    'optimization_for_performance_radio': '//input[@id="opt-perf"]',
    'allow_indoor_channel_checkbox': '//input[@id="do-channel-ctl"]'}
##################################################################################

def set_country_code(zd, option, **kwargs):
    """
    Configure the country code and related option
    """
    cfg_option = {'country_code': '',
                  'channel_optimization': '',
                  'channel_mode':''}    
    cfg_option.update(option)
    
    xloc = LOCATOR_CFG_SYSTEM_COUNTRY_CODE
    xloc_map = {
        'country_code': xloc['country_code_listbox'],
        'compatibility': xloc['optimization_for_compatibility_radio'],
        'interoperability': xloc['optimization_for_interoperability_radio'],
        'performance': xloc['optimization_for_performance_radio'],
        'allow_indoor': xloc['allow_indoor_channel_checkbox'],
        }
    nav_to(zd)
    
    if cfg_option['country_code']:
        zd.s.select_option(xloc_map['country_code'], re.escape(cfg_option['country_code']))
    if cfg_option['channel_optimization']:
        zd.s.click_and_wait(xloc_map[cfg_option['channel_optimization']])
    if cfg_option['channel_mode']:
        zd.s.click_if_not_checked(xloc_map[cfg_option['channel_mode']])
    
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(zd.info['loc_cfg_sys_ctrycode_apply_button'])
    if not zd.s.is_confirmation_present(5):
        raise Exception("No dialog confirmation for setting country code appeared")
    zd.s.get_confirmation()
    logging.info("Change country code option for ZoneDirector to %s successfully" % str(cfg_option))
    
##################################################################################

def __is_in(list1, list2):
    '''
    is one of item in list1 in list2?
    '''
    for i in list1:
        if i in list2:
            return True
    return False

#feature_update = {
#    '9.4.0.0': {
#        'DEFAULT_ZD_VLAN_ID': '1',
#    },
#}

    
def get_sys_log():
    return 'syslog: eventd_to_syslog():'

