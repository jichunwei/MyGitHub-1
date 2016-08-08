import logging
import re
import time

from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.common import lib_Constant as CONST
from RuckusAutoTest.common import utils

LOCATORS_CFG_ACCESS_CONTROL = dict(
    # Configure -> Access Control

    access_controls_span = '//span[contains(@id,"configure_acls")]',

    # L2 ACL
    l2acl_create_new = '//span[@id="new-acl"]',
    l2acl_name_textbox = '//input[@id="name"]',
    l2acl_desc_textbox = '//input[@id="description"]',
    l2acl_allowall_radio = '//input[@id="allowAll"]',
    l2acl_denyall_radio = '//input[@id="denyAll"]',
    l2acl_mac_textbox = '//input[@id="mac"]',
    l2acl_createnew_station_button = '//input[@id="create-new-station"]',
    l2acl_mac_table = '//table[@id="staTable"]',
    l2acl_mac_addr_cell = '//table[@id="staTable"]//tr[$_$]/td[1]',
    l2acl_mac_delete_span = '//table[@id="staTable"]//tr[$_$]/td[2]/span[@id="delete"]',
    l2acl_delete_mac = '//table[@id="staTable"]//span[@id="delete"]',
    l2acl_name_cell = '//table[@id="acl"]//tr[$_$]/td[2]',

    clone_l2acl = '//table[@id="acl"]//tr/td[text()="%s"]/../td/span[text()="Clone"]',
    edit_l2acl = '//table[@id="acl"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',

    l2acl_all_checkbox = '//input[@id="acl-sall"]',
    l2acl_checkbox = '//table[@id="acl"]//tr/td[text()="%s"]/../td[1]/input',
    l2acl_show_more_button = "//input[@id='showmore-acl']",
    l2acl_cancel_button = '//input[@id="cancel-acl"]',
    l2acl_ok_button = '//input[@id="ok-acl"]',
    l2acl_delete_button = '//input[@id="del-acl"]',
    total_l2acls = '//div[@id="actions-acl"]/span',

    # L3/L4 ACL
    l3acl_create_new = '//span[@id="new-policy"]',
    l3acl_name_textbox = '//input[@id="policy-name"]',
    l3acl_desc_textbox = '//input[@id="policy-description"]',
    l3acl_allowall_radio = '//input[@id="policy-allowAll"]',
    l3acl_denyall_radio = '//input[@id="policy-denyAll"]',

    l3acl_all_rules_checkbox = '//input[@id="rule-sall"]',
    l3acl_createnew_rule = '//span[@id="new-rule"]',
    l3acl_rule_table = '//table[@id="rule"]',
    l3acl_rule_checkbox = '//table[@id="rule"]//tr/td[text()="%s"]/../td[1]',
    
    # Rule Information
    l3acl_rule_order = '//table[@id="rule"]//tr/td[text()="%s"]/../td[2]',
    l3acl_rule_description = '//table[@id="rule"]//tr/td[text()="%s"]/../td[3]',
    l3acl_rule_type = '//table[@id="rule"]//tr/td[text()="%s"]/../td[4]',
    l3acl_rule_dest_addr = '//table[@id="rule"]//tr/td[text()="%s"]/../td[5]',
    l3acl_rule_application = '//table[@id="rule"]//tr/td[text()="%s"]/../td[6]',
    l3acl_rule_protocol = '//table[@id="rule"]//tr/td[text()="%s"]/../td[7]',
    l3acl_rule_dest_port = '//table[@id="rule"]//tr/td[text()="%s"]/../td[8]',
    l3acl_rule_edit_button = '//table[@id="rule"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',
    l3acl_rule_clone_button = '//table[@id="rule"]//tr/td[text()="%s"]/../td/span[text()="Clone"]',
    l3acl_rule_move_up_button = '//table[@id="rule"]//tr/td[text()="%s"]/../td[9]/img[1]',
    l3acl_rule_move_down_button = '//table[@id="rule"]//tr/td[text()="%s"]/../td[9]/img[2]',

    # Rule Configuration
    l3acl_rule_order_listbox = '//select[@id="rule-id"]',
    l3acl_rule_description_textbox = '//input[@id="rule-description"]',
    l3acl_rule_type_listbox = '//select[@id="rule-action"]',
    l3acl_rule_dest_addr_textbox = '//input[@id="rule-dst-addr"]',
    l3acl_rule_application_listbox = '//select[@id="rule-app"]',
    l3acl_rule_protocol_textbox = '//input[@id="rule-protocol"]',
    l3acl_rule_dest_port_textbox = '//input[@id="rule-dst-port"]',

    l3acl_rule_delete_button = '//input[@id="del-rule"]',
    l3acl_rule_save_button = '//input[@id="ok-rule"]',
    l3acl_rule_cancel_button = '//input[@id="cancel-rule"]',

    clone_l3acl = '//table[@id="policy"]//tr//td[text()="%s"]//..//span[text()="Clone"]',
    edit_l3acl = '//table[@id="policy"]//tr//td[text()="%s"]//..//span[text()="Edit"]',

    l3acl_name_cell = '//table[@id="policy"]//tr[@idx="%s"]/td[2]',
    l3acl_all_checkbox = '//input[@id="policy-sall"]',
    l3acl_checkbox = '//table[@id="policy"]//tr/td[text()="%s"]/../td[1]/input',
    l3acl_show_more_button = "//input[@id='showmore-policy']",
    l3acl_cancel_button = '//input[@id="cancel-policy"]',
    l3acl_ok_button = '//input[@id="ok-policy"]',
    l3acl_delete_button = '//input[@id="del-policy"]',
    total_l3acls = '//div[@id="actions-policy"]/span',
    
    # L3/L4 IPV6 ACL
    l3acl_ipv6_create_new = '//span[@id="new-policy6"]',
    l3acl_ipv6_name_textbox = '//input[@id="policy6-name"]',
    l3acl_ipv6_desc_textbox = '//input[@id="policy6-description"]',
    l3acl_ipv6_allowall_radio = '//input[@id="policy6-allowAll"]',
    l3acl_ipv6_denyall_radio = '//input[@id="policy6-denyAll"]',

    l3acl_ipv6_all_rules_checkbox = '//input[@id="rule6-sall"]',
    l3acl_ipv6_createnew_rule = '//span[@id="new-rule6"]',
    l3acl_ipv6_rule_table = '//table[@id="rule6"]',
    l3acl_ipv6_rule_checkbox = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[1]',
    
    # Rule Information
    l3acl_ipv6_rule_order = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[2]',
    l3acl_ipv6_rule_description = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[3]',
    l3acl_ipv6_rule_type = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[4]',
    l3acl_ipv6_rule_dest_addr = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[5]',
    l3acl_ipv6_rule_application = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[6]',
    l3acl_ipv6_rule_protocol = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[7]',
    l3acl_ipv6_rule_dest_port = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[8]',
    l3acl_ipv6_rule_icmp_type = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[9]',
    l3acl_ipv6_rule_edit_button = '//table[@id="rule6"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',
    l3acl_ipv6_rule_clone_button = '//table[@id="rule6"]//tr/td[text()="%s"]/../td/span[text()="Clone"]',
    l3acl_ipv6_rule_move_up_button = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[10]/img[1]',
    l3acl_ipv6_rule_move_down_button = '//table[@id="rule6"]//tr/td[text()="%s"]/../td[10]/img[2]',

    # Rule Configuration
    l3acl_ipv6_rule_order_listbox = '//select[@id="rule6-id"]',
    l3acl_ipv6_rule_description_textbox = '//input[@id="rule6-description"]',
    l3acl_ipv6_rule_type_listbox = '//select[@id="rule6-action"]',
    l3acl_ipv6_rule_dest_addr_textbox = '//input[@id="rule6-dst-addr"]',
    l3acl_ipv6_rule_application_listbox = '//select[@id="rule6-app"]',
    l3acl_ipv6_rule_protocol_textbox = '//input[@id="rule6-protocol"]',
    l3acl_ipv6_rule_dest_port_textbox = '//input[@id="rule6-dst-port"]',
    l3acl_ipv6_rule_icmp_type_textbox = '//input[@id="rule6-icmp-type"]',
    
    l3acl_ipv6_rule_advanced_option = "//div[@id='actions-rule6']/a",

    l3acl_ipv6_rule_delete_button = '//input[@id="del-rule6"]',
    l3acl_ipv6_rule_save_button = '//input[@id="ok-rule6"]',
    l3acl_ipv6_rule_cancel_button = '//input[@id="cancel-rule6"]',

    clone_l3acl_ipv6 = '//table[@id="policy6"]//tr//td[text()="%s"]//..//span[text()="Clone"]',
    edit_l3acl_ipv6 = '//table[@id="policy6"]//tr//td[text()="%s"]//..//span[text()="Edit"]',

    l3acl_ipv6_name_cell = '//table[@id="policy6"]//tr[@idx="%s"]/td[2]',
    l3acl_ipv6_all_checkbox = '//input[@id="policy6-sall"]',
    l3acl_ipv6_checkbox = '//table[@id="policy6"]//tr/td[text()="%s"]/../td[1]/input',
    l3acl_ipv6_show_more_button = "//input[@id='showmore-policy6']",
    l3acl_ipv6_cancel_button = '//input[@id="cancel-policy6"]',
    l3acl_ipv6_ok_button = '//input[@id="ok-policy6"]',
    l3acl_ipv6_delete_button = '//input[@id="del-policy6"]',
    total_l3acls_ipv6 = '//div[@id="actions-policy6"]/span',
)

###
## L2 ACL
###

def _cfg_l2_acl_policy(zd, acl_conf, delete_old_mac_list = False):
    """
    This function adds a new ACL rule to the Access Controls table.
    Input:
        zd:        the Zone Director object
        acl_conf : the dictionary of the configuration of an ACL Policy, includes:
            acl_name:        the name of the ACL policy
            description:     the description
            allowed_access:  the policy of the ACL,
                                True for 'Only allow all stations listed below'
                                False for 'Only deny all stations listed below'
            mac_list:        the list of mac addresses will be apply to policy
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    acl_config = dict(acl_name = '',
                       description = '',
                       allowed_access = True,
                       mac_list = [])
    acl_config.update(acl_conf)

    if acl_config['acl_name']:
        zd.s.type_text(xlocs['l2acl_name_textbox'], acl_config['acl_name'])

    if acl_config['description']:
        zd.s.type_text(xlocs['l2acl_desc_textbox'], acl_config['description'])

    if acl_config['allowed_access']:
        zd.s.click(xlocs['l2acl_allowall_radio'])
    else:
        zd.s.click(xlocs['l2acl_denyall_radio'])

    if acl_config['mac_list']:
        if delete_old_mac_list:
            # Delete all existing mac
            _delete_all_mac_on_l2_acl_policy(zd)
        # Assign the mac list to the ACL policy
        _assign_mac_to_l2_acl_policy(zd, acl_config['mac_list'])

    zd.s.click_and_wait(xlocs['l2acl_ok_button'])
    zd.s.get_alert(xlocs['l2acl_cancel_button'])

def _assign_mac_to_l2_acl_policy(zd, mac_list, pause = 1):
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    for mac in mac_list:
        zd.s.type_text(xlocs['l2acl_mac_textbox'], mac)
        zd.s.click_and_wait(xlocs['l2acl_createnew_station_button'])
        zd.s.get_alert(xlocs['l2acl_cancel_button'])
        time.sleep(pause)

def _delete_all_mac_on_l2_acl_policy(zd):
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    del_button = xlocs['l2acl_delete_mac']
    while zd.s.is_element_present(del_button):
        zd.s.click(del_button)

def create_l2_acl_policy(zd, acl_conf, pause = 1):
    """
    Create one new ACL policy base on the input parameters
    Input:
        zd:        the Zone Director object
        acl_conf : the dictionary of the configuration of an ACL Policy
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036             
    try:
        if wgt.is_enabled_to_click(zd, xlocs['l2acl_create_new']):
            zd.s.click_and_wait(xlocs['l2acl_create_new'])
        else:
            raise Exception('The "Create New" button is disabled')

        _cfg_l2_acl_policy(zd, acl_conf)
        time.sleep(pause)
    except Exception, e:
        msg = '[ACL "%s" could not be created]: %s' % (acl_conf['acl_name'], e.message)
        logging.info(msg)
        raise Exception(msg)

    logging.info('The ACL "%s" is created successfully' % acl_conf['acl_name'])


def create_multi_l2_acl_policies(zd, acl_conf_list, pause = 1):
    ""
    ""
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    try:
        if wgt.is_enabled_to_click(zd, xlocs['l2acl_create_new']):
            zd.s.click_and_wait(xlocs['l2acl_create_new'])
        else:
            raise Exception('The "Create New" button is disabled')

        for acl_conf in acl_conf_list:
            if wgt.is_enabled_to_click(zd, xlocs['l2acl_create_new']):
                zd.s.click_and_wait(xlocs['l2acl_create_new'])
            else:
                raise Exception('The "Create New" button is disabled')

            _cfg_l2_acl_policy(zd, acl_conf)
            time.sleep(pause)
            logging.info('The ACL "%s" is created successfully' % acl_conf['acl_name'])

        logging.info('%d ACLs are created successfully' % len(acl_conf_list))

    except Exception, e:
        raise Exception('[Could not create %d ACLs] %s' % (len(acl_conf_list), e.message))

def clone_l2_acl_policy(zd, acl_name, new_acl_conf, pause = 1):
    """
    Clone an existing ACL policy to a new one with new name
    Input:
        zd:              the Zone Director object
        acl_name:        the name of the ACL policy
        new_acl_conf:    the new configuration the ACL policy
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    clone_button = xlocs['clone_l2acl'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, clone_button):
            zd.s.click_and_wait(clone_button)
        else:
            raise Exception('The "Clone" button is disabled')

        _cfg_l2_acl_policy(zd, new_acl_conf)
        logging.info('ACL "%s" is cloned to "%s" successfully' % (acl_name, new_acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[ACL "%s" could not be cloned]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def edit_l2_acl_policy(zd, acl_name, new_acl_conf, pause = 1):
    """
    Edit an existing ACL policy.
    Input:
        zd:              the Zone Director object
        acl_name:        the name of the ACL policy
        new_acl_conf:    the new configuration the ACL policy
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036                   
    edit_button = xlocs['edit_l2acl'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button is disabled')

        _cfg_l2_acl_policy(zd, new_acl_conf, True)
        logging.info('ACL "%s" is edited to %s successfully' % (acl_name, new_acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[ACL "%s" could not be edited]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def delete_l2_acl_policy(zd, acl_name, pause = 1):
    """
    Delete an ACL policy
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    l2acl_checkbox = xlocs['l2acl_checkbox'] % acl_name

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036    
    if not zd.s.is_element_present(l2acl_checkbox):
        msg = 'The ACL "%s" did not exist' % acl_name
        logging.info(msg)
        raise Exception(msg)

    zd._delete_element(l2acl_checkbox, xlocs['l2acl_delete_button'], 'L2 ACL')
    if (zd.s.is_alert_present(5)):
        msg_alert = zd.s.get_alert()
        msg = '[ACL "%s" could not be deleted]: %s' % (acl_name, msg_alert)
        logging.info(msg)
        raise Exception(msg)

    logging.info('The ACL "%s" is deleted successfully' % acl_name)


def delete_all_l2_acl_policies(zd, pause = 1):
    """
    Remove all acl policies out of the ACLs table
    Input: zd: Zone Director object
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    total_l2acls = int(zd._get_total_number(xlocs['total_l2acls'], 'L2 ACLs'))
    if total_l2acls == 0:
        logging.info("There is no l2 ACL in the table")
        return

    while total_l2acls:
        a = xlocs['l2acl_all_checkbox']
        zd._delete_element(a, xlocs['l2acl_delete_button'], "All ACLs")
        if (zd.s.is_alert_present(5)):
            msg_alert = zd.s.get_alert()
            raise Exception(msg_alert)

        time.sleep(pause)
        total_l2acls = int(zd._get_total_number(xlocs['total_l2acls'], 'ACLs'))

    logging.info("Delete all ACLs successfully")
    return


###
## L3/L4 ACL
###

def _cfg_l3_acl_policy(zd, acl_conf):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    acl_config = dict(name = None,
                       description = '',
                       default_mode = 'deny-all',
                       rules = [])
    acl_config.update(acl_conf)
    # the element visible function is added by West.li
    if (acl_config['name'] is not None) and zd.s.is_visible(xlocs['l3acl_name_textbox']):
        zd.s.type_text(xlocs['l3acl_name_textbox'], acl_config['name'])

    if acl_config['description'] and zd.s.is_visible(xlocs['l3acl_desc_textbox']):
        zd.s.type_text(xlocs['l3acl_desc_textbox'], acl_config['description'])

    if acl_config['default_mode'] == 'allow-all' and zd.s.is_visible(xlocs['l3acl_allowall_radio']):
        zd.s.click(xlocs['l3acl_allowall_radio'])
    elif zd.s.is_visible(xlocs['l3acl_denyall_radio']):
        zd.s.click(xlocs['l3acl_denyall_radio'])

    if acl_config['rules']:
        # Assign the rule list to the ACL policy
        for rule_conf in acl_config['rules']:
            time.sleep(1)
            create_l3_acl_rule(zd, rule_conf)

    zd.s.click_and_wait(xlocs['l3acl_ok_button'])
    zd.s.get_alert(xlocs['l3acl_cancel_button'])

def _create_l3_acl_policy(zd, acl_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    try:
        if wgt.is_enabled_to_click(zd, xlocs['l3acl_create_new']):
            zd.s.click_and_wait(xlocs['l3acl_create_new'])
        else:
            raise Exception('The "Create New" button is disabled')

        _cfg_l3_acl_policy(zd, acl_conf)
        time.sleep(pause)
    except Exception, e:
        msg = '[ACL "%s" could not be created]: %s' % (acl_conf['name'], e.message)
        logging.info(msg)
        raise Exception(msg)

def _cfg_l3_acl_rule(zd, rule_config):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    rule_conf = dict(order = '',
                      description = '',
                      action = '',
                      dst_addr = '',
                      application = '',
                      protocol = '',
                      dst_port = ''
                      )
    rule_conf.update(rule_config)
    # the element visible function is added by West.li
    if rule_conf['order'] and zd.s.is_visible(xlocs['l3acl_rule_order_listbox']):
        zd.s.select_option(xlocs['l3acl_rule_order_listbox'], rule_conf['order'])
    if rule_conf['description'] and zd.s.is_visible(xlocs['l3acl_rule_description_textbox']):
        zd.s.type_text(xlocs['l3acl_rule_description_textbox'], rule_conf['description'])
    if rule_conf['action'] and zd.s.is_visible(xlocs['l3acl_rule_type_listbox']):
        zd.s.select_option(xlocs['l3acl_rule_type_listbox'], rule_conf['action'])
    if rule_conf['dst_addr'] and zd.s.is_visible(xlocs['l3acl_rule_dest_addr_textbox']):
        zd.s.type_text(xlocs['l3acl_rule_dest_addr_textbox'], rule_conf['dst_addr'])
    if rule_conf['application'] and zd.s.is_visible(xlocs['l3acl_rule_application_listbox']):
        zd.s.select_option(xlocs['l3acl_rule_application_listbox'], rule_conf['application'])
    if rule_conf['protocol'] and zd.s.is_visible(xlocs['l3acl_rule_protocol_textbox']):
        if not zd.s.is_editable(xlocs['l3acl_rule_protocol_textbox']):
            raise Exception('The "Protocol" field could not be edited')
        zd.s.type_text(xlocs['l3acl_rule_protocol_textbox'], rule_conf['protocol'])
    if rule_conf['dst_port'] and zd.s.is_visible(xlocs['l3acl_rule_dest_port_textbox']):
        if not zd.s.is_editable(xlocs['l3acl_rule_dest_port_textbox']):
            raise Exception('The "Destination Port" field could not be edited')
        zd.s.type_text(xlocs['l3acl_rule_dest_port_textbox'], rule_conf['dst_port'])

    zd.s.click_and_wait(xlocs['l3acl_rule_save_button'])
    zd.s.get_alert(xlocs['l3acl_rule_cancel_button'])

def _get_l3_acl_policy_cfg(zd):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    acl_conf = {'name': '',
                'description': '',
                'default_mode': '',
                'rules': []}

    acl_conf['name'] = zd.s.get_value(xlocs['l3acl_name_textbox'])
    acl_conf['description'] = zd.s.get_value(xlocs['l3acl_desc_textbox'])
    if zd.s.is_checked(xlocs['l3acl_allowall_radio']):
        acl_conf['default_mode'] = 'allow-all'
    else:
        acl_conf['default_mode'] = 'deny-all'
    acl_conf['rules'] = _get_l3_acl_rule_cfg(zd)

    return acl_conf

def _get_l3_acl_rule_cfg(zd):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    rules_list = []
    rule_id = 1
    while zd.s.is_element_present(xlocs['l3acl_rule_order'] % rule_id):
        rule_conf = {}
        rule_conf['order'] = zd.s.get_text(xlocs['l3acl_rule_order'] % rule_id)
        rule_conf['description'] = zd.s.get_text(xlocs['l3acl_rule_description'] % rule_id)
        rule_conf['action'] = zd.s.get_text(xlocs['l3acl_rule_type'] % rule_id)
        rule_conf['dst_addr'] = zd.s.get_text(xlocs['l3acl_rule_dest_addr'] % rule_id)
        rule_conf['application'] = zd.s.get_text(xlocs['l3acl_rule_application'] % rule_id)
        rule_conf['protocol'] = zd.s.get_text(xlocs['l3acl_rule_protocol'] % rule_id)
        rule_conf['dst_port'] = zd.s.get_text(xlocs['l3acl_rule_dest_port'] % rule_id)
        rules_list.append(rule_conf)
        rule_id += 1

    return rules_list

def create_l3_acl_rule(zd, rule_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    try:
        if wgt.is_enabled_to_click(zd, xlocs['l3acl_createnew_rule']):
            zd.s.click_and_wait(xlocs['l3acl_createnew_rule'])
        else:
            raise Exception('The "Create New" button is disabled')

        _cfg_l3_acl_rule(zd, rule_conf)
        time.sleep(pause)
    except Exception, e:
        msg = '[The rule "%s" could not be created]: %s' % (rule_conf, e.message)
        logging.info(msg)
        raise Exception(msg)

    logging.info('The rule "%s" is created successfully' % rule_conf)

def edit_l3_acl_rule(zd, acl_name, rule_order, new_rule_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])

    edit_button = xlocs['edit_l3acl'] % acl_name
    edit_rule_button = xlocs['l3acl_rule_edit_button'] % rule_order
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button of ACL "%s" is disabled' % acl_name)

        if wgt.is_enabled_to_click(zd, edit_rule_button):
            zd.s.click_and_wait(edit_rule_button)
        else:
            raise Exception('The "Edit" button of the rule "%s" is disabled' % rule_order)

        _cfg_l3_acl_rule(zd, new_rule_conf)
        logging.info('The rule with order "%s" of the ACL "%s" is edited to %s successfully'
                      % (rule_order, acl_name, new_rule_conf))
        time.sleep(pause)
        zd.s.click_and_wait(xlocs['l3acl_ok_button'])
        zd.s.get_alert(xlocs['l3acl_cancel_button'])
    except Exception, e:
        msg = '[The rule with order "%s" of the ACL "%s" could not be edited]: %s'
        msg = msg % (rule_order, acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def clone_l3_acl_rule(zd, acl_name, rule_order, new_rule_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    edit_button = xlocs['edit_l3acl'] % acl_name
    clone_rule_button = xlocs['l3acl_rule_clone_button'] % rule_order
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button of ACL "%s" is disabled' % acl_name)

        if wgt.is_enabled_to_click(zd, clone_rule_button):
            zd.s.click_and_wait(clone_rule_button)
        else:
            raise Exception('The "Clone" button of the rule "%s" is disabled' % rule_order)

        _cfg_l3_acl_rule(zd, new_rule_conf)
        logging.info('The rule with order "%s" of the ACL "%s" is cloned to %s successfully'
                      % (rule_order, acl_name, new_rule_conf))
        time.sleep(pause)
        zd.s.click_and_wait(xlocs['l3acl_ok_button'])
        zd.s.get_alert(xlocs['l3acl_cancel_button'])
    except Exception, e:
        msg = '[The rule with order "%s" of the ACL "%s" could not be cloned]: %s'
        msg = msg % (rule_order, acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def create_l3_acl_policy(zd, acl_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    #li.pingping 2014.4.18 to fix bug ZF-8115
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])

    _create_l3_acl_policy(zd, acl_conf, pause)

    logging.info('The ACL "%s" is created successfully' % acl_conf['name'])

def create_multi_l3_acl_policies(zd, acl_conf_list, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    #li.pingping 2014.4.18 to fix bug ZF-8115
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])
    

    for acl_conf in acl_conf_list:
        _create_l3_acl_policy(zd, acl_conf, pause)
                
        logging.info('The ACL "%s" is created successfully' % acl_conf['name'])

    logging.info('%s L3/L4 ACL policies are created successfully' % len(acl_conf_list))

def edit_l3_acl_policy(zd, acl_name, new_acl_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    #li.pingping 2014.4.18 to fix bug ZF-8115
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])

    edit_button = xlocs['edit_l3acl'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button is disabled')

        _cfg_l3_acl_policy(zd, new_acl_conf)
        logging.info('ACL "%s" is edited to %s successfully' % (acl_name, new_acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[ACL "%s" could not be edited]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def clone_l3_acl_policy(zd, acl_name, new_acl_conf, pause = 1):
    """
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    edit_button = xlocs['clone_l3acl'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Clone" button is disabled')

        _cfg_l3_acl_policy(zd, new_acl_conf)
        logging.info('ACL "%s" is cloned to %s successfully' % (acl_name, new_acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[ACL "%s" could not be cloned]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def delete_l3_acl_policy(zd, acl_name, pause = 1):
    """
    Delete an ACL policy
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    l3acl_checkbox = xlocs['l3acl_checkbox'] % acl_name

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    #li.pingping 2014.4.18 to fix bug ZF-8115
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])

    if not zd.s.is_element_present(l3acl_checkbox):
        msg = 'The ACL "%s" did not exist' % acl_name
        logging.info(msg)
        raise Exception(msg)

    zd._delete_element(l3acl_checkbox, xlocs['l3acl_delete_button'], 'L3/L4 ACL')
    if (zd.s.is_alert_present(5)):
        msg_alert = zd.s.get_alert()
        msg = '[ACL "%s" could not be deleted]: %s' % (acl_name, msg_alert)
        logging.info(msg)
        raise Exception(msg)

    logging.info('The ACL "%s" is deleted successfully' % acl_name)


def delete_all_l3_acl_policies(zd, pause = 1):
    """
    Remove all acl policies out of the ACLs table
    Input: zd: Zone Director object
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    #li.pingping 2014.4.18 to fix bug ZF-8115
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])    
    
    if zd.s.is_visible(xlocs['total_l3acls']):
        total_l3acls = int(zd._get_total_number(xlocs['total_l3acls'], 'L3/L4 ACLs'))
        if total_l3acls == 0:
            logging.info("There is no L3/L4 ACL in the table")
            return
    
        while total_l3acls:
            a = xlocs['l3acl_all_checkbox']
            zd._delete_element(a, xlocs['l3acl_delete_button'], "All ACLs")
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception(msg_alert)
    
            time.sleep(pause)
            total_l3acls = int(zd._get_total_number(xlocs['total_l3acls'], 'ACLs'))
            
        logging.info("Delete all ACLs successfully")


def get_l3_acl_policy_cfg(zd, acl_name, pause = 1):
    """
    """
    acl_conf = {}

    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    edit_button = xlocs['edit_l3acl'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            errmsg = 'The "Edit" button is disabled'
            errmsg = errmsg % acl_name
            raise Exception(errmsg)

        acl_conf = _get_l3_acl_policy_cfg(zd)
        logging.info('ACL "%s" configuration: %s' % (acl_name, acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[Could not get the ACL "%s" configuration]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)

    return acl_conf


def get_all_l3_acl_policies(zd, pause = 1):
    """
    """
    acl_name = []

    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    #li.pingping 2014.4.18 to fix bug ZF-8115
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])
    

    while zd.s.is_visible(xlocs['l3acl_show_more_button']):
        zd.s.click_and_wait(xlocs['l3acl_show_more_button'], pause)

    count = 0
    acl_name_cell = xlocs['l3acl_name_cell'] % count
    while zd.s.is_element_present(acl_name_cell):
        time.sleep(pause)
        acl_name.append(zd.s.get_text(acl_name_cell))
        count += 1
        acl_name_cell = xlocs['l3acl_name_cell'] % count
        time.sleep(pause)

    return acl_name

###
## L3/L4 IPV6 ACL Methods
##
def _cfg_l3_ipv6_acl_policy(zd, acl_conf):
    """
    Config L3 IPV6 acl policy.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    acl_config = dict(name = None,
                       description = '',
                       default_mode = 'deny-all',
                       rules = [])
    acl_config.update(acl_conf)

    if acl_config['name'] is not None:
        zd.s.type_text(xlocs['l3acl_ipv6_name_textbox'], acl_config['name'])

    if acl_config['description']:
        zd.s.type_text(xlocs['l3acl_ipv6_desc_textbox'], acl_config['description'])

    if acl_config['default_mode'] == 'allow-all':
        zd.s.click(xlocs['l3acl_ipv6_allowall_radio'])
    else:
        zd.s.click(xlocs['l3acl_ipv6_denyall_radio'])

    if acl_config['rules']:
        # Assign the rule list to the ACL policy
        for rule_conf in acl_config['rules']:
            time.sleep(1)
            create_l3_ipv6_acl_rule(zd, rule_conf)

    zd.s.click_and_wait(xlocs['l3acl_ipv6_ok_button'])
    zd.s.get_alert(xlocs['l3acl_ipv6_cancel_button'])

def _create_l3_ipv6_acl_policy(zd, acl_conf, pause = 1):
    """
    Create a new L3 IPV6 ACL policy.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036 

    try:
        if wgt.is_enabled_to_click(zd, xlocs['l3acl_ipv6_create_new']):
            zd.s.click_and_wait(xlocs['l3acl_ipv6_create_new'])
        else:
            raise Exception('The "Create New" button is disabled')

        _cfg_l3_ipv6_acl_policy(zd, acl_conf)
        time.sleep(pause)
    except Exception, e:
        msg = '[IPV6 ACL "%s" could not be created]: %s' % (acl_conf['name'], e.message)
        logging.info(msg)
        raise Exception(msg)

def _cfg_l3_ipv6_acl_rule(zd, rule_config):
    """
    Configure L3 IPV6 ACL rule settings.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    rule_conf = dict(order = '',
                     description = '',
                     action = '',
                     dst_addr = '',
                     application = '',
                     protocol = '',
                     dst_port = '',
                     icmp_type = '',
                     )
    rule_conf.update(rule_config)

    if rule_conf['order']:
        zd.s.select_option(xlocs['l3acl_ipv6_rule_order_listbox'], rule_conf['order'])
    if rule_conf['description']:
        zd.s.type_text(xlocs['l3acl_ipv6_rule_description_textbox'], rule_conf['description'])
    if rule_conf['action']:
        zd.s.select_option(xlocs['l3acl_ipv6_rule_type_listbox'], rule_conf['action'])
    if rule_conf['dst_addr']:
        zd.s.type_text(xlocs['l3acl_ipv6_rule_dest_addr_textbox'], rule_conf['dst_addr'])
        
    #Set advanced options.
    if rule_conf['application'] or rule_conf['protocol'] or rule_conf['dst_port']:
        if not zd.s.is_visible(xlocs['l3acl_ipv6_rule_application_listbox']):
            zd.s.click_and_wait(xlocs['l3acl_ipv6_rule_advanced_option'])
        
    if rule_conf['application']:
        zd.s.select_option(xlocs['l3acl_ipv6_rule_application_listbox'], rule_conf['application'])
        
    if rule_conf['application'].lower() == 'any' or rule_conf['application'] == '':
        #Default of application is 'Any'.
        #If application is not any, protocl, dst port and icmp type are not editable.
        if rule_conf['protocol']:
            if not zd.s.is_editable(xlocs['l3acl_ipv6_rule_protocol_textbox']):
                raise Exception('The "Protocol" field could not be edited')
            zd.s.type_text(xlocs['l3acl_ipv6_rule_protocol_textbox'], rule_conf['protocol'])
            
            if rule_conf['protocol'] == '58':
                #Need to call key_up to trigger onkeyup event,  
                #which will enable edit icmp type if protocol is 58.
                zd.s.key_up(xlocs['l3acl_ipv6_rule_protocol_textbox'], '8')
        if rule_conf['dst_port'] and rule_conf['protocol'].lower() == 'any' or rule_conf['protocol'] == '':
            if not zd.s.is_editable(xlocs['l3acl_ipv6_rule_dest_port_textbox']):
                raise Exception('The "Destination Port" field could not be edited')
            zd.s.type_text(xlocs['l3acl_ipv6_rule_dest_port_textbox'], rule_conf['dst_port'])
        if rule_conf['icmp_type'] and rule_conf['protocol'] == '58':
            if not zd.s.is_editable(xlocs['l3acl_ipv6_rule_icmp_type_textbox']):
                raise Exception('The "ICMP Type" field could not be edited')
            zd.s.type_text(xlocs['l3acl_ipv6_rule_icmp_type_textbox'], rule_conf['icmp_type'])    

    zd.s.click_and_wait(xlocs['l3acl_ipv6_rule_save_button'])
    zd.s.get_alert(xlocs['l3acl_ipv6_rule_cancel_button'])

def _get_l3_ipv6_acl_policy_cfg(zd):
    """
    Get L3 IPV6 ACL policy configuration.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    acl_conf = {'name': '',
                'description': '',
                'default_mode': '',
                'rules': []}

    acl_conf['name'] = zd.s.get_value(xlocs['l3acl_ipv6_name_textbox'])
    acl_conf['description'] = zd.s.get_value(xlocs['l3acl_ipv6_desc_textbox'])
    if zd.s.is_checked(xlocs['l3acl_ipv6_allowall_radio']):
        acl_conf['default_mode'] = 'allow-all'
    else:
        acl_conf['default_mode'] = 'deny-all'
    acl_conf['rules'] = _get_l3_ipv6_acl_rule_cfg(zd)

    return acl_conf

def _get_l3_ipv6_acl_rule_cfg(zd):
    """
    Get L3 IPV6 ACL rule configuration.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    rules_list = []
    rule_id = 1
    while zd.s.is_element_present(xlocs['l3acl_ipv6_rule_order'] % rule_id):
        rule_conf = {}
        rule_conf['order'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_order'] % rule_id)
        rule_conf['description'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_description'] % rule_id)
        rule_conf['action'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_type'] % rule_id)
        rule_conf['dst_addr'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_dest_addr'] % rule_id)
        rule_conf['application'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_application'] % rule_id)
        rule_conf['protocol'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_protocol'] % rule_id)
        rule_conf['dst_port'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_dest_port'] % rule_id)
        rule_conf['icmp_type'] = zd.s.get_text(xlocs['l3acl_ipv6_rule_icmp_type'] % rule_id)
        
        rules_list.append(rule_conf)
        rule_id += 1

    return rules_list

def create_l3_ipv6_acl_rule(zd, rule_conf, pause = 1):
    """
    Create a new L3 IPV6 ACL rule.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    try:
        if wgt.is_enabled_to_click(zd, xlocs['l3acl_ipv6_createnew_rule']):
            zd.s.click_and_wait(xlocs['l3acl_ipv6_createnew_rule'])
        else:
            raise Exception('The "Create New" button is disabled in IPV6 ACL')

        _cfg_l3_ipv6_acl_rule(zd, rule_conf)
        time.sleep(pause)
    except Exception, e:
        msg = '[The rule of IPV6 ACL "%s" could not be created]: %s' % (rule_conf, e.message)
        logging.info(msg)
        raise Exception(msg)

    logging.info('The rule of IPV6 ACL "%s" is created successfully' % rule_conf)

def edit_l3_ipv6_acl_rule(zd, acl_name, rule_order, new_rule_conf, pause = 1):
    """
    Edit a L3 IPV6 ACL rule settings.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    edit_button = xlocs['edit_l3acl_ipv6'] % acl_name
    edit_rule_button = xlocs['l3acl_ipv6_rule_edit_button'] % rule_order
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button of IPV6 ACL "%s" is disabled' % acl_name)

        if wgt.is_enabled_to_click(zd, edit_rule_button):
            zd.s.click_and_wait(edit_rule_button)
        else:
            raise Exception('The "Edit" button of the rule for IPV6 ACL "%s" is disabled' % rule_order)

        _cfg_l3_ipv6_acl_rule(zd, new_rule_conf)
        logging.info('The rule with order "%s" of the IPV6 ACL "%s" is edited to %s successfully'
                      % (rule_order, acl_name, new_rule_conf))
        time.sleep(pause)
        zd.s.click_and_wait(xlocs['l3acl_ipv6_ok_button'])
        zd.s.get_alert(xlocs['l3acl_ipv6_cancel_button'])
    except Exception, e:
        msg = '[The rule with order "%s" of the IPV6 ACL "%s" could not be edited]: %s'
        msg = msg % (rule_order, acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def clone_l3_ipv6_acl_rule(zd, acl_name, rule_order, new_rule_conf, pause = 1):
    """
    Clone a L3 IPV6 ACL rule.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    edit_button = xlocs['edit_l3acl_ipv6'] % acl_name
    clone_rule_button = xlocs['l3acl_ipv6_rule_clone_button'] % rule_order
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button of IPV6 ACL "%s" is disabled' % acl_name)

        if wgt.is_enabled_to_click(zd, clone_rule_button):
            zd.s.click_and_wait(clone_rule_button)
        else:
            raise Exception('The "Clone" button of the rule for IPV6 ACL "%s" is disabled' % rule_order)

        _cfg_l3_ipv6_acl_rule(zd, new_rule_conf)
        logging.info('The rule with order "%s" of the IPV6 ACL "%s" is cloned to %s successfully'
                      % (rule_order, acl_name, new_rule_conf))
        time.sleep(pause)
        zd.s.click_and_wait(xlocs['l3acl_ipv6_ok_button'])
        zd.s.get_alert(xlocs['l3acl_ipv6_cancel_button'])
    except Exception, e:
        msg = '[The rule with order "%s" of the IPV6 ACL "%s" could not be cloned]: %s'
        msg = msg % (rule_order, acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def create_l3_ipv6_acl_policy(zd, acl_conf, pause = 1):
    """
    Create a new L3 IPV6 ACL policy.
    """
    #xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    _create_l3_ipv6_acl_policy(zd, acl_conf, pause)

    logging.info('The ACL "%s" is created successfully' % acl_conf['name'])

def create_multi_l3_ipv6_acl_policies(zd, acl_conf_list, pause = 1):
    """
    Create multi L3 IPV6 ACL policies.
    """
    #xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    for acl_conf in acl_conf_list:
        _create_l3_ipv6_acl_policy(zd, acl_conf, pause)
                
        logging.info('The IPV6 ACL "%s" is created successfully' % acl_conf['name'])

    logging.info('%s L3/L4 IPV6 ACL policies are created successfully' % len(acl_conf_list))

def edit_l3_ipv6_acl_policy(zd, acl_name, new_acl_conf, pause = 1):
    """
    Edit L3 IPV6 ACL policy settings.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036 

    edit_button = xlocs['edit_l3acl_ipv6'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Edit" button is disabled for IPV6 ACL')

        _cfg_l3_ipv6_acl_policy(zd, new_acl_conf)
        logging.info('IPV6 ACL "%s" is edited to %s successfully' % (acl_name, new_acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[IPV6 ACL "%s" could not be edited]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)


def clone_l3_ipv6_acl_policy(zd, acl_name, new_acl_conf, pause = 1):
    """
    Clone L3 IPV6 ACL policy.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    
    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036 

    edit_button = xlocs['clone_l3acl_ipv6'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            raise Exception('The "Clone" button is disabled')

        _cfg_l3_ipv6_acl_policy(zd, new_acl_conf)
        logging.info('IPV6 ACL "%s" is cloned to %s successfully' % (acl_name, new_acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[IPV6 ACL "%s" could not be cloned]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)

def delete_l3_ipv6_acl_policy(zd, acl_name, pause = 1):
    """
    Delete a L3 IPV6 ACL policy.
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    l3acl_checkbox = xlocs['l3acl_ipv6_checkbox'] % acl_name

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    ##zj 20140410 fixed ZF-8036
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 
    ##zj 20140410 fixed ZF-8036 

    if not zd.s.is_element_present(l3acl_checkbox):
        msg = 'The IPV6 ACL "%s" did not exist' % acl_name
        logging.info(msg)
        raise Exception(msg)

    zd._delete_element(l3acl_checkbox, xlocs['l3acl_ipv6_delete_button'], 'L3/L4 ACL')
    if (zd.s.is_alert_present(5)):
        msg_alert = zd.s.get_alert()
        msg = '[IPV6 ACL "%s" could not be deleted]: %s' % (acl_name, msg_alert)
        logging.info(msg)
        raise Exception(msg)

    logging.info('The IPV6 ACL "%s" is deleted successfully' % acl_name)


def delete_all_l3_ipv6_acl_policies(zd, pause = 1):
    """
    Remove all l3 ipv6 acl policies out of the ACLs table
    Input: zd: Zone Director object
    """
    xlocs = LOCATORS_CFG_ACCESS_CONTROL
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    #@zj 20140721 optimization zf-9291
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']):
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse'])    
           
    if zd.s.is_element_present(xlocs['total_l3acls_ipv6']) and zd.s.is_visible(xlocs['total_l3acls_ipv6']):
        total_l3acls = int(zd._get_total_number(xlocs['total_l3acls_ipv6'], 'L3/L4 IPV6 ACLs'))
        if total_l3acls == 0:
            logging.info("There is no L3/L4 IPV6 ACL in the table")
            return
    
        while total_l3acls:
            a = xlocs['l3acl_ipv6_all_checkbox']
            zd._delete_element(a, xlocs['l3acl_ipv6_delete_button'], "All IPV6 ACLs")
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception(msg_alert)
    
            time.sleep(pause)
            total_l3acls = int(zd._get_total_number(xlocs['total_l3acls_ipv6'], 'L3/L4 IPV6 ACLs'))
            
        logging.info("Delete all IPV6 ACLs successfully")


def get_l3_ipv6_acl_policy_cfg(zd, acl_name, pause = 1):
    """
    Get l3 ipv6 acl policy configuration based on acl name.
    """
    acl_conf = {}

    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)

    edit_button = xlocs['edit_l3acl_ipv6'] % acl_name
    try:
        if wgt.is_enabled_to_click(zd, edit_button):
            zd.s.click_and_wait(edit_button)
        else:
            errmsg = 'The "Edit" button is disabled'
            errmsg = errmsg % acl_name
            raise Exception(errmsg)

        acl_conf = _get_l3_ipv6_acl_policy_cfg(zd)
        logging.info('IPV6 ACL "%s" configuration: %s' % (acl_name, acl_conf))
        time.sleep(pause)
    except Exception, e:
        msg = '[Could not get the IPV6 ACL "%s" configuration]: %s' % (acl_name, e.message)
        logging.info(msg)
        raise Exception(msg)

    return acl_conf

def get_all_l3_ipv6_acl_policies(zd, pause = 1):
    """
    Get all l3 ipv6 acl policy names.
    """
    acl_name_list = []

    xlocs = LOCATORS_CFG_ACCESS_CONTROL

    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)
    time.sleep(pause)
    if zd.s.is_element_present(zd.info['loc_cfg_acl_icon_expand']):
        pass
    elif zd.s.is_element_present(zd.info['loc_cfg_acl_icon_collapse']): 
        zd.s.click_and_wait(zd.info['loc_cfg_acl_icon_collapse']) 

    while zd.s.is_visible(xlocs['l3acl_ipv6_show_more_button']):
        zd.s.click_and_wait(xlocs['l3acl_ipv6_show_more_button'], pause)

    count = 0
    acl_name_cell = xlocs['l3acl_ipv6_name_cell'] % count
    while zd.s.is_element_present(acl_name_cell) and zd.s.is_visible(acl_name_cell):
        time.sleep(pause)
        acl_name_list.append(zd.s.get_text(acl_name_cell))
        count += 1
        acl_name_cell = xlocs['l3acl_ipv6_name_cell'] % count
        time.sleep(pause)

    return acl_name_list

def get_all_l3_ipv6_acl_cfgs(zd, pause = 1):
    """
    Get all l3 ipv6 acl details, key is acl name, value is acl details.
    """
    acls_ipv6 = []
    acls_name_list = get_all_l3_ipv6_acl_policies(zd)
    
    for acl_name in acls_name_list:
        acls_ipv6.append(get_l3_ipv6_acl_policy_cfg(zd, acl_name))
        
    return acls_ipv6

def _verify_l3acl_ipv6_guiset_guiget(gui_set_l3acl, gui_get_l3acl):
    '''
    Verify l3 acl ipv6 between gui set and gui get.
    '''
    import copy
    new_gui_get_l3acl = copy.deepcopy(gui_get_l3acl)
    
    res_acl = {}
    #Remove default rules from get dict.
    for get_cfg in new_gui_get_l3acl:
        if get_cfg.get('rules'):
            old_rule_list = get_cfg['rules']
            new_rule_list = []
            for rule in old_rule_list:
                if rule['order'] not in ['1','2','3','4']:
                    new_rule_list.append(rule)
            
            get_cfg['rules'] = new_rule_list
    
    #Compare length of set and get.
    if len(gui_set_l3acl) != len(new_gui_get_l3acl):
        res_acl['Count'] = "GUI Set:%s, GUI Get: %s" % (len(gui_set_l3acl), len(new_gui_get_l3acl))         
    else:
        for index in range(0, len(gui_set_l3acl)):
            set_cfg = gui_set_l3acl[index]
            get_cfg = new_gui_get_l3acl[index]
            #Compare get set configuration -dict.
            for key, set_value in set_cfg.items():
                get_value = get_cfg[key]
                res_item = {}
                if type(set_value) == list:
                    #Verify rule list configuration.
                    res_rules = _compare_l3acl_ipv6_rules(set_value, get_value)
                    if res_rules:
                        res_item[key] = res_rules
                else:
                    if not get_value == set_value:
                        res_item[key] = "Expected: %s, Actual: %s" % (key, set_value, get_value)
            if res_item:
                res_acl[set_cfg['name']] = res_item
        
    return res_acl

def _compare_l3acl_ipv6_rules(set_rules, get_rules):
    '''
    Compare rule.
    dict structure is 
        {'order': '', 'description': '', 'action': '', 
         'dst_addr': '', 'application': '', 'protocol': '', 
         'dst_port': '', 'icmp_type': ''}
    '''
    res_rules = {}
    
    if len(set_rules) != len(get_rules):
        res_rules['Count'] = "GUI Set:%s, GUI Get:%s" % (len(set_rules), len(get_rules))
    else:
        for index in range(0, len(set_rules)):
            set_rule = set_rules[index]
            get_rule = get_rules[index]
                            
            res_rule = _compare_ipv6_rule(set_rule, get_rule)
            
            if res_rule:
                res_rules[index] = res_rule
        
    return res_rules

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