'''
Created on 2011-2-1
@author: serena.tan@ruckuswireless.com
'''


import logging
from string import Template
from pprint import pformat
import copy
import time
import os
#@author: liangaihua,@since: 2015-1-19,@change: add re to use when configure power
import re

from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zdcli import ap_info_cli

CONFIG_AP_CMD_BLOCK = '''
ap '$mac_addr'
'''
SET_AP_DEVICE_NAME = "devname '$device_name'\n"
SET_AP_DESCRIPTION = "description '$description'\n"
SET_AP_LOCATION = "location '$location'\n"
#SET_AP_PORT_OVERRIDE_ENABLE = "port-setting\n",
SET_AP_PORT_OVERRIDE_ENABLE = "port-setting\n"
#SET_AP_PORT_OVERRIDE_ENABLE = "override\n"
#SET_AP_PORT_OVERRIDE_DISABLE = "no override\n"
SET_AP_PORT_OVERRIDE_DISABLE = "no port-setting\n"
SET_AP_GPS = "gps $latitude,$longitude\n"
#Set IPV4 settings command.
SET_AP_IP_ENABLE = 'ip enable\n'
SET_AP_IP_DISABLE = 'no ip\n'
SET_AP_GROUP_DEFAULT = "group System-Default\n"
SET_AP_GROUP = "group name $group\n"
SET_AP_IP_MODE = "ip mode $ip_mode\n"
SET_AP_IP_ADDR = "ip addr '$ip_addr' '$net_mask'\n"
SET_AP_GATEWAY = "ip addr '$ip_addr' '$net_mask' gateway '$gateway'\n"
SET_AP_PRI_DNS = "ip name-server '$pri_dns'\n"
SET_AP_DNS = "ip name-server '$pri_dns' '$sec_dns'\n"
#Set IPV4 settings command.
SET_AP_IPV6_ENABLE = 'ipv6 enable\n'
SET_AP_IPV6_DISABLE = 'no ipv6\n'
SET_AP_IPV6_MODE = "ipv6 mode $ip_mode\n"
SET_AP_IPV6_ADDR = "ipv6 addr '$ip_addr' '$prefix_len'\n"
SET_AP_IPV6_GATEWAY = "ipv6 addr '$ip_addr' '$prefix_len' gateway '$gateway'\n"
SET_AP_IPV6_PRI_DNS = "ipv6 name-server '$pri_dns'\n"
SET_AP_IPV6_DNS = "ipv6 name-server '$pri_dns' '$sec_dns'\n"

SET_AP_RADIO_CHANNELIZATION_AUTO = "radio $radio channelization auto\n"
SET_AP_RADIO_CHANNELIZATION_NUM = "radio $radio channelization number $channelization\n"
DEFAULT_AP_RADIO_CHANNELIZATION = "no radio $radio channelization-override\n"
SET_AP_RADIO_CHANNEL_AUTO = "radio $radio channel auto\n"
SET_AP_RADIO_CHANNEL_NUM = "radio $radio channel number $channel\n"
DEFAULT_AP_RADIO_CHANNEL = "radio $radio channel-override\n"
SET_AP_RADIO_CHANNEL_RANGE = "radio $radio channel-range $range\n"
DEFAULT_AP_RADIO_CHANNEL_RANGE = "no radio $radio channel-range-override\n"
SET_AP_RADIO_TX_POWER = "radio $radio tx-power $power\n"
SET_AP_RADIO_WLANGROUP = "radio $radio wlan-group $wlangroups\n"
SET_AP_RADIO_AC = "radio $radio admission-control $ac\n"
SET_AP_RADIO_WLAN_SERVICE = "radio $radio wlan-service\n"
DISABLE_AP_RADIO_WLAN_SERVICE = "no radio $radio wlan-service\n"



SET_AP_MESH_MODE = "mesh mode $mesh_mode\n"
SET_AP_UPLINK_AUTO = "mesh uplink-selection auto\n"
SET_AP_UPLINK_MAC = "mesh uplink-selection manual add-mac $add_uplink_mac\n"
SET_AP_UPLINK_MAC_DEL = "mesh uplink-selection manual del-mac $del_uplink_mac\n"


#PORT-SETTING
CONFIG_AP_LAN_PORT = "port-setting\n"
ENABLE_LAN_PORT = "lan '$pid'\n"
DISABLE_LAN_PORT = "no lan '$pid'\n"
ENABLE_LAN_PORT_OPTION82 = "lan '$pid' opt82 enabled\n"
DISABLE_LAN_PORT_OPTION82 = "lan '$pid' opt82 disabled\n"
SET_LAN_PORT_TYPE = "lan '$pid' uplink '$type'\n" #type in ['trunk', 'access', 'general']
SET_LAN_PORT_UNTAG_ID = "lan '$pid' untag '$untagged_vlan'\n"
SET_LAN_PORT_MEMBER = "lan '$pid' member '$vlan_members'\n"
SET_LAN_PORT_DOT1X_TYPE = "lan '$pid' dot1x '$dot1x'\n"

ENABLE_DOT1X_DVLAN = "lan '$pid' dvlan enable\n"
DISABLE_DOT1X_DVLAN = "lan '$pid' dvlan disable\n"
SET_DOT1X_GUEST_VLAN = "lan '$pid' guest-vlan '$guest_vlan'"

SET_DOT1X_AUTH_SVR = "dot1x authsvr '$dot1x_auth_svr'\n"
SET_DOT1X_AUTH_ACCT = "dot1x acctsvr '$dot1x_acct_svr'\n"

ENABLE_DOT1X_MAC_BYPASS = "dot1x mac-auth-bypass\n"
DISABLE_DOT1X_MAC_BYPASS = "no dot1x mac-auth-bypass\n"
DISABLE_DOT1X_AUTH_SVR = "no dot1x authsvr\n"
DISABLE_DOT1X_ACCT_SVR = "no dot1x acctsvr\n"

SET_SUPPLICANT_USERNAME = "dot1x supplicant username '$dot1x_supp_username'\n"
SET_SUPPLICANT_PASSWORD = "dot1x supplicant password '$dot1x_supp_password'\n"
ENABLE_SUPPLICANT_MAC = "dot1x supplicant mac\n"
SAVE_PORT_SETTING = "exit\n"

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
SET_LLDP_USE_GROUP_SETTINGS = "no lldp\n"
SET_LLDP_STATE_ENABLE = "lldp enable\n"
SET_LLDP_STATE_DISABLE = "lldp disable\n"
SET_LLDP_STATE_OTHER = "lldp %s\n"
SET_LLDP_INTERVAL = "lldp interval %s\n" #interval between 1 and 300, default is 30.
SET_LLDP_HOLDTIME = "lldp holdtime %s\n" #holdtime between 60 and 1200, default is 120.
SET_LLDP_PORT_ENABLE = "lldp ifname eth %s enable\n"
SET_LLDP_PORT_DISABLE = "lldp ifname eth %s disable\n"
SET_LLDP_MGMT_ENABLE = "lldp mgmt enable\n"
SET_LLDP_MGMT_DISABLE = "lldp mgmt disable\n"
SET_LLDP_MGMT_OTHER = "lldp mgmt %s\n"
SAVE_PORT_OVERRIDE = "end\n"
SAVE_AP_CONFIG = "exit\n"

MAC_NOT_FOUND_MSG = "The MAC address '$mac_addr' is invalid. Please check the MAC address, and then try again."

RADIO_LIST = ['bg', 'ng', 'na', 'a']
MESH_UPLINK_MODE = ['Smart', 'Manual']


#Key Constant
KEY_CONST=dict(
        mac = 'MAC Address',
        model = 'Model',
)
AP_BASIC_KEY_MAP = {
    'device_name': 'Device Name', 
    'description': 'Description', 
    'location': 'Location', 
    }

AP_NETWORK_KEY_MAP = {
    'ip_mode': 'Device IP Settings',
    'ip_addr': 'IP Address',
    'net_mask': 'Netmask',
    'gateway': 'Gateway',
    'Primary DNS Server': '',
    'Secondary DNS Server': '',
    }

AP_RADIO_KEY_MAP = {
    'channelization': 'Channelization',
    'channel': 'Channel',
    'power': 'Tx. Power',
    'wlangroups': 'WLAN Group Name',
    'wlan_service': 'WLAN Services enabled'
    }

AP_IP_MODE_VALUE_MAP = {
    'dhcp': 'DHCP',
    'static': 'Manual',
    'keep': "Keep AP's Setting",
    }

AP_MESH_MODE_VALUE_MAP = {
    'disable': 'Manual',
    'auto': 'Auto',
    'root-ap': 'Root AP',
    'mesh-ap': 'Mesh AP'
}


#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 


def get_wlan_groups_default_radio_values(radio_mode):
    '''
    '''
    bg_default = dict(channel = 'Auto', wlangroups = 'Default',
                      power = 'Full')
    na_default = dict(channelization = 'Auto', channel = 'Auto',
                      power = 'Full', wlangroups = 'Default')
    ng_default = dict(channelization = 'Auto', channel = 'Auto',
                      power = 'Full', wlangroups = 'Default')

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


def default_wlan_groups_by_mac_addr(zdcli, mac_addr_list):
    '''
    '''
    if type(mac_addr_list) is not list:
        mac_addr_list = [mac_addr_list]
    
    aps = get_aps(zdcli, mac_addr_list)
    
    for mac_addr in mac_addr_list:
        for ap in aps:
            if ap[KEY_CONST['mac']] == mac_addr:
                ap_model = ap[KEY_CONST['model']]
                radio_mode = const.get_radio_mode_by_ap_model(ap_model)
                
                for rm in radio_mode:
                    default_params = get_wlan_groups_default_radio_values(rm)
                    ap_cfg = {'mac_addr':mac_addr,
                              'radio_%s' % rm:default_params}
                    
                    configure_ap(zdcli, ap_cfg)
                    

def default_ap_group_by_mac_addr(zdcli, mac_addr_list):
    if type(mac_addr_list) is not list:
        mac_addr_list = [mac_addr_list]
    
    ap_cfgs = []
    for mac_addr in mac_addr_list:
        ap_cfg = {'mac_addr':mac_addr,
                  'group':'System Default',
                  'wlangroups':'Default',
                  'description':'',
                  }
        ap_cfgs.append(ap_cfg)
    
    configure_aps(zdcli, ap_cfgs)
    
#@author: liang aihua,@change: add a new function to covert tx power,@since: 2015-1-29
#****************************
def _convert_tx_power(value):
    value_mapping = {'1/2':'-3dB',
                     '1/4':'-6dB',
                     '1/8': '-9dB',
                     '0': '0dB',
                     '1': '-1dB',
                     '2': '-2dB',
                     '3': '-3dB',
                     '4': '-4dB',
                     '5': '-5dB',
                     '6': '-6dB',
                     '7': '-7dB',
                     '8': '-8dB',
                     '9': '-9dB',
                     '10': '-10dB',
                     'Auto':'25dB',
                     'Full':'0dB',
                     'Min':'-24dB'} 
    
    if value in value_mapping.keys():
        value = value_mapping[value]
        
    return value
#*********************************************************
    
    
def configure_aps(zdcli, ap_cfg_list):
    '''
    Input:
        ap_cfg_list: a list of AP configuration.
    ''' 
    fail_ap = {}
    pass_ap = {}
    for ap_cfg in ap_cfg_list:
        res, msg = configure_ap(zdcli, ap_cfg)
        if res:
            pass_ap.update({ap_cfg['mac_addr']: msg})
        
        else:
            fail_ap.update({ap_cfg['mac_addr']: msg})
        
    if fail_ap:
        return (False, '%s' % fail_ap)
    
    else:
        return (True, '%s' % pass_ap)


def configure_ap(zdcli, ap_cfg):
    '''
    Input:
        ap_cfg: a dictionary of the AP configuration.
        {'mac_addr': 'ac:67:06:33:76:b0', 
         'device_name': 'Ruckus AP', 
         'description': 'Ruckus AP for test', 
         'location': 'sdc', 
         'port_override': True, 
         'mesh_mode': 'auto', 
         'mesh_uplink_mode': 'Smart', 
         'mesh_uplink_aps': [],
         'gps_coordinates': {'latitude': '37.3881398', 
                             'longitude': '-122.0258633',
                            },
         'network_setting': {'ip_mode': 'static',
                             'ip_addr': '192.168.0.100',
                             'net_mask': '255.255.255.0',
                             'gateway': '192.168.0.253',
                             'pri_dns': '192.168.0.252',
                             'sec_dns': '192.168.0.250',
                             
                             'ip_version': None,
                             'ipv6_mode': None,
                             'ipv6_addr': None,
                             'ipv6_prefix_len': None,
                             'ipv6_gateway': None,
                             'ipv6_pri_dns': None,
                             'ipv6_sec_dns': None,
                             
                            },
         'radio_ng': {'channel': 'Auto',
                      'channelization': 'Auto',
                      'power': 'Auto',
                      'wlangroups': 'Default'
                     },
          }
          
    Warning:
        ip_mode: 'dhcp'/'static'/'keep'
        mesh_mode: 'auto'/'root-ap'/'mesh-ap'/'disable'
        mesh_uplink_mode: 'Smart'/'Manual'
        port_override: True/False
        channel: 'Auto', '1', '2', ...,
        channelization: 'Auto', '20', '40', ...,
        power: 'Auto', 'Full', 'Min', '1/2', '1/4', '1/8', ...,
    '''      
    conf = {'mac_addr': None, 
            'device_name': None, 
            'description': None, 
            'location': None, 
            'port_override': None, 
            'mesh_mode': None, 
            'mesh_uplink_mode': None, 
            'mesh_uplink_aps': None,
            'gps_coordinates': {'latitude': None, 
                                'longitude': None,
                                },
            'network_setting': {'ip_version': None,
                                'ip_mode': None,
                                'ip_addr': None,
                                'net_mask': None,
                                'gateway': None,
                                'pri_dns': None,
                                'sec_dns': None,
                                'ipv6_mode': None,
                                'ipv6_addr': None,
                                'ipv6_prefix_len': None,
                                'ipv6_gateway': None,
                                'ipv6_pri_dns': None,
                                'ipv6_sec_dns': None,
                                },
            'radio_bg': {},
            'radio_ng': {},
            'radio_na': {},
            'radio_a': {},
#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
            'lldp':{'use_group_settings':False,
                    'state':None,
                    'interval':None,
                    'holdtime':None,
                    'enable_ports':[],
                    'disable_ports':[],
                    'mgmt':None}
           }
    for k in conf:
        if ap_cfg.has_key(k):
            if type(conf[k]) == dict:
                conf[k].update(ap_cfg[k])
        
            else:
                conf[k] = ap_cfg[k]
    
    current_uplink_ap = []
    if conf['mesh_uplink_aps'] != None:
        current_uplink_ap = _get_ap_uplink_mac_list(zdcli, ap_cfg['mac_addr'])
        if current_uplink_ap == None:
            return (False, 'The AP [%s] does not exist in ZD CLI!' % ap_cfg['mac_addr'])
    
    logging.info('Configure AP [%s] in ZD CLI with cfg:\n%s' % (ap_cfg['mac_addr'], pformat(ap_cfg, 4, 120)))
    value = _set_ap(zdcli, conf, current_uplink_ap)
    if not value:
        logging.info('Fail to configure AP [%s] in ZD CLI!' % ap_cfg['mac_addr'])
        return (False, 'Fail to configure AP [%s] in ZD CLI!' % ap_cfg['mac_addr'])

    res, msg = _verify_ap_cfg_in_cli(zdcli, ap_cfg)
    
    time.sleep(2)
    if ap_cfg.get('network_setting') or ap_cfg.get('mesh_mode'):
        pause = 100
        logging.info('Wait %s seconds for AP to reboot' % pause)
        time.sleep(pause)
    
    if res:
        logging.info('Configure AP [%s] in ZD CLI successfully!' % ap_cfg['mac_addr'])
        return (True, 'Configure AP [%s] in ZD CLI successfully!' % ap_cfg['mac_addr'])
    
    else:
        logging.info('Fail to configure AP [%s] in ZD CLI [%s]' % (ap_cfg['mac_addr'], msg))
        return (False, 'Fail to configure AP [%s] in ZD CLI [%s]' % (ap_cfg['mac_addr'], msg))
    

def set_ap_port_config_by_mac(
        zdcli, mac_addr, port_config
    ):    
    cmd_block = Template(CONFIG_AP_CMD_BLOCK).substitute(dict(mac_addr = mac_addr))
    cmd_block += _set_ap_port_config(zdcli, port_config)
    cmd_block += SAVE_AP_CONFIG
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][1]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return (False, res)
    
    return (True, "")
        
def verify_cli_cfg_in_gui(cli_cfg_list, gui_info_list):
    cli_len = len(cli_cfg_list)
    gui_len = len(gui_info_list)

    if cli_len != gui_len:
        return (False, 'The number of APs in get from ZD CLI [%s] is not the same as in ZD GUI [%s]!' % (cli_len, gui_len))
    
    for i in range(cli_len):
        for j in range(gui_len):
            if cli_cfg_list[i]['mac_addr'] == gui_info_list[j]['mac_addr']:
                res, msg = verify_ap_cli_cfg_in_gui(cli_cfg_list[i], gui_info_list[j])
                if res:
                    break
                else:
                    return (False, msg)
                
            elif j == gui_len - 1:
                return (False, 'The AP [%s] exists in ZD CLI, but not in ZD GUI!' % gui_info_list[i]['mac_addr'])
            
    return (True, "The information of APs shown in ZD GUI is the same as in ZD CLI!")


def verify_ap_cli_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    cli_cfg_dict.pop('mac_addr')
    return _expect_is_in_dict(cli_cfg_dict, gui_info_dict)

    
def get_aps(zdcli, mac_addr_list):
    ap_info_list = []
    for mac_addr in mac_addr_list:
        ap_info = _get_ap_info_by_mac(zdcli, mac_addr)
        if ap_info == None:
            logging.info('AP [%s] does not exist!' % mac_addr)
        
        else:
            ap_info_list.append(ap_info)
    
    return ap_info_list


def get_ap(zdcli, mac_addr):
    return get_aps(zdcli, [mac_addr])[0]

       
#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 

def _get_ap_uplink_mac_list(zdcli, mac_addr):
    '''
    Output:
        None: AP does not exist.
        A list of the uplink AP mac address.
    '''
    ap_info = _get_ap_info_by_mac(zdcli, mac_addr)
    if ap_info == None:
        return None
    
    else:
        if ap_info.has_key('Uplink') and ap_info['Uplink'].has_key('MAC Address'):
            uplink_mac = ap_info['Uplink']['MAC Address']
            if type(uplink_mac) is list:
                return uplink_mac
            
            else:
                return [uplink_mac]
        
        else:
            return []
            
    
def _get_ap_info_by_mac(zdcli, mac_addr):
    '''
    Output:
        None: AP does not exist.
        A dict of the AP configuration
    '''
    info = ap_info_cli.show_ap_info_by_mac(zdcli, mac_addr)
    if info.has_key('AP'):
        ap_info = info['AP']['ID'].values()[0]
        return ap_info
    
    else:
        return None

def _get_ap_supported_radios(zdcli, mac_addr):
    '''
    '''
    ap_model = _get_ap_info_by_mac(zdcli, mac_addr)['Model']

    return const.get_radio_mode_by_ap_model(ap_model)

    
def _set_ap(zdcli, cfg, current_uplink_ap):  
    cmd_block = _construct_set_ap_cmd_block(cfg, current_uplink_ap)
    logging.info('Configure AP with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True

def _set_ap_port_config(zdcli, port_config):
    cmd_block = ""
    for port, settings in port_config.iteritems():
            if not settings or type(settings) is not dict:
                continue

            # now the lan port and its config are provided
            cmd_block += _set_ap_port_config_detail(zdcli, port, settings)
    
    return cmd_block

def _set_ap_port_config_detail(zdcli, port, settings):
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
    
    pid = port[-1]
    cmd_block = CONFIG_AP_LAN_PORT    
    if settings['enabled']:
        cmd_block += Template(ENABLE_LAN_PORT).substitute(dict(pid = pid))
        if settings.has_key("type") and settings["type"]:
            cmd_block += Template(SET_LAN_PORT_TYPE).substitute(dict(pid = pid, type = settings['type']))
            cmd_block += DISABLE_DOT1X_MAC_BYPASS
            cmd_block += DISABLE_DOT1X_ACCT_SVR
            cmd_block += DISABLE_DOT1X_AUTH_SVR

            if settings["type"] in ["access", "general"]:            
                if settings.has_key("untagged_vlan") and settings["untagged_vlan"]:
                    cmd_block += Template(SET_LAN_PORT_UNTAG_ID).substitute(dict(pid = pid, untagged_vlan = settings["untagged_vlan"]))
                    
            if settings["type"] in ["general"]:
                if settings.has_key("vlan_members") and settings["vlan_members"]:
                    cmd_block += Template(SET_LAN_PORT_MEMBER).substitute(dict(pid = pid, vlan_members = settings["vlan_members"]))
                
        if settings.has_key("dot1x") and settings["dot1x"]:
            cmd_block += Template(SET_LAN_PORT_DOT1X_TYPE).substitute(dict(pid = pid, dot1x = settings["dot1x"]))
            
            if settings["dot1x"] in ["auth-port", "auth-mac"]:
                if settings.has_key("type") and settings['type'] == 'access':
                    if settings['dot1x'] == "auth-mac" and settings.has_key("enable_dvlan"):
                        dvlan_enabled = settings['enable_dvlan']
                        if dvlan_enabled:
                            cmd_block += Template(ENABLE_DOT1X_DVLAN).substitute(dict(pid = pid))
                        else:
                            cmd_block += Template(DISABLE_DOT1X_DVLAN).substitute(dict(pid = pid))
                        
                        if settings.has_key("guest_vlan"):
                            guest_vlan = settings['guest_vlan']
                            cmd_block += Template(SET_DOT1X_GUEST_VLAN).substitute(dict(pid = pid, 
                                                                                        guest_vlan = guest_vlan))
                        
                if settings.has_key("dot1x_auth_svr") and settings["dot1x_auth_svr"]:
                    cmd_block += Template(SET_DOT1X_AUTH_SVR).substitute(dict(dot1x_auth_svr = settings["dot1x_auth_svr"]))            
                if settings.has_key("dot1x_acct_svr") and settings["dot1x_acct_svr"]:
                    cmd_block += Template(SET_DOT1X_AUTH_ACCT).substitute(dict(dot1x_acct_svr = settings["dot1x_acct_svr"]))
                if settings.has_key("dot1x_mac_bypass_enabled"):
                    if settings["dot1x_mac_bypass_enabled"]:                    
                        cmd_block += Template(ENABLE_DOT1X_MAC_BYPASS).substitute(
                                                                    dict(dot1x_mac_bypass_enabled = settings["dot1x_mac_bypass_enabled"]))
                    else:
                        cmd_block += DISABLE_DOT1X_MAC_BYPASS                
                    
            elif settings["dot1x"] in ["supp"]:                
                if settings.get("dot1x_supp_auth_enabled"):
                    cmd_block += Template(SET_SUPPLICANT_USERNAME).substitute(dict(dot1x_supp_username = settings["dot1x_supp_username"]))
                    cmd_block += Template(SET_SUPPLICANT_PASSWORD).substitute(dict(dot1x_supp_password = settings["dot1x_supp_password"]))                
                elif settings.get("dot1x_supp_mac_enabled"):
                    cmd_block += ENABLE_SUPPLICANT_MAC               
                             
            
            
    else:
        cmd_block += Template(DISABLE_LAN_PORT).substitute(dict(pid = pid))
        cmd_block += DISABLE_DOT1X_MAC_BYPASS
        cmd_block += DISABLE_DOT1X_ACCT_SVR
        cmd_block += DISABLE_DOT1X_AUTH_SVR
    
    cmd_block = cmd_block + SAVE_PORT_SETTING#
    
    return cmd_block


def _construct_set_ap_cmd_block(cfg, current_uplink_ap = []):    
    cmd_block = Template(CONFIG_AP_CMD_BLOCK).substitute(dict(mac_addr = cfg['mac_addr']))
    if cfg['description'] != None:
        cmd_block += Template(SET_AP_DESCRIPTION).substitute(dict(description = cfg['description']))
    
    if cfg['device_name'] != None:
        cmd_block += Template(SET_AP_DEVICE_NAME).substitute(dict(device_name = cfg['device_name']))

    if cfg['location'] != None:
        cmd_block += Template(SET_AP_LOCATION).substitute(dict(location = cfg['location']))
    
    if cfg['port_override'] == True:
        cmd_block += SET_AP_PORT_OVERRIDE_ENABLE
        cmd_block += SAVE_PORT_OVERRIDE
        
    elif cfg['port_override'] == False:
        cmd_block += SET_AP_PORT_OVERRIDE_DISABLE
    
    if cfg['mesh_mode']:
        cmd_block += Template(SET_AP_MESH_MODE).substitute(dict(mesh_mode = cfg['mesh_mode']))
    
    if cfg['mesh_uplink_mode'] == 'Smart':
        cmd_block += SET_AP_UPLINK_AUTO
    
    elif cfg['mesh_uplink_aps'] != None:
        for del_mac in current_uplink_ap:
            cmd_block += Template(SET_AP_UPLINK_MAC_DEL).substitute(dict(del_uplink_mac = del_mac))
        
        for add_mac in cfg['mesh_uplink_aps']:
            cmd_block += Template(SET_AP_UPLINK_MAC).substitute(dict(add_uplink_mac = add_mac))
    
    latitude = cfg['gps_coordinates']['latitude']
    longitude = cfg['gps_coordinates']['longitude']
    if latitude != None and longitude != None:
        cmd_block += Template(SET_AP_GPS).substitute(dict(latitude = latitude, longitude = longitude))
    
    try:
        apgroup = cfg.pop('group')
    except:
        apgroup=None
    
    if apgroup:
        if apgroup=="System Default":
            cmd_block += Template(SET_AP_GROUP_DEFAULT).substitute(dict())
        else:
            cmd_block += Template(SET_AP_GROUP).substitute(dict(group = apgroup))

    cmd_block += _construct_set_ap_cmd_block_ip(cfg)    
    for radio in RADIO_LIST:
        radio_digit = '2.4' if 'g' in radio else '5'
        radio_key = 'radio_%s' % radio
        if cfg[radio_key]:
            radio_cfg = cfg[radio_key]
            channelization = radio_cfg.get('channelization')
            channel = radio_cfg.get('channel')
            power = radio_cfg.get('power')
            wlangroup = radio_cfg.get('wlangroups', 'Default')            
            channel_range = radio_cfg.get('channel_range', None)
            wlan_service = radio_cfg.get('wlan_service', None)
            ac = radio_cfg.get('ac')
            if channelization == 'Auto':
                cmd_block += Template(SET_AP_RADIO_CHANNELIZATION_AUTO).substitute(dict(radio = radio_digit))
            elif channelization == "Default":
                cmd_block += Template(DEFAULT_AP_RADIO_CHANNELIZATION).safe_substitute(dict(radio = radio_digit))
            elif channelization:
                cmd_block += Template(SET_AP_RADIO_CHANNELIZATION_NUM).substitute(dict(radio = radio_digit, 
                                                                                       channelization = channelization))
            if channel_range:
                if channel_range == "Default":
                    cmd_block += Template(DEFAULT_AP_RADIO_CHANNEL_RANGE).substitute(dict(radio = radio_digit))
                else:    
                    cmd_block += Template(SET_AP_RADIO_CHANNEL_RANGE).substitute(dict(radio = radio_digit,
                                                                                  range = channel_range
                                                                                  ))
            if channel == 'Auto':
                cmd_block += Template(SET_AP_RADIO_CHANNEL_AUTO).substitute(dict(radio = radio_digit))
            
            elif channel:
                if channel == "Default":
                    cmd_block += Template(DEFAULT_SET_AP_RADIO_CHANNEL).substitute(dict(radio = radio_digit))
                else:
                    cmd_block += Template(SET_AP_RADIO_CHANNEL_NUM).substitute(dict(radio = radio_digit, channel = channel))            
            #@author: liang aihua,@since: 2015-1-29,@change: convert set tx power to cli configurable.
            #**************************        
            if power:
                convert_power = _convert_tx_power(power)
                m = re.search("-?(\d+)", convert_power)
                if m:
                    power = m.group(1)
                cmd_block += Template(SET_AP_RADIO_TX_POWER).substitute(dict(radio = radio_digit, power = power))
            #***************************************************
            
            if wlangroup:
                cmd_block += Template(SET_AP_RADIO_WLANGROUP).substitute(dict(radio = radio_digit, wlangroups = wlangroup))
            
            if ac:
                cmd_block += Template(SET_AP_RADIO_AC).substitute(dict(radio = radio_digit, ac = ac))
            
            if wlan_service == 'Yes':
                cmd_block += Template(SET_AP_RADIO_WLAN_SERVICE).substitute(dict(radio=radio_digit))
            elif wlan_service == 'No':
                cmd_block += Template(DISABLE_AP_RADIO_WLAN_SERVICE).substitute(dict(radio=radio_digit))

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
    if cfg['lldp']['use_group_settings']:
        cmd_block += SET_LLDP_USE_GROUP_SETTINGS
    if cfg['lldp'].get('state') == 'enable':
        cmd_block += SET_LLDP_STATE_ENABLE
    elif cfg['lldp'].get('state') == 'disable':
        cmd_block += SET_LLDP_STATE_DISABLE
    elif cfg['lldp'].get('state'):
        cmd_block += SET_LLDP_STATE_OTHER%cfg['lldp']['state']
    if cfg['lldp']['interval']:
        cmd_block += SET_LLDP_INTERVAL%cfg['lldp']['interval']
    if cfg['lldp']['holdtime']:
        cmd_block += SET_LLDP_HOLDTIME%cfg['lldp']['holdtime']
    if cfg['lldp'].get('mgmt') == 'enable':
        cmd_block += SET_LLDP_MGMT_ENABLE
    elif cfg['lldp'].get('mgmt') == 'disable':
        cmd_block += SET_LLDP_MGMT_DISABLE
    elif cfg['lldp'].get('mgmt'):
        cmd_block += SET_LLDP_MGMT_DISABLE%cfg['lldp']['mgmt']
    if cfg['lldp']['enable_ports']:
        for port in cfg['lldp']['enable_ports']:
            cmd_block += SET_LLDP_PORT_ENABLE%port
    if cfg['lldp']['disable_ports']:
        for port in cfg['lldp']['disable_ports']:
            cmd_block += SET_LLDP_PORT_DISABLE%port
    
            
    cmd_block = cmd_block + SAVE_AP_CONFIG
    
    return cmd_block

def _construct_set_ap_cmd_block_ip(cfg):
    '''
    Construct set command block for ip configuration.
    Include ip version, ipv4 and ipv6 setings.
    '''
    cmd_block_ap_ip = ''
    
    network_setting_cfg = cfg['network_setting']
    
    #IP version configuration command block.
    if network_setting_cfg['ip_version'] != None:
        ip_version = network_setting_cfg['ip_version'].lower()
        
        if ip_version == const.DUAL_STACK:
            cmd_block_ap_ip+= SET_AP_IP_ENABLE
            cmd_block_ap_ip+= SET_AP_IPV6_ENABLE
        elif ip_version == const.IPV4:
            cmd_block_ap_ip+= SET_AP_IP_ENABLE
            cmd_block_ap_ip+= SET_AP_IPV6_DISABLE
        elif ip_version == const.IPV6:
            cmd_block_ap_ip+= SET_AP_IPV6_ENABLE
            cmd_block_ap_ip+= SET_AP_IP_DISABLE
    else:
        #Default IP version is ipv4.
        ip_version = const.IPV4
    
    #ipv4 configuration command block.
    if ip_version in [const.IPV4, const.DUAL_STACK]:
        ip_mode = network_setting_cfg['ip_mode']
        ip_addr = network_setting_cfg['ip_addr']
        net_mask = network_setting_cfg['net_mask']
        gateway = network_setting_cfg['gateway']
        pri_dns = network_setting_cfg['pri_dns']
        sec_dns = network_setting_cfg['sec_dns']
        if ip_mode != None:
            cmd_block_ap_ip += Template(SET_AP_IP_MODE).substitute(dict(ip_mode = ip_mode))
            
        if ip_addr != None and net_mask != None and gateway != None:
            cmd_block_ap_ip += Template(SET_AP_GATEWAY).substitute(dict(ip_addr = ip_addr, net_mask = net_mask, gateway = gateway))
        
        elif ip_addr != None and net_mask != None:
            cmd_block_ap_ip += Template(SET_AP_IP_ADDR).substitute(dict(ip_addr = ip_addr, net_mask = net_mask))
        
        if pri_dns != None and sec_dns != None:
            cmd_block_ap_ip += Template(SET_AP_DNS).substitute(dict(pri_dns = pri_dns, sec_dns = sec_dns))    
        
        elif pri_dns != None:
            cmd_block_ap_ip += Template(SET_AP_PRI_DNS).substitute(dict(pri_dns = pri_dns))
    
    #ipv6 configuration command block.    
    if ip_version in [const.IPV6, const.DUAL_STACK]:
        ipv6_mode = network_setting_cfg['ipv6_mode']
        ipv6_addr = network_setting_cfg['ipv6_addr']
        ipv6_prefix_len = network_setting_cfg['ipv6_prefix_len']
        ipv6_gateway = network_setting_cfg['ipv6_gateway']
        ipv6_pri_dns = network_setting_cfg['ipv6_pri_dns']
        ipv6_sec_dns = network_setting_cfg['ipv6_sec_dns']
    
        if ipv6_mode != None:
            cmd_block_ap_ip += Template(SET_AP_IPV6_MODE).substitute(dict(ip_mode = ipv6_mode))
            
        if ipv6_addr != None and ipv6_prefix_len != None and ipv6_gateway != None:
            cmd_block_ap_ip += Template(SET_AP_IPV6_GATEWAY).substitute(dict(ip_addr = ipv6_addr, prefix_len = ipv6_prefix_len, gateway = ipv6_gateway))
        
        elif ipv6_addr != None and ipv6_prefix_len != None:
            cmd_block_ap_ip += Template(SET_AP_IPV6_ADDR).substitute(dict(ip_addr = ipv6_addr, prefix_len = ipv6_prefix_len))
        
        if ipv6_pri_dns != None and ipv6_sec_dns != None:
            cmd_block_ap_ip += Template(SET_AP_IPV6_DNS).substitute(dict(pri_dns = ipv6_pri_dns, sec_dns = ipv6_sec_dns))
        elif ipv6_pri_dns != None:
            cmd_block_ap_ip += Template(SET_AP_IPV6_PRI_DNS).substitute(dict(pri_dns = ipv6_pri_dns))
        
    return cmd_block_ap_ip

def _verify_ap_cfg_in_cli(zdcli, cfg):
    conf = copy.deepcopy(cfg)
    mac_addr = conf.pop('mac_addr')
    cli_info = _get_ap_info_by_mac(zdcli, mac_addr)
    if cli_info == None:
        return (False, 'AP [%s] does not exist.' % conf['mac_addr'])
    #ChenTao, 2014-10-19, fix bug of ZF-8873
    if not cli_info.has_key('Radio a/n'):
        if conf.get('radio_a'):
            if conf['radio_a'].get('wlan_service') == 'No':
                conf.pop('radio_a') 
        if conf.get('radio_na'):
            if conf['radio_na'].get('wlan_service') == 'No':
                conf.pop('radio_na')
    #ChenTao, 2014-10-19, fix bug of ZF-8873
    expect_info = _define_expect_ap_info_in_cli(conf)
    logging.info("The expect ap info in ZD CLI is: %s" % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, cli_info)
    
    
def _define_expect_ap_info_in_cli(conf):
    expect_info = _dict_map(conf, AP_BASIC_KEY_MAP)
    if conf.get('port_override') == True:
        expect_info['Override global ap-model port configuration'] = 'Yes'
    
    elif conf.get('port_override') == False:
        expect_info['Override global ap-model port configuration'] = 'No'
            
    if conf.has_key('network_setting'):
        network_setting = _dict_map(conf['network_setting'], AP_NETWORK_KEY_MAP)
        if network_setting.has_key('Device IP Settings'):
            ip_setting = network_setting['Device IP Settings']
            if ip_setting not in AP_IP_MODE_VALUE_MAP:
                raise Exception('Can not set ip mode: %s in ZD CLI' % ip_setting)
            
            network_setting['Device IP Settings'] = AP_IP_MODE_VALUE_MAP[ip_setting]
                
        expect_info['Network Setting'] = network_setting
    
    for radio in RADIO_LIST:
        radio_key = 'radio_%s' % radio           
        if conf.has_key(radio_key):
            #@author: liang aihua,@since: 2015-1-29,@change: convert set tx power same as cli
            #******************
            #if conf[radio_key].has_key('power'):
            #    if conf[radio_key]['power'] not in ['Auto', 'Full', 'Min']:
            #        conf[radio_key]['power']= _convert_tx_power(conf[radio_key]['power'])
            #**********************************
            
            radio_setting = _dict_map(conf[radio_key], AP_RADIO_KEY_MAP)
            if 'g' in radio:
                expect_info['Radio b/g/n'] = radio_setting
            
            else:
                expect_info['Radio a/n'] = radio_setting
    
    if conf.has_key('mesh_mode'):
        mesh_mode = conf['mesh_mode']
        if mesh_mode not in AP_MESH_MODE_VALUE_MAP:
            raise Exception('Can not set the mesh mode: %s in ZD CLI' % mesh_mode)
        
        expect_info['Mesh'] = {}
        #@author: Liang Aihua,@change: Mode has been removed, no need to check.
        #expect_info['Mesh']['Mode'] = AP_MESH_MODE_VALUE_MAP[mesh_mode]
        if mesh_mode == 'disable':
            expect_info['Mesh']['Status'] = 'Disabled'
        
        else:
            expect_info['Mesh']['Status'] = 'Enabled'
    
    expect_info['Uplink'] = {}
    if conf.has_key('mesh_uplink_mode'):
        uplink_mode = conf['mesh_uplink_mode']
        if uplink_mode not in MESH_UPLINK_MODE:
            raise Exception('Can not set the mesh uplink mode: %s in ZD CLI' % uplink_mode)
        
        expect_info['Uplink']['Status'] = uplink_mode
    
    if conf.has_key('mesh_uplink_aps'):
        uplink_mac_addr = conf['mesh_uplink_aps']
        if uplink_mac_addr:
            if len(uplink_mac_addr) > 1:
                expect_info['Uplink']['MAC Address'] = uplink_mac_addr
        
            else:
                expect_info['Uplink']['MAC Address'] = uplink_mac_addr[0]
    
    if not expect_info['Uplink']:
        expect_info.pop('Uplink')
            
    if conf.has_key('gps_coordinates'):
        latitude = None
        longitude = None
        if conf['gps_coordinates'].has_key('latitude'):
            latitude = conf['gps_coordinates']['latitude']
        
        if conf['gps_coordinates'].has_key('longitude'):
            longitude = conf['gps_coordinates']['longitude']
            
        if latitude and longitude:
            expect_info['GPS'] = '%s,%s' % (latitude, longitude)
        
        elif latitude == None and longitude == None:
            pass
        
        else:
            raise Exception('Can not set the gps coordinates: %s in ZD CLI' % conf['gps_coordinates'])

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
    if conf.has_key('lldp'):
        expect_info['LLDP'] = {}
        if conf['lldp'].get('use_group_settings') == True:
            expect_info['LLDP']['Status'] = 'Use Parent Setting'
        if conf['lldp'].get('state') == 'enable':
            expect_info['LLDP']['Status'] = 'Enabled'
        elif conf['lldp'].get('state') == 'disable':
            expect_info['LLDP']['Status'] = 'Disabled'
        elif conf['lldp'].get('state'):
            expect_info['LLDP']['Status'] = conf['lldp']['state']
        if conf['lldp'].get('interval'):
            expect_info['LLDP']['Interval'] = conf['lldp']['interval']
        if conf['lldp'].get('holdtime'):
            expect_info['LLDP']['HoldTime'] = conf['lldp']['holdtime']
        if conf['lldp'].get('mgmt') == 'enable':
            expect_info['LLDP']['Mgmt'] = 'Enabled'
        elif conf['lldp'].get('mgmt') == 'disable':
            expect_info['LLDP']['Mgmt'] = 'Disabled'
        elif conf['lldp'].get('mgmt'):
            expect_info['LLDP']['Mgmt'] = conf['lldp']['mgmt']
        if conf['lldp'].get('enable_ports') or conf['lldp'].get('disable_ports'):   
            expect_info['LLDP']['Ports'] = {} 
            if conf['lldp'].get('enable_ports'):
                for port in conf['lldp']['enable_ports']:
                    expect_info['LLDP']['Ports']['Send out LLDP packet on eth%s'%str(port)] = 'Enabled'
            if conf['lldp'].get('disable_ports'):
                for port in conf['lldp']['disable_ports']:
                    expect_info['LLDP']['Ports']['Send out LLDP packet on eth%s'%str(port)] = 'Disabled'
    return expect_info    


def _dict_map(original_dict, map_dict):
    target_dict = dict()
    for k in original_dict.keys():
        if k in map_dict.keys() and original_dict[k] != None:
            target_dict[map_dict[k]] = str(original_dict[k])
    
    return target_dict


def _expect_is_in_dict(expect_dict, original_dict):
    expect_ks = expect_dict.keys()
    orignal_ks = original_dict.keys()
    for k in expect_ks:
        if k not in orignal_ks:
            return (False, 'The parameter [%s] does not exist in dict: %s' % (k, original_dict))
        
        if type(expect_dict[k]) is dict:
            res, msg = _expect_is_in_dict(expect_dict[k], original_dict[k])
            if not res:
                return (False, msg)
            #@author: liangaihua,@since: 2015-1-29,@change: continue compare next key
            #***************
            else:
                continue
            #*************************
            
        #@author: liangaihua,@since: 2015-1-29,@change: convert tx.power or power.
        #********************
        if k == 'Tx. Power' or k == 'power':
            if expect_dict[k]!= original_dict[k]:
                m = re.search(expect_dict[k],original_dict[k])
                if not m:
                    return (False, 'The value [%s] of parameter [%s] is not correct in dict: %s ' % (expect_dict[k], k, original_dict))
        #***********************************
        elif original_dict[k] != expect_dict[k]:
            return (False, 'The value [%s] of parameter [%s] is not correct in dict: %s ' % (expect_dict[k], k, original_dict))         

    return (True, '')

def enter_ap_config_if(zdcli,ap_mac):
    zdcli.do_cmd('config') 
    zdcli.do_cmd('ap %s'%ap_mac)
    
def exit_ap_config_if(zdcli):
    zdcli.do_cmd('end') 
    zdcli.do_cmd('quit')

def set_ap_tx_power(zdcli,ap_mac,radio,power='Full'): 
    Num_list=['1','2','3','4','5','6','7','8','9','10']
    str_list=['auto','Auto','Full','full','Min','min','1/2','1/4','1/8']
    if power in Num_list or str(power) in Num_list:
 # @author: zj 2013-10-15 bugfix:ZF-5639 cli command behavior change      
 #       power='Num %s'%power
        power = '%s' %power
    elif power not in str_list:
        raise('wrong parameter for power:%s'%power)
    #@author: Jane.Guo @since: 2013-09-13 Use do_cfg instead of do_cmd, becase do_cfg will consider timeout and will enter/exit config mode automatically.
    cmd = 'ap %s\n'%ap_mac
    cmd += 'radio %s tx-power %s\n'%(radio,power)
    cmd += 'end\n'
    res = zdcli.do_cfg(cmd)

def del_aps_by_mac(zdcli,mac_addr_list):
    cmd = ''
    for mac_addr in mac_addr_list:
        cmd += 'no ap %s\n'%mac_addr
    zdcli.do_cfg(cmd)
    
