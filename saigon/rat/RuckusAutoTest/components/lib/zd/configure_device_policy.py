"""
@since: May 2013
@author: An Nguyen

This module support to working on Device Policy and Precedence Policy on ZD Configure -> Access Control page
"""

import logging
import re
import time

from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.common import lib_Constant as CONST
from RuckusAutoTest.common import utils

LOCATORS_CFG_ACCESS_CONTROL = dict(
    dvcpcy_table = '//table[@id="devicepolicy"]',
    dvcpcy_table_tfoot = '//table[@id="devicepolicy"]/tfoot',
    dvcpcy_edit_span = '//table[@id="devicepolicy"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',
    dvcpcy_create_span = '//table[@id="devicepolicy"]//span[@id="new-devicepolicy"]',
    dvcpcy_name_textbox = '//form[@id="form-devicepolicy"]//input[@id="devicepolicy-name"]',
    dvcpcy_desc_textbox = '//form[@id="form-devicepolicy"]//input[@id="devicepolicy-description"]',
    dvcpcy_mode_deny_button = '//form[@id="form-devicepolicy"]//input[@id="devicepolicy-denyAll"]',
    dvcpcy_mode_allow_button = '//form[@id="form-devicepolicy"]//input[@id="devicepolicy-allowAll"]',
    dvcpcy_delete_button = '//table[@id="devicepolicy"]//input[@id="del-devrule"]',
    dvcpcy_ok_button = '//table[@id="devicepolicy"]//input[@id="ok-devicepolicy"]',
    dvcpcy_cancel_button = '//table[@id="devicepolicy"]//input[@id="cancel-devicepolicy"]',
    
    
    dvcpcy_rule_table = '//table[@id="devrule"]',
    dvcpcy_rule_table_tfoot = '//table[@id="devrule"]/tfoot',
    dvcpcy_rule_adv_option_span = '//table[@id="devrule"]//img[@src="images/collapse.png"]',
    dvcpcy_rule_create_span = '//table[@id="devrule"]//span[@id="new-devrule"]',
    dvcpcy_rule_edit_span = '//table[@id="devrule"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',
    dvcpcy_rule_order_select = '//table[@id="devrule"]//select[@id="devrule-id"]',
    dvcpcy_rule_desc_textbox = '//table[@id="devrule"]//input[@id="devrule-description"]',
    dvcpcy_rule_os_select = '//table[@id="devrule"]//select[@id="devrule-devinfo"]',
    dvcpcy_rule_type_select = '//table[@id="devrule"]//select[@id="devrule-action"]',
    dvcpcy_rule_uplink_select = '//table[@id="devrule"]//select[@id="devrule-uplink"]',
    dvcpcy_rule_downlink_select = '//table[@id="devrule"]//select[@id="devrule-downlink"]',
    dvcpcy_rule_vlan_textbox = '//table[@id="devrule"]//input[@id="devrule-vlan"]',
    dvcpcy_rule_delete_button = '//table[@id="devrule"]//input[@id="del-devrule"]',
    dvcpcy_rule_save_button = '//table[@id="devrule"]//input[@id="ok-devrule"]',
    dvcpcy_rule_cancel_button = '//table[@id="devrule"]//input[@id="cancel-devrule"]',
    
    #
    prece_table = '//table[@id="precedence"]',
    prece_table_tfoot = '//table[@id="precedence"]/tfoot',
    prece_create_span = '//table[@id="precedence"]//span[@id="new-precedence"]',
    prece_edit_span = '//table[@id="precedence"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',
    prece_name_textbox = '//form[@id="form-precedence"]//input[@id="precedence-name"]',
    prece_desc_textbox = '//form[@id="form-precedence"]//input[@id="precedence-description"]',
    prece_delete_button = '//table[@id="precedence"]//input[@id="del-prerule"]',
    prece_ok_button = '//table[@id="precedence"]//input[@id="ok-precedence"]',
    prece_cancel_button = '//table[@id="precedence"]//input[@id="cancel-precedence"]',
    
        
    prece_rule_table = '//table[@id="prerule"]',
    prece_rule_table_tfoot = '//table[@id="prerule"]/tfoot',
    prece_rule_adv_option_span = '//table[@id="prerule"]//img[@src="images/collapse.png"]',
    prece_rule_create_span = '//table[@id="prerule"]//span[@id="new-prerule"]',
    prece_rule_edit_span = '//table[@id="prerule"]//tr/td[text()="%s"]/../td/span[text()="Edit"]',
    prece_rule_order_select = '//table[@id="prerule"]//select[@id="prerule-id"]',
    prece_rule_desc_textbox = '//table[@id="prerule"]//input[@id="prerule-description"]',
    prece_rule_attr_select = '//table[@id="prerule"]//select[@id="prerule-attr"]',
    prece_rule_policy_select = '//table[@id="prerule"]//select[@id="prerule-order"]',
    prece_rule_policy_up_button = '//table[@id="prerule"]//img[@src="images/sort_asc.gif"]',
    prece_rule_delete_button = '//table[@id="prerule"]//input[@id="del-prerule"]',
    prece_rule_save_button = '//table[@id="prerule"]//input[@id="ok-prerule"]',
    prece_rule_cancel_button = '//table[@id="prerule"]//input[@id="cancel-prerule"]',
    
    
)

#
# PUBLIC FUNCTIONS
#

def show_device_policy(zd):
    """
    """
    return _show_device_policy(zd)

def create_device_policy(zd, dvcpcy_conf):
    try:
        _create_device_policy(zd, dvcpcy_conf)
        return (True, '[CREATE DVCPCY][PASSED]')
    except Exception, e:
        msg = '[CREATE DVCPCY][FAILED] %s' % e.message
        return (False, msg)

def edit_device_policy(zd, policy_name , dvcpcy_conf):
    try:
        _edit_device_policy(zd, policy_name, dvcpcy_conf)
        return (True, '[CREATE DVCPCY][PASSED]')
    except Exception, e:
        msg = '[CREATE DVCPCY][FAILED] %s' % e.message
        return (False, msg)

def show_precedence_policy(zd):
    """
    """
    return _show_precedence_policy(zd)

#
# PRIVATE FUNCTIONS
#

def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)

def _show_device_policy(zd):
    """
    return the detail info of all device policy corresponding to CLI info
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    _nav_to(zd)
    dvcpcy_info = {}
    dev_pol_sum = _get_dvcpcy_summary(zd, 
                                         locators['dvcpcy_table'], 
                                         locators['dvcpcy_table_tfoot'])
    
    for pol in dev_pol_sum:
        dvcpcy_info[pol['name']] = pol.copy()
        dvcpcy_info[pol['name']]['rules'] = _get_dvcpcy_rules(zd, pol['name'])
    
    return dvcpcy_info
        
def _get_dvcpcy_summary(zd, devpolicy_tbl, devpolicy_div):
    return wgt.get_tbl_rows(zd.s, devpolicy_tbl, devpolicy_div)

def _get_dvcpcy_rules(zd, pol_name):
    locators = LOCATORS_CFG_ACCESS_CONTROL
    edit_pol_button = locators['dvcpcy_edit_span'] % pol_name
    show_adv_option = locators['dvcpcy_rule_adv_option_span']
    zd.s.click_and_wait(edit_pol_button)
    if zd.s.is_element_present(show_adv_option):
        zd.s.click_and_wait(show_adv_option)
    rules = wgt.get_tbl_rows(zd.s, locators['dvcpcy_rule_table'], locators['dvcpcy_rule_table_tfoot'])
    dev_pol_rules = {}
    for rule in rules:
        dev_pol_rules[rule['order']] = rule.copy()
        
    return dev_pol_rules

def _create_device_policy(zd, dvcpcy_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    _nav_to(zd)
    if zd.s.is_element_disabled(locators['dvcpcy_create_span']):
        raise Exception('The create device policy span is disabled')
    zd.s.click_and_wait(locators['dvcpcy_create_span'])
    try:
        _cfg_device_policy(zd, dvcpcy_conf)
    except:
        if zd.s.is_element_present(locators['dvcpcy_cancel_button']):
            zd.s.click_and_wait(locators['dvcpcy_cancel_button'])
        raise
    zd.s.click_and_wait(locators['dvcpcy_ok_button'])
    zd.s.get_alert(locators['dvcpcy_cancel_button'])

def _edit_device_policy(zd, policy_name, dvcpcy_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    _nav_to(zd)
    zd.s.click_and_wait(locators['dvcpcy_edit_span'] % policy_name)
    try:
        _cfg_device_policy(zd, dvcpcy_conf)
    except:
        if zd.s.is_element_present(locators['dvcpcy_cancel_button']):
            zd.s.click_and_wait(locators['dvcpcy_cancel_button'])
        raise
    zd.s.click_and_wait(locators['dvcpcy_ok_button'])
    zd.s.get_alert(locators['dvcpcy_cancel_button'])

def _cfg_device_policy(zd, dvcpcy_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    cfg = {'name': None,
           'description': None,
           'mode': None,
           'rules': []}
    cfg.update(dvcpcy_conf)
    
    if cfg['name'] != None:
        zd.s.type_text(locators['dvcpcy_name_textbox'], cfg['name'])    
    if cfg['description'] != None:
        zd.s.type_text(locators['dvcpcy_desc_textbox'], cfg['description'])
    
    if cfg['mode'] != None:
        if cfg['mode'].lower().startswith('allow'):
            loc = locators['dvcpcy_mode_allow_button'] 
        elif cfg['mode'].lower().startswith('deny'):
            loc = locators['dvcpcy_mode_deny_button']
        else:
            msg = 'Do not support to select "%s" for the device rule default mode' % cfg['mode']
            logging.debug(msg)
            raise Exception(msg)
        zd.s.safe_click(loc)
            
    if cfg['rules']:
        for rule_cfg in cfg['rules']:
            _create_device_policy_rule(zd, rule_cfg)
    
def _create_device_policy_rule(zd, dvcpcy_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    zd.s.click_and_wait(locators['dvcpcy_rule_create_span'])
    _cfg_device_policy_rule(zd, dvcpcy_conf)
    zd.s.click_and_wait(locators['dvcpcy_rule_save_button'])
    zd.s.get_alert(locators['dvcpcy_rule_cancel_button'])
    

def _edit_device_policy_rule():
    """
    """
    pass

def _cfg_device_policy_rule(zd, rule_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    cfg = {'description': None,
           'os_type': None,
           'type': None,
           'uplink': None,
           'downlink': None,
           'vlan': None}
    cfg.update(rule_conf)
    
    if cfg['description'] != None:
        zd.s.type_text(locators['dvcpcy_rule_desc_textbox'], cfg['description'])
    if cfg['os_type'] != None:
        zd.s.select_option(locators['dvcpcy_rule_os_select'], cfg['os_type'])
    if cfg['type'] != None:
        zd.s.select_option(locators['dvcpcy_rule_type_select'], cfg['type'])
    if cfg['uplink'] != None:
        zd.s.select_option(locators['dvcpcy_rule_uplink_select'], cfg['uplink'])
    if cfg['downlink'] != None:
        zd.s.select_option(locators['dvcpcy_rule_downlink_select'], cfg['downlink'])
    if cfg['vlan'] != None:
        zd.s.type_text(locators['dvcpcy_rule_vlan_textbox'], cfg['vlan'])

def _show_precedence_policy(zd):
    """
    return the detail info of all device policy corresponding to CLI info
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    _nav_to(zd)
    prece_info = {}
    prece_sum = _get_prece_policy_summary(zd, 
                                         locators['prece_table'], 
                                         locators['prece_table_tfoot'])
    
    for pol in prece_sum:
        prece_info[pol['name']] = pol.copy()
        prece_info[pol['name']]['rules'] = _get_prece_policy_rules(zd, pol['name'])
    
    return prece_info
        
def _get_prece_policy_summary(zd, devpolicy_tbl, devpolicy_div):
    return wgt.get_tbl_rows(zd.s, devpolicy_tbl, devpolicy_div)

def _get_prece_policy_rules(zd, pol_name):
    locators = LOCATORS_CFG_ACCESS_CONTROL
    edit_pol_button = locators['prece_edit_span'] % pol_name
    show_adv_option = locators['prece_rule_adv_option_span']
    zd.s.click_and_wait(edit_pol_button)
    if zd.s.is_element_present(show_adv_option):
        zd.s.click_and_wait(show_adv_option)
    rules = wgt.get_tbl_rows(zd.s, locators['prece_rule_table'], locators['prece_rule_table_tfoot'])
    prece_rules = {}
    for rule in rules:
        prece_rules[rule['order']] = rule.copy()
        
    return prece_rules

def _create_precedence_policy(zd, prece_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    _nav_to(zd)
    if zd.s.is_element_disabled(locators['prece_create_span']):
        raise Exception('The create precedence policy span is disabled')
    zd.s.click_and_wait(locators['prece_create_span'])
    try:
        _cfg_precedence_policy(zd, prece_conf)
    except:
        if zd.s.is_element_present(locators['prece_cancel_button']):
            zd.s.click_and_wait(locators['prece_cancel_button'])
        raise
    zd.s.click_and_wait(locators['prece_ok_button'])
    zd.s.get_alert(locators['prece_cancel_button'])

def _edit_precedence_policy(zd, policy_name, prece_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    _nav_to(zd)
    zd.s.click_and_wait(locators['prece_edit_span'] % policy_name)
    try:
        _cfg_precedence_policy(zd, prece_conf)
    except:
        if zd.s.is_element_present(locators['prece_cancel_button']):
            zd.s.click_and_wait(locators['prece_cancel_button'])
        raise
    zd.s.click_and_wait(locators['prece_ok_button'])
    zd.s.get_alert(locators['prece_cancel_button'])

def _cfg_precedence_policy(zd, prece_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    cfg = {'name': None,
           'description': None,
           'rules': []}
    cfg.update(prece_conf)
    
    if cfg['name'] != None:
        zd.s.type_text(locators['prece_name_textbox'], cfg['name'])    
    if cfg['description'] != None:
        zd.s.type_text(locators['prece_desc_textbox'], cfg['description'])         
    if cfg['rules']:
        for rule_cfg in cfg['rules']:
            _create_precedence_policy_rule(zd, rule_cfg)
    
def _create_precedence_policy_rule(zd, prece_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    zd.s.click_and_wait(locators['prece_rule_create_span'])
    _cfg_precedence_policy_rule(zd, prece_conf)
    zd.s.click_and_wait(locators['prece_rule_save_button'])
    zd.s.get_alert(locators['prece_rule_cancel_button'])

def _edit_precedence_policy_rule():
    """
    """
    pass

def _cfg_precedence_policy_rule(zd, rule_conf):
    """
    """
    locators = LOCATORS_CFG_ACCESS_CONTROL
    cfg = {'order': None,
           'description': None,
           'attribute': None,
           'precedence_policy': None,
           }
    cfg.update(rule_conf)
    
    if cfg['description'] != None:
        zd.s.type_text(locators['prece_rule_desc_textbox'], cfg['description'])
    if cfg['order'] != None:
        zd.s.select_option(locators['prece_rule_order_select'], cfg['order'])
    if cfg['attribute'] != None:
        zd.s.select_option(locators['prece_rule_attr_select'], cfg['attribute'])
    if cfg['precedence_policy'] != None:
        _cfg_order_box(zd, cfg['precedence_policy'], locators['prece_rule_policy_select'], locators['prece_rule_policy_up_button'])

def _cfg_order_box(zd, expected_order, location, up_button):
    """
    """
    current_order = zd.s.get_select_options(location)
    for i in range(len(expected_order)):
        while current_order[i] != expected_order[i]:
            zd.s.select(location, expected_order[i])
            zd.s.click_and_wait(up_button)
            current_order = zd.s.get_select_options(location)
            