'''
'''

import sys
import re
from pprint import pformat
from string import Template


import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _gen_id(index):
    return '[%d]' % index

def define_test_configuration(cfg):
    
    test_cfgs = []
#--------------Initialize 9.x ENV for downgrade to 8.2FCS baseline ---------------#
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial test environment of test, call 2 ZD up at target version'
    test_cfgs.append(({'zd1_ip_addr':cfg['zd1']['ip_addr'], 'zd2_ip_addr':cfg['zd2']['ip_addr'],
                       'share_secret':cfg['zd1']['share_secret']},
                       test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy at target version' 
    test_cfgs.append(({"timeout":1000},test_name,common_name,0,False))
    
    pre_name='[get ap numbers]' 
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = '%sget ap number connected with zd' % pre_name
    param_cfg = dict(timeout = 120, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    #should select default when downgrade,but because of bug23677,can't do like this,
    #after the bug fixed,should add 'default':True at paramerer list
    pre_name='[downgrade zd to base build]'
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name ='%sdowngrade zd to base build' % pre_name
    test_cfgs.append(({'image_file_path': cfg['base_img_file_path']},
                      test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd upgrade' % (pre_name,cfg['wait_for_zd_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_zd_upgrading']*60}, test_name, common_name, 1, False)) 
    
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD version, make sure the Standby ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['base_full_version'],'zd_type':'active'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the Standby ZD version, make sure the Standby ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['base_full_version']},test_name,common_name,1,False))
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall base SIMAP Image to zd1.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['base_sim_ap_img_name'],sim_version=cfg['base_simap_version'],
                     zd='zd1')    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall base SIMAP Image to zd2.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['base_sim_ap_img_name'],sim_version=cfg['base_simap_version'],
                     zd='zd2')    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd sync' % (pre_name,cfg['wait_for_sync_after_instal_simap'])
    test_cfgs.append(({'timeout':cfg['wait_for_sync_after_instal_simap']*60}, test_name, common_name, 1, False))
    
    pre_name='[verify aps are all connected to zd after downgrade]' 
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting for %d minutes for ap upgrade' % (pre_name,cfg['wait_for_ap_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_ap_upgrading']*60}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "%sGet the Active ZD at basic version" % pre_name
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build' % pre_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
    pre_name='[clear configuration at base build]'
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = '%sRemove Roles, except default at base build' % pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove WLANs from ZD WebUI at base build' % pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = '%sRemove all Authentication for creating new servers at base build' % pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))        
    
    pre_name='[add configuration at base build]' 
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate open-none WLAN at base build' % pre_name
    wlan_cfg_list = []    
    open_none_wlan = {
                 'ssid': 'rat-open-none',                
                 'auth': 'open',
                 'encryption' : 'none',                
                }
    wlan_cfg_list.append(open_none_wlan)    
    param_cfg = dict(wlan_cfg_list = wlan_cfg_list)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Create_Single_Role'
    common_name = '%sCreate a role at base build' % pre_name
    param_cfg = dict(role_cfg = {"rolename": "rat-role", 
                                 "rat-role": "", 
                                 "specify_wlan": "rat-open-none",
                                 "guestpass": True, 
                                 "description": "",
                                 "group_attr": "ruckus", 
                                 "zd_admin": "full"} )
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = "%sCreate local username/password as \'rat_local_user/rat_local_user\' at base build" % pre_name
    param_cfg = dict(username = 'rat_local_user', password = 'rat_local_user')
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   


    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate rat-guest-access WLAN at base build'% pre_name
    wlan_cfg_list = []    
    guest_access_wlan = {
                 'ssid': 'rat-guest-access',
                 'type': 'guest', 
                 'auth': 'open',
                 'encryption' : 'none',  
                 'username': 'ras_local_user',
                 'password': 'ras_local_user',                               
                }
    wlan_cfg_list.append(guest_access_wlan)    
    param_cfg = dict(wlan_cfg_list = wlan_cfg_list)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
#    test_name = 'CB_ZD_Find_Station'
#    common_name = 'Find an active station at 8.2'
#    param_cfg = dict(target_station = cfg['target_sta'])
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#    
#    
#    test_name = 'CB_ZD_Remove_Wlan_From_Station'
#    common_name = 'Remove WLANs from station for guest access testing at 8.2'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#    
#    
#    test_name = 'CB_ZD_Associate_Station'
#    common_name = 'Associate station to ssid rat-guest-access at 8.2'
#    param_cfg = dict(wlan_cfg = guest_access_wlan)
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    

    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '%sCreate a LDAP/Radius/Accounting server rat_ldap_test at base buid' % pre_name
    param_cfg = dict(auth_ser_cfg_list = [cfg['ldap_ser_cfg'], cfg['radius_ser_cfg'], cfg['ad_ser_cfg']])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
    
    
    test_name = 'CB_ZD_Get_Wlans_List'
    common_name = '%sGet WLANs list at base build for checking' % pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_Get_Role_List'
    common_name = '%sGet role list at base build for checking' % pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   

    pre_name='[upgrade to target build]'
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name ='%supgrade zd to target build' % pre_name
    test_cfgs.append(({'image_file_path': cfg['target_img_file_path'],},
                      test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd upgrade' % (pre_name,cfg['wait_for_zd_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_zd_upgrading']*60}, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD version, make sure the active ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['target_full_version'],'zd_type':'active'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the Standby ZD version, make sure the Standby ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['target_full_version']},test_name,common_name,1,False))
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to zd1.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['target_sim_ap_img_name'],sim_version=cfg['target_simap_version'],
                     zd='zd1')    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to zd2.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['target_sim_ap_img_name'],sim_version=cfg['target_simap_version'],
                     zd='zd2')
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd sync' % (pre_name,cfg['wait_for_sync_after_instal_simap'])
    test_cfgs.append(({'timeout':cfg['wait_for_sync_after_instal_simap']*60}, test_name, common_name, 1, False))
        
    pre_name='[check ap number after upgrade]' 
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting for %d minutes for ap upgrade' % (pre_name,cfg['wait_for_ap_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_ap_upgrading']*60}, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "%sGet the Active ZD at target build after upgrade"% pre_name
    test_cfgs.append(({},test_name,common_name,0,False))

    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at target build' % pre_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))     

    pre_name='[downgrade zd to base build to check configuration]'
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name ='%sdowngrade zd to base build' % pre_name
    test_cfgs.append(({'image_file_path': cfg['base_img_file_path']},
                      test_name, common_name, 0, False))
        
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd upgrade' % (pre_name,cfg['wait_for_zd_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_zd_upgrading']*60}, test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD version, make sure the active ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['base_full_version'],'zd_type':'active'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the Standby ZD version, make sure the Standby ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['base_full_version']},test_name,common_name,1,False))
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall base SIMAP Image to zd1.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['base_sim_ap_img_name'],sim_version=cfg['base_simap_version'],
                     zd='zd1')    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall base SIMAP Image to zd2.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['base_sim_ap_img_name'],sim_version=cfg['base_simap_version'],
                     zd='zd2')    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd sync' % (pre_name,cfg['wait_for_sync_after_instal_simap'])
    test_cfgs.append(({'timeout':cfg['wait_for_sync_after_instal_simap']*60}, test_name, common_name, 1, False))

    pre_name='[verify configuration and AP after downgrade]'
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting for %d minutes for ap upgrade' % (pre_name,cfg['wait_for_ap_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_ap_upgrading']*60}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "%sGet the Active ZD at base version" % pre_name
    test_cfgs.append(({},test_name,common_name,0,False))
          
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build, again' % pre_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
            
               
    test_name = 'CB_ZD_Verify_Roles'
    common_name = "%sVerify roles info at base build" % pre_name
    test_cfgs.append(({},test_name,common_name,1,False))     
    
    test_name = 'CB_ZD_Verify_Local_User'
    common_name = "%sVerify Local user info at base build"% pre_name
    test_cfgs.append(({},test_name,common_name,1,False))
        
    test_name = 'CB_ZD_Verify_Wlans_Info'
    common_name = "%sVerify Wlans info at base build" % pre_name
    test_cfgs.append(({},test_name,common_name,1,False)) 
    
    test_name = 'CB_ZD_Verify_Authentication_Server_Info'
    common_name = "%sVerify Authentication server info at base build"% pre_name
    test_cfgs.append(({},test_name,common_name,1,False)) 
            
    
#    test_name = 'CB_ZD_Find_Station'
#    common_name = 'ZD1 Find an active station at 8.2FCS.'
#    param_cfg = dict(target_station = cfg['target_sta'])
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
#    
#    test_name = 'CB_ZD_Remove_Wlan_From_Station'
#    common_name = 'ZD1 Remove WLANs from station for guest access testing at 8.2FCS.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
#    
#    
#    test_name = 'CB_ZD_Associate_Station'
#    common_name = 'ZD1 Associate station to ssid rat-guest-access at 8.2FCS.'
#    param_cfg = dict(wlan_cfg = guest_access_wlan)
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))       
#    
#    

#----------------------------Upgrade back to target build--------------------------------------#
    pre_name='[upgrade back to target build]'
    test_name = 'CB_Scaling_Upgrade_ZD'
    common_name ='%supgrade zd to target build' % pre_name
    test_cfgs.append(({'image_file_path': cfg['target_img_file_path'],},
                      test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd upgrade' % (pre_name,cfg['wait_for_zd_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_zd_upgrading']*60}, test_name, common_name, 1, False)) 
    
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the active ZD version, make sure the active ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['target_full_version'],'zd_type':'active'},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_SR_Check_Version'
    common_name = '%sCheck the Standby ZD version, make sure the Standby ZD was upgraded' % pre_name
    test_cfgs.append(({'expect_version':cfg['target_full_version']},test_name,common_name,1,False))
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to zd1.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['target_sim_ap_img_name'],sim_version=cfg['target_simap_version'],
                     zd='zd1')    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
        
    test_name = 'CB_Scaling_Package_SimAPImage_To_ZD'
    common_name = '%sInstall target SIMAP Image to zd2.' % pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],sim_models = cfg['sim_models'],
                     sim_img = cfg['target_sim_ap_img_name'],sim_version=cfg['target_simap_version'],
                     zd='zd2')
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting %d minutes for zd sync' % (pre_name,cfg['wait_for_sync_after_instal_simap'])
    test_cfgs.append(({'timeout':cfg['wait_for_sync_after_instal_simap']*60}, test_name, common_name, 1, False))
         
    pre_name='[after upgrade check ap]'
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:Waiting for %d minutes for ap upgrade' % (pre_name,cfg['wait_for_ap_upgrading'])
    test_cfgs.append(({'timeout':cfg['wait_for_ap_upgrading']*60}, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "Get the Active ZD at target build"
    test_cfgs.append(({},test_name,common_name,0,False)) 
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sRe-Check all of APs are connected including RuckusAP and SIMAP at target build' % pre_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))     
        
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = "Clear up the Smart Redundancy test environment"
    test_cfgs.append(({}, test_name, common_name, 0, True))    
        
    return test_cfgs


def create_test_parameters(tbcfg, attrs, cfg = {}):

    sta_ip_list = tbcfg['sta_ip_list']    
       
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_ap_list = getActiveAp(ap_sym_dict)        
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
    cfg['zd1'] = {'ip_addr':'192.168.0.2',
                  'share_secret':'testing'
                  }
    cfg['zd2'] = {'ip_addr':'192.168.0.3',
                  'share_secret':'testing'
                  }
    
    cfg['target_sta'] = target_sta
        
    cfg['ldap_ser_cfg'] = {'server_name': 'LDAP',
                           'server_addr': '192.168.0.252',
                           'server_port': '389',
                           'ldap_search_base':'dc=example,dc=net',
                           'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
                           'ldap_admin_pwd': 'lab4man1',}
    
    cfg['radius_ser_cfg'] = {'server_name': 'RADIUS',
                             'server_addr': '192.168.0.252',
                             'radius_auth_secret': '1234567890',
                             'server_port': '1812',}
    
    cfg['ad_ser_cfg'] = { 'win_domain_name': 'rat.ruckuswireless.com',
                          'server_port': '389', 
                          'server_name': 'AD_Server', 
                          'server_addr': '192.168.0.250',}
    
    #8.2 FCS zd build
    cfg['base_img_file_path'] = ''
    cfg['base_build_stream'] = 'ZD3000_8.2.0.1_production'
    cfg['base_stream'] = '8.2.0.1'
    cfg['base_build_number'] = '8'
    
    #9.x zd build
    cfg['target_img_file_path'] = ''
    cfg['target_build_stream'] = 'ZD3000_9.0.0.0_production'
    cfg['target_stream'] = '9.0.0.0'
    cfg['target_build_number'] = '52'
    
    #8.2 FCS simap build
    cfg['base_simap_build_stream'] = 'SIM-AP_8.2.0.0_production'
    cfg['base_simap_bno'] = '8'
        
    #9.x simap build
    cfg['target_simap_build_stream'] = 'SIM-AP_9.0.0.0_production'
    cfg['target_simap_bno'] = '24'
    
    #tftp server cfg info    
    cfg['tftpserver'] = '192.168.0.10'
    cfg['file_path'] = 'c:\\tmp'
    cfg['sim_models'] = 'ss2942 ss2741 ss7942 ss7962'
    cfg['timeout'] = 3600
    
    
    import os
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\ZD3000_9.2.0.0.138.tar.gz" )
    cfg['base_img_file_path'] = file    
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\output_build_no_76_directorx86.tar.gz" )
    cfg['target_img_file_path'] = file
    
    filename ="9.2.0.0.136.bl7"
    cfg['base_sim_ap_img_name']=filename
    filename ="9.3.0.0.76.bl7"
    cfg['target_sim_ap_img_name']=filename
    
    cfg['base_simap_version'] = '9.2.0.0.136'
    cfg['target_simap_version'] = '9.3.0.0.76'
    
    cfg['target_full_version'] = '9.3.0.0.76'
    cfg['base_full_version'] = '9.2.0.0.138'
    
    cfg['wait_for_ap_upgrading'] = 30 #minutes
    cfg['wait_for_sync_after_instal_simap']=1 #minute
    cfg['wait_for_zd_upgrading'] = 10 #minutes
    
    return cfg
                


def interactive_cfg(cfg):
    '''
    1) Set ZD/SIMAP Version including 9.x and 8.2FCS.
    2) Set simulator AP models.
    '''
    # 9.x ZD version info setting.
    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure current ZD version [9.x] build stream/bno'
    print '--------------------------------------------------------------------------------'
    zd_bs_9x = 'ZD3000_9.0.0.0_production'
    tmp = raw_input('Please input current ZD [9.x] build stream default [%s]:' % zd_bs_9x)
    if tmp:
        zd_bs_9x = tmp
    
    cfg['target_build_stream'] = zd_bs_9x
    
    zd_bn_9x = '56'
    tmp = raw_input('Please input current ZD [9.x] build no default [%s]:' % zd_bn_9x)
    if tmp:
        zd_bn_9x = tmp
    
    cfg['target_build_number'] = zd_bn_9x
    
    zd_b_9x = '9.0.0.0'
    tmp = raw_input('Please input current ZD [9.x] build default [%s]:' % zd_b_9x)
    if tmp:
        zd_b_9x = tmp
    cfg['target_stream'] = zd_b_9x

    T = '''9.x ZD version configuration result:
    	build_stream=$target_build_stream,
	build_number=$target_build_number,
	stream=$target_stream
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''
    
    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure SIMAP version [9.x] build stream/bno'
    print '--------------------------------------------------------------------------------'
    sim_bs_9x = 'SIM-AP_9.0.0.0_production'
    tmp = raw_input('Please input current SIMAP version [9.x] build stream default [%s]:' % sim_bs_9x)
    if tmp:
	sim_bs_9x = tmp
    cfg['target_simap_build_stream'] = sim_bs_9x

    sim_bn_9x = '25'
    tmp = raw_input('Please input current SIMAP version [9.x] build no default [%s]:' % sim_bn_9x )
    
    if tmp:
	sim_bn_9x = tmp

    cfg['target_simap_bno'] = sim_bn_9x
    

    T = '''9.x SIMAP version configuration result:
    	build_stream=$target_simap_build_stream,
	build_number=$target_simap_bno,
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''

    #8.2FCS version info setting.
    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure ZD version [8.2FCS] build stream/bno'
    print '--------------------------------------------------------------------------------'    
    zd_bs_82fcs = 'ZD3000_8.2.0.1_production'
    tmp = raw_input('Please input ZD [8.2FCS] build stream default [%s]:' % zd_bs_82fcs)
    if tmp:
        zd_bs_82fcs = tmp

    cfg['base_build_stream'] = zd_bs_82fcs

    zd_bn_82fcs = '8'
    tmp = raw_input('Please input ZD [8.2FCS] build no default[%s]:' % zd_bn_82fcs)
    if tmp:
        zd_bn_82fcs = tmp
    
    cfg['base_build_number'] = zd_bn_82fcs

    zd_b_82fcs = '8.2.0.1'
    tmp = raw_input('Please input ZD [8.2FCS] build default [%s]:' % zd_b_82fcs)
    if tmp:
        zd_b_82fcs = tmp
    cfg['base_stream'] = zd_b_82fcs

    T = '''8.2FCS ZD version configuration result:
    	build_stream=$base_build_stream,
	build_number=$base_build_number,
	stream=$base_stream
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''

    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure SIMAP version [8.2FCS] build stream/bno'
    print '--------------------------------------------------------------------------------'
    sim_bs_82fcs = 'SIM-AP_8.2.0.0_production'
    tmp = raw_input('Please input current SIMAP version [8.2FCS] build stream default [%s]:' % sim_bs_82fcs)
    if tmp:
	sim_bs_82fcs = tmp
    cfg['base_simap_build_stream'] = sim_bs_82fcs

    sim_bs_82fcs = '8'
    tmp = raw_input('Please input current SIMAP version [8.2FCS] build no default [%s]:' % sim_bs_82fcs)
    
    if tmp:
	sim_bs_82fcs = tmp

    cfg['base_simap_bno'] = sim_bs_82fcs


    T = '''8.2FCS SIMAP version configuration result:
    	build_stream=$base_simap_build_stream,
	build_number=$base_simap_bno,
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''

    print '--------------------------------------------------------------------------------'
    print '   The following will go to configure SIMAP models'
    print '   Input as formatting: ss2942 ss7942 ss2741'
    print '   Splited by whitespace'
    print '--------------------------------------------------------------------------------'

    sim_models = 'ss2942 ss7942 ss2741'
    tmp = raw_input('Please input simulator AP models default [%s]:' % sim_models)
    if tmp:
        sim_models = tmp
    
    cfg['sim_models'] = sim_models

    T = '''8.2FCS/9.x SIMAP model configuration result:
    	models=$sim_models,
    '''    
    res = Template(T).substitute(cfg)
    print res
    print ''





def create_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    cfg = {}
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    create_test_parameters(tbcfg, attrs, cfg)
    #interact with user for updating paramter.
    #interactive_cfg(cfg)
    ts_name = 'downgrade as previous configuration when SR and Scaling'
    ts = testsuite.get_testsuite(ts_name, 
                                 'ZD downgrade as previous configuration(SR and Scaling)',
                                 combotest=True)
    test_cfgs = define_test_configuration(cfg)

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
    _dict['tbtype'] = 'ZD_Scaling'
    create_test_suite(**_dict)
    
