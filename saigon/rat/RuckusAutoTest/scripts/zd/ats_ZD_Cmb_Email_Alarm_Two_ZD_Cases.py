'''
create @2012/8/9, by west.li@ruckuswireless.com
zd email alarm two zd cases
'''


import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration(alarm_setting,target_sta,mesh_ap):
    test_cfgs = [] 
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'before case start initial test environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'both ZD enable SR'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_Config_Alarm_Setting'
    common_name = 'config alarm email' 
    test_cfgs.append(({'alarm_setting': alarm_setting}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Disable_All_Alarm' 
    common_name = 'disable all alarm from zd web UI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = 'clear all zd alarms from zd1 web UI'
    test_cfgs.append(({'zd':'zd1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = 'clear all zd alarms from zd2 web UI'
    test_cfgs.append(({'zd':'zd2'}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = 'Remove all mails from mail server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_case_name='SR Related Alarm'
    test_name = 'CB_ZD_Enable_Alarm' 
    common_name = '[%s]enable SR related alarm in zd web' % test_case_name
    test_cfgs.append(({'alarm_list':['State_Changed_check_box','Active_Connected_check_box','Standby_Connected_check_box',
                                     'Active_Disconnected_check_box','Standby_Disconnected_check_box']},
                       test_name, common_name, 1, False))
    
#    test_name = 'CB_ZD_SR_Disable'
#    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
#    test_cfgs.append(({},test_name, common_name, 2, False))
#    
#    test_name = 'CB_ZD_SR_Enable'
#    common_name = '[%s]both ZD enable SR to trigger standby connected alarm'% test_case_name
#    test_cfgs.append(({},test_name,common_name,2,False))
#    
#    alarm='MSG_cltr_standby_connected'
#    test_name = 'CB_ZD_SR_Check_Alarm'
#    common_name = '[%s]check two zd standby connected alarm in web' % test_case_name
#    test_cfgs.append(({'alarm':alarm},test_name, common_name, 2, False)) 
#        
#    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
#    common_name = '[%s]verify Alarm Mail On Server standby connedted' % test_case_name  
#    test_cfgs.append(({},test_name, common_name, 2, False))
#    
#    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
#    common_name = '[%s]clear all zd1 alarms from zd1 web UI standby connedted'% test_case_name
#    test_cfgs.append(({'zd':'zd1'}, test_name, common_name, 2, False))
#    
#    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
#    common_name = '[%s]clear all zd2 alarms from zd2 web UI standby connedted'% test_case_name
#    test_cfgs.append(({'zd':'zd2'}, test_name, common_name, 2, False))
#      
#    test_name = 'CB_ZD_Clear_Alarm_MailBox'
#    common_name = '[%s]Remove all mails from mail server standby connedted' % test_case_name
#    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on active ZD to trigger standby disconnect and state change alarm' % test_case_name
    test_cfgs.append(({'single':'active_zd'},test_name, common_name, 2, False))
    
    alarm='MSG_cltr_standby_disconnected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check standby disconnected alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm,'zd':'standby_zd'},test_name, common_name, 2, False))    
    
#    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
#    common_name = '[%s]verify Alarm Mail On Server standby disconnected' % test_case_name  
#    test_cfgs.append(({},test_name, common_name, 2, False))
    
    alarm='MSG_cltr_change_to_active'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check state change alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm,'zd':'standby_zd'},test_name, common_name, 2, False))    
    
#    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
#    common_name = '[%s]verify Alarm Mail On Server state change' % test_case_name  
#    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd1 web UI state change'% test_case_name 
    test_cfgs.append(({'zd':'zd1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd2 web UI  state change'% test_case_name 
    test_cfgs.append(({'zd':'zd2'}, test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server  state change' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]enable SR to check active connected alarm' % test_case_name
    test_cfgs.append(({},test_name,common_name,2,False))
    
    alarm='MSG_cltr_active_connected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check active connected alarm in web' % test_case_name
    #@author: Anzuo, 'zd':'active_zd', zd should be active zd
    test_cfgs.append(({'alarm':alarm,'zd':'active_zd'},test_name, common_name, 2, False))
#    
#    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
#    common_name = '[%s]verify Alarm Mail On Server active connectec' % test_case_name  
#    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd1 web UI active connect' % test_case_name
    test_cfgs.append(({'zd':'zd1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd2 web UI active connect' % test_case_name
    test_cfgs.append(({'zd':'zd2'}, test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server active connect' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on standby ZD to trigger active disconnect' % test_case_name
    test_cfgs.append(({'single':'standby_zd'},test_name, common_name, 2, False))
     
    alarm='MSG_cltr_active_disconnected'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check active disconnected alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm,'zd':'active_zd'},test_name, common_name, 2, False))    
    
#    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
#    common_name = '[%s]verify Alarm Mail On Server active disconnected' % test_case_name  
#    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd1 web UI active disconnected'% test_case_name 
    test_cfgs.append(({'zd':'zd1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Clear_Alarm_Log_On_ZD' 
    common_name = '[%s]clear all zd alarms from zd2 web UI active disconnected'% test_case_name 
    test_cfgs.append(({'zd':'zd2'}, test_name, common_name, 2, True))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server active disconnect' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_case_name='uplink AP Lost'
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR'% test_case_name
    test_cfgs.append(({},test_name,common_name,1,False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = '[%s]Create Mesh AP'% test_case_name
    test_cfgs.append(({'active_ap':mesh_ap,
                       'ap_tag': mesh_ap}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Alarm' 
    common_name = '[%s]enable rogue dhcp server detected alarm in zd web' % test_case_name
    test_cfgs.append(({'alarm_list':['Uplink_AP_Lost_check_box']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = '[%s]Enable mesh in ZD and disable switch port connectet to ap %s,let it become mesh ap'% (test_case_name,mesh_ap)
    test_cfgs.append(({'mesh_ap_list':[mesh_ap],'for_upgrade_test':False},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on the two ZDs' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Delete_All_AP'
    common_name = '[%s]from former standby zd,delete all ap in list' % test_case_name
    test_cfgs.append(({'zd':'standby_zd'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Let_Mesh_AP_Connect_To_Standby_ZD'
    common_name = '[%s]let mesh ap connect to former standby zd' % test_case_name
    test_cfgs.append(({'zd':'standby_zd'},test_name, common_name, 2, False))
    
    alarm='MSG_AP_no_mesh_uplink'
    test_name = 'CB_ZD_Check_Alarm'
    common_name = '[%s]check uplink ap lost alarm in web' % test_case_name
    test_cfgs.append(({'alarm':alarm,'zd':'standby_zd','mesh_ap_tag':mesh_ap},test_name, common_name, 2, False))    
    
#    test_name = 'CB_ZD_Check_Alarm_Mail_On_Server'
#    common_name = '[%s]verify Alarm Mail On Server' % test_case_name  
#    test_cfgs.append(({},test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Clear_Alarm_MailBox'
    common_name = '[%s]Remove all mails from mail server' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))  
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to all aps' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on the two ZDs to set factory' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '[%s]set zd1to factory default to disable mesh' % test_case_name
    test_cfgs.append(({'zd':'zd1'},test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '[%s]set zd2 to factory default to disable mesh' % test_case_name
    test_cfgs.append(({'zd':'zd2'},test_name, common_name, 2, True)) 
    
    return test_cfgs
    
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="ZD Email Alarm two zd Cases"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    target_sta = sta_ip_list[attrs["sta_id"]]
    if tb_cfg['ap_sym_dict'].has_key('AP_01'):
        mesh_ap = 'AP_01'
    #@author: Tan ,@since:zf-14122 
#    if not tb_cfg['ap_sym_dict'].has_key('AP_02'):
#        raise Exception("Need at least two active APs")            
#    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="ZD Email Alarm two zd Cases"
    alarm_setting=dict  (
                        email_addr = 'lab@example.net',
                        server_name = '192.168.0.252', 
                        server_port = 25, 
                        username = 'lab', 
                        password = 'lab4man1', 
#                        setting_name = 'ALARM-TRIGGER-IP-AUTH'
                        )
    test_cfgs = defineTestConfiguration(alarm_setting,target_sta,mesh_ap)
    ts = testsuite.get_testsuite(ts_name, "ZD Email Alarm two zd Cases", interactive_mode = attrs["interactive_mode"], combotest=True)

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
           
    
    
    
    
    
