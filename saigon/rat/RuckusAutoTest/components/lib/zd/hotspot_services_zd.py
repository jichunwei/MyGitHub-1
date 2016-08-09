import logging
import time
import re
import copy

from RuckusAutoTest.components.lib.zd import widgets_zd as WGT

LOCATORS_CFG_HOTSPOTS_SERVICES = dict(
    # Configure -> Hotspot Services
    hs_tbl_loc = "//table[@id='hotspot']",
    clone_profile_span = "//table[@id='hotspot']//tr/td[text()='%s']/../td/span[text()='Clone']",
    edit_profile_span = "//table[@id='hotspot']//tr/td[text()='%s']/../td/span[text()='Edit']",
    create_profile_span = "//span[@id='new-hotspot']",
    
    check_box_before_profile = r"//tr[@idx=%s]//input[@type='checkbox']",
    
    show_more_button = "//input[@id='showmore-hotspot']",
    delete_button = "//input[@id='del-hotspot']",

    select_all_checkbox = "//input[@id='hotspot-sall']",

    ok_button = "//input[@id='ok-hotspot']",
    cancel_button = "//input[@id='cancel-hotspot']",

    name_textbox = "//input[@id='name']",
    login_url_textbox = "//input[@id='login-page-url']",
    start_page_user_radio = "//input[@id='start-page-type-user']",
    start_page_url_radio = "//input[@id='start-page-type-url']",
    start_page_url_textbox = "//input[@id='start-page-url']",
    session_timeout_checkbox = "//input[@id='session-timeout']",
    max_session_timeout_textbox = "//input[@id='max-session-time']",
    idle_timeout_checkbox = "//input[@id='idle-timeout']",
    max_idle_timeout_textbox = "//input[@id='max-idle-time']",
    authsvr_listbox = "//select[@id='authsvr-select']",
    mac_auth_checkbox = "//input[@id='mac-auth']",
    mac_auth_mac_radio = "//input[@id='mac-auth-mac']",
    mac_auth_pwd_radio = "//input[@id='mac-auth-pwd']",
    mac_auth_passwd_radio = "//input[@id='mac-auth-passwd']",
    mac_auth_passwd_1x_format = "//input[@id='mac-auth-1x-format']",
    #@author: chentao Since:2013-10-10 To adapt the mac addr format behavior change
    mac_addr_format_listbox = "//select[@id='mac-addr-format']",
    #@author: chentao Since:2013-10-10 To adapt the mac addr format behavior change
    
    acctsvr_listbox = "//select[@id='acctsvr-select']",
    interim_update_freq_textbox = "//input[@id='interim-update-frequency']",
    additional_radius_attr_img = "//img[@id='show-additional-radius-attr-icon']",
    location_id_textbox = "//input[@id='location-id']",
    location_name_textbox = "//input[@id='location-name']",
    walled_garden_img = "//img[@id='show-walled-garden-icon']",
    walled_garden_textbox = "//input[@id='walled-garden-%s']",
    walled_garden_img_collapse = "//img[@id='show-walled-garden-icon' and contains(@src, 'collapse')]",
    walled_garden_img_expand = "//img[@id='show-walled-garden-icon' and contains(@src, 'expand')]",
     
    walled_garden_create_new =  r"//span[@id='new-walledgarden']",
    walled_garden_add_textbox =  r"//input[@id='walledgarden-addr']",
    walled_garden_get_textbox = r"//table[@id='walledgarden']/tbody/tr[%s]/td[3]",
    walled_garden_save_button = r"//input[@id='ok-walledgarden']",
    walled_garden_delete_button = r"//input[@id='del-walledgarden']",
    walled_garden_select_all_checkbox = r"//input[@id='walledgarden-sall']",
     
    MAX_WALLED_GARDEN =  35,

    # "restricted subnet access" webUI changed (#11324)
    loc_restricted_subnet_select_all_checkbox = "//input[@id='rule-sall']",
    loc_restricted_subnet_delete_button = "//input[@id='del-rule']",
    
    loc_restricted_subnet_advanced_img_check = "//img[@id='icon']",
    loc_restricted_subnet_advanced_img_collapse = "//img[@id='icon' and contains(@src, 'collapse')]",
    loc_restricted_subnet_advanced_img_expand = "//img[@id='icon' and contains(@src, 'expand')]",
    loc_restricted_subnet_newrule_span = "//span[@id='new-rule']",

    loc_restricted_subnet_rule_ok_button = "//input[@id='ok-rule']",
    loc_restricted_subnet_rule_description_textbox = "//input[@id='rule-description']",
    loc_restricted_subnet_rule_action_option = "//select[@id='rule-action']",
    loc_restricted_subnet_rule_dstaddr_textbox = "//input[@id='rule-dst-addr']",
    loc_restricted_subnet_rule_app_option = "//select[@id='rule-app']",
    loc_restricted_subnet_rule_protocol_textbox = "//input[@id='rule-protocol']",
    loc_restricted_subnet_rule_dstport_textbox = "//input[@id='rule-dst-port']",
    
    rule_row = "//table[@id='rule']//tr[td=%s]/td[%s]",
    check_a_rule = "//table[@id='rule']//tr[td='%s']//input",
    
    # "restricted IPV6 access" webUI changed 
    loc_restricted_ipv6_select_all_checkbox = "//input[@id='rule6-sall']",
    loc_restricted_ipv6_delete_button = "//input[@id='del-rule6']",
    
    loc_restricted_ipv6_advanced_img_check = "//img[@id='icon6']",
    loc_restricted_ipv6_advanced_img_collapse = "//img[@id='icon6' and contains(@src, 'collapse')]",
    loc_restricted_ipv6_advanced_img_expand = "//img[@id='icon6' and contains(@src, 'expand')]",
    loc_restricted_ipv6_newrule_span = "//span[@id='new-rule6']",

    loc_restricted_ipv6_rule_ok_button = "//input[@id='ok-rule6']",
    loc_restricted_ipv6_rule_description_textbox = "//input[@id='rule6-description']",
    loc_restricted_ipv6_rule_action_option = "//select[@id='rule6-action']",
    loc_restricted_ipv6_rule_dstaddr_textbox = "//input[@id='rule6-dst-addr']",
    loc_restricted_ipv6_rule_app_option = "//select[@id='rule6-app']",
    loc_restricted_ipv6_rule_protocol_textbox = "//input[@id='rule6-protocol']",
    loc_restricted_ipv6_rule_dstport_textbox = "//input[@id='rule6-dst-port']",
    loc_restricted_ipv6_rule_icmptype_textbox = "//input[@id='rule6-icmp-type']",
    
    rule6_row = "//table[@id='rule6']//tr[td=%s]/td[%s]",
    check_a_rule6 = "//table[@id='rule6']//tr[td='%s']//input",
    
    # for profiles table
    loc_profiles_total_number_span = "//div[@id='actions-hotspot']/span",
    loc_profile_name_cell = "//table[@id='hotspot']//tr[%s]/td[2]",
    loc_profile_next_image = "//img[@id='next-hotspot']",  
    const_profile_table_size = 15,

    # for backward compatibility
    restricted_subnet_img = "//img[@id='show-restricted-subnet-icon']",
    more_restricted_subnet_img = "//img[@id='more-restricted-subnet-icon']",
    restricted_subnet_textbox = "//input[@id='restricted-subnet-%s']",
    
    restricted_ipv6_img = "//img[@id='show-restricted-ipv6-access-icon']",
    more_restricted_ipv6_img = "//img[@id='more-restricted-ipv6-access-icon']",
    restricted_ipv6_textbox = "//input[@id='restricted-ipv6-%s']",
    
    profile_tbl_loc = r"//table[@id='hotspot']",
    profile_tbl_nav_loc = r"//table[@id='hotspot']/tfoot", 

    loc_profiles_search_box = '//tr[@class="t_search"]//span[@class="other-act"]/input[@type="text"]',
    total_profiles_span = "//table[@id='hotspot']//div[@id='actions-hotspot']/span",
    hotspot_row_with_profile_name = "//table[@id='hotspot']//tr/td[text()='%s']/../td[%s]",
    column_id = {'checkbox': 1,
                 'profile_name': 2,
                 'redirect_url': 3,
                 'start_page': 4,                 
                 }, 
                                      
)

locs = LOCATORS_CFG_HOTSPOTS_SERVICES

###
##
## Hotspot Services
##
###
def create_profile_2(zd, cfg, is_nav = True):
    '''
    . a simplified version of create_profile
    '''
    _cfg = copy.deepcopy(cfg)
    _cfg['is_nav'] = is_nav

    return create_profile(zd, **_cfg)

def create_profile(zd, **kwargs):
    """ Create a new Hotspot Service profile
    @param zd: the reference to the Zone Director object
    @kwargs: keyworded argument list
             . is_nav: this param to support create a Hotspot Service on ZD
               template from FlexMaster. If do this from FM, don't navigate.
    """
    params = {
        'name': '',
        'login_page': '',
        'start_page': None,
        'session_timeout': None,
        'idle_timeout': None,
        'auth_svr': '',
        'acct_svr': '',
        'interim_update_interval': None,
        'radius_location_id': '',
        'radius_location_name': '',
        'walled_garden_list': [],
        'restricted_subnet_list': [],
        'restricted_ipv6_list':[],
        'enable_mac_auth': None,
        'mac_bypass_format': None,
        'mac_bypass_password': None,
        'is_nav': True,
    }
    params.update(kwargs)

    if params.pop('is_nav'):
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)

    try:
        if zd.s.is_element_disabled(locs['create_profile_span'], timeout = 1):
            raise Exception("Unable to create more when the 'Create New' button is disabled.")
       
        zd.s.click_and_wait(locs['create_profile_span'])
        zd.s.type_text(locs['name_textbox'], params['name'])
        zd.s.type_text(locs['login_url_textbox'], params['login_page'])

        if params['start_page'] is None:
            zd.s.click_and_wait(locs['start_page_user_radio'])

        else:
            zd.s.click_and_wait(locs['start_page_url_radio'])
            zd.s.type_text(locs['start_page_url_textbox'], params['start_page'])

        if params['session_timeout'] is not None:
            zd.s.click_and_wait(locs['session_timeout_checkbox'])
            zd.s.type_text(locs['max_session_timeout_textbox'], params['session_timeout'])

        if params['idle_timeout'] is not None:
            zd.s.click_and_wait(locs['idle_timeout_checkbox'])
            zd.s.type_text(locs['max_idle_timeout_textbox'], params['idle_timeout'])

        if params['auth_svr']:
            zd.s.select_option(locs['authsvr_listbox'], params['auth_svr'])
            zd.s.click_and_wait(locs['authsvr_listbox'])

        if params['enable_mac_auth'] is not None:
            if params['enable_mac_auth']:
                zd.s.click_if_not_checked(locs['mac_auth_checkbox'])

                if params['mac_bypass_password'] is not None:
                    zd.s.click_and_wait(locs['mac_auth_pwd_radio'])
                    zd.s.type_text(locs['mac_auth_passwd_radio'], params['mac_bypass_password'])
    
                if params['mac_bypass_format'] is not None:
                    #zd.s.click_if_not_checked(locs['mac_auth_passwd_1x_format'])
                    #@author: chentao Since:2013-10-10 To adapt the mac addr format behavior change
                    if params.get('mac_addr_format') is not None:
                        mac_addr_format = params['mac_addr_format']
                    else:
                        mac_addr_format = "AA-BB-CC-DD-EE-FF"  
                    zd.s.select_option(locs['mac_addr_format_listbox'], mac_addr_format)
                    zd.s.click_and_wait(locs['mac_addr_format_listbox'])
                    #@author: chentao Since:2013-10-10 To adapt the mac addr format behavior change

            else:
                zd.s.click_if_checked(locs['mac_auth_checkbox'])

        if params['acct_svr']:
            zd.s.select_option(locs['acctsvr_listbox'], params['acct_svr'])
            zd.s.click_and_wait(locs['acctsvr_listbox'])

        if params['interim_update_interval'] is not None:
            zd.s.type_text(locs['interim_update_freq_textbox'], params['interim_update_interval'])

        if params['radius_location_id'] or params['radius_location_name']:
            zd.s.click_and_wait(locs['additional_radius_attr_img'])
            zd.s.type_text(locs['location_id_textbox'], params['radius_location_id'])
            zd.s.type_text(locs['location_name_textbox'], params['radius_location_name'])

        if params['walled_garden_list']:            
            _cfg_walled_garden(zd, params)

        if params['restricted_subnet_list']:
            zd.s.click_and_wait(locs['restricted_subnet_img'])
            _cfg_restricted_subnet(zd, params)
        
        
        if params['restricted_ipv6_list']:
            zd.s.click_and_wait(locs['restricted_ipv6_img'])
            if zd.s.is_element_present(locs['loc_restricted_ipv6_advanced_img_collapse']):
                zd.s.click_and_wait(locs['loc_restricted_ipv6_advanced_img_collapse'])
            _cfg_restricted_ipv6(zd, params)
        

        zd.s.click_and_wait(locs['ok_button'])
        time.sleep(5)

        if zd.s.is_alert_present(5):
            raise Exception(zd.s.get_alert())

    except Exception, e:
        logging.info("Error when creating a Hotspot profile [%s]" % e.message)
        raise Exception(e.message)

    logging.info("Hotspot profile [%s] was created successfully" % params['name'])

def clone_profile(zd, old_name, new_name):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    profiles_total = get_total_profiles(zd)
    max_ap_per_page = int(locs['const_profile_table_size'])
    row = 1
    i = 0    
    while i < int(profiles_total):
        find_profile = locs['loc_profile_name_cell'] % str(row)
        name = zd.s.get_text(find_profile)
        if name == old_name:        
            clone_span = locs['clone_profile_span'] % name
            zd.s.click_and_wait(clone_span)
            zd.s.type_text(locs['name_textbox'], new_name)   
            zd.s.click_and_wait(locs['ok_button'])
            time.sleep(5)
    
            if zd.s.is_alert_present(5):
                raise Exception(zd.s.get_alert())                   
            return
            
        if row == max_ap_per_page:
            zd.s.click_and_wait(locs['loc_profile_next_image'])
            row = 0
            
        time.sleep(1)
        row += 1
        i += 1        
    
    raise Exception("Not found profile [%s]" %old_name)
    
def cfg_profile(zd, old_name, **p_cfg):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    time.sleep(2)

    profiles_total = get_total_profiles(zd, is_nav = False)
    max_ap_per_page = int(locs['const_profile_table_size'])
    row = 1
    i = 0    
    while i < int(profiles_total):
        find_profile = locs['loc_profile_name_cell'] % str(row)
        name = zd.s.get_text(find_profile)
        if name == old_name:        
            edit_span = locs['edit_profile_span'] % name
            time.sleep(2)
            zd.s.click_and_wait(edit_span)
            _cfg_profile(zd, **p_cfg)
            return
            
        if row == max_ap_per_page:
            zd.s.click_and_wait(locs['loc_profile_next_image'])
            row = 0
            
        time.sleep(1)
        row += 1
        i += 1        
    
    raise Exception("Not found profile [%s]" % p_cfg['name'])

#by West,delete a hot spot   
def del_profile(zd, old_name):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    profiles_total = get_total_profiles(zd)    
    max_ap_per_page = int(locs['const_profile_table_size'])
    row = 1
    i = 0    
    while i < int(profiles_total):
        find_profile = locs['loc_profile_name_cell'] % str(row)
        name = zd.s.get_text(find_profile)
        if name == old_name:    
            zd.s.click_and_wait(locs['check_box_before_profile'] % str(i))
            zd.s.click_and_wait(locs['delete_button'])
            
            return
            
        if row == max_ap_per_page:
            zd.s.click_and_wait(locs['loc_profile_next_image'])
            row = 0
            
        time.sleep(1)
        row += 1
        i += 1        
    
    raise Exception("Not found profile [%s]" % old_name)

def get_profile_info_list(zd, is_nav=True):
    '''
    '''
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)

    return WGT.get_tbl_rows(
        zd.s, locs['hs_tbl_loc'], locs['hs_tbl_loc'],
    )

def get_profile_by_name(zd, profile_name):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    profiles_total = get_total_profiles(zd)    
    max_ap_per_page = int(locs['const_profile_table_size'])
    row = 1
    i = 0    
    while i < int(profiles_total):
        find_profile = locs['loc_profile_name_cell'] % str(row)
        name = zd.s.get_text(find_profile)
        if name == profile_name:        
            edit_span = locs['edit_profile_span'] % name
            zd.s.click_and_wait(edit_span)
            cfg = _get_profile(zd)
            return cfg

        if row == max_ap_per_page:
            zd.s.click_and_wait(locs['loc_profile_next_image'])
            row = 0
            
        time.sleep(1)
        row += 1
        i += 1        
    
    raise Exception("Not found profile [%s]" % profile_name)

def get_all_profiles(zd, is_nav = True):
    '''
    . is_nav: this param to support get all Hotspot Service info of ZD
              template from FlexMaster. If do this from FM, don't navigate.
    '''
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    profiles_total = get_total_profiles(zd, is_nav)
    max_ap_per_page = int(locs['const_profile_table_size'])
    row = 1
    i = 0
    cfg_list = []    
    while i < int(profiles_total):
        find_profile = locs['loc_profile_name_cell'] % str(row)
        name = zd.s.get_text(find_profile)
        edit_span = locs['edit_profile_span'] % name
        zd.s.click_and_wait(edit_span)
        cfg = _get_profile(zd)
        cfg_list.append(cfg)
        if row == max_ap_per_page:
            zd.s.click_and_wait(locs['loc_profile_next_image'])
            row = 0

        time.sleep(1)
        row += 1
        i += 1        
    
    return cfg_list

def get_total_profiles(zd, is_nav = True):
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    locator = locs['loc_profiles_total_number_span']
    number_profiles = zd.s.get_text(locator)
    if not number_profiles:
        time.sleep(5)
        number_profiles = zd.s.get_text(locator)

    time.sleep(1)
    pat = ".*\(([0-9]+)\)$"
    match_obj = re.search(pat, number_profiles)
    if match_obj:
        number_servers = match_obj.group(1)

    else:
        raise Exception("Can not get the total number of rows in profiles Table")

    time.sleep(3)

    return number_servers

def compare_hotspot_restricted_ipv6_access_gui_set_get(set_ipv6_access_list, get_ipv6_access_list):
    '''
    Compare hotspot restricted ipv6 access between GUI set and get.
    '''
    res_dict = {}
    
    gui_get_acl = _convert_list_to_dict(get_ipv6_access_list, 'order')
    set_acl = _convert_list_to_dict(set_ipv6_access_list, 'order')
    
    cli_get_set_keys_mapping = {'type': 'action',}
    
    if len(gui_get_acl) != len(set_acl):
        res_dict['Count'] = "GUI get: %s, GUI set: %s" % (len(gui_get_acl), len(set_acl))
    else:
        gui_get_keys = gui_get_acl.keys().sort()
        gui_set_keys = set_acl.keys().sort()
        
        if gui_set_keys != gui_get_keys:
            res_dict['Keys'] = "GUI set: %s, GUI get: %s" % (gui_set_keys, gui_get_keys)
        else:
            for order, gui_rule in gui_get_acl.items():
                set_rule = set_acl[order]
                set_rule = _convert_dict_with_new_keys(set_rule, cli_get_set_keys_mapping)
                res = _compare_ipv6_rule(set_rule, gui_rule)
                if res:
                    res_dict[order] = res
    
    return res_dict

def remove_profile(zd, profile_name, wait_time = 2):
    """
    """
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    time.sleep(wait_time * 3)

    zd.s.type_keys(info['loc_profiles_search_box'], profile_name)

    time.sleep(wait_time * 2)
    
    while zd.s.is_visible(locs['show_more_button']):
        zd.s.click_and_wait(locs['show_more_button'])

    fidx, lidx, total = _get_page_range_and_total_number_of_profiles(zd)
    profile_existing = True
    if total != '0':
        loc = '%s/input' % (info['hotspot_row_with_profile_name'] % (profile_name, locs['column_id']['checkbox']))
        try:
            zd.s.click_and_wait(loc)
            time.sleep(wait_time / 4)
            zd.s.click_and_wait(locs['delete_button'], 60)
            time.sleep(wait_time)
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception("[ALERT] %s" % msg_alert)

            logging.info('Deleted the profile "%s" successfully' % profile_name)

        except Exception, e:
            if e.message == 'Element %s not found' % loc:
                profile_existing = False

            else:
                raise Exception('[Delete profile %s failed]: %s' % (profile_name, e.message))

    if total == '0' or not profile_existing:
        raise Exception('The profile "%" is not existed')    

def get_profile_name_list(zd, is_nav = True, pause = 10):
    """
    Return the profile name list on the hotspot table of Zone Director
    """
    if is_nav:
        zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
        
    if not zd._wait_for_element(locs['profile_tbl_nav_loc'], pause):
        raise Exception('Not find element [%s]' % locs['profile_tbl_nav_loc'])
    
    profile_list = WGT.get_tbl_rows(zd.s, locs['profile_tbl_loc'], locs['profile_tbl_nav_loc'])
    profile_name_list = [profile['name'] for profile in profile_list]

    return profile_name_list
    
def remove_all_profiles(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)

    while zd.s.is_visible(locs['show_more_button']):
        zd.s.click_and_wait(locs['show_more_button'])
        
    zd.s.click_and_wait(locs['select_all_checkbox'])
    zd.s.click_and_wait(locs['delete_button'], 20)
    
def get_hot_spot_auth_server_list(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)
    zd.s.click_and_wait(locs['create_profile_span'])
    list = zd.s.get_select_options(locs['authsvr_listbox'])
    zd.s.click_and_wait(locs['cancel_button'])
    return list

def _get_all_restricted_subnet_entries(zd):
    """ Retrieve information of all non-default hotspot rules
    @param zd: reference to the Zone Director object
    """
    acl_list = []

    try:        
        zd.s.click_and_wait(locs['restricted_subnet_img']) 
        loc = locs['loc_restricted_subnet_advanced_img_collapse']       
        if zd.s.is_element_present(loc) and zd.s.is_element_visible(loc):            
            zd.s.click_and_wait(loc)

        order = 1
        while zd.s.is_element_present(locs['rule_row'] % (order, 2), timeout = 2):
            if zd.s.is_element_present(locs['check_a_rule'] % order, timeout = 2):
                entry = {}
                entry['order'] = str(order)
                entry['description'] = zd.s.get_text(locs['rule_row'] % (order, 3))
                entry['action'] = zd.s.get_text(locs['rule_row'] % (order, 4))
                entry['dst_addr'] = zd.s.get_text(locs['rule_row'] % (order, 5))
                entry['application'] = zd.s.get_text(locs['rule_row'] % (order, 6))
                entry['protocol'] = zd.s.get_text(locs['rule_row'] % (order, 7))
                entry['dst_port'] = zd.s.get_text(locs['rule_row'] % (order, 8))
                acl_list.append(entry)
            order += 1

    except Exception, e:
        logging.info("Catch the error when reading the Hotspot rules [%s]" % e.message)
        raise

    return acl_list

def _get_all_restricted_ipv6_entries(zd):
    """ Retrieve information of all non-default hotspot rules
    @param zd: reference to the Zone Director object
    """
    acl_list = []

    try:        
        zd.s.click_and_wait(locs['restricted_ipv6_img'])
        loc = locs['loc_restricted_ipv6_advanced_img_collapse']
        if zd.s.is_element_present(loc) and zd.s.is_element_visible(loc):
            zd.s.click_and_wait(loc)

        order = 1
        while zd.s.is_element_present(locs['rule6_row'] % (order, 2), timeout = 2):
            if zd.s.is_element_present(locs['check_a_rule6'] % order, timeout = 2):
                entry = {}
                entry['order'] = str(order)
                entry['description'] = zd.s.get_text(locs['rule6_row'] % (order, 3))
                entry['action'] = zd.s.get_text(locs['rule6_row'] % (order, 4))
                entry['destination_addr'] = zd.s.get_text(locs['rule6_row'] % (order, 5))
                entry['application'] = zd.s.get_text(locs['rule6_row'] % (order, 6))
                entry['protocol'] = zd.s.get_text(locs['rule6_row'] % (order, 7))
                entry['destination_port'] = zd.s.get_text(locs['rule6_row'] % (order, 8))
                entry['icmp_type'] = zd.s.get_text(locs['rule6_row'] % (order, 9))
                acl_list.append(entry)
            order += 1

    except Exception, e:
        logging.info("Catch the error when reading the Hotspot rules [%s]" % e.message)
        raise

    return acl_list

def _convert_dict_with_new_keys(org_dict, keys_mapping):
    '''
    Convert dict replace key with new key based on keys_mapping.
    '''
    new_dict = {}
    
    if keys_mapping:
        for key, value in org_dict.items():
            if keys_mapping.has_key(key):
                new_key = keys_mapping[key]
            else:
                new_key = key
                
            new_dict[new_key] = value
    else:
        new_dict = org_dict
        
    return new_dict

def _compare_ipv6_rule(rule_dict_1, rule_dict_2):
    '''
    Compare two rule dicts. Protocol value may be ICMPv6 (58), will convert to 58.
    dict structure is 
        {'order': '', 'description': '', 'action': '', 
         'dst_addr': '', 'application': '', 'protocol': '', 
         'dst_port': '', 'icmp_type': ''}
    '''
    #Pop order and application if another dict no data.
    if rule_dict_1.has_key('order') and not rule_dict_2.has_key('order'):
        rule_dict_1.pop('order')
    elif rule_dict_2.has_key('order') and not rule_dict_1.has_key('order'):
        rule_dict_2.pop('order')
        
    if rule_dict_1.has_key('application') and not rule_dict_2.has_key('application'):
        rule_dict_1.pop('application')
    elif rule_dict_2.has_key('application') and not rule_dict_1.has_key('application'):
        rule_dict_2.pop('application')
        
    dict_1_keys = rule_dict_1.keys().sort()
    dict_2_keys = rule_dict_2.keys().sort()
    
    res_rule = {}
    if dict_1_keys != dict_2_keys:
        res_rule['Keys'] = "Dict 1: %s, Dict 2: %s" % (dict_1_keys, dict_2_keys)
    else:
        for key, value in rule_dict_1.items():
            value_2 = rule_dict_2.get(key)
            if key.lower() == 'protocol':
                pattern = '.*\((?P<value>[0-9]+)\)'
                matcher = re.compile(pattern).match(value_2)
                if matcher:
                    value_2 = matcher.groupdict()['value']                    
                    
                matcher = re.compile(pattern).match(value)
                if matcher:
                    value = matcher.groupdict()['value']
                        
            if value and value_2 and str(value).lower() != str(value_2).lower():
                fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                res_rule[key] = fail_msg
            elif value != value_2:
                fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                res_rule[key] = fail_msg
    
    if res_rule:
        return "Rule is different: %s" % res_rule
    else:
        return "" 

def _convert_list_to_dict(cfg_list, key_name):
    '''
    Convert dict list to a dict, will use cfg key_name value as key.
    '''     
    cfg_dict = {}
    
    for cfg in cfg_list:
        cfg_dict[cfg[key_name]] = cfg
    
    return cfg_dict

def _get_profile(zd):
    '''
    Return DICT:
    {
        'name': '',
        'login_page': '',
        'start_page': None,
        'session_timeout': None,
        'idle_timeout': None,
        'auth_svr': '',
        'acct_svr': '',
        'interim_update_interval': None,
        'radius_location_id': '',
        'radius_location_name': '',
        'walled_garden_list': [],
        'restricted_subnet_list': [],
        'enable_mac_auth': None,    
    }    
    '''
    profile_cfg = {
        'name': '',
        'login_page': '',
        'start_page': None,
        'session_timeout': None,
        'idle_timeout': None,
        'auth_svr': '',
        'acct_svr': '',
        'interim_update_interval': None,
        'radius_location_id': '',
        'radius_location_name': '',
        'walled_garden_list': [],
        'restricted_subnet_list': [],
        'restricted_ipv6_list': [],
        'enable_mac_auth': None,    
        }    
    profile_cfg['name'] = zd.s.get_value(locs['name_textbox'])
    profile_cfg['login_page'] = zd.s.get_value(locs['login_url_textbox'])
    if zd.s.is_checked(locs['start_page_url_radio']):
        profile_cfg['start_page'] = zd.s.get_value(locs['start_page_url_textbox'])
    
    if zd.s.is_checked(locs['session_timeout_checkbox']):
        profile_cfg['session_time'] = zd.s.get_value(locs['max_session_timeout_textbox'])
    
    if zd.s.is_checked(locs['idle_timeout_checkbox']):
        profile_cfg['idle_time'] = zd.s.get_value(locs['max_idle_timeout_textbox'])

    else:
        profile_cfg['idle_time'] = 'Disabled'

    profile_cfg['auth_svr'] = zd.s.get_selected_option(locs['authsvr_listbox'])
    profile_cfg['acct_svr'] = zd.s.get_selected_option(locs['acctsvr_listbox'])
    if not zd.s.is_element_disabled(locs['interim_update_freq_textbox']):
        profile_cfg['interim_update_interval'] = zd.s.get_value(locs['interim_update_freq_textbox'])
        
    if zd.s.is_element_present(locs['mac_auth_checkbox']) \
    and zd.s.is_visible(locs['mac_auth_checkbox']):
        if zd.s.is_checked(locs['mac_auth_checkbox']):
            profile_cfg['enable_mac_auth'] = True
        else:
            profile_cfg['enable_mac_auth'] = False
    
#    import pdb
#    pdb.set_trace()
    zd.s.click_and_wait(locs['additional_radius_attr_img'])
    if not zd.s.is_element_disabled(locs['location_id_textbox']):
        profile_cfg['radius_location_id'] = zd.s.get_value(locs['location_id_textbox'])
    
    if not zd.s.is_element_disabled(locs['location_name_textbox']):
        profile_cfg['radius_location_name'] = zd.s.get_value(locs['location_name_textbox'])
        
    zd.s.click_and_wait(locs['additional_radius_attr_img'])
    
    
    
    profile_cfg['walled_garden_list'] = _get_walled_garden(zd)
    
    profile_cfg['restricted_subnet_list'] = _get_all_restricted_subnet_entries(zd)
    
    profile_cfg['restricted_ipv6_list'] = _get_all_restricted_ipv6_entries(zd)
    
    zd.s.click_and_wait(locs['cancel_button'])
    
    return profile_cfg

def _cfg_profile(zd, **kwargs):
    """ Modify a existed Hotspot Service profile
    @param zd: the reference to the Zone Director object
    @kwargs: keyworded argument list
    """
    params = {
        'name': '',
        'login_page': '',
        'start_page': None,
        'session_timeout': None,
        'idle_timeout': None,
        'auth_svr': '',
        'acct_svr': '',
        'interim_update_interval': None,
        'radius_location_id': '',
        'radius_location_name': '',
        'walled_garden_list': [],
        'restricted_subnet_list': [],
        'restricted_ipv6_list': [],
        'enable_mac_auth': None,
        'mac_bypass_format': None,
        'mac_bypass_password': None,
    }
    params.update(kwargs)
        
    try:
        zd.s.type_text(locs['name_textbox'], params['name'])
        zd.s.type_text(locs['login_url_textbox'], params['login_page'])

        if params['start_page'] is None:
            zd.s.click_and_wait(locs['start_page_user_radio'])

        else:
            zd.s.click_and_wait(locs['start_page_url_radio'])
            zd.s.type_text(locs['start_page_url_textbox'], params['start_page'])

        if params['session_timeout'] is not None:
            #zd.s.click_and_wait(locs['session_timeout_checkbox'])
            zd.s.click_if_not_checked(locs['session_timeout_checkbox'])
            zd.s.type_text(locs['max_session_timeout_textbox'], params['session_timeout'])
        else:
            zd.s.click_if_checked(locs['session_timeout_checkbox'])
            #zd.s.click_if_checked(locs['max_session_timeout_textbox'])        
            

        if params['idle_timeout'] is not None:
            #zd.s.click_and_wait(locs['idle_timeout_checkbox'])
            zd.s.click_if_not_checked(locs['idle_timeout_checkbox'])
            zd.s.type_text(locs['max_idle_timeout_textbox'], params['idle_timeout'])
        else:            
            #zd.s.click_if_checked(locs['max_idle_timeout_textbox'])
            zd.s.click_if_checked(locs['idle_timeout_checkbox'])

        if params['auth_svr']:
            zd.s.select_option(locs['authsvr_listbox'], params['auth_svr'])
            zd.s.click_and_wait(locs['authsvr_listbox'])
        else:
            zd.s.select_option(locs['authsvr_listbox'], 'Local Database')
            zd.s.click_and_wait(locs['authsvr_listbox'])

        if params['enable_mac_auth'] is not None:
            if params['enable_mac_auth']:
                zd.s.click_if_not_checked(locs['mac_auth_checkbox'])
                
                if params['mac_bypass_password'] is not None:
                    zd.s.click_and_wait(locs['mac_auth_pwd_radio'])
                    zd.s.type_text(locs['mac_auth_passwd_radio'], params['mac_bypass_password'])
                else:
                    zd.s.click_and_wait(locs['mac_auth_mac_radio'])
    
                if params['mac_bypass_format'] is not None:
                    zd.s.click_if_not_checked(locs['mac_auth_passwd_1x_format'])
                else:
                    zd.s.click_if_checked(locs['mac_auth_passwd_1x_format'])

            else:
                zd.s.click_if_checked(locs['mac_auth_checkbox'])

        if params['acct_svr']:
            zd.s.select_option(locs['acctsvr_listbox'], params['acct_svr'])
            zd.s.click_and_wait(locs['acctsvr_listbox'])
        else:
            zd.s.select_option(locs['acctsvr_listbox'], 'Disabled')
            zd.s.click_and_wait(locs['acctsvr_listbox'])            

        if params['interim_update_interval'] is not None:
            zd.s.type_text(locs['interim_update_freq_textbox'], params['interim_update_interval'])        
            

        if params['radius_location_id'] or params['radius_location_name']:
            zd.s.click_and_wait(locs['additional_radius_attr_img'])
            zd.s.type_text(locs['location_id_textbox'], params['radius_location_id'])
            zd.s.type_text(locs['location_name_textbox'], params['radius_location_name'])
                
        #remove walled garden first
        _remove_all_walled_garden(zd)
        if params['walled_garden_list']:
            _cfg_walled_garden(zd, params)

        if params['restricted_subnet_list']:
            zd.s.click_and_wait(locs['restricted_subnet_img'])
            _cfg_restricted_subnet(zd, params)
            
        
        if params['restricted_ipv6_list']:
            zd.s.click_and_wait(locs['restricted_ipv6_img'])
            _cfg_restricted_ipv6(zd, params)

        zd.s.click_and_wait(locs['ok_button'])
        time.sleep(5)

        if zd.s.is_alert_present(5):
            raise Exception(zd.s.get_alert())

    except Exception, e:
        logging.info("Error when modifying a Hotspot profile [%s]" % e.message)
        raise Exception(e.message)

    logging.info("Hotspot profile [%s] was created successfully" % params['name'])
    
#Updated by cwang@20130529, Doesn't support before 9.5 build
def _cfg_walled_garden(zd, params):
    '''
    Udpate it for support behavior change under v91/v92/v93
    '''    
    if zd.s.is_element_present(locs['walled_garden_img_collapse']):
        zd.s.click_and_wait(locs['walled_garden_img_collapse'])
            
    idx = 1
    _cfg = params['walled_garden_list']
#    if params.has_key('Max_walled_garden') and params['Max_walled_garden']:        
#        _cfg = ['www.example.net', '172.21.0.252', '172.22.0.0/16',
#                                        '172.23.0.252:8888', '172.23.0.252', '172.24.0.0/16',
#                                        '172.24.0.252:6666', '172.24.0.252:7777', '172.24.0.252:8888',
#                                        '172.24.0.252:9999', '172.24.0.252', '172.25.0.0/16', '172.25.0.252:6666',
#                                        '172.25.0.252:7777', '172.25.0.252:8888', '172.25.0.252:9999', '172.25.0.252',
#                                        '172.26.0.0/16', '172.26.0.252:6666', '172.26.0.252:7777', '172.26.0.252:8888',
#                                        '172.26.0.252:9999', '172.26.0.252', '172.27.0.0/16', '172.27.0.252:6666', '172.27.0.252:7777',
#                                        '172.27.0.252:8888', '172.27.0.252:9999', '172.27.0.252', '172.28.0.0/16', '172.28.0.252:6666',
#                                        '172.28.0.252:7777', '172.28.0.252:8888', '172.28.0.252:9999', '172.28.0.252', ]

    for v in _cfg:        
        zd.s.click_and_wait(locs['walled_garden_create_new'])
        zd.s.type_text(locs['walled_garden_add_textbox'], v)
#        time.sleep(1.0)
        zd.s.click_and_wait(locs['walled_garden_save_button'])
        
        idx += 1
        
        if idx == int(locs['MAX_WALLED_GARDEN']) + 1:
            logging.info("The given walled_garden_list has exceeded the max size of the table")
            break
        time.sleep(3)

#Update by cwang@20130529
def _remove_all_walled_garden(zd):
    zd.s.click_and_wait(locs['walled_garden_img'])
    zd.s.click_if_not_checked(locs['walled_garden_select_all_checkbox'])
    if not zd.s.is_element_disabled(locs['walled_garden_delete_button']):
        zd.s.choose_ok_on_next_confirmation()
        zd.s.click_and_wait(locs['walled_garden_delete_button'])        
        if zd.s.is_confirmation_present(5):
            logging.info(zd.s.get_confirmation())
            
        if zd.s.is_alert_present(5):
            _alert = zd.s.get_alert()
            if not re.search('Nothing\s+is\s+selected', _alert, re.I):
                raise Exception(_alert)                
    else:
        logging.info('Have not any walled garden been selected.')


#Update by cwang@20130529, doesn't support before 9.5 build
def _get_walled_garden(zd):
    walled_garden_list = []
    loc = locs['walled_garden_img_collapse']
    if zd.s.is_element_present(loc) and zd.s.is_element_visible(loc):
        zd.s.click_and_wait(loc)
        
    for idx in range(1, int(locs['MAX_WALLED_GARDEN'])+1):
        x = locs['walled_garden_get_textbox'] % idx
        if zd.s.is_element_present(x):
            walled_garden_list.append(zd.s.get_text(x))
        else:
            break
    
    if zd.s.is_element_present(locs['walled_garden_img_expand']):
        zd.s.click_and_wait(locs['walled_garden_img_expand'])
    
    
    return walled_garden_list


def _cfg_restricted_subnet(zd, params):
    #Remove rule first.
    if zd.s.is_element_present(locs['loc_restricted_subnet_select_all_checkbox']):
        zd.s.click_and_wait(locs['loc_restricted_subnet_select_all_checkbox'], 2)
        if zd.s.is_editable(locs['loc_restricted_subnet_delete_button']):
            zd.s.click_and_wait(locs['loc_restricted_subnet_delete_button'], 10)            
        
    if zd.s.is_element_present(locs['loc_restricted_subnet_advanced_img_check']):
        MAX_RESTRICTED_SUBNET_3 = 32
        if zd.s.is_element_present(locs['loc_restricted_subnet_advanced_img_collapse']):
            zd.s.click_and_wait(locs['loc_restricted_subnet_advanced_img_collapse'])

        idx = 1
        for item in params['restricted_subnet_list']:
            _cfg_restricted_subnet_advanced(zd, item)
            idx += 1

            if idx == MAX_RESTRICTED_SUBNET_3 + 1:
                logging.info("The given restricted_subnet_list has exceeded the max size of the table")
                break

    else:
        _cfg_restricted_subnet_simple(zd, params)
        
def _cfg_restricted_ipv6(zd, params):
    #Remove rule first.
    if zd.s.is_element_present(locs['loc_restricted_ipv6_select_all_checkbox']):
        zd.s.click_and_wait(locs['loc_restricted_ipv6_select_all_checkbox'], 2)
        if zd.s.is_editable(locs['loc_restricted_ipv6_delete_button']):
            zd.s.click_and_wait(locs['loc_restricted_ipv6_delete_button'], 10)            
        
    if zd.s.is_element_present(locs['loc_restricted_ipv6_advanced_img_check']):
        MAX_RESTRICTED_SUBNET_3 = 32
        if zd.s.is_element_present(locs['loc_restricted_ipv6_advanced_img_collapse']):
            zd.s.click_and_wait(locs['loc_restricted_ipv6_advanced_img_collapse'])

        idx = 1
        for item in params['restricted_ipv6_list']:
            _cfg_restricted_ipv6_advanced(zd, item)
            idx += 1

            if idx == MAX_RESTRICTED_SUBNET_3 + 1:
                logging.info("The given restricted_ipv6_list has exceeded the max size of the table")
                break

    else:
        _cfg_restricted_ipv6_simple(zd, params)
        
def _cfg_restricted_subnet_simple(zd, params):
    MAX_RESTRICTED_SUBNET_1 = 5
    MAX_RESTRICTED_SUBNET_2 = 15
    if len(params['restricted_subnet_list']) > MAX_RESTRICTED_SUBNET_1:
        zd.s.click_and_wait(locs['more_restricted_subnet_img'])

    idx = 1
    for item in params['restricted_subnet_list']:
        x = locs['restricted_subnet_textbox'] % idx
        if type(item) is dict:
            item = item['destination_addr']

        zd.s.type_text(x, item)

        idx += 1
        if idx == MAX_RESTRICTED_SUBNET_2 + 1:
            logging.info("The given restricted_subnet_list has exceeded the max size of the table")
            break

def _cfg_restricted_ipv6_simple(zd, params):
    MAX_RESTRICTED_SUBNET_1 = 5
    MAX_RESTRICTED_SUBNET_2 = 15
    if len(params['restricted_ipv6_list']) > MAX_RESTRICTED_SUBNET_1:
        zd.s.click_and_wait(locs['more_restricted_ipv6_img'])

    idx = 1
    for item in params['restricted_ipv6_list']:
        x = locs['restricted_ipv6_textbox'] % idx
        if type(item) is dict:
            item = item['destination_addr']

        zd.s.type_text(x, item)

        idx += 1
        if idx == MAX_RESTRICTED_SUBNET_2 + 1:
            logging.info("The given restricted_ipv6_list has exceeded the max size of the table")
            break

def _cfg_restricted_subnet_advanced(zd, conf):
    params = {'description': '',
              'action': 'Deny',
              'destination_addr': 'Any',
              'application': 'Any',
              'protocol': None,
              'destination_port': None,
              }

    if type(conf) is dict:
        params.update(conf)

    else:
        params.update({'destination_addr': conf})

    try:
        zd.s.click_and_wait(locs['loc_restricted_subnet_newrule_span'])
        #add some 'is_visible' by west.li @2011.1.11,if we don't know the element visiable or not,we should add
        #execption process after the type or select,or the code can't run smooth
        if params['description'] and zd.s.is_visible(locs['loc_restricted_subnet_rule_description_textbox']):
            zd.s.type_text(locs['loc_restricted_subnet_rule_description_textbox'],
                           params['description'])

        if params['action'] and zd.s.is_visible(locs['loc_restricted_subnet_rule_action_option']):
            zd.s.select_option(locs['loc_restricted_subnet_rule_action_option'],
                               params['action'])

        if params['destination_addr'] and zd.s.is_visible(locs['loc_restricted_subnet_rule_dstaddr_textbox']):
            zd.s.type_text(locs['loc_restricted_subnet_rule_dstaddr_textbox'],
                           params['destination_addr'])

        if zd.s.is_element_present(locs['loc_restricted_subnet_advanced_img_expand']):
            if params['application'] and zd.s.is_visible(locs['loc_restricted_subnet_rule_app_option']):
                zd.s.select_option(locs['loc_restricted_subnet_rule_app_option'],
                                   params['application'])

                if params['application'] == 'Any':
                    if params['protocol']:
                        zd.s.type_text(locs['loc_restricted_subnet_rule_protocol_textbox'],
                                       params['protocol'])

                    if params['destination_port']:
                        zd.s.type_text(locs['loc_restricted_subnet_rule_dstport_textbox'],
                                       params['destination_port'])

        zd.s.click_and_wait(locs['loc_restricted_subnet_rule_ok_button'])
        time.sleep(5)


    except Exception, e:
        logging.info("Error in adding the restricted subnet '%s'. " % params['destination_addr'] + e.message)
        raise

    logging.debug("Restricted subnet '%s' was added successfully." % params['destination_addr'])

def _cfg_restricted_ipv6_advanced(zd, conf):
    params = {'description': '',
              'action': 'Deny',
              'destination_addr': 'Any',
              'application': 'Any',
              'protocol': None,
              'destination_port': None,
              'icmp_type': None,
              }

    if type(conf) is dict:
        params.update(conf)

    else:
        params.update({'destination_addr': conf})

    try:
        zd.s.click_and_wait(locs['loc_restricted_ipv6_newrule_span'])

        if params['description']:
            zd.s.type_text(locs['loc_restricted_ipv6_rule_description_textbox'],
                           params['description'])

        if params['action']:
            zd.s.select_option(locs['loc_restricted_ipv6_rule_action_option'],
                               params['action'])

        if params['destination_addr']:
            zd.s.type_text(locs['loc_restricted_ipv6_rule_dstaddr_textbox'],
                           params['destination_addr'])

        if zd.s.is_element_present(locs['loc_restricted_ipv6_advanced_img_expand']):
            if params['application']:
                zd.s.select_option(locs['loc_restricted_ipv6_rule_app_option'],
                                   params['application'])

                if params['application'] == 'Any':
                    if params['protocol']:
                        zd.s.type_text(locs['loc_restricted_ipv6_rule_protocol_textbox'],
                                       params['protocol'])
                        if params['protocol'] == '58':
                            #Need to call key_up to trigger onkeyup event,  
                            #which will enable edit icmp type if protocol is 58.
                            zd.s.key_up(locs['loc_restricted_ipv6_rule_protocol_textbox'], '8')

                    if params['destination_port']:
                        zd.s.type_text(locs['loc_restricted_ipv6_rule_dstport_textbox'],
                                       params['destination_port'])
                        
                    #When protocol is 58(ICMPV6), then icmp_type can be edit.
                    if params['icmp_type'] and params['protocol'] == '58':
                        zd.s.type_text(locs['loc_restricted_ipv6_rule_icmptype_textbox'], params['icmp_type'])

        zd.s.click_and_wait(locs['loc_restricted_ipv6_rule_ok_button'])
        time.sleep(5)


    except Exception, e:
        logging.info("Error in adding the restricted ipv6 '%s'. " % params['destination_addr'] + e.message)
        raise

    logging.debug("Restricted IPV6 '%s' was added successfully." % params['destination_addr'])

def _get_page_range_and_total_number_of_profiles(zd):
    total_info = zd.s.get_text(info['total_profiles_span'])
    if not total_info:
        time.sleep(1)
        total_info = zd.s.get_text(info['total_profiles_span'])

    pat = "(\d+)-(\d+) \((\d+)\)"
    match_obj = re.findall(pat, total_info)

    if match_obj:
        from_idx, to_idx, total = match_obj[0]

    else:
        raise Exception("Cannot get the total number of rows in generated hotspot table")

    return from_idx, to_idx, total
