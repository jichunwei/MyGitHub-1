# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library include the functions relate to zd admin privilage level verify
"""

import logging
import time
import os
import re
    

from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.components.lib.zd import active_clients_zd
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import control_zd
from RuckusAutoTest.components.lib.zd import wlan_zd  
from RuckusAutoTest.components.lib.zd import access_points_zd
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wlan_groups
from RuckusAutoTest.tests.zd.lib import test_methods_dpsk as dpsk
from RuckusAutoTest.components.lib.zd import access_control_zd as acl
from RuckusAutoTest.components.lib.zd import guest_access_zd as guest
from RuckusAutoTest.components.lib.zd import hotspot_services_zd as hotspot
from RuckusAutoTest.components.lib.zd import wips_zd as wips
from RuckusAutoTest.components.lib.zd import service_zd as service
from RuckusAutoTest.components.lib.zd import aaa_servers_zd as aaa
from RuckusAutoTest.common import lib_Constant as constant

new_wlan_cfg = {
        'ssid': "new_wlan_zd_operation_level",
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
save_to = constant.save_to
not_auth_alt_msg='You do not have authorization to perform this task'

def ping_ap(zd,ap_mac):
    logging.info("Open ping and trace route windows for AP[%s]" % ap_mac)
    lib.zd.aps.open_pingtool_by_mac_addr(zd, ap_mac)

    # verify ping command to AP 
    logging.info("Verify ping command to AP[%s]" % ap_mac)
    result = lib.zd.pt.perform_ping_test(zd)
    logging.info("Ping result: %s" % result)
    
    # close ping trace route windows
    logging.info("Close Ping & Trace Route window")
    lib.zd.pt.close_ping_traceroute_windows(zd)
    return result

def go_to_blocked_clients(zd,level):
    return active_clients_zd.go_to_blocked_clients_from_monitor_page(zd,level)

def delete_all_dpsk(zd,level):
    zd.login()
    zd.navigate_to(zd.MONITOR, zd.MONITOR_GENERATED_PSK_CERTS, 2)
    
    total_generated_psk = zd._get_total_number(zd.info['loc_mon_total_generated_psk_span'],
                                                         "Generated Dynamic-PSKs")
    total_generated_psk = int(total_generated_psk)
    if total_generated_psk==0:
        raise Exception('no dpsk exist in zd')
    
    if level == 'monitor' or level == 'operator': 
#        if not _remove_all_psks_button_disabled(zd):
#            msg = 'operator or monitor user,delete all dpsk button not disabled'
#            logging.error(msg)
#            return False
        
        if not _remove_all_generated_psks_not_allowed(zd):
            msg = 'operator or monitor user,remove psk is allowed'
            logging.error(msg)
            return False
        
        psk_num = zd._get_total_number(zd.info['loc_mon_total_generated_psk_span'],
                                                         "Generated Dynamic-PSKs")
        psk_num = int(psk_num)
        
        if not psk_num==total_generated_psk:
            msg = 'operator or monitor user,remove psk successfully'
            logging.error(msg)
            return False
        msg = 'monitor or operator user,no permation to remove psk,correct behavior'
        logging.info(msg)
        return True
    
    else:
#        if _remove_all_psks_button_disabled(zd):
#            msg = 'super user,delete all dpsk button disabled'
#            logging.error(msg)
#            return False
#        
        if _remove_all_generated_psks_not_allowed(zd):
            msg = 'super user,remove psk is not allowed'
            logging.error(msg)
            return False
        
        psk_num = zd._get_total_number(zd.info['loc_mon_total_generated_psk_span'],
                                                         "Generated Dynamic-PSKs")
        psk_num = int(psk_num)
        
        if psk_num==total_generated_psk:
            msg = 'super user,not remove psk successfully'
            logging.error(msg)
            return False
        
        msg = 'super user,have permation to remove psk,correct behavior'
        logging.info(msg)
        return True

def delete_guest_pass(zd,level):
    zd.login()
    zd.navigate_to(zd.MONITOR, zd.MONITOR_GENERATED_GUESTPASSES)
    
    total_generated_guest = zd._get_total_number(zd.info['loc_mon_total_guestpasses_span'],
                                                         "Guestpass_Table")
    total_generated_guest = int(total_generated_guest)
    if total_generated_guest==0:
        raise Exception('no guest exist in zd')
    
    if level == 'monitor' or level == 'operator': 
#        if not _remove_all_guest_button_disabled(zd):
#            msg = 'operator or monitor user,delete all guest button not disabled'
#            logging.error(msg)
#            return False
        
        if not _remove_all_generated_guest_not_allowed(zd):
            msg = 'operator or monitor user,remove guest is allowed'
            logging.error(msg)
            return False
        
        guest_num = zd._get_total_number(zd.info['loc_mon_total_guestpasses_span'],
                                                         "Guestpass_Table")
        guest_num = int(guest_num)
        
        if not guest_num==total_generated_guest:
            msg = 'operator or monitor user,remove guest successfully'
            logging.error(msg)
            return False
        msg = 'monitor or operator user,no permation to remove guest,correct behavior'
        logging.info(msg)
        return True
    
    else:
#        if _remove_all_guest_button_disabled(zd):
#            msg = 'super user,delete all guest button disabled'
#            logging.error(msg)
#            return False
        
        if _remove_all_generated_guest_not_allowed(zd):
            msg = 'super user,remove guest is not allowed'
            logging.error(msg)
            return False
        
        guest_num = zd._get_total_number(zd.info['loc_mon_total_guestpasses_span'],
                                                         "Guestpass_Table")
        guest_num = int(guest_num)
        
        if guest_num==total_generated_guest:
            msg = 'super user,not remove guest successfully'
            logging.error(msg)
            return False
        
        msg = 'super user,have permation to remove guest,correct behavior'
        logging.info(msg)
        return True
    
def clear_all_events(zd,level):
    ###@zj 20140526 fix zf-8470
    zd.navigate_to(zd.MONITOR, zd.MONITOR_ALL_EVENTS_ACTIVITIES)
    
    alt_get = False
    total_events = zd._get_total_number(zd.info['loc_mon_allevents_total_number_span'], "Events/Activities")
    event_num = int(total_events)
    _clear_all_events(zd)
    if zd.s.is_alert_present():
        alt = zd.s.get_alert()
        logging.info('alert get %s'%alt)
        alt_get=True
    total_events = zd._get_total_number(zd.info['loc_mon_allevents_total_number_span'], "Events/Activities")
    event_num2 = int(total_events)
    
    if level == 'monitor' or level == 'operator':
        if not alt_get:
            msg = 'monitor or operator user,delete all events,not get alert'
            logging.error(msg)
            return False
        if event_num2<event_num:
            msg = 'monitor or operator user,delete some events(%s<%s)'%(event_num2,event_num)
            logging.error(msg)
            return False
        return True
    else:
        if alt_get:
            msg = 'super user,delete all events,get alert'
            logging.error(msg)
            return False
        return True
    
def change_real_time_monitor_status(zd,level):
    alt_get=False
    status = _real_time_monitor_started(zd)
    if status:
        _stop_real_time_monitor(zd)
    else:
        _start_real_time_monitor(zd)
        
    if zd.s.is_alert_present():
        alt = zd.s.get_alert()
        logging.info('alert get %s'%alt)
        alt_get=True
    zd.refresh()
    status2 = _real_time_monitor_started(zd)
    
    if level == 'monitor' or level == 'operator':
        if not alt_get:
            msg = 'monitor or operator user,change real time monitor status,not get alert'
            logging.error(msg)
            return False
        if status!=status2:
            msg = 'monitor or operator user,change real time monitor status successfully'
            logging.error(msg)
            return False
        return True
    else:
        if alt_get:
            msg = 'super user,change real time monitor status,get alert'
            logging.error(msg)
            return False
        if status==status2:
            msg = 'super user,change real time monitor status failed'
            logging.error(msg)
            return False
        return True
    
        

def change_language(zd,level):
    alt_get = False
    selection = r"//select[@id='locale']"
    zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)
    initial_vlaue=zd.s.get_selected_label(selection)
    logging.info('initial language is %s'%initial_vlaue)
    initial_vlaue = str(initial_vlaue)
    if initial_vlaue.startswith('German'):
        language = 'English'
    else:
        language = 'German'
    logging.info('try to set language as %s'%language)
    zd.s.select_option(selection,language)
    if zd.s.is_alert_present():
        alt = zd.s.get_alert()
        logging.info('alert get %s'%alt)
        alt_get=True
    
    zd.refresh()
    time.sleep(2)
    value_get=zd.s.get_selected_label(selection)
    value_get=str(value_get)
    
    if level == 'monitor' or level == 'operator':
        if not alt_get:
            msg = 'monitor or operator user,change language,not get alert'
            logging.error(msg)
            return False
        if initial_vlaue!=value_get:
            msg = 'monitor or operator user,change language from %s to %s'%(initial_vlaue,value_get)
            logging.error(msg)
            return False
        return True
    else:
        if alt_get:
            msg = 'super user,change language,get alert'
            logging.error(msg)
            return False
        if initial_vlaue==value_get:
            msg = 'super user,change language failed'
            logging.error(msg)
            return False
        msg = 'super user change language successfully'
        logging.info(msg)
        msg = 'change language back to initial value[%s]'%initial_vlaue
        logging.info(msg)
        zd.s.select_option(selection,initial_vlaue)
        return True

def set_session_time_out(zd,level):
    alt_get = False
    time_out_get = zd.get_session_timeout()
    msg='get zd session timeout %s'%time_out_get
    
    logging.info(msg)
    if time_out_get==1440:
        timeout=1
    else:
        timeout = time_out_get+1
    zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)
    _set_session_time_out(zd,timeout)    
    
    
    if zd.s.is_alert_present():
        alt = zd.s.get_alert()
        logging.info('alert get %s'%alt)
        alt_get=True
    
    zd.refresh()
    time.sleep(2)
    time_out_get2 = zd.get_session_timeout()
    
    if level == 'monitor' or level == 'operator':
        if not alt_get:
            msg = 'monitor or operator user,set session timeout,not get alert'
            logging.error(msg)
            return False
        if time_out_get!=time_out_get2:
            msg = 'monitor or operator user,set session timeout from %s to %s'%(time_out_get,time_out_get2)
            logging.error(msg)
            return False
        return True
    else:
        if alt_get:
            msg = 'super user,set session timeout,get alert'
            logging.error(msg)
            return False
        if time_out_get==time_out_get2:
            msg = 'super user,set session timeout failed'
            logging.error(msg)
            return False
        msg = 'super user set session timeout successfully'
        logging.info(msg)
        return True


def backup_cfg(zd):
    save_path = lib.zd.bkrs.backup(zd, save_to = save_to)
    if save_path is not None:
        return True
    else:
        return False


def set_remot_trouble_shooting(zd,level):
    alt_get=False
    log_checkbox = r"//input[@id='remote-access']"
    apply_button = r"//input[@id='apply-remote-access']"
    zd.navigate_to(zd.ADMIN, zd.ADMIN_DIAGNOSTIC)
    elabled = _log_enabled(zd,log_checkbox)
    _change_log_level(zd,log_checkbox,apply_button)

    if zd.s.is_alert_present():
        alt = zd.s.get_alert()
        logging.info('alert get %s'%alt)
        alt_get=True
        
    elabled2 = _log_enabled(zd,log_checkbox)
    
    if level == 'monitor' or level == 'operator':
        if not alt_get:
            msg = 'monitor or operator user,set remote trouble shouting,not get alert'
            logging.error(msg)
            return False
        if elabled!=elabled2:
            msg = 'monitor or operator user,set remote trouble shouting seccessfully'
            logging.error(msg)
            return False
        return True
    else:
        if alt_get:
            msg = 'super user,set remote trouble shouting,get alert'
            logging.error(msg)
            return False
        if elabled2==elabled:
            msg = 'super user,set set remote trouble shouting failed'
            logging.error(msg)
            return False
        msg = 'super user set set remote trouble shoutingsuccessfully'
        logging.info(msg)
        return True



def set_debug_log_level(zd,level):
    alt_get=False
    log_checkbox = r"//input[@id='system-mgmt']"
    apply_button = r"//input[@id='apply-log']"
    zd.navigate_to(zd.ADMIN, zd.ADMIN_DIAGNOSTIC)
    log_elabled = _log_enabled(zd,log_checkbox)
    _change_log_level(zd,log_checkbox,apply_button)

    if zd.s.is_alert_present():
        alt = zd.s.get_alert()
        logging.info('alert get %s'%alt)
        alt_get=True
        
    log_elabled2 = _log_enabled(zd,log_checkbox)
    
    if level == 'monitor' or level == 'operator':
        if not alt_get:
            msg = 'monitor or operator user,set debug log,not get alert'
            logging.error(msg)
            return False
        if log_elabled!=log_elabled2:
            msg = 'monitor or operator user,set debug log seccessfully'
            logging.error(msg)
            return False
        return True
    else:
        if alt_get:
            msg = 'super user,set debug log,get alert'
            logging.error(msg)
            return False
        if log_elabled2==log_elabled:
            msg = 'super user,set debug log failed'
            logging.error(msg)
            return False
        msg = 'super user set debug log successfully'
        logging.info(msg)
        return True

def save_debug_info(zd):
    button = r"//input[@value='Save Debug Info']"
    zd.navigate_to(zd.ADMIN, zd.ADMIN_DIAGNOSTIC)
    save_path = control_zd.download_single_file(zd, button, filename_re = '.+.dbg', save_to=save_to)
    if save_path is not None:
        return True
    else:
        return False

def save_sys_log(zd):
    button = r"//input[@value='Save System Log']"
    zd.navigate_to(zd.ADMIN, zd.ADMIN_DIAGNOSTIC)
    save_path = control_zd.download_single_file(zd, button, filename_re = '.+.tar', save_to=save_to)
    if save_path is not None:
        return True
    else:
        return False

def download_registration_file(zd):
    button = zd.info['registration_apply']
    zd.navigate_to(zd.ADMIN, zd.ADMIN_REG)
    _input_reg_info(zd)
    save_path = control_zd.download_single_file(zd, button, filename_re = '.+.csv', save_to=save_to)
    if save_path is not None:
        return True
    else:
        return False

def system_name_cfg(zd,level):
    alt_get=False
    name = zd._get_system_name()
    system_name = name+'1'
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM, 2)
    
    logging.info("Set the system name to '%s'" % system_name)
    zd.s.type(zd.info['loc_cfg_system_name_textbox'], system_name)
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(zd.info['loc_cfg_system_name_apply_button'])
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
        
    zd.refresh()    
    name2 = zd._get_system_name()
    result,msg= _alert_behavior_correct(alt_get,level,'set system name')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(name,name2,level,'set system name')
    if not result:
        logging.error(msg)
        return result
    return True

def create_wlan(zd,level,wlan_conf=new_wlan_cfg):
    alt_get=False
    xlocs = wlan_zd.LOCATORS_CFG_WLANS
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    total_wlans = int(_get_total_number(zd, xlocs['total_wlans_span'], 'WLAN'))
    wlan_zd.create_wlan(zd,wlan_conf,get_alert=False)
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True

    total_wlans2 = int(_get_total_number(zd, xlocs['total_wlans_span'], 'WLAN'))
    
    result,msg= _alert_behavior_correct(alt_get,level,'create wlan')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(total_wlans,total_wlans2,level,'create wlan')
    if not result:
        logging.error(msg)
        return result
    return True

def edit_wlan(zd,level,ssid,new_wlan_conf):
    alt_get=False
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    xlocs = wlan_zd.LOCATORS_CFG_WLANS
    new_ssid = new_wlan_conf['ssid']
    zd._fill_search_txt(xlocs['wlan_search_textbox'], new_ssid, is_refresh = False)
    new_edit_button = xlocs['edit_wlan'] % new_ssid
    if zd.s.is_element_present(new_edit_button):
        raise Exception('target wlan exist in zd')
    
    wlan_zd.edit_wlan(zd, ssid, new_wlan_conf,get_alert=False,clear_search_box = False)
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    
    zd._fill_search_txt(xlocs['wlan_search_textbox'], new_ssid, is_refresh = False)
    new_edit_button = xlocs['edit_wlan'] % new_ssid
    wlan_exist = zd.s.is_element_present(new_edit_button)
    
    result,msg= _alert_behavior_correct(alt_get,level,'edit wlan')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,wlan_exist,level,'edit wlan')
    if not result:
        logging.error(msg)
        return result
    return True

def del_wlan(zd,level,ssid):
    alt_get=False
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    xlocs = wlan_zd.LOCATORS_CFG_WLANS
    zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = False)
    edit_button = xlocs['edit_wlan'] % ssid
    if not zd.s.is_element_present(edit_button):
        raise Exception('wlan not exist in zd')
    try:
        wlan_zd.del_wlan(zd, ssid)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt = e.message
            msg = 'alert get %s'%alt
            logging.info(msg)
            alt_get=True
    
    zd._fill_search_txt(xlocs['wlan_search_textbox'], ssid, is_refresh = False)
    edit_button = xlocs['edit_wlan'] % ssid
    wlan_exist = zd.s.is_element_present(edit_button)
    
    result,msg= _alert_behavior_correct(alt_get,level,'del wlan')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(True,wlan_exist,level,'del wlan')
    if not result:
        logging.error(msg)
        return result
    return True

def add_wlan_grp(zd,level,wlan_grp_name):
    alt_get = False
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    xloc = wlan_groups.LOCATORS_CFG_WLANGROUPS
    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_grp_name)
    wlan_groups._nav_to_cfg(zd)
    if zd.s.is_element_present(loc_edit_wg_by_name):
        raise Exception('wlan group exist before add')
    
    wlan_groups.create_wlan_group(zd,wlan_grp_name,'')
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    
    wlan_groups._nav_to_cfg(zd)
    wlan_grp_exist = zd.s.is_element_present(loc_edit_wg_by_name)
    
    result,msg= _alert_behavior_correct(alt_get,level,'add wlangrp')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,wlan_grp_exist,level,'add wlangrp')
    if not result:
        logging.error(msg)
        return result
    return True

def edit_wlan_grp(zd,level,grp_name,new_name):
    alt_get = False
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    xloc = wlan_groups.LOCATORS_CFG_WLANGROUPS
    loc_edit_wg_by_name = xloc['doEdit'] % (new_name)
    wlan_groups._nav_to_cfg(zd)
    if zd.s.is_element_present(loc_edit_wg_by_name):
        raise Exception('target wlan group exist before edit')
    try:
        wlan_groups.edit_wlan_group(zd,grp_name,new_name)
    except Exception,e:
        if 'You do not have authorization to perform this task' in e.message:
            alt_get = True
    
    wlan_groups._nav_to_cfg(zd)
    wlan_grp_exist=zd.s.is_element_present(loc_edit_wg_by_name)
    result,msg= _alert_behavior_correct(alt_get,level,'edit wlangrp')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,wlan_grp_exist,level,'edit wlangrp')
    if not result:
        logging.error(msg)
        return result
    return True
    
def del_wlan_grp(zd,level,name):
    alt_get = False
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    xloc = wlan_groups.LOCATORS_CFG_WLANGROUPS
    loc_edit_wg_by_name = xloc['doEdit'] % (name)
    wlan_groups._nav_to_cfg(zd)
    if not zd.s.is_element_present(loc_edit_wg_by_name):
        raise Exception('wlan group not exist')
    
    wlan_groups.del_wlan_group(zd,name)
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
        
    wlan_groups._nav_to_cfg(zd)
    wlan_grp_exist = zd.s.is_element_present(loc_edit_wg_by_name)
        
    result,msg= _alert_behavior_correct(alt_get,level,'del wlangrp')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(True,wlan_grp_exist,level,'del wlangrp')
    if not result:
        logging.error(msg)
        return result
    return True

def set_auto_del_expired_dpsk(zd,level):
    alt_get = False
    status = wlan_zd.auto_del_expire_dpsk_enabled(zd)
    if status:
        wlan_zd.disable_auto_del_expire_dpsk(zd)
    else:
        wlan_zd.enable_auto_del_expire_dpsk(zd)
    
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    status2 = wlan_zd.auto_del_expire_dpsk_enabled(zd)   

    result,msg= _alert_behavior_correct(alt_get,level,'edit auto_del_expired_dpsk ')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(status,status2,level,'edit auto_del_expired_dpsk')
    if not result:
        logging.error(msg)
        return result
    return True

def generate_multiple_dpsk(zd,level):
    alt_get = False
    number = dpsk._get_num_of_psks(zd)
    try:
        wlan_zd.generate_multiple_dpsk(zd,{'number_of_dpsk':5})
    except Exception,e:
        if 'You do not have authorization to perform this task' in e.message:
            alt_get= True
    number2 = dpsk._get_num_of_psks(zd)
    
    result,msg= _alert_behavior_correct(alt_get,level,'generate dpsk')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(number,number2,level,'generate dpsk')
    if not result:
        logging.error(msg)
        return result
    return True

def set_zeroit_auth_server(zd,level,server=''):
    alt_get = False
    server_before = wlan_zd.get_zeroit_auth_server(zd)
    if server_before==server:
        raise Exception('server name already the same to target name')
    
    wlan_zd.set_zeroit_auth_server(zd,server)
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    server_after = wlan_zd.get_zeroit_auth_server(zd)
    
    result,msg= _alert_behavior_correct(alt_get,level,'set zeroit auth server')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(server_before,server_after,level,'set zeroit auth server')
    if not result:
        logging.error(msg)
        return result
    return True

def change_limit_zd_discovery_status(zd,level):
    alt_get=False
    enable_cfg = dict(
        enabled = True,
        keep_ap_setting = True,
    )
    disable_cfg = dict(
        enabled = False,
    )
    status = _limited_zd_discovery_enabled(zd)
    try:
        if status:
            _cfg_limit_zd_discovery(zd,disable_cfg)
        else:
            _cfg_limit_zd_discovery(zd,enable_cfg)
    except Exception,e:
        logging.info('exception catch when set limited zd discovery[%s]'%e.message)
        if 'You do not have authorization to perform this task' in e.message:
            alt_get = True
    status2 = _limited_zd_discovery_enabled(zd)
    
    result,msg= _alert_behavior_correct(alt_get,level,'set limited zd discovery')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(status,status2,level,'set limited zd discovery')
    if not result:
        logging.error(msg)
        return result
    return True

def set_ap_channelization(zd,ap_mac,radio='na'):
    status = _ap_channelizadtion_override_group_cfg(zd,ap_mac,radio)
    logging.info('status at the begining is %s'%status)
    try:
        _set_ap_channelization(zd,ap_mac,radio)
    except Exception,e:
        logging.error('exception met %s'%e.message)
    status2= _ap_channelizadtion_override_group_cfg(zd,ap_mac,radio)
    logging.info('status after set is %s'%status2)
    if status2:
        _disable_ap_channelization_override(zd,ap_mac,radio)
    
    result,msg= _compare_value_after_set(status,status2,'super','set ap channelization')
    if not result:
        logging.error(msg)
        return result
    return True


def create_l2_acl(zd,level,acl_cfg,pause = 1):
    xlocs = acl.LOCATORS_CFG_ACCESS_CONTROL
    alt_get=False
    name= acl_cfg['acl_name']
    edit_button =  xlocs['edit_l2acl'] % name
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036                   
    if zd.s.is_element_present(edit_button):
        raise Exception('acl exist before create')
    try:
        acl.create_l2_acl_policy(zd,acl_cfg)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036                   
    time.sleep(pause)
    status = zd.s.is_element_present(edit_button)
    
    result,msg= _alert_behavior_correct(alt_get,level,'create l2 acl')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,status,level,'create l2 acl')
    if not result:
        logging.error(msg)
        return result
    
    return True

def edit_l2_acl(zd,level,acl_name,new_conf,pause = 1):
    xlocs = acl.LOCATORS_CFG_ACCESS_CONTROL
    alt_get=False
    name= new_conf['acl_name']
    edit_button =  xlocs['edit_l2acl'] % name
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036                   
    if zd.s.is_element_present(edit_button):
        raise Exception('target acl exist before edit')
    
    try:
        acl.edit_l2_acl_policy(zd, acl_name, new_conf)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036    
    status = zd.s.is_element_present(edit_button)
    
    result,msg= _alert_behavior_correct(alt_get,level,'edit l2 acl')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,status,level,'edit l2 acl')
    if not result:
        logging.error(msg)
        return result
       
    return True     


def del_l2_acl(zd,level,acl_name,pause = 1):
    xlocs = acl.LOCATORS_CFG_ACCESS_CONTROL
    alt_get=False
    name= acl_name
    edit_button =  xlocs['edit_l2acl'] % name
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036        
    time.sleep(pause)
    if not zd.s.is_element_present(edit_button):
        raise Exception('acl not exist before del')
    
    try:
        acl.delete_l2_acl_policy(zd, acl_name)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036   
    status = zd.s.is_element_present(edit_button)
    
    result,msg= _alert_behavior_correct(alt_get,level,'del l2 acl')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(True,status,level,'del l2 acl')
    if not result:
        logging.error(msg)
        return result
    return True    

user_test='pri_user_add' 
password_test='pri_user_add'
def create_user(zd,level,username=user_test, password=password_test):
    alt_get=False
    number=zd.get_number_users()
    try:
        zd.create_user(username,password)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    number2=zd.get_number_users()
    
    result,msg= _alert_behavior_correct(alt_get,level,'create user')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(number,number2,level,'create user')
    if not result:
        logging.error(msg)
        return result
    return True     

user_to_edit = 'pri_user_edit'
def edit_user(zd,level,user_name,new_user_name=user_to_edit):
    alt_get=False
    try:
        zd.edit_user(user_name,new_user_name)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    user_exist = _user_exist_in_zd(zd,new_user_name)
    
    result,msg= _alert_behavior_correct(alt_get,level,'edit user')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,user_exist,level,'edit user')
    if not result:
        logging.error(msg)
        return result
    return True  

def del_user(zd,level,user_name):
    alt_get=False
    try:
        zd.delete_user(user_name)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    user_exist = _user_exist_in_zd(zd,user_name)
    
    result,msg= _alert_behavior_correct(alt_get,level,'delet user')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(True,user_exist,level,'edit user')
    if not result:
        logging.error(msg)
        return result
    return True  

role_name_add = 'role_pri_add'
def create_role(zd,level,role_name=role_name_add):
    alt_get=False
    try:
        _cfg={'rolename':role_name}
        zd.create_role(**_cfg)
    except Exception,e:
        logging.info('alert get %s'%e.message)
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    result,msg= _alert_behavior_correct(alt_get,level,'create role')
    if not result:
        logging.error(msg)
        return result
    
    return True     

role_name_edit = 'role_pri_edit'
def edit_role(zd,level,role_name,new_role_name=role_name_edit):
    alt_get=False
    try:
        zd.edit_role(role_name,new_role_name)
    except Exception,e:
        logging.info('alert get %s'%e.message)
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    result,msg= _alert_behavior_correct(alt_get,level,'edit role')
    if not result:
        logging.error(msg)
        return result
    
    return True     
    
def delete_role(zd,level,role_name):
    alt_get=False
    try:
        zd._delete_role(role_name)
    except Exception,e:
        logging.info('alert get %s'%e.message)
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    result,msg= _alert_behavior_correct(alt_get,level,'delete role')
    if not result:
        logging.error(msg)
        return result
    
    return True     


def select_guest_auth_server(zd, level ,server):
    # select authentication server option
    alt_get = False
    current_server = _get_guest_auth_server(zd)
    if current_server==server:
        raise Exception ('current server is the same to target one')
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)
    info = guest.info
    zd.s.select_option(info['auth_server_option'], server)
    zd.s.click_and_wait(info['guestpass_apply_button'])
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    server_after = _get_guest_auth_server(zd)
    
    result,msg= _alert_behavior_correct(alt_get,level,'set guest auth server')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(current_server,server_after,level,'set guest auth server')
    if not result:
        logging.error(msg)
        return result
    return True


hotspot_test_cfg_add={'name':'hot_spot_test_privilage_add',
                  'login_page':'http://192.168.0.252',
                  }
def create_hotspot_cfg(zd,level,hotspot_cfg=hotspot_test_cfg_add):
    alt_get=False
    try:
        hotspot.create_profile(zd, **hotspot_cfg)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    result,msg= _alert_behavior_correct(alt_get,level,'create role')
    if not result:
        logging.error(msg)
        return result
    
    return True


hotspot_test_cfg_edit={'name':'hot_spot_test_privilage_edit',
                  'login_page':'http://192.168.0.252',
                  }
def edit_hotspot_cfg(zd,level,old_name,hotspot_cfg=hotspot_test_cfg_edit):
    alt_get=False
    try:
        hotspot.cfg_profile(zd, old_name, **hotspot_cfg)
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get=True
    
    result,msg= _alert_behavior_correct(alt_get,level,'edit role')
    if not result:
        logging.error(msg)
        return result
    
    return True
    
def del_hotspot_cfg(zd,level,old_name):
    alt_get=False
    hotspot.del_profile(zd, old_name)
    if zd.s.is_alert_present(5):
        alt_msg=zd.s.get_alert()
        alt_get=True
        logging.info('alert get [%s]'%alt_msg)
        
    result,msg= _alert_behavior_correct(alt_get,level,'del role')
    if not result:
        logging.error(msg)
        return result
    
    return True

def change_rogue_dhcp_detection_status(zd,level):
    alt_get=False
    status = wips.get_dhcp_server_dection_status(zd)
    if status:
        wips.disable_rogue_dhcp_server_detection(zd)
    else:
        wips.enable_rogue_dhcp_server_detection(zd)
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    status2 = wips.get_dhcp_server_dection_status(zd)

    result,msg= _alert_behavior_correct(alt_get,level,'change rogue dhcp detection status')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(status,status2,level,'change rogue dhcp detection status')
    if not result:
        logging.error(msg)
        return result
    return True


def change_background_scan_status(zd,level):
    alt_get=False
    status=service.background_scan_2_4G_enabled(zd)
    if status:
        service.set_2_4_G_background_scan_options(zd,None)
    else:
        service.set_2_4_G_background_scan_options(zd,20)
    
    if zd.s.is_alert_present(5):
        alt = zd.s.get_alert()
        msg = 'alert get %s'%alt
        logging.info(msg)
        alt_get=True
    status2=service.background_scan_2_4G_enabled(zd)   

    result,msg= _alert_behavior_correct(alt_get,level,'set background scan')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(status,status2,level,'set background scan')
    if not result:
        logging.error(msg)
        return result
    return True

def change_email_alarm_status(zd,level,email_addr='eee@www.com', mail_server_addr='192.168.0.252'):
#######@zj20140522 optimization zonedirector asz for email alarm beharior change zf-8437
    alt_get1 =""
    alt_get2 =""
    alt_get = False
    status=zd.alarm_email_enabled_check()
    logging.info('before setting,status is %s'%status)
    try:
        if status:
            msg = 'email alarm enabled,try to disable it'
            logging.info(msg)
            alt_get1,alt_get2 = zd.disable_alarm_email()
        else:
            msg = 'email alarm disabled,try to enable it'
            logging.info(msg)
            alt_get1,alt_get2 = zd.set_alarm_email(email_addr, mail_server_addr)
    except Exception,e:
        msg = e.message
#        if not_auth_alt_msg in e.message:
#            alt_get=True

    if not_auth_alt_msg in alt_get1 and not_auth_alt_msg in alt_get2:
        alt_get = True
    elif not_auth_alt_msg not in alt_get1 and not_auth_alt_msg not in alt_get2:
        alt_get = False
    else:
        msg='get wrong alt,set emailalarm syscfg: %s; set emailalarm settings: %s' % (alt_get1,alt_get2)
        logging.info(msg)
        return False,msg
         
    status2=zd.alarm_email_enabled_check()
#######@zj20140522 optimization zonedirector asz  for email alarm beharior change     
    
    logging.info('after setting,status is %s'%status2)
    
    result,msg= _alert_behavior_correct(alt_get,level,'change email alarm status')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(status,status2,level,'change email alarm status')
    if not result:
        logging.error(msg)
        return result
#zj 20140422 ZF-7694. fix failed when return ,  "TypeError: 'bool' object is not iterable"  
    return True,msg

test_aaa_cfg={'server_type':'ad',
              'server_name':'aaa_ad_for_test_add',
              'server_addr':'192.168.0.252',
              'server_port':'389'
              }
def create_aaa_server(zd,level,server_cfg=test_aaa_cfg):
    alt_get = False
    try:
        msg = aaa.create_server_2(zd, server_cfg)
        if msg and (not_auth_alt_msg in msg):
            alt_get = True
            logging.info('alert get when create aaa server')
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get = True
            logging.info('alert get when create aaa server')
        
    status = _aaa_server_exist(zd,server_cfg['server_name'])
    
    result,msg= _alert_behavior_correct(alt_get,level,'create aaa server')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,status,level,'create aaa server')
    if not result:
        logging.error(msg)
        return result
    
    return True

new_aaa_name_edit = 'aaa_pri_test_edit'
new_server_type ='ad'
def edit_aaa_server(zd,level,old_name,new_name=new_aaa_name_edit,new_type=new_server_type):
    alt_get = False
    try:
        msg = aaa.edit_server(zd, old_name , {'server_name':new_name,'server_type':new_type})
        if msg and (not_auth_alt_msg in msg):
            alt_get = True
            logging.info('alert get when edit aaa server')
    except Exception,e:
        if not_auth_alt_msg in e.message:
            alt_get = True
            logging.info('alert get when create aaa server')
    status = _aaa_server_exist(zd,new_name)
    
    result,msg= _alert_behavior_correct(alt_get,level,'create aaa server')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(False,status,level,'create aaa server')
    if not result:
        logging.error(msg)
        return result
    
    return True
    
def del_aaa_server(zd,level,name):
    alt_get = False
    aaa.del_server(zd, name)
    if zd.s.is_alert_present(5):
        alt_msg=zd.s.get_alert()
        alt_get=True
        logging.info('alert get [%s]'%alt_msg)
        
    status = _aaa_server_exist(zd,name)
    
    result,msg= _alert_behavior_correct(alt_get,level,'delete aaa server')
    if not result:
        logging.error(msg)
        return result
    
    result,msg= _compare_value_after_set(True,status,level,'delete aaa server')
    if not result:
        logging.error(msg)
        return result
    
    return True
    
    
        
def _aaa_server_exist(zd,server_name):
    locs=aaa.locs
    tbl_id = aaa.tbl_id
    
    wgt._fill_search_txt(
        zd.s, locs['aaa_tbl_filter_txt'] % tbl_id['aaa_server'], server_name
    )

    if zd.s.is_element_present(locs['aaa_edit_btn']):
        return True
    else:
        return False
    
def _get_guest_auth_server(zd):
    info = guest.info
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)

    newval = zd.s.get_selected_option(info['auth_server_option'])
    return newval


def _user_exist_in_zd(zd,user_name):
    zd._fill_search_txt(zd.info['loc_cfg_user_search_textbox'], user_name)
    
    user_total = zd._get_total_number(zd.info['loc_cfg_user_total_number_span'], "Users")
    if int(user_total)==1:
        user_exist=True
    elif int(user_total)==0:
        user_exist=False
    else:
        raise Exception('user number unexpected %s(%s)'%(user_total,user_name))
    return user_exist
    

def _ap_channelizadtion_override_group_cfg(zd,ap_mac,radio='na'):
    loc = access_points_zd.LOCATORS_CFG_ACCESSPOINTS
    check_box=loc['check_channelization']%radio
    access_points_zd._nav_to(zd)
    access_points_zd._open_ap_dialog_by_mac(zd, ap_mac)
    
    if zd.s.is_checked(check_box):
        res = True
    else:
        res = False
    access_points_zd._cancel_and_close_ap_dialog(zd)
    return res


def _set_ap_channelization(zd,mac_addr,radio='na'):
    '''
    radio=ng/na/bg
    '''
    loc = access_points_zd.LOCATORS_CFG_ACCESSPOINTS
    check_box=loc['check_channelization']%radio
    access_points_zd._nav_to(zd)
    access_points_zd._open_ap_dialog_by_mac(zd, mac_addr)
    
    zd.s.click_and_wait(check_box)
    
    access_points_zd._save_and_close_ap_dialog(zd)


def _disable_ap_channelization_override(zd,mac_addr,radio='na'):
    '''
    radio=ng/na/bg
    '''
    loc = access_points_zd.LOCATORS_CFG_ACCESSPOINTS
    check_box=loc['check_channelization']%radio
    access_points_zd._nav_to(zd)
    access_points_zd._open_ap_dialog_by_mac(zd, mac_addr)
    
    zd.s.click_if_checked(check_box)
    
    access_points_zd._save_and_close_ap_dialog(zd)

    
def _alert_behavior_correct(alt_get,level,action,single_ap_only=False):
    if level=='monitor' or level=='operator':
        if not alt_get:
            msg='operator or monitor user not get alert when %s-wrong behavior'%action
            logging.error(msg)
            return False,msg
        else:
            msg='operator or monitor user get alert when %s-correct behavior'%action
            logging.info(msg)
            return True,msg
    else:
        if alt_get:
            msg='super user get alert when %s-wrong behavior'%action
            logging.error(msg)
            return False,msg
        else:
            msg='super user not alert when %s-correct behavior'%action
            logging.info(msg)
            return True,msg


def _compare_value_after_set(value_before,value_after,level,action,single_ap_only=False):
    same_value=(value_before==value_after)
    if level=='monitor' or level=='operator':
        if not same_value:
            msg='operator or monitor user %s success-wrong behavior'%action
            logging.error(msg)
            return False,msg
        else:
            msg='operator or monitor user %s failed-correct behavior'%action
            logging.info(msg)
            return True,msg
    else:
        if same_value:
            msg='super user %s failed-wrong behavior'%action
            logging.error(msg)
            return False,msg
        else:
            msg='super user %s success-correct behavior'%action
            logging.info(msg)
            return True,msg
            

def _input_reg_info(zd,info={}):
    conf = {'name':'1',
            'email':'2',
            'phone':'3',
            'cmp_name':'4',
            'cmp_addr':'5'}
    conf.update(info)
    name_textbox = zd.info['registration_name']
    emali_textbox = zd.info['registration_email']
    phone_textbox = zd.info['registration_phone']
    cmp_name_textbox = zd.info['registration_cmp_name']
    cmp_addr_textbox = zd.info['registration_cmp_addr']
    
    s=zd.s
    s.type_text(name_textbox,conf['name'])
    s.type_text(emali_textbox,conf['email'])
    s.type_text(phone_textbox,conf['phone'])
    s.type_text(cmp_name_textbox,conf['cmp_name'])
    s.type_text(cmp_addr_textbox,conf['cmp_addr'])

#
#def _remove_all_psks_button_disabled(zd):
#    if not zd.s.is_element_present(zd.info['loc_mon_generated_psk_delall_button']):
#        return True
#    
#    if zd.s.is_element_disabled(zd.info['loc_mon_generated_psk_delall_button']):
#        return True
#    
#    return False
#            
def _remove_all_generated_psks_not_allowed(zd):
    try:
        zd._delete_element(zd.info['loc_mon_generated_psk_all_checkbox'],
                             zd.info['loc_mon_generated_psk_delete_button'], "Dynamic-PSKs")
    except Exception,e:
        logging.info('exception get:%s'%e.message)
        expected_alt = 'Your privilege is limited to monitoring and viewing operation status'
        msg = e.message
        if (expected_alt in msg) or (not_auth_alt_msg in msg):
            return True
    
    return False


#def _remove_all_guest_button_disabled(zd):
#    if not zd.s.is_element_present(zd.info['loc_mon_guestpass_guestdelall_button']):
#        return True
#    
#    if zd.s.is_element_disabled(zd.info['loc_mon_guestpass_guestdelall_button']):
#        return True
#    
#    return False
            
def _remove_all_generated_guest_not_allowed(zd):
    try:
        zd._delete_element(zd.info['loc_mon_guestpass_guestall_checkbox'],
                             zd.info['loc_mon_guestpass_guestdel_button'], "GuestPass")
    except Exception,e:
        logging.info('exception get:%s'%e.message)
        expected_alt = 'Your privilege is limited to monitoring and viewing operation status'
        msg = e.message
        if (expected_alt in msg) or (not_auth_alt_msg in msg):
            return True
    
    return False

def _clear_all_events(zd):
    ###@zj 20140526 fix zf-8470
#    zd.navigate_to(zd.MONITOR, zd.MONITOR_ALL_EVENTS_ACTIVITIES)

    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(zd.info['loc_mon_allevents_clear_all_button'])
    time.sleep(1)
    if zd.s.is_confirmation_present(5):
        logging.info(zd.s.get_confirmation())            


def _set_session_time_out(zd,timeout):
    zd.s.type_text(zd.info['loc_admin_preference_idle_timeout_textbox'],str(timeout))
    zd.s.click_and_wait(zd.info['loc_admin_preference_idle_timeout_apply_button'])
    if zd.s.is_confirmation_present(5):
        confirmation=zd.s.get_confirmation()
        logging.info("Got confirmation: %s" % confirmation)
        msg='set timeout %s successfully'%timeout 

def _real_time_monitor_started(zd):
    stop_button = zd.info['loc_mon_stop_monitoring_button']
    start_button = zd.info['loc_mon_start_monitoring_button']
    
    zd.login()
    zd.navigate_to(zd.MONITOR, zd.MONITOR_REAL_TIME)
    time.sleep(1)
    zd.refresh()
    time.sleep(1)
    
    if zd.s.is_element_present(stop_button):
        return True
    elif zd.s.is_element_present(start_button):
        return False
    raise Exception ('both stop and start button not exist,wrong status')

def _start_real_time_monitor(zd):
    start_button = zd.info['loc_mon_start_monitoring_button']
    zd.s.click_and_wait(start_button)
    
def _stop_real_time_monitor(zd):
    stop_button = zd.info['loc_mon_stop_monitoring_button']
    zd.s.click_and_wait(stop_button)


def _log_enabled(zd,check_box):
    zd.refresh()
    time.sleep(2)
    if zd.s.is_checked(check_box):
        return True
    else:
        return False
    
def _change_log_level(zd,check_box,apply_button):
    zd.s.click_and_wait(check_box)
    zd.s.click_and_wait(apply_button)

def _remote_trouble_shooting_enabled(zd,check_box):
    zd.refresh()
    time.sleep(2)
    if zd.s.is_checked(check_box):
        return True
    else:
        return False
    
def _change_remote_trouble_shooting_status(zd,check_box,apply_button):
    zd.s.click_and_wait(check_box)
    zd.s.click_and_wait(apply_button)



def _get_total_number(zd, locator, table_name):
    """
    """
    total = zd.s.get_text(locator)
    if not total:
        time.sleep(5)
        total = zd.s.get_text(locator)

    pat1 = ".*\(([0-9]+)\)$"
    match_obj1 = re.search(pat1, total)
    
    #if the current page include all the items, the total number will like this '1-3(3)'
    pat2 = "(\d+)-(\d+) \((\d+)\)"
    match_obj2 = re.search(pat2, total)
    
    if match_obj1:
        total = match_obj1.group(1)
    elif match_obj2:
        total = match_obj2.group(3)
    else:
        raise Exception("Can not get the total number of rows in %s table" % table_name)

    return total


def _cfg_limit_zd_discovery(zd,cfg):
    access_points_zd.cfg_limited_zd_discovery(zd,cfg)

def _limited_zd_discovery_enabled(zd, is_nav = True):
    '''
    '''
    xloc = access_points_zd.LOCATORS_CFG_ACCESSPOINTS
    if is_nav:
        access_points_zd._nav_to(zd)
        time.sleep(0.5)
    if zd.s.is_checked(xloc['check_zp_ip']):
        return True
    return False   


