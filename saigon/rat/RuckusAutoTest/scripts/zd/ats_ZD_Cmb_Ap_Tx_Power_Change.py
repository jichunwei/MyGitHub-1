'''
by west.li 
ap tx power change test
step:
1.remove all ap group in zd to make sure all aps belong to default ap group
2.set country code in zd web
3.enable mesh in zd web
4.do ap tx power change test(both for 2.4G and 5G)
    a.set 'full' in ap tx power in zd web
    b.get full power value in ap cli
    c.set ap tx power change value to different value in zd web and verfy the txpower in ap shell
    d.set default ap group tx power change value,different from aps setting,verify the value in ap is the same with ap group 
5.do the corresponding operation of step 4 in zd cli
7.restore the enviroment by set zd factory default(restore country code and disable mesh) 
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_configuration(ap_mac_list,list_of_radio_list,country_code,wlan_cfg,wg_cfg,target_sta,dest_ip):
    test_cfgs = [] 
    test_name = 'CB_ZD_Set_Factory_Default' 
    common_name = 'clean environment by set zd to factory default'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'set country to %s'%(country_code)
    test_cfgs.append(({'country_code':country_code},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mesh' 
    common_name = 'enable zd mesh,no switch port will be disabled'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station'
    test_params = {'sta_tag': target_sta, 'sta_ip_addr': target_sta}
    test_cfgs.append((test_params, test_name, common_name, 1, True))
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create WLAN group: %s" % (wg_cfg['name']) 
    test_cfgs.append(({'wgs_cfg': wg_cfg,'add_wlan':False}, test_name, common_name, 1, True))
    
    test_name = 'CB_ZD_Create_Single_Wlan'
    common_name = "Create WLAN : %s" % (wlan_cfg['ssid']) 
    test_cfgs.append(({'wlan_cfg': wlan_cfg}, test_name, common_name, 1, True))
    
    test_name = 'CB_ZD_Config_Wlan_On_Wlan_Group'
    common_name = "assign WLAN %s to group: %s" % (wlan_cfg['ssid'],wg_cfg['name']) 
    test_cfgs.append(({'wlan_list':[wlan_cfg['ssid']],'wgs_cfg': wg_cfg}, test_name, common_name, 1, True))
    
    test_case_name='[ZD web ap tx power change test]' 
    test_name = 'CB_ZD_Ap_Tx_Power_Change_Test' 
    common_name = '%scheck ap tx power change function in zd web UI'%(test_case_name)
    test_params={'ap_mac_list':ap_mac_list,
                 'list_of_radio_list':list_of_radio_list,
                 'wlan_group_name':wg_cfg['name'],
                 'sta_tag':target_sta,
                 'wlan_cfg': wlan_cfg,
                 'ping_timeout_ms': 10000, 
                 'dest_ip': dest_ip}
    test_cfgs.append((test_params,test_name, common_name, 1, False))
    
    test_case_name='[ZD cli ap tx power change test]' 
    test_name = 'CB_ZDCLI_Ap_Tx_Power_Change_Test' 
    common_name = '%scheck ap tx power change function in zd CLI'%(test_case_name)
    test_params={'ap_mac_list':ap_mac_list,
                 'list_of_radio_list':list_of_radio_list,
                 'wlan_group_name':wg_cfg['name'],
                 'sta_tag':target_sta,
                 'wlan_cfg': wlan_cfg,
                 'ping_timeout_ms': 10000, 
                 'dest_ip': dest_ip}
    test_cfgs.append((test_params,test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Set_Factory_Default' 
    common_name = 'set zd to factory to disable mesh and restore country code'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs
    

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="ap tx power change test"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        
        while True:
            ap_list = raw_input("Choose one or more APs you want to test(split by space):")
            ap_list = ap_list.split()
            ap_mac_list=[]
            list_of_radio_list=[]
            model_test=''
            for ap in ap_list:
                if ap not in ap_sym_dict:
                    print "AP[%s] doesn't exist." % ap
                    
                else:
#                    import pdb
#                    pdb.set_trace()
                    model_test+=" %s"%ap_sym_dict[ap]['model']
                    radios_list=[]
                    radios_l=const._ap_model_info[ap_sym_dict[ap]['model'].lower()]['radios']
                    if 'bg' in radios_l or 'ng' in radios_l:
                        radios_list.append('2.4')
                    if 'na' in radios_l:
                        radios_list.append('5')
                    ap_mac_list.append(ap_sym_dict[ap]['mac'])
                    list_of_radio_list.append(radios_list)
                
            if len(ap_mac_list)==len(ap_list) and ap_mac_list:
                break
            else:
                print('you input some invalid parameter,please input again')
            
        print('%d ap will be test,they are %s'% (len(ap_mac_list),ap_mac_list))
        country_code=raw_input("please input country code you want to test,default is United Kingdom:")
        if not country_code:
            country_code='United Kingdom'
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    name="ap tx power change test country code %s %s"%(country_code,model_test)
    attrs['testsuite_name']=name
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name =name
    wlan_cfg = {
    'ssid': "new_wlan_for_txpower-%s" % time.strftime("%H%M%S"),
    'auth': "open", 
    'wpa_ver': "", 
    'encryption': "none",
    'key_index': "", 
    'key_string': "",
    'do_webauth': False, 
    }
    
    wg_cfg = {
        'name': 'rat-wg-txpower-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for upgrade test',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    
    dest_ip= '192.168.0.252'
    test_cfgs = define_test_configuration(ap_mac_list,list_of_radio_list,country_code,wlan_cfg,wg_cfg,target_sta,dest_ip)
    ts = testsuite.get_testsuite(ts_name,name, interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
