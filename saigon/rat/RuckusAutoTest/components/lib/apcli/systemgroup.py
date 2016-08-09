# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library support to execute the command of system group:

"""

import re
import time
from RuckusAutoTest.common.Ratutils import ping
import logging
#
def set_director(ap, pri_zd_addr = "", sec_zd_addr = "", zdcode = ""):
    '''
    Set ap director information.
    is_dns: False if both ip1 and ip2 are ip address; True if one of them is domain name.        
    #the primary address is longer than 64
    #the secondary address is longer than 64
    '''
    if pri_zd_addr or sec_zd_addr:
        res = ap.do_cmd('set director addr %s %s' % (pri_zd_addr, sec_zd_addr))
    elif zdcode:
        res = ap.do_cmd('set director zdcode %s' % zdcode)
    else:
        res = ap.do_cmd('set director addr del')        
        res = ap.do_cmd('set director zdcode del')
    
    import logging
    logging.debug("Result: %s" % res)
    if 'error' in res.lower():
        return res

def get_director(ap, **kwargs):
    """
    """
    cmd = "get director"
    info = ap.do_cmd(cmd)
    dir_info = {}
    for line in info.split("\r\n"):
        if ": " in line:
            a = line.split(": ")
            key = a[0].strip().replace(" ", "_")
            value = a[1].strip().strip(",").split(" / ") if " / " in a[1] else a[1].strip().strip(",")
            dir_info[key.lower()] = value
    
    return dir_info

def set_factory(ap):
    """
    """
    cmd = "set factory"
    info = ap.do_cmd(cmd)
    if 'OK' not in info:
        return False,'ap set factory failed'
    cmd = "reboot"
    info = ap.do_cmd(cmd)
    if 'OK' not in info:
        return False,'reboot ap failed'
    time_out=600
    start_time=time.time()
    while True:
        if time.time() - start_time > time_out:
            raise Exception("Error: Timeout when ap reboot")
        res = ping(ap.ip_addr)
        if res.find("Timeout") != -1:
            logging.info('ap is rebooting')
            break
        
    while True:
        if time.time() - start_time > time_out:
            raise Exception("Error: Timeout when ap reboot")
        res = ping(ap.ip_addr)
        if res.find("Timeout") == -1:
            logging.info('ap reboot success')
            break
        time.sleep(2)
    
    return True,'ap set factory and reboot successfully'

def get_ip_mode(ap, interface, **kwargs):
    """
    """
    cmd = "get ipmode %s" % interface
    info = ap.do_cmd(cmd)
    rex = '[Mode|mode] ?: ?(\w+)'
    ipmode = re.findall(rex, info)[0]
    
    return ipmode.lower()
    
def get_ip_settings(ap, interface, **kwargs):
    """
    """
    ip_mode = get_ip_mode(ap, interface)
    ip_settings = {'ip_mode': ip_mode}
    ip_modes = ['ipv4', 'ipv6']
    if ip_mode in ip_modes:
        ip_settings[ip_mode] = _get_ip_setting(ap, interface, ip_mode) 
    elif ip_mode == 'dual':
        for mode in ip_modes:
            ip_settings[mode] = _get_ip_setting(ap, interface, mode)
    
    return ip_settings
    
def _get_ip_setting(ap, interface, ip_mode='ipv6', **kwargs):
    ip_setting = {}
    if ip_mode == 'ipv6':
        cmd ='get ipv6addr %s' % interface
        info = ap.do_cmd(cmd)
        for line in info.split('\n'):
            line = line.strip().strip(',')
            if ': ' in line:
                a = line.split(': ')
                key = a[0].strip().replace(' ', '_').lower()
                value = a[1].strip()
                ip_setting[key] = value
                
    elif ip_mode == 'ipv4':
        cmd = 'get ipaddr %s' % interface
        info = ap.do_cmd(cmd)
        ip_setting['ip'] = re.search("IP: [0-9. ]+Netmask", info).group().split()[1]
        ip_setting['netmask'] = re.search("Netmask [0-9. ]+", info).group().split()[1]
        ip_setting['gateway'] = re.search("Gateway [0-9. ]+", info).group().split()[1]
    
    return ip_setting

def set_zd_ip(ap,ip_addr):
    cmd="set director addr '%s'"%ip_addr
    info = ap.do_cmd(cmd)
    if 'OK' not in info:
        return False,'ap set zd ip failed'
    return True,'set zd ip to %s success'%ip_addr

def exec_support(ap):
    """
    Execute support command in AP CLI.
    """
    cmd="support"
    info = ap.do_cmd(cmd)
    if 'OK' not in info:
        return False,'support command failed'
    
    return True,'support command success'

def exec_command(ap,cmd_test,cmd_pmt="",force_ssh=False,expect_value=''):
    """
    Execute  command in AP CLI.
    """
    cmd = cmd_test
    if cmd_pmt == 'shell':
        ap.goto_shell(force_ssh=force_ssh)
    if cmd_pmt == 'shell':
        info = ap.do_cmd(cmd,prompt='#',force_ssh=force_ssh)
    else:
        info = ap.do_cmd(cmd,force_ssh=force_ssh)
    if cmd_pmt == 'shell':
        ap.exit_shell(force_ssh=force_ssh)
    if expect_value != '' and expect_value in info:
        return True,'Command  exec success'
    if 'OK' not in info:
        return False,'Command exec failed,%s' % info
    
    return True,'Command  exec success'

def set_mesh_uplink_selection(ap, type='default'):
    """
        Set mesh uplink selection and check
        @author: Jane.Guo
        @since: 2013-11-15

        Set Mesh Uplink Selection
        rkscli: set mesh-uplink-selection rssi/default
        Get Mesh Uplink Selection
        rkscli: get mesh-uplink-selection : get mesh-uplink-selection
        rssi (RSSI based uplink selection) 
        default (Throughput based uplink selection)
    """
    cmd = 'set mesh-uplink-selection %s' % type
    res1 = ap.do_cmd(cmd)
    
    cmd = 'get mesh-uplink-selection'
    res2 = ap.do_cmd(cmd)
    if re.findall(type, res2):
        return ""
    else:
        return "Set and check mesh uplink selection fail: %s, %s" % (res1,res2)