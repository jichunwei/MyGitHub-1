'''
by west.li 2012.2.2
zd upgrade from base build to target build
step is as below:
    download both base build and target build zd img
    upgrade zd to base build
    add configuration to zd by restoring configuration file
    get xml file list in zd
    download all xml files from zd
    upgrade
    get all xml files in zd
    compare xml files
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = []    
    upgrade_waiting = 10
    
    wlan_cfg = tcfg['wlan_cfg']
    ap_tag = tcfg['active_ap']
    sta_tag = tcfg['target_sta']
    radio_mode = tcfg['active_radio']
    dest_ip = tcfg['dest_ip']
    
    test_name = 'CB_ZD_Cmb_Upgrade_Init'
    common_name = 'read parameter from upgrade_parameter' 
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name='[Download zd img]'
    test_name = 'CB_ZD_Download_ZD_Img'
    common_name = '%sDownload ZD img from build server' % test_case_name
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_case_name='[test prepration]'
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%sDisable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 0, False))    
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '%sbefore upgrade set zd1 Factory default' % test_case_name
    test_cfgs.append(({'zd':'zd1'},test_name, common_name, 0, False))  
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '%sbefore upgrade set zd2 Factory default' % test_case_name
    test_cfgs.append(({'zd':'zd2'},test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_SR_Single_Upgrade'
    common_name = '%sUpgrade two ZD to base build one by one' % test_case_name
    test_cfgs.append(({'build':'base'},test_name,common_name,0,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = 'Waiting upgrade to base build for %d mins ' % upgrade_waiting
    test_cfgs.append(({'timeout':upgrade_waiting*60}, test_name, common_name, 0, False))
    
    test_case_name='[SR Enable and Check version]'
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%sEnable Smart Redundancy ready to do test' % test_case_name
    test_cfgs.append(({"timeout":1000},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the Standby ZD version, make sure the Standby base build is correct' % test_case_name
    test_cfgs.append(({'build':'base','zd_type':'standby'},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD version, make sure the Standby base build is correct' % test_case_name
    test_cfgs.append(({'build':'base','zd_type':'active'},test_name,common_name,0,False))
    
    test_case_name='[get ap number before upgrade]'
    test_name = 'CB_ZD_Get_Ap_Num_From_Web'
    common_name = '%sget ap number connected with zd before upgrade'%test_case_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_case_name='[Add configuration by restoring CFG file]'
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the configuration to ZD'% test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip'}, test_name, common_name, 1, False))    
    
    test_case_name='[Download base build xml files in active zd]'
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = '%sGet the Active ZD.'% test_case_name
    test_cfgs.append(({},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD' % test_case_name
    test_cfgs.append(({'build':'base'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files before upgrade' % test_case_name
    test_cfgs.append(({'prefix':'base'},test_name, common_name, 1, False))
    
    test_case_name='[Download base build xml files in standby zd]'
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in standby ZD' % test_case_name
    test_cfgs.append(({'build':'base_standby'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in standby zd before upgrade' % test_case_name
    test_cfgs.append(({'prefix':'base_standby'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the configuration by comparing xml files in active zd and standby zd before upgrade' % test_case_name
    test_cfgs.append(({'scenario':'sr','prefix2':'base_standby'},test_name, common_name, 2, False))
    
    test_case_name='[Upgrade zd to target build]'
    test_name = 'CB_ZD_SR_Upgrade'
    common_name = '%sUpgrade the 2 zds to target build' % test_case_name
    test_cfgs.append(({'build':'target'},test_name,common_name,1,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = 'Waiting upgrade for %d mins ' % upgrade_waiting
    test_cfgs.append(({'timeout':upgrade_waiting*60}, test_name, common_name, 1, False))
    
    test_case_name='[check target version]'
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the standby ZD was upgraded successfully' % test_case_name
    test_cfgs.append(({'build':'target','zd_type':'standby'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD was upgraded successfully' % test_case_name
    test_cfgs.append(({'build':'target','zd_type':'active'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_Check_Ap_Version_After_Upgrade'
    common_name = '%sCheck the ap version, make sure the ap was upgraded' % test_case_name
    test_cfgs.append(({'action':'upgrade'},test_name,common_name,2,False))
    
    test_case_name='[check ap number after upgrade]'
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = '%sGet the Active ZD' % test_case_name
    test_cfgs.append(({},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_Check_Ap_Num_From_Web'
    common_name = '%sCheck all of APs are connected after upgrade' % test_case_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_case_name='[Download target build xml files]'
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in active ZD after upgrade' % test_case_name
    test_cfgs.append(({'build':'target_active'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in active ZD after upgrade' % test_case_name
    test_cfgs.append(({'prefix':'target_active'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in standby ZD after upgrade ' % test_case_name
    test_cfgs.append(({'build':'target_standby'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in standby ZD after upgrade' % test_case_name
    test_cfgs.append(({'prefix':'target_standby'},test_name, common_name, 1, False))
    
    test_case_name='[Compare the configuration]'
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the configuration by comparing xml files in active zd before upgrade and stangby zd after upgrade' % test_case_name
    test_cfgs.append(({'scenario':'upgrade','prefix2':'target_standby'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the configuration by comparing xml files in active zd before upgrade and active zd after upgrade' % test_case_name
    test_cfgs.append(({'scenario':'upgrade_and_sr','prefix2':'target_active'},test_name, common_name, 2, True))
    
    test_case_name='[test %s client associate with ap]'%tcfg['active_radio']
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = '%sCreate AP: %s' % (test_case_name,ap_tag)
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = '%sCreate station: %s' % (test_case_name,sta_tag)
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "%sCreate WLAN group: %s" % (test_case_name,tcfg['wg_cfg']['name']) 
    test_cfgs.append(({'wgs_cfg': tcfg['wg_cfg']}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Create_Single_Wlan'
    common_name = "%sCreate WLAN : %s" % (test_case_name,wlan_cfg['ssid']) 
    test_cfgs.append(({'wlan_cfg': wlan_cfg}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_Wlan_On_Wlan_Group'
    common_name = "%sassign WLAN %s to group: %s" % (test_case_name,wlan_cfg['ssid'],tcfg['wg_cfg']['name']) 
    test_cfgs.append(({'wlan_list':[wlan_cfg['ssid']],'wgs_cfg': tcfg['wg_cfg']}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign the WLAN group to radio '%s' of AP: %s" % (test_case_name,radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s ' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_case_name='[restore Enviroment]'
    test_name = 'CB_ZD_Remove_ZD_Img_From_Pc'
    common_name = '%sremove zd img from PC after the test' % test_case_name
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    return test_cfgs
    

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="SR enable zd upgrade only"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an active AP: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            
            else:
                active_ap_mac=ap_sym_dict[active_ap]['mac']
                break
        target_sta = testsuite.getTargetStation(sta_ip_list)
        active_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="single zd upgrade only"
    
    wlan_cfg = {
        'ssid': "new_wlan_after_upgrade-%s" % time.strftime("%H%M%S"),
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
    
    wg_cfg = {
        'name': 'rat-wg-upgrade-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for upgrade test',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    tcfg = dict(active_ap = active_ap_mac,
                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                wg_cfg = wg_cfg,
                dest_ip= '192.168.0.252'
                )
    
    test_cfgs = define_test_configuration(tcfg)
    ts = testsuite.get_testsuite(ts_name, "sr enable zd upgrade only", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
