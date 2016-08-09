"""
This module supports to do the functions in the debug mode of ZDCLI:

Commands available: (TBD)
  help                 Shows available commands.
  history              Shows a list of previously run commands.
  quit                 Exits the debug context.
  fw_upgrade           Upgrades the controller's firmware.
  delete-station {MAC} Deauthorizes a station.
  restart-ap {MAC}     Restarts a device.
  wlaninfo             Configures and enables debugging of WLAN service settings.
  show ap              Displays a list of all approved devices.
  show station         Displays a list of all connected stations (or clients).
  ps                   Displays information about all processes that are running (ps -aux).
  save_debug_info {IP-ADDR} {FILE-NAME} Saves debug information.
  remote_ap_cli        Excute AP CLI command in remote AP.
"""

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

go_to_debug_cmd = 'debug'
debug_mode_prompt = 'ruckus\(debug\)#'
remote_ap_cli_cmd = 'remote_ap_cli'
sniffer_cmd_in_ap_cli = 'set capture'

########################################################################################
# PUBLIC SECSSION
########################################################################################

def fw_upgrade(zdcli,  **kwargs):
    if zdcli.next_gen_cli:
        _goto_debug_mode(zdcli)
    else:
        zdcli.do_cmd(zdcli.conf['shell_key'], zdcli.shell_prompt)
    
    zdcli._fw_upgrade(**kwargs)

def do_debug(zdcli, cmd, **kwargs):
    try:
        return _do_debug(zdcli, cmd, **kwargs)
    except:
        zdcli.re_login()
        return _do_debug(zdcli, cmd, **kwargs)

def ps(zdcli, **kwargs):
    res = do_debug(zdcli, 'ps', **kwargs)
    res = _read_ps(res)
    return res

def wlaninfo(zdcli, option, **kwargs):
    res = do_debug(zdcli, 'wlaninfo %s' % option, **kwargs)
    info = output.parse(res)
    return {'info': info, 'raw': res}

def delete_station(zdcli, mac, **kwargs):
    res = do_debug(zdcli, 'delete-station %s' % mac, **kwargs)
    if '' in res: return 1, res
    else: return 0, res

def restart_ap(zdcli, mac, **kwargs):
    res = do_debug(zdcli, 'restart-ap %s' % mac, **kwargs)
    if 'The command was executed successfully' in res: return 1, res
    else: return 0, res

def save_debug_info(zdcli, tftp_server_ip, **kwargs):
    name = 'debug_info_%s.txt' % ''
    res = do_debug(zdcli, 'save_debug_info %s %s' % (tftp_server_ip, name), **kwargs)
    if '' in res: return 1, res
    else: return 0, res

def save_config(zdcli, tftp_server_ip, **kwargs):
    name = 'debug_info_%s.txt' % ''
    res = do_debug(zdcli, 'save_debug_info %s %s' % (tftp_server_ip, name), **kwargs)
    if '' in res: return 1, res
    else: return 0, res
        
def get_ap_info_orderby_mac(zdcli, **kwargs):
    tcfg=dict(break_if_error=False)
    tcfg.update(kwargs)
    res = do_debug(zdcli, 'show ap')
    ap_dict_by_id = output.parse(res,break_if_error=tcfg['break_if_error'])
    ap_dict_by_mac = {}
    for ap in ap_dict_by_id['AP']['ID'].values():
        ap_dict_by_mac[ap['MAC Address']] = ap
    return ap_dict_by_mac

def do_remote_ap_cli_cmd(zdcli, **kwargs):
    '''
    usage: remote_ap_cli [-q] {-a ap_mac | -A } "cmd arg1 arg2 .."
       excute AP CLI command in remote AP
       -A ; all connected AP's
       -q ; do not show result
       cmd ; Ruckus CLI, e.g. "get station wlan0 list"
    '''
    cfg = {'all_aps': False,
           'ap_mac_list': [],
           'ap_cli_cmd': '',
           'time_out': 10,
           }
    cfg.update(kwargs)
    
    _goto_debug_mode(zdcli)
    cmd = remote_ap_cli_cmd
    if cfg['all_aps']:
        cmd = "%s -A '%s'" % (cmd, cfg['ap_cli_cmd'])
        res = zdcli.do_cmd(cmd, debug_mode_prompt, cfg['time_out'])
    
    else:
        res = {}
        for mac in cfg['ap_mac_list']:
            cmd = "%s -a %s '%s'" % (cmd, mac, cfg['ap_cli_cmd'])
            res[mac] = zdcli.do_cmd(cmd, debug_mode_prompt, cfg['time_out'])
    
    _exit_debug_mode(zdcli)
    
    return res

def start_capture_in_aps(zdcli, **kwargs):
    cfg = {'all_aps': False,
           'ap_mac_list': [],
           'wlan_name': '',
           'mode': '',
           'filter': '',
           'time_out': 10,
           }
    cfg.update(kwargs)
    
    ap_cli_cmd = '%s %s %s' % (sniffer_cmd_in_ap_cli, cfg['wlan_name'], cfg['mode'])
    if cfg['filter']:
        ap_cli_cmd = '%s-%s' % (ap_cli_cmd, cfg['filter'])
    
    cfg['ap_cli_cmd'] = ap_cli_cmd
    do_remote_ap_cli_cmd(zdcli, **cfg)
    
def stop_capture_in_aps(zdcli, **kwargs):
    cfg = {'all_aps': False,
           'ap_mac_list': [],
           'wlan_name': '',
           'time_out': 10,
           }
    cfg.update(kwargs)
    
    ap_cli_cmd = '%s %s idle' % (sniffer_cmd_in_ap_cli, cfg['wlan_name'])
    cfg['ap_cli_cmd'] = ap_cli_cmd
    do_remote_ap_cli_cmd(zdcli, **cfg)
    
########################################################################################
# PRIVATE SECSSION
########################################################################################

def _goto_debug_mode(zdcli):
    zdcli.position_at_priv_exec_mode()
    zdcli.do_cmd(go_to_debug_cmd, debug_mode_prompt)

def _exit_debug_mode(zdcli):
    #zdcli.zdcli.write('quit\n')
    zdcli.do_cmd('quit')
    
def _do_debug(zdcli, cmd, **kwargs):
    option = {'time_out': 10}
    if kwargs: option.update(kwargs)
    _goto_debug_mode(zdcli)
    res = zdcli.do_cmd(cmd, debug_mode_prompt, option['time_out'])
    _exit_debug_mode(zdcli)
    
    return res

def _read_ps(info):
    ps = info.split('\r\n')
    ps = [line.strip() for line in ps]
    
    return {'ps': ps,
            'raw': info}