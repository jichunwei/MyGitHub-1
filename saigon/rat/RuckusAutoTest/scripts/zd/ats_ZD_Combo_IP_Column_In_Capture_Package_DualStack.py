"""
Verify Ip address column in packet capture onfiguration.

    Pre-condition:
       AP joins ZD1
       ZD1 is auto approval
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) make sure all APs connect
        2)[system dualstack]set system IP mode is dualstack 
        3)[system dualstack]set all AP mode to ipv4/ipv6/dualstack via randomly selected
        4)[system dualstack]check IP column title
        5)[system dualstack]check IP column value
        6) set system IP mode is dualstack
        7) set all AP IP mode to dualstack 
        8)make sure all APs connect

    
Created on 2014-06-4
@author: Yu.yanan@odc-ruckuswireless.com
"""
import sys

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_KwList as kwlist
import random
import pdb

def define_test_cfg(cfg):
    test_cfgs = []
    list_tmp = []  
    tc_name_sub = "system " 
    
    ap_restore_ip_cfg = cfg['restore_ap_ip_cfg']
    zd_ip_dual_stack_cfg = cfg['zd_ip_dual_stack_cfg']
    zd_restore_ip_cfg = cfg['restore_zd_ip_cfg']

    ap_ip_mode_cfg_list = cfg['ap_ip_mode_cfg_list']
    ap_mac_tag_dict = cfg['ap_tag_map']
    
    round = 0
    step = 0
    round += 1
    
    tc_common_name = tc_name_sub + const.DUAL_STACK
    test_name = 'CB_ZD_CLI_Set_Device_IP_Settings'
    common_name = '[%s]%s.%s set system IP mode is %s ' % (tc_common_name,round, step, const.DUAL_STACK)
    test_cfgs.append(({'ip_cfg': zd_ip_dual_stack_cfg}, test_name, common_name, 1, False))

    for mac_key,tag_value in ap_mac_tag_dict.items(): 
        #@attention: get random and not repeat ap_ip_mode_cfg
        ap_list_len = len(ap_ip_mode_cfg_list)
        if ap_list_len > 0: 
            index = random.randint(0,len(ap_ip_mode_cfg_list)-1)
            if ap_ip_mode_cfg_list[index] in list_tmp and ap_list_len > 1:
                    del ap_ip_mode_cfg_list[index]
                    index = random.randint(0,len(ap_ip_mode_cfg_list)-1)
            list_tmp.append(ap_ip_mode_cfg_list[index])
            ap_ip_mode_cfg = ap_ip_mode_cfg_list[index]
        else:
            ap_ip_mode_cfg = ap_restore_ip_cfg
        
        step += 1
        ap_ip_name_sub = ap_ip_mode_cfg['ip_version']
        if ap_ip_mode_cfg.has_key(const.IPV4):
            ap_mode = ap_ip_mode_cfg[const.IPV4]['ip_mode']
            common_name = '[%s]%s.%s set %s mode to %s %s' % (tc_common_name, round, step,tag_value, ap_ip_name_sub,ap_mode)
        else:
            common_name = '[%s]%s.%s set %s mode to %s ' % (tc_common_name, round, step,tag_value, ap_ip_name_sub)
        
        test_name = 'CB_ZD_CLI_Set_AP_IP_Settings'
        test_cfgs.append(({'ip_cfg': ap_ip_mode_cfg,'ap_mac_list': mac_key,'connect_flag':False}, test_name, common_name, 2, False))
                
        test_name = 'CB_ZD_Make_AP_Connect_To_ZD'
        step += 1 
        common_name = '[%s]%s.%s set %s connect zd' % (tc_common_name, round, step,tag_value)
        test_cfgs.append(({'ip_cfg': ap_ip_mode_cfg,'ap_mac': mac_key}, test_name, common_name, 2, False))
            
            
    test_name = 'CB_ZD_Verify_Packet_Capture_Ip_Column_Title'
    step += 1 
    common_name = '[%s]%s.%s check IP column title' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Packet_Capture_Ip_Column_Value'
    step += 1
    common_name = '[%s]%s.%s check IP column value' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    for mac_key,tag_value in ap_mac_tag_dict.items():            
        test_name = 'CB_ZD_CLI_Set_AP_IP_Settings'
        common_name = 'set %s IP mode to dualstack' %tag_value
        test_cfgs.append(({'ip_cfg': ap_restore_ip_cfg,'ap_mac_list': mac_key,'connect_flag':True}, test_name, common_name, 0, True))
        
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

def _define_zd_ip_cfg(zd_ip_version,zd_ipv4_addr,netmask,gateway,ipv4_pri_dns,zd_ipv6_addr, ipv6_gateway,ipv6_pri_dns, prefix_len):
    zd_ip_cfg = {}
    
    zd_ip_cfg['ip_version'] = zd_ip_version
    if zd_ip_version in [const.IPV4, const.DUAL_STACK]:
        zd_ip_cfg[const.IPV4] = {'ip_alloc': 'static', #dhcp, manual, as-is.
                                 'ip_addr': zd_ipv4_addr,
                                 'netmask': netmask,
                                 'gateway': gateway,
                                 'pri_dns': ipv4_pri_dns,
                                 'sec_dns': '',
                                 }
    if zd_ip_version in [const.IPV6, const.DUAL_STACK]:
        zd_ip_cfg[const.IPV6] = {'ipv6_alloc': 'manual', 
                                 'ipv6_addr': zd_ipv6_addr,
                                 'ipv6_prefix_len': prefix_len,
                                 'ipv6_gateway': ipv6_gateway,
                                 'ipv6_pri_dns': ipv6_pri_dns,
                                 'ipv6_sec_dns': '2020:db8:1::252',
                                 }
    return zd_ip_cfg
def define_test_parameters(tbcfg,ap_mac_addr):
    
    zd_ipv6_addr = tbcfg['ZD']['ip_addr']   
    ipv6_gateway = testsuite.get_ipv6_gateway(tbcfg)
    ipv6_pri_dns = testsuite.get_ipv6_pri_dns(tbcfg)
    prefix_len = testsuite.get_ipv6_prefix_len(tbcfg)
    
    zd_ipv4_addr = testsuite.get_zd_ipv4_addr(tbcfg)
    netmask = testsuite.get_ipv4_net_mask(tbcfg)
    ipv4_gateway = testsuite.get_ipv4_gateway(tbcfg)
    ipv4_pri_dns = testsuite.get_ipv4_pri_dns(tbcfg)
    
    zd_dual_stack_cfg = _define_zd_ip_cfg(const.DUAL_STACK,zd_ipv4_addr, netmask,ipv4_gateway,ipv4_pri_dns,zd_ipv6_addr, ipv6_gateway, ipv6_pri_dns,prefix_len)
    
    ap_ipv4_dhcp_cfg = _define_ap_ip_cfg(const.IPV4)
    ap_ipv6_auto_cfg = _define_ap_ip_cfg(const.IPV6)
    ap_dual_stack_dhcp_cfg = _define_ap_ip_cfg(const.DUAL_STACK)
    
    ap_ipv4_static_cfg = _define_ap_ip_cfg(const.IPV4,'static')
    ap_dual_stack_static_cfg = _define_ap_ip_cfg(const.DUAL_STACK,'static')

    
    tcfg = {'restore_zd_ip_cfg': zd_dual_stack_cfg,
            'zd_ip_dual_stack_cfg': zd_dual_stack_cfg,
            'restore_ap_ip_cfg': ap_dual_stack_dhcp_cfg,
            'ap_mac_addr': ap_mac_addr,
            'ap_ip_mode_cfg_list':[ap_ipv4_dhcp_cfg,ap_dual_stack_dhcp_cfg,ap_ipv6_auto_cfg,ap_ipv4_static_cfg,ap_dual_stack_static_cfg],
            }

    return tcfg


def create_test_suite(**kwargs):  
    ts_cfg = dict(interactive_mode = True,
                 )  
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    all_ap_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
      
    if ts_cfg["interactive_mode"]:
        active_ap_list = testsuite.get_active_ap(ap_sym_dict)
    active_aps_dict = {}
    for ap_tag in active_ap_list:
        if ap_sym_dict.has_key(ap_tag):
            active_aps_dict[ap_tag] = ap_sym_dict.get(ap_tag)
    
    ap_tag_map = {}
    for key_tag in active_aps_dict:
        mac = ap_sym_dict[key_tag]['mac']
        ap_tag_map[mac]=key_tag
    
    ts_name = 'ZD-Verify dualstack address column in packet capture configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify display dualstack column in packet capture', combotest=True)
    tcfg = define_test_parameters(tbcfg,all_ap_mac_list)
    ap_tag_conf = {"ap_tag_map":ap_tag_map}
    tcfg.update(ap_tag_conf)
    test_cfgs = define_test_cfg(tcfg)
  
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.add_test_case(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)