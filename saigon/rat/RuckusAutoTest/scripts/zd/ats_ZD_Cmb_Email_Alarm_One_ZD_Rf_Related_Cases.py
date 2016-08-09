'''
create @2012/8/16, by west.li@ruckuswireless.com
zd email alarm rf related cases
'''


import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

def defineTestConfiguration(alarm_setting,wlan_cfg,ap_mac_to_disconnect):
    test_cfgs = [] 
    
    test_name = 'CB_ZD_CLI_Configure_Alarm'
    common_name = 'Configure alarm settings in ZD CLI' 
    test_cfgs.append(({'alarm_cfg': alarm_setting}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Get_Alarm_Info'
    common_name = 'Get alarm settings from ZD GUI' 
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Verify_Alarm_Cfg_In_GUI'
    common_name = 'Verify alarm settings in ZD GUI'
    test_cfgs.append(({'alarm_cfg': alarm_setting}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Disable_Alarm_Event'
    common_name = 'disable all event alarm through ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_All_Alarm_Disabled'
    common_name = 'verify all event alarm disabled from web UI'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'remove all wlan from zd'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Single_Wlan'
    common_name = "Create WLAN : %s" % (wlan_cfg['ssid']) 
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'disable_wlan_on_default_wlan_group':False}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'close Automatically approve all join requests from APs in zd web'
    test_cfgs.append(({'auto_approval': False,'max_clients':0}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Enable_Report_Rogue_Device'
    common_name = 'enable report rogue device'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Open_Backgroung_Scan'
    common_name = 'open background scan'
    test_cfgs.append(({'2_4':'10','5':''}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Force_AP_Standalone'
    common_name = 'make one ap become standalone ap'
    test_cfgs.append(({'ap_index':1}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = 'clear all zd alarms from zd web UI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = 'Remove all mails from mail server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name='Rogue AP,LAN Rogue AP'
    test_name = 'CB_ZDCLI_Enable_Alarm_Event' 
    common_name = '[%s]enable rogue AP Lan Rogue AP alarm in zd web' % test_case_name
    test_cfgs.append(({'event':['rogue-ap-detected','lan-rogue-ap-detected']}, test_name, common_name, 1, False))
    
    import copy
    wlan_cfg1=copy.deepcopy(wlan_cfg)
    wlan_cfg1['ssid']+='_121'
    test_name = 'CB_ZD_Create_Wlan_On_Standalone_AP'
    common_name = '[%s]create wlan in channel 1 in standalone ap' % test_case_name
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg1],'radio':'ng','channel':'8'},test_name, common_name, 2, False))    
    
    alarm='MSG_rogue_AP_detected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check rougue ap alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server rougue ap' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
        
    test_name = 'CB_AP_Ping'    
    common_name = '[%s]Ping standalone ap from ap under zd control to let ap know they are in the same subnet' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    alarm='MSG_lanrogue_AP_detected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check lan rougue ap alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server lan rougue ap' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Disable_Alarm_Event'
    common_name = '[%s]disable all event alarm through ZDCLI'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
#    
#    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
#    common_name = '[%s]clear all zd alarms from zd web UI' % test_case_name
#    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_case_name='SSID-spoofing AP Detected'
    test_name = 'CB_ZDCLI_Enable_Alarm_Event' 
    common_name = '[%s]enable SSID-spoofing AP Detected alarm in zd cli' % test_case_name
    test_cfgs.append(({'event':['ssid-spoofing-ap-detected']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Create_Wlan_On_Standalone_AP'
    common_name = '[%s]create wlan with the same ssid in zd in standalone ap channel 2' % test_case_name
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],'radio':'ng','channel':'2'},test_name, common_name, 2, False))   
    
    alarm='MSG_SSID_spoofing_AP_detected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check SSID-spoofing AP Detected alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify SSID-spoofing AP Detected Alarm Mail On Server' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Wlan_On_Standalone_AP'
    common_name = '[%s]create wlan with the different ssid in zd in standalone ap channel 2' % test_case_name
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg1],'radio':'ng','channel':'2'},test_name, common_name, 2, True))   
    
    test_name = 'CB_ZDCLI_Disable_Alarm_Event'
    common_name = '[%s]disable all event alarm through ZDCLI'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
#    
#    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
#    common_name = '[%s]clear all zd alarms from zd web UI'% test_case_name
#    test_cfgs.append(({}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_case_name='MAC-spoofing AP Detected'
    test_name = 'CB_ZDCLI_Enable_Alarm_Event' 
    common_name = '[%s]enable SSID-spoofing AP Detected alarm in zd cli' % test_case_name
    test_cfgs.append(({'event':['mac-spoofing-ap-detected']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_AP_Bssid'
    common_name = '[%s]get the bssid of the ap under zd control'%test_case_name
    test_cfgs.append(({'ap_index':0}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Set_AP_Wlan_Bssid'
    common_name = '[%s]set stand alone ap bssid the same to that under zd control'%test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    alarm='MSG_MAC_spoofing_AP_detected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check MAC-spoofing AP Detected alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
    common_name = '[%s]verify Alarm Mail On Server' % test_case_name  
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_AP_Wlan_Bssid'
    common_name = '[%s]restore stand alone ap bssid' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, True))  
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = '[%s]disable all alarm from zd web UI' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'open Automatically approve all join requests from APs in zd web'
    test_cfgs.append(({'max_clients':0}, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Force_AP_Standalone'
    common_name = 'let zd control the standalone ap'
    test_cfgs.append(({'ap_index':1,'op_type':'recovery'}, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Open_Backgroung_Scan'
    common_name = 'restore the background scan interval'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    return test_cfgs
    
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="ZD Email Alarm RF Related Cases"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    target_sta = sta_ip_list[attrs["sta_id"]]
    ap_mac_to_disconnect = tb_cfg['ap_sym_dict']['AP_01']['mac']
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="ZD Email Alarm RF Related Cases"
    alarm_setting=dict  (
                        email_addr = 'lab@example.net',
                        server_name = '192.168.0.252', 
                        server_port = 25, 
                        username = 'lab', 
                        password = 'lab4man1', 
#                        setting_name = 'ALARM-TRIGGER-IP-AUTH'
                        )
    import time
    wlan_cfg = {
        'ssid': "rugue_test_West-%s" % time.strftime("%H%M%S"),
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
    test_cfgs = defineTestConfiguration(alarm_setting,wlan_cfg,ap_mac_to_disconnect)
    ts = testsuite.get_testsuite(ts_name, "ZD Email Alarm RF Related Cases", interactive_mode = attrs["interactive_mode"], combotest=True)

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
           
    
    
    
    
    