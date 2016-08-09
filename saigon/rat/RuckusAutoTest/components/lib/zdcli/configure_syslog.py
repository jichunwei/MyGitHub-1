"""
This module include the functions support to configure the ZD syslog options under cli:
    ruckus# config
    ruckus(config)# system
    ruckus(config-sys)# syslog
    ruckus(config-sys-syslog)# help
    
    Commands available:
      server <IP-ADDR>     Sets the syslog server address.
      facility <FACILITY NAME>
                           Sets the syslog facility name (local0 - local7).
      priority <PRIORITY LEVEL>
                           Sets the syslog priority level (emerg, alert, crit, err, warning, notice, info, debug).
      ap-facility <FACILITY NAME>
                           Sets the AP syslog facility name (local0 - local7).
      ap-priority <PRIORITY LEVEL>
                           Sets the AP syslog priority level (emerg, alert, crit, err, warning, notice, info, debug).
    ruckus(config-sys-syslog)#

@author: An Nguyen, Mar 2013
"""
import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#
# PUBLIC FUNCTIONS
#

def disable_syslog(zdcli):
    return _disable_syslog(zdcli)

def config_syslog(zdcli, **kwargs):
    params = {'enable_remote_syslog': True}
    params.update(kwargs)
    if params['enable_remote_syslog']:
        return _config_syslog(zdcli, **kwargs)
    else:
        return _disable_syslog(zdcli)

def get_syslog_config(zdcli):
    return _get_syslog_config(zdcli)

#
# PRIVATE FUNCTIONS
#

def _disable_syslog(zdcli):
    """
    """
    cmd_block = 'system\nno syslog\nend\n'
    logging.info('[ZD CLI] Disable ZD Syslog option')
    return zdcli.do_cfg(cmd_block, raw = True)

def _config_syslog(zdcli, **kwargs):
    """
    Base on the parameter the suitable commands will be call
    """
    params = {'remote_syslog_ip': None,
              'zd_facility_name': None,
              'zd_priority_level': None,
              'ap_facility_name': None,
              'ap_priority_level': None}
    params.update(kwargs)
    
    cfg_cmds = {'remote_syslog_ip': 'server %s',
                'zd_facility_name': 'facility %s',
                'zd_priority_level': 'priority %s',
                'ap_facility_name': 'ap-facility %s',
                'ap_priority_level': 'ap-priority %s',}
    
    cmd_block = 'system\nsyslog\n'
    save_block = 'end\n'
    
    for key in ['remote_syslog_ip', 'zd_facility_name', 'zd_priority_level', 'ap_facility_name', 'ap_priority_level']:
        if params.get(key) is not None:
            cmd_block += cfg_cmds[key] % params[key] + '\n'
    cmd_block += save_block
    
    logging.info('[ZD CLI] Configure the syslog %s by the set of commands %s' % (params, cmd_block))
    res = zdcli.do_cfg(cmd_block, raw = True)
    
    return res  

def _get_syslog_config(zdcli):
    syslog_cfg = {}
    res = zdcli.do_cfg_show('system\n')
    cfg = output.parse(res).get('Log')
    if not cfg:
        logging.debug('[ZD CLI] Can not get the syslog config under system info %s' %res)
    else:
        syslog_cfg['enable_remote_syslog'] = True if cfg.get('Status') == 'Enabled' else False
        syslog_cfg['remote_syslog_ip'] = cfg.get('Address')
        syslog_cfg['zd_facility_name'] = cfg.get('Facility')
        syslog_cfg['zd_priority_level'] = cfg.get('Priority')
        syslog_cfg['ap_facility_name'] = cfg.get('AP Facility')
        syslog_cfg['ap_priority_level'] = cfg.get('AP Priority')
        
    return syslog_cfg
