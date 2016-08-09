import logging
import re
import time
import traceback

from RuckusAutoTest.components.lib.zd import control_zd as control_zd

LOCATORS_ADMIN_PREFERENCE  = {
    'loc_admin_preference_span':r"//span[@id='admin_pref']",

    'loc_admin_preference_auth_local_radio':r"//input[@id='auth-by-local']",
    'loc_admin_preference_auth_external_radio':r"//input[@id='auth-by-external']",
    'loc_admin_preference_auth_server_option':r"//select[@id='authsvr']",
    'loc_admin_preference_fallback_local_checkbox':r"//input[@id='fallback-local']",
    'loc_admin_preference_admin_name_textbox':r"//input[@id='admin-name']",
    'loc_admin_preference_admin_old_pass_textbox':r"//input[@id='admin-old-pass']",
    'loc_admin_preference_admin_pass1_textbox':r"//input[@id='admin-pass1']",
    'loc_admin_preference_admin_pass2_textbox':r"//input[@id='admin-pass2']",
    'loc_admin_preference_apply_button':r"//input[@id='apply-admin']",
    'loc_admin_preference_idle_timeout_textbox':r"//input[@id='idletime']",
    'loc_admin_preference_idle_timeout_apply_button':r"//input[@id='apply-idletime']",


}

xlocs = LOCATORS_ADMIN_PREFERENCE

def get_admin_cfg(zd):
    """
    """
    res={'auth_method':None,
         'auth_server':None,
         'fallback_local':None,
         'admin_name':None
         }
    zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)
    if zd.s.is_checked(xlocs['loc_admin_preference_auth_local_radio']):
        res['auth_method']='local'
    elif zd.s.is_checked(xlocs['loc_admin_preference_auth_external_radio']):
        res['auth_method']='external'
    else:
        raise 'can not auth method'
    
    if res['auth_method']=='external':
        res['auth_server']=str(zd.s.get_selected_label(xlocs['loc_admin_preference_auth_server_option']))
        if zd.s.is_checked(xlocs['loc_admin_preference_fallback_local_checkbox']):
            res['fallback_local']=True
        else:
            res['fallback_local']=False
            
    if res['auth_method']=='local' or res['fallback_local']:
        res['admin_name']=zd.s.get_value(xlocs['loc_admin_preference_admin_name_textbox'])
    
    return res


