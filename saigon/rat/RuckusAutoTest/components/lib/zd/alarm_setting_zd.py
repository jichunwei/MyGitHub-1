import time, logging

LOCATORS_CFG_ALARM_SETTINGS = dict(
    email_from_textbox = "//input[@id='email_from']",#chen.tao 2014-2-18, to fix ZF-7119
    smtp_port_textbox = "//input[@id='smtp-port']",
    username_textbox = "//input[@id='smtp-user']", 
    password_textbox = "//input[@id='smtp-pass']", 
    confirm_password_textbox = "//input[@id='smtp-pass2']",
    test_button = "//input[@id='test-notif']",
    show_encryption_option = "//form[@id='form-email-server']//a[@href='#']",
    tls_checkbox = "//input[@id='smtp-tls']",
    starttls_checkbox = "//input[@id='smtp-starttls']",
    msg_notify_text = "//span[@id='msg-notif']",
    msg_notify_success = "Success!",
    test_alarm_title = 'testing alarm',
    test_alarm_message = 'This is an alarm test.',
)

LOCATORS_CFG_ALARM_EVENTS = dict(
    #locators related to email alarm event add by west.li
    All_Alarm_Event_check_box       = "//input[@id='select-all']" ,
    
    Rogue_AP_Detected_check_box     = "//input[@id='MSG_rogue_AP_detected']" ,
    Rogue_Device_Detected_check_box = "//input[@id='MSG_ad_hoc_network_detected']" ,
    ap_lost_contact_check_box       = "//input[@id='MSG_AP_lost']" ,
    SSID_spoofing_AP_detected_check_box = "//input[@id='MSG_SSID_spoofing_AP_detected']" ,
    MAC_spoofing_AP_Detected_check_box = "//input[@id='MSG_MAC_spoofing_AP_detected']" ,
    Rogue_DHCP_Server_Detected_check_box = "//input[@id='MSG_admin_rogue_dhcp_server']" ,
    
    Temporary_license_expired_check_box = "//input[@id='MSG_admin_templic_expired']" ,
    Temporary_license_will_expire_check_box = "//input[@id='MSG_admin_templic_oneday']" ,
    LAN_Rogue_AP_Detected_check_box = "//input[@id='MSG_lanrogue_AP_detected']" ,
    AAA_Server_Unreachable_check_box = "//input[@id='MSG_RADIUS_service_outage']" ,
    AP_Has_Hardware_Problem_check_box = "//input[@id='MSG_AP_hardware_problem']" ,
    Uplink_AP_Lost_check_box = "//input[@id='MSG_AP_no_mesh_uplink']" ,
    
    Incomplete_Primary_Secondary_IP_Settings_check_box = "//input[@id='MSG_AP_keep_no_AC_cfg']" ,
    State_Changed_check_box = "//input[@id='MSG_cltr_change_to_active']" ,
    Active_Connected_check_box = "//input[@id='MSG_cltr_active_connected']" ,
    Standby_Connected_check_box = "//input[@id='MSG_cltr_standby_connected']" ,
    Active_Disconnected_check_box = "//input[@id='MSG_cltr_active_disconnected']" ,
    Standby_Disconnected_check_box = "//input[@id='MSG_cltr_standby_disconnected']" ,
    
    alarm_event_apply_button = "//input[@id='apply-alarmevent']" ,
)
def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ALARM_SETTINGS)

def nav_to_system(zd):
    #@author: Jane.Guo @since: 2013-9 adapt to 9.8 move alarm email to system page
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    
def enable_all_email_event_alarm(zd):
    xlocs = LOCATORS_CFG_ALARM_EVENTS
    loc     =xlocs['All_Alarm_Event_check_box']
    button  =xlocs['alarm_event_apply_button']
    nav_to(zd)
    zd.s.click_if_not_checked(loc)
    zd.s.click_and_wait(button)
    
def disable_all_email_event_alarm(zd):
    xlocs = LOCATORS_CFG_ALARM_EVENTS
    loc     =xlocs['All_Alarm_Event_check_box']
    button  =xlocs['alarm_event_apply_button']
    nav_to(zd)
    zd.s.click_if_not_checked(loc)
    time.sleep(0.5)
    zd.s.click_if_checked(loc)
    time.sleep(0.5)
    zd.s.click_and_wait(button)
    
def enable_email_event_alarm(zd,alarm_event_list,disable_all_in_advance=False):
    xlocs = LOCATORS_CFG_ALARM_EVENTS
    loc     =xlocs['All_Alarm_Event_check_box']
    button  =xlocs['alarm_event_apply_button']
    nav_to(zd)
    if disable_all_in_advance:
        zd.s.click_if_not_checked(loc)
        zd.s.click_if_checked(loc)
    for event_loc in alarm_event_list:
        loc = xlocs[event_loc]
        zd.s.click_if_not_checked(loc)
    zd.s.click_and_wait(button)

def all_email_event_disabled(zd):
    xlocs = LOCATORS_CFG_ALARM_EVENTS
    loc     =xlocs['All_Alarm_Event_check_box']
    nav_to(zd)
    zd.refresh()
    if zd.s.is_checked(loc):
        return False,'all event are enabled'
    for loc in xlocs:
        if zd.s.is_checked(xlocs[loc]):
            return False,'event %s is enabled'%loc
    return True,'all event are disabled'
    
def check_enabled_email_event(zd,alarm_event_list):
    logging.info('the expected event is %s'%alarm_event_list)
    xlocs = LOCATORS_CFG_ALARM_EVENTS
    nav_to(zd)
    for event in xlocs:
        if event in alarm_event_list:
            if not zd.s.is_checked(xlocs[event]):
                return False,'event %s not enabled'%event
        if event not in alarm_event_list:
            if zd.s.is_checked(xlocs[event]):
                return False,'event %s enabled'%event  
    return True,'all event in list is enabled and all event not in list not enabled'

def get_alarm_setting(zd):
    xlocs = LOCATORS_CFG_ALARM_SETTINGS
    nav_to(zd)#@author: chen.tao since 2014-10-30, change the checkbox xpath
    email_enable = zd.s.is_checked(zd.info['loc_cfg_alarm_settings_doemail_checkbox'])
    
    if email_enable:
        email_addr = zd.s.get_value(zd.info['loc_cfg_alarm_settings_email_textbox'])
        #@author: Jane.Guo @since: 2013-9 adapt to 9.8 move alarm email to system page
        nav_to_system(zd)
        smtp_server = zd.s.get_value(zd.info['loc_cfg_system_alarm_smtp_ip_textbox'])
    
        server_port = zd.s.get_value(xlocs['smtp_port_textbox'])
        username = zd.s.get_value(xlocs['username_textbox'])
        password = zd.s.get_value(xlocs['password_textbox'])
        
        tls = zd.s.is_checked(xlocs['tls_checkbox'])
        starttls = zd.s.is_checked(xlocs['starttls_checkbox'])
        
        if tls and starttls:
            encrypt = 'Starttls'
        elif tls:
            encrypt = 'tls'
        else:
            encrypt = 'None'
    else:
        email_addr = ''
        smtp_server = ''
        server_port = ''
        username = ''
        password = ''
        encrypt = ''
            
    alarm_dict = {'enabled' : email_enable,
                 'email_addr': email_addr,
                 'smtp_server': smtp_server,
                 'server_port': server_port,
                 'username': username,
                 'password': password,
                 'encrypt': encrypt
                 }
    return alarm_dict
    
def set_alarm_email(zd, email_addr="", server_name="", server_port="25", username="", password="", tls_option = False, starttls = False, enable = True):
    xlocs = LOCATORS_CFG_ALARM_SETTINGS
    #@author: Jane.Guo @since: 2013-9 adapt to 9.8 move alarm email to system page
    nav_to_system(zd)    
    if not zd.s.is_checked(zd.info['loc_cfg_system_alarm_enable_checkbox']):
        zd.s.click_and_wait(zd.info['loc_cfg_system_alarm_enable_checkbox'])
    zd.s.type_text(xlocs['email_from_textbox'], email_addr)#chen.tao 2014-2-18, to fix ZF-7119
    zd.s.type_text(zd.info['loc_cfg_system_alarm_smtp_ip_textbox'], server_name)
    zd.s.type_text(xlocs['smtp_port_textbox'], server_port)
    zd.s.type_text(xlocs['username_textbox'], username)
    zd.s.type_text(xlocs['password_textbox'], password)
    zd.s.type_text(xlocs['confirm_password_textbox'], password)
    
    zd.s.click_and_wait(xlocs['show_encryption_option'])
    if (not zd.s.is_checked(xlocs['tls_checkbox']) and tls_option):
        zd.s.click_and_wait(xlocs['tls_checkbox'])
        if (not zd.s.is_checked(xlocs['starttls_checkbox']) and starttls):
            zd.s.click_and_wait(xlocs['starttls_checkbox'])
        if (zd.s.is_checked(xlocs['starttls_checkbox']) and not starttls):
            zd.s.click_and_wait(xlocs['starttls_checkbox'])
    if (zd.s.is_checked(xlocs['tls_checkbox']) and not tls_option):
        zd.s.click_and_wait(xlocs['tls_checkbox'])
            
    zd.s.click_and_wait(zd.info['loc_cfg_system_alarm_apply_button'])
    
    nav_to(zd)
    checkbox = zd.info['loc_cfg_alarm_settings_doemail_checkbox']
    if (not zd.s.is_checked(checkbox)):
        zd.s.click_and_wait(checkbox)
    if not enable: 
        zd.s.click_and_wait(checkbox)
            
    zd.s.type_text(zd.info['loc_cfg_alarm_settings_email_textbox'], email_addr)
    zd.s.click_and_wait(zd.info['loc_cfg_alarm_settings_notify_apply_button'])
        
    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())    
    
#######@zj20140522 optimization setting email alarm zf-8437
def set_alarm_email_syscfg(zd, email_addr="lab@example.net", server_name="192.168.0.252", server_port="25", username="lab", password="lab4man1", tls_option = False, starttls = False):
    xlocs = LOCATORS_CFG_ALARM_SETTINGS
    nav_to_system(zd)
    enablecheckbox = zd.info['loc_cfg_system_alarm_enable_checkbox']
    if not zd.s.is_checked(enablecheckbox):
        zd.s.click_and_wait(enablecheckbox)
    zd.s.type_text(xlocs['email_from_textbox'], email_addr)
    zd.s.type_text(zd.info['loc_cfg_system_alarm_smtp_ip_textbox'], server_name)
    zd.s.type_text(xlocs['smtp_port_textbox'], server_port)
    zd.s.type_text(xlocs['username_textbox'], username)
    zd.s.type_text(xlocs['password_textbox'], password)
    zd.s.type_text(xlocs['confirm_password_textbox'], password)
    
    zd.s.click_and_wait(xlocs['show_encryption_option'])
    if (not zd.s.is_checked(xlocs['tls_checkbox']) and tls_option):
        zd.s.click_and_wait(xlocs['tls_checkbox'])
        if (not zd.s.is_checked(xlocs['starttls_checkbox']) and starttls):
            zd.s.click_and_wait(xlocs['starttls_checkbox'])
        if (zd.s.is_checked(xlocs['starttls_checkbox']) and not starttls):
            zd.s.click_and_wait(xlocs['starttls_checkbox'])
    if (zd.s.is_checked(xlocs['tls_checkbox']) and not tls_option):
        zd.s.click_and_wait(xlocs['tls_checkbox'])
            
    zd.s.click_and_wait(zd.info['loc_cfg_system_alarm_apply_button'])

    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())    

def set_alarm_email_alarmcfg(zd, email_addr, enable = True):    
    nav_to(zd)
    checkbox = zd.info['loc_cfg_alarm_settings_doemail_checkbox']
    if (not zd.s.is_checked(checkbox)):
        zd.s.click_and_wait(checkbox)
    if not enable: 
        zd.s.click_and_wait(checkbox)
            
    zd.s.type_text(zd.info['loc_cfg_alarm_settings_email_textbox'], email_addr)
    zd.s.click_and_wait(zd.info['loc_cfg_alarm_settings_notify_apply_button'])
        
    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())    


def clear_alarm_settings(zd):
    nav_to(zd)
    set_alarm_email_alarmcfg(zd, '', enable = False)
    zd.s.click_and_wait(zd.info['loc_cfg_alarm_settings_notify_apply_button'])
    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())  
    
def clear_syscfg_alarm_settings(zd):
    nav_to_system(zd)
    enablecheckbox = zd.info['loc_cfg_system_alarm_enable_checkbox']
    if zd.s.is_checked(enablecheckbox):
        zd.s.click_and_wait(enablecheckbox)
    zd.s.click_and_wait(zd.info['loc_cfg_system_alarm_apply_button'])
    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())  
#######@zj20140522 optimization setting email alarm

def test_alarm_settings(zd, pause = 5.0):
    #@author: Jane.Guo @since: 2013-9 adapt to 9.8 move alarm email to system page
    nav_to(zd)
    xlocs = LOCATORS_CFG_ALARM_SETTINGS
    zd.s.click_and_wait(xlocs['test_button'])
    time.sleep(pause)
    result = zd.s.get_text(xlocs['msg_notify_text'])
    logging.info("Test alarm setting return message: %s" % result)
    if result == xlocs['msg_notify_success']: 
        return True
    else: 
        return False
    
def verify_alarm_mails_on_server(zd, mail_server, mail_to, mail_folder = '/home/lab/Maildir/new/', is_test_mail = False, time_out = 300):
    xlocs = LOCATORS_CFG_ALARM_SETTINGS
    mail_from = '%s@%s' % (zd.get_system_name(), zd.ip_addr)
    if is_test_mail:
        title = xlocs['test_alarm_title']
        message = xlocs['test_alarm_message']
        alarms_info_list = [[mail_from, mail_to, title, message]]
    
    else:
        alarms_list = zd.get_alarms()
        alarms_info_list = [[mail_from, mail_to, i[1], i[3]] for i in alarms_list]
        logging.info("All alarms in ZD are:\n%s" % alarms_info_list)
    
    time.sleep(60)
    stime = time.time()
    while True:
        logging.info('Read mails from mail server')
        alarms_mail_list = mail_server.read_postfix_mails(mail_folder)
        logging.info("All alarm mails in server are:\n%s" % alarms_mail_list)
        
        logging.info('Check if ZD sent out appropriate alarm mail or not')
        all_in = True
        for alarm_info in alarms_info_list:
            if alarm_info not in alarms_mail_list:
                all_in = False
                logging.info('Server did not receive the alarm mail from ZD about alarm [%s]' % alarm_info[3])
                break
        
        if not all_in:
            etime = time.time()
            if etime - stime > time_out:
                return (False, 'Server did not receive the alarm mail from ZD about alarm [%s] during [%d] seconds' % (alarm_info[3], time_out + 60))
            
            logging.info("Sleep 30 seconds.")
            time.sleep(30)
            mail_server.re_init()
        
        else:
            return (True, 'Server received all alarm mails from ZD')

#check alarm msg in mailbox or not
def check_alarm_mails_on_server(mail_server, msg, mail_folder = '/home/lab/Maildir/new/', is_test_mail = False, time_out = 300):
    
    time.sleep(60)
    stime = time.time()
    while True:
        logging.info('Read mails from mail server')
        alarms_mail_list = mail_server.read_postfix_mails(mail_folder)
        logging.info("All alarm mails in server are:\n%s" % alarms_mail_list)
        
        logging.info('Check if expected msg in mailbox')
        msg_in = False
        for alarm_info in alarms_mail_list:
            alarm=alarm_info[3]
            if not type(msg)==list:
                if msg in alarm:
                    msg_in = True
                    logging.info('Server receive the alarm mail from ZD about alarm [%s]' % msg)
                    break
            elif type(msg)==list:
                msg_in = True
                for s in msg:
                    if not msg in alarm:
                        msg_in = False
                        logging.info('str [%s] not in alarm' % msg)
                        break
                    logging.info('Server receive the alarm mail from ZD about alarm [%s]' % msg)
        
        if not msg_in:
            etime = time.time()
            if etime - stime > time_out:
                return (False, 'Server did not receive the alarm mail from ZD about alarm [%s] during [%d] seconds' % (msg, time_out + 60))
            
            logging.info("Sleep 30 seconds.")
            time.sleep(30)
            mail_server.re_init()
        
        else:
            return (True, 'Server received expected alarm mail from ZD')
        
        
