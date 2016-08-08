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
    common_name = 'Initial SR ENV'
    param_cfg = dict(zd1_ip_addr = cfg['zd1']['ip_addr'], zd2_ip_addr = cfg['zd2']['ip_addr'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    

    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name,0,False))


    test_name = 'CB_Scaling_RemoveZDAllConfig'
    common_name = 'Prepare for testing...'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy for synchronize configuration'
    test_cfgs.append(({'timeout':cfg['wait_for']},test_name,common_name,0,False))
             
    test_name = 'CB_ZD_SR_Mgmt_ACL_Sync_Testing'
    common_name = '[ZDs ACL management data]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_CountryCode_Sync_Testing'
    common_name = '[ZD country code data] sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_SNMP_FM_Setting_Sync_Testing'
    common_name = '[Enable / Disable / SNMP service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_WLAN_Sync_Testing'
    common_name = '[Add / Del / Modify WLAN service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Maps_Sync_Testing'
    common_name = '[Add / Del Maps]sync-up from Active ZD.'
    param_cfg = dict(img_list = cfg['img_list'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_SR_Roles_Sync_Testing'
    common_name = '[Add / Del / Modify Roles service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_User_Sync_Testing'
    common_name = '[Add / Del / Modify Users service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
       
    test_name = 'CB_ZD_SR_Guest_Access_Sync_Testing'
    common_name = '[Enable / Disable / Modify Guest Access service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
       
    test_name = 'CB_ZD_SR_Hotspot_Setting_Sync_Testing'
    common_name = '[Add / Del / Modify HotSpot service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))

    test_name = 'CB_ZD_SR_AAA_Server_Sync_Testing'
    common_name = '[Add / Del / Modify AAA server service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_SR_Alarm_Setting_Sync_Testing'
    common_name = '[Enable / Disable / Modify Alarm service / setting]sync-up from Active ZD.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    

    test_name = 'CB_Scaling_RemoveZDAllConfig'
    common_name = 'Clean up ENV'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
 
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy, again'
    test_cfgs.append(({},test_name,common_name,0,True))
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = 'Cleanup testing environment'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))  
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
        jpg_img_path = None
        
        while not jpg_img_path:
            jpg_img_path = os.path.join(os.getcwd(), "maps", "map.jpg")
            tmp = raw_input('Enter the full path of an \'.JPG\' image: %s' % jpg_img_path)
            if tmp != '':
                jpg_img_path = tmp            
            if not os.path.isfile(jpg_img_path):
                print "File %s doesn't exist" % jpg_img_path
                jpg_img_path = None

        png_img_path = None
        while not png_img_path:
            png_img_path = os.path.join(os.getcwd(), "maps", "map.png")                        
            tmp = raw_input('Enter the full path of an \'.PNG\' image: %s' % png_img_path)
            if tmp != '':
                png_img_path = tmp
            if not os.path.isfile(png_img_path):
                print "File %s doesn't exist" % png_img_path
                png_img_path = None

        gif_img_path = None
        while not gif_img_path:
            gif_img_path = os.path.join(os.getcwd(), "maps", "map.gif")
            tmp = raw_input('Enter the full path of an \'.GIF\' image: %s' % gif_img_path)
            if tmp != '':
                gif_img_path = tmp
            if not os.path.isfile(gif_img_path):
                print "File %s doesn't exist" % gif_img_path
                gif_img_path = None
                
    else:
        jpg_img_path = os.path.join(os.getcwd(), "maps", "map.jpg")
        png_img_path = os.path.join(os.getcwd(), "maps", "map.png")
        gif_img_path = os.path.join(os.getcwd(), "maps", "map.gif")
    
    img_list = [jpg_img_path, png_img_path, gif_img_path]
    cfg['img_list'] = img_list
    
    
#    cfg['full_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\full_cfg.bak'
#    cfg['empty_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\empty_cfg.bak' 
    
    cfg['zd1'] = {'ip_addr':'192.168.0.2',
                  'share_secret':'testing'
                  }
    
    cfg['zd2'] = {'ip_addr':'192.168.0.3',
                  'share_secret':'testing'
                  }    
    
    cfg['wait_for'] = 3600
    

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
    
    ts_name = 'ZDs configuration synchronization and runtime info'
    ts = testsuite.get_testsuite(ts_name, 'ZDs configuration synchronization and runtime info', combotest=True)
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