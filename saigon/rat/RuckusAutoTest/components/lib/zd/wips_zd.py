'''
 wips related configuration 
'''
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
locs={
      'rogue_dhcp_server_detection_checkbox':r"//input[@id='dhcpp']",
      'rogue_dhcp_server_detection_apply_button':"//input[@id='apply-dhcpp']",

    # Configure -> WIPS
    'loc_cfg_wips_span':r"//span[@id='configure_wips']",
    'loc_cfg_wips_report_rogue_devices_checkbox':r"//input[@id='report-rogue-ap']",
    'loc_cfg_wips_prevent_malicious_rogue_ap_checkbox':r"//input[@id='report-malicious-ap']",
    'loc_cfg_wips_apply_button':r"//input[@id='apply-wips']",
    }

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WIPS)
    
def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WIPS)

def enable_rogue_dhcp_server_detection(zd):
    checkbox=locs['rogue_dhcp_server_detection_checkbox']
    button=locs['rogue_dhcp_server_detection_apply_button']
    
    nav_to(zd)
    if not zd.s.is_checked(checkbox):
        zd.s.click_and_wait(checkbox)
        zd.s.click_and_wait(button)
    
    
def disable_rogue_dhcp_server_detection(zd):
    checkbox=locs['rogue_dhcp_server_detection_checkbox']
    button=locs['rogue_dhcp_server_detection_apply_button']
    
    nav_to(zd)
    if zd.s.is_checked(checkbox):
        zd.s.click_and_wait(checkbox)
        zd.s.click_and_wait(button)
        
def get_dhcp_server_dection_status(zd):
    checkbox=locs['rogue_dhcp_server_detection_checkbox']
    nav_to(zd)
    if zd.s.is_checked(checkbox):
        return True
    else:
        return False
        
def config_rogue_dhcp_server_detection(zd,enable=True):
    if enable:
        enable_rogue_dhcp_server_detection(zd)
    else:
        disable_rogue_dhcp_server_detection(zd)
    
    
def enable_wips_report_rogue_devices(zd):
    _nav_to(zd)
    zd.s.click_if_not_checked(locs['loc_cfg_wips_report_rogue_devices_checkbox'])
    zd.s.click_and_wait(locs['loc_cfg_wips_apply_button'])
    
def enable_wips_prevent_rogue_devices(zd):
    _nav_to(zd)
    zd.s.click_if_not_checked(locs['loc_cfg_wips_prevent_malicious_rogue_ap_checkbox']) 
    zd.s.click_and_wait(locs['loc_cfg_wips_apply_button'])

def enable_wips_all_options(zd):
    _nav_to(zd)
    zd.s.click_if_not_checked(locs['loc_cfg_wips_report_rogue_devices_checkbox'])
    zd.s.click_if_not_checked(locs['loc_cfg_wips_prevent_malicious_rogue_ap_checkbox']) 
    zd.s.click_and_wait(locs['loc_cfg_wips_apply_button'])

def disable_wips_report_rogue_devices(zd):
    _nav_to(zd)
    zd.s.click_if_checked(locs['loc_cfg_wips_report_rogue_devices_checkbox'])
    zd.s.click_and_wait(locs['loc_cfg_wips_apply_button'])
    
def disable_wips_prevent_rogue_devices(zd):
    _nav_to(zd)
    zd.s.click_if_checked(locs['loc_cfg_wips_prevent_malicious_rogue_ap_checkbox']) 
    zd.s.click_and_wait(locs['loc_cfg_wips_apply_button'])

def disable_wips_all_options(zd):
    _nav_to(zd)
    zd.s.click_if_checked(locs['loc_cfg_wips_prevent_malicious_rogue_ap_checkbox']) 
    zd.s.click_if_checked(locs['loc_cfg_wips_report_rogue_devices_checkbox'])
    zd.s.click_and_wait(locs['loc_cfg_wips_apply_button'])
