# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2012

This testsuite is configure to allow testing follow test cases - which are belong to Configure WLAN - QoS:


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    
    tcnames = ['One IPv4 subnet - No DHCP server',
               'One IPv4 subnet - With DHCP server',
               'One IPv4 subnet - AP find ZD by DHCP option 15',
               'One IPv4 subnet - AP find ZD by DHCP option 43',
               'One IPv4 subnet - AP find ZD by pre-configured',              
               'One IPv4 subnet - AP find ZD by FQDN',
               'One IPv4 subnet - AP find ZD by last controller', 
               'One IPv4 subnet - AP with static IP',
               'Two IPv4 subnets - With DHCP server',
               'Two IPv4 subnets - No DHCP server',
               'Two IPv4 subnets - AP find ZD by DHCP option 15',
               'Two IPv4 subnets - AP find ZD by DHCP option 43',
               'Two IPv4 subnets - AP find ZD by pre-configured',                              
               'Two IPv4 subnets - AP find ZD by FQDN',
               'Two IPv4 subnets - AP find ZD by last controller',
               'Two IPv4 subnets - AP with static IP',]
    
    
    zd_ip_address = '192.168.0.2'
    zd_dn_for_fqdn = 'zonedirector.example.net'
    ap_tag = 'AP1'
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    
    for tcname in tcnames :
        if 'No DHCP server' in tcname:                   
            test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
            common_name = '[%s] Disable the DHCP server' % tcname
            test_cfgs.append(({'start_server': False}, test_name, common_name, 1, False))
        
        if 'With DHCP server' in tcname:
            test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
            common_name = '[%s] Enable the DHCP server' % tcname
            test_cfgs.append(({'start_server': True}, test_name, common_name, 1, False))
        
        if 'DHCP option 15' in tcname:
            test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
            common_name = '[%s] Enable DHCP option 15 and disable option 43' % tcname
            test_cfgs.append(({'option_list': [{'name': 'option 15', 'action': 'enable'},
                                               {'name': 'option 43', 'action': 'disable'}],
                               'start_server': True}, test_name, common_name, 1, False))
        
        if 'DHCP option 43' in tcname:
            test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
            common_name = '[%s] Enable DHCP option 43 and disable option 15' % tcname
            test_cfgs.append(({'option_list': [{'name': 'option 15', 'action': 'disable'},
                                               {'name': 'option 43', 'action': 'enable'}],
                               'start_server': True}, test_name, common_name, 1, False))
                                
        if 'pre-configured' in tcname:
            test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
            common_name = '[%s] Configure primary ZD IP address via AP CLI' % tcname
            test_params = {'ap_tag': ap_tag,
                           'primary_zd_ip': zd_ip_address
                           }
            test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        if 'FQDN' in tcname:
            test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
            common_name = '[%s] Configure FQDN via AP CLI' % tcname
            test_params = {'ap_tag': ap_tag,
                           'primary_zd_ip': zd_dn_for_fqdn
                           }
            test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        if 'last controller' in tcname:
            test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
            common_name = '[%s] Delete pre-configured ZD info' % tcname
            test_params = {'ap_tag': ap_tag}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        if 'static' in tcname:
            test_name = 'CB_ZD_Config_AP_IP_Settings'
            common_name = '[%s] Set static IP for AP' % tcname
            test_params = {'ap_tag': ap_tag,
                           'ip_cfg': {'ip_version': 'ipv4',
                                      'ipv4': {'pri_dns': '192.168.0.252', 
                                               'net_mask': '255.255.255.0', 
                                               'ip_addr': '192.168.0.123' if 'One IPv4' in tcname else '192.168.33.123', 
                                               'gateway': '192.168.0.253' if 'One IPv4' in tcname else '192.168.33.253', 
                                               'ip_mode': 'manual'}
                                     }}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
                    
        
        test_name = 'CB_ZD_Delete_APs'
        common_name = '[%s] Remove the active AP' % tcname
        test_cfgs.append(({'ap_tag': ap_tag}, test_name, common_name, 2, False))
        
        if 'No DHCP server' in tcname:
            common_name = '[%s] Verify %s can not reconnect to ZD' % (tcname, ap_tag)
            is_allow = False
        else:
            common_name = '[%s] Verify %s reconnect to ZD' % (tcname, ap_tag)
            is_allow = True
            
        test_name = 'CB_ZD_Verify_AP_Join'
        test_cfgs.append(({'ap_tag': ap_tag,
                           'is_allow': is_allow}, test_name, common_name, 2, False))
        
        # cleanup test cases     
        
        if 'static' in tcname:
            test_name = 'CB_ZD_Config_AP_IP_Settings'
            common_name = '[%s] Set DHCP IP for AP' % tcname
            test_params = {'ap_tag': ap_tag,
                           'ip_cfg': {'ip_version': 'ipv4',
                                      'ipv4': {'ip_mode': 'dhcp'}}}
            test_cfgs.append((test_params, test_name, common_name, 2, True))
        
            if 'One IPv4 subnet' in tcname:
                test_name = 'CB_ZD_Reconnect_AP_By_LWAPP'
                common_name = 'Reconnect Active AP to ZD via L3LWAPP'
                test_params = {'ap_tag': ap_tag,
                               'mode': 'l3',
                               'discovery_method': 'dhcp',}
                test_cfgs.append((test_params, test_name, common_name, 0, False))
            
            if 'Two IPv4 subnets' in tcname:
                test_name = 'CB_ZD_Reconnect_AP_By_LWAPP'
                common_name = 'Reconnect Active AP to ZD in same subnet'
                test_params = {'ap_tag': ap_tag,
                               'mode': 'l2',
                               'discovery_method': 'dhcp',}
                test_cfgs.append((test_params, test_name, common_name, 0, True))
        
        if 'DHCP option 43' in tcname:
            test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
            common_name = '[%s] Recover the DHCP server option' % tcname
            test_cfgs.append(({'option_list': [{'name': 'option 15', 'action': 'enable'},
                                               {'name': 'option 43', 'action': 'enable'}],
                               'start_server': True}, test_name, common_name, 2, True))
        
    
    return test_cfgs
 
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = testsuite.getActiveAp(ap_sym_dict)[0]            

        
    test_cfgs = define_test_cfg({'active_ap': active_ap})
        
    ts_name = "IPv4 LWAPP Discovery Optimization"
    ts = testsuite.get_testsuite(ts_name, "Verify IPv4 LWAPP Discovery Optimization", combotest=True)
    
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
    createTestSuite(**_dict)
