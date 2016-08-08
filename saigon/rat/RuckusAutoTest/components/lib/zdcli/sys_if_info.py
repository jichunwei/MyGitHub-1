'''
Author#cwang@ruckuswireless.com
date#2010-10-28
This file is used for system interface information [Device IP Address] getting/setting/searching etc.
'''
from string import Template

import logging
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common.utils import compare_dict_key_value
from RuckusAutoTest.components.lib.zdcli.administrator_functions import reboot
from RuckusAutoTest.common import lib_Constant as const


#=============================================#
#             Access Methods            
#=============================================#
def get_sys_if_info(zdcli):
    '''
    Get system interface information.
    '''  
    res = zdcli.do_cfg_show(SHOW_SYS_IF)
    
    rr = output.parse(res)
    return rr
    

def verify_device_ip_addr(gui_d, cli_d):
    '''
    Checking device information, between GUI and CLI.
    '''
    return _verify_device_ip_addr(gui_d, cli_d)

def verify_device_ip_settings(dict_1, cli_d):
    '''
    Verify device ip settings between gui/set and cli get.
    dict_1 is gui get or set dict.
    '''
    cli_key_mapping = {'ip_version': 'Protocol Mode',
                       'ipv4': 'Device IP Address',
                       'ipv6': 'Device IPv6 Address',
                       'vlan': 'Management VLAN',
                       }
    
    ipv4_cli_key_mapping = {'ip_alloc': 'Mode',
                            'ip_addr': 'IP Address',
                            'gateway': 'Gateway Address',
                            'netmask': 'Netmask',
                            'pri_dns': 'Primary DNS',
                            'sec_dns': 'Secondary DNS',
                            }
    
    ipv6_cli_key_mapping = {'ipv6_alloc': 'Mode',
                            'ipv6_addr': 'IPv6 Address',
                            'ipv6_gateway': 'Gateway Address',
                            'ipv6_prefix_len': 'Prefix Length',
                            'ipv6_pri_dns': 'Primary DNS',
                            'ipv6_sec_dns': 'Secondary DNS',
                            }
    
    mode_value_mapping = {'dual stack': 'dualstack',
                          'IPv4-Only': 'ipv4',
                          'IPv6-Only': 'ipv6',
                          }
    
    new_cli_d = {}
    
    for new_key, cli_key in cli_key_mapping.items():
        if cli_d.has_key(cli_key):
            new_value = cli_d[cli_key]
            if new_key == 'ipv4':
                new_value = _convert_cli_d(new_value, ipv4_cli_key_mapping)
            elif new_key == 'ipv6':
                new_value = _convert_cli_d(new_value, ipv6_cli_key_mapping)
            elif new_key == 'ip_version':
                if mode_value_mapping.has_key(new_value):
                    new_value = mode_value_mapping[new_value]
            elif new_key == 'vlan':
                if new_value.has_key('Status') and new_value['Status'].lower() == 'disabled':
                    new_value = ''
                else:   
                    new_value = new_value['VLAN ID']
        else:
            new_value = ''
        new_cli_d[new_key] = new_value
                    
    res = _compare_ip_settings(new_cli_d, dict_1)
    
    return res 
    
def set_sys_if(zdcli,conf,ip_type = const.IPV4):
    '''
    Set system interfaces include ip version, ipv4 and ipv6 configurations.
    If ip_version is ipv4, set ipv4 configuration, which is compatible the old version without ipv6. 
    If ip_version is ipv6, set ip version as conf['version'].
    '''
    #Set ip version.
    timeout = 60
    
    logging.info('Set system interface as %s' % conf)
    sys_if_config_cmd_block = _define_sys_if_config_cmd_block(conf, ip_type)
    _do_excute_cmd(zdcli,sys_if_config_cmd_block, timeout=timeout)
    logging.info('Restarting ZD to make setting take effecct.')
    reboot(zdcli)

#===============================================#
#           Protected Constant
#===============================================#
SHOW_SYS_IF = '''
system
    interface
'''

SET_SYS_IF_IP_MODE= '''
system
    interface
        ip mode $mode
'''

SET_SYS_IF_IP_GATEWAY = '''
system
    interface
        ip route gateway $gateway
'''

SET_SYS_IF_IP_ADDR = '''
system
    interface
        ip addr $ip_addr $net_mask
'''

SET_SYS_IF_IP_DNS = '''
system
    interface
        ip name-server $pri_dns $sec_dns
'''

SET_SYS_IF_VLAN = '''
system
    interface
        vlan $vlan_id
'''

REMOVE_SYS_IF_VLAN = '''
system
    interface
        no vlan
'''

IP_ADD_K_MAP = {'Gateway Address':'gateway',
                'IP Address':'ip_addr',
                'Netmask':'net_mask',
                'Primary DNS':'pri_dns',
                'Secondary DNS':'sec_dns',
                }

#IPV6 configuration.
SET_SYS_IF_DISABLE_IPV4 = 'no ip'
SET_SYS_IF_DISABLE_IPV6 = 'no ipv6'

SET_SYS_IF_ENABLE_IPV4 = 'ip enable'
SET_SYS_IF_IPV4_GATEWAY = 'ip route gateway $gateway'
SET_SYS_IF_IPV4_DNS = 'ip name-server $pri_dns $sec_dns'
SET_SYS_IF_IPV4_ADDR = 'ip addr $ip_addr $net_mask'
SET_SYS_IF_IPV4_MODE ='ip mode $mode' #dhcp/static

SET_SYS_IF_ENABLE_IPV6 = 'ipv6 enable'
SET_SYS_IF_IPV6_GATEWAY = 'ipv6 route gateway $gateway'
SET_SYS_IF_IPV6_DNS = 'ipv6 name-server $pri_dns $sec_dns'
SET_SYS_IF_IPV6_ADDR = 'ipv6 addr $ip_addr $prefix_len'
SET_SYS_IF_IPV6_MODE = 'ipv6 mode $mode' #auto/manual

SET_SYS_IF_VLAN = 'vlan $vlan_id'
SET_SYS_IF_DISABLE_VLAN = 'no vlan'

#===============================================#
#           Protected Method
#===============================================#
def _define_sys_if_config_cmd_block(conf, ip_type = const.IPV4):
    """
    For ip_version is ipv4:
    {'gateway': '192.168.0.253',
    'ip_addr': '192.168.0.2',
    'mode': 'static',
    'net_mask': '255.255.255.0',
    'pri_dns': '192.168.0.252',
    'sec_dns': '192.168.0.254'}
    For ip_version is ipv6:
        ip_version: ipv4, ipv6, dualstack.
        vlan: ipv4 vlan.
        ipv4:
           mode: ipv4 setting mode: manual/dhcp.
           ip_addr: ipv4 address.
           netmask: ipv4 net mask.
           gateway: ipv4 gateway.
           pri_dns: ipv4 primary dns.
           sec_dns: ipv4 secondary dns.    
        ipv6:
           ipv6_mode: ipv6 setting mode: manual/auto.
           ipv6_addr: ipv6 address.
           ipv6_prefix_len: ipv6 prefix len.
           ipv6_gateway: ipv6 gateway.
           ipv6_pri_dns: ipv6 primary dns.
           ipv6_sec_dns: ipv6 secondary dns.
    """                         
    cmd_block = '%s' % (SHOW_SYS_IF)
    
    ipv4_conf = None
    ipv6_conf = None        
    
    if ip_type == const.IPV6:
        ip_version = conf['ip_version']       
        #Generate ip version configuration.
        if ip_version in [const.IPV4, const.DUAL_STACK]:
            cmd_block += "%s\n" % SET_SYS_IF_ENABLE_IPV4
            ipv4_conf = conf.get('ipv4')
        else:
            cmd_block += "%s\n" % SET_SYS_IF_DISABLE_IPV4
            
        if ip_version in [const.IPV6, const.DUAL_STACK]:
            cmd_block += "%s\n" % SET_SYS_IF_ENABLE_IPV6
            ipv6_conf = conf.get('ipv6')
        else:
            cmd_block += "%s\n" % SET_SYS_IF_DISABLE_IPV6            
    else:
        ipv4_conf = conf
    
    if ipv4_conf:
        #Generate cmd block for ipv6 config.
        if ipv4_conf.has_key('ip_alloc'):
            ip_alloc = ipv4_conf['ip_alloc'].lower()
        else:
            ip_alloc = ipv4_conf['mode'].lower()
            
        cmd_block += "%s\n" % Template(SET_SYS_IF_IPV4_MODE).substitute(dict(mode = ip_alloc)) 
        if ip_alloc == 'static':
            cmd_block += "%s\n" % Template(SET_SYS_IF_IPV4_ADDR).substitute(dict(ip_addr = ipv4_conf['ip_addr'], 
                                                                                 net_mask = ipv4_conf['netmask']))
            cmd_block += "%s\n" % Template(SET_SYS_IF_IPV4_GATEWAY).substitute(dict(gateway = ipv4_conf['gateway']))
            if ipv4_conf.has_key('sec_dns'):
                cmd_block += "%s\n" % Template(SET_SYS_IF_IPV4_DNS).substitute(dict(pri_dns = ipv4_conf['pri_dns'],
                                                                                    sec_dns = ipv4_conf['sec_dns']))
            else:
                cmd_block += "%s\n" % Template(SET_SYS_IF_IPV4_DNS).substitute(dict(pri_dns = ipv4_conf['pri_dns'], 
                                                                                    sec_dns = ''))
                                                                      
    if ipv6_conf:
        if ipv6_conf.has_key('ipv6_alloc'):
            ipv6_alloc = ipv6_conf['ipv6_alloc'].lower()
        else:
            ipv6_alloc = ipv6_conf['ipv6_mode'].lower()
            
        cmd_block += "%s\n" % Template(SET_SYS_IF_IPV6_MODE).substitute(dict(mode = ipv6_alloc)) 
        if ipv6_alloc == 'manual':
            cmd_block += "%s\n" % Template(SET_SYS_IF_IPV6_ADDR).substitute(dict(ip_addr = ipv6_conf['ipv6_addr'], 
                                                                                 prefix_len = ipv6_conf['ipv6_prefix_len']))
            cmd_block += "%s\n" % Template(SET_SYS_IF_IPV6_GATEWAY).substitute(dict(gateway = ipv6_conf['ipv6_gateway']))
            if ipv6_conf.has_key('ipv6_sec_dns'):
                cmd_block += "%s\n" % Template(SET_SYS_IF_IPV6_DNS).substitute(dict(pri_dns = ipv6_conf['ipv6_pri_dns'], 
                                                                                    sec_dns = ipv6_conf['ipv6_sec_dns']))
            else:
                cmd_block += "%s\n" % Template(SET_SYS_IF_IPV6_DNS).substitute(dict(pri_dns = ipv6_conf['ipv6_pri_dns'],
                                                                                    sec_dns = ''))
                
    logging.info(cmd_block)
    return cmd_block
        
def _set_sys_if_mode(zdcli,conf,timeout):
    if conf.has_key('mode'):
        mode = conf['mode']
        cmd = Template(SET_SYS_IF_IP_MODE).substitute(dict(mode = mode))
        _do_excute_cmd(zdcli,cmd,timeout)
    
def _set_sys_if_ip_addr(zdcli,conf,timeout):
    if conf.has_key('ip_addr') and conf['ip_addr']:
        ip_addr = conf['ip_addr']
        net_mask = conf['net_mask']
        cmd = Template(SET_SYS_IF_IP_ADDR).substitute(dict(ip_addr = ip_addr,
                                                           net_mask = net_mask))
        _do_excute_cmd(zdcli,cmd,timeout)

def _set_sys_if_ip_gateway(zdcli,conf):
    if conf.has_key('gateway'):
        gateway = conf['gateway']
        cmd = Template(SET_SYS_IF_IP_GATEWAY).substitute(dict(gateway = gateway))
        _do_excute_cmd(zdcli,cmd)

def _set_sys_if_ip_dns(zdcli,conf):
    if conf.has_key('pri_dns') and conf['pri_dns']:
        pri_dns = conf['pri_dns']
    if conf.has_key('sec_dns'):
        sec_dns = conf['sec_dns']
    
    cmd = Template(SET_SYS_IF_IP_DNS).substitute(dict(pri_dns = pri_dns,
                                                      sec_dns = sec_dns))
    _do_excute_cmd(zdcli,cmd)
                
def _set_vlan(zdcli,conf):
    if conf.has_key('vlan_id') and conf['vlan_id']:
        vlan_id = conf['vlan_id']
        cmd = Template(SET_SYS_IF_VLAN).substitute(dict(vlan_id = vlan_id))
        
        _do_excute_cmd(zdcli,cmd)

def _remove_vlan(zdcli,conf={}):
    cmd = REMOVE_SYS_IF_VLAN
    _do_excute_cmd(zdcli,cmd)
    

def _do_excute_cmd(zdcli,cmd, timeout=10):
    try:
        logging.info("CLI is: %s" %cmd)
        zdcli.do_cfg(cmd, timeout=timeout, print_out = True, raw = True)
    except Exception,ex:
        errmsg = ex.message
        raise Exception(errmsg)
    


def _verify_device_ip_addr(gui_d, cli_d):
    '''
    GUI:
       {'gateway': u'192.168.0.253',
        'ip_addr': u'192.168.0.2',
        'net_mask': u'255.255.255.0',
        'pri_dns': u'192.168.0.252',
        'sec_dns': u''}
    CLI:
        {'Gateway Address': '192.168.0.253',
         'IP Address': '192.168.0.2',
         'Mode': 'DHCP',
         'Netmask': '255.255.255.0',
         'Primary DNS': '192.168.0.252',
         'Secondary DNS': ''}   
    '''
    r_d = _map_k_d(gui_d, cli_d, IP_ADD_K_MAP)
    return _validate_dict_value(r_d, cli_d)

def _verify_mgmt_vlan(gui_d, cli_d):
    '''
    GUI:
    ?
    CLI:
    {'Status': 'Disabled', 'VLAN ID': ''}
    '''


def _map_k_d(gui_d, cli_d, k_map):
    '''
    Mapping GUI key to CLI key.
    '''
    r_d = {}
    for key in gui_d.keys():
        for k, v in k_map.items():
            if key == v:
                r_d[k] = gui_d[v]
                
    return r_d

def _convert_cli_d(cli_d, cli_key_mapping):
    '''
    Mapping CLI key to new key.
    '''
    new_cli_d = {}
    
    for new_key, cli_key in cli_key_mapping.items():
        if cli_d.has_key(cli_key):
            new_cli_d[new_key] = cli_d[cli_key]
        else:
            new_cli_d[new_key] = ''
            
    return new_cli_d
    
def _validate_dict_value(gui_d, cli_d):
    for g_k, g_v in gui_d.items():
        for c_k, c_v in cli_d.items():
            if g_k == c_k:
                if g_v == c_v:
                    continue
                else:
                    return (False, 'value of key [%s] is not equal' % g_k)
                            
    return (True, 'All of value are matched')


def verify_cli_set_get(cli_set,cli_get):
    '''
    cli_set:
        {ip_mode:static, ip_addr:'',...}
    cli_get:
        {'Device IP Address': {'Gateway Address': '192.168.0.253',
                       'IP Address': '192.168.0.2',
                       'Mode': 'Manual',
                       'Netmask': '255.255.255.0',
                       'Primary DNS': '1.1.1.1',
                       'Secondary DNS': '2.2.2.2'},
         'Management VLAN': {'Status': 'Disabled', 'VLAN ID': ''}}
    '''
    cli_get_info = {}
    cli_get_info.update(cli_get['Device IP Address'])
    cli_get_info.update(cli_get['Management VLAN'])
    
    if cli_get_info['Mode'] == 'Manual':
        cli_get_info['Mode'] = 'static'
        if cli_get_info['IP Address'] != cli_set['ip_addr']:
            return('[ZDCLI:] Get IP Address [%s],expect Set[%s]' %(cli_get_info['IP Address'],cli_set['ip_addr']))
        
        if cli_get_info['Netmask'] != cli_set['net_mask']:
            return('[ZDCLI:] Get Netmask [%s],expect Set[%s]' %(cli_get_info['Netmask'],cli_set['net_mask']))
        
        if cli_get_info['Gateway Address'] != cli_set['gateway']:
            return('[ZDCLI:] Get Gateway Address [%s],expect Set[%s]' %(cli_get_info['Gateway Address'],cli_set['gateway']))
        
        if cli_get_info['Primary DNS'] != cli_set['pri_dns']:
            return('[ZDCLI:] Get Primary DNS [%s],expect Set[%s]' %(cli_get_info['Primary DNS'],cli_set['pri_dns']))
        
        if cli_get_info['Secondary DNS'] != cli_set['sec_dns']:
            return('[ZDCLI:] Get Secondary DNS [%s],expect Set[%s]' %(cli_get_info['Secondary DNS'],cli_set['sec_dns']))
        
    if cli_get_info['Mode'].lower() != cli_set['mode'].lower():
        return('[ZDCLI:] Get System Interface IP Mode [%s], expect Set[%s]' %(cli_get_info['Mode'],cli_set['mode']))


def verify_cli_set_gui_get(cli_set,gui_get):
    '''
    gui_get:
    {'gateway': u'192.168.0.253',
     'ip_addr': u'192.168.0.2',
     'ip_alloc': 'manual',
     'netmask': u'255.255.255.0',
     'pri_dns': u'',
     'sec_dns': u'',
     'vlan': u''}
    '''
    if gui_get['ip_alloc'] == 'manual':
        gui_get['ip_alloc'] = 'static'
        if gui_get['ip_addr'] != cli_set['ip_addr']:
            return("[ZDGUI:] Get System Interface IP Address [%s], expect Set[%s]" %(gui_get['ip_addr'],cli_set['ip_addr']))
    
        if gui_get['netmask'] != cli_set['net_mask']:
            return("[ZDGUI:] Get System Interface IP netmask [%s], expect Set[%s]" %(gui_get['netmask'],cli_set['net_mask']))
    
        if gui_get['gateway'] != cli_set['gateway']:
            return("[ZDGUI:] Get System Interface IP gateway [%s], expect Set[%s]" %(gui_get['gateway'],cli_set['gateway']))
    
        if gui_get['pri_dns'] != cli_set['pri_dns']:
            return("[ZDGUI:] Get System Interface IP pri_dns [%s], expect Set[%s]" %(gui_get['pri_dns'],cli_set['pri_dns']))
        
        if gui_get['sec_dns'] != cli_set['sec_dns']:
            return("[ZDGUI:] Get System Interface IP sec_dns [%s], expect Set[%s]" %(gui_get['sec_dns'],cli_set['sec_dns']))
    
    if gui_get['ip_alloc'].lower() != cli_set['mode'].lower():
        return("[ZDGUI:] Get System Interface IP Mode [%s], expect Set[%s]" %(gui_get['ip_alloc'],cli_set['mode']))
    
    
def _compare_ip_settings(dict_1, dict_2):
    '''
    Compare ip setting in two dicts.
    '''
    res_err = {}
    logging.info('Compare two dict about zd ip settings.dict_1:%s',dict_1)
    logging.info('Compare two dict about zd ip settings.dict_2:%s',dict_2)
    if dict_1 and dict_2:
        key_version = 'ip_version'
        ip_version_1 = dict_1.get(key_version)
        ip_version_2 = dict_2.get(key_version)
        
        if ip_version_1 and ip_version_2 and ip_version_1.lower() == ip_version_2.lower():
            if ip_version_2 in [const.IPV4, const.DUAL_STACK]:
                err_msg = _compare_ip_detail_cfg(dict_1, dict_2, const.IPV4)
                if err_msg:
                    res_err[const.IPV4] = err_msg
            if ip_version_2 in [const.IPV6, const.DUAL_STACK]:
                err_msg = _compare_ip_detail_cfg(dict_1, dict_2, const.IPV6)
                if err_msg:
                    res_err[const.IPV6] = err_msg
                    
            key_vlan = 'vlan'
            if dict_1.has_key(key_vlan):
                if dict_1.get(key_vlan) != dict_2.get(key_vlan):
                    err_msg = 'Item vlan has difference (%s,%s)' % (dict_1.get(key_vlan), dict_2.get(key_vlan))
                
        else:
            if ip_version_1 == ip_version_2:
                err_msg = 'IP version is null in both set and get.'             
            else:
                err_msg = 'Error: Item ip version has difference (%s,%s)' % (ip_version_1, ip_version_2)
            res_err['ip_version'] = err_msg
    else:
        if not dict_1:
            res_err = "Dict_1 is empty, dict_2 is %s" % dict_2
        elif not dict_2:
            res_err = "Dict_2 is empty, dict_1 is %s" % dict_1
        
                
    return res_err
    
def _compare_ip_detail_cfg(ip_cfg_1, ip_cfg_2, ip_version = const.IPV4):
    err_msg = ''
    if ip_cfg_1.has_key(ip_version) and ip_cfg_2.has_key(ip_version):
        ip_detail_1 = ip_cfg_1[ip_version]
        ip_detail_2 = ip_cfg_2[ip_version]
        
        if ip_version == const.IPV4:
            key_ip_alloc = 'ip_alloc'
        else:
            key_ip_alloc = 'ipv6_alloc'
        
        ip_alloc_1 = ip_detail_1.get(key_ip_alloc)
        ip_alloc_2 = ip_detail_2.get(key_ip_alloc)
      
        if ip_alloc_1 and ip_alloc_2:
            if ip_alloc_1.lower() in ['manual','static'] and ip_alloc_2.lower() in ['manual','static']:  #@author: yu.yanan @attention: ipv4:static,ipv6:manual @since: 2014-6-26
                    #Compare ip details information if ip mode is manual/static.
                    err_msg = compare_dict_key_value(ip_detail_1, ip_detail_2,pass_items = ['ip_alloc'])
            elif ip_alloc_1.lower() == ip_alloc_2.lower():  #@author: yu.yanan @attention: ipv4:static,ipv6:manual @since: 2014-6-26
                pass
            else:
                err_msg = "ip_alloc is different. dict_1: %s, dict_2: %s" % (ip_alloc_1, ip_alloc_2)
        else:
            err_msg = "ip_alloc is different. dict_1: %s, dict_2: %s" % (ip_alloc_1, ip_alloc_2)
        
    else:
        if not ip_cfg_1.has_key(ip_version):
            err_msg = 'No ip configuration in dict_1: %s' % ip_cfg_1
        else:
            err_msg = 'No ip configuration in dict_2: %s' % ip_cfg_2
            
    return err_msg