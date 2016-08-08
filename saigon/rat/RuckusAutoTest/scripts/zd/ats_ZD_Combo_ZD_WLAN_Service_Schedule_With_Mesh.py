'''
WLAN Service Schedule with single/dual band mesh.

    Mesh link is stable whatever root or mesh AP wlan service schedule enable/disable/specific.    
    Single radio
    1. Change one wlan service schedule to turn-on "15 minutes" on RAP and make sure the mesh link won't be impact.
    2. Change one wlan service schedule to turn-off "15 minutes" on RAP and make sure the mesh link won't be impact.
    3. Change one wlan service schedule to turn-on "15 minutes" on MAP and make sure the mesh link won't be impact.
    4. Change one wlan service schedule to turn-off "15 minutes" on MAP and make sure the mesh link won't be impact.
    Dual radios
    5. Change one wlan service schedule to turn-on "15 minutes" on RAP and make sure the mesh link won't be impact.
    6. Change one wlan service schedule to turn-off "15 minutes" on RAP and make sure the mesh link won't be impact.
    7. Change one wlan service schedule to turn-on "15 minutes" on MAP and make sure the mesh link won't be impact.
    8. Change one wlan service schedule to turn-off "15 minutes" on MAP and make sure the mesh link won't be impact.
    expect result: All steps should result properly.
    
    How to:
        1) Create four WLANs [Single band root, single band mesh, dual band root, dual band mesh]
        2) Assign WLANs to [single band root, single band mesh, dual band root, dual band mesh] AP.        
        4) Check Mesh uplink/downlink.
        5) Pick up a Station to associate and ping
        6) Check station info from ZD.
        7) repeat do 4)-6) to others WLANs 
        7) Turn-off WLAN schedule.
        8) Check mesh uplink/downlink.
        9) repeat do 7)-8) to others mesh link.
    
Created on 2011-4-25
@author: cwang@ruckuswireless.com
'''
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

SINGLE_ROOT = 0
SINGLE_MESH = 1
DUAL_ROOT = 2
DUAL_MESH = 3

def get_wlan_list():
    '''
        Define four WLANs:
            1) "rat-wlan-service-sr-%s" % (time.strftime("%H%M%S"))
            2) "rat-wlan-service-sm-%s" % (time.strftime("%H%M%S"))
            3) "rat-wlan-service-dr-%s" % (time.strftime("%H%M%S"))
            3) "rat-wlan-service-dm-%s" % (time.strftime("%H%M%S"))
    '''
    temp = dict(ssid = "rat-wlan-service-sr-%s" % (time.strftime("%H%M%S")),
                    auth = "open", wpa_ver = "", encryption = "none",
                    key_index = "" , key_string = "",
                    username = "", password = "", auth_svr = "", 
                    web_auth = None, do_service_schedule=None,)
                    
    ssid_list = ["rat-wlan-service-sr-%s" % (time.strftime("%H%M%S")),
                 "rat-wlan-service-sm-%s" % (time.strftime("%H%M%S")),
                 "rat-wlan-service-dr-%s" % (time.strftime("%H%M%S")),
                 "rat-wlan-service-dm-%s" % (time.strftime("%H%M%S")),
                  ]
    wlan_list = []
    for ssid in ssid_list:
        cp = temp.copy()
        cp['ssid'] = ssid
        wlan_list.append(cp)
    
    return wlan_list

def get_wlan_group_list():
    '''
        Define four wlan groups:
    '''    
    return [dict(name = 'rat-wlan-group-sr',
                description = 'rat-wlan-group-sr'),
            dict(name = 'rat-wlan-group-sm',
                 description = 'rat-wlan-group-sm'),
            dict(name = 'rat-wlan-group-dr',
                 description = 'rat-wlan-group-dr'),
            dict(name = 'rat-wlan-group-dm',
                 description = 'rat-wlan-group-dm'
                 )]

def get_single_band_mesh_peer(tbcfg, ap_sym_dict):    
    mesh_layout = tbcfg['Mesh']['layout']    
    for mesh_path in mesh_layout:
        #find out mesh link.
        if len(mesh_path) >= 2:
            #find out single band
            root = mesh_path[1][0]
            root_cfg = ap_sym_dict[root]
            model = root_cfg['model']
            if const.is_ap_support_dual_band(model):
                continue
            else:
                return mesh_path
    
    raise Exception("Didn't find single band mesh peer")

def get_dual_band_mesh_peer(tbcfg, ap_sym_dict):
    mesh_layout = tbcfg['Mesh']['layout']    
    for mesh_path in mesh_layout:
        #find out mesh link.
        if len(mesh_path) >= 2:
            #find out single band
            root = mesh_path[1][0]
            root_cfg = ap_sym_dict[root]
            model = root_cfg['model']
            if const.is_ap_support_dual_band(model):
                return mesh_path
            
    raise Exception("Didn't find dual band mesh peer")  
  

def define_test_configuration(tbcfg):
    '''
        tbcfg: which contains all of configurations to this test suites.
    '''
    test_cfgs = []    
    #do WLAN service schedule on test case    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'    
    common_name = 'Remove All Wlan Groups for cleanup ENV.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Remove_All_Wlans'    
    common_name = 'Clean all Wlans for cleanup ENV.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    #Create 4 WLANs
    wlan_list = get_wlan_list()
    wlan_name_str = ', '.join([x['ssid'] for x in wlan_list])
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create WLAN %s to prepare for testing.' % (wlan_name_str)
    param_cfg = dict(wlan_cfg_list = wlan_list)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
    common_name = 'Remove all wlans out of default wlan group for cleanup ENV.'     
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    #Create 4 WLANGroup
    wlangroup_list = get_wlan_group_list()
    for wg in wlangroup_list:
        test_name = 'CB_ZD_Create_Wlan_Group'
        common_name = 'Create Wlan Group: %s to prepare for testing' % (wg['name'])
        param_cfg = dict(wgs_cfg = wg)
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    i = 0
    for wlan in wlan_list:
        test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
        common_name = 'Assign wlan: %s to wg: %s to prepare for testing.' % (wlan['ssid'], wlangroup_list[i]['name'])
        param_cfg = dict(wlangroup_name = wlangroup_list[i]['name'],
                         wlan_name_list = [wlan['ssid']])
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        i += 1
    
        
    zd_ip_addr = tbcfg['ZD']['ip_addr']
    ap_sym_dict = tbcfg['ap_sym_dict']
    single_band_mesh_path = get_single_band_mesh_peer(tbcfg, ap_sym_dict)
    
    active_ap = s_r_ap = single_band_mesh_path[1][0]
    #active_ap = s_r_ap = single_band_mesh_path[0]
    test_cfgs.extend(gen(active_ap, ap_mode= SINGLE_ROOT, ap_sym_dict = ap_sym_dict, \
                         wlan_group_list = wlangroup_list, zd_ip_addr = zd_ip_addr))
    #@author: Liang Aihua,@since:2014-12-18,@change: Distribute correct roles for APs.
    active_ap = s_m_ap = single_band_mesh_path[0]
    #active_ap = s_m_ap = single_band_mesh_path[1][0]
    
    #@author: Liang Aihua,@change: These steps has been contained in gen()
    #test_name = 'CB_ZD_Find_Active_AP'
    #common_name = 'Create an Active AP: %s to prepare for testing.' % (active_ap)     
    #param_cfg = dict(active_ap = active_ap)
    #test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_cfgs.extend(gen(active_ap, ap_mode= SINGLE_MESH, ap_sym_dict = ap_sym_dict, \
                         wlan_group_list = wlangroup_list, zd_ip_addr = zd_ip_addr))
    
    dual_band_mesh_path = get_dual_band_mesh_peer(tbcfg, ap_sym_dict)
    active_ap = d_r_ap = dual_band_mesh_path[1][0]
    #active_ap = d_r_ap = dual_band_mesh_path[0]
    test_cfgs.extend(gen(active_ap, ap_mode= DUAL_ROOT, ap_sym_dict = ap_sym_dict, \
                         wlan_group_list = wlangroup_list, zd_ip_addr = zd_ip_addr))
    
    active_ap = d_m_ap = dual_band_mesh_path[0]
    #active_ap = d_m_ap = dual_band_mesh_path[1][0]
    
    #@author: Liang Aihua,@change: These steps has been contained in gen()
    #test_name = 'CB_ZD_Find_Active_AP'
    #common_name = 'Create an Active AP: %s to prepare for testing.' % (active_ap)     
    #param_cfg = dict(active_ap = active_ap)
    #test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_cfgs.extend(gen(active_ap, ap_mode= DUAL_MESH, ap_sym_dict = ap_sym_dict, \
                         wlan_group_list = wlangroup_list, zd_ip_addr = zd_ip_addr))
    

    ap_list = [s_r_ap, s_m_ap, d_r_ap, d_m_ap]
    
    tl_id = '[Mesh link check when WLAN of Single band Root AP turn on/off]'
    test_cfgs.extend(build(tl_id, wlan_list, ap_mode = SINGLE_ROOT, ap_list = ap_list, zd_ip_addr = zd_ip_addr))
    
    tl_id = '[Mesh link check when WLAN of Single band MESH AP turn on/off]'    
    test_cfgs.extend(build(tl_id, wlan_list, ap_mode = SINGLE_MESH, ap_list = ap_list, zd_ip_addr = zd_ip_addr))
        
    tl_id = '[Mesh link check when WLAN of dual band Root AP turn on/off]'    
    test_cfgs.extend(build(tl_id, wlan_list, ap_mode = DUAL_ROOT, ap_list = ap_list, zd_ip_addr = zd_ip_addr))
    
    tl_id = '[Mesh link check when WLAN of dual band Mesh AP turn on/off]'    
    test_cfgs.extend(build(tl_id, wlan_list, ap_mode = DUAL_MESH, ap_list = ap_list, zd_ip_addr = zd_ip_addr))
    return test_cfgs
                
#generate wlan group to AP test cases. 
def gen(active_ap, ap_mode = SINGLE_ROOT, ap_sym_dict = None, wlan_group_list = None, zd_ip_addr = '192.168.0.2'):    
    test_cfgs = []
    ap_cfg = ap_sym_dict[active_ap]
    ap_model = ap_cfg['model']
    radios = const.get_radio_mode_by_ap_model(ap_model)    
    test_name = 'CB_ZD_Find_Active_AP'
    common_name = 'Create an Active AP: %s to prepare for testing.' % (active_ap)     
    param_cfg = dict(active_ap = active_ap)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    for radio in radios:    
            wg_name = wlan_group_list[ap_mode]['name']
            test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
            common_name = 'Associate AP: %s, radio: %s to WLAN Group: %s to prepare for testing.' % \
            (active_ap, radio, wg_name)     
            param_cfg = dict(active_ap = active_ap,
                             wlan_group_name = wg_name, 
                             radio_mode = radio)
            test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_AP_Ping'    
    common_name = 'Ping ZD from single band mesh AP %s.' % active_ap
    param_cfg = dict(target_ip = zd_ip_addr)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
    return test_cfgs 

#build mesh link test cases.
def build(tl_id, wlan_list, ap_mode = SINGLE_ROOT, ap_list = [], zd_ip_addr = '192.168.0.2'):    
    test_cfgs = []
    index = 0
    if ap_mode == SINGLE_ROOT:
        index = SINGLE_ROOT
    elif ap_mode == SINGLE_MESH:
        index = SINGLE_MESH
    elif ap_mode == DUAL_ROOT:
        index = DUAL_ROOT
    elif ap_mode == DUAL_MESH:
        index = DUAL_MESH
    else:
        raise Exception('Un-support mode %s' % ap_mode)
    
    active_ap = ap_list[index] 
    wlan_ssid = wlan_list[ap_mode]['ssid']
    test_name = 'CB_ZD_Find_Active_AP'
    common_name = '%sCreate an Active AP: %s to prepare for testing.' % (tl_id, active_ap)     
    param_cfg = dict(active_ap = active_ap)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
            
    
    test_name = 'CB_ZD_Schedule_WLAN_Service'
    common_name = '%sSchedule WLAN %s specific on' % (tl_id, wlan_ssid)    
    param_cfg = dict(ssid = wlan_ssid, 
                     on = False,
                     off = False, 
                     specific = True,
                     wlan_cfg = wlan_list[ap_mode])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_Ping'    
    common_name = '%sPing ZD from single band mesh AP %s.' % (tl_id, active_ap)
    param_cfg = dict(target_ip = zd_ip_addr)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Schedule_WLAN_Service'
    common_name = '%sSchedule WLAN %s specific off' % (tl_id, wlan_ssid)    
    param_cfg = dict(ssid = wlan_ssid, 
                     on = False,
                     off = True, 
                     specific = False,
                     wlan_cfg = wlan_list[ap_mode])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    
    test_name = 'CB_AP_Ping'
    common_name = '%sPing ZD from single band mesh AP %s.' % (tl_id, active_ap)
    param_cfg = dict(target_ip = zd_ip_addr)
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
      
    return test_cfgs  


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)
        
    ts_name = 'WLAN Service - configurable-mesh'
    ts = testsuite.get_testsuite(ts_name, 'WLAN Service - configurable-mesh-link[single/dual band]', combotest=True)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)      
    test_cfgs = define_test_configuration(tbcfg)
    
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
    create_test_suite(**_dict)

