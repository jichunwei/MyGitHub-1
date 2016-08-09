'''
create @2012/6/28, by west.li@ruckuswireless.com
zd email alarm not rf related cases
'''


import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration(alarm_setting,target_sta,ap_tag,zd_ip):
    test_cfgs = [] 
    
    test_name = 'CB_ZD_Config_Alarm_Setting'
    common_name = 'config alarm email' 
    test_cfgs.append(({'alarm_setting': alarm_setting}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = 'disable all alarm from zd web UI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    #chen.tao 2014-01-16 to fix ZF-6824
    test_name = 'CB_ZD_Enable_Mgmt_Interface'
    common_name = 'Enable Management Interface from web UI'
    test_cfgs.append(({'ip_addr':'192.168.0.5','vlan':1},test_name, common_name, 0, False))
    #chen.tao 2014-01-16 to fix ZF-6824
    
    test_name = 'CB_ZD_CLI_Verify_All_Event_Disabled'
    common_name = 'verify the value is sync from Web to ZDCLI'
    test_cfgs.append(({},test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = 'clear all zd alarms from zd web UI'
    #@zj 20140717 fix ZF-9200
    test_cfgs.append(({'ell':True}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = 'Remove all mails from mail server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_case_name='Rogue DHCP Server'
    test_name = 'CB_ZD_Enable_Alarm' 
    common_name = '[%s]enable rogue dhcp server detected alarm in zd web' % test_case_name
    test_cfgs.append(({'alarm_list':['Rogue_DHCP_Server_Detected_check_box']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_DHCP_Server'
    common_name = '[%s]enable DHCP server in zd' % test_case_name
    test_cfgs.append(({'option':'enable'},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Triger_Rogue_DHCP_Alarm'
    common_name = '[%s]disable/enable rogue DHCP server detection in zd' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False)) 
    
    alarm='MSG_admin_rogue_dhcp_server'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check rougue DHCP alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_DHCP_Server'
    common_name = '[%s]disable DHCP server in zd' % test_case_name
    test_cfgs.append(({'option':'disabled'},test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = '[%s]disable all alarm from zd web UI' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd web UI' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_case_name='Incomplete Primary/Secondary IP Settings'
    test_name = 'CB_ZD_Enable_Alarm' 
    common_name = '[%s]enable rogue dhcp server detected alarm in zd web' % test_case_name
    test_cfgs.append(({'alarm_list':['Incomplete_Primary_Secondary_IP_Settings_check_box']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Set_Primary_Secondary_ZD'
    common_name = '[%s]set primary zd ,not set secondary' % test_case_name
    test_cfgs.append(({'enabled':True,'primary_zd_ip':zd_ip,'secondary_zd_ip':'','keep_zd_ip':True},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Scaling_APs_Reboot'
    common_name = '[%s]reboot all the aps connected to zd' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))    
    
    alarm='MSG_AP_keep_no_AC_cfg'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check Incomplete Primary/Secondary IP Settings alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_Primary_Secondary_ZD'
    common_name = '[%s]disable primary secondary zd' % test_case_name
    test_cfgs.append(({'enabled':False},test_name, common_name, 2, True))    
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = '[%s]disable all alarm from zd web UI'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd web UI'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_case_name='AAA Server Unreachable'
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[%s]Remove all WLAN from ZD'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Enable_Alarm' 
    common_name = '[%s]enable rogue dhcp server detected alarm in zd web' % test_case_name
    test_cfgs.append(({'alarm_list':['AAA_Server_Unreachable_check_box']}, test_name, common_name, 2, False))
    
    radius_server={'server_addr': '169.0.2.1',
                    'server_port' : '1833',
                    'server_name' : 'AAA_Alarm_server',
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': 'chap',
                    'username': 'rad.cisco.user',
                    'password': 'rad.cisco.user',
                    }
    wlan_cfg={'username': 'ras.eap.user', 
              'ssid': 'wlan_alarm_aaa_unreachable_test', 
              'auth_svr':radius_server['server_name'], 
              'encryption': 'AES', 
              'key_index': '', 
              'auth': 'EAP', 
              'key_string': '', 
              'password': 'ras.eap.user', 
              'wpa_ver': 'WPA2' #@author Tanshiciong @since 20150421 zf-12794
              }
    alarm='MSG_RADIUS_service_outage'
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '[%s]Create Authentication Servers' % test_case_name
    param_cfg = dict(auth_ser_cfg_list = [radius_server])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s]Create a 802.1xEAP on ZD' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = '%sCreate station: %s' % (test_case_name,target_sta)
    test_params = {'sta_tag': target_sta, 'sta_ip_addr': target_sta}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '[%s]try to associate the station %s to the wlan %s' % (test_case_name,target_sta, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':target_sta,'expected_failed':True},test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check AAA Server Unreachable alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server'% test_case_name   
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[%s]Remove all WLAN from ZD after test'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_Authentication_Server'
    common_name = '[%s]remove Authentication Servers' % test_case_name
    param_cfg = dict(auth_ser_name_list = [radius_server['server_name']])
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = '[%s]disable all alarm from zd web UI'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd web UI'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_case_name='AP Lost Contact'
    test_name = 'CB_ZD_Enable_Alarm' 
    common_name = '[%s]enable rogue dhcp server detected alarm in zd web' % test_case_name
    test_cfgs.append(({'alarm_list':['ap_lost_contact_check_box']}, test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[%s]Disable switch port connectet to one ap' % test_case_name
    test_cfgs.append(({'ap_tag':ap_tag,'device':'ap'},test_name, common_name, 2, False))

    alarm='MSG_AP_lost'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check ap lost contact alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to ap' % test_case_name
    test_cfgs.append(({'device':'ap','number':1},test_name, common_name, 2, True))  
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = '[%s]disable all alarm from zd web UI' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd web UI' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))

    #chen.tao 2014-01-16 to fix ZF-6824
    test_name = 'CB_ZD_Disable_Mgmt_Interface'
    common_name = 'Disable Management Interface from web UI'
    test_cfgs.append(({},test_name, common_name, 0, True)) 
    #chen.tao 2014-01-16 to fix ZF-6824
    return test_cfgs
    
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="ZD Email Alarm not RF Related Cases"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    target_sta = sta_ip_list[attrs["sta_id"]]
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="ZD Email Alarm not RF Related Cases"
    alarm_setting=dict  (
                        email_addr = 'lab@example.net',
                        server_name = '192.168.0.252', 
                        server_port = 25, 
                        username = 'lab', 
                        password = 'lab4man1', 
#                        setting_name = 'ALARM-TRIGGER-IP-AUTH'
                        )
      
    mgmt_if_enable = raw_input('this testbed enable mgmt vlan or not?"Y" for yes,"N" for No:')
    if mgmt_if_enable=="Y":
        zd_ip = '192.168.128.2'
    else:
        zd_ip = '192.168.0.2'
        
    test_cfgs = defineTestConfiguration(alarm_setting,target_sta,'AP_01',zd_ip)
    ts = testsuite.get_testsuite(ts_name, "ZD Email Alarm not RF Related Cases", interactive_mode = attrs["interactive_mode"], combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)   
    
    
 
if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
           
    
    
    
    
    