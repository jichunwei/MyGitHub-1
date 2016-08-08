'''
Created on 2010-9-1
@author: cwang@ruckuswireless.com
'''
import sys
import random
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = list()
    
    pre_name = 'remember Process ID'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid mark.' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'verify aps are all connected'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs are connected including RuckusAP and SIMAP' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    pre_name = 'create User by upload user-list.xml'
    test_name = 'CB_ZDCLI_Upload_Files_By_TFTP'
    common_name = '[%s]:Upload user-list.xml files from tftp server.' %pre_name
    param_cfg = dict(tftpserver = cfg['tftpserver'],
                     upload_file_list = cfg['file_list']                     
                     )
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
   
    #Append an action for activate users
    user_web_auth_wlan = cfg['wlan_cfg_list'][0]
    username = 'rat_local_user_1'
    password = 'admin'    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = '[%s]:Create local User as name/password [%s/%s]' % (pre_name,username, password,)
    param_cfg = dict(username = username,
		     password = password,
		     fullname = username)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'create web auth Wlan'
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[%s]:Remove WLANs from ZD WebUI' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    #create guest pass wlan
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s]:Create web authentication WLAN with local database' %pre_name
    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list'], }, test_name, common_name, 0, False))
    
    
    user_web_auth_wlan['username'] = username
    user_web_auth_wlan['password'] = password
    
    pre_name = 'associate STA to web auth wlan'
    test_name = 'CB_ZD_Find_Station'
    common_name = '[%s]:Find an active station' %pre_name
    param_cfg = dict(target_station = cfg['target_sta'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[%s]:Remove WLANs from station for guest access testing' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[%s]:Associate station to ssid' %pre_name
    param_cfg = dict(wlan_cfg = user_web_auth_wlan)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Station_Renew_WIFI_IP_Address'
    common_name = '[%s]:Renew WIFI device' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
        
    test_name = 'CB_ZD_Station_Verify_Client_Unauthorized'
    common_name = '[%s]:Checking client is unauthorized by [username:%s]' %  (pre_name,username)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Station_Perform_Web_Auth'
    common_name = '[%s]:Active client to authorization, username [%s], password [%s]' % ( pre_name,username, password)
    param_cfg = dict(username = username,
                     password = password)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
    
    
    test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    common_name = '[%s]:Checking client is authorized by [username:%s]' %  (pre_name,username)
    param_cfg = dict(username = username)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
    
    
    test_name = 'CB_ZD_Remove_All_Active_Clients'
    common_name = '[%s]:Clean client is authorized by [username:%s]' % (pre_name,username)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   
     
    random.seed()
    username = 'rat_local_user_%d' % random.randrange(2, 5999)
    
    test_name = 'CB_ZD_Station_Perform_Web_Auth'
    common_name = '[%s]:Active client to authorization, username [%s], password [%s]' % (pre_name,username, password)
    param_cfg = dict(username = username,
                     password = password)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))      
    
    test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    common_name = '[%s]:Checking client is authorized by [username:%s]' % (pre_name,username)
    param_cfg = dict(username = username)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Remove_All_Active_Clients'
    common_name = '[%s]:Remove client is authorized by [username:%s]' % (pre_name,username)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    username = 'rat_local_user_6000'

    test_name = 'CB_ZD_Station_Perform_Web_Auth'
    common_name = '[%s]:Active client to authorization, username [%s], password [%s]' % (pre_name,username, password)
    param_cfg = dict(username = username,
                     password = password)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))      
    
    test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    common_name = '[%s]:Checking client is authorized by [username:%s]' % (pre_name,username)
    param_cfg = dict(username = username)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    pre_name = 'remove wlans and users'
    test_name = 'CB_ZD_Remove_All_Active_Clients'
    common_name = '[%s]:Remove client is authorized by [username:%s]' % (pre_name,username)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[%s]:Clean WLANs from ZD WebUI' % (pre_name)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    
    #Because delete from webui directly which is too slow, so change it to delete from CLI    

    test_name = 'CB_ZDCLI_Delete_Files_From_CLI'
    common_name = '[%s]:Clean up all users from ZD WebUI'% (pre_name)
    param_cfg = dict(delete_file_list = cfg['file_list'] )
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  
    
    pre_name = 'check Process id not be changed'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid checking.'% (pre_name)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))     
    
    return test_cfgs

def define_test_params(tbcfg, attrs,):
    cfg = dict()
    
    sta_ip_list = tbcfg['sta_ip_list']    
       
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_ap_list = getActiveAp(ap_sym_dict)        
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
    cfg['target_sta'] = target_sta
            
    wlan_cfg_list = []
    random.seed()
    user_web_auth_wlan = {'ssid': 'rat-webauth_%d' % random.randrange(50000, 100000),                 
                          'do_webauth':True,
                          'auth': 'open',
                          'encryption' : 'none', 
                          'username':"ras.local.user",
                          'password':"ras.local.user",                                                      
                          }
    wlan_cfg_list.append(user_web_auth_wlan)
    cfg['wlan_cfg_list'] = wlan_cfg_list
        
    cfg['timeout'] = 3 * 1800
    cfg['tftpserver'] = '192.168.0.20'
    file_loc = '/writable/etc/airespider'
    cfg['file_list'] = [{'file_name':'user-list.xml',
                         'file_loc':file_loc},]    
    return cfg

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    cfg = define_test_params(tbcfg, attrs)
    test_cfgs = define_test_cfg(cfg)
    
    ts_name = '6000 User Generation'
    ts = testsuite.get_testsuite(ts_name, 'To verify Max users can be created and authenticated as wireless user successfully', combotest=True)
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
