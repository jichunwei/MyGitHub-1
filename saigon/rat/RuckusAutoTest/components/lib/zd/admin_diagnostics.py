import logging
import time
import os

from RuckusAutoTest.components.lib.zd import control_zd as control_zd
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.components.lib.zd import aps

from RuckusAutoTest.common import lib_Constant as constant

LOCATORS_ADMIN_DIAG  = {
    'loc_admin_diagnostics_save_debug_info':r"//input[@value='Save Debug Info']",
    'loc_admin_diagnostics_save_sys_log':r"//input[@value='Save System Log']",
}
#@author: yu.yanan #@since: 2014-06-10
locators = dict(
    cur_ap_tb1_loc = r"//table[@id='curraps']",
    cur_ap_tb1_nav_loc = r"//table[@id='curraps']/tfoot",
    capture_tb1_loc = r"//table[@id='capaps']",
    capture_tb1_nav_loc = r"//table[@id='capaps']/tfoot",
    add_to_capture_aps_btn = r"//input[@id='custom-curraps']",
    remove_all_capture_aps_btn =r"//input[@id='cap-remove-all']",
    cur_ap_all_check = r"//input[@id='curraps-sall']",
    capture_ap_all_check =r"//input[@id='capaps-sall']",
    cur_ap_tb1_value_loc = r"//table[@id='curraps']/tbody/tr"
)
AP_INFO_MAP = {
    'description': 'description',
    'devname': 'device_name',
    'ip': 'ip_addr',
    'ipv6': 'ipv6',
    'mac': 'mac',
    'model': 'model'
}

save_to = constant.save_to
loc = LOCATORS_ADMIN_DIAG
#@author: yu.yanan #@since: 2014-06-10
def _nav_to(zd):
    return zd.navigate_to(zd.ADMIN, zd.ADMIN_DIAGNOSTIC)

def download_file(zd,download_button,filename_re):
    zd.navigate_to(zd.ADMIN, zd.ADMIN_DIAGNOSTIC)
    file_path = control_zd.download_single_file(zd, download_button, filename_re=filename_re, save_to=save_to)
    logging.debug('The current file save at %s' % file_path)
    if not file_path:
        logging.error("save file fail! the file is empty")
        return False
    return True

def save_dbg_info(zd):
    return download_file(zd,loc['loc_admin_diagnostics_save_debug_info'],'.+.dbg')

def save_sys_log(zd):
    return download_file(zd,loc['loc_admin_diagnostics_save_sys_log'],'.+.tar')

#@author: yu.yanan #@since: 2014-06-10
def _get_all_ap_briefs(zd,loc,nav_loc):
    _nav_to(zd)
    time.sleep(3)   
    ap_info_list = wgt.get_tbl_rows(zd.s, loc, nav_loc) 
    return aps.update_ipv4_ipv6(ap_info_list)
    

def get_current_aps_from_admin_diagnostics(zd):
    
    return list_to_dict(wgt.map_rows(_get_all_ap_briefs(zd,locators['cur_ap_tb1_loc'],locators['cur_ap_tb1_nav_loc']), AP_INFO_MAP),'mac')

def _open_add_to_capture_aps(zd):
    _nav_to(zd)
    time.sleep(6)  
    zd.refresh()
    time.sleep(6)   
    zd.s.click_if_not_checked(locators['cur_ap_all_check'])
 
    if zd.s.is_element_present(locators['cur_ap_tb1_value_loc']):
        zd.s.click_and_wait(locators['add_to_capture_aps_btn'],8)
        logging.debug('click and wait add to capture aps btn')
    else:
        logging.error("Error: current aps table is empty")
        return False

def _close_remove_all_capture_aps(zd):
    _nav_to(zd)
    time.sleep(3)    
    zd.s.click_if_not_checked(locators['capture_ap_all_check'])
    zd.s.click_and_wait(locators['remove_all_capture_aps_btn'])
    logging.debug('close to capture aps btn')
def get_capture_aps(zd):
    _open_add_to_capture_aps(zd)
    capture_aps_list = _get_all_ap_briefs(zd,locators['capture_tb1_loc'],locators['capture_tb1_nav_loc'])
    logging.debug('capture_aps_list:%s',capture_aps_list)
    _close_remove_all_capture_aps(zd)
    if capture_aps_list == []:
        logging.error("capture aps table is None!")
        return False
    return list_to_dict(wgt.map_rows(capture_aps_list, AP_INFO_MAP),'mac')  

def get_current_aps_table_title(zd):
    _nav_to(zd)
    time.sleep(6)
    zd.refresh()
    time.sleep(6) 
    table_title_list = zd.s.get_visible_tbl_hdrs_by_attr( locators['cur_ap_tb1_loc'], attr='innerText')
    logging.debug('get current aps table title list: %s' % table_title_list)
    return table_title_list

def get_capture_aps_table_title(zd):
    _open_add_to_capture_aps(zd)
    table_title_list = zd.s.get_visible_tbl_hdrs_by_attr( locators['capture_tb1_loc'], attr='innerText')
    logging.debug('get capture aps table title list: %s' % table_title_list)
    _close_remove_all_capture_aps(zd)
    return table_title_list
   
