'''
This module define the l2 ACL

'''

import logging
import os

from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common.utils import compare_dict_key_value
from RuckusAutoTest.common import utils

SHOW_AP_ALL = 'show ap all'
SHOW_AP_DEVNAME = 'show ap devname $name'
SHOW_AP_MAC = 'show ap mac $mac'
SHOW_AP_PORT_SETTING = '''
ap '$mac'
port-setting
show
'''

def show_ap_all(zdcli):
    cmd_block = SHOW_AP_ALL
    logging.info("======show AP all==========")

    ap_all = zdcli.do_show(cmd_block)
    
    logging.info('The result\n:%s',ap_all)
    ap_info_on_cli = output.parse(ap_all)
    
    return ap_info_on_cli


def show_ap_info_by_name(zdcli,dev_name):
    cmd_block = Template(SHOW_AP_DEVNAME).substitute(dict(name = dev_name))
    if dev_name == '':
        cmd_block = """show ap devname ''"""
    logging.info( "=======show AP device name=========")

    l2acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The result\n%s:' % l2acl_result)
    ap_info_on_cli = output.parse(l2acl_result)
    
    return ap_info_on_cli


def show_ap_info_by_mac(zdcli,mac):
    cmd_block = Template(SHOW_AP_MAC).substitute(dict(mac = mac))
    
    logging.info( "=======show AP mac=========")

    l2acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The result\n%s:' % l2acl_result)
    ap_info = output.parse(l2acl_result)
    
    return ap_info


def show_ap_port_config_by_mac(zdcli, mac):
    cmd_block = Template(SHOW_AP_PORT_SETTING).substitute(dict(mac = mac))    
    res = zdcli.do_cfg_show(cmd_block, raw = True)    
    logging.info('The result\n%s:' % res)
    ap_port_setting_on_cli = output.parse(res)
    return ap_port_setting_on_cli['PORTS']


def verify_ap_port_setting(expect_info, actual_info):
    """
    expect_info:
        {
            'lan2': {
                     'enabled': True,
                     'type': 'trunk',              #[trunk, access, general]
                     'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                     'vlan_members': '1-4094',   #[1-4094] (expected String type)
                     'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                  },
          }
    actual_info:
        {'Accounting server name for Eth 802.1X': 'achris-acct',
         'Authentication server name for Eth 802.1X': 'achris',
         'LAN ID': {'1': {'802.1X': 'disabled',
                          'DHCP opt82': 'Disabled',
                          'Enable LAN': 'Yes',
                          'LAN Type': 'trunk',
                          'Members': '1-4094',
                          'Untag ID': '1'},
                    '2': {'802.1X': 'auth-port',
                          'DHCP opt82': 'Disabled',
                          'Enable LAN': 'Yes',
                          'LAN Type': 'trunk',
                          'Members': '1-4094',
                          'Untag ID': '1'},
                    '3': {'802.1X': 'supp',
                          'DHCP opt82': 'Disabled',
                          'Enable LAN': 'Yes',
                          'LAN Type': 'trunk',
                          'Members': '1-4094',
                          'Untag ID': '1'}},
         'MAC Auth Bypass': 'Enabled',
         'Supplicant Password': '**************',
         'Supplicant Username': 'ras.local.user'}
    """
    key_map = {"Enable LAN":"enabled",
               "LAN Type":"type",
               "Untag ID":"untagged_vlan",
               "Members":"vlan_members",
               "802.1X":"dot1x",
               "Authentication server name for Eth 802.1X":"dot1x_auth_svr",
               "Accounting server name for Eth 802.1X":"dot1x_acct_svr",
               "Supplicant Username":"dot1x_supp_username",
               "Supplicant Password":"dot1x_supp_password",
               "MAC Auth Bypass":"dot1x_mac_bypass_enabled",               
               }
    _port_setting_cli = _resolve_port_setting_cli(actual_info, key_map)
    _lan_setting_cli = _port_setting_cli.pop("lans")
    attr = _port_setting_cli
    
    for lan_id, lan_setting in _lan_setting_cli.items():
        if lan_id in expect_info.keys():        
            if not _verify_lan_setting(lan_setting, expect_info[lan_id], attr):
                return (False, "Expect:%s, Actual:%s" % (expect_info, lan_setting[lan_id]))
        
    return (True, "")


def verify_ap_port_config(port_setting_cli, port_setting_gui):
    """
    CLI:
    {'Accounting server name for Eth 802.1X': 'achris-acct',
     'Authentication server name for Eth 802.1X': 'achris',
     'LAN ID': {'1': {'802.1X': 'disabled',
                      'DHCP opt82': 'Disabled',
                      'Enable LAN': 'Yes',
                      'LAN Type': 'trunk',
                      'Members': '1-4094',
                      'Untag ID': '1'},
                '2': {'802.1X': 'auth-port',
                      'DHCP opt82': 'Disabled',
                      'Enable LAN': 'Yes',
                      'LAN Type': 'trunk',
                      'Members': '1-4094',
                      'Untag ID': '1'},
                '3': {'802.1X': 'supp',
                      'DHCP opt82': 'Disabled',
                      'Enable LAN': 'Yes',
                      'LAN Type': 'trunk',
                      'Members': '1-4094',
                      'Untag ID': '1'}},
     'MAC Auth Bypass': 'Enabled',
     'Supplicant Password': '**************',
     'Supplicant Username': 'ras.local.user'}
     
    GUI:
    
    {'lan1': {'dot1x': u'disabled',
          'enabled': True,
          'type': u'trunk',
          'untagged_vlan': u'1',
          'vlan_members': ''},
     'lan2': {'dot1x': u'auth-port',
              'dot1x_acct_svr': u'achris-acct',
              'dot1x_auth_svr': u'achris',
              'dot1x_mac_bypass_enabled': True,
              'enabled': True,
              'type': u'trunk',
              'untagged_vlan': u'1',
              'vlan_members': ''},
     'lan3': {'dot1x': u'supp',
              'dot1x_supp_auth_enabled': True,
              'dot1x_supp_mac_enabled': False,
              'dot1x_supp_password': u'ras.local.user',
              'dot1x_supp_username': u'ras.local.user',
              'enabled': True,
              'type': u'trunk',
              'untagged_vlan': u'1',
              'vlan_members': ''},
     'override_parent': True}
    """
    key_map = {"Enable LAN":"enabled",
               "LAN Type":"type",
               "Untag ID":"untagged_vlan",
               "Members":"vlan_members",
               "802.1X":"dot1x",
               "Authentication server name for Eth 802.1X":"dot1x_auth_svr",
               "Accounting server name for Eth 802.1X":"dot1x_acct_svr",
               "Supplicant Username":"dot1x_supp_username",
               "Supplicant Password":"dot1x_supp_password",
               "MAC Auth Bypass":"dot1x_mac_bypass_enabled",               
               }
    
    
    if not port_setting_gui['override_parent']:
        return (True, "Haven't override, won't check in detail")
    
    else:        
        _port_setting_cli = _resolve_port_setting_cli(port_setting_cli, key_map)
        _lan_setting_cli = _port_setting_cli.pop("lans")
        attr = _port_setting_cli
        for lan_id, lan_setting in _lan_setting_cli.items():            
            if not _verify_lan_setting(lan_setting, port_setting_gui[lan_id], attr):
                return (False, "gui_info:%s, cli_info%s" % (lan_setting, port_setting_gui[lan_id]))
            
        return (True, "")
        
def _verify_lan_setting(lan_cli, lan_gui, attr):
    if lan_cli["dot1x"] in ["auth-port", "auth-mac", "supp"]: 
        lan_cli.update(attr) 
        if lan_cli['enabled'] == "Yes":
            lan_cli['enabled'] = True
        else:
            lan_cli['enabled'] = False
                 
        if lan_cli["dot1x"] in ["auth-port", "auth-mac"]:
            lan_cli["dot1x_auth_svr"] = attr["dot1x_auth_svr"]
            lan_cli["dot1x_acct_svr"] = attr["dot1x_acct_svr"]
            if attr["dot1x_mac_bypass_enabled"] == "Disabled":                
                lan_cli["dot1x_mac_bypass_enabled"] = False
            else:
                lan_cli["dot1x_mac_bypass_enabled"] = True
                            
        elif lan_cli["dot1x"] == "supp":            
            if lan_cli["dot1x_supp_username"] == "MAC Address (Use MAC Address of AP as User Name)":
                lan_cli["dot1x_supp_mac_enabled"] = True
                lan_cli["dot1x_supp_auth_enabled"] = False                
            else:
                lan_cli["dot1x_supp_mac_enabled"] = False
                lan_cli["dot1x_supp_auth_enabled"] = True
            
            #Doesn't check password, which has already encoded.
            lan_cli.pop("dot1x_supp_password")            
#            lan_gui.pop("dot1x_supp_password")
        
        return _verify_port_info(lan_cli, lan_gui)
        
    elif lan_cli["dot1x"] == lan_gui["dot1x"] and lan_cli["dot1x"] == "disabled":
        return True
            

def _resolve_port_setting_cli(port_setting, key_map):
    _dd = {}
    for key, value in port_setting.items():
        if key in key_map.keys():
            _dd[key_map[key]] = value
            if key == "LAN ID":
                continue
    
    lan_cfg = port_setting['LAN ID']
    _lan_dd = {}
    for lan_id, lan_setting in lan_cfg.items():
        _tt = {}
        for key, value in lan_setting.items():
            if key in key_map.keys():
                _tt[key_map[key]] = value
                            
        _lan_dd["lan%s" % lan_id] = _tt
    
    _dd.update({"lans":_lan_dd})
    
    return _dd 

def _verify_port_info(cli_info,gui_info):
    cli_ks = cli_info.keys()
    gui_ks = gui_info.keys()
    
    for key in gui_ks:
        if key in cli_ks:  
            if cli_info[key] is str:
                e_v = str(gui_info[key])
            else:
                e_v = gui_info[key]
                                              
            if cli_info[key] != e_v:
                logging.info("Expected value %s=%s, actual %s=%s" % (key, cli_info[key], key, gui_info[key]))
                return False
        
    logging.info('The information of port setting in CLI is correct!')
    return True
            

def verify_ap_all(all_ap_info_on_cli,all_ap_info_on_zd):
    """ 
       all_ap_info_on_zd:
       [{'channel': u'11 (11b/g)',
      'clients': u'0',
      'description': u'',
      'device_name': u'',
      'ip_addr': u'192.168.0.123',
      'mac': u'00:24:82:22:9a:c0',
      'mesh_mode': u'Auto',
      'model': u'zf2942',
      'status': u'Connected (Root AP)'},
     {'channel': u'1 (11b/g)',
      'clients': u'0',
      'description': u'',
      'device_name': u'ChowChow',
      'ip_addr': u'192.168.0.177',
      'mac': u'00:24:82:22:94:c0',
      'mesh_mode': u'Auto',
      'model': u'zf2942',
      'status': u'Connected (Root AP)'}]
      
      
      {'AP': {'ID': {'1': {'Approved': 'Yes',
                     'Description': '',
                     'Device Name': 'ChowChow',
                     'GPS': '',
                     'Location': 'QARuckus',
                     'MAC Address': '00:24:82:22:94:c0',
                     'Mesh': {'Mode': 'Auto', 'Status': 'Enabled'},
                     'Model': 'zf2942',
                     'Network Setting': {'Device IP Settings': "Keep AP's Setting",
                                         'Gateway': '192.168.0.253',
                                         'IP Address': '192.168.0.177',
                                         'Netmask': '255.255.255.0',
                                         'Primary DNS Server': '192.168.0.252',
                                         'Secondary DNS Server': '0.0.0.0'},
                     'Radio b/g/n': {'Channel': 'Auto',
                                     'TX Power': 'Use Global Configuration',
                                     'WLAN Group Name': 'Default'}},
               '2': {'Approved': 'Yes',
                     'Description': '',
                     'Device Name': '',
                     'GPS': '',
                     'Location': '',
                     'MAC Address': '00:24:82:22:9a:c0',
                     'Mesh': {'Mode': 'Auto', 'Status': 'Enabled'},
                     'Model': 'zf2942',
                     'Network Setting': {'Device IP Settings': "Keep AP's Setting",
                                         'Gateway': '192.168.0.253',
                                         'IP Address': '192.168.0.123',
                                         'Netmask': '255.255.255.0',
                                         'Primary DNS Server': '192.168.0.252',
                                         'Secondary DNS Server': '0.0.0.0'},
                     'Radio b/g/n': {'Channel': 'Auto',
                                     'TX Power': 'Use Global Configuration',
                                     'WLAN Group Name': 'Default'},
                     'Uplink Status': 'Smart'}}},
 'ruckus#': ''}
      
      
   """
    logging.info("AP information on CLI: %s" % all_ap_info_on_cli)
    logging.info("AP information on ZD: %s" % all_ap_info_on_zd)
    
    number = len(all_ap_info_on_zd)
    for k in range(1,number+1):
        for j in range(1,number+1):
            cli_info = _generate_cli_info(all_ap_info_on_cli,k)
            gui_info = _generate_gui_info(all_ap_info_on_zd,j)
            if cli_info['mac'] == gui_info['mac']:
                if not _verify_ap_info(cli_info,gui_info):
                    return False
    return True
        
def _generate_cli_info(cli_info,k):
    info = {}
    k = str(k)
    cli_infomation = cli_info['AP']["ID"][k]
#    key_list = ['description','device_name','ip_addr','mac','model']
    info['description'] =  cli_infomation['Description']
    info['device_name'] = cli_infomation['Device Name']
    info['ip_addr'] = cli_infomation['Network Setting']['IP Address']
    info['mac'] = cli_infomation['MAC Address']
    info['model'] = cli_infomation['Model']
    
    return info
    
def _generate_gui_info(gui_info,k):
    info = {}
    info['description'] = gui_info[k-1]['description']
    info['device_name'] = gui_info[k-1]['device_name']
    info['ip_addr'] = gui_info[k-1]['ip_addr']
    info['mac'] = gui_info[k-1]['mac']
    info['model'] = gui_info[k-1]['model']
    
    return info

def _generate_gui_info_by_mac(gui_info):
    info = {}
    info['description'] = gui_info['general']['description']
    info['device_name'] = gui_info['general']['devname']
    info['ip_addr'] = gui_info['general']['ip']
    info['mac'] = gui_info['general']['mac']
    info['model'] = gui_info['general']['model']
    
    return info
    
def _verify_ap_info(cli_info,gui_info):
    cli_ks = cli_info.keys()
    gui_ks = gui_info.keys()
    
    for key in gui_ks:
        if key not in cli_ks:
            logging.info('The parameter [%s] of AP [%s] exists in GUI but not in CLI' % (key, gui_info['mac']))
            return False
        
        if cli_info[key] != gui_info[key]:
            logging.info("The information of AP [%s] in CLI [%s = %s] is not the same as in GUI [%s = %s]" % (cli_info['mac'], key, cli_info[key], key, gui_info[key]))
            return False
        
    logging.info('The information of AP [%s] in CLI is correct!' % cli_info['mac'])
    return True
            

def verify_ap_name(ap_info_on_cli,ap_info_on_zd,k=1):
    
    logging.info("AP information on CLI: %s" % ap_info_on_cli)
    logging.info("AP information on ZD: %s" % ap_info_on_zd)
    
    
    cli_info = _generate_cli_info(ap_info_on_cli,k)
    gui_info = _generate_gui_info_by_mac(ap_info_on_zd)
    if not _verify_ap_info(cli_info,gui_info):
        return False
    return True

def verify_ap_mac(ap_info_on_cli,ap_info_on_zd,k = 1):
    """ 
        In [45]: zd.get_ap_info_ex('00:24:82:22:94:c0')
    Out[45]:
    {'downlink': {},
     'general': {'description': u'',
                 'devname': u'ChowChow',
                 'firmware_version': u'9.0.0.0.54',
                 'ip': u'192.168.0.177',
                 'mac': u'00:24:82:22:94:c0',
                 'model': u'zf2942',
                 'serial_number': u'990901003364'},
     'info': {'num_sta': u'0',
              'status': u'Connected (Root AP)',
              'tunnel_mode': u'L2',
              'uptime': u'3d 22h 50m',
              'wlan_id': u''},
     'neighbor': {},
     'radio': {'airtime': u'0.0/0.0/0.0/0.0',
               'bgscan': u'Enabled',
               'channel': u'1',
               'channelization': u'',
               'mcast': u'0.00',
               'noisefloor': u'-93',
               'num_sta': u'0',
               'phyerr': u'0',
               'retries': u'0.00 / 0.00',
               'rx': u'91M/16G',
               'tx': u'29K/3.8M',
               'tx_power': u'100%',
               'wlangroup': u'Default'},
     'uplink': {'ap': u'',
                'assoc': u'0',
                'desc': u'',
                'retries': u'',
                'rssi': u'',
                'rx': u'',
                'tx': u'',
                'type': u''},
     'wlans': {}}
    """

    logging.info("AP information on CLI: %s" % ap_info_on_cli)
    logging.info("AP information on ZD: %s" % ap_info_on_zd)

    cli_info = _generate_cli_info(ap_info_on_cli,k)
    gui_info = _generate_gui_info_by_mac(ap_info_on_zd)
    if not _verify_ap_info(cli_info,gui_info):
        return False
    return True

def verify_ap_ip_cfg_cli_get_set(set_ip_cfg, cli_get_cfg):
    '''
    CLI get config:
    u'Network Setting':{u'Protocol mode': u'IPv4 and IPv6',
                        u'Device IP Settings': u'DHCP',
                        u'Netmask': u'255.255.255.0',
                        u'Primary DNS Server': u'192.168.0.252',
                        u'Secondary DNS Server': u'',
                        u'Gateway': u'192.168.0.253',
                        u'IP Address': u'192.168.0.198',
                        u'Device IPv6 Settings': u'Auto Configuration',
                        u'IPv6 Address': u'2020:db8:1:0:64f:aaff:fe2a:6240',
                        u'IPv6 Gateway': u'',
                        u'IPv6 Prefix Length': u'64',
                        u'IPv6 Primary DNS Server': u'',
                        u'IPv6 Secondary DNS Server': u'',
                       },
    CLI set config:
    {'ip_version': 'dualstack', 'ipv4': {'ip_mode': 'dhcp'}, 'ipv6': {'ipv6_mode': 'auto'}}, 'ap_mac_list': u'04:4f:aa:2a:62:40'}
    {'ip_version': 'ipv6', 'ipv6': {'ipv6_mode': 'auto'}}                   
    '''
    cli_get_ip_cfg = cli_get_cfg['Network Setting']
    new_cli_get_ip_cfg = _convert_cli_ip_cfg(cli_get_ip_cfg)
    
    res = _compare_ip_cfg_dict(set_ip_cfg, new_cli_get_ip_cfg)
    
    return res

def verify_ap_ip_cfg_gui_cli_get(gui_get_cfg, cli_get_cfg):
    '''
    GUI get config:
     u'04:4f:aa:2a:62:40': {   'ip_version': 'dualstack',
                               'ipv4': {'ip_mode': 'dhcp'},
                               'ipv6': {'ipv6_mode': 'auto'}
    '''
    cli_get_ip_cfg = cli_get_cfg['Network Setting']
    new_cli_get_ip_cfg = _convert_cli_ip_cfg(cli_get_ip_cfg)
    
    res = _compare_ip_cfg_dict(gui_get_cfg, new_cli_get_ip_cfg)
    
    return res

def _convert_cli_ip_cfg(cli_ip_cfg):
    keys_mapping = {'Protocol mode': 'ip_version',
                    'Device IP Settings': 'ip_mode',
                    'IP Address': 'ip_addr',
                    'Netmask': 'netmask',
                    'Gateway': 'gateway',
                    'Primary DNS Server': 'pri_dns',
                    'Secondary DNS Server': 'sec_dns',
                    'Device IPv6 Settings': 'ipv6_mode',
                    'IPv6 Address': 'ipv6_addr',
                    'IPv6 Prefix Length': 'ipv6_prefix_len',
                    'IPv6 Gateway': 'ipv6_gateway',
                    'IPv6 Primary DNS Server': 'ipv6_pri_dns',
                    'IPv6 Secondary DNS Server': 'ipv6_sec_dns',
                    }
    
    ipv4_keys = ['ip_mode', 'ip_addr', 'netmask', 'gateway', 'pri_dns', 'sec_dns']
    ipv6_keys = ['ipv6_mode', 'ipv6_addr', 'ipv6_prefix_len' , 'ipv6_gateway', 'ipv6_pri_dns' , 'ipv6_sec_dns']
    
    values_mapping = {'IPv4 and IPv6': const.DUAL_STACK,
                      'IPv4-Only': const.IPV4,
                      'IPv6-Only': const.IPV6,
                      'Auto Configuration': 'auto',
                      }
    
    new_cli_ip_cfg = {}
    
    ipv4_cfg = {}
    ipv6_cfg = {}
    
    for key, value in cli_ip_cfg.items():
        new_key = key
        if keys_mapping.has_key(key):
            new_key = keys_mapping[key]
            
        new_value = value
        if values_mapping.has_key(value):
            new_value = values_mapping[value]
        
        if new_key in ipv4_keys:
            ipv4_cfg[new_key] = new_value
        elif new_key in ipv6_keys:
            ipv6_cfg[new_key] = new_value
        else:
            new_cli_ip_cfg[new_key] = new_value
            
    if ipv4_cfg:
        new_cli_ip_cfg[const.IPV4] = ipv4_cfg
    if ipv6_cfg:
        new_cli_ip_cfg[const.IPV6] = ipv6_cfg
        
    return new_cli_ip_cfg

def _compare_ip_cfg_dict(ip_cfg_1, ip_cfg_2):
    '''
    Compare get and set IP configuration.        
    '''
    res_err = {}
    
    key_version = 'ip_version'
    set_ip_version = ip_cfg_1.get(key_version)
    get_ip_version = ip_cfg_2.get(key_version)
    
    if set_ip_version and get_ip_version and set_ip_version.lower() == get_ip_version.lower():
        if get_ip_version in [const.IPV4, const.DUAL_STACK]:
            err_msg = ''
            key_ipv4 = const.IPV4
            if ip_cfg_1.has_key(key_ipv4) and ip_cfg_2.has_key(key_ipv4):
                set_ipv4_cfg = ip_cfg_1[key_ipv4]
                get_ipv4_cfg = ip_cfg_2[key_ipv4]
                
                key_ip_alloc = 'ip_mode'
                set_ipv4_alloc = set_ipv4_cfg.get(key_ip_alloc)
                get_ipv4_alloc = get_ipv4_cfg.get(key_ip_alloc)
                
                if set_ipv4_alloc and get_ipv4_alloc and set_ipv4_alloc.lower() == get_ipv4_alloc.lower():
                    if set_ipv4_alloc.lower() in ['manual','static']:
                        err_msg = compare_dict_key_value(set_ipv4_cfg, get_ipv4_cfg)
                else:
                    err_msg = 'Error: Item ipv4 alloc has difference (%s,%s)' % (set_ipv4_alloc, get_ipv4_alloc)
                
            else:
                if not ip_cfg_1.has_key(key_ipv4):
                    err_msg = 'No ipv4 configuration in set config: %s' % ip_cfg_1
                else:
                    err_msg = 'No ipv4 configuration in get config: %s' % ip_cfg_2
                    
            if err_msg:
                res_err[key_ipv4] = err_msg
            
        if get_ip_version in [const.IPV6, const.DUAL_STACK]:
            err_msg = ''
            
            key_ipv6 = const.IPV6
            if ip_cfg_1.has_key(key_ipv6) and ip_cfg_2.has_key(key_ipv6):
                set_ipv6_cfg = ip_cfg_1[key_ipv6]
                get_ipv6_cfg = ip_cfg_2[key_ipv6]
                
                key_ipv6_alloc = 'ipv6_mode'
                set_ipv6_alloc = set_ipv6_cfg.get(key_ipv6_alloc)
                get_ipv6_alloc = get_ipv6_cfg.get(key_ipv6_alloc)
                
                if set_ipv6_alloc and get_ipv6_alloc and set_ipv6_alloc.lower() == get_ipv6_alloc.lower():
                    if set_ipv6_alloc == 'manual':
                        err_msg = compare_dict_key_value(set_ipv6_cfg, get_ipv6_cfg)
                else:
                    err_msg = 'Error: Item ipv6 alloc has difference (%s,%s)' % (set_ipv6_alloc, get_ipv6_alloc)
                
            else:
                if not ip_cfg_1.has_key(key_ipv6):
                    err_msg = 'No ipv6 configuration in set config: %s' % ip_cfg_1
                else:
                    err_msg = 'No ipv6 configuration in get config: %s' % ip_cfg_2
            
            if err_msg:
                res_err[key_ipv6] = err_msg
            
    else:
        if set_ip_version == get_ip_version:
            err_msg = 'IP version is null in both set and get.'                    
        else:
            err_msg = 'Error: Item ip version has difference (%s,%s)' % (set_ip_version, get_ip_version)
        res_err['ip_version'] = err_msg
                
    return res_err

def get_ap_status(zdcli,ap_mac):
    ap_mac = ap_mac.lower()
    cmd = 'wlaninfo -a %s'%ap_mac
    not_found = 'AP %s not found'%ap_mac
    res = zdcli.do_shell_cmd(cmd)
    if not_found in res:
        return 'disconnected'
    else:
        return 'connected'

def get_ap_group_name(zdcli,ap_mac):
    ap_mac = ap_mac.lower()
    cmd = 'show ap mac %s'%ap_mac
    res = zdcli.do_cmd(cmd)
    return res.split('Group Name=')[1].split('\r\r\n')[0].strip()

#@author: yu.yanan #@since: 2014-6-10 
def get_ap_ip(zdcli,ap_mac):
    ap_mac = ap_mac.lower()
    cmd = 'show ap mac %s'%ap_mac
    res = zdcli.do_cmd(cmd,timeout = 20)
    logging.info("AP information on ZD: %s" % res)
    ip_mode = res.split('Protocol mode=')[1].split('\r\r\n')[0].strip()
    if ip_mode == 'IPv6-Only': 
        ip = res.split('IPv6 Address=')[1].split('\r\r\n')[0].strip()
    else:
        ip = res.split('IP Address=')[1].split('\r\r\n')[0].strip()
    return ip