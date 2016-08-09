import logging
import re
import time

from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.components.lib.zd import aps
from RuckusAutoTest.components.lib.zd import access_points_zd as ap
from RuckusAutoTest.components.lib.zd import wlan_zd as wlan

AP_INFO_HDR_MAP = {
    'description': 'description',
    'ip': 'ip_addr',
    'ipv6': 'ipv6',
    'mac': 'mac',
    'num_sta': 'clients',
    'radio_channel': 'channel',
    'state': 'status',
    'model': 'model',
}

#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
def get_mem_ap_brief_by_mac(zd, wgs_name, mac_addr):
    '''
    '''
    ap_info = wgt.map_row(
        _get_mem_ap_brief_by(zd, wgs_name, dict(mac = mac_addr)),
        AP_INFO_HDR_MAP
    )
    zd.re_navigate()

    return ap_info


def get_all_mem_ap_briefs(zd, wgs_name):
    '''
    . get all ap info on Monitors > Access Points
    return
    . as a dict of dicts with mac addresses as keys

    '''
    ap_info = list_to_dict(
        wgt.map_rows(_get_all_mem_ap_briefs(zd, wgs_name),
                     AP_INFO_HDR_MAP
                     ),
        'mac'
    )
    zd.re_navigate()

    return ap_info


#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------

locators = dict(
    tbl_loc = "//table[@id='%s']",
    tbl_nav_loc = "//table[@id='%s']/tfoot",
    tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
)

tbl_id = dict(
    mem_ap = 'aps',
)


def _nav_to_cfg(zd):
    '''
    '''
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)


def _nav_to_mon(zd):
    '''
    '''
    zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN)


def _open_wlangroup_detail_page(zd, wgs_name, wait = 1.5):
    xloc = LOCATORS_MON_WLANGROUPS
    zd.s.click_and_wait(xloc['check_detail_by_name'] % wgs_name, wait)


def _get_all_mem_ap_briefs(zd, wgs_name):
    '''
    return
    . a list of dict
    '''
    _nav_to_mon(zd)

    _open_wlangroup_detail_page(zd, wgs_name)

    ap_info = wgt.get_tbl_rows(
        zd.s, locators['tbl_loc'] % tbl_id['mem_ap'],
        locators['tbl_nav_loc'] % tbl_id['mem_ap']
    )

    return aps.update_ipv4_ipv6(ap_info)


def _get_mem_ap_brief_by(zd, wgs_name, match, verbose = False):
    _nav_to_mon(zd)
    _open_wlangroup_detail_page(zd, wgs_name)

    ap_info = wgt.get_first_row_by(
        zd.s, locators['tbl_loc'] % tbl_id['mem_ap'],
        locators['tbl_nav_loc'] % tbl_id['mem_ap'], match,
        filter = locators['tbl_filter_txt'] % tbl_id['mem_ap'],
        verbose = verbose,
    )

    return aps.update_ipv4_ipv6(ap_info)


LOCATORS_CFG_WLANS = dict(
    create_new = r"//table[@id='wlan']//span[@id='new-wlan']",
    doEdit = r"//table[@id='wlan']//tr/td[text()='%s']/../td/span[text()='Edit']",
)

LOCATORS_CFG_WLANGROUPS = dict(
    select_all = r"//table[@id='wgroup']//input[@id='wgroup-sall']",

    check_name_default = r"//table[@id='wgroup']//tr/td[text()='Default']/../td/input[@name='wgroup-select']",
    check_name = r"//table[@id='wgroup']//tr/td[text()='%s']/../td/input[@name='wgroup-select']",
    create_new = r"//table[@id='wgroup']//span[@id='new-wgroup']",
    get_totals = r"//table[@id='wgroup']//div[@class='actions']/span",
    get_name = r"//table[@id='wgroup']//tr/td[text()='%s']/../td[2]",
    get_description = r"//table[@id='wgroup']//tr/td[text()='%s']/../td[3]",
    get_wgs_name = r"//table[@id='wgroup']//tr[@idx='%s']/td[2]",

    doEdit_default = r"//table[@id='wgroup']//tr/td[text()='Default']/../td/span[text()='Edit']",
    doEdit = r"//table[@id='wgroup']//tr/td[text()='%s']/../td/span[text()='Edit']",
    doClone = r"//table[@id='wgroup']//tr/td[text()='%s']/../td/span[text()='Clone']",
    doDelete = r"//table[@id='wgroup']//input[@id='del-wgroup']",
    doNext = "//table[@id='wgroup']//img[@id='showmore-wgroup']",

    edit_name = r"//form[@id='form-wgroup']//input[@id='wgroup-name']",
    edit_description = r"//form[@id='form-wgroup']//input[@id='wgroup-description']",
    #edit_member_vlan_override = r"//form[@id='form-wgroup']//input[@id='has-vlan']",
    #edit_member_vlan_wlan = r"//table[@id='wlanTable']//td/label[text()='%s']/../input",
    
    show_more_wlan_in_wlangroup = r"//form[@id='form-wgroup']//input[@id='showmore-wgwlan']",#zoeadd
    
    edit_OK = r"//form[@id='form-wgroup']//input[@id='ok-wgroup']",
    edit_Cancel = r"//form[@id='form-wgroup']//input[@id='cancel-wgroup']",

    show_more_button = "//table[@id='wgroup']//input[@id='showmore-wgroup']",
    #Update the step by Jacky Luh@2011-07-22
    search_terms_input = "//table[@id='wgwlan']//tr[@class='t_search']//input[@type='text']",
    search_wlangroup_input = r"//fieldset/table[@id='wgroup']/tfoot//tr[@class='t_search']/td/span[@class='other-act']/input[@type='text']",

    edit_member_vlan_override = r'',
    edit_member_wlan_name = r"//table[@id='wgwlan']//td[text()='%s']/../td[2]",
    edit_member_wlan_original_vlan = r"//table[@id='wgwlan']//td[text()='%s']/../td[3]",
    edit_member_vlan_wlan = r"//table[@id='wgwlan']//td[text()='%s']/..//input[@type='checkbox']",
    edit_member_wlan_vlan_no_change = r"//table[@id='wgwlan']//td[text()='%s']/..//input[contains(@id,'vo-asis')]",
    edit_member_wlan_vlan_untag = r"//table[@id='wgwlan']//td[text()='%s']/..//input[contains(@id,'vo-untag')]",
    edit_member_wlan_vlan_tag = r"//table[@id='wgwlan']//td[text()='%s']/..//input[contains(@id,'vo-tag')]",
    edit_member_wlan_tag_override = r"//table[@id='wgwlan']//td[text()='%s']/..//input[@type='text']",
    wlan_member_tbl = r"//table[@id='wgwlan']",
    wlan_member_chk_tmpl = r"//table[@id='wgwlan']//td[text()='%s']/..//input[@type='checkbox']",
    
    wlan_group_checkbox = r"//table[@id='wgroup']//tr[td='%s']//input[@type='checkbox']"
)

LOCATORS_MON_WLANGROUPS = dict(
    check_detail_by_name = r"//table[@id='wlangroupsummary']//td/a[text()='%s']",

    get_member_ap_description_by_mac = r"//table[@id='aps']//tr/td/a[text()='%s']/../../td[2]",
    get_member_ap_model_by_mac = r"//table[@id='aps']//tr/td/a[text()='%s']/../../td[3]",
    get_member_ap_status_by_mac = r"//table[@id='aps']//tr/td/a[text()='%s']/../../td[4]",
    get_member_ap_ip_addr_by_mac = r"//table[@id='aps']//tr/td/a[text()='%s']/../../td[5]",
    get_member_ap_channel_by_mac = r"//table[@id='aps']//tr/td/a[text()='%s']/../../td[6]",
    get_member_ap_clients_by_mac = r"//table[@id='aps']//tr/td/a[text()='%s']/../../td[7]",
)

###
##
## WLAN GROUPS
##
###
def check_default_wlan_member(zd, wlan_name, pause = 1.0):
    return cfg_default_wlan_member(zd, wlan_name, True, pause)


def uncheck_default_wlan_member(zd, wlan_name, pause = 1.0):
    return cfg_default_wlan_member(zd, wlan_name, False, pause)


def cfg_default_wlan_member(zd, wlan_name, check = False, pause = 1.0):
    '''
    '''
    return cfg_wlan_member(zd, 'Default', wlan_name, check, pause)


def cfg_wlan_member(zd, wlangroup_name, wlan_name, check = False, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)
    loc_edit_wg_by_name = xloc['doEdit'] % (wlangroup_name)
    time_start=time.time()
    while not zd.s.is_element_present(loc_edit_wg_by_name) and time.time()-time_start<60:
        _nav_to_cfg(zd)
        time.sleep(5)
    zd.s.click_and_wait(loc_edit_wg_by_name)
    time.sleep(pause)
    
    while zd.s.is_visible(xloc['show_more_wlan_in_wlangroup']):
        zd.s.click_and_wait(xloc['show_more_wlan_in_wlangroup'])
        
    loc_edit_wg_wlan = xloc['edit_member_vlan_wlan'] % (wlan_name)
    #@author: chen.tao 2013-12-19, to fix bug ZF-6493
    if not zd.s.is_element_present(loc_edit_wg_wlan):
        logging.warning('Attention: WLAN %s does not exist, do nothing!'%wlan_name)
        return
    #@author: chen.tao 2013-12-19, to fix bug ZF-6493
    try:
        if check:
            zd.s.click_if_not_checked(loc_edit_wg_wlan)
    
        else:
            zd.s.click_if_checked(loc_edit_wg_wlan)
    except:
        _search_wlan_members_by_wlan_name(zd, wlan_name)
        if check:
            zd.s.click_if_not_checked(loc_edit_wg_wlan)
    
        else:
            zd.s.click_if_checked(loc_edit_wg_wlan)

    time.sleep(pause)
    zd.s.click_and_wait(xloc['edit_OK'])
    time.sleep(pause)


def cfg_wlan_group_members(zd, wlangroup_name, wlan_name_list, check = False, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)
    loc_edit_wg_by_name = xloc['doEdit'] % (wlangroup_name)
    if not zd.s.is_element_present(loc_edit_wg_by_name):
        zd.refresh()
        time.sleep(10)
    if not zd.s.is_element_present(loc_edit_wg_by_name):
        _search_wlan_group(zd,wlangroup_name)
    zd.s.click_and_wait(loc_edit_wg_by_name)
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_wlan_in_wlangroup']):
        zd.s.click_and_wait(xloc['show_more_wlan_in_wlangroup'])
        
    for wlan_name in wlan_name_list:
        loc_edit_wg_wlan = xloc['edit_member_vlan_wlan'] % (wlan_name)
        if not zd.s.is_element_present(loc_edit_wg_wlan):
            time.sleep(10)
        try:
            if check:
                zd.s.click_if_not_checked(loc_edit_wg_wlan)
    
            else:
                zd.s.click_if_checked(loc_edit_wg_wlan)
        except:
            _search_wlan_members_by_wlan_name(zd, wlan_name)
            if check:
                zd.s.click_if_not_checked(loc_edit_wg_wlan)
    
            else:
                zd.s.click_if_checked(loc_edit_wg_wlan)

        time.sleep(pause)

    zd.s.click_and_wait(xloc['edit_OK'])
    time.sleep(pause)


def edit_wlan_group(zd, wlan_group, new_wlan_group = '', description = '', pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)
    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_group)
    zd.s.click_and_wait(loc_edit_wg_by_name)
    time.sleep(pause)
    if new_wlan_group:
        zd.s.type_text(xloc['edit_name'], new_wlan_group)

    zd.s.type_text(xloc['edit_description'], description)
    zd.s.click_and_wait(xloc['edit_OK'])
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        if not re.search('Please enter a different name', _alert, re.I):
            raise Exception(_alert)

    time.sleep(pause)

#added by west li
#del a wlan group
def del_wlan_group(zd, wlan_group, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)
    check_box = xloc['wlan_group_checkbox'] % (wlan_group)
    _search_wlan_group(zd, wlan_group)
    if zd.s.is_element_present(check_box):
        zd.s.click_and_wait(check_box)
        zd.s.click_and_wait(xloc['doDelete'])
        time.sleep(pause)


def create_wlan_group(
        zd, wlan_group, wlan_name, check_VLAN_override = False, description = '', is_nav = True
    ):
    '''
    . is_nav: this param to support config wlan group on ZD template in
      FlexMaster. If do this from FM, don't navigate to ZD > WLANs page.
    '''
    xloc = LOCATORS_CFG_WLANGROUPS
    logging.info("Create [wlangroup %s] with-memeber [wlan %s]" % (wlan_group, wlan_name))
    if is_nav:
        _nav_to_cfg(zd)

    if not wgt.is_enabled_to_click(zd, xloc['create_new']):
        raise Exception("Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported")

    zd.s.click_and_wait(xloc['create_new'])
    zd.s.type_text(xloc['edit_name'], wlan_group)
    zd.s.type_text(xloc['edit_description'], description)
    
    while zd.s.is_visible(xloc['show_more_wlan_in_wlangroup']):
        zd.s.click_and_wait(xloc['show_more_wlan_in_wlangroup'])
        
    vo_loc = xloc['edit_member_vlan_override']
    if vo_loc:
        if check_VLAN_override:
            zd.s.click_if_not_checked(vo_loc)

        else:
            zd.s.click_if_checked(vo_loc)

    #JLIN@20100413 wlan_name can be empty list
    if wlan_name:
        if type(wlan_name) is list:
            for wlan in wlan_name:
                try:
                    zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % wlan)
                except:
                    _search_wlan_members_by_wlan_name(zd, wlan)
                    zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % wlan)

        else:
            try:
                zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % (wlan_name))
            except:
                _search_wlan_members_by_wlan_name(zd, wlan_name)
                zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % (wlan_name))

    zd.s.click_and_wait(xloc['edit_OK'])


def create_wlan_group_2(zd, cfg, is_nav = True):
    '''
    . a simplified version of create_wlan_group
    . cfg = dict(
        name = string,
        description = string,
        wlan_member = [list of wlan members],
        vlan_override = True | False,
    )
    . is_nav: this param to support config wlan group on ZD template in
      FlexMaster. If do this from FM, don't navigate.
    '''
    create_wlan_group(
        zd, cfg['name'], cfg['wlan_member'], cfg['vlan_override'],
        cfg['description'], is_nav
    )

#
# Create a series Wlan Group
#
def create_multi_wlan_groups(zd, wlan_group, wlan_name, check_VLAN_override = False, description = '', num_of_wgs = 1, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    logging.info("Create %d WLAN Group(s) with-memeber [wlan %s]" % (num_of_wgs, wlan_name))

    _nav_to_cfg(zd)
    for i in range(num_of_wgs):
        wgs_name = "%s-%d" % (wlan_group, i + 1)
        if num_of_wgs == 1:
            wgs_name = wlan_group

        logging.info("Create [wlangroup %s] with-memeber [wlan %s]" % (wgs_name, wlan_name))
        if not zd.s.is_visible(xloc['create_new']):
            msg = "Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported"
            raise Exception(msg)

        zd.s.click_and_wait(xloc['create_new'])
        zd.s.type_text(xloc['edit_name'], wgs_name)
        zd.s.type_text(xloc['edit_description'], description)
        
        while zd.s.is_visible(xloc['show_more_wlan_in_wlangroup']):
            zd.s.click_and_wait(xloc['show_more_wlan_in_wlangroup'])

        vo_loc = xloc['edit_member_vlan_override']
        if vo_loc:
            if check_VLAN_override:
                zd.s.click_if_not_checked(vo_loc)

            else:
                zd.s.click_if_checked(vo_loc)                  

        if type(wlan_name) is list:
            for wlan_name_idx in wlan_name:
                try:
                    zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % (wlan_name_idx))
                except:
                    _search_wlan_members_by_wlan_name(zd, wlan_name_idx)
                    zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % (wlan_name_idx))
        else:
            try:
                zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % (wlan_name))
            except:
                    _search_wlan_members_by_wlan_name(zd, wlan_name)
                    zd.s.click_if_not_checked(xloc['edit_member_vlan_wlan'] % (wlan_name))

        zd.s.click_and_wait(xloc['edit_OK'])
        time.sleep(pause)


def get_wlan_group_of_member(zd, wlan_group_name, member_wlan_name, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    result = {'name': wlan_group_name, 'wlan_member': {'name': member_wlan_name}}
    _nav_to_cfg(zd)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd.s.click_and_wait(xloc['show_more_button'])

    zd.s.click_and_wait(xloc['doEdit'] % wlan_group_name)
    result['name'] = zd.s.get_value(xloc['edit_name'])
    result['description'] = zd.s.get_value(xloc['edit_description'])
    
    _search_wlan_members_by_wlan_name(zd, member_wlan_name)
    
    vo_loc = xloc['edit_member_vlan_override']
    if vo_loc:
        result['vlan_overwrite'] = wgt.get_checkbox_boolean(zd, vo_loc)

    else:
        result['vlan_overwrite'] = True

    result['wlan_member']['checked'] = wgt.get_checkbox_boolean(zd, xloc['edit_member_vlan_wlan'] % (member_wlan_name))

    return result


def remove_wlan_groups(zd, ap_mac_addrList = [], z_pauseDelete = 4, pause = 1.0):
    logging.info('remove wlan group in zd %s' % zd.ip_addr)
    if ap_mac_addrList:
        ap.default_wlan_groups_by_mac_addr(zd, ap_mac_addrList)

    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)
    tot_wgs = zd.s.get_text(xloc['get_totals'])
    if tot_wgs.find('(1)') > 0:
        logging.info('No wlan groups to delete')
        return

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd.s.click_and_wait(xloc['show_more_button'])

    zd.s.click_and_wait(xloc['select_all'])
    zd.s.click_if_checked(xloc['check_name_default'])
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(xloc['doDelete'])
    time.sleep(z_pauseDelete)
    if zd.s.is_confirmation_present(5):
        zd.s.get_confirmation()

    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        if not re.search('Nothing\s+is\s+selected', _alert, re.I):
            raise Exception(_alert)

#
# Monitor>WLANs>WlanGroups
#
def get_status_ex_by_ap_mac_addr(zd, wgs_name, macAddr):
    '''
    WARNING: OBSOLETE, please use get_mem_ap_brief_by_mac function
    '''
    return get_mem_ap_brief_by_mac(zd, wgs_name, macAddr)


    # the code below is not applicable and will be removed soon
    xloc = LOCATORS_MON_WLANGROUPS
    zd.navigate_to(zd.MONITOR, zd.MONITOR_WLAN)
    zd.s.click_and_wait(xloc['check_detail_by_name'] % wgs_name)
    result = {'wgs_name': wgs_name, 'mac': macAddr}
    for xid in ['model', 'status', 'ip_addr', 'channel', 'clients', 'description']:
        locid = 'get_member_ap_%s_by_mac' % xid
        result[xid] = zd.s.get_text(xloc[locid] % macAddr)

    return result


        
#
# Clone a Wlangroup from an exist wlan
#
def clone_wlan_group(zd, wlan_group, new_wlan_group, description = '', pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    logging.info("Clone [wlangroup %s] to [new wlangroup %s]" % (wlan_group, new_wlan_group))
    _nav_to_cfg(zd)

    # Show all wlan group on one page to clone
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd.s.click_and_wait(xloc['show_more_button'])

    logging.info("Find [wlangroup %s] to clone in WLAN Groups table" % wlan_group)
    clone = xloc['doClone'] % (wlan_group)
    if zd.s.is_element_present(clone):
        zd.s.click_and_wait(clone)
        zd.s.type_text(xloc['edit_name'], new_wlan_group)
        zd.s.type_text(xloc['edit_description'], description)
        zd.s.click_and_wait(xloc['edit_OK'])

        if zd.s.is_alert_present(5):
            _alert = zd.s.get_alert()
            if not re.search('Please enter a different name', _alert, re.I):
                raise Exception(_alert)

    else:
        logging.debug("Can't find [wlangroup %s] in WLAN Groups table" % wlan_group)


#
# Get current total number of Wlan Group on ZD
#
def get_total_wlan_groups(zd):
    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)
    tot_wgs = int(zd._get_total_number(xloc['get_totals'], "wgroup"))
    logging.info("Current total Wlan Group on ZD %d " % tot_wgs)

    return tot_wgs


def find_wlan_group(zd, wlan_group, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    _nav_to_cfg(zd)

    logging.info("find [wlangroup %s] in Wlan Group Table" % (wlan_group))
    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd.s.click_and_wait(xloc['show_more_button'], pause)

    find_result = False

    if zd.s.is_element_present(xloc['get_name'] % wlan_group):
        find_result = True

    return find_result

#
# Remove all wlans out of wlan group
#
def remove_wlan_members_from_wlan_group(zd, wlan_group_name, wlan_name_list):
    for wlan_name in wlan_name_list:
        if get_wlan_group_of_member(zd, wlan_group_name, wlan_name):
            cfg_wlan_member(zd, wlan_group_name, wlan_name, False)

#
# Get Wlan Group Configuration
#
def get_wlan_group_cfg(zd, wlan_group, pause = 1.0):
    wgs_cfg = dict(
            name = '',
            description = '',
            vlan_override = False,
            wlan_member = dict()
    )
    #Added by Serena Tan, 2010.10.27.
    group_list = get_wlan_groups_list(zd)
    if wlan_group not in group_list:
        logging.info('The WLAN group [%s] does not exist!' % wlan_group)
        return None

    xloc = LOCATORS_CFG_WLANGROUPS
    wlan_list = wlan.get_wlan_list(zd)

    _nav_to_cfg(zd)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd.s.click_and_wait(xloc['show_more_button'])

    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_group)
    zd.s.click_and_wait(loc_edit_wg_by_name)
    time.sleep(pause)
    wgs_cfg['name'] = wlan_group
    wgs_cfg['description'] = zd.s.get_value(xloc['edit_description'])
    
    vo_loc = xloc['edit_member_vlan_override']
    if vo_loc:
        wgs_cfg['vlan_override'] = wgt.get_checkbox_boolean(zd, vo_loc)

    else:
        wgs_cfg['vlan_override'] = True

    # get detail wlan_member vlan
    for wlan_name in wlan_list:
        #Update the step by Jacky Luh@2011-07-22
        _search_wlan_members_by_wlan_name(zd, wlan_name)
        is_wlan_member = wgt.get_checkbox_boolean(zd, xloc['edit_member_vlan_wlan'] % (wlan_name))
        if is_wlan_member:
            wgs_cfg['wlan_member'][wlan_name] = dict()
            if wgs_cfg['vlan_override']:
                wgs_cfg['wlan_member'][wlan_name]['original_vlan'] = zd.s.get_text(xloc['edit_member_wlan_original_vlan'] % wlan_name)
                if zd.s.is_checked(xloc['edit_member_wlan_vlan_no_change'] % wlan_name):
                    wgs_cfg['wlan_member'][wlan_name]['vlan_override'] = "No Change"

                elif zd.s.is_element_present(xloc['edit_member_wlan_vlan_untag'] % wlan_name) \
                    and zd.s.is_checked(xloc['edit_member_wlan_vlan_untag'] % wlan_name):
                    #Update for 9.4 change remove untag radio button.
                    wgs_cfg['wlan_member'][wlan_name]['vlan_override'] = "Untag"

                elif zd.s.is_checked(xloc['edit_member_wlan_vlan_tag'] % wlan_name):
                    wgs_cfg['wlan_member'][wlan_name]['vlan_override'] = "Tag"

                else:
                    raise Exception("Unexpect Vlan Override settings")

                if wgs_cfg['wlan_member'][wlan_name]['vlan_override'] == "Tag":
                    wgs_cfg['wlan_member'][wlan_name]['tag_override'] = zd.s.get_value(xloc['edit_member_wlan_tag_override'] % wlan_name)

    zd.s.click_and_wait(xloc['edit_Cancel'], pause)

    return wgs_cfg


#
# Set Wlan Group configuration.
# Note: Do not call this function directly for how to call this function)
#
def set_wlan_group_cfg(zd, wgs_cfg, wlan_list, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    if zd.s.is_visible(xloc['edit_name']):
        zd.s.type_text(xloc['edit_name'], wgs_cfg['name'])

    if zd.s.is_visible(xloc['edit_description']):
        zd.s.type_text(xloc['edit_description'], wgs_cfg['description'])

    vo_loc = xloc['edit_member_vlan_override']
    if vo_loc:
        zd.s.click_and_wait(vo_loc)
        time.sleep(pause)

    # uncheck all wlan member
    for uncheck_wlan_name in wlan_list:        
        try:
            zd.s.click_if_checked(xloc['edit_member_vlan_wlan'] % (uncheck_wlan_name))

        except:
            _search_wlan_members_by_wlan_name(zd, uncheck_wlan_name)
            zd.s.click_if_checked(xloc['edit_member_vlan_wlan'] % (uncheck_wlan_name))
           
    # check the wlanmembers
    if wgs_cfg.get('wlan_member'):
        for check_wlan_name in wgs_cfg['wlan_member'].keys():
            try:
                zd.s.click_and_wait(xloc['edit_member_vlan_wlan'] % (check_wlan_name))

            except:
                _search_wlan_members_by_wlan_name(zd, check_wlan_name)
                zd.s.click_and_wait(xloc['edit_member_vlan_wlan'] % (check_wlan_name))

            if wgs_cfg['vlan_override']:
                if wgs_cfg['wlan_member'][check_wlan_name]['vlan_override'] == "No Change":
                    zd.s.click_and_wait(xloc['edit_member_wlan_vlan_no_change'] % check_wlan_name)

                elif wgs_cfg['wlan_member'][check_wlan_name]['vlan_override'] == "Untag":
                    zd.s.click_and_wait(xloc['edit_member_wlan_vlan_untag'] % check_wlan_name)

                elif wgs_cfg['wlan_member'][check_wlan_name]['vlan_override'] == "Tag":
                    zd.s.click_and_wait(xloc['edit_member_wlan_vlan_tag'] % check_wlan_name, pause)
                    zd.s.type_text(xloc['edit_member_wlan_tag_override'] % check_wlan_name, wgs_cfg['wlan_member'][check_wlan_name]['tag_override'])

                else:
                    raise Exception("Unexpect Vlan Override settings")

#
# Edit Wlan Group Configuration
#
def edit_wlan_group_cfg(zd, wlan_group, wgs_cfg, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    wlan_list = wlan.get_wlan_list(zd)

    _nav_to_cfg(zd)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd.s.click_and_wait(xloc['show_more_button'])

    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_group)
    zd.s.click_and_wait(loc_edit_wg_by_name)
    time.sleep(pause)

    set_wlan_group_cfg(zd, wgs_cfg, wlan_list)

    zd.s.click_and_wait(xloc['edit_OK'])

    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
#        if re.search('Please enter a different name', _alert, re.I):
#            raise Exception(_alert)
        raise Exception(_alert)

    time.sleep(pause)


#
# Create New Wlan Group Configuration
#
def create_new_wlan_group(zd, wgs_cfg, pause = 1.0,add_wlan=True,add_wlan_list=[]):
    xloc = LOCATORS_CFG_WLANGROUPS
    if not add_wlan:
        wlan_list=[]
    elif not add_wlan_list:
        wlan_list = wlan.get_wlan_list(zd)
    else:
        wlan_list=add_wlan_list

    _nav_to_cfg(zd)
    time.sleep(3*pause)

    zd.s.click_and_wait(xloc['create_new'])
    time.sleep(pause)

    set_wlan_group_cfg(zd, wgs_cfg, wlan_list)

    zd.s.click_and_wait(xloc['edit_OK'])

    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        if re.search('Please enter a different name', _alert, re.I):
            raise Exception(_alert)

    time.sleep(pause)

#
# Get Wlan Group List
#

def get_wlan_groups_list(zd, pause = 1.0, is_nav = True):
    xloc = LOCATORS_CFG_WLANGROUPS
    if is_nav:
        _nav_to_cfg(zd)
        time.sleep(pause)

    # Show all wlan group on one page
    _show_all(zd.s)

    wgs_list = []
    tot_wgs = zd.s.get_text(xloc['get_totals'])
    tot_wgs = tot_wgs.split()[-1].split("(")[-1].split(")")[0]
    for i in range(int(tot_wgs)):
        wgs_name = zd.s.get_text(xloc['get_wgs_name'] % str(i))
        wgs_list.append(wgs_name)

    time.sleep(pause)

    return wgs_list


def get_wlan_group_cfg_2(zd, group_name, pause = 1, is_nav = True, ):
    '''
    . The main purpose of this function is to get wlan members of a group
    to support verify ZD template (from FM).
    . return:
    a dict(
        name = 'group name',
        description = 'description',
        wlan_member = [list of wlan members],
        vlan_override = True | False,
        vlan_override = dict(
            name_of_wlan_mem_1 = dict(
                vlan_cfg = nochange | untag |tag,
                tag = 'tag value in int', (only present if vlan_cfg = tag)
            ),
        ),
    )
    Note: No function uses vlan override for now.
          The return doesn't support to get config "vlan_override".
    '''
    # get table
    l = LOCATORS_CFG_WLANGROUPS
    tbl = l['wlan_member_tbl']
    group_cfg = dict(
        name = '',
        description = 'description',
        wlan_member = [],
        vlan_override = None,
    )

    if is_nav:
        _nav_to_cfg(zd)
        time.sleep(pause)
    # Show all wlan group on one page
    _show_all(zd.s)

    zd.s.click_and_wait(l['doEdit'] % (group_name))
    time.sleep(pause)

    # get the wlan member list of this group
    mem_list, hds = [], zd.s.get_tbl_hdrs_by_attr(l['wlan_member_tbl'])
    for r in zd.s.iter_table_rows(tbl, hds):
        wlan_chk_tmpl, wlan_name = l['wlan_member_chk_tmpl'], r['row']['wlans']
        if zd.s.is_checked(wlan_chk_tmpl % wlan_name):
            mem_list.append(wlan_name)

    group_cfg['name'] = group_name
    group_cfg['description'] = zd.s.get_value(l['edit_description'])

    vo_loc = l['edit_member_vlan_override']
    if vo_loc:
        group_cfg['vlan_override'] = zd.s.is_checked(vo_loc)

    else:
        group_cfg['vlan_override'] = True

    group_cfg['wlan_member'] = mem_list

    return group_cfg

def get_all_wlan_group_cfgs(zd, is_nav = True):
    '''
    to get all wlan group cfgs
    '''
    group_list = get_wlan_groups_list(zd, is_nav = is_nav)
    cfg_list = []
    for g in group_list:
        cfg_list.append(get_wlan_group_cfg_2(zd, g, is_nav = is_nav))

    return cfg_list



#Added by Serena Tan, 2010.10.27.
def get_all_wlan_group_cfgs_2(zd, is_nav = True):
    '''
    to get all wlan group cfgs, with the cfgs of "vlan_override".
    '''
    group_list = get_wlan_groups_list(zd, is_nav = is_nav)
    cfg_dict = {}

    for g in group_list:
        cfg_dict[g] = get_wlan_group_cfg(zd, g)

    return cfg_dict


#-------------------------------------------------------------------------------
#                        UN-PUBLIC METHODs
def _show_all(se):
    button = LOCATORS_CFG_WLANGROUPS['show_more_button']
    while se.is_visible(button):
        se.click_and_wait(button)

#Create the steps by Jacky Luh@2011-07-22
#Search the wlan in the wlan member list of the wlangroup.
def _search_wlan_members_by_wlan_name(zd, wlan_name, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    search_terms_input = xloc['search_terms_input']
    if zd.s.is_element_present(search_terms_input):
        zd.s.type_text(search_terms_input, '')
        time.sleep(pause)
        zd.s.type_text(search_terms_input, wlan_name)
        time.sleep(0.2)
        zd.s.type_keys(search_terms_input, '\013')
        time.sleep(pause)

def _search_wlan_group(zd, wlan_group_name, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    search_terms_input = xloc['search_wlangroup_input']
    if zd.s.is_element_present(search_terms_input):
        zd.s.type_text(search_terms_input, '')
        time.sleep(pause)
        zd.s.type_keys(search_terms_input, wlan_group_name)
        time.sleep(1)

feature_update = {
    '9.5.0.0': {
        'LOCATORS_CFG_WLANGROUPS': {
            'edit_member_vlan_override': r'',
            'edit_member_wlan_name':r"//table[@id='wgwlan']//td[text()='%s']/../td[2]",
            'edit_member_wlan_original_vlan':r"//table[@id='wgwlan']//td[text()='%s']/../td[3]",
            'edit_member_vlan_wlan':r"//table[@id='wgwlan']//td[text()='%s']/..//input[@type='checkbox']",
            'edit_member_wlan_vlan_no_change':r"//table[@id='wgwlan']//td[text()='%s']/..//input[contains(@id,'vo-asis')]",
            'edit_member_wlan_vlan_untag':r"//table[@id='wgwlan']//td[text()='%s']/..//input[contains(@id,'vo-untag')]",
            'edit_member_wlan_vlan_tag':r"//table[@id='wgwlan']//td[text()='%s']/..//input[contains(@id,'vo-tag')]",
            'edit_member_wlan_tag_override':r"//table[@id='wgwlan']//td[text()='%s']/..//input[@type='text']",
            'wlan_member_tbl':r"//table[@id='wgwlan']",
            'wlan_member_chk_tmpl':r"//table[@id='wgwlan']//td[text()='%s']/..//input[@type='checkbox']",
        },
    },
}

# mainline build prior to 9.2.0.0 production
# this can be removed any time when we no longer test mainline builds of 9.2


