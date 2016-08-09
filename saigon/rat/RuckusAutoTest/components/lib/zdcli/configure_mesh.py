# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This module supports to do the functions under ruckus(config-mesh)# mode of ZDCLI:

Commands available:
  help                 Shows available commands.
  history              Shows a list of previously run commands.
  abort                Exits the config-mesh context without saving changes.
  end                  Saves changes, and then exits the config-mesh context.
  exit                 Saves changes, and then exits the config-mesh context.
  quit                 Exits the config-mesh context without saving changes.
  no detect-hops       Disables Mesh hop count detection.
  no detect-fanout     Disables Mesh downlinks detection.
  hops-warn-threshold {NUMBER} Enter Mesh hop count threshold.
  fan-out-threshold {NUMBER} Enter Mesh downlinks threshold.
  ssid {WORD/SSID}     Sets Mesh SSID.
  passphrase {WORD}    Sets Mesh pass phrase.
  show                 Display Mesh settings.

"""

from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components.lib.apcli.cli_regex import SUCCESS_CMD_MSG
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#
# GLOBAL DEFINATION
#

go_to_config_cmd = 'config'
go_to_config_mesh_cmd = 'mesh'
config_mesh_mode_prompt = 'ruckus\(config-mesh\)#'

setting_success_msg = SUCCESS_CMD_MSG

########################################################################################
# PUBLIC SECSSION
########################################################################################

def config_mesh(zdcli,  **kwargs):
    cfg = {}
    if kwargs: cfg.update(kwargs)
    
    try:
        _config_mesh(zdcli, **cfg)
    except Exception, e:
        test_mode = zdcli.current_prompt
        action = 'exception'
        logging.log_debug(test_mode, action, '%s' % e.message)
        logging.log_debug(test_mode, '', 'Re connect to device and try to set the configuration 1 more time.')
        zdcli.re_login()
        _config_mesh(zdcli, **cfg)


def get_mesh_info(zdcli):
    res = zdcli.do_show('mesh info')
    res = output.parse(res)
    if not res.has_key('Mesh Settings'):
        raise Exception, 'Can not get the mesh setting'
    
    mesh_cfg = {}
    for key in res['Mesh Settings'].keys():
        mesh_cfg[key.lower().replace(' ', '_')] = res['Mesh Settings'][key]
    
    mesh_cfg['mesh_hop_detection'] = mesh_cfg['mesh_hop_detection']['Status']
    mesh_cfg['mesh_downlinks_detection'] = mesh_cfg['mesh_downlinks_detection']['Status']

    return mesh_cfg

########################################################################################
# PRIVATE SECSSION
########################################################################################

def _goto_config_mesh_mode(zdcli):
    zdcli.do_cmd(go_to_config_cmd)
    zdcli.do_cmd(go_to_config_mesh_cmd, config_mesh_mode_prompt)

def _excute_setting(zdcli, cmd):
    test_mode = zdcli.current_prompt
    action = cmd
    try:
        rx = zdcli.do_cmd(cmd, config_mesh_mode_prompt)
    except Exception, e:
        print e.message
        logging.log_debug(test_mode, action, e.message, 2)
        
    if setting_success_msg not in rx:
        print rx
        logging.log_debug(test_mode, action, rx, 2)
    else:
        logging.log_info(test_mode, action, rx)

def _set_ssid(zdcli, ssid):
    cmd = 'ssid "%s"' % ssid
    
    _excute_setting(zdcli, cmd)
        
def _set_passphrase(zdcli, passphrase):
    cmd = 'passphrase "%s"' % passphrase
    
    _excute_setting(zdcli, cmd)

def _set_hops_warn_threshold(zdcli, threshold):
    cmd = 'hops-warn-threshold %s' % threshold
    
    _excute_setting(zdcli, cmd)

def _set_fan_out_threshold(zdcli, threshold):
    cmd = 'fan-out-threshold %s' % threshold
    
    _excute_setting(zdcli, cmd)

def _disable_detect_hops(zdcli):
    cmd = 'no detect-hops'
    
    _excute_setting(zdcli, cmd)

def _disable_detect_fanout(zdcli):
    cmd = 'no detect-fanout'
    
    _excute_setting(zdcli, cmd)

def _save_config(zdcli):
    zdcli._back_to_priv_exec_mode('end')

def _config_mesh(zdcli,  **kwargs):
    mesh_conf = {'mesh_downlinks_detection': None,
                 'mesh_downlinks_threshold': None,
                 'mesh_hop_detection': None,
                 'mesh_hops_threshold': None,
                 'mesh_name': None,
                 'mesh_passphrase': None
                 }
    
    obj = 'zd cli'
    action = 'configure mesh'
    
    if kwargs: mesh_conf.update(kwargs)
    if mesh_conf.has_key('mesh_name(essid)'):
        mesh_conf['mesh_name'] = mesh_conf['mesh_name(essid)']
        
    _goto_config_mesh_mode(zdcli)
    
    if mesh_conf['mesh_name'] is not None:
        _set_ssid(zdcli, mesh_conf['mesh_name'])
    
    if mesh_conf['mesh_passphrase'] is not None:
        _set_passphrase(zdcli, mesh_conf['mesh_passphrase'])
    
    if mesh_conf['mesh_hop_detection'] and mesh_conf['mesh_hop_detection'].lower() == 'disabled':
        _disable_detect_hops(zdcli)
    elif mesh_conf['mesh_hop_detection'] and mesh_conf['mesh_hop_detection'].lower() == 'enabled' and mesh_conf['mesh_hops_threshold']:
        _set_hops_warn_threshold(zdcli, mesh_conf['mesh_hops_threshold'])
    
    if mesh_conf['mesh_downlinks_detection'] and mesh_conf['mesh_downlinks_detection'].lower() == 'disabled':
        _disable_detect_fanout(zdcli)
    elif mesh_conf['mesh_downlinks_detection'] and mesh_conf['mesh_downlinks_detection'].lower() == 'enabled' and mesh_conf['mesh_downlinks_threshold']:
        _set_fan_out_threshold(zdcli, mesh_conf['mesh_downlinks_threshold'])
    
    _save_config(zdcli)
