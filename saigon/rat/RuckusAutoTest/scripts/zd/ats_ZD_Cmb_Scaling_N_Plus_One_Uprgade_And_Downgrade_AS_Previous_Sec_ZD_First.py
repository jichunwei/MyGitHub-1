'''
by west.li 2013.1.23
'''

import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = []
    upgrade_waiting = 10
    
    wlan_cfg = tcfg['wlan_cfg']
    mesh_ap_mac = tcfg['mesh_ap']
    sta_tag = tcfg['target_sta']
    dest_ip = tcfg['dest_ip']
    zd1_ip =  tcfg['zd1_ip']
    zd2_ip =  tcfg['zd2_ip']
    wg_name = tcfg['wlan_group_name']
    ap_group_cfg = tcfg['ap_group_cfg']
    pc_dir =  tcfg['pc_dir']
    ap_check_in_default_group = tcfg['mac_addr_check_in_default_group']
    ap1 = random.choice(ap_group_cfg['add_members'])
    ap2 = random.choice(ap_check_in_default_group)
    ap_list_check_version = [ap1,ap2]
    upgrade_timeout = 7200
    switch_zd_timeout = 1800
    sim_models = 'ss7962'
    
    import os
    save_to = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads" )
    
    test_case_name = '[prepare environment]'
    test_name = 'CB_ZD_Cmb_Upgrade_Init'
    common_name = '%sread parameter from upgrade_parameter'%test_case_name
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = '%sInitial Test Environment'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = '%sget ap number connected with zd'%test_case_name
    param_cfg = dict(timeout = 120, chk_gui = False, zdcli = 'zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    

    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = '%sconfig AP policy in sec zd'%test_case_name
    test_para = {
                'auto_approve':False,
                'vlan_id':'',
                'limited_zd_discovery':{
                                          'enabled':True,
                                          'primary_zd_ip':zd1_ip,
                                          'secondary_zd_ip':zd2_ip,
                                          'keep_ap_setting':False,
                                          'prefer_prim_zd':True,
                                        },
                'zdcli':'zdcli2'
                }
    test_cfgs.append((test_para,test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Remove_AP'
    common_name = '%sremove aps from zd2 ap list'%test_case_name
    mac_list =  ap_group_cfg['add_members']+ap_check_in_default_group
    test_cfgs.append(( {'ap_mac_list':mac_list,'zdcli':'zdcli2'}, test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the configuration to ZD'%test_case_name
    test_cfgs.append(({'restore_type':'restore_everything_except_ip','zd':'zd1'}, test_name, common_name, 0, False))    
#    
#    test_name = 'CB_ZD_Enable_Mesh'
#    common_name = 'Enable mesh in ZD and disable switch port connectet to ap %s,let it become mesh ap'% mesh_ap_mac
#    test_cfgs.append(({'mesh_ap_mac_list':[mesh_ap_mac]},test_name, common_name, 2, False))
#    
    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = '%sconfig AP policy in primiary zd'%test_case_name
    test_para = {
                'auto_approve':True,
                'vlan_id':'',
                'limited_zd_discovery':{
                                          'enabled':True,
                                          'primary_zd_ip':zd1_ip,
                                          'secondary_zd_ip':zd2_ip,
                                          'keep_ap_setting':False,
                                          'prefer_prim_zd':True,
                                        },
                'zdcli':'zdcli1'
                }
    test_cfgs.append((test_para,test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = '%screate wlan %s for data plan verification'%(test_case_name,wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_conf':wlan_cfg,'zdcli':'zdcli1'},test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Remove_Wlan_Out_Of_Wlan_Group'
    common_name = '%sremove wlan %s out of default wlan group'%(test_case_name,wlan_cfg['ssid'])
    test_cfgs.append(({'zdcli':'zdcli1','wlan_name_list':[wlan_cfg['ssid']],'wlan_group_name':'Default'},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_WLAN_Groups'
    common_name = '%sadd new wlan group %s,add wlan %s in it'%(test_case_name,wg_name,wlan_cfg['ssid'])
    wg_cfg =    {'wg_name': wg_name,
                 'wlan_member': {
                                 wlan_cfg['ssid']: {},
                                }
                }
    test_cfgs.append(({'zdcli':'zdcli1','wg_cfg_list':[wg_cfg],},test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_New_AP_Group'
    common_name = '%screate new ap group %s'%(test_case_name,ap_group_cfg['name'])
    ap_group_cfg.update({'zdcli':'zdcli1'})
    test_cfgs.append((ap_group_cfg,test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '%smesh ap set factory default before upgrade'%test_case_name
    test_cfgs.append(({'ap_mac':[mesh_ap_mac]},test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Wait_AP_Connect'
    common_name = '%swait ap connected after set factory'%test_case_name
    test_cfgs.append(({'ap_mac':mesh_ap_mac,'zd_tag':'zdcli1'},test_name, common_name, 0, False))

    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '%sDisable switch port connected to mesh ap'%test_case_name
    test_cfgs.append(({'disable_mac_list':[mesh_ap_mac],'device':'ap','for_mesh':True,'zdcli':'zdcli1'},test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Wait_AP_Connect'
    common_name = '%swait ap connected to zd as mesh ap'%test_case_name
    test_cfgs.append(({'ap_mac':mesh_ap_mac,'zd_tag':'zdcli1'},test_name, common_name, 0, False))

    test_name = 'CB_Scaling_Backup_Config'
    common_name = '%sBackup ZD1 under batch configurations'%test_case_name
    test_cfgs.append(( {'zd':'zd1','filename':'Nplusone_upgrade.bak'}, test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore ZD2 under batch configurations' %test_case_name
    test_cfgs.append(( {'zd':'zd2','restore_type':'restore_everything_except_ip'}, test_name, common_name, 0, False))    
    
    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = '%sconfig AP policy in secondary zd'%test_case_name
    test_para = {
                'auto_approve':True,
                'mgmt_vlan':'keeping',
                'limited_zd_discovery':{
                                          'enabled':True,
                                          'keep_ap_setting':True,
                                        },
                'zdcli':'zdcli2'
                }
    test_cfgs.append((test_para,test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Remove_AP'
    common_name = '%safter config,remove aps from zd2 ap list'%test_case_name
    mac_list =  ap_group_cfg['add_members']+ap_check_in_default_group
    test_cfgs.append(( {'ap_mac_list':mac_list,'zdcli':'zdcli2'}, test_name, common_name, 0, False))    
    
    test_case_name = '[upgrade test]'
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in pri ZD'%test_case_name
    test_cfgs.append(({'build':'base_sec_zd1'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in pri zd before upgrade'%test_case_name
    test_cfgs.append(({'prefix':'base_sec_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in sec ZD'%test_case_name
    test_cfgs.append(({'build':'base_sec_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in sec zd before upgrade'%test_case_name
    test_cfgs.append(({'prefix':'base_sec_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build'%test_case_name
    param_cfg = dict(timeout = 60,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    
    
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name = '%supgrade sec zd to target build'%test_case_name
    test_cfgs.append(({'zd':'zd2','zdcli':'zdcli2','build':'target'},test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting sec zd upgrade to target build for %d mins '  %(test_case_name,upgrade_waiting)
    test_cfgs.append(({'timeout':upgrade_waiting*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Version'
    common_name = '%sCheck the ZD(zd2) version, make sure the ZD was upgraded' %test_case_name
    test_cfgs.append(({'build':'target','zd':'zd2','zdcli':'zdcli2'},test_name,common_name,0,False))   
    
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to zd2.'%test_case_name
    param_cfg = dict(build='target',sim_models = sim_models,zd='zd2')    
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
        
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name = '%supgrade pri zd to target build'%test_case_name
    test_cfgs.append(({'zd':'zd1','zdcli':'zdcli1','build':'target'},test_name, common_name, 1, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting pri zd upgrade to target build for %d mins ' % (test_case_name,upgrade_waiting)
    test_cfgs.append(({'timeout':upgrade_waiting*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Version'
    common_name = '%sCheck the ZD version, make sure the ZD was upgraded' %test_case_name
    test_cfgs.append(({'build':'target','zd':'zd1','zdcli':'zdcli1'},test_name,common_name,0,False))   
    
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to zd1.'%test_case_name
    param_cfg = dict(build='target',sim_models = sim_models,zd='zd1')    
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
        
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP after upgrade to target build' %test_case_name
    param_cfg = dict(timeout = upgrade_timeout,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Check_Ap_Version_After_Upgrade'
    common_name = '%sCheck the ap version, make sure the ap was upgraded' %test_case_name
    test_cfgs.append(({'action':'upgrade','ap_mac_list':ap_list_check_version},test_name,common_name,2,False))
        
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in pri ZD after upgrade'%test_case_name
    test_cfgs.append(({'build':'target_sec_zd1'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in pri zd after upgrade'%test_case_name
    test_cfgs.append(({'prefix':'target_sec_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in sec ZD after upgrade'%test_case_name
    test_cfgs.append(({'build':'target_sec_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in sec zd after upgrade'%test_case_name
    test_cfgs.append(({'prefix':'target_sec_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the pri zd configuration by comparing xml files before and after upgrade'%test_case_name
    test_cfgs.append(({'scenario':'upgrade','prefix1':'base_sec_zd1','prefix2':'target_sec_zd1','pc_dir':pc_dir},test_name, common_name, 1, False))

    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the sec zd configuration by comparing xml files before and after upgrade'%test_case_name
    test_cfgs.append(({'scenario':'upgrade','prefix1':'base_sec_zd2','prefix2':'target_sec_zd2','not_cmp_file':['ap-list.xml','apgroup-list.xml'],'pc_dir':pc_dir},test_name, common_name, 2, True))
    
    test_case_name = '[N+1 function test]'
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '%sDisable switch port connectet pri zd' % test_case_name
    test_cfgs.append(({'zdcli':'zdcli1','device':'zd'},test_name, common_name, 1, False))   
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to second zd' %test_case_name
    param_cfg = dict(timeout = switch_zd_timeout,zdcli='zdcli2')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Create_Station'
    common_name = '%sCreate station: %s' % (test_case_name,sta_tag)
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s after aps switch sec zd' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s after aps switch sec zd' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZDCLI_Verify_AP_APgroup_Name'
    common_name = '%sin sec zd,verify the aps in default ap group' % (test_case_name)
    test_params = {'zdcli':'zdcli2','ap_mac_list':ap_check_in_default_group,'apg_name':'System Default'}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Verify_AP_APgroup_Name'
    common_name = '%sin sec zd,verify the aps in ap group%s' % (test_case_name,ap_group_cfg['name'])
    test_params = {'zdcli':'zdcli2','ap_mac_list':ap_group_cfg['add_members'],'apg_name':ap_group_cfg['name']}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable sw port connected to pri zd' % test_case_name
    test_cfgs.append(({'device':'zd'},test_name, common_name, 1, False)) 
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to pri zd' %test_case_name
    param_cfg = dict(timeout = switch_zd_timeout,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s after aps switch back to pri zd' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s after aps switch back to pri zd' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_case_name='[downgrade back]'
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name = '%sdowngrade sec zd to base build'%test_case_name
    test_cfgs.append(({'zd':'zd2','zdcli':'zdcli2','build':'base'},test_name, common_name, 1, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting sec zd downgrade to base build for %d mins '  %(test_case_name,upgrade_waiting)
    test_cfgs.append(({'timeout':upgrade_waiting*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Version'
    common_name = '%sCheck the ZD version, make sure the ZD was downgrade' %test_case_name
    test_cfgs.append(({'build':'base','zd':'zd2','zdcli':'zdcli2'},test_name,common_name,0,False))   
    
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall base SIMAP Image to zd2.'%test_case_name
    param_cfg = dict(build='base',sim_models = sim_models,zd='zd2')    
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
        
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name = '%sdowngrade pri zd to base build'%test_case_name
    test_cfgs.append(({'zd':'zd1','zdcli':'zdcli1','build':'base'},test_name, common_name, 1, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting pri zd downgradegrade to target build for %d mins ' % (test_case_name,upgrade_waiting)
    test_cfgs.append(({'timeout':upgrade_waiting*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Version'
    common_name = '%sCheck the ZD version, make sure the ZD was downgraded back' %test_case_name
    test_cfgs.append(({'build':'base','zd':'zd1','zdcli':'zdcli1'},test_name,common_name,0,False))   
    
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall base SIMAP Image to zd1.'%test_case_name
    param_cfg = dict(build='base',sim_models = sim_models,zd='zd1')    
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
        
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP after upgrade to target build' %test_case_name
    param_cfg = dict(timeout = upgrade_timeout,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in pri ZD after upgrade and downgrade'%test_case_name
    test_cfgs.append(({'build':'base2_sec_zd1'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in pri zd after upgrade and downgrade'%test_case_name
    test_cfgs.append(({'prefix':'base2_sec_zd1'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Xml_File_List_In_ZD'
    common_name = '%sget xml file list in sec ZD after upgrade and downgrade'%test_case_name
    test_cfgs.append(({'build':'base2_sec_zd2'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '%sDownload xml files in sec zd after upgrade and downgrade'%test_case_name
    test_cfgs.append(({'prefix':'base2_sec_zd2'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the pri zd configuration by comparing xml files before and after upgrade'%test_case_name
    test_cfgs.append(({'scenario':'upgrade','prefix1':'base_sec_zd1','prefix2':'base2_sec_zd1','pc_dir':pc_dir},test_name, common_name, 2, True))

    test_name = 'CB_ZD_Compare_Xml_Files_On_Pc'
    common_name = '%scompare the sec zd configuration by comparing xml files before and after upgrade'%test_case_name
    test_cfgs.append(({'scenario':'upgrade','prefix1':'base_sec_zd2','prefix2':'base2_sec_zd2','not_cmp_file':['ap-list.xml','apgroup-list.xml'],'pc_dir':pc_dir},test_name, common_name, 2, True))
    
    test_case_name='[restore Environment]'
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable sw port connected to mesh ap' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True)) 
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected to pri zd' %test_case_name
    param_cfg = dict(timeout = 120,zdcli='zdcli1')
    test_cfgs.append((param_cfg, test_name, common_name, 0, True)) 
    
    return test_cfgs
    

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="upgrade and downgrade as previous with N plue one configuration,sec first"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    physical_ap_sym_dict = {}
    physical_ap_mac_list = []
    ap_sym_dict = tb_cfg['ap_sym_dict']
    all_ap_mac = tb_cfg['ap_mac_list']
    for ap in ap_sym_dict:
        if ap_sym_dict[ap]['model'].startswith('zf'):
            physical_ap_sym_dict[ap] = ap_sym_dict[ap]
            physical_ap_mac_list.append(ap_sym_dict[ap]['mac'])
            
    mac_add_in_new_ap_group = []      
    mac_addr_check_in_default_group=[]
    if len(all_ap_mac)>len(physical_ap_mac_list):   
        mac_add_in_new_ap_group = physical_ap_mac_list
        number_sim_ap = 1
        for i in range(0,number_sim_ap):
            mac = random.choice(all_ap_mac)
            if not mac in mac_add_in_new_ap_group:
                mac_add_in_new_ap_group.append(mac)
                
        mac_addr_check_in_default_group=[]
        while not mac_addr_check_in_default_group:      
            for i in range(0,number_sim_ap):
                mac = random.choice(all_ap_mac)
                if not mac in mac_add_in_new_ap_group:
                    mac_addr_check_in_default_group.append(mac)
    else:
        for ap in ap_sym_dict:
            if ap_sym_dict[ap]['model']=='zf7363':
                mac_add_in_new_ap_group.append(ap_sym_dict[ap]['mac'])
            else:
                mac_addr_check_in_default_group.append(ap_sym_dict[ap]['mac'])
    
    if len(mac_add_in_new_ap_group) ==0:
        print('no ap add in new ap group')
        return
    
    if len(mac_addr_check_in_default_group) ==0:
        print('no ap add in default ap group')
        return
    
#    mac_add_in_new_ap_group = [all_ap_mac[0]]
#    mac_addr_check_in_default_group = [all_ap_mac[1]]
    
    zd1_ip = tb_cfg['ZD1']['ip_addr']
    zd2_ip = tb_cfg['ZD2']['ip_addr']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(physical_ap_sym_dict)
        while True:
#            active_ap = raw_input("Choose an active AP: ")
#            if active_ap not in physical_ap_sym_dict:
#                print "AP[%s] doesn't exist." % active_ap
#            
#            else:
#                active_ap_mac=physical_ap_sym_dict[active_ap]['mac']
#                print('active_ap_mac is %s'% active_ap_mac)
#            
            mesh_ap = raw_input("Choose an mesh AP: ")
            if mesh_ap not in physical_ap_sym_dict:
                print "AP[%s] doesn't exist." % mesh_ap
            
            else:
                mesh_ap_mac=physical_ap_sym_dict[mesh_ap]['mac']
                print('mesh_ap_mac is %s'% mesh_ap_mac)
                break
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="upgrade and downgrade as previous with N plue one configuration,sec first"
    wlan_cfg = {
        'ssid': "wlan_nplusone_west" ,
        'name':"wlan_nplusone_west" ,
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
    
    wlan_group_name = 'upgrade_nplusone'
    ap_group_cfg ={     'name':'upgrade_nplusone',
                        'description':'',
                        'radio2.4':{
                                   'wlan-grp':wlan_group_name,
                                   },
                        'radio5.0':{
                                   'wlan-grp':wlan_group_name,
                                   },
                        'add_members':mac_add_in_new_ap_group
                        }
    
    tcfg = dict(
#                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                dest_ip= '192.168.0.252',
                mesh_ap=mesh_ap_mac,
                ap_mac_list = physical_ap_mac_list,
                zd1_ip=zd1_ip,
                zd2_ip=zd2_ip,
                ap_group_cfg = ap_group_cfg,
                wlan_group_name = wlan_group_name,
                mac_addr_check_in_default_group = mac_addr_check_in_default_group,
                pc_dir = 'C://Documents and Settings//lab//My Documents//Downloads'
                )
    test_cfgs = define_test_configuration(tcfg)
    ts = testsuite.get_testsuite(ts_name, "upgrade and downgrade as previous with N plue one configuration,sec first", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
