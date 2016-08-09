'''
Generated Guest Passes table headers:
['full_name',
 'expire_time',
 'created_by',
 'shared_guestpass',
 'wlan']
'''
import logging
import re
import time
import os

from RuckusAutoTest.common.DialogHandler import (DialogManager, BaseDialog, StandardDialog)

from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.common.DialogHandler import (
    DialogManager, BaseDialog, application
)
from RuckusAutoTest.components.resources.ZDWebUIResource import *
from RuckusAutoTest.common import lib_Constant as constant
from RuckusAutoTest.components.lib.zd.release_compare import older_than_release

DEFAULT_GUEST_ACCESS_NAME = 'Guest_Access_Default'
#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
def get_guestpass_by_name(zd, guest_name):
    '''
    '''
    return _get_guestpass_by(zd, dict(full_name = guest_name))


def get_all_guestpasses_total_numbers(zd, timeout = 150, is_refresh = False):
    _nav_to_mon_guestpass(zd)
    locator = info['total_guestpasses_span']
    zd._wait_for_element(locator, timeout = timeout, is_refresh = is_refresh)
    return zd._get_total_number(locator, 'guest')

#@author: yuyanan @since: 2015-4-2 @change:9.10 new feature
def get_all_selfguestpasses(zd,key='full_name'):
    '''
    '''
    all_guespass_list = _get_all_selfguestpasses(zd)
    return list_to_dict(all_guespass_list, key)


def get_all_guestpasses(zd):
    '''
    '''
    return list_to_dict(_get_all_guestpasses(zd), 'full_name')

def generate_shared_guestpass(zd, info):
    generate_guestpass(zd, **info)

#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------

info = dict(
    # Configure -> Guest Access
    guestpass_auth_radio = "//input[@id='guest-auth-guestpass']",
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#    guestpass_shared_checkbox = "//input[@id='shared-guestpass']",
    guestpass_auth_none_radio = "//input[@id='guest-auth-none']",
    term_of_use_checkbox = "//input[@id='guest-show-tou']",
    terms_textbox = "//textarea[@id='tou']",
    redirect_orig_checkbox = "//input[@id='guest-redirect-orig']",
    redirect_url_checkbox = "//input[@id='guest-redirect-url']",
    redirect_url_textbox = "//input[@id='redirect-url']",
    apply_guest_btn = "//input[@id='apply-guest']",
    title_textbox = "//input[@id='guest-title']",
 
    # Guest Pass Generation
    guestpass_url_span = "//span[@id='guestpass-url']",
    auth_server_option = "//select[@id='authsvr']",
    guestpass_apply_button = "//input[@id='apply-guestpass']",
    countdown_by_issued_radio = "//input[@id='guest-countdown-by-issued']",
    countdown_by_used_radio = "//input[@id='guest-countdown-by-used']",
    guestvalid_textbox = "//input[@id='guest-valid']",

    # Restricted Access subnet
    open_list = "//tr[@id='restricted-subnet']/th/a",
    create_rule = "//span[@id='new-rule']",
    select_all_checkbox = "//input[@id='rule-sall']",
    advanced_option_anchor = "//div[@id='actions-rule']/a",
    delete_button = "//input[@id='del-rule']",

    edit_a_rule = "//table[@id='rule']//tr[td='%s']//span[text()='Edit']",
    clone_a_rule = "//table[@id='rule']//tr[td='%s']//span[text()='Clone']",
    check_a_rule = "//table[@id='rule']//tr[td='%s']//input",

    rule_order = "//select[@id='rule-id']",
    rule_description = "//input[@id='rule-description']",
    rule_action = "//select[@id='rule-action']",
    rule_dst_addr = "//input[@id='rule-dst-addr']",
    rule_application = "//select[@id='rule-app']",
    rule_protocol = "//input[@id='rule-protocol']",
    rule_dst_port = "//input[@id='rule-dst-port']",
    rule_save_button = "//input[@id='ok-rule']",
    rule_cancel_button = "//input[@id='cancel-rule']",

    rule_row = "//table[@id='rule']//tr[td=%s]/td[%s]",
    
    # Restricted IPV6 Access
    open_ipv6_list = "//tr[@id='restricted-subnet6']/th/a",
    create_ipv6_rule = "//span[@id='new-rule6']",
    select_all_ipv6_checkbox = "//input[@id='rule6-sall']",
    advanced_ipv6_option_anchor = "//div[@id='actions-rule6']/a",
    delete_ipv6_button = "//input[@id='del-rule6']",

    edit_a_ipv6_rule = "//table[@id='rule6']//tr[td='%s']//span[text()='Edit']",
    clone_a_ipv6_rule = "//table[@id='rule6']//tr[td='%s']//span[text()='Clone']",
    check_a_ipv6_rule = "//table[@id='rule6']//tr[td='%s']//input",

    ipv6_rule_order = "//select[@id='rule6-id']",
    ipv6_rule_description = "//input[@id='rule6-description']",
    ipv6_rule_action = "//select[@id='rule6-action']",
    ipv6_rule_dst_addr = "//input[@id='rule6-dst-addr']",
    ipv6_rule_application = "//select[@id='rule6-app']",
    ipv6_rule_protocol = "//input[@id='rule6-protocol']",
    ipv6_rule_dst_port = "//input[@id='rule6-dst-port']",
    ipv6_rule_icmp_type = "//input[@id='rule6-icmp-type']",
    
    ipv6_rule_save_button = "//input[@id='ok-rule6']",
    ipv6_rule_cancel_button = "//input[@id='cancel-rule6']",

    ipv6_rule_row = "//table[@id='rule6']//tr[td=%s]/td[%s]",

    guestpass_printout_sample = "//fieldset/table[@id='gprint']/../p/a",
    create_gprint = "//span[@id='new-gprint']",
    edit_gprint = "//table[@id='gprint']//tr[td='%s']//span[text()='Edit']",
    clone_gprint = "//table[@id='gprint']//tr[td='%s']//span[text()='Clone']",
    preview_gprint = "//table[@id='gprint']//tr[td='%s']//span[text()='Preview']",
    check_gprint = "//table[@id='gprint']//tr[td='%s']//input",
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    gprint_name = "//input[@id='print_name']",
    gprint_description = "//input[@id='description']",
    filename_uploadgprint = "//input[@id='filename-uploadgprint']",
    uploaded_uploadgprint = "//span[@id='uploaded-uploadgprint']",
    error_uploadgprint = "//span[@id='error-uploadgprint']",
    perform_uploadgprint = "//input[@id='perform-uploadgprint']",
    cancel_uploadgprint = "//input[@id='cancel-uploadgprint']",
    ok_gprint = "//input[@id='ok-gprint']",
    cancel_gprint = "//input[@id='cancel-gprint']",
    show_more_gprint = "//input[@id='showmore-gprint']",
    delete_gprint = "//input[@id='del-gprint']",

    gprint_filter = "//table[@id='gprint']//tr[@class='t_search']/td/span",

    gprint_info_by_row = "//table[@id='gprint']//tr[%s]/td[%s]",

    # LOCATORS_MON_GENERATED_GUEST_ACCESS
    guestpass_tbl_loc = "//table[@id='guest']",
    guestpass_tbl_nav_loc = "//table[@id='guest']/tfoot",
    guestpass_tbl_filter_txt = "//table[@id='guest']/tfoot//input[@type='text']",
    
    # LOCATORS_MON_GENERATED_SELF_SERVICE_GUEST_ACCESS
    selfguestpass_tbl_loc = "//table[@id='selfguest']",
    selfguestpass_tbl_nav_loc = "//table[@id='selfguest']/tfoot",
    selfguestpass_tbl_filter_txt = "//table[@id='selfguest']/tfoot//input[@type='text']",
    


    generated_guestpasses_span = "//span[contains(@id,'monitor_guests')]" ,

    guestpass_row_with_id = "//table[@id='guest']//tr[@idx='%s']/td[%s]",
    guestpass_row_with_guest_name = "//table[@id='guest']//tr/td[text()='%s']/../td[%s]",
    column_id = {'checkbox': 1,
                 'guestname': 2,
                 'remarks': 3,
                 'expires': 4,
                 'creator': 5,
                 'wlan': 6,
                 },

    guestpass_showmore_button = "//input[contains(@id,'showmore-guest')]",
    guestpass_nextguest_image = "//img[@id='next-guest']",
    guestpass_guestall_checkbox = "//input[contains(@id,'guest-sall')]",
    guestpass_guestdel_button = "//input[contains(@id,'del-guest')]",
    guestpass_guestdelall_button = "//input[contains(@id,'delall-guest')]",
    total_guestpasses_span = "//table[@id='guest']//div[contains(@class,'actions')]/span",
    guestpass_search_box = "//input[@id='search-guest']",
    
    #Delete Self Service Guestpass
    selfguestpass_guestdel_button = "//input[contains(@id,'del-selfguest')]",
    selfguestpass_guestall_checkbox = "//input[contains(@id,'selfguest-sall')]",
    total_selfguestpasses_span = "//table[@id='selfguest']//div[contains(@class,'actions')]/span",
    selfguestpass_guestdelall_button = "//input[contains(@id,'delall-selfguest')]",

    # LOCATORS_GUEST_ACCESS_GENERATION
    # Guest Information page
    username_textbox = "//input[@id='username']",
    password_textbox = "//input[@name='password']",
    login_button = "//input[@name='ok']",

    single_radio = "//input[@id='single']",
    multiple_radio = "//input[@id='multiple']",

    dialog_expire_span = "//span[@id='expire']",
    #dialog_pass_div = "//div[@id='guestpass']",
    dialog_pass_div = "//div[@id='scene_single']//div[@class='key']",
    loginfailed_div = "//div[@id='loginfailed']",
    printout_option = "//select[@id='guestPrintList']",
    print_instruction_anchor = "//a[text()='Print Instructions']",
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    #guest_name_text = "//th[contains(text(), 'the generated guest pass')]/strong",
    guest_name_text = "//div[@id='scene_single']//div[@class='text']/p",

    fullname_textbox = "//input[@id='fullname']",
    duration_textbox = "//input[@name='duration']",
    duration_unit_option = "//select[@id='duration-unit']",
    guest_wlan_option = "//select[@id='guest-wlan']",
    #JLUH@20140423, modified by the 9.8 changed.
    guest_email_option = "//input[@id='email']",
    guest_sent_out_email_button = "//button[@id='single_email']",
    guest_multi_email_progress_div = "//div[@id='loaded']",
    guest_sent_out_multi_email_button = "//button[@id='multi_email']",
    remarks_textarea = "//textarea[@name='remarks']",
    key_textbox = "//input[@id='key']",

    number_profile_textbox = "//input[@id='number']",
    profile_file_textbox = "//input[@id='file-batchpass']",
    text_batchpass = "//span[@id='text-batchpass']",
    download_example = "//a[text()='download']",
    print_all_instruction_anchor = "//a[text()='Print All Instructions']",
    download_generated_guestpass = "//a[text()='here']",

    error_text = 'The uploaded profile does not contain correct information. Please try another file.',
    uploading_text = 'Uploading',
    uploaded_text = 'guest passes created. Click Next button to proceed.',

    next_button = "//input[@value='Next >']",
    show_existing_guestpass_link = "//a[text()='Show existing guest passes']",

    expire_cell = "//td[contains(@id,'expire')]",
    print_instruction_link = "//td[@id='expire%s']//..//a[text()='Print']",
)

guestpass_info = {}

def get_server_list_can_be_selected(zd):
    _nav_to_cfg_guestpass(zd)
    return zd.s.get_select_options(info['auth_server_option'])

def _nav_to_mon_guestpass(zd):
    return zd.navigate_to(zd.MONITOR, zd.MONITOR_GENERATED_GUESTPASSES)


def _nav_to_cfg_guestpass(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)


def _get_guestpass_by(zd, match, verbose=False):
    '''
    '''
    _nav_to_mon_guestpass(zd)
    return wgt.get_first_row_by(
        zd.s, info['guestpass_tbl_loc'], info['guestpass_tbl_nav_loc'], match,
        filter=info['guestpass_tbl_filter_txt'], verbose=verbose,
    )

#@author: yuyanan @since: 2015-4-2 @change:9.10 new feature
def _get_all_selfguestpasses(zd):
    '''
    '''
    _nav_to_mon_guestpass(zd)
    return wgt.get_tbl_rows(
        zd.s, info['selfguestpass_tbl_loc'], info['selfguestpass_tbl_nav_loc']
    )
    
def _get_all_guestpasses(zd):
    '''
    '''
    _nav_to_mon_guestpass(zd)
    return wgt.get_tbl_rows(
        zd.s, info['guestpass_tbl_loc'], info['guestpass_tbl_nav_loc']
    )



###
##
## Restricted Sub net Access
##
###

def _log_to_the_page(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)

def _get_guest_access_config(zd,guest_access_name = DEFAULT_GUEST_ACCESS_NAME):
    authentication = None
    authentication_server = None
    expire_days = None
    redirection = None
    terms_of_use = None
    terms = None
    title = None
    url = None
    validity_period = None
    multiple_users_to_share_a_single_guest_pass = None

    #@author:yuyanan @since: 2015-4-2 @change:9.10 newfeature:get access config according to guest name
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    edit_span = Locators['loc_cfg_guest_access_edit_span'] % guest_access_name
    time.sleep(2)
    zd.s.click_and_wait(edit_span)
            
    if zd.s.is_checked(info['guestpass_auth_radio']):
        authentication = 'Use guest pass authentication.'
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#        if zd.s.is_checked(info['guestpass_shared_checkbox']):
#            multiple_users_to_share_a_single_guest_pass = 'Allowed'
#        else:
#            multiple_users_to_share_a_single_guest_pass = 'Disallowed'
    else:
        authentication = 'No Authentication.'
        
    if zd.s.is_checked(info['term_of_use_checkbox']):
        terms_of_use = 'Enabled'
        terms = zd.s.get_value(info['terms_textbox'])
    else:
        terms_of_use = 'Disabled'
    
    if zd.s.is_checked(info['redirect_orig_checkbox']):
        redirection = 'To the URL that the user intends to visit.'
    if zd.s.is_checked(info['redirect_url_checkbox']):
        redirection = 'To the following URL.'
        url = zd.s.get_value(info['redirect_url_textbox'])
    
    authentication_server = zd.s.get_selected_label(info['auth_server_option'])
    if zd.s.is_checked(info['countdown_by_issued_radio']):
        validity_period = 'Effective from the creation time.'
    if zd.s.is_checked(info['countdown_by_used_radio']):
        validity_period = 'Effective from first use.'
        expire_days = zd.s.get_value(info['guestvalid_textbox'])
    
    title = zd.s.get_value(info['title_textbox'])    
    
    config = {'authentication': authentication,
              'authentication_server': authentication_server,
              'expire_days': expire_days,
              'redirection': redirection,                  
              'terms_of_use': terms_of_use,
              'terms': terms,
              'title': title,
              'url': url,
              'validity_period': validity_period}

    zd.s.click_and_wait(Locators['loc_cfg_guest_access_cancel'])
    time.sleep(2)

    return config

def __set_restricted_subnet(zd, _rule_info):
    rule_info = {'order': '', 'description': '', 'action': '', 'dst_addr': '',
                 'application': '', 'protocol': '', 'dst_port': ''}
    rule_info.update(_rule_info)


    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#    edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
#    time.sleep(2)
    #@author: Anzuo, should not edit before set rule, or the webpage will be refreshed and script cannot find rule action
#    zd.s.click_and_wait(edit_span)

    if rule_info['order']:
        zd.s.select_option(info['rule_order'], rule_info['order'])
    if rule_info['description']:
        zd.s.type_text(info['rule_description'], rule_info['description'])
    if rule_info['action']:
        zd.s.select_option(info['rule_action'], rule_info['action'])
    if rule_info['dst_addr']:
        zd.s.type_text(info['rule_dst_addr'], rule_info['dst_addr'])

    if rule_info['application'] or rule_info['protocol'] or rule_info['dst_port']:
        if not zd.s.is_visible(info['rule_application']):
            zd.s.click_and_wait(info['advanced_option_anchor'])

    if rule_info['application']:
        zd.s.select_option(info['rule_application'], rule_info['application'])
        zd.s.click_and_wait(info['rule_application'])
    if rule_info['protocol']:
        zd.s.type_text(info['rule_protocol'], rule_info['protocol'])
    if rule_info['dst_port']:
        zd.s.type_text(info['rule_dst_port'], rule_info['dst_port'])

    zd.s.click_and_wait(info['rule_save_button'])

#    zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
    time.sleep(2)

#@author:yuyanan @since: 2015-3-25 @change:9.10 new feature: get access config according to guest name
def get_guest_access_config(zd,guest_access_name = DEFAULT_GUEST_ACCESS_NAME):
    _nav_to_cfg_guestpass(zd)
    return _get_guest_access_config(zd,guest_access_name)

def create_restricted_subnet_entries(zd, rule_info):
    """
    Create one or more Guest ACL rule
    @param zd: the reference to the Zone Director object
    @param rule_info: a dictionary or a list of dictionary which holds information if one or more ACLs
    """
    if type(rule_info) == dict:
        rule_list = [rule_info]
    elif type(rule_info) == list:
        rule_list = rule_info
    else:
        logging.info("Incorrect data type of [rule_info] given: %s" % type(rule_info))
        return

    try:
        _log_to_the_page(zd)
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        if not zd.s.is_element_present(edit_span):
            return
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        zd.s.click_and_wait(edit_span)
        zd.s.click_and_wait(info['open_list'])

        for rule in rule_list:
            zd.s.click_and_wait(info['create_rule'])
            __set_restricted_subnet(zd, rule)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when creating a new Guest ACL rule [%s]" % e.message)
        raise

    logging.info("Finish creating new Guest ACL rule(s)")


def edit_restricted_subnet_entry(zd, new_rule_info, order = '', dst_addr = ''):
    """
    Edit an existing Guest ACL rule
    @param zd: the reference to the Zone Director object
    @param order: the order of the rule is going to be modified
    @param dst_addr: the destination address of the rule is going to be modified
    @param new_rule_info: new information is going to be applied to the rule
    """
    rule_info = {'order': '', 'description': '', 'action': '', 'dst_addr': '',
                 'application': '', 'protocol': '', 'dst_port': ''}
    rule_info.update(new_rule_info)

    if not order and not dst_addr:
        logging.info("No rule is going to be modified")
        return

    try:
        _log_to_the_page(zd)
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        if not zd.s.is_element_present(edit_span):
            return
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        zd.s.click_and_wait(edit_span)
        zd.s.click_and_wait(info['open_list'])

        if order:
            loc = info['edit_a_rule'] % order
        else:
            loc = info['edit_a_rule'] % dst_addr

        zd.s.click_and_wait(loc)
        __set_restricted_subnet(zd, rule_info)
        
        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)

    except Exception, e:
        logging.info("Catch the error when modifying a Guest ACL rule [%s]" % e.message)
        raise

    logging.info("Finish modifying a Guest ACL rule")


def clone_restricted_subnet_entry(zd, new_rule_info, order = '', dst_addr = ''):
    """
    Edit an existing Guest ACL rule
    @param zd: the reference to the Zone Director object
    @param order: the order of the rule is going to be modified
    @param dst_addr: the destination address of the rule is going to be modified
    @param new_rule_info: new information is going to be applied to the rule
    """
    rule_info = {'order': '', 'description': '', 'action': '', 'dst_addr': '',
                 'application': '', 'protocol': '', 'dst_port': ''}
    rule_info.update(new_rule_info)

    if not order and not dst_addr:
        logging.info("No rule is going to be cloned")
        return

    try:
        _log_to_the_page(zd)
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        if not zd.s.is_element_present(edit_span):
            return
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        zd.s.click_and_wait(edit_span)
        
        zd.s.click_and_wait(info['open_list'])

        if order:
            loc = info['clone_a_rule'] % order
        else:
            loc = info['clone_a_rule'] % dst_addr

        zd.s.click_and_wait(loc)
        __set_restricted_subnet(zd, rule_info)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when cloning a Guest ACL rule [%s]" % e.message)
        raise

    logging.info("Finish cloning a Guest ACL rule")


def get_restricted_subnet_entry(zd, order = '', dst_addr = ''):
    """ Retrieve information of an existing Guest ACL rule
    @param zd: reference to the Zone Director object
    @param order: identify the ACL rule by order number
    @param dst_addr: identify the ACL rule by destination address
    """
    if not order and not dst_addr:
        logging.info("No rule is returned")
        return None

    if order:
        key = order

    else:
        key = dst_addr

    entry = dict()
    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        if not zd.s.is_element_present(edit_span):
            return
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        zd.s.click_and_wait(edit_span)
        zd.s.click_and_wait(info['open_list'])
        
        
        zd.s.click_and_wait(info['advanced_option_anchor'])

        entry['order'] = order if order else zd.s.get_text(info['rule_row'] % (key, 2))
        entry['description'] = zd.s.get_text(info['rule_row'] % (key, 3))
        entry['action'] = zd.s.get_text(info['rule_row'] % (key, 4))
        entry['dst_addr'] = dst_addr if dst_addr else zd.s.get_text(info['rule_row'] % (key, 5))
        entry['application'] = zd.s.get_text(info['rule_row'] % (key, 6))
        entry['protocol'] = zd.s.get_text(info['rule_row'] % (key, 7))
        entry['dst_port'] = zd.s.get_text(info['rule_row'] % (key, 8))

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_cancel'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when reading a Guest ACL rule [%s]" % e.message)
        raise

    return entry


def get_all_restricted_subnet_entries(zd):
    """ Retrieve information of all non-default ACL rules
    @param zd: reference to the Zone Director object
    """
    acl_list = []

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        #@author: Jane.Guo @since: 2013-12 ZF-6432
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        if not zd.s.is_element_present(edit_span):
            return acl_list
        zd.s.click_and_wait(edit_span)
        zd.s.click_and_wait(info['open_list'])
        
        zd.s.click_and_wait(info['advanced_option_anchor'])

        order = 1
        while zd.s.is_element_present(info['rule_row'] % (order, 2), timeout = 2):
            if zd.s.is_element_present(info['check_a_rule'] % order, timeout = 2):
                entry = {}
                entry['order'] = str(order)
                entry['description'] = zd.s.get_text(info['rule_row'] % (order, 3))
                entry['action'] = zd.s.get_text(info['rule_row'] % (order, 4))
                entry['dst_addr'] = zd.s.get_text(info['rule_row'] % (order, 5))
                entry['application'] = zd.s.get_text(info['rule_row'] % (order, 6))
                entry['protocol'] = zd.s.get_text(info['rule_row'] % (order, 7))
                entry['dst_port'] = zd.s.get_text(info['rule_row'] % (order, 8))
                acl_list.append(entry)
            order += 1
            
        zd.s.click_and_wait(Locators['loc_cfg_guest_access_cancel'])
        time.sleep(2)

    except Exception, e:
        logging.info("Catch the error when reading the Guest ACL rules [%s]" % e.message)
        raise

    return acl_list


def remove_restricted_subnet_entry(zd, order = '', dst_addr = ''):
    """ Remove an existing Guest ACL rule from the ZD """
    if not order and not dst_addr:
        logging.info("No rule is removed")
        return None

    if order:
        key = order

    else:
        key = dst_addr

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        if not zd.s.is_element_present(edit_span):
            return
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        zd.s.click_and_wait(edit_span)
        
        zd.s.click_and_wait(info['open_list'])
        
        zd.s.choose_ok_on_next_confirmation()
        #@author: chentao @since: 2013-10-12 check if restricted subnets exist,if not, do nothing.
        if not zd.s.is_element_present(info['check_a_rule'] % key):
            zd.s.click_and_wait(Locators['loc_cfg_guest_access_cancel'])
            time.sleep(2)
            return
        else:    
            zd.s.click_and_wait(info['check_a_rule'] % key)
            zd.s.click_and_wait(info['delete_button'])
        #@author: chentao @since: 2013-10-12 check if restricted subnets exist,if not, do nothing.
        if zd.s.is_confirmation_present(5):
            msg = zd.s.get_confirmation()
            logging.info("Catch the confirmation [%s]" % msg)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when removing a Guest ACL rule [%s]" % e.message)
        raise


def remove_all_restricted_subnet_entries(zd):
    """ Remove all Guest ACL rules except the default rule from the ZD """

    acl_list = get_all_restricted_subnet_entries(zd)
    logging.info("Remove all Guest ACL rules except the default rule from the ZD")
    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        if not zd.s.is_element_present(edit_span):
            return
        zd.s.click_and_wait(edit_span)
        
        zd.s.click_and_wait(info['open_list'])
        
        fnd = False
        for acl in acl_list:
            order = acl['order']
            dst_addr = acl['dst_addr']
            if order == '1':
                continue
            #Updated by cwang because of 172.16.0.0 is webserver subnet.
            #['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
            if dst_addr in ['10.0.0.0/8', '192.168.0.0/16']:
                continue

            zd.s.click_if_not_checked(info['check_a_rule'] % order)
            fnd =  True


        if fnd:
            zd.s.choose_ok_on_next_confirmation()
            zd.s.click_and_wait(info['delete_button'])
        else:
            return

        if zd.s.is_confirmation_present(5):
            msg = zd.s.get_confirmation()
            logging.info("Catch the confirmation [%s]" % msg)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when removing all Guest ACL rules [%s]" % e.message)
        raise

###
##
## Restricted IPV6 Access
##
###

def __set_restricted_subnet_ipv6(zd, _rule_info):
    rule_info = {'order': '', 'description': '', 'action': '', 'dst_addr': '',
                 'application': 'Any', 'protocol': 'Any', 'dst_port': '', 'icmp_type': '',}
    rule_info.update(_rule_info)

    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#    edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
#    time.sleep(2)
    #@author: Anzuo, should not edit before set rule, or the webpage will be refreshed and script cannot find rule action
#    zd.s.click_and_wait(edit_span)
        
    if rule_info['order']:
        zd.s.select_option(info['ipv6_rule_order'], rule_info['order'])
    if rule_info['description']:
        zd.s.type_text(info['ipv6_rule_description'], rule_info['description'])
    if rule_info['action']:
        zd.s.select_option(info['ipv6_rule_action'], rule_info['action'])
    if rule_info['dst_addr']:
        zd.s.type_text(info['ipv6_rule_dst_addr'], rule_info['dst_addr'])
        
    #Set advanced options.
    if rule_info['application'] or rule_info['protocol'] or rule_info['dst_port']:
        if not zd.s.is_visible(info['ipv6_rule_application']):
            zd.s.click_and_wait(info['advanced_ipv6_option_anchor'])
            
    if rule_info['application']:
        zd.s.select_option(info['ipv6_rule_application'], rule_info['application'])
    
    if rule_info['application'].lower() == 'any':
        #Default of application is 'Any'.
        #If application is not any, protocl, dst port and icmp type are not editable.
        if rule_info['protocol']:
            if not zd.s.is_editable(info['ipv6_rule_protocol']):
                raise Exception('The "Protocol" field could not be edited')
            zd.s.type_text(info['ipv6_rule_protocol'], rule_info['protocol'])
            if rule_info['protocol'] == '58':
                #Need to call key_up to trigger onkeyup event,  
                #which will enable edit icmp type if protocol is 58.
                zd.s.key_up(info['ipv6_rule_protocol'], '8')
        if rule_info['dst_port'] and rule_info['protocol'].lower() == 'any':
            #When protocol is specified, destination port is not editable.
            if not zd.s.is_editable(info['ipv6_rule_dst_port']):
                raise Exception('The "Destination Port" field could not be edited')
            zd.s.type_text(info['ipv6_rule_dst_port'], rule_info['dst_port'])
        #When protocol is 58(ICMPV6), then icmp_type can be edit.
        if rule_info['icmp_type'] and rule_info['protocol'] == '58':
            if not zd.s.is_editable(info['ipv6_rule_icmp_type']):
                raise Exception('The "ICMP Type" field could not be edited')
            zd.s.type_text(info['ipv6_rule_icmp_type'], rule_info['icmp_type'])

    zd.s.click_and_wait(info['ipv6_rule_save_button'])

#    zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
    time.sleep(2)


def create_restricted_subnet_entries_ipv6(zd, rule_info):
    """
    Create one or more Guest ACL rule
    @param zd: the reference to the Zone Director object
    @param rule_info: a dictionary or a list of dictionary which holds information if one or more ACLs
    """
    if type(rule_info) == dict:
        rule_list = [rule_info]
    elif type(rule_info) == list:
        rule_list = rule_info
    else:
        logging.info("Incorrect data type of [rule_info] given: %s" % type(rule_info))
        return

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        zd.s.click_and_wait(edit_span)
        zd.s.click_and_wait(info['open_ipv6_list'])
        
        for rule in rule_list:
            logging.info("Creating ipv6 rule order %s-%s" % (rule['order'], rule['description']))
            zd.s.click_and_wait(info['create_ipv6_rule'])
            __set_restricted_subnet_ipv6(zd, rule)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when creating a new Guest IPV6 ACL rule [%s]" % e.message)
        raise

    logging.info("Finish creating new Guest IPV6 ACL rule(s)")


def edit_restricted_subnet_entry_ipv6(zd, new_rule_info, order = '', dst_addr = ''):
    """
    Edit an existing Guest ACL rule
    @param zd: the reference to the Zone Director object
    @param order: the order of the rule is going to be modified
    @param dst_addr: the destination address of the rule is going to be modified
    @param new_rule_info: new information is going to be applied to the rule
    """
    rule_info = {'order': '', 'description': '', 'action': '', 'dst_addr': '',
                 'application': '', 'protocol': '', 'dst_port': '', 'icmp_type': '',}
    rule_info.update(new_rule_info)

    if not order and not dst_addr:
        logging.info("No ipv6 rule is going to be modified")
        return

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        zd.s.click_and_wait(edit_span)
        #@ZJ 20141030 ZF-10544
        zd.s.click_and_wait(info['open_ipv6_list'])
#        zd.s.click_and_wait(info['open_list'])
        
        if order:
            loc = info['edit_a_ipv6_rule'] % order
        else:
            loc = info['edit_a_ipv6_rule'] % dst_addr

        zd.s.click_and_wait(loc)
        __set_restricted_subnet_ipv6(zd, rule_info)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when modifying a Guest IPV6 ACL rule [%s]" % e.message)
        raise

    logging.info("Finish modifying a Guest IPV6 ACL rule")


def clone_restricted_subnet_entry_ipv6(zd, new_rule_info, order = '', dst_addr = ''):
    """
    Edit an existing Guest ACL rule
    @param zd: the reference to the Zone Director object
    @param order: the order of the rule is going to be modified
    @param dst_addr: the destination address of the rule is going to be modified
    @param new_rule_info: new information is going to be applied to the rule
    """
    rule_info = {'order': '', 'description': '', 'action': '', 'dst_addr': '',
                 'application': '', 'protocol': '', 'dst_port': '', 'icmp_type': '',}
    rule_info.update(new_rule_info)

    if not order and not dst_addr:
        logging.info("No ipv6 rule is going to be cloned")
        return

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        zd.s.click_and_wait(edit_span)
        #@ZJ 20141030 ZF-10544
        zd.s.click_and_wait(info['open_ipv6_list'])
#        zd.s.click_and_wait(info['open_list'])
        
        if order:
            loc = info['clone_a_ipv6_rule'] % order
        else:
            loc = info['clone_a_ipv6_rule'] % dst_addr

        zd.s.click_and_wait(loc)
        __set_restricted_subnet_ipv6(zd, rule_info)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when cloning a Guest IPV6 ACL rule [%s]" % e.message)
        raise

    logging.info("Finish cloning a Guest IPV6 ACL rule")


def get_restricted_subnet_entry_ipv6(zd, order = '', dst_addr = ''):
    """ Retrieve information of an existing Guest ACL rule
    @param zd: reference to the Zone Director object
    @param order: identify the ACL rule by order number
    @param dst_addr: identify the ACL rule by destination address
    """
    if not order and not dst_addr:
        logging.info("No ipv6 rule is returned")
        return None

    if order:
        key = order

    else:
        key = dst_addr

    entry = dict()
    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        zd.s.click_and_wait(edit_span)
        #@ZJ 20141030 ZF-10544
        zd.s.click_and_wait(info['open_ipv6_list'])
#        zd.s.click_and_wait(info['open_list'])
        
        zd.s.click_and_wait(info['advanced_ipv6_option_anchor'])

        entry['order'] = order if order else zd.s.get_text(info['ipv6_rule_row'] % (key, 2))
        entry['description'] = zd.s.get_text(info['ipv6_rule_row'] % (key, 3))
        entry['action'] = zd.s.get_text(info['ipv6_rule_row'] % (key, 4))
        entry['dst_addr'] = dst_addr if dst_addr else zd.s.get_text(info['ipv6_rule_row'] % (key, 5))
        entry['application'] = zd.s.get_text(info['ipv6_rule_row'] % (key, 6))
        entry['protocol'] = zd.s.get_text(info['ipv6_rule_row'] % (key, 7))
        entry['dst_port'] = zd.s.get_text(info['ipv6_rule_row'] % (key, 8))
        entry['icmp_type'] = zd.s.get_text(info['ipv6_rule_row'] % (key, 9))

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_cancel'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when reading a Guest IPV6 ACL rule [%s]" % e.message)
        raise

    return entry


def get_all_restricted_subnet_entries_ipv6(zd):
    """ Retrieve information of all non-default ACL rules
    @param zd: reference to the Zone Director object
    """
    acl_list = []

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        zd.s.click_and_wait(edit_span)
        
        zd.s.click_and_wait(info['advanced_ipv6_option_anchor'])

        order = 1
        while zd.s.is_element_present(info['ipv6_rule_row'] % (order, 2), timeout = 2):
            if zd.s.is_element_present(info['check_a_ipv6_rule'] % order, timeout = 2):
                entry = {}
                entry['order'] = str(order)
                entry['description'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 3))
                entry['action'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 4))
                entry['dst_addr'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 5))
                entry['application'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 6))
                entry['protocol'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 7))
                entry['dst_port'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 8))
                entry['icmp_type'] = zd.s.get_text(info['ipv6_rule_row'] % (order, 9))
                acl_list.append(entry)
            order += 1

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_cancel'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when reading the Guest ACL rules [%s]" % e.message)
        raise

    return acl_list


def remove_restricted_subnet_entry_ipv6(zd, order = '', dst_addr = ''):
    """ Remove an existing Guest ACL rule from the ZD """
    if not order and not dst_addr:
        logging.info("No ipv6 rule is removed")
        return None

    if order:
        key = order

    else:
        key = dst_addr

    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        if not zd.s.is_element_present(edit_span):
            return
        #@author: chen.tao 2013-12-19, to fix bug ZF-6495
        zd.s.click_and_wait(edit_span)
        
        #@ZJ 20141030 ZF-10544
        zd.s.click_and_wait(info['open_ipv6_list'])
#        zd.s.click_and_wait(info['open_list'])
        
        zd.s.choose_ok_on_next_confirmation()
        zd.s.click_and_wait(info['check_a_ipv6_rule'] % key)
        zd.s.click_and_wait(info['delete_ipv6_button'])

        if zd.s.is_confirmation_present(5):
            msg = zd.s.get_confirmation()
            logging.info("Catch the confirmation [%s]" % msg)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when removing a Guest IPV6 ACL rule [%s]" % e.message)
        raise


def remove_all_restricted_subnet_entries_ipv6(zd):
    """ Remove all Guest ACL rules except the default rule from the ZD """
    logging.info("Remove all Guest ACL rules for ipv6 except the default rule from the ZD")
    try:
        _log_to_the_page(zd)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        #zj 2013-12-4 ZF-6432 add judgement
        if not zd.s.is_element_present(edit_span):
            return
        
        zd.s.click_and_wait(edit_span)
        #@ZJ 20141030 ZF-10544
        zd.s.click_and_wait(info['open_ipv6_list'])
#        zd.s.click_and_wait(info['open_list'])
        zd.s.choose_ok_on_next_confirmation()
        if zd.s.is_element_present(info['select_all_ipv6_checkbox']) and zd.s.is_visible(info['select_all_ipv6_checkbox']):
            zd.s.click_and_wait(info['select_all_ipv6_checkbox'])
            zd.s.click_and_wait(info['delete_ipv6_button'])

        if zd.s.is_confirmation_present(5):
            msg = zd.s.get_confirmation()
            logging.info("Catch the confirmation [%s]" % msg)

        zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
        time.sleep(2)
        
    except Exception, e:
        logging.info("Catch the error when removing all Guest IPV6 ACL rules [%s]" % e.message)
        raise
    
def verify_restricted_ipv6_access_gui_set_get(set_access_list, get_access_list):
    '''
    Verify restricted ipv6 access list between gui set and gui get.
    '''
    res_access_list = {}
    
    if len(set_access_list) != len(get_access_list):
        res_access_list['Count'] = "Expected:%s, Actual: %s" % (len(set_access_list), len(get_access_list))
    else:
        for index in range(0, len(set_access_list)):
            set_access = set_access_list[index]
            get_access = get_access_list[index]
            
            res_access = _compare_ipv6_rule(set_access, get_access)
            
            if res_access:
                res_access_list[index+1] = res_access
    
    return res_access_list
        
        
def _compare_ipv6_rule(rule_dict_1, rule_dict_2):
    '''
    Compare rule.
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
                        
            if value and value_2:
                if str(value).lower() != str(value_2).lower():
                    fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                    res_rule[key] = fail_msg
            elif value != value_2:
                    fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                    res_rule[key] = fail_msg
    
    if res_rule:
        return "Rule is different: %s" % res_rule
    else:
        return ""     

###
##
## Guest Pass Printout Customization
##
###
def download_guestpass_printout_sample(zd, sample_filename = 'guestpass_print.html'):
    _log_to_the_page(zd)

    time.sleep(4)
    return _download_single_file(zd, info['guestpass_printout_sample'], sample_filename)

def __cfg_guestpass_printout(zd, gprint_cfg):
    cfg = {'name': '', 'description': '', 'html_file':''}
    cfg.update(gprint_cfg)

    if cfg['name']:
        zd.s.type_text(info['gprint_name'], cfg['name'])

    if cfg['description']:
        zd.s.type_text(info['gprint_description'], cfg['description'])

    if cfg['html_file']:
        zd.s.type_text(info['filename_uploadgprint'], cfg['html_file'])
        t0 = time.time()
        while time.time() - t0 < 15:
            time.sleep(3)
            if zd.s.is_visible(info['uploaded_uploadgprint']):
                break

        if zd.s.is_visible(info['error_uploadgprint']):
            raise Exception(zd.s.get_text(info['error_uploadgprint']))

        zd.s.click_and_wait(info['perform_uploadgprint'])

    zd.s.click_and_wait(info['ok_gprint'])
    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())

def create_guestpass_printout(zd, gprint_cfg):
    """
    Create one or many customized Guest Pass Printout entries
    @param zd: reference to the ZD object
    @param gprint_cfg: a dictionary or a list of dictionary items which have the following keys:
    {'name':'', 'description':'', 'html_file': 'path to the customized guest pass printout file'}
    """
    if type(gprint_cfg) == list:
        gprint_cfg_list = gprint_cfg
    elif type(gprint_cfg) == dict:
        gprint_cfg_list = [gprint_cfg]
    else:
        logging.info("Incorrect data type of [gprint_cfg] given: %s" % type(gprint_cfg))
        return

    try:
        _log_to_the_page(zd)
        for cfg in gprint_cfg_list:
            if zd.s.is_element_disabled(info['create_gprint'], timeout = 1):
                logging.info("Unable to create more when the 'Create New' button is disabled.")
                raise

            zd.s.click_and_wait(info['create_gprint'])
            time.sleep(1)
            __cfg_guestpass_printout(zd, cfg)

    except Exception, e:
        logging.info("Catch the error when creating new Guest Pass Printout(s) [%s]" % e.message)
        raise

    logging.info("Finish creating %s new Guest Pass Printout(s)" % len(gprint_cfg_list))


def edit_guestpass_printout(zd, name, new_gprint_cfg):
    try:
        _log_to_the_page(zd)
        zd.s.click_and_wait(info['edit_gprint'] % name)
        time.sleep(1)
        __cfg_guestpass_printout(zd, new_gprint_cfg)

    except Exception, e:
        logging.info("Catch the error when editing a Guest Pass Printout [%s]: %s" % (name, e.message))
        raise

    logging.info("Finish editing the Guest Pass Printout [%s]" % name)


def clone_guestpass_printout(zd, name, new_gprint_cfg):
    try:
        _log_to_the_page(zd)
        zd.s.click_and_wait(info['clone_gprint'] % name)
        time.sleep(1)
        __cfg_guestpass_printout(zd, new_gprint_cfg)

    except Exception, e:
        logging.info("Catch the error [%s] when cloning from Guest Pass Printout [%s]" % (e.message, name))
        raise

    logging.info("Finish cloning a new Guest Pass Printout from [%s]" % name)


def get_list_of_guestpass_printout(zd, filter = ''):
    gprint_info = {'name': 2, 'description': 3}
    gprint_list = []

    try:
        _log_to_the_page(zd)

        if filter:
            zd.s.type_keys(info['gprint_filter'], filter)
            time.sleep(3)

        tr_idx = 1
        while True:
            try:
                gprint = {}
                for key, td_idx in gprint_info.items():
                    gprint[key] = zd.s.get_text(info['gprint_info_by_row'] % (tr_idx, td_idx))

            except Exception, e:
                if "not found" in e.message: break
                else: raise

            gprint_list.append(gprint)
            tr_idx += 1

    except Exception, e:
        logging.info("Catch the error [%s] when reading the list of the Guest Pass Printouts" % e.message)
        raise

    logging.info("Finish reading the list of the existing Guest Pass Printouts")
    return gprint_list


def remove_guestpass_printout(zd, gprint_name):
    """
    Remove the selected Guest Pass Printouts from the ZD
    @param zd: reference to the ZD object
    @param gprint_name: a string or a list of the strings represent names of the printouts
    """
    if type(gprint_name) == list:
        gprint_list = gprint_name

    elif type(gprint_name) == str:
        gprint_list = [gprint_name]

    else:
        logging.info("Incorrect data type of [gprint_name] given: %s" % type(gprint_name))
        return

    try:
        _log_to_the_page(zd)

        for name in gprint_list:
            zd.s.click_and_wait(info['check_gprint'] % name)
            time.sleep(0.5)

        zd.s.choose_ok_on_next_confirmation()
        zd.s.click_and_wait(info['delete_gprint'])
        time.sleep(1)

        if zd.s.is_confirmation_present(5):
            logging.info("Catch the confirmation [%s]" % zd.s.get_confirmation())

        if zd.s.is_alert_present(5):
            alert = zd.s.get_alert()
            logging.info("Catch the alert [%s]" % alert)
            raise Exception(alert)

    except Exception, e:
        logging.info("Catch the error [%s] when removing the Guest Pass Printout(s)" % e.message)
        raise

    logging.info("Finish removing the Guest Pass Printout(s)")


###
##
## Guestpass generation
##
###
def generate_guestpass(zd, **kwarg):
    """
    This method is used for getting the guestpass with the given username and password
    (on Authentication server or Local Database)
    """
    conf = {'type':'single',
            'guest_fullname':'',
            'duration':'',
            'duration_unit': '',
            'wlan': '',
            'remarks': '',
            'key': '',
            'is_shared': 'No',
            'auth_ser': 'Local Database',
            'username': '',
            'password': ''}
    conf.update(**kwarg)

    _perform_auth_to_generate_guestpass(zd, conf['username'], conf['password'], conf['is_shared'], conf['auth_ser'])
    
    try:
        if conf['type'] == 'single':
            _generate_single_guestpass(zd, **conf)
    
        elif conf['type'] == 'multiple':
            _generate_multiple_guestpass(zd, **conf)
    
        else:
            # Navigate to the ZoneDirector's url
            zd.do_login()
            zd.logout()
            raise Exception('Do not support for the "%s" creation type' % conf['type'])
        
    except Exception, ex:
            # Navigate to the ZoneDirector's url
            zd.do_login()
            zd.logout()
            #Jluh@20140428 updated by the 9.8 changed
            #@author: liangaihua,@since: 2015-2-16,@change: behavior change zf-12131
            #if 'email address is invalid' in ex.message:
            if 'email address is invalid' in ex.message or 'Email is invalid format'in ex.message:
                guestpass_info.update({'invalid_csv_file_email_alert': ex.message})

def _perform_auth_to_generate_guestpass(zd, username, password,
                                        is_shared = False, server = ''):
    """
    """
    zd.do_login()
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)
    time.sleep(2)

    # Enable "shared by multiple guests"
#    if is_shared == 'Yes':
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        #_set_shared_guest_pass(zd)

    # Select authentication server
    if server != '':
        _select_auth_server(zd, server)

    guestpass_url = zd.s.get_text(info['guestpass_url_span'])
    logging.info("Navigate to the guestpass url: '%s'" % guestpass_url)
    zd.s.open(guestpass_url)
    zd.s.wait_for_page_to_load(zd.conf['loadtime_open2'])

    logging.info("Fill authentication username '%s' and password '%s'" % (username, password))
    zd.s.type_text(info['username_textbox'], username)
    zd.s.type_text(info['password_textbox'], password)
    zd.s.click_and_wait(info['login_button'], 15)

    if zd.s.is_element_present(info['loginfailed_div'], 0.5):
        error_msg = zd.s.get_text(info['loginfailed_div'])
        logging.info("Error: %s" % error_msg)
        logging.info("Navigate to the ZoneDirector's url.")
        zd.do_login()
        zd.logout()
        raise Exception(error_msg)

def _generate_single_guestpass(zd, **kwarg):
    try:
        __generate_single_guestpass(zd, **kwarg)

    except Exception, e:
        raise Exception(e.message)

    # Get the expired time and the guest pass
    # update the guestpass_info for further usage
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    guest_name_all = zd.s.get_text(info['guest_name_text'])
    #u'Here is the generated guest pass for aa'
    guest_name = re.match('.*the generated guest pass for (.*)',guest_name_all).group(1)    
    
    gp_info = {'guest_name': guest_name,
               'guest_pass': zd.s.get_text(info['dialog_pass_div']),
               'expired_time': zd.s.get_text(info['dialog_expire_span'])}
    guestpass_info.update({'single_gp': gp_info})

    if kwarg.has_key('validate_gprints'):
        if kwarg['validate_gprints']:
            return # to stay on the current page for further processing

        else:
            logging.info("Get the guestpass and expired time")
            logging.info("The expired time is '%s'" % gp_info['expired_time'])
            logging.info("The guestpass is '%s'" % gp_info['guest_pass'])
            logging.info("The guest name is '%s'" % gp_info['guest_name'])

    # Finish generating guest pass
    logging.info("Navigate to the Zone Director's url")
    zd.do_login()
    zd.logout()


def _generate_multiple_guestpass(zd, **kwarg):
    """
    """
    #Jluh@20140428, updated by the 9.8 changed
    conf = {'duration': '',
            'duration_unit': '',
            'wlan': '',
            'is_shared': 'No',
            'number_profile': '',
            'profile_file': '',
            'username': '',
            'email': '',
            }
    conf.update(**kwarg)

    # Click to choice the creation type is multiple
    zd.s.click_and_wait(info['multiple_radio'])

    # Fill the information of the guest pass
    msg = "Fill the guest pass information --- \
           Duration: '%s', duration unit: '%s', number: '%s', profile file: '%s'"
    msg = msg % (conf['duration'], conf['duration_unit'], conf['number_profile'], conf['profile_file'])
    logging.info(msg)

    if conf['duration']:
        zd.s.type_text(info['duration_textbox'], conf['duration'])
    if conf['duration_unit']:
        zd.s.select_option(info['duration_unit_option'], conf['duration_unit'])
    if conf['wlan']:
        zd.s.select_option(info['guest_wlan_option'], conf['wlan'])
    if conf['number_profile']:
        zd.s.type_text(info['number_profile_textbox'], conf['number_profile'])
    if conf['profile_file']:
        #Jluh@20140428, updated by the 9.8 changed
        zd.s.type(info['profile_file_textbox'], conf['profile_file'])
        if zd.s.is_alert_present(5):
            msg_alert = zd.s.get_alert()
            print msg_alert
            raise Exception(msg_alert)
        while True:
            if not zd.s.is_element_present(info['text_batchpass']):
                time.sleep(2)
            else:
                upload_file_msg = zd.s.get_text(info['text_batchpass'])
                if info['error_text'] in upload_file_msg:
                    zd.do_login()
                    zd.logout()
                    raise Exception(upload_file_msg)
                elif info['uploading_text'] in upload_file_msg:
                    time.sleep(2)
                else:
                    logging.info(upload_file_msg)
                    break

    # Enable "shared by multiple guests"
#    if conf['is_shared'] == 'Yes':
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        #_enable_shared_guest_pass(zd)

    # Get all values of required fills
    required_values = {}
    required_values['duration'] = zd.s.get_value(info['duration_textbox'])
    try:
        required_values['guest_wlan'] = zd.s.get_selected_label(info['guest_wlan_option'])

    except:
        required_values['guest_wlan'] = None

    logging.info(required_values)

    # Perform generating guest pass
    zd.s.click_and_wait(info['next_button'])
    time.sleep(3)

    # Check if the alert of maximum allowable size exists
    # If it does, close the dialog
    if conf.has_key('dlg_title') and conf.has_key('dlg_text'):
        if application.findwindows.find_windows(title = conf['dlg_title']):
            dlg = BaseDialog(conf['dlg_title'], "", "OK", "{ENTER}")
            manager = DialogManager()
            manager.add_dialog(dlg)

            manager.start()

            time.sleep(10)
            manager.shutdown()

            zd.do_login()
            zd.logout()

            raise Exception("[ALERT] %s" % conf['dlg_text'])

    err_field = [key for key in required_values.keys() if not required_values[key] or not required_values[key].strip()]
    if err_field:
        errmsg = 'The field(s) %s is(are) empty but there is not any alert message' % err_field
        zd.do_login()
        zd.logout()
        raise Exception(errmsg)
    
    #sent out the email, if the email option is enabled.
    if conf['email'] and zd.s.is_element_present(info['guest_sent_out_multi_email_button']):
        logging.info("Click the sent-out-email button")
        zd.s.click_and_wait(info['guest_sent_out_multi_email_button'])
        time.sleep(15)  
        logging.info("Please have a check the guest-pass email from %s" % conf['email'])

    # Finish generating guest pass
    logging.info("Navigate to the Zone Director's url")
    zd.do_login()
    if zd.is_logged_in():
        zd.logout()


def _verify_guestpass_printout(zd, gp_key, **kwarg):
    conf = {}
    conf.update(**kwarg)

    if conf['printout_checker2']:
        chk2 = str(conf['printout_checker2'])
        chk2 = chk2.replace('{GP_GUEST_KEY}', gp_key)
        conf.update({'printout_checker2': chk2})

    # This dialog handler closes any Print dialogs launched by the Guest Pass Printout window
    dlg_mgr = DialogManager()
    dlg_mgr.add_dialog(BaseDialog("Print", "", "Cancel"))
    dlg_mgr.start()

    # Obtain list of Guest Pass Printouts
    gprints = zd.s.get_select_options(info['printout_option'])

    # Obtain the current window names
    win_names = zd.s.get_all_window_names()

    found = False
    for gprint in gprints:
        if gprint in conf['printout_name']:
            found = True
            break

    if found == False:
        logging.info("Unable to find the Guest Pass Printout [%s] created in the previous step" % conf['printout_name'])

    else:
        logging.info("Open the Guest Pass Printout [%s] and verify its content" % gprint)
        zd.s.select_option(info['printout_option'], gprint)
        zd.s.click_and_wait(info['print_instruction_anchor'])
        time.sleep(3)

        # Find the new window's name
        new_win_name = [name for name in zd.s.get_all_window_names() \
                        if name != 'null' and 'selenium_blank' not in name \
                        and name not in win_names][0]

        # Verify its content
        try:
            zd.s.select_window(new_win_name)
            gprint_content = zd.s.get_html_source()

            if conf['printout_checker1'] in gprint_content and conf['printout_checker2'] in gprint_content:
                found = True

        except:
            # Stop the dialog manager
            #dlg_mgr.shutdown()
            #dlg_mgr.join(10)
            found = False

        finally:
            for name in zd.s.get_all_window_names():
                if name != 'null' and name not in win_names:
                    zd.s.select_window(name)
                    zd.s.close()
            zd.s.select_window('')

    # Stop the dialog manager
    dlg_mgr.shutdown()
    dlg_mgr.join(10)

    # Finish verifying Guest Pass Printout
    logging.info("Navigate to the Zone Director's url")
    zd.do_login()
    zd.logout()

    return found


def __generate_single_guestpass(zd, **kwarg):
    """
    """
    #Jluh@20140428, updated by the 9.8 changed
    conf = {'guest_fullname':'',
            'duration':'',
            'duration_unit': '',
            'wlan': '',
            'email': '',
            'remarks': '',
            'key': '',
            'is_shared': 'No',
            'username': '',
            }
    conf.update(**kwarg)
    # Click to choice the creation type is single
    zd.s.click_and_wait(info['single_radio'])

    # Fill the information of the guest pass
    msg = "Fill the guest pass information --- \
           Full name: '%s', duration: '%s', duration unit: '%s', remarks:'%s', key:'%s'"
    msg = msg % (conf['guest_fullname'], conf['duration'], conf['duration_unit'], conf['remarks'], conf['key'])
    logging.info(msg)

    if conf['guest_fullname']:
        zd.s.type_text(info['fullname_textbox'], conf['guest_fullname'])

    if conf['duration']:
        zd.s.type_text(info['duration_textbox'], str(conf['duration']))

    if conf['duration_unit']:
        zd.s.select_option(info['duration_unit_option'], conf['duration_unit'])

    if conf['wlan']:
        zd.s.select_option(info['guest_wlan_option'], conf['wlan'])
        
    if conf['email']:
        zd.s.type_text(info['guest_email_option'], conf['email'])

    if conf['remarks']:
        zd.s.type_text(info['remarks_textarea'], conf['remarks'])

    if conf['key']:
        zd.s.type_text(info['key_textbox'], conf['key'])

    # Enable "shared by multiple guests"
#    if conf['is_shared'] == 'Yes':
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        #_enable_shared_guest_pass(zd)

    # Get all values of required fills
    required_values = {}
    required_values['guest_fullname'] = zd.s.get_value(info['fullname_textbox'])
    required_values['duration'] = zd.s.get_value(info['duration_textbox'])
    try:
        required_values['guest_wlan'] = zd.s.get_selected_label(info['guest_wlan_option'])

    except:
        required_values['guest_wlan'] = None

    required_values['key'] = zd.s.get_value(info['key_textbox'])

    logging.info(required_values)

    # Perform generating guest pass
    zd.s.click_and_wait(info['next_button'])
    time.sleep(3)

    # Check if the alert of maximum allowable size exists
    # If it does, close the dialog
    if conf.has_key('dlg_title') and conf.has_key('dlg_text'):
        if application.findwindows.find_windows(title = conf['dlg_title']):
            #dlg = BaseDialog(conf['dlg_title'], conf['dlg_text'], "OK", "{ENTER}")
            dlg = BaseDialog(conf['dlg_title'], "", "OK", "{ENTER}")
            manager = DialogManager()
            manager.add_dialog(dlg)

            manager.start()

            time.sleep(10)
            manager.shutdown()

            zd.do_login()
            zd.logout()

            raise Exception("[ALERT] %s" % conf['dlg_text'])

    err_field = [key for key in required_values.keys() if not required_values[key] or not required_values[key].strip()]
    if err_field:
        errmsg = 'The field(s) %s is(are) empty but there is not any alert message' % err_field
        zd.do_login()
        zd.logout()
        raise Exception(errmsg)
    
    if conf['email']:
        logging.info("Click the sent-out-email button")
        zd.s.click_and_wait(info['guest_sent_out_email_button'])
        time.sleep(5)
        logging.info("Please have a check the guest-pass email from %s" % conf['email'])
        

def download_generated_guestpass_record(zd, username, password, sample_filename = 'generated_batch_guestpass.csv'):
    
    _perform_auth_to_generate_guestpass(zd, username, password)
    ##zj2014-01-25 ZF-7245  fixed  download failed because the page is wrong.  
    ## download link is in "https://192.168.1.106/user/guestpass.jsp?e=false"
    zd.s.click_and_wait(info['multiple_radio'])
    zd.s.click_and_wait(info['next_button'])
    ##zd.s.click_and_wait(info['show_existing_guestpass_link'])
    time.sleep(5)

    logging.debug("checking if download generated guestpass link is present")
    if zd.s.is_element_present(info['download_generated_guestpass']):
        logging.debug("link's present; attemping to download")
        try:
            loc = info['download_generated_guestpass']
            return _download_single_file(zd, loc, sample_filename)

        except Exception, e:
            logging.debug(e.message)
            raise

    else:
        logging.debug("link's not present; attemping to logout")
        zd.do_login()
        zd.logout()
        raise Exception('There is not any generated guest passed file to download')


def _download_generated_guestpass_record(zd, sample_filename = 'generated_batch_guestpass.csv'):
    # Make the path to the file, which is supposed to be saved on the Desktop of the current logged in user
    file_path = os.path.join(os.path.expanduser('~'), r"Desktop\%s" % sample_filename)
    # Remove it if it is existing
    if os.path.isfile(file_path):
        os.remove(file_path)
    # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
    dlg1 = BaseDialog(title = "Opening %s" % sample_filename, text = "", button_name = "", key_string = "{PAUSE 3} %s {PAUSE 1} {ENTER}")
    dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "", key_string = "{PAUSE 3} %{F4}")
    dlg_mgr = DialogManager()
    dlg_mgr.add_dialog(dlg1)
    dlg_mgr.add_dialog(dlg2)
    dlg_mgr.start()


    zd.s.click_and_wait(info['download_generated_guestpass'])

    # Wait until the file is saved
    t0 = time.time()
    while time.time() - t0 < 15:
        if os.path.isfile(file_path): break

    # Regardless what has happened, stop the dialog handlers
    time.sleep(5)
    dlg_mgr.shutdown()
    time.sleep(2)

    zd.do_login()
    zd.logout()

    if os.path.isfile(file_path):
        return file_path
    raise Exception("Unable to download and save the file to [%s]" % file_path)

###
##
## Generated guest pass
##
###

def _log_to_generate_guestpass_page(zd):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_GENERATED_GUESTPASSES)


def _click_showmore_button_on_generated_guestpass_page(zd):
    while zd.s.is_visible(info['guestpass_showmore_button']):
        zd.s.click_and_wait(info['guestpass_showmore_button'])


#@author:yuyanan @since:2015-4-3 @change:9.10 new feature:modify parameter for transfer xpath
#cwang@2010-10-26, behavior change against Toranto build.
def _get_page_range_and_total_number_of_generated_guestpass(zd,loc=info['total_guestpasses_span']):
    
    total_info = zd.s.get_text(loc)
    if not total_info:
        time.sleep(1)
        total_info = zd.s.get_text(loc)

    pat = "\((\d+)\)"
    match_obj = re.findall(pat, total_info)

    from_idx = 0
    to_idx = 0
    if match_obj:
        total = match_obj[0]

    else:
        raise Exception("Can not get the total number of rows in generated guest pass table")

    return from_idx, to_idx, total



def delete_guestpass(zd, guest_name, wait_time = 2):
    """
    """
    _log_to_generate_guestpass_page(zd)
    time.sleep(wait_time * 15)

    zd.s.type_keys(info['guestpass_search_box'], guest_name)

    time.sleep(wait_time * 5)
    _click_showmore_button_on_generated_guestpass_page(zd)
    time.sleep(wait_time * 5)
    fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd)
    guestpass_existing = True
    if total != '0':
        loc = '%s/input' % (info['guestpass_row_with_guest_name'] % (guest_name, info['column_id']['checkbox']))
        try:
            zd.s.click_and_wait(loc)
            time.sleep(wait_time / 4)
            zd.s.click_and_wait(info['guestpass_guestdel_button'])
            time.sleep(wait_time)
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception("[ALERT] %s" % msg_alert)

            logging.info('Deleted the guest pass "%s" successfully' % guest_name)

        except Exception, e:
            if e.message == 'Element %s not found' % loc:
                guestpass_existing = False

            else:
                raise Exception('[Delete Guest %s failed]: %s' % (guest_name, e.message))

    if total == '0' or not guestpass_existing:
        raise Exception('The guest pass "%" is not existed')
    
#@author: yuyanan @since: 2015-4-25 @change:9.10 new feature    
def delete_all_selfservice_guestpass(zd, wait_time = 2):
    _log_to_generate_guestpass_page(zd)
    time.sleep(wait_time)
    fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd,info['total_selfguestpasses_span'])
    if total == '0':
        logging.debug('There is no guest pass in the "Generated Guest Pass" table')
        return

    total_guestpass = total

    while total != '0':
        #if the button 'Delete All' exists, click it to quickly remove all guestpass
        delall_loc = info['selfguestpass_guestdelall_button']
        if zd.s.is_element_present(delall_loc) and not zd.s.is_element_disabled(delall_loc):
           
            zd.s.click_and_wait(delall_loc)
            fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd,info['total_selfguestpasses_span'])
            if total == '0':
                logging.info('%s guestpasses are deleted successfully' % total_guestpass)
                return True
            
        loc = info['selfguestpass_guestall_checkbox']
        try:
            if not zd.s.is_checked(loc):
                zd.s.click_and_wait(loc)

            time.sleep(wait_time / 2)
            zd.s.click_and_wait(info['selfguestpass_guestdel_button'])
            time.sleep(wait_time * 2 + int(total) / 100)
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception("[ALERT] %s" % msg_alert)

        except Exception, e:
            if e.message == 'Element %s not found' % loc:
                return False

            else:
                raise Exception('[Delete Multiple selfGuestPass failed]: %s' % (e.message))

        fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd)                    
            
    logging.info('%s selfguestpasses are deleted successfully' % total_guestpass)


def delete_all_guestpass(zd, wait_time = 2):
    """
    """
    _log_to_generate_guestpass_page(zd)
    time.sleep(wait_time)
    #_click_showmore_button_on_generated_guestpass_page(zd)
#    time.sleep(wait_time)
    fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd)
    if total == '0':
        logging.debug('There is no guest pass in the "Generated Guest Pass" table')
        return

    total_guestpass = total

    while total != '0':
        #ChrisWang@20100617 if the button 'Delete All' exists, click it to quickly remove all guestpass
        delall_loc = info['guestpass_guestdelall_button']
        if zd.s.is_element_present(delall_loc) and not zd.s.is_element_disabled(delall_loc):
            zd.s.choose_ok_on_next_confirmation()
            zd.s.click_and_wait(delall_loc)

            if zd.s.is_confirmation_present(5):
                zd.s.get_confirmation()

            fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd)
            if total == '0':
                logging.info('%s guestpasses are deleted successfully' % total_guestpass)
                return True

        loc = info['guestpass_guestall_checkbox']
        try:
            if not zd.s.is_checked(loc):
                zd.s.click_and_wait(loc)

            time.sleep(wait_time / 2)
            zd.s.click_and_wait(info['guestpass_guestdel_button'])
            time.sleep(wait_time * 2 + int(total) / 100)
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception("[ALERT] %s" % msg_alert)

        except Exception, e:
            if e.message == 'Element %s not found' % loc:
                guestpass_existing = False

            else:
                raise Exception('[Delete Multiple GuestPass failed]: %s' % (e.message))

        fidx, lidx, total = _get_page_range_and_total_number_of_generated_guestpass(zd)

    logging.info('%s guestpasses are deleted successfully' % total_guestpass)


###
##
## Shared Guest Pass
##
###
def _set_shared_guest_pass(zd):
    '''
    '''
    zd.s.click_if_not_checked(info['guestpass_auth_radio'])
    zd.s.click_if_not_checked(info['guestpass_shared_checkbox'])
    zd.s.click_and_wait(info['apply_guest_btn'])


def _enable_shared_guest_pass(zd):
    zd.s.click_if_not_checked(info['guestpass_shared_checkbox'])


def _select_auth_server(zd, server):
    # select authentication server option
    zd.s.select_option(info['auth_server_option'], server)
    zd.s.click_and_wait(info['guestpass_apply_button'])
    time.sleep(2)
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)

    newval = zd.s.get_selected_option(info['auth_server_option'])
    if newval != server:
        raise Exception('Element guest access auth server value %s changed after Web is refreshed' % server)

def select_auth_server(zd, server):
    _select_auth_server(zd, server)

###
##
## common methods
##
###
def _download_single_file(zd, loc, filename):
    try:
        # Make the path to the file, which is supposed to be saved on the Desktop of the current logged in user
        file_path = os.path.join(constant.save_to, r"%s" % filename)

        # Remove it if it is existing
        if os.path.isfile(file_path):
            os.remove(file_path)
        # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
        #zj 2014-02221 script optimization when download ZF-7540
#        dlg1 = BaseDialog(title = "Opening %s" % filename, text = "", button_name = "", key_string = "{PAUSE 3} %s  {ENTER}")
        dlg1 = BaseDialog(title = "Opening %s" % filename, text = "", button_name = "", key_string = "{PAUSE 3} %s {PAUSE 1} {ENTER}")
        dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "", key_string = "%{F4}")
        dlg_mgr = DialogManager()
        dlg_mgr.add_dialog(dlg1)
        dlg_mgr.add_dialog(dlg2)
        dlg_mgr.start()
        time.sleep(10)

        logging.debug("click the download link")
        zd.s.click_and_wait(loc)

        # Wait until the file is saved
        t0 = time.time()
        while time.time() - t0 < 120:
            if os.path.isfile(file_path): break

        if os.path.isfile(file_path):
            return file_path

    except Exception, e:
        logging.debug(e.message)
        raise Exception("Unable to download and save the file to [%s]" % file_path)

    finally:
        # Regardless what has happened, stop the dialog handlers
        time.sleep(5)
        dlg_mgr.shutdown()
        time.sleep(2)

        zd.do_login()
        zd.logout()

# for demonstration only. update it accordingly base on the changes if any
const = [1, 2]

def _log_to_the_page_v82(zd):
    #logging.debug('----- _log_to_the_page() updated method was called -----')
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)
    
def create_default_guestaccess_policy(zd, selfservice=False):
    """
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    This function configures the Guest Access Policy to specified info
    @param use_guest_auth: A boolean value indicates that Guest Pass authen is used or not
    @param use_tou: A boolean value indicates that TOU is used or not
    @param redirect_url: A string holds the URL that is redirected to; use NULL to disable this feature
    """
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)
    
    #check exist
    if zd.s.is_element_present(Locators['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME):
        return
    
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    create_new_span = Locators['loc_cfg_guest_access_new_span']
    gc_name = Locators['loc_cfg_guest_access_name']
    if zd.s.is_element_disabled(create_new_span, timeout = 1):
        raise Exception("Unable to create more when the 'Create New' button is disabled.") 
    zd.s.click_and_wait(create_new_span)
    zd.s.type_text(gc_name, DEFAULT_GUEST_ACCESS_NAME)
    
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
    selfser = Locators['loc_cfg_guestpass_selfservice_check_box']
    if zd.s.is_element_present(selfser, 2):
        if not selfservice:
            zd.s.uncheck(selfser)
        else:
            zd.s.check(selfser)
    else:
        if older_than_release(zd.version['version'], '9.9.1.0'):#Chico, 2015-6-29, optimize to cover future releases
            pass
        else:
            raise Exception("Element '%s' doesn't exist." % selfser)
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226

    zd.s.click_and_wait(Locators['loc_cfg_guest_access_ok'])
    time.sleep(5)

    if zd.s.is_alert_present(5):
        raise Exception(zd.s.get_alert())

def delete_default_guestaccess_policy(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)

    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
    check_before = Locators['loc_cfg_guest_access_check_box_before_profile'] % str(0)
    delete_span = Locators['loc_cfg_guest_access_delete_span']
    
    if zd.s.is_element_present(check_before):
        zd.s.click_and_wait(check_before)
        zd.s.click_and_wait(delete_span)
    return

#Jluh@20140428 updated by the 9.8 changed
def config_ga_email_content(zd, content):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)
    
    email_textarea = Locators['loc_guestaccess_email_content']
    email_content_apply_button = Locators['loc_guestaccess_email_content_apply_button']
    
    zd.refresh()
    time.sleep(2)
    zd.s.type_text(email_textarea, '')
    zd.s.type(email_textarea, content)      
    zd.s.click_and_wait(email_content_apply_button, 2)
    if zd.s.is_alert_present(5):
        msg_alert = zd.s.get_alert()
        print msg_alert
        return msg_alert
    else:
        return ''
    