'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.26
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This document is to execute 'show config' and parse the response.
'''

from RuckusAutoTest.common import lib_Constant as CONST
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#=============================================#
#             Access Methods            
#=============================================#

def show_config(zdcli):
    '''
    Get all config info [show config].
    '''
    res = zdcli.do_show('config')
    res = output.parse(res)
    return res

#@author: yin.wenling 2014-9-3 ZF-9706 [Automation ZD3k] show_config.py is too slow to be used if ZD has thousands entries of configurations 
def show_interface(zdcli):
    '''
    system
        interface
            show
    '''
    cmd_block = '''
               system
                   interface
               '''
    res = zdcli.do_cfg_show(cmd_block)
    res = output.parse(res)
    return res

#@author: yin.wenling 2014-9-3 ZF-9706 [Automation ZD3k] show_config.py is too slow to be used if ZD has thousands entries of configurations 
def get_ip_info_via_show_interface(zdcli):
    '''
    Get all ip information from zd cli, ipv4 and ipv6.
    '''
    ip_version_mapping = {'IPv4-Only': CONST.IPV4,
                          'IPv6-Only': CONST.IPV6,
                          'dual stack': CONST.DUAL_STACK,
                          }
    
    mode_mapping = {'Auto': 'auto'}

    config_dict = show_interface(zdcli)

    ipv4_key = 'Device IP Address'
    ipv6_key = 'Device IPv6 Address'
    ip_mode = 'Protocol Mode'

    ip_info_d = {}
    
    #Default ip version is ipv4.
    ip_info_d['ip_version'] = CONST.IPV4
    
    if config_dict.has_key(ip_mode):
        version = config_dict[ip_mode]
        if ip_version_mapping.has_key(version):
            version = ip_version_mapping[version]
        ip_info_d['ip_version'] = version
        
    if ip_info_d['ip_version'] in [CONST.IPV4, CONST.DUAL_STACK]:
        if config_dict.has_key(ipv4_key):
            #ip_info_d.update(config_dict[ipv4_key])
            ip_info_d['ip_addr_mode'] = config_dict[ipv4_key]['Mode']
            if mode_mapping.has_key(ip_info_d['ip_addr_mode']):
                ip_info_d['ip_addr_mode'] = mode_mapping[ip_info_d['ip_addr_mode']]
                
            ip_info_d['ip_addr'] = config_dict[ipv4_key]['IP Address']
            ip_info_d['ip_addr_mask'] = config_dict[ipv4_key]['Netmask']
            ip_info_d['ip_gateway'] = config_dict[ipv4_key]['Gateway Address']
            ip_info_d['ip_pri_dns'] = config_dict[ipv4_key]['Primary DNS']
            ip_info_d['ip_sec_dns'] = config_dict[ipv4_key]['Secondary DNS']
            
    if ip_info_d['ip_version'] in [CONST.IPV6, CONST.DUAL_STACK]:
        if config_dict.has_key(ipv6_key):            
            ip_info_d['ipv6_addr_mode'] = config_dict[ipv6_key]['Mode']
            if mode_mapping.has_key(ip_info_d['ipv6_addr_mode']):
                ip_info_d['ipv6_addr_mode'] = mode_mapping[ip_info_d['ipv6_addr_mode']]
            ip_info_d['ipv6_addr'] = config_dict[ipv6_key]['IPv6 Address']
            ip_info_d['ipv6_prefix_len'] = config_dict[ipv6_key]['Prefix Length']
            ip_info_d['ipv6_gateway'] = config_dict[ipv6_key]['Gateway Address']
            ip_info_d['ipv6_pri_dns'] = config_dict[ipv6_key]['Primary DNS']
            ip_info_d['ipv6_sec_dns'] = config_dict[ipv6_key]['Secondary DNS']

    return ip_info_d
               
def get_ip_info(zdcli):
    '''
    Get all ip information from zd cli, ipv4 and ipv6.
    '''
    ip_version_mapping = {'IPv4-Only': CONST.IPV4,
                          'IPv6-Only': CONST.IPV6,
                          'dual stack': CONST.DUAL_STACK,
                          }
    #@author: Anzuo, for set factory default and zd is ipv6 auto mode
#    mode_mapping = {'Auto': 'auto-configuration'}
    mode_mapping = {'Auto': 'auto'}

    config_dict = show_config(zdcli)

    ipv4_key = 'Device IP Address'
    ipv6_key = 'Device IPv6 Address'
    ip_mode = 'Protocol Mode'

    ip_info_d = {}
    
    #Default ip version is ipv4.
    ip_info_d['ip_version'] = CONST.IPV4
    
    if config_dict.has_key(ip_mode):
        version = config_dict[ip_mode]
        if ip_version_mapping.has_key(version):
            version = ip_version_mapping[version]
        ip_info_d['ip_version'] = version
        
    if ip_info_d['ip_version'] in [CONST.IPV4, CONST.DUAL_STACK]:
        if config_dict.has_key(ipv4_key):
            #ip_info_d.update(config_dict[ipv4_key])
            ip_info_d['ip_addr_mode'] = config_dict[ipv4_key]['Mode']
            if mode_mapping.has_key(ip_info_d['ip_addr_mode']):
                ip_info_d['ip_addr_mode'] = mode_mapping[ip_info_d['ip_addr_mode']]
                
            ip_info_d['ip_addr'] = config_dict[ipv4_key]['IP Address']
            ip_info_d['ip_addr_mask'] = config_dict[ipv4_key]['Netmask']
            ip_info_d['ip_gateway'] = config_dict[ipv4_key]['Gateway Address']
            ip_info_d['ip_pri_dns'] = config_dict[ipv4_key]['Primary DNS']
            ip_info_d['ip_sec_dns'] = config_dict[ipv4_key]['Secondary DNS']
            
    if ip_info_d['ip_version'] in [CONST.IPV6, CONST.DUAL_STACK]:
        if config_dict.has_key(ipv6_key):            
            ip_info_d['ipv6_addr_mode'] = config_dict[ipv6_key]['Mode']
            if mode_mapping.has_key(ip_info_d['ipv6_addr_mode']):
                ip_info_d['ipv6_addr_mode'] = mode_mapping[ip_info_d['ipv6_addr_mode']]
            ip_info_d['ipv6_addr'] = config_dict[ipv6_key]['IPv6 Address']
            ip_info_d['ipv6_prefix_len'] = config_dict[ipv6_key]['Prefix Length']
            ip_info_d['ipv6_gateway'] = config_dict[ipv6_key]['Gateway Address']
            ip_info_d['ipv6_pri_dns'] = config_dict[ipv6_key]['Primary DNS']
            ip_info_d['ipv6_sec_dns'] = config_dict[ipv6_key]['Secondary DNS']

    return ip_info_d