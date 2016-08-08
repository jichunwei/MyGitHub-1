import logging
import time
import os
import re
import copy
import warnings

from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd
from RuckusAutoTest.components.lib.zd import aps
from RuckusAutoTest.common import lib_Constant as CONST
from RuckusAutoTest.common import lib_List

#-----------------------------------------------------------------------------
# PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------

def set_ap_config_by_mac(
        zd, mac_addr,
        general_info = None,
        radio_config = None,
        ip_config = None,
        mesh_config = None,
        port_config = None
    ):
    '''
    mac_addr = '68:92:34:2a:9f:00',
    general_info = {
        'device_name': 'RuckusAP',
        'description': '',
        'device_location': 'Lab',
        'gps_latitude': '',
        'gps_longitude': '',
        'ap_group': 'System Default',
    },
    radio_config = {
        'radio_mode': { #[na, ng, bg] are valid radio modes
            'channelization': None,
            'channel': None,
            'power': None,
            'wlangroups': None,
            'wlan_service': None,
            'ac':None,
        },
        'override_parent': True,
    },
    ip_config = {
        'ip_mode': '', #[manual, dhcp, as_is] are valid IP modes
        'ip_param': {
            'ip_addr': '192.168.0.123',
            'net_mask': '255.255.255.0',
            'gateway': '192.168.0.253',
            'pri_dns': '192.168.0.252',
            'sec_dns': '',
        },
    },
    mesh_config = {
        'mesh_mode': '', #[auto, root, mesh, disabled] are valid mesh modes
        'mesh_param': {
            'uplink_mode': '', #[smart, manual] are valid uplink modes
            'uplink_aps': ['68:92:34:2a:9f:00'], #mac_addr lists
        },
    },
    port_config = {
        'override_parent': True,
        'lan1': {
            'enabled': True,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    items = (
        (general_info, _set_ap_general),
        (ip_config, _set_ap_ip_config),
        (mesh_config, _set_ap_mesh),
    )

    if radio_config:
        if radio_config.has_key('override_parent'):
            radio_config.pop('override_parent')
            
        _set_ap_radios_all(zd, radio_config)

    if port_config:
        _set_ap_port_config(zd, port_config)

    for item in items:
        # only sets the value when it is provided
        # this is to improve performance
        if item[0] is not None:
            item[1](zd, **item[0])

    _save_and_close_ap_dialog(zd)

    zd.re_navigate()


def set_ap_general_by_mac_addr(
        zd, mac_addr, device_name = None, description = None,
        device_location = None, gps_latitude = None, gps_longitude = None,
        ap_group = None
    ):
    '''
    general_info = {
        'device_name': 'RuckusAP',
        'description': '',
        'device_location': 'Lab',
        'gps_latitude': '',
        'gps_longitude': '',
        'ap_group': 'System Default',
    }
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _set_ap_general(
        zd, device_name, description,
        device_location, gps_latitude, gps_longitude,
        ap_group
    )

    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def set_ap_radio_by_mac_addr(zd, mac_addr, radio_mode, radio_param_config ):
    '''
    radio_config = {
        'radio_mode': '', #[na, ng, bg] are valid radio modes
        'radio_param_config': {
            'channelization': 'Auto',
            'channel': 'Auto',
            'power': 'Auto',
            'wlangroups': 'Default',
            'wlan_service': True,
            'ac':'0',
        },
    }
    '''
    #@ZJ 20141011
    radio_param = {
            'channelization': 'Auto',
            'channel': 'Auto',
            'power': 'Auto',
            'wlangroups': 'Default',
            'wlan_service': True,
            'ac':'0',
            }
    radio_param.update(radio_param_config)
    #@ZJ 20141011
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)
    
    if zd.s.is_element_visible("//span[@id='not-joined']", timeout=2):
        raise Exception("[ZD web show when edit AP(%s)]---This Access Point is not approved/joined yet. Please connect it to proceed configuration." % mac_addr)

    info = _set_ap_radio(zd, radio_mode, radio_param)

    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def set_ap_ip_config_by_mac_addr(
        zd, mac_addr,
        ip_mode = 'manual',
        ip_param = {
            'ip_addr': None,
            'net_mask': None,
            'gateway': None,
            'pri_dns': None,
            'sec_dns': None,
        },
        ip_type = CONST.IPV4,                      
    ):
    '''
    For version is 4:
    ip_config = {
        'ip_mode': '', #[manual, dhcp, as_is] are valid IP modes
        'ip_param': {
            'ip_addr': '192.168.0.123',
            'net_mask': '255.255.255.0',
            'gateway': '192.168.0.253',
            'pri_dns': '192.168.0.252',
            'sec_dns': '',
        },
    }
    
    For version is 6:    
        'ip_mode': '',  #Don't need it for version 6.
        'ip_param:'     
         {'ip_version': 'dualstack',
          'ipv4': {'ip_mode': 'dhcp',
                            'ip_addr': '192.168.0.2',
                            'netmask': '255.255.255.0',
                            'gateway': '192.168.0.253',
                            'pri_dns': '192.168.0.252',
                            'sec_dns': '',},
          'ipv6': {'ipv6_mode': 'manual',
                            'ipv6_addr': '2020:db8:1::2',
                            'ipv6_prefix_len': '64',
                            'ipv6_gateway': '2020:db8:1::251',
                            'ipv6_pri_dns': '',
                            'ipv6_sec_dns': ''},
      }
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)
    
    info = _set_ap_ip_config(zd, ip_mode, ip_param, ip_type)
    
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info

def set_ap_mesh_by_mac_addr(
        zd, mac_addr,
        mesh_mode = 'auto',
        mesh_param = {
            'uplink_mode': 'smart',
        }
    ):
    '''
    mesh_config = {
        'mesh_mode': '', #[auto, root, mesh, disabled] are valid mesh modes
        'mesh_param': {
            'uplink_mode': '', #[smart, manual] are valid uplink modes
            'uplink_aps': ['68:92:34:2a:9f:00'], #mac_addr lists
        },
    }
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _set_ap_mesh(zd, mesh_mode, mesh_param)

    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def set_ap_port_config_by_mac(
        zd, mac_addr, port_config
    ):
    '''
    port_config = {
        'override_parent': True,
        'lan1': {
            'enabled': True,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _set_ap_port_config(zd, port_config)

    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info

def set_ap_network_setting_by_mac(zd, mac_addr, ipmode):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']

    override_loc = xloc['ip_version2']['override_parent']
    version_loc = xloc['ip_version2']['ip_version']

    if ipmode == '*':
        zd.s.click_if_checked(override_loc)
    else:
        zd.s.click_if_not_checked(override_loc)
        zd.s.select_value(version_loc, ipmode)
        
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

def get_ap_config_by_mac(zd, mac_addr):
    '''
    general_info = {
        'device_name': 'RuckusAP',
        'description': '',
        'device_location': 'Lab',
        'gps_latitude': '',
        'gps_longitude': '',
        'ap_group': 'System Default',
    },
    radio_config = {
        'radio mode': { #[na, ng, bg] are valid radio modes
            'channelization': None,
            'channel': None,
            'power': None,
            'wlangroups': None,
            'wlan_service': None,
        },
    },
    ip_config = {
        'ip_mode': '', #[manual, dhcp, as_is] are valid IP modes
        'ip_param': {
            'ip_addr': '192.168.0.123',
            'net_mask': '255.255.255.0',
            'gateway': '192.168.0.253',
            'pri_dns': '192.168.0.252',
            'sec_dns': '',
        },
    },
    mesh_config = {
        'mesh_mode': '', #[auto, root, mesh, disabled] are valid mesh modes
        'mesh_param': {
            'uplink_mode': '', #[smart, manual] are valid uplink modes
            'uplink_aps': ['68:92:34:2a:9f:00'], #mac_addr lists
        },
    port_config = {
        'override_parent': True,
        'lan1': {
            'enabled': True,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    items = (
        ('general_info', _get_ap_general_info),
        ('radio_config', _get_ap_radio_config),
        ('ip_config', _get_ap_ip_config),
        ('mesh_config', _get_ap_mesh_config),
        ('port_config', _get_ap_port_config)
    )

    ap_config = {}
    for item in items:
        ap_config.update({item[0]: item[1](zd, mac_addr)})

    _cancel_and_close_ap_dialog(zd)

    zd.re_navigate()

    return ap_config


def get_ap_general_info_by_mac(zd, mac_addr):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _get_ap_general_info(zd)

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def get_ap_radio_config_by_mac(
        zd, mac_addr,
        radio_list = ['na', 'ng']
    ):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _get_ap_radio_config(zd, mac_addr, radio_list)

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def get_ap_network_setting_by_mac(zd, mac_addr):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']

    override_loc = xloc['ip_version2']['override_parent']
    version_loc = xloc['ip_version2']['ip_version']

    info = dict()

    if zd.s.is_checked(override_loc):
        value = zd.s.get_value(version_loc)
        info = {'ip_mode': value, 'ip_version': value}
    else:
        ip_mode = '*' # use parent, not override group config
        zd.s.click_if_not_checked(override_loc)
        value = zd.s.get_value(version_loc)
        zd.s.click_if_checked(override_loc)
        info = {'ip_mode': ip_mode, 'ip_version': value}
        
    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info

def get_ap_ip_config_by_mac(zd, mac_addr, ip_type = CONST.IPV4):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _get_ap_ip_config(zd, mac_addr, ip_type)

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def get_ap_mesh_config_by_mac(zd, mac_addr):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _get_ap_mesh_config(zd)

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info


def get_ap_port_config_by_mac(zd, mac_addr):
    '''
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)

    info = _get_ap_port_config(zd)

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return info

def set_channelization(zd,mac_addr,channelization='20', radio='na'):
    '''
    radio=ng/na/bg
    '''
    loc = LOCATORS_CFG_ACCESSPOINTS
    check_box=loc['check_channelization']%radio
    select_box = loc['select_channelization']%radio
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)
    
    zd.s.click_if_not_checked(check_box)
    zd.s.select_value(select_box,channelization)
    
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()


def get_selectable_channel_list(zd,mac_addr, radio='ng'):
    '''
    radio=ng/na/bg
    '''
    loc = LOCATORS_CFG_ACCESSPOINTS
    check_box=loc['check_channel']%radio
    select_box = loc['select_channel']%radio
    
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)
    
    zd.s.click_if_not_checked(check_box)
    channel_list=zd.s.get_select_options(select_box)
    if 'Auto' in channel_list:
        channel_list.remove('Auto')

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return channel_list


def set_channel_range(zd,ap_mac,enable=True,radio='ng',enable_channel_index_list=[]):
    '''
    radio=ng/na/bg
    '''
    loc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac)
    channel_checkbox = loc['channel_checkbox']%(radio,'%s')
    enable_checkbox = loc['channel_setting_enable_checkbox']%radio

    if not enable:
        zd.s.click_if_checked(enable_checkbox)
    else:
        zd.s.click_if_not_checked(enable_checkbox)
        channel_idx=1
        while True:
            check_box = channel_checkbox%channel_idx
            if zd.s.is_element_present(check_box) and zd.s.is_visible(check_box):
                if channel_idx in enable_channel_index_list:
                    zd.s.click_if_not_checked(check_box)
                else:
                    zd.s.click_if_checked(check_box)  
                channel_idx+=1
            else:
                break   
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()


def enable_all_channel(zd,ap_mac,radio='ng'):
    '''
    radio=ng/na/bg
    '''
    loc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac)
    channel_checkbox = loc['channel_checkbox']%(radio,'%s')
    enable_checkbox = loc['channel_setting_enable_checkbox']%radio

    zd.s.click_if_not_checked(enable_checkbox)
    channel_idx=1
    while True:
        check_box = channel_checkbox%channel_idx
        if zd.s.is_element_present(check_box) and zd.s.is_visible(check_box):
            zd.s.click_if_not_checked(check_box)
        else:
            logging.info('the %sth checkbox not found,all channel enabled'%channel_idx)
            break   
        channel_idx+=1
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()


def config_5_8G_channel(zd,ap_mac,override=True,enable=True):
    loc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac)
    
    if not override:
        zd.s.click_if_checked(loc['ap_5_8G_override_group_checkbox'])
    else:
        zd.s.click_if_not_checked(loc['ap_5_8G_override_group_checkbox'])
        if enable:
            zd.s.click_if_not_checked(loc['ap_5_8_G_enable_checkbox'])
        else:
            zd.s.click_if_checked(loc['ap_5_8_G_enable_checkbox'])
        
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()
   
   

def verify_channel_range(zd,ap_mac,channel_list,radio='ng'):
    '''
    radio=ng/na/bg
    '''
    #return True if in ap configure page has and only has the channels in channel_list,or return False
    #convert the channel in channel list to str
    for i in range(len(channel_list)):
        channel_list[i]=str(channel_list[i])
    logging.info('the channel list to verify %s'%channel_list)
        
    loc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac)
    channel_lable = loc['channel_lable']%(radio,'%s')
    channel_checkbox = loc['channel_checkbox']%(radio,'%s')
    for channel in channel_list:
        lable = channel_lable%channel
        if not zd.s.is_element_present(lable):
            logging.error("channel %s not exist"%channel)
            _cancel_and_close_ap_dialog(zd)
            return False
    overflow_channel_index=len(channel_list)+1
    not_exist_checkbox = channel_checkbox%overflow_channel_index
    logging.info('check element %s not present'%not_exist_checkbox)
    
    selectable_chanel_list = get_selectable_channel_list(zd,ap_mac, radio)
    temp = [int(channel) for channel in selectable_chanel_list]
    selectable_chanel_list = copy.copy(temp)
    
    logging.info('selectable channel list is %s'%selectable_chanel_list) 
    
    if zd.s.is_element_present(not_exist_checkbox) and zd.s.is_visible(not_exist_checkbox):
        logging.error("channel list is longer than expected")
        _cancel_and_close_ap_dialog(zd)
        return False

    #convert the channel in selectable_chanel_list to str
    for i in range(len(selectable_chanel_list)):
        selectable_chanel_list[i]=str(selectable_chanel_list[i])
        
    if not lib_List.list_in_list(selectable_chanel_list, channel_list):
        logging.error("selectable channel(%s) not in channel list(%s)"%(selectable_chanel_list, channel_list))
        _cancel_and_close_ap_dialog(zd)
        return False
    if not lib_List.list_in_list(channel_list,selectable_chanel_list):
        logging.error("channel list(%s) not in selectable  channel list(%s)"%(channel_list,selectable_chanel_list))
        _cancel_and_close_ap_dialog(zd)
        return False
    
    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()
    return True


def disable_channel_selection_related_group_override(zd,ap_mac):

    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac)

    _disable_channel_selection_related_group_override(zd,ap_mac)
    
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

#-----------------------------------------------------------------------------
#  PRIVATE SECTION
#-----------------------------------------------------------------------------

AP_INFO_HDR_MAP = {
    'description': 'description',
    'devname': 'device_name',
    'ip': 'ip_address',
    'ipv6': 'ipv6',
    'mac': 'mac_address',
    'mesh_mode': 'mesh_mode',
    'mgmt_vlan_id': 'vlan',
    'model': 'model',
    'num_sta': 'clients',
    'radio_channel': 'channel',
    'state': 'status',
    'extipport': 'extipport',
}

locators = dict(
    ap_tbl_loc = "//table[@id='ap']",
    ap_tbl_nav_loc = "//table[@id='ap']/tfoot",
    ap_tbl_filter_txt = "//table[@id='ap']/tfoot//input[@type='text']",
    ap_detail_dialog_btn = "//span[contains(@id, 'edit')]",
)

LOCATORS_CFG_ACCESSPOINTS = dict(
    select_coordinate_source = r"//*[@id='manual-source']", ##@ZJ 20141020 fix ZF-10195 for AP7782
    edit_by_mac_addr = r"//table[@id='ap']//tr/td[text()='%s']/../td/span",
    edit_description = r"//table[@id='table-ap']//input[@id='description']",

    edit_channelization = r"//table[@id='table-ap']//select[@id='channelization-11%s']",
    edit_channel = r"//table[@id='table-ap']//select[@id='channel-11%s']",
    edit_power = r"//table[@id='table-ap']//select[@id='power-11%s']",
    edit_wlangroups = r"//table[@id='table-ap']//select[@id='wlangroup-11%s']",
    wlan_service_checkbox = "//input[@id='enabled-11%s']",
    edit_ac = r"//table[@id='table-ap']//select[@id='ac-11%s']",

    edit_mesh_mode_auto = "//table[@id='table-ap']//input[@id='mesh-mode-auto']",
    edit_mesh_mode_rootap = "//table[@id='table-ap']//input[@id='mesh-mode-rap']",
    edit_mesh_mode_meshap = "//table[@id='table-ap']//input[@id='mesh-mode-map']",
    edit_mesh_mode_disable = "//table[@id='table-ap']//input[@id='mesh-mode-disable']",

    check_ap_uplink = r"//div[@id='uplinks']//div[%s]/input",
    ap_uplink_label = r"//div[@id='uplinks']//div[%s]/label",

    edit_OK = r"//form[@id='form-ap']//input[@id='ok-ap']",
    edit_Cancel = r"//form[@id='form-ap']//input[@id='cancel-ap']",

    select_global_txpower = r"//select[@id='power-%s']",
    edit_apglobal_apply = r"//input[@id='apply-apglobalconf']",

    check_zp_ip = r"//input[@id='enable-zd-ip']",
    edit_primary_zd_ip = r"//input[@id='zd-prim-ip']",
    edit_secondary_zd_ip = r"//input[@id='zd-sec-ip']",
    enable_config_zd_setting = r"//input[@id='disable-keep-zd-ip']",
    prefer_prim_zd = r"//input[@id='prefer-prim-zd']",
    keep_ap_setting = r"//input[@id='enable-keep-zd-ip']",
    enable_keep_zd_ip = r"//input[@id='enable-keep-zd-ip']",
    edit_zd_ip_apply = r"//input[@id='apply-appolicy']",
    #@author: li.pingping @bug: ZF-8368 @since: 2014-5-15
    confirm_ap_mgmt_vlan_checkbox=r"//div[@class='reconfirm-checkmsg']//input[@type='checkbox']",
    confirm_prim_sec_zd_OK_button = r"//div[10]/div/div/div[3]/button[1]",
    confirm_prim_sec_zd_Cancel_button = r"//div[10]/div/div/div[3]/button[2]",
    
    edit_ap_device_name = r"//input[@id='devname']",
    edit_ap_device_location = r"//input[@id='location']",
    edit_ap_device_gps_latitude = r"//input[@id='latitude']",
    edit_ap_device_gps_longitude = r"//input[@id='longitude']",

    edit_parent_conf_channelization = r"//table[@id='table-ap']//input[@id='parentconf-channelization-11%s']",
    edit_parent_conf_channel = r"//table[@id='table-ap']//input[@id='parentconf-channel-11%s']",
    edit_parent_conf_power = r"//table[@id='table-ap']//input[@id='parentconf-power-11%s']",
    edit_parent_conf_wlangroups = r"//table[@id='table-ap']//input[@id='parentconf-wlangroup-11%s']",
    edit_parent_conf_ac = r"//table[@id='table-ap']//input[@id='parentconf-ac-11%s']",#na, ng

    edit_ap_search_textbox = r"//table[@id='ap']//span[@class='other-act']/input",

    aps_table_id = "apsummary",
    ap_info_cell_base_on_mac = "//table[@id='apsummary']//tr/td/a[text()='%s']/../../td[%s]",
    ap_restart_button_base_on_mac = "//table[@id='apsummary']//tr/td/a[text()='%s']/../../td[@class='action']/img[contains(@id, 'restart')]",
    ap_info_cell_base_on_idx = "//table[@id='apsummary']//tr[@idx='%s']/td[%s]",
    aps_next_image = "//img[@id='next-apsummary']",
    aps_total_number_span = "//table[@id='apsummary']//div[@class='actions']/span",
    aps_search_textbox = "//table[@id='apsummary']//span[@class='other-act']/input",
    select_11N_mode_2_4G = r"//select[@id='mode-2.4G']",
    select_11N_mode_5G = r"//select[@id='mode-5G']",

    #add load-balancing
    enable_load_balance_input = r"//input[@id='balance-enable']",
    disable_load_balance_input = r"//input[@id='balance-disable']",
    
    #Cherry: add for ip mode and ipv6 settings
    ap_ip_settings = dict(        
        ip_version = dict (
            ipv4 = r"//input[@id='ipv4mode']",
            ipv6 = r"//input[@id='ipv6mode']",
            dualstack = r"//input[@id='dualmode']",
            ),
        ip_version2 = dict(override_parent = r"//input[@id='parentconf-cfgap-ipmode']",
                           ip_version = r"//select[@id='cfgap-ipmode']"
                           ),
        ipv6_mode = dict ( #ipv6 allocation type
            manual = r"//input[@id='manual-ipv6']",
            auto = r"//input[@id='autoconfig']",
            as_is = r"//input[@id='as-is-ipv6']",
            ),
        ipv6_addr = r"//input[@id='ipv6-addr']",
        ipv6_prefix_len = r"//input[@id='ipv6-plen']",
        ipv6_gateway = r"//input[@id='ipv6-gateway']",
        ipv6_pri_dns = r"//input[@id='ipv6-dns1']",
        ipv6_sec_dns = r"//input[@id='ipv6-dns2']",
    ),
    
    #stan
    select_ap_group = r"//select[@id='ap-group']",

    check_channelization = r"//input[@id='parentconf-channelization-11%s']",
    check_channel = r"//input[@id='parentconf-channel-11%s']",
    check_power = r"//input[@id='parentconf-power-11%s']",
    check_wlangroups = r"//input[@id='parentconf-wlangroup-11%s']",
    
    select_channelization = r"//select[@id='channelization-11%s']",
    select_channel = r"//select[@id='channel-11%s']",
    
    check_port_override = r"//input[@id='parentconf-port-setting']",

    enableport_checkbox = r"//input[@id='ps-enableport-setting%s']",
    uplinkport_combo = r"//select[@id='ps-uplinkport-setting%s']",
    untagport_txt = r"//input[@id='ps-untagport-setting%s']",
    membersport_txt = r"//input[@id='ps-membersport-setting%s']",
    
    dot1x_guest_vlan_text = r"//input[@id='ps-guestport-setting%s']",
    dot1x_dvlan_chk = r"//input[@id='dvlan-enableport-setting%s']",
    
    #8021x setting.
    dot1xport_combo = r"//select[@id='ps-dot1xport-setting%s']",
    dot1x_auth_svr_combo = r"//select[@id='ps-authsvrport-setting']",
    dot1x_acct_svr_combo = r"//select[@id='ps-acctsvrport-setting']",  
    dot1x_mac_bypass_chk = r"//input[@id='ps-mac-authport-setting']",  
    
    dot1x_supp_mac_radio = r"//input[@id='ps-supp-macport-setting']",
    dot1x_supp_auth_radio = r"//input[@id='ps-supp-manualport-setting']",
    dot1x_supp_username_text = r"//input[@id='ps-supp-userport-setting']",
    dot1x_supp_password_text = r"//input[@id='ps-supp-pwdport-setting']",
    
    enable_2_4G_wlan_service_check_box = r"//input[@id='enabled-11ng']",
    enable_5_0G_wlan_service_check_box = r"//input[@id='enabled-11na']",
    
    ap_5_8G_override_group_checkbox = r"//input[@id='parentconf-do-cbandchann']",
    ap_5_8_G_enable_checkbox = r"//input[@id='do-cbandchann']",
    
    channel_lable = r"//span[@id='chl-11%s']//label[text()='%s']",#%(radio,channel)
    channel_checkbox = r"//input[@id='chl-11%s-%s']",#%(radio,channel_ixd)
    channel_setting_enable_checkbox = r"//input[@id='parentconf-chl-11%s']",#%radio

    mgmt_vlan_keep_ap_setting = r"//input[@id='keep-mgmt-vlan']",
    mgmt_vlan_not_keep_ap_setting = r"//input[@id='enable-mgmt-vlan']",
    mgmt_vlan_id_value = r"//input[@id='mgmt-vlan-ap']",
    #radio band switch
    check_radio_band = r"//input[@id='parentconf-do-workingradio']",
    radio_band_value = r"//select[@id='do-workingradio']",

    #Auto Recovery
    auto_recovery_check_box = r"//input[@id='enable-ap-auto-recovery']",
    auto_recovery_value = r"//input[@id='ap-auto-recovery']",

)


def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_POINT)


def _click_on_ap_btn(zd, match, loc, wait = 1.5):
    r = _get_ap_brief_by(zd, match, True)
    btn = (r['tmpl'] % r['idx']) + loc
    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn, wait)

    else:
        raise Exception('Unable to click on the button since it is disabled')


def _get_ap_brief_by(zd, match, verbose = False):
    '''
    '''
    _nav_to(zd)
    ap_info = widgets_zd.get_first_row_by(
        zd.s, locators['ap_tbl_loc'],
        locators['ap_tbl_nav_loc'], match,
        filter = locators['ap_tbl_filter_txt'],
        verbose = verbose,
    )

    return ap_info


def _open_ap_dialog_by_mac(zd, mac_addr):
    '''
    opens Access Point detail dialog for setting/getting values
    '''
    return _click_on_ap_btn(
        zd, dict(mac = mac_addr),
        locators['ap_detail_dialog_btn']
    )


def _save_and_close_ap_dialog(zd):
    '''
    saves and closes the Access Point detail dialog
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    zd.s.click_and_wait(xloc['edit_OK'])

    if zd.s.is_alert_present(1.5):
        _alert = zd.s.get_alert()
        raise Exception(_alert)


def _cancel_and_close_ap_dialog(zd):
    '''
    cancels and closes the Access Point detail dialog
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    zd.s.click_and_wait(xloc['edit_Cancel'])


def _get_ap_supported_radios(zd, mac_addr):
    '''
    '''
    ap_model = aps._get_ap_brief_by(zd, dict(mac = mac_addr))['model']

    return CONST.get_radio_mode_by_ap_model(ap_model)


def _get_ap_general_info(zd, mac_addr = ''):
    '''
    refers to get_ap_config_by_mac for docstring
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    items = (
        ('device_name', xloc['edit_ap_device_name']),
        ('description', xloc['edit_description']),
        ('device_location', xloc['edit_ap_device_location']),
        ('gps_latitude', xloc['edit_ap_device_gps_latitude']),
        ('gps_longitude', xloc['edit_ap_device_gps_longitude']),
    )

    general_info = {}
    for item in items:
        general_info.update({item[0]: zd.s.get_value(item[1])})

    #stan
    if zd.s.is_element_present(xloc['select_ap_group']):
        ap_group = zd.s.get_selected_label(xloc['select_ap_group'])
        general_info.update({'ap_group': ap_group})

    try:
        display = zd.s.is_element_displayed(xloc['check_radio_band'], 3)
    except:
        display = False

    if display:
        if zd.s.is_checked(xloc['check_radio_band']):
            type = 'override' 
            value = zd.s.get_selected_option(xloc['radio_band_value'])
        else:
            type = 'reserve'
            zd.s.click_if_not_checked(xloc['check_radio_band'])
            value = zd.s.get_selected_option(xloc['radio_band_value'])

        general_info.update({'radion_band_type': type, 'radion_band_value': value})

    return general_info


def _get_ap_radio_config(zd, mac_addr = '', radio_list = []):
    '''
    refers to get_ap_config_by_mac for docstring
    NOTE: Either radio_list or mac_addr must be provided
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS

    items = ['channelization', 'channel', 'power', 'wlangroups', 'ac']
    radio_param = dict((item, None) for item in items)

    if not isinstance(radio_list, list):
        radio_list = [radio_list]

    if not radio_list:
        radio_list = _get_supported_radio(zd, mac_addr)
        _open_ap_dialog_by_mac(zd, mac_addr)

    radio_params = {}
    for radio_mode in radio_list:
        param = copy.deepcopy(radio_param)
        if radio_mode in ['bg']:
            param.pop('channelization')
            logging.info('channelization is not for %s radio mode' % radio_mode)

        for item in param.iterkeys():
            loc = xloc['edit_%s' % item] % radio_mode
            parent_conf_loc = xloc['edit_parent_conf_%s' % item] % radio_mode

            if not zd.s.is_element_present(''.join([loc, '[@disabled]']), .2):
                param.update({item: zd.s.get_selected_option(loc)})

            elif zd.s.is_element_present(parent_conf_loc, .2):
                param.update({item: 'Group Config'})

        wlan_service = True
        xloc_wlan_service = xloc['wlan_service_checkbox'] % radio_mode
        if zd.s.is_element_present(xloc_wlan_service, .2):
            wlan_service = zd.s.is_checked(xloc_wlan_service)

        param.update({'wlan_service': wlan_service})

        radio_params.update({radio_mode: param})

    return radio_params

def _get_ap_ip_config(zd, mac_addr = '', ip_type = CONST.IPV4):
    '''
    refers to get_ap_config_by_mac for docstring
    '''
        
    ip_config = {}
    
    if ip_type == CONST.IPV4:
        ip_mode, ip_param = _get_ap_ipv4_config(zd)
        
        ip_config['ip_mode'] = ip_mode            
        ip_config['ip_param'] = ip_param
    elif ip_type == CONST.IPV6:
        ip_version = _get_ap_ip_version(zd)
        ip_config ['ip_version'] = ip_version

        ipv4_cfg = {}
        if ip_version in [CONST.IPV4, CONST.DUAL_STACK]:
            ip_mode, ip_param = _get_ap_ipv4_config(zd)
            ipv4_cfg['ip_mode'] = ip_mode
            ipv4_cfg.update(ip_param)
        
        ipv6_cfg = {}
        if ip_version in [CONST.IPV6, CONST.DUAL_STACK]:
            ipv6_cfg = _get_ap_ipv6_config(zd)
            
        ip_config[CONST.IPV4] = ipv4_cfg
        ip_config[CONST.IPV6] = ipv6_cfg

    return ip_config

def _get_ap_ipv4_config(zd):
    '''
    #Get ipv4 configuration.
    '''
    xpath_by_mode = {
        'dhcp': zd.info['loc_cfg_ap_dhcp_ip_radio'],
        'as_is': zd.info['loc_cfg_ap_keep_ap_setting_radio'],
        'manual': zd.info['loc_cfg_ap_manual_ip_radio'],
    }
    
    ip_mode = ''
    for (item, loc) in xpath_by_mode.iteritems():
        if zd.s.is_checked(loc):
            ip_mode = item
            break
    ip_param = {}
    
    if ip_mode == 'manual':
        ip_param = _get_ap_ip_config_manual(zd)
        
    return ip_mode, ip_param


#Updated by cwang@20130529, remove postfix tag v2, doesn't need feature update after 9.5
def _get_ap_ip_version(zd):
    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']
    ip_version = CONST.IPV4
    
    _dd = {'1':CONST.IPV4,
           '2':CONST.IPV6,
           '3':CONST.DUAL_STACK
           }
    override_loc = xloc['ip_version2']['override_parent']
    version_loc = xloc['ip_version2']['ip_version']
    
    if zd.s.is_checked(override_loc):
        value = zd.s.get_value(version_loc)
        return _dd[value]
                    
    return ip_version


def _get_ap_ipv6_config(zd):
    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']
    
    #Get IPV6 settings.
    ipv6_ks = ['ipv6_addr','ipv6_prefix_len','ipv6_gateway','ipv6_pri_dns','ipv6_sec_dns']
    
    ipv6_cfg = {}
    for k, loc in xloc['ipv6_mode'].iteritems():
        if zd.s.is_element_present(loc):
            if zd.s.is_checked(loc):
                ipv6_cfg['ipv6_mode'] = k
                break
    
    ipv6_mode = ipv6_cfg['ipv6_mode'].lower()    
    if ipv6_mode == 'manual':
        for k in ipv6_ks:
            if zd.s.is_element_present(xloc[k]):
                ipv6_cfg[k] = zd.s.get_value(xloc[k])
                    
    return ipv6_cfg

def _get_ap_ip_config_manual(zd):
    '''
    refers to get_ap_config_by_mac for docstring
    '''
    items = (
        ('ip_addr', zd.info['loc_cfg_ap_ip_address_textbox']),
        ('net_mask', zd.info['loc_cfg_ap_net_mask_textbox']),
        ('gateway', zd.info['loc_cfg_ap_gateway_textbox']),
        ('pri_dns', zd.info['loc_cfg_ap_pri_dns_textbox']),
        ('sec_dns', zd.info['loc_cfg_ap_sec_dns_textbox']),
    )

    ip_param = {}
    for item in items:
        ip_param.update({item[0]: zd.s.get_value(item[1])})

    return ip_param


def _get_ap_mesh_config(zd, mac_addr = ''):
    '''
    refers to get_ap_config_by_mac for docstring
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    xpath_by_mode = {
        'auto': xloc['edit_mesh_mode_auto'],
        'root': xloc['edit_mesh_mode_rootap'],
        'mesh': xloc['edit_mesh_mode_meshap'],
        'disabled': xloc['edit_mesh_mode_disable']
    }

    mesh_mode = 'disabled'
    for (mode, loc) in xpath_by_mode.iteritems():
        if zd.s.is_visible(loc) and zd.s.is_checked(loc):
            mesh_mode = mode
            break

    mesh_param = {}
    if mesh_mode in ['auto', 'mesh']:
        mesh_param = _get_mesh_uplink(zd)

    mesh_config = {
        'mesh_mode': mesh_mode,
        'mesh_param': mesh_param,
    }

    return mesh_config


def _get_mesh_uplink(zd):
    '''
    refers to get_ap_config_by_mac for docstring
    '''
    xpath_by_mode = {
        'smart': zd.info['loc_cfg_ap_smart_uplink_radio'],
        'manual': zd.info['loc_cfg_ap_manual_uplink_radio'],
    }

    uplink_mode = 'smart'
    for (item, loc) in xpath_by_mode.iteritems():
        if zd.s.is_checked(loc):
            uplink_mode = item
            break

    uplink_aps = []
    if uplink_mode == 'manual':
        uplink_aps = _get_mesh_uplink_aps(zd)

    mesh_param = {
        'uplink_mode': uplink_mode,
        'uplink_aps': uplink_aps,
    }

    return mesh_param


def _get_mesh_uplink_aps(zd):
    '''
    refers to get_ap_config_by_mac for docstring
    '''
    mesh_uplink_aps = []

    idx = 1
    while True:
        ul_ap_label = zd.info['loc_cfg_ap_uplink_label'].replace("$_$", str(idx))
        ul_ap_checkbox = zd.info['loc_cfg_ap_uplink_checkbox'].replace("$_$", str(idx))
        if not zd.s.is_element_present(ul_ap_label, .2):
            break

        if zd.s.is_checked(ul_ap_checkbox):
            ul_ap_text = zd.s.get_text(ul_ap_label).lower()
            matcher = re.compile(CONST.MAC_REGEX).match(ul_ap_text)

            if matcher:
                ul_ap_mac = matcher.groupdict()['mac']
                mesh_uplink_aps.append(ul_ap_mac)

        idx += 1 # moves on to the next uplink candidate available

    return mesh_uplink_aps


def _get_ap_port_config_detail(zd):
    '''
    {'lan1': {'dot1x': u'disabled',
          'enabled': True,
          'type': u'trunk',
          'untagged_vlan': u'1',
          'vlan_members': ''},
     'lan2': {'dot1x': u'auth-port',
              'dot1x_acct_svr': u'None',
              'dot1x_auth_svr': u'achris',
              'dot1x_mac_bypass_enabled': True,
              'enabled': True,
              'type': u'trunk',
              'untagged_vlan': u'1',
              'vlan_members': ''},
     'lan3': {'dot1x': u'auth-mac',
              'dot1x_acct_svr': u'None',
              'dot1x_auth_svr': u'achris',
              'dot1x_mac_bypass_enabled': True,
              'enabled': True,
              'type': u'access',
              'untagged_vlan': u'1',
              'vlan_members': ''},
     'override_parent': True}
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    port_config = {}

    idx = 1
    while True:
        loc = xloc['enableport_checkbox'] % idx
        if not zd.s.is_element_present(loc, .2):
            break

        settings = {}
        #mod by west.li,maybe the element not visible
        if zd.s.is_visible(loc):
            settings['enabled'] = zd.s.is_checked(loc)

        loc = xloc['uplinkport_combo'] % idx
        #mod by west.li,maybe the element not visible
        if zd.s.is_visible(loc):
            settings['type'] = zd.s.get_selected_value(loc)

        loc = xloc['untagport_txt'] % idx
        #mod by west.li,maybe the element not visible
        if zd.s.is_visible(loc):
            settings['untagged_vlan'] = zd.s.get_value(loc)

        settings['vlan_members'] = ''
        loc = xloc['membersport_txt'] % idx
#        if not zd.s.is_element_present(''.join([loc, '[@disabled]']), .2):
        settings['vlan_members'] = zd.s.get_value(loc)
            
#        elif setting['type'] == u'access':
#            settings['vlan_members'] = settings['untagged_vlan']
#        elif setting['type'] == u'trunk':
#            settings['vlan_members'] = u"1-4094"
                
        loc = xloc['dot1xport_combo'] % idx
        if zd.s.is_element_present(loc, .2):
            settings['dot1x'] = zd.s.get_selected_value(loc)
            if "disabled" != settings['dot1x']:
                if settings['dot1x'] in ['auth-port', 'auth-mac']:
                    loc = xloc['dot1x_auth_svr_combo']
                    settings['dot1x_auth_svr'] = zd.s.get_selected_option(loc)
                    
                    loc = xloc['dot1x_acct_svr_combo']
                    settings['dot1x_acct_svr'] = zd.s.get_selected_option(loc)
                    
                    loc = xloc['dot1x_mac_bypass_chk']                    
                    settings['dot1x_mac_bypass_enabled'] = zd.s.is_checked(loc)
                    
                    #Guest VLAN, Xian-9.5 Feature.                                        
                    if settings.get('type') == 'access' \
                        and settings.get('dot1x') == 'auth-mac':
                        loc = xloc['dot1x_dvlan_chk'] % idx                       
                        settings['dot1x_dvlan_enabled'] = zd.s.is_checked(loc)                                                                               
                        loc = xloc['dot1x_guest_vlan_text'] % idx
                        settings['dot1x_guest_vlan'] = zd.s.get_value(loc)                                        
                    
                elif settings['dot1x'] == 'supp':
                        loc = xloc['dot1x_supp_mac_radio']
                        settings['dot1x_supp_mac_enabled'] = zd.s.is_checked(loc)                            
                                                                            
                        loc = xloc['dot1x_supp_auth_radio']
                        if zd.s.is_checked(loc):
                            settings['dot1x_supp_auth_enabled'] = True
                            settings['dot1x_supp_username'] = zd.s.get_value(xloc['dot1x_supp_username_text'])
                            settings['dot1x_supp_password'] = zd.s.get_value(xloc['dot1x_supp_password_text'])
                        else:
                            settings['dot1x_supp_auth_enabled'] = False                                
                    

        port_config.update({'lan%s' % idx: settings})

        idx += 1 #moves on to the next lan port available

    return port_config


def _get_ap_port_config(zd, mac_addr = ''):
    '''
    port_config = {
        'override_parent': True,
        'lan1': {
            'enabled': True,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''

    xloc = LOCATORS_CFG_ACCESSPOINTS
    port_config = {}

    override_parent = False
    parent_conf_loc = xloc['check_port_override']
    if zd.s.is_element_present(parent_conf_loc):
        if zd.s.is_checked(parent_conf_loc):
            override_parent = True

    if override_parent:
        _get_ap_port_config_detail(zd)

    port_config['override_parent'] = override_parent
    port_config.update(_get_ap_port_config_detail(zd))

    return port_config


def _set_ap_general(
        zd, device_name = None, description = None,
        device_location = None, gps_latitude = None, gps_longitude = None,
        ap_group = None, radion_band_type = None, radion_band_value = None
    ):
    '''
    refers to set_ap_general_by_mac_addr() for docstring
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    items = (
        (device_name, xloc['edit_ap_device_name']),
        (description, xloc['edit_description']),
        (device_location, xloc['edit_ap_device_location']),
        (gps_latitude, xloc['edit_ap_device_gps_latitude']),
        (gps_longitude, xloc['edit_ap_device_gps_longitude']),
    )

    for item in items:
        #@ZJ 20141020 fix ZF-10195
        if item[0]:
            if item[1] == xloc['edit_ap_device_gps_latitude'] or item[1] == xloc['edit_ap_device_gps_longitude']:
                if zd.s.is_element_present(xloc['select_coordinate_source']):
                    zd.s.click_if_not_checked(xloc['select_coordinate_source'])
            zd.s.type_text(item[1], item[0])

    if ap_group is not None:
        if zd.s.is_element_present(xloc['select_ap_group'], 2):
            widgets_zd.do_select_item(zd, xloc['select_ap_group'], ap_group)
        else:
            raise Exception('%s not present'%xloc['select_ap_group'])

    try:#chen.tao 2014-02-07, to fix ZF-7518
        display = zd.s.is_element_displayed(xloc['check_radio_band'], 3)
    except:
        display = False
    try:
        if display and radion_band_type and radion_band_value:
            zd.s.click_if_not_checked(xloc['check_radio_band'])
            zd.s.select_option(xloc['radio_band_value'],radion_band_value)
            if radion_band_type == 'reserve':
                zd.s.click_if_checked(xloc['check_radio_band'])
    except Exception, e:
            raise Exception('Error occured while setting ap radio band, msg: %s' % e.message)


def _set_ap_radios_all(zd, radio_config):
    '''
    radio_config = {
        'radio_mode': { #[na, ng, bg] are valid radio modes
            'channelization': None,
            'channel': None,
            'power': None,
            'wlangroups': None,
            'wlan_service': None,
            'ac':None,#0, 10, 20, 30, 40 ...
        },
    },
    '''
    for radio_mode, radio_param in radio_config.iteritems():
        _set_ap_radio(zd, radio_mode, radio_param)


def _set_ap_radio(zd, radio_mode, radio_param):
    '''
    refers to set_ap_radio_by_mac_addr() for docstring
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS

    items = ['channelization', 'channel', 'power', 'wlangroups', 'ac']
    params = dict((item, None) for item in items)
    params.update(radio_param)

    if radio_mode in ['bg']:
        item = params.pop('channelization')
        logging.info('channelization is not for %s radio mode' % radio_mode)

    logging.debug("[onCfgAP changeRadio] %s" % (str(params)))

    # 9.0 supports to enable/disable WLAN Service for each radio
    if params.has_key('wlan_service'):
        wlan_service = params.pop('wlan_service')
        xloc_wlan_service = xloc['wlan_service_checkbox'] % radio_mode
        if wlan_service:
            if zd.s.is_element_visible(xloc_wlan_service):
                zd.s.click_if_not_checked(xloc_wlan_service)

        else:
            if zd.s.is_element_visible(xloc_wlan_service):
                zd.s.click_if_checked(xloc_wlan_service)
            
    for (param_k, param_v) in params.iteritems():
        override_parent = True
        if param_v:
            if param_v == 'Group Config':
                override_parent = False

            loc = xloc['edit_%s' % param_k] % radio_mode
            logging.debug("[onCfgAP select] 11%s %s = '%s'" % \
                          (radio_mode, param_k, param_v))

            parent_conf_loc = xloc['edit_parent_conf_%s' % param_k] % radio_mode
            if zd.s.is_element_visible(parent_conf_loc, .2):
                if override_parent:
                    zd.s.click_if_not_checked(parent_conf_loc)

                else:
                    zd.s.click_if_checked(parent_conf_loc)

            if zd.s.is_element_visible(loc,1) and not zd.s.is_element_present(''.join([loc, '[@disabled]']), .2):
                if param_k in ['ac']:
                    try:
                        zd.s.select_value(loc, param_v)
                    except:
                        zd.s.select_option(loc, param_v)
                else:
                    widgets_zd.do_select_item(zd, loc, param_v)
                time.sleep(1)


def _set_ap_band_switch(zd, radio_band):
    '''
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    xloc_radio_band = xloc['check_radio_band']

    if zd.s.is_element_present(xloc_radio_band, .2):
        zd.s.click_if_not_checked(xloc_radio_band)
        zd.s.select_option(xloc['radio_band_value'], radio_band)

#Updated by cwang@20130529, Remove postfix tag v2, doesn't need feature update after 9.5
def _set_ap_ip_config(zd, ip_mode, ip_param = {}, ip_type = CONST.IPV4):
    '''
    refers to set_ap_ip_config_by_mac_addr() for docstring
    '''
    xpath_by_mode = {
        'dhcp': zd.info['loc_cfg_ap_dhcp_ip_radio'],
        'as_is': zd.info['loc_cfg_ap_keep_ap_setting_radio'],
        'manual': zd.info['loc_cfg_ap_manual_ip_radio'],
    }
    
    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']
    
    if ip_type == CONST.IPV4:
        #For version is 4, we only set ipv4 configurations.
        #If version can be set and current ip version is ipv6, need to set it as ipv4.
        chk = zd.s.is_element_present        
        if chk(xloc['ip_version2']['override_parent'], 3):
            ip_version = CONST.IPV4
            _set_ap_ip_version(zd, ip_version)
                            
        #Set ipv4 configuration.
        zd.s.click_and_wait(xpath_by_mode[ip_mode])
        if ip_mode == 'manual':
            return _set_ap_ip_config_manual(zd, **ip_param)
        
    elif ip_type == CONST.IPV6:
        #For version is 6, we will set ip version, ipv4 and ipv6 configuration.        
        ip_cfg = ip_param
        
        if ip_cfg.get('ip_version'):
            ip_version = ip_cfg['ip_version'].lower()
        else:
            ip_version = CONST.IPV4
            
        _set_ap_ip_version(zd, ip_version)
        
        if ip_version in [CONST.IPV4, CONST.DUAL_STACK]:
            if ip_cfg.has_key(CONST.IPV4):
                ipv4_cfg = ip_cfg[CONST.IPV4]
            else:
                ipv4_cfg = {'ip_mode': 'as_is'}
                
            ip_mode = ipv4_cfg.get('ip_mode')
            zd.s.click_and_wait(xpath_by_mode[ip_mode])
            
            if ip_mode == 'manual':
                return _set_ap_ip_config_manual(zd,
                                                ip_addr = ipv4_cfg['ip_addr'],
                                                net_mask = ipv4_cfg['net_mask'],
                                                gateway = ipv4_cfg['gateway'],
                                                pri_dns = ipv4_cfg['pri_dns'],
                                                sec_dns = ipv4_cfg.get('sec_dns','')
                                                )
            
        if ip_version in [CONST.IPV6, CONST.DUAL_STACK]:
            if ip_cfg.has_key(CONST.IPV6):
                ipv6_cfg = ip_cfg[CONST.IPV6]
            else:
                ipv6_cfg = {'ipv6_mode': 'as_is'}
                
            _set_ap_ipv6_config(zd, ipv6_cfg)
            
    else:
        raise Exception("IP Type %s is incorrect." % ip_type)
    

#Updated by cwang@20130529, remove postfix tag v2, doesn't need feature update after 9.5
def _set_ap_ip_version(zd, ip_version, override_parent=True):
    '''
    Behavior change after 9.4, RadioButton -- > SelectItem
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']
    k = 'ip_version2'
    if override_parent:
        zd.s.click_if_not_checked(xloc[k]['override_parent'])
        _dd = {CONST.IPV4:'1',
               CONST.IPV6:'2',
               CONST.DUAL_STACK:'3'
               }
        zd.s.select_value(xloc[k]['ip_version'], _dd[ip_version])
        
    else:
        zd.s.click_if_checked(xloc[k]['override_parent'])
    
    
def _set_ap_ipv6_config(zd, ipv6_cfg):
    '''
    Set AP IPV6 settings:
      ipv6_mode: manual/auto
      For manual, set the items: 'ipv6_addr', 'ipv6_prefix_len', 'ipv6_gateway', 'ipv6_pri_dns', 'ipv6_sec_dns'
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS['ap_ip_settings']
    
    k = 'ipv6_mode'
    if k in ipv6_cfg:
        zd.s.click_if_not_checked(xloc[k][ipv6_cfg[k]])
        
    ipv6_mode = ipv6_cfg[k].lower()
    if ipv6_mode == 'manual':
        ks = ['ipv6_addr', 'ipv6_prefix_len', 'ipv6_gateway', 'ipv6_pri_dns', 'ipv6_sec_dns']
        for k in ks:
            if k in ipv6_cfg:
                zd.s.type_text(xloc[k], ipv6_cfg[k])

def _set_ap_ip_config_manual(
        zd, ip_addr = None,
        net_mask = None,
        gateway = None,
        pri_dns = None,
        sec_dns = None
    ):
    '''
    'ip_param': {
        'ip_addr': '192.168.0.123',
        'net_mask': '255.255.255.0',
        'gateway': '192.168.0.253',
        'pri_dns': '192.168.0.252',
        'sec_dns': '',
    },
    '''
    items = (
        (ip_addr, zd.info['loc_cfg_ap_ip_address_textbox']),
        (net_mask, zd.info['loc_cfg_ap_net_mask_textbox']),
        (gateway, zd.info['loc_cfg_ap_gateway_textbox']),
        (pri_dns, zd.info['loc_cfg_ap_pri_dns_textbox']),
        (sec_dns, zd.info['loc_cfg_ap_sec_dns_textbox']),
    )
    for item in items:
        # only sets the value when it is provided
        # this is to improve performance
        if item[0] is not None:
            zd.s.type_text(item[1], item[0])


def _set_ap_mesh(zd, mesh_mode, mesh_param = {}):
    '''
    refers to set_ap_mesh_by_mac_addr() for docstring
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    xpath_by_mode = {
        'auto': xloc['edit_mesh_mode_auto'],
        'root': xloc['edit_mesh_mode_rootap'],
        'mesh': xloc['edit_mesh_mode_meshap'],
        'disabled': xloc['edit_mesh_mode_disable']
    }

    zd.s.click_and_wait(xpath_by_mode[mesh_mode.lower()])

    uplink_mode = 'smart'
    if mesh_param:
        uplink_mode = mesh_param['uplink_mode']

    if mesh_mode in ['auto', 'mesh']:
        if mesh_param.has_key('uplink_aps'):
            uplink_aps = mesh_param['uplink_aps']

        else:
            uplink_aps = []

        _set_mesh_uplink(zd, uplink_mode, uplink_aps)


def _set_mesh_uplink(zd, uplink_mode, uplink_aps):
    '''
    refers to _set_ap_mesh() for docstring
    '''
    xpath_by_mode = {
        'smart': zd.info['loc_cfg_ap_smart_uplink_radio'],
        'manual': zd.info['loc_cfg_ap_manual_uplink_radio'],
    }

    if zd.s.is_element_present(xpath_by_mode[uplink_mode.lower()], .2):
        zd.s.click_and_wait(xpath_by_mode[uplink_mode.lower()])

    if uplink_mode == 'manual':
        return _set_mesh_uplink_manual(zd, uplink_aps)


def _set_mesh_uplink_manual(zd, uplink_aps):
    '''
    refers to _set_mesh_uplink() for docstring
    '''
    if not isinstance(uplink_aps, list):
        uplink_aps = [uplink_aps]

    # Show All APs
    zd.s.click_and_wait(zd.info['loc_cfg_ap_uplink_showall_anchor'], 3)

    idx = 1
    count = 0
    while True:
        ul_ap_label = zd.info['loc_cfg_ap_uplink_label'].replace("$_$", str(idx))
        ul_ap_checkbox = zd.info['loc_cfg_ap_uplink_checkbox'].replace("$_$", str(idx))
        if not zd.s.is_element_present(ul_ap_label, .2):
            break

        ul_ap_text = zd.s.get_text(ul_ap_label).lower()
        matcher = re.compile(CONST.MAC_REGEX).match(ul_ap_text)

        if matcher:
            ul_ap_mac = matcher.groupdict()['mac']
            if ul_ap_mac in uplink_aps:
                zd.s.click_if_not_checked(ul_ap_checkbox)
                count += 1
            else:
                zd.s.click_if_checked(ul_ap_checkbox)

        idx += 1 # moves on to the next uplink candidate available


    if count == 0:
        raise Exception("Not found any uplink AP to point to")

    if count < len(uplink_aps):
        # some uplink APs are checked successfully, but not all in uplink_aps list
        # may consider to raise an exception here
        logging.debug("Not all uplink APs can be checked")


def _set_ap_port_config_detail(zd, port, settings):
    '''
    port = 'lan1'
    settings = {
        'enabled': True,
        'type': 'trunk',              #[trunk, access, general]
        'untagged_vlan': '1',         #[1-4094, none] (expected String type)
        'vlan_members': '50,10-20',   #[1-4094] (expected String type)
        
        'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                
        'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
        'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
        'dot1x_mac_bypass_enabled': False, #optional param.
        
        'dot1x_supp_mac_enabled':False, #optional param.
        'dot1x_supp_auth_enabled':True, #optional param.
        'dot1x_supp_username':'ras.local.user',
        'dot1x_supp_password': 'ras.local.user',
    }
    
    '''

    xloc = LOCATORS_CFG_ACCESSPOINTS

    pid = port[-1]

    try:
        loc = xloc['enableport_checkbox'] % pid

    except KeyError:
        logging.info("The given port '%s' is not available.")
        return

    if settings['enabled']:
        zd.s.click_if_not_checked(loc)

    else:
        zd.s.click_if_checked(loc)
        #upon unchecked, its settings are not enabled to edit
        return

    loc = xloc['uplinkport_combo'] % pid
    port_type = settings.get('type')
    if port_type:
        zd.s.select_value(loc, settings['type'])
    
    
    loc = xloc['untagport_txt'] % pid
    if settings.get('untagged_vlan'):
        zd.s.type_text(loc, settings['untagged_vlan'])
        zd.s.type_keys(loc, '')

    loc = xloc['membersport_txt'] % pid
    if settings.get('vlan_members'):
        if not zd.s.is_element_present(''.join([loc, '[@disabled]']), .2):
            zd.s.type_text(loc, settings['vlan_members'])
            zd.s.type_keys(loc, '')

    loc = xloc['dot1xport_combo'] % pid
    if settings.get('dot1x'):
        # dot1x is not available with mesh enabled system
        if zd.s.is_element_present(loc, .2):
            zd.s.select_value(loc, settings['dot1x'])
        
        if settings['dot1x'] in ['auth-port', 'auth-mac']:        
            loc = xloc['dot1x_auth_svr_combo']
            if settings.get('dot1x_auth_svr'):            
                zd.s.select_option(loc, settings['dot1x_auth_svr'])
            
            loc = xloc['dot1x_acct_svr_combo']            
            if 'dot1x_acct_svr' in settings.keys() and settings['dot1x_acct_svr']:
                zd.s.select_option(loc, settings['dot1x_acct_svr'])
            
            loc = xloc['dot1x_mac_bypass_chk']            
            if 'dot1x_mac_bypass_enabled' in settings.keys():
                if settings['dot1x_mac_bypass_enabled']:
                    zd.s.click_if_not_checked(loc)
                else:
                    zd.s.click_if_checked(loc)
            
            #Guest VLAN, Xian-9.5 Feature.                                        
            if settings.get('type') == 'access' and \
                settings.get('dot1x') == 'auth-mac':
                
                loc = xloc['dot1x_dvlan_chk'] % pid
                if settings.get('enable_dvlan'):
                    enable = settings.get('enable_dvlan')
                    if enable == True:
                        zd.s.click_if_not_checked(loc)
                        if settings.get('guest_vlan'):
                            loc = xloc['dot1x_guest_vlan_text'] % pid
                            zd.s.type_text(loc, settings.get('guest_vlan'))
                        
                    elif enable == False:
                        zd.s.click_if_checked(loc)
                        
        elif settings['dot1x'] == 'supp':
            if settings['dot1x_supp_mac_enabled']:
                loc = xloc['dot1x_supp_mac_radio']
                zd.s.click_if_not_checked(loc)
                
            elif settings['dot1x_supp_auth_enabled']:
                loc = xloc['dot1x_supp_auth_radio']
                zd.s.click_if_not_checked(loc)
                
                loc = xloc['dot1x_supp_username_text']
                zd.s.type_text(loc, settings['dot1x_supp_username'])
                
                loc = xloc['dot1x_supp_password_text']
                zd.s.type_text(loc, settings['dot1x_supp_password'])
        
        


def _set_ap_port_config(zd, port_config):
    '''
    port_config = {
        'override_parent': True,
        'lan1': {
            'enabled': True,
            'type': 'trunk',              #[trunk, access, general]
            'untagged_vlan': '1',         #[1-4094, none] (expected String type)
            'vlan_members': '50,10-20',   #[1-4094] (expected String type)
            'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
        },
    }
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS

    override_parent = port_config['override_parent']
    parent_conf_loc = xloc['check_port_override']
    

    if zd.s.is_element_present(parent_conf_loc, .2):
        if override_parent:
            zd.s.click_if_not_checked(parent_conf_loc)

        else:
            zd.s.click_if_checked(parent_conf_loc)

        if zd.s.is_checked(parent_conf_loc):
            for port, settings in port_config.iteritems():
                if not settings or type(settings) is not dict:
                    continue

                # now the lan port and its config are provided
                _set_ap_port_config_detail(zd, port, settings)



def _disable_channel_selection_related_group_override(zd,ap_mac): 
    loc = LOCATORS_CFG_ACCESSPOINTS
    override_checkbox_list=[loc['channel_setting_enable_checkbox']%'ng',
                            loc['channel_setting_enable_checkbox']%'na',
                            loc['channel_setting_enable_checkbox']%'bg',
                            loc['ap_5_8G_override_group_checkbox'],
                            loc['check_channelization']%'ng',
                            loc['check_channelization']%'na',
                            loc['check_channelization']%'bg',]
    
    for checkbox in override_checkbox_list:
        if zd.s.is_element_present(checkbox) and zd.s.is_visible(checkbox):
            zd.s.click_if_checked(checkbox)
        


#-----------------------------------------------------------------------------
#  OLD/UN-MODIFIED METHODS + MODIFIED METHODS + ADAPTER METHODS SECTION
#-----------------------------------------------------------------------------

def get_wlan_groups_default_radio_values(radio_mode):
    '''
    '''
    bg_default = dict(channel = 'Auto', wlangroups = 'Default',
                      power = 'Auto')
    na_default = dict(channelization = 'Auto', channel = 'Auto',
                      power = 'Auto', wlangroups = 'Default')
    ng_default = dict(channelization = 'Auto', channel = 'Auto',
                      power = 'Auto', wlangroups = 'Default')

    if os.path.exists('RAT_5GCHANNEL_149'):
        na_default.update(channel = '149')

    if os.path.exists('RAT_TXPOWER_MIN'):
        na_default.update(power = 'Min')
        bg_default.update(power = 'Min')
        ng_default.update(power = 'Min')

    if radio_mode == 'na':
        return na_default

    elif radio_mode == 'bg':
        return bg_default

    else:
        return ng_default


def default_wlan_groups_by_mac_addr(zd, mac_addr_list):
    '''
    '''
    if type(mac_addr_list) is not list:
        mac_addr_list = [mac_addr_list]

    for mac_addr in mac_addr_list:
        ap_info = zd.get_all_ap_info(mac_addr)
        if ap_info:
            if ap_info['status'].lower().startswith("approval"):
                continue
        
        radio_mode = _get_supported_radio(zd, mac_addr)
        _open_ap_dialog_by_mac(zd, mac_addr)
        for rm in radio_mode:
            default_params = get_wlan_groups_default_radio_values(rm)
            _cfg_wlan_groups_by_mac_addr(zd, mac_addr, rm, default_params, '')
            time.sleep(1)

        _save_and_close_ap_dialog(zd)
        time.sleep(2)


def cfg_wlan_groups_by_mac_addr(
        zd, mac_addr_list, radio_params = {},
        description = None
    ):
    '''
    ap_rp = {'ng': {'wlangroups': 'Default', 'channel': '6'},
             'na': {'wlangroups': 'Default', 'channel': '149'}}

    cfg_wlan_groups_by_mac_addr(zd, ['00:1f:41:23:00:01'], ap_rp, 'Test Editing AP')
    '''
    r_params = dict()
    r_params.update(radio_params)
    for rm in r_params.keys():
        if r_params[rm].has_key('default') and r_params[rm]['default']:
            r_params[rm] = get_wlan_groups_default_radio_values(rm)

    if type(mac_addr_list) is not list:
        mac_addr_list = [mac_addr_list]

    for ap_mac_addr in mac_addr_list:
        _open_ap_dialog_by_mac(zd, ap_mac_addr)

        _set_ap_general(zd, description = description)
        for rm, rp in r_params.items():
            _cfg_wlan_groups_by_mac_addr(zd, ap_mac_addr, rm, rp, description)
            time.sleep(1)

        _save_and_close_ap_dialog(zd)


def enable_load_balancing(zd):
    '''
    Enable clients load-balancing
    '''
    _nav_to(zd)
    xloc = LOCATORS_CFG_ACCESSPOINTS
    zd.s.click_and_wait(xloc['enable_load_balance_input'])
    zd.s.click_and_wait(xloc['edit_zd_ip_apply'])


def disable_load_balancing(zd):
    '''
    Disable clients load-balancing
    '''
    _nav_to(zd)
    xloc = LOCATORS_CFG_ACCESSPOINTS
    zd.s.click_and_wait(xloc['disable_load_balance_input'])
    zd.s.click_and_wait(xloc['edit_zd_ip_apply'])


def _cfg_wlan_groups_by_mac_addr(
        zd, ap_mac_addr, radio_mode, radio_param = {},
        description = None
    ):
    '''
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS

    logging.info("[onCfgAP %s] [radio '%s'] [radio cfg %s] [description '%s']" %
                 (ap_mac_addr, radio_mode, str(radio_param), description))

    if description or type(description) in [str, unicode]:
        logging.info("[onCfgAP set] decription = '%s'" % (description))
        zd.s.type_text(xloc['edit_description'], description)
    #@ZJ 20141010  ZF-10263
    xloc_wlan_service = xloc['wlan_service_checkbox'] % radio_mode
    if zd.s.is_element_visible(xloc_wlan_service):
        zd.s.click_if_not_checked(xloc_wlan_service)
    #@ZJ 20141010  ZF-10263
    _cfg_ap_radio(zd, radio_mode, radio_param)


def _cfg_ap_radio(zd, radio_mode, radio_param = {}):
    '''
    '''
    return _set_ap_radio(zd, radio_mode, radio_param)


def get_cfg_info_by_mac_addr(zd, ap_mac_addr):
    '''
    WARNING: ADAPTER, please use get_ap_config_by_mac function.
    '''
    logging.info("Get AP radio configuration on Zone Director of AP [%s]" %
                 (ap_mac_addr))

    ap_info = {'mac': ap_mac_addr}

    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac_addr)
    ap_info['description'] = _get_ap_general_info(zd)['description']
    ap_info.update(_get_ap_radio_config(zd, ap_mac_addr)),

    ap_info['mesh_mode'] = _get_mesh_mode_cfg(zd)

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return ap_info


def _get_ap_radio(zd, radio_mode):
    '''
    WARNING: ADAPTER, please use _get_ap_radio_config function.
    '''
    mac_addr = ''
    return _get_ap_radio_config(zd, mac_addr, radio_mode)[radio_mode]


def assign_to_wlan_groups_by_radio(
        zd, ap_mac_addr, wlan_groups, radio = 'ng',
        description = None
    ):
    '''
    '''
    bg_params = ng_params  = na_params = dict(wlangroups = "Default")
    rm_cfg = {'bg': bg_params, 'ng': ng_params, 'na': na_params}
    if rm_cfg.has_key(radio):
        rm_cfg[radio]['wlangroups'] = wlan_groups

    cfg_wlan_groups_by_mac_addr(zd, ap_mac_addr, rm_cfg, description)


def get_supported_radio(zd, ap_mac_addr):
    '''
    WARNING: OBSOLETE, please use _get_ap_supported_radios function
    '''
    return _get_supported_radio(zd, ap_mac_addr)


def _get_supported_radio(zd, ap_mac_addr):
    '''
    WARNING: OBSOLETE, please use _get_ap_supported_radios function
    '''
    return _get_ap_supported_radios(zd, ap_mac_addr)


def assign_to_wlan_group(zd, ap_mac_addr, radio, wlan_group):
    '''
    Assign AP to wlan group
    Note:
        if AP support dual band like Dalmatian, call this function 2 times,
        each time for a radio.
    '''
    logging.info("Assign AP[%s] to [wlangroup %s]" % (ap_mac_addr.lower(), wlan_group))

    radio_param = {'wlangroups': wlan_group}
    return set_ap_radio_by_mac_addr(
        zd, ap_mac_addr, radio, radio_param
    )


def assign_to_default_wlan_group(zd, ap_mac_addr):
    '''
    Assign AP back to Default Wlan Group. Use this function on clean up function
    '''
    support_radio = get_supported_radio(zd, ap_mac_addr)

    for radio in support_radio:
        assign_to_wlan_group(zd, ap_mac_addr, radio, "Default")


def assign_all_ap_to_default_wlan_group(zd):
    '''
    Assign AP back to Default Wlan Group. Use this function on clean up function
    '''
    return assign_all_ap_to_specific_wlan_group(zd, 'Default')


def assign_all_ap_to_specific_wlan_group(zd, wlan_group):
    '''
    '''
    ap_sym_list = zd.get_all_ap_sym_dict()
    for ap_sym_name in ap_sym_list.keys():
        ap_mac = ap_sym_list[ap_sym_name]['mac']
        support_radio = get_supported_radio(zd, ap_mac)
        for radio in support_radio:
            assign_to_wlan_group(zd, ap_mac, radio, wlan_group)


def get_ap_cfg(zd, ap_mac_addr, support_radio = []):
    '''
    WARNING: ADAPTER, please use get_ap_config_by_mac function.
    '''
    ap_config = get_ap_config_by_mac(zd, ap_mac_addr)
    ap_config_info = {}

    radio_config = ap_config['radio_config']
    for radio in support_radio:
        ap_config_info['channel_%s' % radio] = radio_config[radio]['channel']
        ap_config_info['power_%s' % radio] = radio_config[radio]['power']
        ap_config_info['wlangroups_%s' % radio] = radio_config[radio]['wlangroups']


    ap_config_info['ip_management'] = {}

    ip_config = ap_config['ip_config']
    if ip_config['ip_mode'] == 'as_is':
        ap_config_info['ip_management']['by-dhcp'] = 'keep_ap_setting'

    else:
        ap_config_info['ip_management']['by-dhcp'] = ip_config['ip_mode']


    if ip_config['ip_mode'] == 'manual':
        ap_config_info['ip_management'].update(ip_config['ip_param'])


    mesh_config = ap_config['mesh_config']
    ap_config_info['mesh_mode'] = mesh_config['mesh_mode']

    ap_config_info['mesh_uplink_aps'] = []
    if mesh_config['mesh_mode'] in ['auto', 'mesh']:
        ap_config_info['mesh_uplink_mode'] = mesh_config['mesh_param']['uplink_mode']
        ap_config_info['mesh_uplink_aps'] = mesh_config['mesh_param']['uplink_aps']

    return ap_config_info


def cfg_global_tx_power(zd, txpwr_dict):
    '''
    '''
    warnings.warn('Not work under Udaipur 9.2', DeprecationWarning)

    xloc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)
    conf = {'2.4G':'Auto', '5G':'Auto'}
    conf.update(txpwr_dict)
    for radio in conf:
        select_txpower_xpath = xloc['select_global_txpower'] % radio
        zd.s.select_option(select_txpower_xpath, conf[radio])

    zd.s.click_and_wait(xloc['edit_apglobal_apply'])


def _get_mesh_mode_cfg(zd):
    '''
    WARNING: ADAPTER, please use _get_ap_mesh_config function.
    '''
    return _get_ap_mesh_config(zd)['mesh_mode']


def cfg_ap(zd, ap_mac_addr, cfg_set = {}):
    '''
    WARNING: ADAPTER, please use set_ap_config_by_mac function.
    '''
    params = {}
    params.update(cfg_set)

    _nav_to(zd)
    zd.refresh() 
    _open_ap_dialog_by_mac(zd, ap_mac_addr)

    if params.get('mesh_mode'):
        if params.get('uplink_option'):
            _set_ap_mesh(zd, params['mesh_mode'], params['uplink_option'])
        else:
            _set_ap_mesh(zd, params['mesh_mode'])
    
    if params.get('band_switch'):
        _set_ap_band_switch(zd, params['band_switch'])
    
    if params.get('radio'):
        radio_mode = params['radio']
        radio_param = {
            'channel': params['channel'] if params.get('channel') else None,
            'wlan_service': params['wlan_service'] if params.has_key('wlan_service') else None,
        }
        _set_ap_radio(zd, radio_mode, radio_param)

    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

    logging.info('[AP(%s) Setting] Modified on %s successfully' % (ap_mac_addr, params))


def get_limited_zd_discovery_cfg(zd, is_nav = True):
    '''
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    zd_discover_ip_cfg = dict(
        enabled = False,
        primary_zd_ip = '',
        secondary_zd_ip = ''
    )
    if is_nav:
        _nav_to(zd)
        time.sleep(0.5)

    if zd.s.is_checked(xloc['check_zp_ip']):
        zd_discover_ip_cfg['enabled'] = True
        #Get keep ap setting and prefer primary zd value.
        if zd.s.is_element_present(xloc['keep_ap_setting']):
            zd_discover_ip_cfg['keep_ap_setting'] = zd.s.is_checked(xloc['keep_ap_setting'])            
        if zd.s.is_element_present(xloc['prefer_prim_zd']):
            zd_discover_ip_cfg['prefer_prim_zd'] = zd.s.is_checked(xloc['prefer_prim_zd'])
            
        zd_discover_ip_cfg['primary_zd_ip'] = zd.s.get_value(xloc['edit_primary_zd_ip'])
        zd_discover_ip_cfg['secondary_zd_ip'] = zd.s.get_value(xloc['edit_secondary_zd_ip'])

    return zd_discover_ip_cfg


def cfg_limited_zd_discovery(zd, zd_discover_cfg, pause = 1.0, is_nav = True):
    '''
    Configure limited ZD discovery. 
    After 9.4, add keep_ap_setting and prefer primary zd checkbox.
    . is_nav: This param to support config Limited ZD Discover on ZD template
              from FlexMaster. If do this from FM, don't navigate.
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS

    zd_discover_ip_cfg = dict(
        enabled = False,
        primary_zd_ip = '',
        secondary_zd_ip = '',
        keep_ap_setting = False,
        prefer_prim_zd = False,
    )
    
    zd_discover_ip_cfg.update(zd_discover_cfg)
    
    if is_nav:
        _nav_to(zd)
    
    time.sleep(pause)
        
    if zd_discover_ip_cfg['enabled']:
        #Enable limited zd discovery setting.
        if not zd.s.is_checked(xloc['check_zp_ip']):
            zd.s.click_and_wait(xloc['check_zp_ip'])
            
        time.sleep(pause)
        
        if zd_discover_cfg.has_key('keep_ap_setting') and zd_discover_cfg['keep_ap_setting']:
            if not zd.s.is_checked(xloc['keep_ap_setting']):
                zd.s.click_and_wait(xloc['keep_ap_setting'])
                
            time.sleep(pause)
            
        else:
            if not zd.s.is_checked(xloc['enable_config_zd_setting']):
                zd.s.click_and_wait(xloc['enable_config_zd_setting'])
                
            time.sleep(pause)
                
            #Set prefer primary zd.
            if zd_discover_cfg['prefer_prim_zd']:
                if not zd.s.is_checked[xloc['prefer_prim_zd']]:
                    zd.s.click_and_wait(xloc['prefer_prim_zd'])
            else:
                zd.s.click_if_checked(xloc['prefer_prim_zd'])
                    
            if zd_discover_cfg.has_key('primary_zd_ip'):
                zd.s.type_text(xloc['edit_primary_zd_ip'], zd_discover_ip_cfg['primary_zd_ip'])
            if zd_discover_cfg.has_key('secondary_zd_ip'):
                zd.s.type_text(xloc['edit_secondary_zd_ip'], zd_discover_ip_cfg['secondary_zd_ip'])
    else:
        #Disable limited zd discovery.
        zd.s.click_if_checked(xloc['check_zp_ip'])
        time.sleep(pause)
        
    zd.s.click_and_wait(xloc['edit_zd_ip_apply'])
    
    if zd_discover_cfg.has_key('keep_zd_ip') and zd_discover_cfg['keep_zd_ip']:
        zd.s.click_if_not_checked(xloc['enable_keep_zd_ip'])
        zd.s.click_and_wait(xloc['edit_zd_ip_apply'])
        time.sleep(pause)
    
    #@author: li.pingping @bug: ZF-8368 @since: 2014-5-15
    if zd.s.is_element_present(xloc['confirm_prim_sec_zd_OK_button']):
        zd.s.click_and_wait(xloc['confirm_prim_sec_zd_OK_button'])
    
    #Raise exception is get any alert.
    time.sleep(pause * 3)
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        #Primary zd addr cannot be empty
        err_ptn_list = ['.* cannot be empty.*']
        
        is_match_err = False
        for ptn in err_ptn_list:
            if re.search(ptn, _alert, re.I):
                is_match_err = True
                break    
        
        if is_match_err:
            return _alert
        else:            
            raise Exception(_alert)
        
def verify_limited_zd_discovery(dict_1, dict_2):
    '''
    Verify two limited ZD discovery cfg dict are same.    
    '''
    status_1 = dict_1['enabled']
    status_2 = dict_2['enabled']
    
    err_msg = ''
    if status_1 != status_2:        
        err_msg = 'Status is different: %s, %s' % (status_1, status_2)
    else:
        if status_1 == True:
            keep_ap_setting_1 = dict_1.get('keep_ap_setting')
            keep_ap_setting_2 = dict_2.get('keep_ap_setting')
            if keep_ap_setting_1 != keep_ap_setting_2:
                err_msg = 'Keep AP setting are different: %s, %s' % (keep_ap_setting_1, keep_ap_setting_2)
            else:
                if keep_ap_setting_1 == False:
                    if dict_1.get('primary_zd_ip') != dict_2.get('primary_zd_ip'):
                        err_msg = "Primary ZD IP/ADDR are different: %s, %s" % (dict_1['primary_zd_ip'], dict_2['primary_zd_ip'])
                    if dict_1.get('secondary_zd_ip') != dict_2.get('secondary_zd_ip'):
                        err_msg = "Secondary ZD IP/ADDR are different: %s, %s" % (dict_1['secondary_zd_ip'], dict_2['secondary_zd_ip'])
                    if dict_1.get('prefer_prim_zd') != dict_2.get('prefer_prim_zd'):
                        err_msg = "Perfer primary ZD are different: %s, %s" % (dict_1['prefer_prim_zd'], dict_2['prefer_prim_zd'])
    return err_msg

def get_ap_device_info(zd, ap_mac_addr, pause = 1.0):
    '''
    WARNING: ADAPTER, please use get_ap_general_info_by_mac function.
    '''
    info = get_ap_general_info_by_mac(zd, ap_mac_addr)

    ap_info = dict(
        device_name = info['device_name'],
        device_location = info['device_location'],
        gps_coordinates = dict(latitude = info['gps_latitude'],
                               longitude = info['gps_longitude'])
    )

    return ap_info


def set_ap_device_info(zd, ap_mac_addr, ap_info, pause = 1.0):
    '''
    WARNING: ADAPTER, please use set_ap_general_by_mac_addr function.
    '''
    info = {
        'device_name': ap_info['device_name'] if ap_info.has_key('device_name') else '',
        'device_location': ap_info['device_location'] if ap_info.has_key('device_location') else '',
        'gps_latitude': ap_info['gps_coordinates']['latitude'] if ap_info.has_key('gps_coordinates') else '',
        'gps_longitude': ap_info['gps_coordinates']['longitude'] if ap_info.has_key('gps_coordinates') else '',
    }

    return set_ap_general_by_mac_addr(zd, ap_mac_addr, **info)


def set_ap_cfg_info(zd, cfg, pause = 1.0):
    '''
    WARNING: ADAPTER, please use set_ap_general_by_mac_addr function.
    '''
    mac_addr = cfg['mac']

    info = {
        'device_name': cfg['device_name'] if cfg.has_key('device_name') else '',
        'description': cfg['description'] if cfg.has_key('description') else '',
        'device_location': cfg['device_location'] if cfg.has_key('device_location') else '',
        'gps_latitude': cfg['gps_coordinates']['latitude'] if cfg.has_key('gps_coordinates') else '',
        'gps_longitude': cfg['gps_coordinates']['longitude'] if cfg.has_key('gps_coordinates') else '',
    }

    return set_ap_general_by_mac_addr(zd, mac_addr, **info)


def get_ap_cfg_info(zd, ap_mac_addr, pause = 1.0):
    '''
    WARNING: ADAPTER, please use get_ap_general_info_by_mac function.
    '''
    info = get_ap_general_info_by_mac(zd, ap_mac_addr)

    ap_info = dict(
        descrption = info['description'],
        device_name = info['device_name'],
        location = info['device_location'],
        gps_coordinates = dict(latitude = info['gps_latitude'],
                               longitude = info['gps_longitude'])
    )

    return ap_info


def get_11n_mode_only_info(zd, pause = 1.0):
    '''
    '''
    warnings.warn('Not work under Udaipur 9.2', DeprecationWarning)

    xloc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)

    info_11n_mode = dict()
    info_11n_mode['2.4G'] = zd.s.get_selected_label(xloc['select_11N_mode_2_4G'])
    info_11n_mode['5G'] = zd.s.get_selected_label(xloc['select_11N_mode_5G'])

    time.sleep(pause)

    return info_11n_mode


def set_11n_mode_only_info(zd, radio, mode, pause = 1.0):
    '''
    '''
    warnings.warn('Not work under Udaipur 9.2', DeprecationWarning)

    xloc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)

    if radio == "2.4G":
        zd.s.select_option(xloc['select_11N_mode_2_4G'], mode)

    elif radio == "5G":
        zd.s.select_option(xloc['select_11N_mode_5G'], mode)

    else:
        raise Exception("Invalid Radio Mode")

    zd.s.click_and_wait(xloc['edit_apglobal_apply'])
    time.sleep(pause)

def set_ap_tx_power(zd,ap_mac,radio,power='Full'):
    Num_list=['1','2','3','4','5','6','7','8','9','10']
    str_list=['auto','Auto','Full','full','Min','min','Global']
    fraction_list=['1/2','1/4','1/8']
    if power in Num_list or str(power) in Num_list :
        power='-%sdB'%power
    elif power in str_list:
        power=power.capitalize()
    elif power in fraction_list:
        if power == '1/2':
            power='-3dB'
        if power == '1/4':
            power='-6dB'
        if power == '1/8':
            power='-9dB'
    else:
        raise('wrong parameter for power:%s'%power)
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd,ap_mac)
    if radio=='2.4':
        check_box=zd.info['loc_cfg_ap_txpower_11ng_checkbox']
        selection=zd.info['loc_cfg_ap_txpower_11ng_option']
    elif radio=='5':
        check_box=zd.info['loc_cfg_ap_txpower_11na_checkbox']
        selection=zd.info['loc_cfg_ap_txpower_11na_option']
    else:
        raise('wrong parameter radio:%s'%radio)
    if not zd.s.is_element_present(check_box):
        raise('ap not support %sG radio'%radio)
    elif 'Global'==power:
        zd.s.click_if_checked(check_box)
    else:
        zd.s.click_if_not_checked(check_box)
        zd.s.select_option(selection,power)
    zd.s.click_and_wait(zd.info['loc_cfg_ap_ok_button'])
    

def set_ap_channel(zd,ap_mac,radio,channel):
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd,ap_mac)
    if radio=='2.4':
        check_box=zd.info['loc_cfg_ap_channel_11ng_checkbox']
        selection=zd.info['loc_cfg_ap_channel_11ng_option']
    elif radio=='5':
        check_box=zd.info['loc_cfg_ap_channel_11na_checkbox']
        selection=zd.info['loc_cfg_ap_channel_11na_option']
    else:
        raise('wrong parameter radio:%s'%radio)
    if not zd.s.is_element_present(check_box):
        raise('ap not support %sG radio'%radio)
    elif 'Global'==channel:
        zd.s.click_if_checked(check_box)
    else:
        zd.s.click_if_not_checked(check_box)
        zd.s.select_option(selection,channel)
        
    zd.s.click_and_wait(zd.info['loc_cfg_ap_ok_button'])

def get_ap_tx_power_options(zd, ap_mac_addr, pause = 1.0):
    '''
    '''
    warnings.warn('Not work under Udaipur 9.2', DeprecationWarning)

    xloc = LOCATORS_CFG_ACCESSPOINTS
    _nav_to(zd)
    logging.info("Get AP Device Information on Zone Director of AP [%s]" % (ap_mac_addr))
    edit_by_mac_addr = xloc['edit_by_mac_addr'] % (ap_mac_addr.lower())
    zd.s.click_and_wait(edit_by_mac_addr)
    if zd.s.is_visible(zd.info['loc_cfg_ap_txpower_11bg_option']):
        tx_power_options = zd.s.get_select_options(zd.info['loc_cfg_ap_txpower_11bg_option'])

    else:
        tx_power_options = zd.s.get_select_options(zd.info['loc_cfg_ap_txpower_11ng_option'])

    return tx_power_options


def get_ap_cfg_2(zd, ap_mac_addr, pause = 1):
    '''
    WARNING: ADAPTER, please use get_ap_config_by_mac function.
    '''
    ap_config = get_ap_config_by_mac(zd, ap_mac_addr)
    ap_config_info = {}

    general_info = ap_config['general_info']
    ap_config_info.update({
        'device_name': general_info['device_name'],
        'description': general_info['description'],
        'location': general_info['device_location'],
        'gps_coordinates': {'latitude': general_info['gps_latitude'],
                            'longitude': general_info['gps_longitude']},
        'ap_group': 'System Default', #not yet implemented in get_ap_config_by_mac
    })

    radio_config = ap_config['radio_config']
    for radio in radio_config.iterkeys():
        ap_config_info['radio_%s' % radio]= radio_config[radio]

    ap_config_info['network_setting'] = {}
    ip_config = ap_config['ip_config']
    ap_config_info['network_setting']['ip_mode'] = {
        'as_is': 'keep',
        'manual': 'static',
        'dhcp': 'dhcp',
    }[ip_config['ip_mode']]

    if ip_config['ip_mode'] == 'manual':
        ap_config_info['network_setting'].update(ip_config['ip_param'])

    mesh_config = ap_config['mesh_config']
    ap_config_info['mesh_mode'] = {
        'auto': 'auto',
        'root': 'root-ap',
        'mesh': 'mesh-ap',
        'disabled': 'disable',
    }[mesh_config['mesh_mode']]

    ap_config_info['mesh_uplink_aps'] = []
    if mesh_config['mesh_mode'] in ['auto', 'mesh']:
        ap_config_info['mesh_uplink_mode'] = mesh_config['mesh_param']['uplink_mode'].capitalize()
        ap_config_info['mesh_uplink_aps'] = mesh_config['mesh_param']['uplink_aps']

    if ap_config['port_config'].has_key('override_parent'):
        ap_config_info['port_override'] = ap_config['port_config']['override_parent']

    return ap_config_info


def get_ap_cfg_list(zd, mac_addr_list):
    ap_cfg_list = []
    for mac_addr in mac_addr_list:
        ap_cfg = get_ap_cfg_2(zd, mac_addr)
        if ap_cfg:
            ap_cfg['mac_addr'] = mac_addr
            ap_cfg_list.append(ap_cfg)

    return ap_cfg_list


def get_all_ap_cfg(zd):
    all_ap_cfg = {}
    for mac_addr in aps.get_all_ap_briefs(zd).iterkeys():
        ap_cfg = get_ap_cfg_2(zd, mac_addr)
        all_ap_cfg.update({mac_addr: ap_cfg})

    return all_ap_cfg


def get_radio_cfg_options(zd, ap_mac_addr, pause = 1.0):
    '''
        {'radio_bg': {'channel': [],
                      'channelization': [],
                      'power': [],
                      },
         'radio_na': ...,
         ...
        }
    '''
    xloc = LOCATORS_CFG_ACCESSPOINTS
    logging.info("Get the supported radio cfg options from Zone Director of AP [%s]" % (ap_mac_addr))

    supported_radios = _get_ap_supported_radios(zd, ap_mac_addr)

    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, ap_mac_addr)

    support_radio_cfg = {}
    for radio in supported_radios:
        edit_channel = xloc['edit_channel'] % radio
        if zd.s.is_visible(edit_channel):
            radio_key = 'radio_%s' % radio
            support_radio_cfg[radio_key] = {}
            support_radio_cfg[radio_key]['channel'] = zd.s.get_select_options(edit_channel)
            support_radio_cfg[radio_key]['power'] = zd.s.get_select_options(xloc['edit_power'] % radio)
            #channelization is not for bg radio mode
            if radio not in ['bg']:
                support_radio_cfg[radio_key]['channelization'] = zd.s.get_select_options(xloc['edit_channelization'] % radio)

    logging.info('AP [%s] support radio cfg: %s' % (ap_mac_addr, support_radio_cfg))

    _cancel_and_close_ap_dialog(zd)
    zd.re_navigate()

    return support_radio_cfg


###
## Access Points Monitor
###
def get_ap_info_by_mac(zd, ap_mac, pause = 1):
    '''
    WARNING: OBSOLETE, please use lib.zd.aps.get_ap_brief_by_mac_addr function
    '''
    return widgets_zd.map_row(
        aps._get_ap_brief_by(zd, dict(mac = ap_mac)),
        AP_INFO_HDR_MAP
    )


def get_all_ap_info(zd, pause = 1):
    '''
    WARNING: OBSOLETE, please use lib.zd.aps.get_all_ap_briefs function
    '''
    return list_to_dict(
        widgets_zd.map_rows(aps._get_all_ap_briefs(zd), AP_INFO_HDR_MAP),
        'mac_address'
    )


def _cfg_ap_wlan_service(zd,radio='both',enable=True):
    '''
    radio='both,'2.4','5.0'
    '''
    loc=LOCATORS_CFG_ACCESSPOINTS
    check_box_2_4=loc['enable_2_4G_wlan_service_check_box']
    check_box_5_0=loc['enable_5_0G_wlan_service_check_box']
    if radio in ['both','2.4']:
        if zd.s.is_element_present(check_box_2_4):
            if enable:
                zd.s.click_if_not_checked(check_box_2_4)
            else:
                zd.s.click_if_checked(check_box_2_4)
    if radio in ['both','5.0']:
        if zd.s.is_element_present(check_box_5_0):
            if enable:
                zd.s.click_if_not_checked(check_box_5_0)
            else:
                zd.s.click_if_checked(check_box_5_0)

def set_ap_wlan_service_by_mac(zd, mac_addr,radio='both',enable=True):
    '''
    radio='both,'2.4','5.0'
    '''
    _nav_to(zd)
    _open_ap_dialog_by_mac(zd, mac_addr)
    _cfg_ap_wlan_service(zd,radio,enable)
    _save_and_close_ap_dialog(zd)
    zd.re_navigate()

def reboot_ap(zd, ap_mac, pause = 2):
    '''
    WARNING: OBSOLETE, please use lib.zd.aps.reboot_ap_by_mac_addr function
    '''
    return aps.reboot_ap_by_mac_addr(zd, ap_mac)

def set_auto_recovery(zd, enable=True, recovery_time=30):
    '''
    '''
    xloc=LOCATORS_CFG_ACCESSPOINTS
    check_box=xloc['auto_recovery_check_box']

    _nav_to(zd)
    time.sleep(2)
    if enable:
        zd.s.click_if_not_checked(check_box)
        zd.s.type_text(xloc['auto_recovery_value'], recovery_time)
    else:
        zd.s.click_if_checked(check_box)

    zd.s.click_and_wait(xloc['edit_zd_ip_apply'])
    zd.re_navigate()

def set_ap_mgmt_vlan_in_ap_policy(zd,vlan_id = 'keep', is_nav = True):
    if is_nav:
        _nav_to(zd)
        time.sleep(2)
    loc = LOCATORS_CFG_ACCESSPOINTS
    keep =  loc['mgmt_vlan_keep_ap_setting']
    not_keep =  loc['mgmt_vlan_not_keep_ap_setting']
    value =  loc['mgmt_vlan_id_value']
    apply = loc['edit_zd_ip_apply']
    confirm = loc['confirm_ap_mgmt_vlan_checkbox']
    if vlan_id == 'keep':
        zd.s.click_and_wait(keep, 1)
    else:
        zd.s.click_and_wait(not_keep, 1)
        zd.s.type_text(value,vlan_id)
        
    zd.s.click_and_wait(apply)
    
    if zd.s.is_element_present(confirm):
        zd.s.click_if_not_checked(confirm)
    
    if zd.s.is_element_present(loc['confirm_prim_sec_zd_OK_button']):
        zd.s.click_and_wait(loc['confirm_prim_sec_zd_OK_button'])

def get_ap_mgmt_vlan_in_ap_policy(zd, is_nav = True):
    if is_nav:
        _nav_to(zd)
        time.sleep(2)
    loc = LOCATORS_CFG_ACCESSPOINTS
    not_keep =  loc['mgmt_vlan_not_keep_ap_setting']
    value =  loc['mgmt_vlan_id_value']
    if zd.s.is_checked(not_keep):
        vlan = str(zd.s.get_value(value))
        return vlan
    return "1"
        

