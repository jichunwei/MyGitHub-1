'''
This module define library of Smart Redundancy information
by Louis Lou (louis.lou@ruckuswireless.com)   
'''
import time
import logging
import re
from string import Template

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

SR_SHOW = """
system
smart-redundancy
show
"""
#@author:chen.tao since:2013-10-28 to adapt to the cli behavior change
SET_SR_PEER_IP = """
system
    smart-redundancy
        peer-addr $ip_addr
"""
#@author:chen.tao since:2013-10-28 to adapt to the cli behavior change
SET_SR_SECRET = """
system
    smart-redundancy
        secret $secret
"""

SET_NO_SR ='''
system
    no smart-redundancy
'''

SET_SR_CLUSTER_TIMER = '''
system
    smart-redundancy
    cluster-timer $t_min $t_day
'''
def set_no_sr(zdcli):
    cmd = SET_NO_SR
    logging.info('[ZDCLI:%s]: Disable S.R' %(zdcli.ip_addr))
    _do_excute_cmd(zdcli,cmd)

def set_sr_peer_ip(zdcli,conf):
    cmd = Template(SET_SR_PEER_IP).substitute(dict(ip_addr = conf['peer_ip_addr']))
    
    logging.info("[ZDCLI:%s]:Set S.R peer IP address[%s]" %(zdcli.ip_addr,conf['peer_ip_addr']))
    _do_excute_cmd(zdcli,cmd)
    
    
def set_sr_secret(zdcli,conf):
    cmd = Template(SET_SR_SECRET).substitute(dict(secret = conf['secret']))
    
    logging.info("[ZDCLI:%s]:Set S.R Secret:[%s]" %(zdcli.ip_addr,conf['secret']))
    _do_excute_cmd(zdcli,cmd)
    
    
def show_sr_info(zdcli):
    cmd_block = SR_SHOW
    logging.info("======config-sys-smart-redundancy)#show ==========")

    sr_info = zdcli.do_cfg_show(cmd_block)
    
    logging.info('The result\n:%s',sr_info)
    sr_info_on_cli = output.parse(sr_info)
    
    return sr_info_on_cli

def verify_sr_info(sr_cli,sr_zd):
    '''
    {'Smart Redundancy': {'Status': 'Enabled', 'Peer IP Address': '192.168.0.3', 'Shared Secret': 'testing'}, 'ruckus(config-sys-smart-redundancy)#': ''}

9.5.2.0
ruckus(config-sys-smart-redundancy)# show
Smart Redundancy:
  Status= Disabled
  Peer IP/IPv6 Address=
  Shared Secret=

9.7.0.0.35
ruckus(config-sys-smart-redundancy)# show
Smart Redundancy:
  Status= Enabled
  Local Connect Status= Disconnected
  Peer IP/IPv6 Address= 192.168.0.3
  Peer Connect Status = Disconnected
  Shared Secret= testing

    '''
    sr_info_cli = sr_cli['Smart Redundancy']
    
    #@author: Jane.Guo  2013-06-04 Add 2 check keys and modify one key.
    for keys in sr_info_cli.keys():
        if not sr_zd.has_key(keys):
            continue
        if not re.match(sr_info_cli[keys].lower(),sr_zd.get(keys).lower()):
            return False
        
    return True
    
def verify_no_sr_info(sr_cli):
    sr_info_cli = sr_cli['Smart Redundancy']
    
    #@author: Jane.Guo  2013-06-04 modify key
    if sr_info_cli.get('Peer IP Address') or sr_info_cli.get('Peer IP/IPv6 Address'):
        return False
    if sr_info_cli['Shared Secret']:
        return False
    
    if sr_info_cli['Status'] == 'Disabled':
        logging.info('Smart Redundancy Status is Disabled')
        return True
    else:
        return False
    
def _do_excute_cmd(zdcli,cmd):
    try:
        time.sleep(1)
        logging.info("CLI is: %s" %cmd)
        zdcli.do_cfg(cmd)
        time.sleep(2)
    except Exception,ex:
        errmsg = ex.message
        raise Exception(errmsg)

def set_sr_cluster_timer(zdcli,conf):
    cmd = Template(SET_SR_CLUSTER_TIMER).substitute(dict(t_min = conf['t_min'], t_day = conf['t_day']))
    
    logging.info("[ZDCLI:%s]:Set SR cluster timer[%s minute(s), %s day(s)]" %(zdcli.ip_addr,conf['t_min'],conf['t_day']))
    _do_excute_cmd(zdcli,cmd)

def get_sr_pool_info(zdcli):
    """
    Current Smart Redundancy Status= Normal
    Smart Redundancy Pool License= 75
    
    Current Smart Redundancy Status= Degraded
    (Peer ZD disconnected)
    Smart Redundancy Pool License= 75
    Smart Redundancy Pool is valid for= 60 days
    
    Current Smart Redundancy Status= Invalid
    Smart Redundancy Pool License= 0

    """
    sr_info = show_sr_info(zdcli)
    status = sr_info['Smart Redundancy'].get('Current Smart Redundancy Status')
    srp = sr_info['Smart Redundancy'].get('Smart Redundancy Pool License')
    valid_day = sr_info['Smart Redundancy'].get('Smart Redundancy Pool is valid for')
    return dict(status = status, srp = srp,valid_day = valid_day )