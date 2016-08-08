"""
This module supports to do the functions in the shell mode of ZoneDirectorCLI:

"""

import logging
import time
import re

########################################################################################
# PUBLIC SECSSION
########################################################################################

def get_dpsk_list(zdcli):
    """
    Get the dpsk records by reading the /etc/airespider/dpsk-list.xml file under zone director shell mode
    Return the decoded passphrase if decode is True
    """
    cmd = 'cat /etc/airespider/dpsk-list.xml'
    info = zdcli.do_shell_cmd(cmd)
    if "No such file or directory" in info:
        logging.debug('[Please take note]: %s' % info)
    
    return _read_dpsks_record(info)

def get_dhcp_lease_time_by_mac(zdcli, mac):
    """
    @author: Jane.Guo
    @since: 2013-5-10 for Force DHCP feature
    wlaninfo -s 00:24:d7:96:86:18
    ruckus$ wlaninfo --all-sta-cache-hash
    """
    lease_time = {}
    lease_time['errmsg'] = ""
    lease_time['current'] = _get_dhcp_lease_time_by_mac(zdcli, mac)
    
    sta_list = _get_dhcp_lease_time_list(zdcli)
    for sta in sta_list:
        if sta['sta_mac'] == mac.lower():
            lease_time['init'] = sta['dhcp_lease_time']
            logging.info("Get init lease time is %s" % lease_time['init'])
            break
    
    if not lease_time.has_key('current'):
        lease_time['errmsg'] = "Get dhcp lease time by mac fail,mac is "+ str(mac)
    if not lease_time.has_key('init'):
        lease_time['errmsg'] = lease_time['errmsg'] + "Get dhcp lease time by list fail,mac is "+ str(mac)
        lease_time['errmsg'] = lease_time['errmsg'] + " station list is" + str(sta_list)
    return lease_time
    
#    column_name_list = info[0].split()
#    column_name_list.remove('name')
#    logging.info(column_name_list)
#    sta_info = [x.split() for x in info if re.search('([0-9a-f]{8})', x)]
#    logging.info(sta_info)
#    sta_list = []
#    for sta in sta_info:
#        sta_one = {}
#        #need to consider:Windows       (Windows 7/Vista     ) 
#        for idx in range (0, len(sta)):
#            if re.match('.*\(.*',sta[idx]): 
#                sta[idx] = str(sta[idx])+ str(sta[idx+1]) + str(sta[idx+2])             
#                sta.pop(idx+1)
#                sta.pop(idx+1)
#                break
#                
#        logging.info(sta)       
#        for idx in range (0, len(sta)):
#            sta_one[column_name_list[idx].lower()] = sta[idx]
#        sta_list.append(dict(sta_one))
#  
#    logging.info(sta_list)
    
    
#    if "No such file or directory" in info:
#        logging.debug('[Please take note]: %s' % info)
#    
#    return _read_dpsks_record(info)

def get_netstat_info(zdcli):
    """
    return the socket information from zd shell mode by using the command "netstat -na"
    """ 
    return _get_netstat_info(zdcli)

def get_memory_leak_info(zdcli):
    """
    return the memory leak information from zd shell mode
    """
    return _get_memory_leak_info(zdcli)

def get_cpu_using_info(zdcli, **kwargs):
    """
    return the cpu using information from zd shell mode by using the command "top"
    """
    cfg = {'duration': 60}
    cfg.update(kwargs)
    
    return _get_cpu_using_info(zdcli, **cfg)

def kill_process(zdcli,name = 'stamgr'):
    cmd = "killall -9 %s"%name
    zdcli.do_shell_cmd(cmd) 

def enable_all_debug_log(zdcli):
    """
    enable all debug log on zd by command:
        apmgrinfo -d 7 -m all
    """
    cmd = 'apmgrinfo -d 7 -m all'
    return zdcli.do_shell_cmd(cmd)

########################################################################################
# PRIVATE SECSSION
########################################################################################

def _get_dhcp_lease_time_by_mac(zdcli, mac):
    """
    @author: Jane.Guo
    @since: 2013-5-10 for Force DHCP feature
    wlaninfo -s 00:24:d7:96:86:18
    """    
    cmd = 'wlaninfo -s ' + str(mac)
    info = zdcli.do_shell_cmd(cmd)
    info = info.split("\r\n")[1:-1]
    
    for idx in range(0,len(info)): 
        lease_time = re.match('.*DHCP lease time =\s*(\d*)\s*.*',info[idx])
        if lease_time:
            logging.info("Get lease time is %s" % lease_time.group(1))
            break     
    return lease_time.group(1)

def _get_dhcp_lease_time_list(zdcli):
    """
    @author: Jane.Guo
    @since: 2013-5-10 for Force DHCP feature
    ruckus$ wlaninfo --all-sta-cache-hash
     mac                time                  OS type                           host name    DHCP_IP     DHCP_Lease_Time  VLAN  XID
 00:24:d7:96:86:18 00000001748:369728020 Windows       (Windows 7/Vista     ) RS-STA 192.168.0.112 120 1 538ce472
*** Total STA Entries: 1:1 ***

    """   
    cmd = 'wlaninfo --all-sta-cache-hash' 
    info = zdcli.do_shell_cmd(cmd)
    info = info.split('\r\n')
    
    sta_list = []
    for idx in range(0,len(info)):
        if re.search('([0-9a-fA-F:]{17})', info[idx]):
#            import pdb
#            pdb.set_trace()
            sta = {}
            sta_mac = re.search('([0-9a-fA-F:]{17})', info[idx])
            dhcp_lease_time = re.search('[0-9.]{7,15}\s(\d*)\s', info[idx])
            sta['sta_mac'] = sta_mac.group(1)
            sta['dhcp_lease_time'] = dhcp_lease_time.group(1)
            sta_list.append(dict(sta))
                    
    return sta_list

def _read_single_dpsk_info(raw_info = ''):
    """
    """
    raw_info = raw_info.strip().split()
    dpsk_info = {}
    for pair in raw_info:
        if '=' in pair:
            temp = pair.strip().split('=')
            dpsk_info[temp[0].strip()] = temp[1].strip('"').strip('\'')
                
    return dpsk_info

def _read_dpsks_record(record):
    """
    """
    record = record.strip().split('\r\n')
    dpsks_info = {}
    for line in record:
        dpsk_info = _read_single_dpsk_info(line)
        if dpsk_info:
            dpsks_info[dpsk_info['user']] = dict(dpsk_info)
    
    return dpsks_info

def _get_cpu_using_info(zdcli, **kwargs):
    """
    return the cpu using information from zd shell mode by using the command "top"
    """
    cfg = {'duration': 60}
    cfg.update(kwargs)
    
    result = {'raw': '',
              'detail_set': []}
   
    cmd = 'top'
    
    mem_re = '.*Mem:?\s*(\d+)K\s*used,?\s*(\d+)K\s*free,?\s*(\d+)K\s*shrd,?\s*(\d+)K\s*buff,?\s*(\d+)K\s*cached'
    mem_keys = ['used', 'free', 'shrd', 'buff', 'cached']
    cpu_re = 'CPU:?\s*(\d+)%\s*usr\s*(\d+)%\s*sys\s*(\d)%\s*nic\s*(\d+)%\s*idle\s*(\d+)%\s*io\s*(\d+)%\s*irq\s*(\d+)%\s*sirq'
    cpu_keys = ['usr', 'sys', 'nic', 'idle', 'io', 'irq', 'sirq']
    load_re = 'Load average:?\s(.*)'
    thread_re = '\s*(\d+)\s+(\d+)\s+(\w+)\s+(\w+\s+.+)\s+(\d+)\s+(\d+)%\s+(\d+)%\s+(.*)'
    thread_keys = ['pid', 'ppid', 'user', 'stat', 'vsz', 'mem', 'cpu', 'command']
    
    # go to shell mode
    zdcli.do_cmd(zdcli.conf['shell_key'])
    time.sleep(1)
    # send the "top" command to catch the CPU using info
    try:
        zdcli.zdcli.write("%s \n" % cmd)
        time.sleep(cfg['duration'])
        info = zdcli.do_cmd('\x03 \n')
    # exit
    finally:
        zdcli.zdcli.write('exit \n')
        time.sleep(5)
        zdcli.re_login()
    
    result['raw'] = info
    
    info = info.split('\r\x1b[H\x1b[J')
        
    for detail in info:
        cpu_info = {'mem_info': {},
                    'cpu_info': {},
                    'load_average': '',
                    'thread_info': {}}
        detail_info = detail.split('\r\n')
        for line in detail_info:
            if re.match(mem_re, line):
                mem_vals = re.findall(mem_re, line.strip())[0] 
                cpu_info['mem_info'] = dict(zip(mem_keys, mem_vals))
            elif re.match(cpu_re, line):
                cpu_vals = re.findall(cpu_re, line.strip())[0] 
                cpu_info['cpu_info'] = dict(zip(cpu_keys, cpu_vals))
            elif re.match(load_re, line):
                load_val = re.findall(load_re, line.strip())[0] 
                cpu_info['load_average'] = load_val
            elif re.match(thread_re, line):
                thread_vals = re.findall(thread_re, line.strip())[0]
                cpu_info['thread_info'][thread_vals[0]] = dict(zip(thread_keys, thread_vals))
        
        result['detail_set'].append(cpu_info)
    
    return result

def _get_memory_leak_info(zdcli):
    """
    return the memory leak information from zd shell mode by using command "cat /proc/meminfo"
    """
    mem_info = {'raw': '',
                'detail': {}}
    cmd = 'cat /proc/meminfo'
    info = zdcli.do_shell_cmd(cmd)
    mem_info['raw'] = info
    
    info = info.split('\r\n')
    for line in info:
        if not ':' in line:
            continue
        line_info = line.split(':')
        mem_info['detail'][line_info[0].lower()] = line_info[1].lower().strip('kb').strip()
    
    return mem_info

def _get_netstat_info(zdcli):
    """
    return the socket information from zd shell mode by command "netstat -na"
    """ 
    netstat_info = {'raw': '',
                    'active_internet_connections': [],
                    'active_unix_domain_sockets': []}
    
    conn_re = '(\w+)\s+(\d+)\s+(\d+)\s+([\w\d:\.\*]+)\s+([\w\d:\.\*]+)\s+(\w+)'
    conn_keys = ['proto', 'recv-q', 'send-q', 'local_address', 'foreign_address', 'state']
    socket_re = '(\w+)\s+(\d+)\s+\[(.+)\]\s+(\w+)\s+(\w*)\s+(\d+)\s+(.*)'
    socket_keys = ['proto', 'refcnt', 'flags', 'type', 'state', 'i-note', 'path']
    
    cmd = 'netstat -na'
    info = zdcli.do_shell_cmd(cmd)
    netstat_info['raw'] = info
    
    info = info.split('\r\n')
    for line in info:
        if re.match(conn_re, line):
            conn_vals = re.findall(conn_re, line)[0]
            netstat_info['active_internet_connections'].append(dict(zip(conn_keys, conn_vals)))
        elif re.match(socket_re, line):
            socket_vals = re.findall(socket_re, line)[0]
            netstat_info['active_unix_domain_sockets'].append(dict(zip(socket_keys, socket_vals)))
    
    return netstat_info
    
