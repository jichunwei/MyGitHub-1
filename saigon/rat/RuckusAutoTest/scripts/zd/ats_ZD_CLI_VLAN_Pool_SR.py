'''
Created on Dec 15, 2014

@author: chen.tao@odc-ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    sta_tag = 'sta%s' % radio_mode

    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
                                    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs on ZD1'
    test_cfgs.append(({'zdcli_tag':'zdcli1'}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs on ZD2'
    test_cfgs.append(({'zdcli_tag':'zdcli2'}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = 'Try to del all vlan pools on ZD1.'
    test_params = {'del_all':True,'zdcli_tag':'zdcli1'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = 'Try to del all vlan pools on ZD2.'
    test_params = {'del_all':True,'zdcli_tag':'zdcli2'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
############################################################

    test_case_name = '[vlan_pool_in_sr]'
    num = 0
    idx = '1.%s' 

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool on active ZD'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_sr_test",'vlan':'10'},
                   'zdcli_tag':'active_zd_cli'}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    open_none_wlan = {
             "name" : "VLAN_POOL_SR_Test",
             "ssid" : "VLAN_POOL_SR_Test",
             "type" : "standard-usage",
             "auth" : "open",
             "encryption" : "none",
             'vlanpool':'vlan_pool_sr_test',
             "dvlan" : "True"}
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a open none WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': open_none_wlan,
                       'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': open_none_wlan}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10'],
                       'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover the active ZD' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': open_none_wlan}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10'],
                       'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover the active ZD' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': open_none_wlan}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10'],
                       'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test'%(test_case_name + idx%(num))
    test_params = {'del_all':True,'zdcli_tag':'active_zd_cli'}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on the two ZDs' 
    test_cfgs.append(({},test_name, common_name, 0, True))
    
    return test_cfgs
def make_test_suite(**kwargs):

    attrs = dict(interactive_mode = True,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ") 
    target_sta_radio = testsuite.get_target_sta_radio()    
    active_ap = active_ap_list[0]   
    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            }
    test_cfgs = define_test_cfg(tcfg)
#----------------------------------------------------------------------------------------------------------
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "VLAN_POOL_Smart_Redundancy" 
            
    ts = testsuite.get_testsuite(ts_name,'VLAN_POOL_Smart_Redundancy',combotest=True)
#----------------------------------------------------------------------------------------------------------
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
    make_test_suite(**_dict)



