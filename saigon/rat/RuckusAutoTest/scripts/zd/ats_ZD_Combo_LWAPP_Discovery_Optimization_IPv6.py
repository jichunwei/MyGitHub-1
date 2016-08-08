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
    
    tcnames = ['IPv6 - No DHCP server',
               'IPv6 - With DHCP server',
               'IPv6 - AP find ZD by pre-configured',              
               'IPv6 - AP find ZD by FQDN',
               'IPv6 - AP find ZD by last controller', 
               'IPv6 - AP with static IP',
               ]    
    
    zd_ip_address = '2020:db8:1::2'
    zd_dn_for_fqdn = 'www.ruckuszdipv6.net'
    ap_tag = 'AP1'
    
    dhcp_service_name = 'radvd'
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    
    for tcname in tcnames :
        if 'No DHCP server' in tcname:                
            test_name = 'CB_LinuxPC_Config_DHCPv6_Server_Option'
            common_name = '[%s] Disable the DHCP server' % tcname
            test_cfgs.append(({'start_server': False,
                               'dhcp_service_name': dhcp_service_name}, test_name, common_name, 1, False))
        
        if 'With DHCP server' in tcname:
            test_name = 'CB_LinuxPC_Config_DHCPv6_Server_Option'
            common_name = '[%s] Enable the DHCP server' % tcname
            test_cfgs.append(({'start_server': True,
                               'dhcp_service_name': dhcp_service_name}, test_name, common_name, 1, False))
        
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
            test_name = 'CB_ZD_Config_AP_IPv6_Settings'
            common_name = '[%s] Set static IP for AP' % tcname
            test_params = {'ap_tag': ap_tag,
                           'ip_cfg': {'ip_version': 'ipv6',
                                      'ipv6': {'ipv6_pri_dns': '2020:db8:1::252', 
                                               'ipv6_sec_dns': '',
                                               'ipv6_addr': '2020:db8:1::123',
                                               'ipv6_gateway': '2020:db8:1::251', 
                                               'ipv6_mode': 'manual'}
                                     }}
            test_cfgs.append((test_params, test_name, common_name, 1, False))                    
        if 'With DHCP server' not in tcname:
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
            test_name = 'CB_ZD_Config_AP_IPv6_Settings'
            common_name = '[%s] Set DHCP IP for AP' % tcname
            test_params = {'ap_tag': ap_tag,
                           'ip_cfg': {'ip_version': 'ipv6',
                                      'ipv6': {'ipv6_mode': 'auto'}}}
            test_cfgs.append((test_params, test_name, common_name, 2, True))
        
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
        
    ts_name = "IPv6 LWAPP Discovery Optimization"
    ts = testsuite.get_testsuite(ts_name, "Verify IPv6 LWAPP Discovery Optimization", combotest=True)
    
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
