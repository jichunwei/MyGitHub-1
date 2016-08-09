'''
512 clients support
2012-10-10
by west
case 1,default apgroup,set max clients number in web and verify in cli
    for each ap model,get the max supported client number
    verify 1 and max supported number and one random between them can be set
case 2,default apgroup,set max clients number in cli and verify in web
    for each ap model,get the max supported client number
    verify 1 and max supported number and one random between them can be set
    verify 0 and max supported number+1 can not be set
case 3,new apgroup,set max clients number in cli and verify in web
    for each ap model,get the max supported client number
    verify 1 and max supported number and one random between them can be set
case 4,new wlan,assign wlan to default wlan group,set max clients number in web and verify in web
    verify 1 and 512 and one random between them can be set
case 5,wlan in case 4,set max clients number in cli and verify in cli
    verify 1 and 512 and one random between them can be set
    verify 0 and 513 can not be set

case 6,7 enable mesh,root and mesh ap can work
    enable mesh,1 root ap and 1 mesh ap,
    disable wlan service in mesh ap,client connect to root ap,ping 192.168.0.252
    disable wlan service in root ap,client connect to mesh ap, ping 192.168.0.252
    
case 8,check client info in zd web
    check wlan page client number
    check wlan info page client status
    ap  page check client number
    ap detail page client status
    client page check client status
    dashboard check client number
 
set factory to disable mesh 
'''


import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = [] 
#    root_ap_macs = tcfg['root_aps']
#    mesh_ap_mac = tcfg['mesh_ap']
    sta_tag = tcfg['target_sta']
    dest_ip = tcfg['dest_ip']
    ap_grp_name='New_ap_grp'
    time_str=time.strftime("%H%M%S")
    wlan_cfg= {"name" : "wlan_512_client_auto_test_%s"%time_str,
                "ssid" : "wlan_512_client_auto_test_%s"%time_str,
                "auth" : "open",
                "encryption" : "none",
                "max_clients":"512"
                }

    new_ap_grp_cfg={'name':ap_grp_name
                   }
    
    test_name = 'CB_ZD_CLI_Configure_WLAN' 
    common_name = 'create new wlan%s'%wlan_cfg["name"]
    test_cfgs.append(({'wlan_cfg':wlan_cfg,}, test_name, common_name, 0, False))

    test_name = 'CB_ZDCLI_New_AP_Group' 
    common_name = 'create new ap group %s'%(ap_grp_name)
    test_cfgs.append((new_ap_grp_cfg, test_name, common_name, 0, False))
    
    test_case_name='[default ap group,Web configuration]'
    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset min client number in web and verify in cli'%test_case_name
    test_cfgs.append(({'set_type':'Min'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset client number between max and min in web and verify in cli'%test_case_name
    test_cfgs.append(({'set_type':'Random'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset max client number in web and verify in cli'%test_case_name
    test_cfgs.append(({'set_type':'Max'}, test_name, common_name, 2, False))
    
    test_case_name='[default ap group,Cli configuration]'
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset min client number in cli and verify in web'%test_case_name
    test_cfgs.append(({'set_type':'Min'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset client number between max and min in cli and verify in web'%test_case_name
    test_cfgs.append(({'set_type':'Random'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset max client number in cli and verify in web'%test_case_name
    test_cfgs.append(({'set_type':'Max'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset client number lower than minimum value in cli and verify in web'%test_case_name
    test_cfgs.append(({'set_type':'Lower'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset max client number higher than max in cli and verify in web'%test_case_name
    test_cfgs.append(({'set_type':'Higher'}, test_name, common_name, 2, False))
    
    test_case_name='[new created ap group,Web configuration]'
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset min client number in cli and verify in web'%test_case_name
    test_cfgs.append(({'grp_name':ap_grp_name,'set_type':'Min'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset client number between max and min in cli and verify in web'%test_case_name
    test_cfgs.append(({'grp_name':ap_grp_name,'set_type':'Random'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sset max client number in cli and verify in web'%test_case_name
    test_cfgs.append(({'grp_name':ap_grp_name,'set_type':'Max'}, test_name, common_name, 2, False))
    
    test_case_name='[wlan,Web Configuration]'
    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number' 
    common_name = '%sset client number a random number in cli and verify in web'%test_case_name
    test_cfgs.append(({'wlan_name':wlan_cfg['name'],'number':'random'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number' 
    common_name = '%sset client number 512 in web and verify in cli'%test_case_name
    test_cfgs.append(({'wlan_name':wlan_cfg['name']}, test_name, common_name, 2, False))
    
    test_case_name='[wlan,Cli Configuration]'
    test_name = 'CB_ZDCLI_Set_Wlan_Max_Clients_Number' 
    common_name = '%sset client number a random number in web and verify in cli'%test_case_name
    test_cfgs.append(({'wlan_name':wlan_cfg['name'],'number':'random'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Set_Wlan_Max_Clients_Number' 
    common_name = '%sset client number 512 in cli and verify in web'%test_case_name
    test_cfgs.append(({'wlan_name':wlan_cfg['name']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Set_Wlan_Max_Clients_Number' 
    common_name = '%sset client number 0 in cli and verify in web'%test_case_name
    test_cfgs.append(({'wlan_name':wlan_cfg['name'],'number':'lower'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Set_Wlan_Max_Clients_Number' 
    common_name = '%sset client number to bigger than 512 in cli and verify in web'%test_case_name
    test_cfgs.append(({'wlan_name':wlan_cfg['name'],'number':'higher'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD and disable switch port connectet to ap %s,let it become mesh ap'% tcfg['mesh_ap']
    test_cfgs.append(({'mesh_ap_list':tcfg['mesh_ap'],'for_upgrade_test':False},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station: %s' % (sta_tag)
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Set_Wlan_Max_Clients_Number' 
    common_name = 'set wlan client number 512 in cli and verify in web'
    test_cfgs.append(({'wlan_name':wlan_cfg['name']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Set_AP_Model_Max_Clients_Number' 
    common_name = 'set ap_group max client number in cli and verify in web'
    test_cfgs.append(({'grp_name':ap_grp_name,'set_type':'Max'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = 'set default apgroup max client number in web and verify in cli'
    test_cfgs.append(({'set_type':'Max'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Wlan_Service'
    common_name = 'enable root ap wlan service to test'
    test_cfgs.append(({'ap_tag':tcfg['root_aps'], 'enable': True},test_name, common_name, 0, False))
    
    test_case_name='[root ap under 512 configuration]'

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s ' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Wlan_Service'
    common_name = 'enable mesh ap wlan service after root ap testing'
    test_cfgs.append(({'ap_tag':tcfg['mesh_ap'],'enable': True},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Wlan_Service'
    common_name = 'disable root ap wlan service to test mesh ap'
    test_cfgs.append(({'ap_tag':tcfg['root_aps']},test_name, common_name, 0, False))

    test_case_name='[mesh ap under 512 configuration]'
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s ' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Client_Number_In_Dashboard'
    common_name = '%s verify the station number in dashboard' % (test_case_name)
    test_cfgs.append(({'sta_number':1},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Connected_Client_Number'
    common_name = '%s verify the station number in ap brief page' % (test_case_name)
    test_cfgs.append(({'ap_tag': tcfg['mesh_ap'],'num_sta':1},test_name, common_name, 2, False))
    
    sta_info={'status': 'Authorized',
              'auth_method': wlan_cfg['auth'].upper(),
              'wlan': wlan_cfg['ssid'],
              }
    test_name = 'CB_ZD_Verify_Client_Info_In_AP_Detail_Page'
    common_name = '%s verify the station status in ap detail page' % (test_case_name)
    test_cfgs.append(({'ap_tag': tcfg['mesh_ap'],'sta_tag':sta_tag,'info':sta_info},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Connected_Client_Number'
    common_name = '%s verify the station number in wlan brief page' % (test_case_name)
    test_cfgs.append(({'wlan_name': wlan_cfg['name'],'num_sta':1},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Client_Info_In_Wlan_Detail_Page'
    common_name = '%s verify the station status in wlan detail page' % (test_case_name)
    test_cfgs.append(({'wlan_name': wlan_cfg['name'],'sta_tag':sta_tag,'info':sta_info},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Active_Client'
    common_name = '%s verify the station status in client brief page' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,'expected_info':sta_info,'info_cat': 'brief'},test_name, common_name, 2, False))
    
    sta_info={
              'authMethod': wlan_cfg['auth'].upper(),
              'wlan': wlan_cfg['ssid'],
              'ap_tag': tcfg['mesh_ap'],
              }
    
    test_name = 'CB_ZD_Verify_Active_Client'
    common_name = '%s verify the station status in client detail page' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,'expected_info':sta_info,'info_cat': 'detail'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, True))  
    
    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="Xian 512 client support"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            root_aps = raw_input("Choose an root AP(input multi item if there will be more than 1 root AP, split with space): ")
            root_ap_list = root_aps.split(' ')
            for root_ap in root_ap_list:
                if root_ap not in ap_sym_dict:
                    print "AP[%s] doesn't exist." % root_ap
                
                else:
                    break
            
            mesh_ap = raw_input("Choose an mesh AP: ")
            if mesh_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % mesh_ap
            
            else:
                break
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="Xian 512 client support"

    tcfg = dict(root_aps = root_ap_list,
                target_sta = target_sta,
                dest_ip= '192.168.0.252',
                mesh_ap=mesh_ap
                )
    test_cfgs = define_test_configuration(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    ts = testsuite.get_testsuite(ts_name, "Xian 512 client support", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
