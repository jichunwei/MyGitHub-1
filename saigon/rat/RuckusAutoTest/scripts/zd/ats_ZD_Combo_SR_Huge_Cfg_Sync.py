'''
Created on 2010-7-9

@author: cwang@ruckuswireless.com
'''
import sys
import os

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []    
        
    
        
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial test environment of test, call 2 ZD up'
    test_cfgs.append(({'zd1_ip_addr':cfg['zd1']['ip_addr'], 'zd2_ip_addr':cfg['zd2']['ip_addr'],
                       'share_secret':cfg['zd1']['share_secret']},
                       test_name, common_name, 0, False))

    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy for synchronize configuration'
    test_cfgs.append(({'timeout':1000},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = 'get ap number connected with zd'
    param_cfg = dict(timeout = 120, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
#    test_name = 'CB_ZD_SR_Get_Active_ZD'
#    common_name = 'Get Active ZD'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
#    test_name = 'CB_ZD_SR_Get_Standby_ZD'
#    common_name = 'Get Standby ZD'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#        
#    test_name = 'CB_ZD_SR_Set_Active_ZD'
#    common_name = "Set Active ZD as %s" % cfg['zd1']['ip_addr']
#    test_cfgs.append(({},test_name,common_name,0,False)) 
    

#    test_name = 'CB_ZD_Create_Local_User'
#    common_name = "Create local username/password as 'rat_local_user/rat_local_user' at 9.x."
#    param_cfg = dict(username = 'rat_local_user_1', password = 'admin')
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))     
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_Restore'
    common_name = '[restore to full CFG]Restore ZD to full configurations'
    param_cfg = dict(restore_file_path = cfg['full_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
    
#    test_name = 'CB_ZDCLI_Upload_Files_By_TFTP'
#    common_name = 'Upload configuration files from tftp server.'
#    param_cfg = dict(tftpserver = cfg['tftpserver'],
#                     upload_file_list = cfg['file_list']                     
#                     )
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
        
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[Enable SR]Enable Smart Redundancy for synchronize configuration'
    test_cfgs.append(({'timeout':1000},test_name,common_name,0,False))
#    
#    
#    test_name = 'CB_ZD_SR_Get_Active_ZD'
#    common_name = 'Get Active ZD'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#        
#    test_name = 'CB_ZD_SR_Get_Standby_ZD'
#    common_name = 'Get Standby ZD'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#        
#    test_name = 'CB_ZD_SR_Set_Active_ZD'
#    common_name = "Set Active ZD as %s, again" % cfg['zd1']['ip_addr']
#    test_cfgs.append(({},test_name,common_name,0,False)) 
#    
    
#    test_name = 'CB_ZD_Scaling_Remove_All_Wlan_Groups'
#    common_name = 'Remove wlangroups from ZD WebUI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
#    test_name = 'CB_ZD_SR_Delete_Multi_mgmtipacl'
#    common_name = 'Remove all of mgmtipacl from ZD WebUI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
#    test_name = 'CB_ZD_Remove_All_Wlans'
#    common_name = 'Remove WLANs from ZD WebUI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
#    test_name = 'CB_Scaling_Remove_AAA_Servers'
#    common_name = 'Remove all Authentication for creating new servers.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
#    test_name = 'CB_ZD_Remove_All_Profiles'
#    common_name = 'Remove all hotspot profiles.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
            
#    test_name = 'CB_ZD_Remove_All_Maps'
#    common_name = 'Remove all maps.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_case_name='[verify ap number after SR enable]'    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build' % test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
          
#    #Create guest pass WLAN
#    dpsk_wlan = {'ssid': 'guest_pass_test',
#                 'type': 'guest', 
#                 'auth': 'open',
#                 'encryption' : 'none',                
#                }    
#    test_name = 'CB_ZD_Create_Wlan'
#    common_name = 'Create guest pass wlan'
#    param_cfg = dict(wlan_cfg_list = [dpsk_wlan])    
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#    
#    #Create DPSK WLAN
#    dpsk_wlan = {
#                'ssid': 'dpsk_test',
#                'auth': 'PSK',
#                'wpa_ver': 'WPA',
#                'encryption': 'AES',
#                'type': 'standard',
#                'key_string': '1234567890',
#                'key_index': '',
#                'auth_svr': '',
#                'do_zero_it': True,
#                'do_dynamic_psk': True,                 
#                }        
#    test_name = 'CB_ZD_Create_Wlan'
#    common_name = 'Create dpsk wlan'
#    param_cfg = dict(wlan_cfg_list = [dpsk_wlan])    
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
#        
#    #Create 30 WLANs
#    wlan_cfg_list = [] 
#    chk_wlan = {'ssid': 'open_wlan_1',                
#                 'auth': 'open',
#                 'encryption' : 'none',                
#                }
#    for index in range(1, 30):
#        open_wlan = {'ssid': 'open_wlan_%s' % index, 
#                     'auth': 'open',
#                     'encryption' : 'none',                
#                     }
#        wlan_cfg_list.append(open_wlan) 
#        
#    common_name = 'Create WLAN %s' % wlan_cfg_list
#    param_cfg = dict(wlan_cfg_list = wlan_cfg_list)    
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#        
#    #Create fully Wlan-Groups    
#    test_name = 'CB_ZD_Create_Wlan_Groups'
#    common_name = 'Create fully wlan groups'    
#    param_cfg = dict(num_of_wgs = 32)    
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#    
    #Create fully aaa servers    
    server_cnt = 32    
    server_cfg = cfg['server_cfg']
    server_list = []
    for i in range(1, server_cnt+1):
        s_cfg_tmp = server_cfg.copy()
        s_cfg_tmp['server_name'] = 'radius_server_%d' % i
        server_list.append(s_cfg_tmp)
                        
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '[Maximum AAA Servers]Create fully AAA servers'    
    param_cfg = dict(auth_ser_cfg_list = server_list)    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
             
    #Create fully management IP ACLs.
    test_name = 'CB_ZD_SR_Create_Multi_mgmtipacl'
    common_name = '[Maximum mgmt IP ACLs]Create multi mgmt ip acls'
    param_cfg = cfg['mgmtipacl']
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    #Create maxinum hotspot.
    test_name = 'CB_ZD_Create_Maxinum_Hotspot'
    common_name = '[Maximum Hotspots]Create maxinum hotspots'
    param_cfg = dict(num_of_hotspots = 32,
                     num_of_rules = 16                                        
                     )
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    
    #Create full maps
    test_name = 'CB_ZD_Create_Full_Maps'
    common_name = '[Maximum Maps]Create full maps'
    param_cfg = dict(num_of_maps = 40,
                     map_path = cfg['img_list'][0]                                        
                     )
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
#    param_cfg = dict(zd_key_name = 'zd1')
#    test_name = 'CB_ZD_Scaling_Set_Current_ZD'
#    common_name = 'Set current zd as zd1 at 9.x'
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
#        
    
#    test_name = 'CB_Scaling_Generate_ZDCLI'
#    common_name = 'Re-generate ZDCLI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    
    #Verify APs can be managed successfully when hung configurations be setted. 
    
    test_case_name='[verify ap number after huge configuration be set]'    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP at base build' % test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
        
    #Hung configurations checking.
    test_name = 'CB_ZD_SR_Verify_Hung_CFGs'
    common_name = '[Hung Configuration Sync-up]Checking hung cfgs have synchronized successfully'
    param_cfg = dict(timeout = cfg['timeout'], chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Find_Station'
    common_name = '[Associate station]ZD1 Find an active station'
    param_cfg = dict(target_station = cfg['target_sta'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[Associate station]ZD1 Remove WLANs from station for guest access testing'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[Associate station]ZD1 Associate station to ssid %s' % cfg['wlan_cfg_list'][0]['ssid']
    param_cfg = dict(wlan_cfg = cfg['wlan_cfg_list'][0])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
        
#    test_name = 'CB_ZD_Scaling_Remove_All_Wlan_Groups'
#    common_name = 'Clean wlangroups from ZD WebUI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))
#        
#    test_name = 'CB_ZD_SR_Delete_Multi_mgmtipacl'
#    common_name = 'Clean all of mgmtipacl from ZD WebUI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))
#        
#    test_name = 'CB_ZD_Remove_All_Wlans'
#    common_name = 'Clean WLANs from ZD WebUI'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))
#
#    
#    test_name = 'CB_ZD_Remove_All_Profiles'
#    common_name = 'Clean all hotspot profiles.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#            
#    test_name = 'CB_ZD_Remove_All_Maps'
#    common_name = 'Clean all maps.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))
#
#    
#    test_name = 'CB_ZD_Remove_All_Authentication_Server'
#    common_name = 'Clean all Authentication Servers.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#
#    
#    test_name = 'CB_ZD_Remove_All_L2_ACLs'
#    common_name = 'Clean all l2 ACLs.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#    
#    test_name = 'CB_ZD_Remove_All_L3_ACLs'
#    common_name = 'Clean all l3 ACLs.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#    
#    
#    test_name = 'CB_ZD_SR_Delete_Multi_mgmtipacl'
#    common_name = 'Clean all mgmtipacl.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#    
#    test_name = 'CB_ZD_Remove_All_Guest_Passes'
#    common_name = 'Clean all guest passes.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#        
#    test_name = 'CB_ZD_Remove_All_DPSK'
#    common_name = 'Clean all DPSKs.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    
#    
#    test_name = 'CB_ZD_Remove_All_Users'
#    common_name = 'Clean all Users.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))
#        
#    
#    test_name = 'CB_ZD_Remove_All_Roles'
#    common_name = 'Clean all roles.'
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))    

#    test_name = 'CB_ZDCLI_Delete_Files_From_CLI'
#    common_name = 'Clean up all users from ZD WebUI'
#    param_cfg = dict(delete_file_list = cfg['file_list'] )
#    test_cfgs.append((param_cfg, test_name, common_name, 1, True))      
        
#
#    test_name = 'CB_ZD_SR_Disable'
#    common_name = 'Disable Smart Redundancy for restoring.'
#    test_cfgs.append(({},test_name,common_name,0,False))
    
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = 'Cleanup testing environment'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, True))  
    
    
    test_name = 'CB_ZD_Restore'
    common_name = '[restore empty CFG]Restore ZD to empty configurations'
    param_cfg = dict(restore_file_path = cfg['empty_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
                
    return test_cfgs        
        

def define_test_params(tbcfg, attrs, cfg):
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_ap_list = getActiveAp(ap_sym_dict)        
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    cfg['target_sta'] = target_sta
                
    if attrs["interactive_mode"]:        
        print '.........................................................'
        print 'The full path of image follow format: [disk]:[path]\\...\\[image file name]'
        default_png_img_path = os.path.join(os.getcwd(), "maps", "map.png")  
        png_img_path = None
        while not png_img_path:            
            tmp = raw_input('Enter the full path of an \'.PNG\' image: [%s]' % os.path.realpath(default_png_img_path))            
            if tmp != '':
                png_img_path = os.path.realpath(default_png_img_path)
            else:
                png_img_path = default_png_img_path
                
            if not os.path.isfile(png_img_path):
                print "File %s doesn't exist" % png_img_path
                png_img_path = None
                
    else:        
        png_img_path = os.path.join(os.getcwd(), "maps", "map.png")        
        
    img_list = [png_img_path]
    cfg['img_list'] = img_list
    cfg['zd1'] = {'ip_addr':'192.168.0.2',
                  'share_secret':'testing'
                  }
    cfg['zd2'] = {'ip_addr':'192.168.0.3',
                  'share_secret':'testing'
                  }
    cfg['wait_for'] = 1800 * 2
    cfg['timeout'] = 3 * 1800
#    cfg['tftpserver'] = '192.168.0.20'
#    file_loc = '/writable/etc/airespider'
#    cfg['file_list'] = [
#                        #{'file_name':'user-list.xml',
#                        # 'file_loc':file_loc}, 
#                        {'file_name':'role-list.xml',
#                          'file_loc':file_loc},
#                        {'file_name':'acl-list.xml',
#                          'file_loc':file_loc},
#                        {'file_name':'dpsk-list.xml',
#                          'file_loc':file_loc},
#                        {'file_name':'guest-list.xml',
#                          'file_loc':file_loc},
#                        {'file_name':'authsvr-list.xml',
#                          'file_loc':file_loc},]
    cfg['mgmtipacl'] = dict(number = 16,
                            name = 'mgmt-ip-acl-test',
                            type = 'range',
                            addr = '192.168.0.2-192.168.0.225',   
                            )

    cfg['server_cfg'] = { 'server_addr': '192.168.0.252', 'server_port': '1812', 'server_name': 'radius_server',
                          'win_domain_name': '', 'ldap_search_base': '',
                          'ldap_admin_dn': '', 'ldap_admin_pwd': '',
                          'radius_auth_secret': '1234567890', 'radius_acct_secret': ''}
    

    default_wlan_conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
                         'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
                         'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
                         'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '',
                         'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    
    open_none = default_wlan_conf.copy()
    open_none.update({'ssid':'Open-None', 'auth':'open', 'encryption':'none'})
    set_of_30_open_none_wlans = []
    for idx in range(0, 30):
        wlan = open_none.copy()
        wlan['ssid'] = 'Rat-%s-wlan%2d' % (wlan['ssid'], idx + 1)
        set_of_30_open_none_wlans.append(wlan)
    cfg['wlan_cfg_list'] = set_of_30_open_none_wlans   
    
    
    cfg['gp_wlan'] = {'ssid': 'wlan-guestpass',
                      'type': 'guest', 
                      'auth': 'open',
                      'encryption' : 'none',                
                      }
    
    cfg['dpsk_wlan'] = {'ssid': 'wlan-dpsk',
                        'auth': 'PSK',
                        'wpa_ver': 'WPA',
                        'encryption': 'AES',
                        'type': 'standard',
                        'key_string': '1234567890',
                        'key_index': '',
                        'auth_svr': '',
                        'do_zero_it': True,
                        'do_dynamic_psk': True,                 
                        }
        
    cfg['full_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\full_cfg.bak'
    cfg['empty_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\empty_cfg.bak'     
    

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    cfg = {}    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    define_test_params(tbcfg, attrs, cfg)
    
    ts_name = 'Hung Configuration synchronization with scaling'
    ts = testsuite.get_testsuite(ts_name, 'Hung Configuration synchronization', combotest=True)
    test_cfgs = define_test_cfg(cfg)

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
    createTestSuite(**_dict)