'''
by west.li 2013.1.23
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
CFG_FILE_1='C:\\Documents and Settings\\lab\\My Documents\\Downloads\\full_config.bak'
CFG_FILE_2='C:\\Documents and Settings\\lab\\My Documents\\Downloads\\full_cfg_standby.bak'
HUGE_CFG_SYNC_TIME = 60*60*3
WLAN_SSID = 'WLAN-3'

def define_test_configuration(tcfg):
    test_cfgs = []
    
    wlan_cfg = tcfg['wlan_cfg']
    sta_tag = tcfg['target_sta']
    dest_ip = tcfg['dest_ip']
    pc_dir =  tcfg['pc_dir']

    test_case_name = ''
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = '%sInitial Test Environment'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = '%sget ap number connected with zd'%test_case_name
    param_cfg = dict(timeout = 120, chk_gui = False, zdcli = 'zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%sDisable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
           
    test_name = 'CB_ZD_Create_Station'
    common_name = '%sCreate station: %s' % (test_case_name,sta_tag)
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_case_name = '[full cfg to partial cfg]'
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the full configuration to ZD1'%test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip','zd':'zd1','restore_file_path':CFG_FILE_1}, test_name, common_name, 1, False))    

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the partial configuration to ZD2'%test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip','zd':'zd2','restore_file_path':CFG_FILE_2}, test_name, common_name, 2, False))    

    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD1'%test_case_name
    test_cfgs.append(({'zdcli':'zdcli1','build':'bak1_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in pri zd before SR enable'%test_case_name
    test_cfgs.append(({'zdcli':'zdcli1','prefix':'bak1_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%sboth ZD enable SR(zd1->zd2)' % test_case_name
    test_cfgs.append(({'zd1':'zd1','zd2':'zd2','timeout':HUGE_CFG_SYNC_TIME},test_name,common_name,2,False)) 
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected after enable SR'%test_case_name
    param_cfg = dict(timeout = 120,zdcli='active_zd_cli')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s after sr enable' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s after sr enable' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD1 after SR enable'%test_case_name
    test_cfgs.append(({'build':'sr1_zd1'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in ZD1 after SR enable'%test_case_name
    test_cfgs.append(({'prefix':'sr1_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD2 after SR enable'%test_case_name
    test_cfgs.append(({'build':'sr1_zd2'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in ZD2 after SR enable'%test_case_name
    test_cfgs.append(({'prefix':'sr1_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the zd1 before and after SR configuration by comparing xml files'%test_case_name
    test_cfgs.append(({'scenario':'sr','prefix1':'bak1_zd1','prefix2':'sr1_zd1','pc_dir':pc_dir,'not_cmp_file':['ap-list.xml']},test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the two zds configuration by comparing xml files after SR enable'%test_case_name
    test_cfgs.append(({'scenario':'sr','prefix1':'sr1_zd2','prefix2':'sr1_zd1','pc_dir':pc_dir},test_name, common_name, 2, True))
    
    test_case_name = '[partial cfg to full cfg]'
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%sdisable SR at first'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))    

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the full configuration to ZD1'%test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip','zd':'zd1','restore_file_path':CFG_FILE_2}, test_name, common_name, 1, False))    

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the partial configuration to ZD2'%test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip','zd':'zd2','restore_file_path':CFG_FILE_1}, test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD1'%test_case_name
    test_cfgs.append(({'zdcli':'zdcli1','build':'bak2_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in pri zd before upgrade'%test_case_name
    test_cfgs.append(({'zdcli':'zdcli1','prefix':'bak2_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '%sboth ZD enable SR(zd1->zd2)' % test_case_name
    test_cfgs.append(({'zd1':'zd1','zd2':'zd2','timeout':HUGE_CFG_SYNC_TIME},test_name,common_name,2,False)) 
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected after enable SR'%test_case_name
    param_cfg = dict(timeout = 120,zdcli='active_zd_cli')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s after sr enable' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s after sr enable' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD1 after SR enable'%test_case_name
    test_cfgs.append(({'build':'sr2_zd1'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in ZD1 after SR enable'%test_case_name
    test_cfgs.append(({'prefix':'sr2_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in ZD2 after SR enable'%test_case_name
    test_cfgs.append(({'build':'sr2_zd2'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in ZD2 after SR enable'%test_case_name
    test_cfgs.append(({'prefix':'sr2_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the zd1 before and after SR configuration by comparing xml files'%test_case_name
    test_cfgs.append(({'scenario':'sr','prefix1':'bak2_zd1','prefix2':'sr2_zd1','pc_dir':pc_dir,'not_cmp_file':['ap-list.xml']},test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the two zds configuration by comparing xml files after SR enable'%test_case_name
    test_cfgs.append(({'scenario':'sr','prefix1':'sr2_zd2','prefix2':'sr2_zd1','pc_dir':pc_dir},test_name, common_name, 2, True))
    
    return test_cfgs
    

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="SR enable when both ZD has Huge configuration"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="SR enable when both ZD has Huge configuration"
    wlan_cfg = {
        'ssid':WLAN_SSID ,
        'name':WLAN_SSID ,
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
    
    tcfg = dict(
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                dest_ip= '192.168.0.252',
                pc_dir = 'C://Documents and Settings//lab//My Documents//Downloads'
                )
    test_cfgs = define_test_configuration(tcfg)
    ts = testsuite.get_testsuite(ts_name, "SR enable when both ZD has Huge configuration", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
