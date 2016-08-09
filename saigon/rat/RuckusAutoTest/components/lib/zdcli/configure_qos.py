# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This module supports to do the functions under ruckus(config-sys-qos)# and ruckus(config-wlan)#
mode of ZDCLI:

Commands available for ruckus(config-sys-qos)#
  tx-failed-threshold {NUMBER} Sets the TX failed threshold value.
  heuristics video inter-packet-gap min {NUMBER} max {NUMBER} Sets the heuristics video inter-packet-gap maximum value.
  heuristics video packet-length min {NUMBER} max {NUMBER} Sets the heuristics video packet-length maximum value.
  heuristics voice inter-packet-gap min {NUMBER} max {NUMBER} Sets the heuristics voice inter-packet-gap maximum value.
  heuristics voice packet-length min {NUMBER} max {NUMBER} Sets the heuristics voice packet-length maximum value.
  heuristics classification video packet-octet-count {OCTET} Sets the heuristics classification video packet-octet-count value.
  heuristics classification voice packet-octet-count {OCTET} Sets the heuristics classification voice packet-octet-count value.
  heuristics no-classification video packet-octet-count {OCTET} Sets the heuristics no-classification video packet-octet-count value.
  heuristics no-classification voice packet-octet-count {OCTET} Sets the heuristics no-classification voice packet-octet-count value.
  tos classification video {TOS} Sets the tos classification video value.
  tos classification voice {TOS} Sets the tos classification voice value.
  
Commands available for ruckus(config-wlan)#
  qos classification   Enables QoS classification.
  qos heuristics-udp   Enables QoS heuristics for UDP traffic.
  qos directed-multicast Enables QoS for directed multicast traffic.
  qos igmp-snooping    Enables QoS for IGMP snooping traffic.
  qos mld-snooping     Enables QoS for MLD snooping traffic.
  qos tos-classification Enables QoS tos classification.
  qos priority high    Sets QoS priority to 'high'.
  qos priority low     Sets QoS priority to 'low'.
  qos directed-threshold {NUMBER} Configures QoS for directed threshold.

"""

from RuckusAutoTest.components.lib.zdcli import output_as_dict
import logging

#
# GLOBAL DEFINATION
#

go_to_config_cmd = 'config'
go_to_config_wlan_cmd = 'wlan'
config_wlan_mode_prompt = 'ruckus\(config-wlan\)#'
go_to_config_sys_qos_cmd = 'system\nqos\n'
disable_global_qos_cmd = 'system\nno qos\n'
config_sys_qos_mode_prompt = 'ruckus\(config-sys-qos\)#'
                           
wlan_qos_classification_cmd = {'enabled': 'qos classification',
                               'disabled': 'no qos classification'}
wlan_qos_directed_multicast_cmd = {'enabled': 'qos directed-multicast',
                                   'disabled': 'no qos directed-multicast'}
wlan_qos_igmp_snooping_mode_cmd = {'enabled': 'qos igmp-snooping',
                                   'disabled': 'no qos igmp-snooping'}
wlan_qos_mld_snooping_mode_cmd = {'enabled': 'qos mld-snooping',
                                  'disabled': 'no qos mld-snooping'}
wlan_qos_tos_classification_cmd = {'enabled': 'qos tos-classification',
                                   'disabled': 'no qos tos-classification'}
wlan_qos_udp_heuristic_classification = {'enabled': 'qos heuristics-udp',
                                         'disabled': 'no qos heuristics-udp'}
wlan_qos_directed_threshold_cmd = {'directed_threshold': 'qos directed-threshold %s'}
wlan_qos_priority_cmd = {'high': 'qos priority high',
                         'low': 'qos priority low'}

sys_qos_cmd = {'tx_failure_threshold': 'tx-failed-threshold',
               'heuristic_pkt_gap_video': 'heuristics video inter-packet-gap',
               'heuristic_pkt_gap_voice': 'heuristics voice inter-packet-gap',
               'heuristic_pkt_len_video': 'heuristics video packet-length',
               'heuristic_pkt_len_voice': 'heuristics voice packet-length',
               'heuristic_octet_count_video': 'heuristics classification video packet-octet-count',
               'heuristic_octet_count_voice': 'heuristics classification voice packet-octet-count',
               'no_heuristic_octet_count_video': 'heuristics no-classification video packet-octet-count',
               'no_heuristic_octet_count_voice': 'heuristics no-classification voice packet-octet-count', 
               'tos_classification_video': 'tos classification video',
               'tos_classification_voice': 'tos classification voice',
              }

setting_success_msg = ['Changes are saved!', '']

########################################################################################
# PUBLIC SECSSION
########################################################################################

def config_wlan_qos(zdcli, **kwargs):
    option = {}
    if kwargs: option.update(kwargs)
    
    cmd_block = _define_wlan_qos_cmd_block(option)
    logging.debug(cmd_block)
    zdcli.do_cfg(cmd_block)
    
def config_sys_qos(zdcli, **kwargs):
    option = {}
    if kwargs: option.update(kwargs)
    
    cmd_block = _define_sys_qos_cmd_block(option)
    logging.debug(cmd_block)
    zdcli.do_cfg(cmd_block)

def disable_global_qos(zdcli, **kwargs):
    zdcli.do_cfg(disable_global_qos_cmd)

def get_qos_setting(zdcli):
    val = zdcli.do_cfg_show(go_to_config_sys_qos_cmd)
    return output_as_dict.parse(val)
    
########################################################################################
# PRIVATE SECSSION
########################################################################################

def _define_wlan_qos_cmd_block(option):
    """
    """
    if not option.get('wlan'):
        return ''
    
    cmd_block = '%s %s\n' %(go_to_config_wlan_cmd, option['wlan'])
    if option.get('classification'):
        cmd_block += wlan_qos_classification_cmd[option['classification'].lower()] + '\n'
        
    if option.get('directed_multicast'):
        cmd_block += wlan_qos_directed_multicast_cmd[option['directed_multicast'].lower()] + '\n'
        
    if option.get('igmp_snooping_mode'):
        cmd_block += wlan_qos_igmp_snooping_mode_cmd[option['igmp_snooping_mode'].lower()] + '\n'

    if option.get('mld_snooping_mode'):
        cmd_block += wlan_qos_mld_snooping_mode_cmd[option['mld_snooping_mode'].lower()] + '\n'
        
    if option.get('tos_classification'):
        cmd_block += wlan_qos_tos_classification_cmd[option['tos_classification'].lower()] + '\n'
    
    if option.get('udp_heuristic_classification'):
        cmd_block += wlan_qos_udp_heuristic_classification[option['udp_heuristic_classification'].lower()] + '\n' 
    
    if option.get('priority'):
        cmd_block += wlan_qos_priority_cmd[option['priority'].lower()] + '\n'
    
    if option.get('directed_threshold'):
        cmd_block += wlan_qos_directed_threshold_cmd['directed_threshold'] % option['directed_threshold']  + '\n'
    
    return cmd_block
        

def _define_sys_qos_cmd_block(option):
    """
    """
    cmd_block = go_to_config_sys_qos_cmd
    
    if option.get('tx_failure_threshold'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['tx_failure_threshold'], option['tx_failure_threshold'])
    
    if option.get('heuristic_max_pkt_gap_video') and option.get('heuristic_min_pkt_gap_video'):
        cmd_block += '%s min %s max %s\n' % (sys_qos_cmd['heuristic_pkt_gap_video'],
                                             option['heuristic_min_pkt_gap_video'], 
                                             option['heuristic_max_pkt_gap_video'],)
        
    if option.get('heuristic_max_pkt_gap_voice') and option.get('heuristic_min_pkt_gap_voice'):
        cmd_block += '%s min %s max %s\n' % (sys_qos_cmd['heuristic_pkt_gap_voice'],
                                             option['heuristic_min_pkt_gap_voice'], 
                                             option['heuristic_max_pkt_gap_voice'],)
    
    if option.get('heuristic_min_pkt_len_video') and option.get('heuristic_max_pkt_len_video'):
        cmd_block += '%s min %s max %s\n' % (sys_qos_cmd['heuristic_pkt_len_video'],
                                             option['heuristic_min_pkt_len_video'],
                                             option['heuristic_max_pkt_len_video'])
    
    if option.get('heuristic_min_pkt_len_voice') and option.get('heuristic_max_pkt_len_voice'):
        cmd_block += '%s min %s max %s\n' % (sys_qos_cmd['heuristic_pkt_len_voice'],
                                             option['heuristic_min_pkt_len_voice'],
                                             option['heuristic_max_pkt_len_voice'])
    
    if option.get('heuristic_octet_count_video'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['heuristic_octet_count_video'],
                                  option['heuristic_octet_count_video'])
    
    if option.get('heuristic_octet_count_voice'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['heuristic_octet_count_voice'],
                                  option['heuristic_octet_count_voice'])
        
    if option.get('no_heuristic_octet_count_video'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['no_heuristic_octet_count_video'],
                                  option['no_heuristic_octet_count_video'])
    
    if option.get('no_heuristic_octet_count_voice'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['no_heuristic_octet_count_voice'],
                                  option['no_heuristic_octet_count_voice'])
    #@author: chen.tao since 2014-10-21, to fix ZF-10172
    if option.get('tos_classification_video'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['tos_classification_video'],
                                  option['tos_classification_video'])
    
    if option.get('tos_classification_voice'):
        cmd_block += '%s %s\n' % (sys_qos_cmd['tos_classification_voice'],
                                  option['tos_classification_voice'])
        
    return cmd_block

def _verify_execute_cmd_msg(return_info):
    """
    """
    error_cmd = []
    for cmd in return_info.keys():
        if return_info[cmd] not in setting_success_msg:
            error_cmd.append(cmd)
    
    if error_cmd:
        return (0, 'Below command\(s\)  %s did not execute successful' % error_cmd)
    return (1, 'All commands in block executed successfully')
        