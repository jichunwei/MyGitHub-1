
'''
import CA to ZD
Created on Nov 12, 2014
@author: Yu.yanan@odc-ruckuswireless.com
'''

import logging
import time
import os

from RuckusAutoTest.components.lib.zd import control_zd as control_zd
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt
from RuckusAutoTest.components.lib.zd import aps

locators = dict(
    advanced_options_anchor = r"//tr[@id='advance']//a[@href='#']",
    cover_ca_radio = r"//input[@id='cover_CA']",
    loc_brower_select_ca = r"//input[@id='filename-uploadCA']",
    loc_ca_upload_button = r"//input[@id='perform-uploadCA']",
    loc_admin_ca_upload_error_span = r"//span[@id='error-uploadCA']",

)
def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_CERTIFICATE)


def _import_ca(zd,ca_path):
    _nav_to(zd)
    
    if os.path.exists(ca_path):
        logging.info('The ca file exists')
    else:
        raise Exception("The CA do not exists.please check it.")

    zd.s.click_and_wait(locators['advanced_options_anchor'])
    zd.s.click_and_wait(locators['cover_ca_radio'])
    
    browser_ca_field = locators['loc_brower_select_ca']
    if not zd.s.is_element_present(browser_ca_field):
        raise Exception("The field to select ca file is not present")
    try:
        zd.s.type(browser_ca_field,ca_path)
    except:
        raise Exception("Can not set value %s to the locator %s" % (ca_path, browser_ca_field))
    
    upload_ca_button = locators['loc_ca_upload_button']
    
    if not zd.s.is_element_present(upload_ca_button):
        raise Exception("The button to upload ca file is not present")
    zd.s.click_and_wait(upload_ca_button)
    logging.info('click upload ca button.')
    
    if zd.s.is_confirmation_present(5):
        cfm=zd.s.get_confirmation()
        logging.info("There's a confirmation:\n%s"%cfm)
        logging.info('Clicked OK')
    if zd.s.is_element_visible(locators['loc_admin_ca_upload_error_span']):
        msg = zd.s.get_text(locators['loc_admin_ca_upload_error_span'])
        if not msg.find('successful'):
            raise Exception(msg)
    
    
    

    