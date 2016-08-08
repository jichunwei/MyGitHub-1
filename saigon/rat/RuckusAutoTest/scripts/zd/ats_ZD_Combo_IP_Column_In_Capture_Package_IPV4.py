"""
Verify Ip address column in packet capture onfiguration.

    Pre-condition:
       AP joins ZD1
       ZD1 is auto approval
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) make sure all APs connect
        2)[system IPv4]set system IP mode is IPv4 only 
        3)[system IPv4]set all AP mode to ipv4/dualstack via randomly selected
        4)[system IPv4]check IP column title
        5)[system IPv4]check IP column value
        6) set system IP mode is IPv4
        7) set all AP IP mode to dualstack 
        8)make sure all APs connect

    
Created on 2014-05-13
@author: Yu.yanan@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy

import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
import random

def define_test_cfg(cfg):
    test_cfgs = []
    list_tmp = []
    tc_name_sub = "system " 
    
    ap_restore_ip_cfg = cfg['restore_ap_ip_cfg']
    zd_ip_cfg = cfg['zd_ip_cfg']

    ap_ipv4_and_dualstack_cfg_list = cfg['ap_ipv4_and_dualstack_cfg_list']
    ap_mac_tag_dict = cfg['ap_tag_map']
    
    round = 0
    step = 0
    round += 1
    
    
    test_name = 'CB_ZD_CLI_Get_Sys_IP_Info'
    common_name = 'get current system IP'
    test_cfgs.append(({'tag_ip_format':True}, test_name, common_name, 0, True))
    
    tc_common_name = tc_name_sub + const.IPV4
    test_name = 'CB_ZD_CLI_Set_Device_IP_Settings'
    common_name = '[%s]%s.%s set system IP mode is IPV4 Only ' % (tc_common_name,round, step)
    test_cfgs.append(({'ip_cfg': zd_ip_cfg}, test_name, common_name, 1, False))
    
    for mac_key,tag_value in ap_mac_tag_dict.items(): 
        #@attention: get random and not repeat ap_ip_mode_cfg
        ap_list_len = len(ap_ipv4_and_dualstack_cfg_list)
        if ap_list_len > 0: 
            index = random.randint(0,len(ap_ipv4_and_dualstack_cfg_list)-1)
            if ap_ipv4_and_dualstack_cfg_list[index] in list_tmp and ap_list_len > 1:
                    del ap_ipv4_and_dualstack_cfg_list[index]
                    index = random.randint(0,len(ap_ipv4_and_dualstack_cfg_list)-1)
            list_tmp.append(ap_ipv4_and_dualstack_cfg_list[index])
            ap_ip_mode_cfg = ap_ipv4_and_dualstack_cfg_list[index]
        else:
            ap_ip_mode_cfg = ap_restore_ip_cfg
 
        ap_ip_name_sub = ap_ip_mode_cfg['ip_version']
        ap_mode = ap_ip_mode_cfg[const.IPV4]['ip_mode']
         
        test_name = 'CB_ZD_CLI_Set_AP_IP_Settings'
        step += 1
        common_name = '[%s]%s.%s set %s mode to %s %s' % (tc_common_name, round, step,tag_value,ap_ip_name_sub,ap_mode)
        test_cfgs.append(({'ip_cfg': ap_ip_mode_cfg,'ap_mac_list': mac_key}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Packet_Capture_Ip_Column_Title'
    step += 1 
    common_name = '[%s]%s.%s check IP column title' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
            
    test_name = 'CB_ZD_Verify_Packet_Capture_Ip_Column_Value'
    step += 1
    common_name = '[%s]%s.%s check IP column value' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    
    for mac_key,tag_value in ap_mac_tag_dict.items():
        
        ap_ip_name_sub = ap_restore_ip_cfg['ip_version']
        test_name = 'CB_ZD_CLI_Set_AP_IP_Settings'
        common_name = 'set %s mode to %s dhcp' %(tag_value,ap_ip_name_sub)
        test_cfgs.append(({'ip_cfg': ap_restore_ip_cfg,'ap_mac_list': mac_key}, test_name, common_name, 0, True))
    #yuyanan 2014-7-17 optimize     
    test_name = 'CB_ZD_CLI_Set_Device_IP_Settings'
    common_name = 'restore zd config' 
    test_cfgs.append(({'carribag_tag': True}, test_name, common_name, 0, True))
        
    return test_cfgs


def _define_ap_ip_cfg(ap_ip_version,ap_ipv4_mode = 'dhcp'):
    ap_ip_cfg = {}
    ap_ip_cfg['ip_version'] = ap_ip_version
    if ap_ip_version in [const.IPV4, const.DUAL_STACK]:
        if ap_ipv4_mode == 'static':
            ap_ip_cfg[const.IPV4] = {'ip_mode': 'static'}
        else:
            ap_ip_cfg[const.IPV4] = {'ip_mode': 'dhcp'} 
    if ap_ip_version in [const.IPV6, const.DUAL_STACK]:
        ap_ip_cfg[const.IPV6] = {'ipv6_mode': 'auto'}
    return ap_ip_cfg

def _define_zd_ip_cfg(zd_ip_version,zd_ipv4_addr,netmask,gateway,pri_dns):
    zd_ip_cfg = {}
    zd_ip_cfg['ip_version'] = zd_ip_version
    if zd_ip_version in [const.IPV4, const.DUAL_STACK]:
        zd_ip_cfg[const.IPV4] = {'ip_alloc': 'static', #dhcp, manual, as-is.
                                 'ip_addr': zd_ipv4_addr,
                                 'netmask': netmask,
                                 'gateway': gateway,
                                 'pri_dns': pri_dns,
                                 'sec_dns': '',
                                 }
    if zd_ip_version in [const.IPV6, const.DUAL_STACK]:
        zd_ip_cfg[const.IPV6] = {'ipv6_alloc': 'auto'}
    #zd_ip_cfg['vlan'] = ''
    
    return zd_ip_cfg


def define_test_parameters(tbcfg, ap_mac_addr):
    zdinfo = tbcfg['ZD']
    zd_ipv4_addr = zdinfo.get('ip_addr')
    netmask = zdinfo.get('netmask')
    gateway = zdinfo.get('gateway')
    pri_dns = zdinfo.get('pri_dns')
    
    zd_ipv4_cfg = _define_zd_ip_cfg(const.IPV4,zd_ipv4_addr,netmask,gateway,pri_dns)
    ap_ipv4_dhcp_cfg = _define_ap_ip_cfg(const.IPV4)
    ap_dual_stack_dhcp_cfg = _define_ap_ip_cfg(const.DUAL_STACK)
    
    ap_ipv4_static_cfg = _define_ap_ip_cfg(const.IPV4,'static')
    ap_dual_stack_static_cfg = _define_ap_ip_cfg(const.DUAL_STACK,'static')
    
    tcfg = {'restore_zd_ip_cfg': zd_ipv4_cfg,
            'zd_ip_cfg': zd_ipv4_cfg,
            'restore_ap_ip_cfg': ap_dual_stack_dhcp_cfg,
            'ap_mac_addr': ap_mac_addr,
            'ap_ipv4_and_dualstack_cfg_list':[ap_ipv4_dhcp_cfg,ap_dual_stack_dhcp_cfg,ap_ipv4_static_cfg,ap_dual_stack_static_cfg],
            } 
    return tcfg


def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 )
    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    all_ap_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
        
    if ts_cfg["interactive_mode"]:
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    
    active_aps_dict = {}
    for ap_tag in active_ap_list:
        if ap_sym_dict.has_key(ap_tag):
            active_aps_dict[ap_tag] = ap_sym_dict.get(ap_tag)
    
    ap_tag_map = {}
    for key_tag in active_aps_dict:
        mac = ap_sym_dict[key_tag]['mac']
        ap_tag_map[mac]=key_tag
    

    ts_name = 'ZD-Verify IPv4 address column in packet capture configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify display ipv4 column in packet capture', combotest=True)
    tcfg = define_test_parameters(tbcfg, all_ap_mac_list)
    ap_tag_conf = {"ap_tag_map":ap_tag_map}
    tcfg.update(ap_tag_conf)
    
    test_cfgs = define_test_cfg(tcfg)
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