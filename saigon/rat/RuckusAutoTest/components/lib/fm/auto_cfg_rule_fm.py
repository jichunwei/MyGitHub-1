'''
This module is to provide utility functionality for Inventory > Device Registration
>  Auto Configuration Setup page.

Note: Currently this lib is just a wrapper. It is using function from FlexMaster.py.
Will develop to use functions of AutoConfig later.
'''
#from RuckusAutoTest.components.lib.AutoConfig import Ctrl, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.common.utils import try_interval
from RuckusAutoTest.components.lib import AutoConfig as ac
import logging

Locators = dict(

)

def nav_to(fm, force = False):
    fm.navigate_to(fm.INVENTORY, fm.INVENTORY_DEVICE_REG, force = force)
    #fm.selenium.click_and_wait(Locators['reg_status_tab'], 1.5)

def create_auto_cfg_rule(fm, cfg_rule_name, device_group, model, cfg_template_name, advance_return = False):
    '''
    - This funciton is to create an auto configuration setup for an AP. Currently,
    we only test for Device Name first and may be we test for WLAN Common, WLAN 1->8

    kwa:
    - cfg_rule_name: name of auto config rule
    - device_group: group of devices to aplly this rule
    - model: model to apply this rule
    - cfg_template_name: The template for this rule
    - advance_return: True: will return the created time from "Create Time" column
                      in format "YYMMDD.HHMMSS" if advance_return=True (refer to
                      _parse_auto_cfg_rule_created_time for more info).
                      False: no return
    '''
    p = dict(
        cfg_rule_name = cfg_rule_name,
        device_group = device_group,
        model = model,
        cfg_template_name = cfg_template_name,
        advance_return = advance_return,
    )

    return fm.create_auto_cfg_rule(**p)

def stop_auto_cfg_rule(fm, cfg_rule_name, create_time = None):
    '''
    This function is to stop an auto cfg rule.
    - cfg_rule_name: name of the rule to stop
    - create_time: if None, do normal search
                   Not None, it is in format "YYMMDD.HHMMSS" do binary search.
    '''
    p = dict(cfg_rule_name = cfg_rule_name)
    if create_time is not None:
        p.update(dict(
            advance_search = True,
            create_time = create_time,
        ))

    return fm.stop_auto_cfg_rule(**p)


def is_device_marked_auto_config(fm, serial):
    '''
    This fucntion is to check whether an AP auto configured or not.
    The way to check is that base on image of column 5 (td[5]).
        - Auto Configured:     => Show image: <img src="/intune/images/accept.png"/>
        - Not auto configured: => Show image: <img src="/intune/images/close.gif"/>
    - serial: 'serial number of device to search'
    Return:
    - return True/False/raise exception if not found the device
    '''
    return fm.is_device_auto_configured(serial = serial)

def is_device_auto_configured_by_rule(fm, serial, cfg_rule_name, create_time = None):
    '''
    This function is to check whether a serial device is auto configured by a rule
    - serial: device serial
    - cfg_rule_name: name of the rule to stop
    - create_time: if None, do normal search
                   Not None, it is in format "YYMMDD.HHMMSS" do binary search.
    Return:
    - return True/False/raise exception if not found the rule
    '''
    p = dict(
        serial = serial,
        cfg_rule_name = cfg_rule_name,
    )
    if create_time is not None:
        p.update(dict(
            advance_search = True,
            create_time = create_time
        ))

    return fm.is_device_auto_configured_by_rule(**p)


def delete_auto_cfg_rule(fm, cfg_rule_name, create_time=None):
    '''
    This function is to stop an auto cfg rule.
    - cfg_rule_name: name of the rule to stop
    - create_time: if None, do normal search
                   Not None, it is in format "YYMMDD.HHMMSS" do binary search.

    . Will revise this function to use AutoConfig later
    '''
    p, s = dict(cfg_rule_name = cfg_rule_name), fm.selenium
    if create_time is not None:
        p.update(dict(
            advance_search = True,
            create_time = create_time,
        ))

    del_link_loc = "//span[.='Delete']"
    row_content, row_loc = fm.bin_search_auto_cfg_rule(**p) \
                           if create_time else\
                           fm.search_auto_cfg_rule(**p)

    if row_loc:
        s.safe_click(row_loc + del_link_loc)
        if s.is_confirmation_present():
            logging.info('Got a pop up window "%s"' % s.get_confirmation())
        return True

    return False
