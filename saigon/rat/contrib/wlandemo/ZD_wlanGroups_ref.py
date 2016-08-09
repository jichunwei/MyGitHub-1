import logging
import re
import time

from RuckusAutoTest.components.lib.zd import widgets_zd as WGT
from RuckusAutoTest.components.lib.zd import access_points_zd as AP
from RuckusAutoTest.components.lib.zd import wlan_zd as WLAN

import RuckusAutoTest.common.lib_Debug as bugme

LOCATORS_CFG_WLANS = dict(
    create_new = r"//table[@id='wlan']//span[contains(@id,'new-wlan')]",
    # doEdit = r"//table[@id='wlan']//tr/td[text()='wlan-shared']/../td/span[text()='Edit']",
    doEdit = r"//table[@id='wlan']//tr/td[text()='%s']/../td/span[text()='Edit']",
)

LOCATORS_CFG_WLANGROUPS = dict(
    select_all = r"//table[@id='wgroup']//input[@id='wgroup-sall']",

    check_name_default = r"//table[@id='wgroup']//tr/td[text()='Default']/../td/input[@name='wgroup-select']",
    check_name = r"//table[@id='wgroup']//tr/td[text()='%s']/../td/input[@name='wgroup-select']",
    create_new = r"//table[@id='wgroup']//span[contains(@id,'new-wgroup')]",
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
    edit_member_vlan_override = r"//form[@id='form-wgroup']//input[@id='has-vlan']",
    edit_member_vlan_wlan = r"//table[@id='wlanTable']//td/label[text()='%s']/../input",

    edit_OK = r"//form[@id='form-wgroup']//input[@id='ok-wgroup']",
    edit_Cancel = r"//form[@id='form-wgroup']//input[@id='cancel-wgroup']",

    show_more_button = "//table[@id='wgroup']//input[@id='showmore-wgroup']",

    edit_member_wlan_name = r"//table[@id='wlanTable']//tr/td/label[text()='%s']/../../td[1]",
    edit_member_wlan_original_vlan = r"//table[@id='wlanTable']//tr/td/label[text()='%s']/../../td[2]",
    edit_member_wlan_vlan_no_change = r"//table[@id='wlanTable']//tr/td/label[text()='%s']/../../td[3]/input[contains(following-sibling::label, 'No Change')]",
    edit_member_wlan_vlan_untag = r"//table[@id='wlanTable']//tr/td/label[text()='%s']/../../td[3]/input[contains(following-sibling::label, 'Untag')]",
    edit_member_wlan_vlan_tag = r"//table[@id='wlanTable']//tr/td/label[text()='%s']/../../td[3]/input[contains(following-sibling::label, 'Tag')]",
    edit_member_wlan_tag_override = r"//table[@id='wlanTable']//tr/td/label[text()='%s']/../../td[3]/input[@type = 'text']"
)

LOCATORS_MON_WLANGROUPS = dict(
    #check_detail_by_name = r"//table[@id='wlangroupsummary']//td/a[text()='wlan-22na']"MONITOR_CURRENTLY_ACTIVE_CLIENTS',
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
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    loc_edit_wg_by_name = xloc['doEdit'] % ('Default')
    zd._click(loc_edit_wg_by_name)
    time.sleep(pause)
    loc_edit_wg_wlan = xloc['edit_member_vlan_wlan'] % (wlan_name)
    if check:
        zd.s.check(loc_edit_wg_wlan)
    else:
        zd.s.uncheck(loc_edit_wg_wlan)
    time.sleep(pause)
    zd._click(xloc['edit_OK'])
    time.sleep(pause)
    zd._logout()


def cfg_wlan_member(zd, wlangroup_name, wlan_name, check = False, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    loc_edit_wg_by_name = xloc['doEdit'] % (wlangroup_name)
    zd._click(loc_edit_wg_by_name)
    time.sleep(pause)
    loc_edit_wg_wlan = xloc['edit_member_vlan_wlan'] % (wlan_name)
    if check:
        zd.s.check(loc_edit_wg_wlan)
    else:
        zd.s.uncheck(loc_edit_wg_wlan)
    time.sleep(pause)
    zd._click(xloc['edit_OK'])
    time.sleep(pause)
    zd._logout()


def cfg_wlan_group_members(zd, wlangroup_name, wlan_name_list, check = False, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    loc_edit_wg_by_name = xloc['doEdit'] % (wlangroup_name)
    zd._click(loc_edit_wg_by_name)
    time.sleep(pause)
    for wlan_name in wlan_name_list:
        loc_edit_wg_wlan = xloc['edit_member_vlan_wlan'] % (wlan_name)
        if check:
            zd.s.check(loc_edit_wg_wlan)
        else:
            zd.s.uncheck(loc_edit_wg_wlan)
        time.sleep(pause)

    zd._click(xloc['edit_OK'])
    time.sleep(pause)
    zd._logout()


def edit_wlan_group(zd, wlan_group, new_wlan_group = '', description = '', pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_group)
    zd._click(loc_edit_wg_by_name)
    time.sleep(pause)
    if new_wlan_group:
        zd._type_text(xloc['edit_name'], new_wlan_group)
    zd._type_text(xloc['edit_description'], description)
    zd._click(xloc['edit_OK'])
    if zd.s.is_alert_present():
        _alert = zd.s.get_alert()
        if not re.search('Please enter a different name', _alert, re.I):
            raise Exception(_alert)

    time.sleep(pause)
    zd._logout()


def create_wlan_group(zd, wlan_group, wlan_name, check_VLAN_override = False, description = ''):
    xloc = LOCATORS_CFG_WLANGROUPS
    logging.info("Create [wlangroup %s] with-memeber [wlan %s]" % (wlan_group, wlan_name))
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    if not WGT.is_enabled_to_click(zd, xloc['create_new']):
        raise Exception("Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported")

    zd._click(xloc['create_new'])
    zd._type_text(xloc['edit_name'], wlan_group)
    zd._type_text(xloc['edit_description'], description)
    if check_VLAN_override:
        zd.s.check(xloc['edit_member_vlan_override'])
    else:
        zd.s.uncheck(xloc['edit_member_vlan_override'])
    if type(wlan_name) is list:
        for wlan in wlan_name:
            zd.s.check(xloc['edit_member_vlan_wlan'] % wlan)
    else:
        zd.s.check(xloc['edit_member_vlan_wlan'] % (wlan_name))
    zd._click(xloc['edit_OK'])
    zd._logout()


#
# Create a series Wlan Group & check all Wlans in each WlanGroup
#
def create_multi_wlan_groups(zd, wlan_group, wlan_name, check_VLAN_override = False, description = '', num_of_wgs = 1, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    logging.info("Create %d WLAN Group(s) with-memeber [wlan %s]" % (num_of_wgs, wlan_name))
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    for i in range(num_of_wgs):
        wgs_name = "%s-%d" % (wlan_group, i + 1)
        if num_of_wgs == 1:
            wgs_name = wlan_group
        logging.info("Create [wlangroup %s] with-memeber [wlan %s]" % (wgs_name, wlan_name))
        if not zd.s.is_visible(xloc['create_new']):
            msg = "Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported"
            zd._logout()
            raise Exception("Can't create new WLAN Groups because ZD reachs maximum number of wlangroup supported")

        zd._click(xloc['create_new'])
        zd._type_text(xloc['edit_name'], wgs_name)
        zd._type_text(xloc['edit_description'], description)
        if check_VLAN_override:
            zd.s.check(xloc['edit_member_vlan_override'])
        else:
            zd.s.uncheck(xloc['edit_member_vlan_override'])
        if type(wlan_name) is list:
            for wlan in wlan_name:
                zd.s.check(xloc['edit_member_vlan_wlan'] % wlan)
        else:
            zd.s.check(xloc['edit_member_vlan_wlan'] % (wlan_name))
        zd._click(xloc['edit_OK'])
        time.sleep(pause)
    zd._logout()


def get_wlan_group_of_member(zd, wlan_group_name, member_wlan_name, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    result = {'name': wlan_group_name, 'wlan_member': {'name': member_wlan_name}}
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])

    zd._click(xloc['doEdit'] % wlan_group_name)
    result['name'] = zd._get_value(xloc['edit_name'])
    result['description'] = zd._get_value(xloc['edit_description'])
    result['vlan_overwrite'] = WGT.get_checkbox_boolean(zd, xloc['edit_member_vlan_override'])
    result['wlan_member']['checked'] = WGT.get_checkbox_boolean(zd, xloc['edit_member_vlan_wlan'] % (member_wlan_name))
    zd._logout()

    return result


# Remove all config from ZD:
#
#   from ratenv import *
#   import ZoneDirector_WlanGroups as wgs
#   tb = initRatEnv('wgs.demo')
#   zd = tb.components['ZoneDirector']
#   wgs.remove_wlan_groups(zd, tb.getAPsSymDictAsMacAddrList())
#   zd.remove_all_cfg()
#
def remove_wlan_groups(zd, ap_mac_addrList = [], z_pauseDelete = 4, pause = 1.0):
    if ap_mac_addrList:
        AP.default_wlan_groups_by_mac_addr(zd, ap_mac_addrList)
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    tot_wgs = zd._get_text(xloc['get_totals'])
    if tot_wgs.find('(1)') > 0:
        logging.info('No wlan groups to delete')
        zd._logout()
        return
    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])

    zd._click(xloc['select_all'])
    zd.s.uncheck(xloc['check_name_default'])
    zd.s.choose_ok_on_next_confirmation()
    zd._click(xloc['doDelete'])
    time.sleep(z_pauseDelete)
    if zd.s.is_confirmation_present():
        zd.s.get_confirmation()
    if zd.s.is_alert_present():
        _alert = zd.s.get_alert()
        if not re.search('Nothing\s+is\s+selected', _alert, re.I):
            raise Exception(_alert)
    zd._logout()


#
# Monitor>WLANs>WlanGroups
#
def get_status_ex_by_ap_mac_addr(zd, wgs_name, macAddr):
    xloc = LOCATORS_MON_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.MONITOR, zd.MONITOR_WLAN)
    zd._click(xloc['check_detail_by_name'] % wgs_name)
    result = {'wgs_name': wgs_name, 'mac': macAddr}
    for xid in ['model', 'status', 'ip_addr', 'channel', 'clients', 'description']:
        locid = 'get_member_ap_%s_by_mac' % xid
        result[xid] = zd._get_text(xloc[locid] % macAddr)
    zd._logout()
    return result


#
# Clone a Wlangroup from an exist wlan
#
def clone_wlan_group(zd, wlan_group, new_wlan_group, description = '', pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    logging.info("Clone [wlangroup %s] to [new wlangroup %s]" % (wlan_group, new_wlan_group))
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    # Show all wlan group on one page to clone
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])

    logging.info("Find [wlangroup %s] to clone in WLAN Groups table" % wlan_group)
    clone = xloc['doClone'] % (wlan_group)
    if zd._check_element_present(clone):
        zd._click(clone)
        zd._type_text(xloc['edit_name'], new_wlan_group)
        zd._type_text(xloc['edit_description'], description)
        zd._click(xloc['edit_OK'])

        if zd.s.is_alert_present():
            _alert = zd.s.get_alert()
            if not re.search('Please enter a different name', _alert, re.I):
                raise Exception(_alert)

    else:
        logging.debug("Can't find [wlangroup %s] in WLAN Groups table" % wlan_group)

    zd._logout()


#
# Get current total number of Wlan Group on ZD
#
def get_total_wlan_groups(zd):
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)
    tot_wgs = int(zd._get_total_number(xloc['get_totals'], "wgroup"))
    logging.info("Current total Wlan Group on ZD %d " % tot_wgs)
    zd._logout()

    return tot_wgs

def find_wlan_group(zd, wlan_group, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    logging.info("find [wlangroup %s] in Wlan Group Table" % (wlan_group))
    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])
        time.sleep(pause)
    find_result = False

    if zd._check_element_present(xloc['get_name'] % wlan_group):
        find_result = True
    zd._logout()
    return find_result


#
# Remove all wlans out of wlan group
#
def remove_wlan_members_fromgmt_vlan_group(zd, wlan_group_name, wlan_name_list):
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
    xloc = LOCATORS_CFG_WLANGROUPS
    wlan_list = WLAN.get_wlan_list(zd)

    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])

    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_group)
    zd._click(loc_edit_wg_by_name)
    time.sleep(pause)
    wgs_cfg['name'] = wlan_group
    wgs_cfg['description'] = zd._get_value(xloc['edit_description'])
    wgs_cfg['vlan_override'] = WGT.get_checkbox_boolean(zd, xloc['edit_member_vlan_override'])

    # get detail wlan_member vlan
    for wlan_name in wlan_list:
        is_wlan_member = WGT.get_checkbox_boolean(zd, xloc['edit_member_vlan_wlan'] % (wlan_name))
        if is_wlan_member:
            wgs_cfg['wlan_member'][wlan_name] = dict()
            if wgs_cfg['vlan_override']:
                wgs_cfg['wlan_member'][wlan_name]['original_vlan'] = zd._get_text(xloc['edit_member_wlan_original_vlan'] % wlan_name)
                if zd._is_checked(xloc['edit_member_wlan_vlan_no_change'] % wlan_name):
                    wgs_cfg['wlan_member'][wlan_name]['vlan_override'] = "No Change"
                elif zd._is_checked(xloc['edit_member_wlan_vlan_untag'] % wlan_name):
                    wgs_cfg['wlan_member'][wlan_name]['vlan_override'] = "Untag"
                elif zd._is_checked(xloc['edit_member_wlan_vlan_tag'] % wlan_name):
                    wgs_cfg['wlan_member'][wlan_name]['vlan_override'] = "Tag"
                else:
                    raise Exception("Unexpect Vlan Override settings")

                if wgs_cfg['wlan_member'][wlan_name]['vlan_override'] == "Tag":
                    wgs_cfg['wlan_member'][wlan_name]['tag_override'] = zd._get_value(xloc['edit_member_wlan_tag_override'] % wlan_name)
    zd._click(xloc['edit_Cancel'])
    time.sleep(pause)
    zd._logout()

    return wgs_cfg


#
# Set Wlan Group configuration.
# Note: Do not call this function directly for how to call this function)
#
def set_wlan_group_cfg(zd, wgs_cfg, wlan_list, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    if zd.s.is_visible(xloc['edit_name']):
        zd._type_text(xloc['edit_name'], wgs_cfg['name'])
    if zd.s.is_visible(xloc['edit_description']):
        zd._type_text(xloc['edit_description'], wgs_cfg['description'])

    if wgs_cfg['vlan_override']:
        zd._click(xloc['edit_member_vlan_override'])
        time.sleep(pause)

    # uncheck all wlan member
    for wlan_name in wlan_list:
        zd.s.uncheck(xloc['edit_member_vlan_wlan'] % (wlan_name))

    for wlan_name in wgs_cfg['wlan_member'].keys():
        zd._click(xloc['edit_member_vlan_wlan'] % (wlan_name))
        if wgs_cfg['vlan_override']:
            if wgs_cfg['wlan_member'][wlan_name]['vlan_override'] == "No Change":
                zd._click(xloc['edit_member_wlan_vlan_no_change'] % wlan_name)
            elif wgs_cfg['wlan_member'][wlan_name]['vlan_override'] == "Untag":
                zd._click(xloc['edit_member_wlan_vlan_untag'] % wlan_name)
            elif wgs_cfg['wlan_member'][wlan_name]['vlan_override'] == "Tag":
                zd._click(xloc['edit_member_wlan_vlan_tag'] % wlan_name)
                time.sleep(pause)
                zd._type_text(xloc['edit_member_wlan_tag_override'] % wlan_name, wgs_cfg['wlan_member'][wlan_name]['tag_override'])
            else:
                raise Exception("Unexpect Vlan Override settings")


#
# Edit Wlan Group Configuration
#
def edit_wlan_group_cfg(zd, wlan_group, wgs_cfg, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    wlan_list = WLAN.get_wlan_list(zd)

    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])

    loc_edit_wg_by_name = xloc['doEdit'] % (wlan_group)
    zd._click(loc_edit_wg_by_name)
    time.sleep(pause)

    set_wlan_group_cfg(zd, wgs_cfg, wlan_list)

    zd._click(xloc['edit_OK'])

    if zd.s.is_alert_present():
        _alert = zd.s.get_alert()
        if re.search('Please enter a different name', _alert, re.I):
            raise Exception(_alert)

    time.sleep(pause)
    zd._logout()


#
# Create New Wlan Group Configuration
#
def create_new_wlan_group(zd, wgs_cfg, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    wlan_list = WLAN.get_wlan_list(zd)

    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    zd._click(xloc['create_new'])
    time.sleep(pause)

    set_wlan_group_cfg(zd, wgs_cfg, wlan_list)

    zd._click(xloc['edit_OK'])

    if zd.s.is_alert_present():
        _alert = zd.s.get_alert()
        if re.search('Please enter a different name', _alert, re.I):
            raise Exception(_alert)

    time.sleep(pause)
    zd._logout()


#
# Get Wlan Group List
#

def get_wlan_groups_list(zd, pause = 1.0):
    xloc = LOCATORS_CFG_WLANGROUPS
    zd.do_login()
    zd._navigate_to(zd.CONFIGURE, zd.CONFIGURE_WLANS)

    # Show all wlan group on one page
    time.sleep(pause)
    while zd.s.is_visible(xloc['show_more_button']):
        zd._click(xloc['show_more_button'])

    wgs_list = []
    tot_wgs = zd._get_text(xloc['get_totals'])
    tot_wgs = tot_wgs.split()[-1].split("(")[-1].split(")")[0]
    for i in range(int(tot_wgs)):
        wgs_name = zd._get_text(xloc['get_wgs_name'] % str(i))
        wgs_list.append(wgs_name)
    time.sleep(pause)
    zd._logout()

    return wgs_list

