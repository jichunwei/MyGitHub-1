'''
Description:
  This testsuite is used to test the functionalities of Multiple SNMP trap receivers.
  
  How to test:
  1. Configure two IPV4 servers and two IPV6 servers to test Maximum number of SNMPv2 Trap servers, 
  and verify trap message can be sent to the four trap servers.
  2. Configure two IPV4 servers and two IPV6 servers to test Maximum number of SNMPv3 Trap servers, 
  and verify trap message can be sent to the four trap servers.
  3. Verify multiple trap servers can be configured via SNMP and trap message can be sent to all the trap servers
  4. Verify SNMP trap can work properly when ZD backup and restore
      
Created on 2012-7-25
@author: zoe.huang@ruckuswireless.com

'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMPv2 Agent via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = 'Enable SNMP Trap via GUI'
    param_cfg = {'snmp_trap_cfg': tcfg['enable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = 'Remove SNMP Trap info'
    param_cfg = {'snmpv2': '2','snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    #1. Maximum v2 trap server number

    test_case_name = '[Maximum SNMPv2 trap server with ipv4 and ipv6 combination] '
      
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sConfigure maximum SNMPv2 trap servers via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap info via CLI' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify maximum trap servers are set successfully via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v2_trap_cfg'],
                 'time_out': 300
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_AP'
    common_name = '%sDelete an ap from ZD' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver'
    common_name = '%sVerify AP Join trap can be sent to all the trap servers' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v2_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 300
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv2 Trap info' % test_case_name
    param_cfg = {'snmpv2': '2'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    #2. Maximum v3 trap server number
    
    test_case_name = '[Maximum SNMPv3 trap server with ipv4 and ipv6 combination] '
      
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sConfigure maximum SNMPv3 trap servers via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap info via CLI' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify maximum trap servers are set successfully via CLI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v3_trap_cfg'],
                 'time_out': 300
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_AP'
    common_name = '%sDelete an ap from ZD' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver'
    common_name = '%sVerify AP Join trap can be sent to all the trap servers' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_maximum_v3_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 300
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv3 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
   
    #3.SNMPv2 trap servers set via SNMP
    
    test_case_name = '[SNMPv2 trap servers set via SNMP] '
    
    test_name = 'CB_ZD_SNMP_Verify_Update_Sys_SNMP_Info'
    common_name = '%sSet SNMP Trap info via SNMP and Validation between Set and Get' % test_case_name
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_snmp_agent_v2_cfg'],
                 'set_snmp_cfg': get_snmpv2_set_cfg(tcfg['enable_multi_v2_trap_cfg'])
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info via CLI' % test_case_name
    param_cfg = {'info_type':'trap'}
    test_cfgs.append((param_cfg , test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info via SNMP' % test_case_name
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_snmp_agent_v2_cfg'],
                 'info_type': 'trap',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify SNMP Trap Info between SNMP Get and CLI Get' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v2_trap_cfg'],
                 'time_out': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_AP'
    common_name = '%sDelete an ap from ZD' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver'
    common_name = '%sVerify AP Join trap can be sent to all the trap servers' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v2_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv2 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv2': '2'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    #4.SNMPv3 trap servers set via SNMP
    
    test_case_name = '[SNMPv3 trap servers set via SNMP] '
    
    test_name = 'CB_ZD_SNMP_Verify_Update_Sys_SNMP_Info'
    common_name = '%sSet SNMP Trap info via SNMP and Validation between Set and Get' % test_case_name
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_snmp_agent_v2_cfg'],
                 'set_snmp_cfg': get_snmpv3_set_cfg(tcfg['enable_multi_v3_trap_cfg'])
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info via CLI' % test_case_name
    param_cfg = {'info_type':'trap'}
    test_cfgs.append((param_cfg , test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info via SNMP' % test_case_name
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_snmp_agent_v2_cfg'],
                 'info_type': 'trap',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify SNMP Trap Info between SNMP Get and CLI Get' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'time_out': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_AP'
    common_name = '%sDelete an ap from ZD' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver'
    common_name = '%sVerify AP Join trap can be sent to all the trap servers' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv3 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    #5. Backup restore
    
    test_case_name = '[Backup Restore by Full Failover and Policy] '
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv3 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv3 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Backup' 
    common_name = '%sBackup configure file for ZD' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    ######Full Restore############
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap before full restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI before full restore' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP trap is disabled before full restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore configure file for ZD by full mode' % test_case_name
    param_cfg = {'restore_type':'restore_everything'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI after restore ZD by full mode' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP trap info restored by full mode' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages after full restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'time_out': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_AP'
    common_name = '%sDelete an ap from ZD after full restore' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver'
    common_name = '%sVerify AP Join trap can be sent to all the trap servers after full restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    ######Failover Restore############
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap before failover restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI before failover restore' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP trap is disabled before failover restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore configure file for ZD by failover mode' % test_case_name
    param_cfg = {'restore_type':'restore_everything_except_ip'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI after restore ZD by failover mode' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP trap info restored by failover mode' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to receive trap messages after failover restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'time_out': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_AP'
    common_name = '%sDelete an ap from ZD after failover restore' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap_Multiple_Receiver'
    common_name = '%sVerify APJointrap sent to all trap servers after failover restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 200
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    ######Policy Restore############
    test_name = 'CB_ZD_Enable_Disable_SNMP_Trap'
    common_name = '%sDisable SNMP Trap before policy restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI before policy restore' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP trap is disabled before policy restore' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore configure file for ZD by policy mode' % test_case_name
    param_cfg = {'restore_type':'restore_basic_config'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP trap Info via GUI after restore ZD by policy mode' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP trap info is not restored by policy mode' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv3 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    
    #6.Defined ZD events report to SNMPv2 trap server
    
    test_case_name = '[Defined ZD events report to SNMPv2 trap server] '
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv2 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv2 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Cfg_Event_Log_Level'
    common_name = '%sConfig ZD log to show more' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v2_trap_cfg'],
                 'time_out': 600
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Trigger_Trap'
    common_name = '%sTigger several kinds of Traps' % test_case_name
    param_cfg = {'station': {'sta_tag': 'sta-ng', 'sta_ip_addr': '192.168.1.11'},
                  'wlan_cfg' : {'sta_encryption': 'none', 'encryption': 'none', 'sta_auth': 'open', 'ssid': 'openwlanv2', 'auth': 'open'},
                  'new_ssid' : 'openwlanv2_changed'
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Defined_Traps_Sent_To_Multiple_Receiver'
    common_name = '%sVerify all the triggered traps can be sent to all the trap servers' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v2_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 400
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv2 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv2': '2'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
       
    #7.Defined ZD events report to SNMPv3 trap server
    
    test_case_name = '[Defined ZD events report to SNMPv3 trap server] '
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sConfigure two SNMPv3 trap servers via GUI' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify two SNMPv3 trap servers are configured successfully' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Cfg_Event_Log_Level'
    common_name = '%sConfig ZD log to show more again' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Start_Linux_SNMPTrap_Server'
    common_name = '%sTrap servers start to listen and receive trap messages again' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'time_out': 600
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Trigger_Trap'
    common_name = '%sTigger several kinds of Traps again' % test_case_name
    param_cfg = {'station': {'sta_tag': 'sta-ng', 'sta_ip_addr': '192.168.1.11'},
                  'wlan_cfg' : {'sta_encryption': 'none', 'encryption': 'none', 'sta_auth': 'open', 'ssid': 'openwlanv3', 'auth': 'open'},
                  'new_ssid' : 'openwlanv3_changed'
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Defined_Traps_Sent_To_Multiple_Receiver'
    common_name = '%sVerify all triggered SNMPv3 traps can be sent to all the trap servers' % test_case_name
    param_cfg = {'snmp_trap_cfg': tcfg['enable_multi_v3_trap_cfg'],
                 'zd_ipv6_addr': tcfg['zd_ipv6_addr'],
                 'wait_time_for_trap': 400
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = '%sRemove SNMPv3 Trap info via CLI' % test_case_name
    param_cfg = {'snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Remove_SNMP_Trap'
    common_name = 'Remove SNMP Trap info at cleanup'
    param_cfg = {'snmpv2': '2','snmpv3': '3'}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = 'Disable SNMP Trap'
    param_cfg = {'snmp_trap_cfg': tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
 
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMPv2 Agent via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['disable_snmp_v2_agent_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    return test_cfgs

def get_snmpv2_set_cfg(cli_snmp_cfg):
    snmp_cli_keys_mapping = {
                             'server_ip': 'v2_trap_server',
                             }
    
    snmp_cfg = {} 
    snmp_cfg['trap_enable'] = 1
    snmp_cfg['trap_version'] = 1 #snmpv2   
    for i in range(1,5):
        if cli_snmp_cfg.has_key(str(i)):
            snmp_cfg[str(i)]= {}
            trap_server_info =  cli_snmp_cfg[str(i)]      
            for key,value in snmp_cli_keys_mapping.items():
                if trap_server_info.has_key(key):
                    new_key = value
                    snmp_cfg[str(i)][new_key] = trap_server_info[key]         
                
    return snmp_cfg  

def get_snmpv3_set_cfg(cli_snmp_cfg):
    snmp_cli_keys_mapping = {
                             'sec_name':'v3_trap_user',
                             'server_ip': 'v3_trap_server',
                             'auth_protocol': 'v3_trap_auth',
                             'auth_passphrase': 'v3_trap_auth_key',
                             'priv_protocol': 'v3_trap_priv',
                             'priv_passphrase':'v3_trap_priv_key',
                             }
    
    snmp_cfg = {} 
    snmp_cfg['trap_enable'] = 1
    snmp_cfg['trap_version'] = 2 #snmpv3   
    for i in range(1,5):
        if cli_snmp_cfg.has_key(str(i)):
            snmp_cfg[str(i)]= {}
            trap_server_info =  cli_snmp_cfg[str(i)]      
            for key,value in snmp_cli_keys_mapping.items():
                if trap_server_info.has_key(key):
                    new_key = value
                    snmp_cfg[str(i)][new_key] = trap_server_info[key]         
                
    return snmp_cfg  
    
def define_test_parameters(tbcfg, trap_server_ip_1, trap_server_ip_2, trap_server_ip_3, trap_server_ip_4,zd_ipv6_addr):
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3, }
    enable_snmp_agent_v2_cfg = {'version': 2,
                                'enabled': True,
                                'ro_community': 'public',
                                'rw_community': 'private',
                                'contact': 'support@ruckuswireless.com',
                                'location': 'Shenzhen'
                               }
    disable_snmp_v2_agent_cfg = {'version': 2,
                                 'enabled': False
                                 }
    
    enable_multi_v2_trap_cfg = {'version': 2,
                                   'enabled': True,
                                   '1': {'server_ip':trap_server_ip_1},
                                   '2': {'server_ip':trap_server_ip_2},
                               }
    
    enable_multi_v3_trap_cfg = {'version': 3,
                                'enabled': True,
                                '1': {'sec_name': 'ruckus-read',
                                       'server_ip': trap_server_ip_1,
                                       'auth_protocol': 'MD5',
                                       'auth_passphrase': '12345678',
                                       'priv_protocol': 'DES',
                                       'priv_passphrase': '12345678',
                                     },
                                '2': {'sec_name': 'ruckus-read',
                                      'server_ip': trap_server_ip_2,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': '12345678',
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': '12345678',
                                     }
                                  }
    enable_maximum_v2_trap_cfg = {'version': 2,
                                   'enabled': True,
                                   '1': {'server_ip':trap_server_ip_1},
                                   '2': {'server_ip':trap_server_ip_2},
                                   '3': {'server_ip':trap_server_ip_3},
                                   '4': {'server_ip':trap_server_ip_4},
                                 }
    enable_maximum_v3_trap_cfg = {'version': 3,
                                  'enabled': True,
                                  '1': {'sec_name': 'ruckus-read',
                                      'server_ip': trap_server_ip_1,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': '12345678',
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': '12345678',
                                      },
                                  '2': {'sec_name': 'ruckus-read',
                                      'server_ip': trap_server_ip_2,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': '12345678',
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': '12345678',
                                      },
                                 '3': {'sec_name': 'ruckus-read',
                                      'server_ip': trap_server_ip_3,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': '12345678',
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': '12345678',
                                      },
                                  '4': {
                                      'sec_name': 'ruckus-read',
                                      'server_ip': trap_server_ip_4,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': '12345678',
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': '12345678',
                                      }
                                  }
    
    disable_trap_cfg = {'enabled': False}
    enable_trap_cfg = {'enabled': True}
        
    tcfg = {'snmp_cfg': snmp_cfg,
            'enable_snmp_agent_v2_cfg': enable_snmp_agent_v2_cfg,
            'disable_snmp_v2_agent_cfg': disable_snmp_v2_agent_cfg,
            'enable_multi_v2_trap_cfg': enable_multi_v2_trap_cfg,
            'enable_multi_v3_trap_cfg': enable_multi_v3_trap_cfg,
            'enable_maximum_v2_trap_cfg': enable_maximum_v2_trap_cfg,
            'enable_maximum_v3_trap_cfg': enable_maximum_v3_trap_cfg,
            'disable_trap_cfg': disable_trap_cfg,
            'enable_trap_cfg': enable_trap_cfg,
            'zd_ipv6_addr': zd_ipv6_addr
            }
    
    return tcfg

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    error = len(checklist)-len(checkset)
    if error:
        print checklist
        print checkset
        raise Exception('%s test_name, common_name duplicate' % error) 


def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ts_name = 'Multiple trap receivers - Functionalities'
    ts = testsuite.get_testsuite(ts_name, 'SNMP Trap Functionalities: Max number of trap servers, configuration via SNMP, Backup/restore, etc.', combotest=True)
        
    trap_server_ip_1 = raw_input("Please input ipv4 address of dhcp sever[192.168.0.252]: ")
    if not trap_server_ip_1:
        trap_server_ip_1 = '192.168.0.252'
        
    trap_server_ip_2 = raw_input("Please input ipv4 address of dhcp sever with VLAN10[192.168.10.252]: ")   
    if not trap_server_ip_2:
        trap_server_ip_2 = '192.168.10.252'
    
    trap_server_ip_3 = raw_input("Please input ipv4 address of dhcp server with VLAN20[192.168.20.252]: ")
    if not trap_server_ip_3:
        trap_server_ip_3 = '192.168.20.252'
        
    trap_server_ip_4 = raw_input("Please input ipv6 address of dhcp server[2020:db8:1::252]: ") 
    if not trap_server_ip_4:
        trap_server_ip_4 = '2020:db8:1::252'    
    
    zd_ipv6_addr = raw_input("Please input ipv6 address of ZoneDirector[2020:db8:1::2]: ")
    if not zd_ipv6_addr:
        zd_ipv6_addr = '2020:db8:1::2'
        
    tcfg = define_test_parameters(tbcfg, trap_server_ip_1, trap_server_ip_2, trap_server_ip_3, trap_server_ip_4, zd_ipv6_addr)    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    
