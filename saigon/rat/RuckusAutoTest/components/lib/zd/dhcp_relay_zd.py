'''
Usage:

@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: Dec 2012
'''

import time
import logging

#
#  LOCATIONS
#

LOCATORS_CONF_DHCP_RELAY = dict(
    dhcp_relay_span = '//span[@id="configure_dhcpsvrs"]',
    
    loc_create_new_span = '//span[@id="new-dhcpsvr"]',
    loc_edit_span = '//span[@id=""]',
    loc_clone_span = '//span[@id=""]',
    
    loc_search_box = '//table[@id="dhcpsvr"]//tr[@class="t_search"]//input[@type="text"]',
    
    loc_name_textbox = '//input[@id="name"]',
    loc_desc_textbox = '//input[@id="description"]',
    loc_svr1_textbox = '//input[@id="svr1"]',
    loc_svr2_textbox = '//input[@id="svr2"]',
    
    loc_ok_button = '//input[@id="ok-dhcpsvr"]',
    loc_cancel_button = '//input[@id="cancel-dhcpsvr"]',
    
    loc_select_all_checkbox = '//input[@id="dhcpsvr-sall"]',
    loc_delete_button = '//input[@id="del-dhcpsvr"]',
    loc_show_more_button = '//input[@id="showmore-dhcpsvr"]',
    loc_total_dhcp_relay_span = '//div[@id="actions-dhcpsvr"]/span',
    )



#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def create_dhcp_relay_svr(zd, **kwargs):
    _create_new_dhcp_relay(zd, **kwargs)

def delete_all_dhcp_relay_svr(zd, **kwargs):
    _delete_all_dhcp_relay_svr(zd, **kwargs)
             
#-----------------------------------------------------------------------------
#  PRIVATE ACCESS METHODS
#-----------------------------------------------------------------------------

def _config_dhcp_relay(zd, **kwargs):
    """
    This function is used to configure the dhcp relay options:
    parameters: {'name': the name of the DHCP server agents,
                 'description': description for the relay server, (optional)
                 'first_server': the primary server ip address,
                 'second_server': the secondary ip address, (optional)
                 }
    """    
    locs = {'name': LOCATORS_CONF_DHCP_RELAY['loc_name_textbox'],
            'description': LOCATORS_CONF_DHCP_RELAY['loc_desc_textbox'],
            'first_server': LOCATORS_CONF_DHCP_RELAY['loc_svr1_textbox'],
            'second_server': LOCATORS_CONF_DHCP_RELAY['loc_svr2_textbox']}
    
    params = {'name': '',
              'description': '',
              'first_server': '',
              'second_server': ''}
    params.update(kwargs)
    
    for key in params.keys():
        if params[key] != None and key in locs.keys():
            zd.s.type_text(locs[key], params[key])
    
    zd.s.click_and_wait(LOCATORS_CONF_DHCP_RELAY['loc_ok_button'])
    # If an alert of wrong configuration(ex: wrong name, duplicated name...) appears,
    # click the Cancel button
    zd.s.get_alert(LOCATORS_CONF_DHCP_RELAY['loc_cancel_button'])

def _create_new_dhcp_relay(zd, **kwargs):
    """
    """
    params = {'is_nav': True,
              'pause': 2,
              'svr_cfg': {}}
    params.update(kwargs)
    
    if params['is_nav']:
        zd.navigate_to(zd.CONFIGURE, LOCATORS_CONF_DHCP_RELAY['dhcp_relay_span'])
        time.sleep(params['pause'])
    
    try:
        zd.s.click_and_wait(LOCATORS_CONF_DHCP_RELAY['loc_create_new_span'])
        _config_dhcp_relay(zd, **params['svr_cfg'])
        msg = 'Create the new DHCP relay server [%s] successfully' % params['svr_cfg']
    except Exception, e:
        msg = 'Failed to create new DHCP relay server [%s]: %s' % (params['svr_cfg']['name'], e.message)
        logging.debug(msg)
        raise Exception(msg)

def _delete_all_dhcp_relay_svr(zd, **kwargs):
    """
    This function support to delete all the dhcp relay server configuration
    """
    params = {'is_nav': True,
              'pause': 2}
    params.update(kwargs)
    
    if params['is_nav']:
        zd.navigate_to(zd.CONFIGURE, LOCATORS_CONF_DHCP_RELAY['dhcp_relay_span'])
        time.sleep(params['pause'])
    
    total_dhcps = int(zd._get_total_number(LOCATORS_CONF_DHCP_RELAY['loc_total_dhcp_relay_span'], 'DHCP Relay'))
    if total_dhcps == 0:
        logging.info("There is no dhcp relay server in the table")
        return
    
    while zd.s.is_visible(LOCATORS_CONF_DHCP_RELAY['loc_show_more_button']):
        zd.s.click_and_wait(LOCATORS_CONF_DHCP_RELAY['loc_show_more_button'])
    
    while total_dhcps:            
        try:
            zd.s.click_and_wait(LOCATORS_CONF_DHCP_RELAY['loc_select_all_checkbox'])
            
            zd.s.choose_ok_on_next_confirmation()
            zd.s.click_and_wait(LOCATORS_CONF_DHCP_RELAY['loc_delete_button'])
            
            if (zd.s.is_alert_present(5)):
                msg_alert = zd.s.get_alert()
                raise Exception(msg_alert)
        except Exception, e:
            msg = 'Failed to delete all DHCP relay servers: %s' % (e.message)
            logging.debug(msg)
            raise Exception(msg)
            
        total_dhcps = int(zd._get_total_number(LOCATORS_CONF_DHCP_RELAY['loc_total_dhcp_relay_span'], 'DHCP Relay'))
    
    logging.info("All dhcp relay server are deleted")
        
    