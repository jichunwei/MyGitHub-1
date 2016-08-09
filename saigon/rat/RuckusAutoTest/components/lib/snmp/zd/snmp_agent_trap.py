'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for verify snmp agent and trap.
'''

import logging
import time

from RuckusAutoTest.components.lib.snmp.zd import sys_info
from RuckusAutoTest.components.lib.zdcli.sys_basic_info import get_sys_info
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import check_snmpd_process

#=============================================#
#             Access Methods            
#=============================================#
def verify_snmp_agent(snmp, zdcli, snmp_agent_cfg):
    '''
    Verify snmp agent based on agent_cfg, 
    include action (enable/disable), version (2/3), other related config.
    '''
    result = {}
    
    is_enable = snmp_agent_cfg['enabled']
    # Update snmp config.
    snmp.set_config(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))    
    message = verify_snmp_command(snmp, zdcli, is_enable)
    
    if message:        
        logging.warning(message)
        result.update({'GetSNMP': message})           

    return result

def verify_snmpd_process(zdcli, is_enabled):
    '''
    Verify snmpd is started or shut down.
    '''    
    time.sleep(10)
    result = ''
    if is_enabled:
        if not check_snmpd_process(zdcli):
            result = 'Snmpd process is not in ps list.'           
    else:
        if check_snmpd_process(zdcli):
            result = 'Snmpd process is still in ps list.'
            
    if result:
        logging.warning(result)
        return {'CheckProcess' : result}

def verify_snmp_command(snmp,zdcli, is_enable):
    '''
    Verify snmp command works well. 
    '''    
    result = False
    sys_name_snmp = sys_info.get_system_name(snmp)
    cli_sys_info = get_sys_info(zdcli)
    if cli_sys_info.has_key('System Overview'):
        sys_name_cli = cli_sys_info['System Overview']['Name']
    else:
        sys_name_cli = 'No value from cli.'
        
    if compare(sys_name_snmp, sys_name_cli, 'eq'):
        result = True        
    else:
        result = False
        
    res = ''
    if result != is_enable:
        if is_enable:
            message = "SNMP command can't work when the agent is enabled."
        else:
            message = "SNMP command still can work when the agent is disabled."
            
        res = "FAIL: %s" % message
                        
    return res

def verify_ap_join_trap(trap_service_cfg, ap_mac_addr, agent_ip_addr = '192.168.0.2'):
    '''
    Verify AP join ZD trap inforamtion.    
    '''
    expect_trap_cfg = {'agent_ip_addr':agent_ip_addr,
                       'trap_obj_name':'ruckusZDEventAPJoinTrap',
                       'event_obj_name': 'ruckusZDEventAPMacAddr',
                       'event_obj_value':ap_mac_addr,
                       'event_mib': 'RUCKUS-ZD-EVENT-MIB',
                       }
    
    return verify_trap_info(trap_service_cfg, expect_trap_cfg)

def verify_trap_info(trap_service_cfg, expect_trap_cfg):
    '''
    Get trap information and compare them with expect trap cfg.
    trap_receiver_cfg: 
        For v2 trap:
            {'server_ip': '192.168.0.10',
             'port': 162,
             'version': 2,
             'community': 'public',
             'timeout': 20,
             }       
        For v3 trap:
            {'server_ip': '192.168.0.10',
             'port': 162,
             'version': 2,
             'sec_name': 'ruckus-read',
             'auth_protocol': 'MD5',
             'auth_passphrase': '12345678',
             'priv_protocol': 'DES',
             'priv_passphrase': '12345678',
             'timeout': 20
             }
    expect_trap_cfg:
        {'agent_ip_addr':'192.168.0.2',
         'trap_obj_name':'ruckusZDEventAPJoinTrap',
         'trap_obj_value':'',
         'event_mib': 'RUCKUS-ZD-EVENT-MIB',
        }
    '''
    exp_agent_ip_addr = expect_trap_cfg['agent_ip_addr']
    
    #Create default snmp object to translate object name to oid.
    snmp = helper.create_snmp({})
    
    #Get snmp trap oid, which is the key to expect trap oid.
    snmpv2_mib = 'SNMPv2-MIB'
    snmp_trap_obj_name = 'snmpTrapOID'    
    snmp_trap_oid = _get_oid_by_mib_name(snmp,snmpv2_mib,snmp_trap_obj_name)
    snmp_trap_oid = '%s.0' % (snmp_trap_oid)
    
    #Get expect trap OID.
    trap_event_mib = expect_trap_cfg['event_mib']
    exp_trap_obj_name = expect_trap_cfg['trap_obj_name']
    exp_trap_oid = _get_oid_by_mib_name(snmp,trap_event_mib,exp_trap_obj_name)
         
    event_obj_name = expect_trap_cfg['event_obj_name']
    event_oid = _get_oid_by_mib_name(snmp,trap_event_mib,event_obj_name)
    
    exp_event_value = expect_trap_cfg['event_obj_value']
    
    #sys_uptime_obj_name = 'sysUpTimeInstance'    
    #rfc1213_mib = 'RFC1213-MIB'
    #sys_uptime_oid = snmp.translate_name(rfc1213_mib, sys_uptime_obj_name)
    #if sys_uptime_oid[0] == '.':
    #    sys_uptime_oid = sys_uptime_oid[1:]
        
    trap_obj = helper.create_snmp_trap(trap_service_cfg)
    trap_obj.start()
    trap_res_list = trap_obj.get_trap_result()
    trap_obj.close()
    
    is_match = False
    msg = ''
    
    for trap_info in trap_res_list:
        agent_ip_addr = trap_info['agent_ip_addr']
        #snmp_udp_domain = trap_info['snmp_udp_domain']
        trap_oid = trap_info[snmp_trap_oid]
        if agent_ip_addr == exp_agent_ip_addr and trap_oid == exp_trap_oid:
            event_value = trap_info[event_oid]
            if event_value.lower() == exp_event_value.lower():
                is_match = True
                msg = 'Received AP join trap for %s' % (event_value)
                break
    
    if not is_match:        
        msg = 'Trap information is incorrect: Expected: %s, Actual: %s' % (expect_trap_cfg, trap_res_list)
    
    return is_match, msg

def expected_trap_info(trap_obj, agent_ip_addr='192.168.0.2', event_obj='', event_obj_value='', event_mib='RUCKUS-ZD-EVENT-MIB'):
    '''
    Description:
        Structure trap info 
    '''
#    if event_obj_value:
#        event_obj_value = '\'%s\'' % event_obj_value

    expect_trap_cfg = { 'agent_ip_addr':agent_ip_addr,
                        'trap_obj_name': trap_obj,
                        'event_obj_name': event_obj,
                        'event_obj_value':event_obj_value,
                        'event_mib': event_mib
                           }
    return  expect_trap_cfg  

def verify_trap_sent_to_server(expect_trap_cfg, trap_messages_list):
    '''_
    Description: 
    Verify expected trap is in the trap message list got by trap server
    Input
    --expect_trap_cfg:
         {'agent_ip_addr':agent_ip_addr,
          'trap_obj_name':'ruckusZDEventAPJoinTrap',
          'event_obj_name': 'ruckusZDEventAPMacAddr',
          'event_obj_value':ap_mac_addr,
          'event_mib': 'RUCKUS-ZD-EVENT-MIB',
        }
    --trap_messages_list: trap messages got by trap server
    
    Output:
    is_match: find or not find
    msg: description of verify result
    '''
    exp_agent_ip_addr = expect_trap_cfg['agent_ip_addr']
    
    #Create default snmp object to translate object name to oid.
    snmp = helper.create_snmp({})
    
    #Get snmp trap oid, which is the key to expect trap oid.
    snmpv2_mib = 'SNMPv2-MIB'
    snmp_trap_obj_name = 'snmpTrapOID'    
    snmp_trap_oid = _get_oid_by_mib_name(snmp,snmpv2_mib,snmp_trap_obj_name)
    snmp_trap_oid = '%s.0' % (snmp_trap_oid)
    
    #Get expect trap OID.
    trap_event_mib = expect_trap_cfg['event_mib']
    exp_trap_obj_name = expect_trap_cfg['trap_obj_name']
    exp_trap_oid = _get_oid_by_mib_name(snmp,trap_event_mib,exp_trap_obj_name)
    
    exp_event_value = ''
    event_oid = ''
    event_obj_name = ''
    if expect_trap_cfg.has_key('event_obj_name') and expect_trap_cfg.has_key('event_obj_value'):    
        event_obj_name = expect_trap_cfg['event_obj_name']
        event_oid = _get_oid_by_mib_name(snmp,trap_event_mib,event_obj_name)
    
        exp_event_value = expect_trap_cfg['event_obj_value']
    
    is_match = False
    msg = ''
    
    for trap_info in trap_messages_list:
        agent_ip_addr = trap_info['agent_ip_addr']
        trap_oid = trap_info[snmp_trap_oid]
        if agent_ip_addr == exp_agent_ip_addr and trap_oid == exp_trap_oid:
            if event_obj_name == '' and exp_event_value == '':
                is_match = True
                msg = 'Received trap: %s' % (exp_trap_obj_name)
                break
            else: 
                if trap_info.has_key(event_oid):               
                    event_value = trap_info[event_oid]
                    if exp_event_value.lower() == event_value.lower() or exp_event_value.lower() in event_value.lower():
                        is_match = True
                        msg = 'Received trap: %s with info: %s' % (exp_trap_obj_name,event_value)
                        break
                else:
                    logging.info("Trap: %s doesn't have event oid %s" % (trap_oid, event_oid))
    
    if not is_match:   
        logging.info('Trap is not got by trap server: Expected: %s, Actual: %s' % (expect_trap_cfg, trap_messages_list))     
        msg = 'Expected trap[name: %s, oid: %s] is not got by trap server.' % (exp_trap_obj_name, exp_trap_oid)
    
    return is_match, msg

def _get_oid_by_mib_name(snmp, mib_name, obj_name):
    '''
    Get object oid by mib and name.
    Remove the first and last dot(.) char.
    '''
    oid = None
    oids_list = snmp.translate_name(mib_name, obj_name)
    if oids_list and len (oids_list) >0:
        oid = oids_list[0]         
        if oid[0] == '.':
            oid = oid[1:]
        if oid[-1] == '.':
            oid = oid[:-1]
            
    if not oid or 'Bad OBJECTS' in oid or 'error' in oid or 'Error' in oid:
        raise Exception("Can't get snmp trap oid for %s::%s" % (mib_name, obj_name))
    
    return oid    