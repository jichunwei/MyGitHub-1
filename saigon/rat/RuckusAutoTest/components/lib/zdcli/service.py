'''
@author: serena.tan@ruckuswireless.com
'''

import logging
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import output_as_dict


CONFIG_SERVICE_CMD_BLOCK = '''
service
'''

ENABLE_SERVICE_SIMPLE_CMD = dict(
    adjust_ap_power = "auto-adjust-ap-power\n",
    adjust_ap_channel = "auto-adjust-ap-channel\n",
    protect_network = "protect-excessive-wireless-request\n",
    report_rogue_device = "rogue-report\n",
    detect_rogue_dhcp = "rogue-dhcp-detection\n",
    detect_aeroscout_rfid = "aeroscout-detection\n",
    )

DISABLE_SERVICE_SIMPLE_CMD_PATTERN = "no %s"

CONFIG_SERVICE_CMD_COMPLEX = dict(
    enable_block_client = "temp-block-auth-failed-client time '%s'\n",
    disable_block_client = "no temp-block-auth-failed-client\n",
    enable_scan_24g = "background-scan radio-2.4-interval '%s'\n",
    disable_scan_24g = "no background-scan radio-2.4\n",
    enable_scan_5g = "background-scan radio-5-interval '%s'\n",
    disable_scan_5g = "no background-scan radio-5\n",
    enable_raps = "raps\n",
    disable_raps = "no raps\n",
    block_all_mcast = "tun-block-mcast all\n",#chentao 2014-03-25
    block_non_well_known_mcast = "tun-block-mcast non-well-known\n"#chentao 2014-03-25
    )

SAVE_CONFIG= "exit\n"

SHOW_SERVICE_INFO = '''
service
'''

SERVICE_INFO_PROMPT = "Services"

SERVICE_CFG_INFO_KEY_MAP = {'adjust_ap_power' : 'Automatically adjust ap radio power',
                            'adjust_ap_channel': 'Automatically adjust ap channel',
                            'protect_network': 'Protect my wireless network against excessive wireless requests',
                            'report_rogue_device': 'Report rogue devices in ZD event log',
                            'detect_rogue_dhcp': 'Rogue DHCP server detection',
                            'detect_aeroscout_rfid': 'AeroScout RFID tag detection',
                            'raps': 'Radio Avoidance Pre-scanning',
                            } 

SERVICE_ADVANCE_CFG_INFO_KEY_MAP = {
                                    #@Author:chen.tao 2014-01-11, to fix ZF-6462
                                    #'block_client': 'Temporarily block wireless clients with repeated authentication failures',
                                    #@Author:chen.tao 2014-01-11, to fix ZF-6462
                                    'scan_24g': 'Run a background scan on 2.4GHz radio',
                                    'scan_5g': 'Run a background scan on 5GHz radio'
                                   }
    
    
#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 
def get_service_info(zdcli):
    '''
    Output: a dict of the service information
    {'AeroScout RFID tag detection': 'Enabled',
     'Automatically adjust ap channel': 'Enabled',
     'Automatically adjust ap radio power': 'Enabled',
     'Channelfly works in 2.4GHz radio': 'Disabled',
     'Channelfly works in 5GHz radio': 'Disabled',
     'Run a background scan on 2.4GHz radio': {'Status': 'Enabled', 
                                               'Time': '20 seconds'},
     'Run a background scan on 5GHz radio': {'Status': 'Enabled', 
                                             'Time': '30 seconds'},
    'Packet Inspection Filter(PIF) uplink process': 'Disabled', 
    'EKHAU settings': {'status': 'Disabled', 
                        'ERC IP': '192.168.1.1', 
                        'ERC port': '8569'}, 
    'Packet Inspection Filter(PIF) rate limit': {'status': 'Disabled'},
    'RAPS': 'Enabled', 
    'Tunnel encryption for tunneled traffic': 'Disabled', 
    'Tunnel Proxy ARP of tunnel WLAN': {'status': 'Disabled', 'ageing time': '0'}, 
    'Block broadcast traffic from network to tunnel except ARP and DHCP': 'Disabled', 
    'Block multicast traffic from network to tunnel': 'Block non well-known', 
    '''
    logging.info("Get the service information from ZD CLI.")
    data = zdcli.do_cfg_show(SHOW_SERVICE_INFO)
    
    service_info = _parse_service_data(data)
    logging.info("The service information in ZD CLI is:\n%s" % pformat(service_info, 4, 120))    
    
    return service_info


def configure_service(zdcli, service_cfg):
    '''
    Input: a dict of the service configuration.
        service_cfg = dict(adjust_ap_power = False,
                            adjust_ap_channel = False,
                            protect_network = False,
                            block_client = False,
                            scan_24g = False,
                            scan_5g = False,
                            report_rogue_device = False,
                            detect_rogue_dhcp = False,
                            detect_aeroscout_rfid = False,
                            block_client_interval = '',
                            scan_24g_interval = '',
                            scan_5g_interval = '',
                           )
    '''     
    conf = dict(adjust_ap_power = None,
                adjust_ap_channel = None,
                protect_network = None,
                block_client = None,
                scan_24g = None,
                scan_5g = None,
                report_rogue_device = None,
                detect_rogue_dhcp = None,
                detect_aeroscout_rfid = None,
                block_client_interval = '',
                scan_24g_interval = '',
                scan_5g_interval = '',
                raps = None,
                )
    conf.update(service_cfg)
    
    logging.info('Configure service in ZD CLI with cfg:\n%s' % pformat(service_cfg, 4, 120))
    value = _set_service(zdcli, conf)
    if not value:
        return (False, 'Fail to configure service in ZD CLI!')
    
    res, msg = _verify_service_cfg_in_cli(zdcli, conf)
    if res:
        return (True, 'Configure service in ZD CLI successfully!')
    
    else:
        return (False, msg)
    

def verify_cli_service_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    logging.info("The service information in ZD GUI is:\n %s" % pformat(gui_info_dict, 4, 120))
    
    expect_info_dict = _define_expect_gui_info(cli_cfg_dict)
    logging.info("The expect service information in ZD GUI is:\n %s" % pformat(expect_info_dict, 4, 120))
    
    res, msg = _expect_is_in_dict(expect_info_dict, gui_info_dict)
    if res:
        return (True, 'The service configuration in CLI is showed correctly in GUI!')
    
    else:
        return (False, msg)


#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 

def _parse_service_data(data):
    data_dict = output_as_dict.parse(data)
    if not data_dict.has_key(SERVICE_INFO_PROMPT):
        raise Exception("The service info in ZD CLI is not correct: %s" % data)
    
    info_dict = data_dict[SERVICE_INFO_PROMPT]

    return info_dict
    
    
def _set_service(zdcli, cfg):  
    cmd_block = _construct_configure_service_cmd_block(cfg)
    logging.info('Configure service with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True


def _verify_service_cfg_in_cli(zdcli, cfg):
    '''
    Input:
        cfg = dict(adjust_ap_power = None,
                    adjust_ap_channel = None,
                    protect_network = None,
                    block_client = None,
                    block_client_interval = '',
                    scan_24g = None,
                    scan_24g_interval = '',
                    scan_5g = None,
                    scan_5g_interval = '',
                    report_rogue_device = None,
                    detect_rogue_dhcp = None,
                    detect_aeroscout_rfid = None,
                    block_client_interval = '',
                    )
    ''' 
    cli_info = get_service_info(zdcli)
    
    expect_info = _define_expect_cli_info(cfg)
    logging.info("The expect service information in ZD CLI is: %s" % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, cli_info)
#
#
def _construct_configure_service_cmd_block(cfg):  
    '''
    Input:
        cfg = dict(adjust_ap_power = None,
                    adjust_ap_channel = None,
                    protect_network = None,
                    block_client = None,
                    block_client_interval = '',
                    scan_24g = None,
                    scan_24g_interval = '',
                    scan_5g = None,
                    scan_5g_interval = '',
                    report_rogue_device = None,
                    detect_rogue_dhcp = None,
                    detect_aeroscout_rfid = None,
                    block_client_interval = '',
                    )
    '''    
    cmd_block = CONFIG_SERVICE_CMD_BLOCK
    
    if cfg['block_client'] == True and cfg['block_client_interval']:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['enable_block_client'] % cfg['block_client_interval']
    
    elif cfg['block_client'] == False:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['disable_block_client']
        
    if cfg['scan_24g'] == True and cfg['scan_24g_interval']:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['enable_scan_24g'] % cfg['scan_24g_interval']
    
    elif cfg['scan_24g'] == False:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['disable_scan_24g']    
        
    if cfg['scan_5g'] == True and cfg['scan_5g_interval']:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['enable_scan_5g'] % cfg['scan_5g_interval']
    
    elif cfg['scan_5g'] == False:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['disable_scan_5g'] 
        
    if cfg['raps'] == True:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['enable_raps']
    
    elif cfg['raps'] == False:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['disable_raps'] 

#chentao 2014-03-25
    if cfg.has_key('block_all_mcast') and cfg['block_all_mcast']:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['block_all_mcast']
    elif cfg.has_key('block_non_well_known_mcast') and cfg['block_non_well_known_mcast']:
        cmd_block += CONFIG_SERVICE_CMD_COMPLEX['block_non_well_known_mcast']
    for k in ENABLE_SERVICE_SIMPLE_CMD:
        if cfg[k] == True:
            cmd_block += ENABLE_SERVICE_SIMPLE_CMD[k]
        
        elif cfg[k] == False:
            cmd_block += DISABLE_SERVICE_SIMPLE_CMD_PATTERN % ENABLE_SERVICE_SIMPLE_CMD[k]

    cmd_block += SAVE_CONFIG
    
    return cmd_block


def _define_expect_cli_info(cfg):
    '''
    Input:
        cfg = dict(adjust_ap_power = None,
                    adjust_ap_channel = None,
                    protect_network = None,
                    block_client = None,
                    block_client_interval = '',
                    scan_24g = None,
                    scan_24g_interval = '',
                    scan_5g = None,
                    scan_5g_interval = '',
                    report_rogue_device = None,
                    detect_rogue_dhcp = None,
                    detect_aeroscout_rfid = None,
                    block_client_interval = '',
                    )
               
    Output:
        info = {'AeroScout RFID tag detection': 'Enabled',
                'Automatically adjust ap channel': 'Enabled',
                'Automatically adjust ap radio power': 'Enabled',
                'Channelfly works in 2.4GHz radio': 'Disabled',
                'Channelfly works in 5GHz radio': 'Disabled',
                'Protect my wireless network against excessive wireless requests': 'Enabled',
                'Report rogue devices in ZD event log': 'Enabled',
                'Rogue DHCP server detection': 'Enabled',
                'Run a background scan on 2.4GHz radio': {'Status': 'Enabled', 
                                                          'Time': '20 seconds'},
                'Run a background scan on 5GHz radio': {'Status': 'Enabled', 
                                                        'Time': '30 seconds'},
                'Temporarily block wireless clients with repeated authentication failures': {'Status': 'Enabled',
                                                                                             'Time': '30 seconds'}
                }
    '''
    info = dict()
    for key in cfg:
        if key in SERVICE_CFG_INFO_KEY_MAP:
            if cfg[key] == True:
                info[SERVICE_CFG_INFO_KEY_MAP[key]] = 'Enabled'
            
            elif cfg[key] == False:
                info[SERVICE_CFG_INFO_KEY_MAP[key]] = 'Disabled'
    
    advance_info = _define_advance_expect_cli_info(cfg)
    info.update(advance_info)
    
    return info


def _define_advance_expect_cli_info(cfg):
    _info = dict()
        
    for k in SERVICE_ADVANCE_CFG_INFO_KEY_MAP:
        _info_key = SERVICE_ADVANCE_CFG_INFO_KEY_MAP[k]
        _info[_info_key] = {}
        cfg_interval_key = '%s_interval' % k
        if cfg[k] == True and cfg[cfg_interval_key]:
            _info[_info_key]['Status'] = 'Enabled'
            _info[_info_key]['Time'] = '%s seconds' % cfg[cfg_interval_key]
            
        elif cfg[k] == False:
            _info[_info_key]['Status'] = 'Disabled'

    return _info


def _define_expect_gui_info(cli_cfg_dict):
    expect_info = {}
    for key in cli_cfg_dict:
        if key in SERVICE_CFG_INFO_KEY_MAP and cli_cfg_dict[key] != None and cli_cfg_dict[key] != '':
            expect_info[key] = cli_cfg_dict[key]
             
    return expect_info


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
        
        elif original_dict[k] != expect_dict[k]:
            return (False, 'The value [%s] of parameter [%s] is not correct in dict: %s ' % (expect_dict[k], k, original_dict))         

    return (True, '')
