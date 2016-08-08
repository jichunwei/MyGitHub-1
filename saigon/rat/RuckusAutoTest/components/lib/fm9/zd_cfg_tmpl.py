'''
Support page:
    Configure > ZoneDirectors > Config Templates.

Supported functions:
1. Create a ZD template.
2. Edit a Zd template
3. Delete ZD template
4. Find zd tmpl
5. Get template config:
    . To get whole config in a template. This is to support for getting
      provisioning result to do compare bt ZD UI and ZD template.

6. Get cfg of a form (get_form_cfg):
    . To get config of one following pages: wlans, ap policies, system, hotspot,
      aaa server from both ZD Template and ZD UI

'''
import re
import logging
import time
from pprint import pformat
from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns
from RuckusAutoTest.components import Helper_ZD as zd_libs
#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def create_zd_tmpl(fm, tmpl_name, bk_cfg_name, cfg, timeout = 300):
    '''
    cfg = dict(
        # sample cfg for wlans form
        wlans = {
            'wlan': dict(
                'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '',
                'encryption': '', 'type': 'standard', 'hotspot_profile': '',
                'key_string': '', 'key_index': '', 'auth_svr': '',
                'do_webauth': None, 'do_isolation': None, 'do_zero_it': None,
                'do_dynamic_psk': None, 'acl_name': '', 'l3_l4_acl_name': '',
                'uplink_rate_limit': '', 'downlink_rate_limit': '',
                'dvlan': False, 'vlan_id': None, 'do_hide_ssid': None,
                'do_tunnel': None, 'acct_svr': '', 'interim_update': None
            ),
            wlan_group = dict(
                name = string,
                description = string,
                member_wlans = [list of wlan members],
                enable_vlan_override = True | False,
            ),
            psk_expiration = 'Unlimited' | 'One day' | 'One week' | 'Two weeks'...
        },
        'ap_policies': {
            'limited_zd_discovery': dict(
                enabled = False,
                primary_zd_ip = '192.168.0.189',
                secondary_zd_ip = ''
            ),
        },
        'aaa_servers':
            'server': {
                'server_addr': '', 'server_port': '', 'server_name': '',
                'win_domain_name': '', 'ldap_search_base': '',
                'ldap_admin_dn': '', 'ldap_admin_pwd': '',
                'radius_auth_secret': '', 'radius_acct_secret': ''
            },
        },
        'hotspot_servers': {
            'service': {
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
            },
        }
    )
    '''
    nav_to(fm, True)
    _cfg_zd_tmpl(fm, tmpl_name, cfg, bk_cfg_name, 'create', timeout)


def edit_zd_tmpl(fm, tmpl_name, new_cfg, timeout = 300):
    '''
    . to edit configurations such as WLANs, AAA Server, Hotspot Services ...
      of the zd config template.
      Support:
            - Add a new form to current ZD template.
            - Add new items to an existing form.
      Not support:
            - Clone/delete an existing items of a form.
            - Rename/Modify attribute(s) of an item of a existing form.

            E.g: The current template has WLANs form containing wlan "test1",
                 the test script is unable to rename this wlan "test1"
                 as well as its other attributes.
    . new_cfg: refer to create_zd_tmpl to know its keys
    '''
    r_info = find_zd_tmpl(fm, tmpl_name)
    if not r_info:
        raise Exception('Not found the ZD template %s' % tmpl_name)

    fm.s.click_and_wait(r_info['links']['edit'])
    _wait_the_form_stable(fm.s, 'Initial Form')
    _unselect_all_cfg_options(fm.s)
    _cfg_zd_tmpl(fm, tmpl_name, new_cfg, '', 'edit', timeout)


def rename_zd_tmpl(fm, old_name, new_name):
    '''
    Bug: Currently, cannot rename a zd template name. FM always shows error
         message so NOT SUPPORT rename the template now.
    '''
    s = fm.selenium
    r_info = find_zd_tmpl(fm, old_name)
    if not r_info:
        raise Exception('Not found the ZD template %s' % old_name)
    s.click_and_wait(r_info['links']['edit'])

    #_cfg_zd_tmpl(fm, new_name, cfg, timeout)


def delete_zd_tmpl(fm, tmpl_name):
    s = fm.selenium
    r_info = find_zd_tmpl(fm, tmpl_name)

    if not r_info:
        raise Exception('Not found the ZD template %s' % tmpl_name)

    s.click_and_wait(r_info['links']['delete'])
    # Get OK, Cancel pop up. Otherwise, an exception will be raised and this selenium fails.
    if s.is_confirmation_present():
        logging.info('Got a pop up window "%s"' % s.get_confirmation())

    return


def find_zd_tmpl(fm, tmpl_name):
    '''
    . to find a report with report name
    '''
    nav_to(fm, True)

    return _get_tbl(
        fm, 'tmpl_tbl',
        dict(
             match=dict(templatename=tmpl_name),
             op = 'equal',
             get = '1st'
        )
    )


def get_tmpl_cfg(fm, tmpl_name, timeout = 300):
    '''
    to get configuration of a template.
    '''
    s, l, expired_time, cfg = fm.s, locators, timeout + time.time(), {}

    r = find_zd_tmpl(fm, tmpl_name)
    if not r:
        raise Exception('Not found template name %s' % tmpl_name)

    s.click_and_wait(r['links']['edit'])
    _wait_the_form_stable(s, 'Initial Form')
    selected_form_order = _get_selected_items(fm)

    while len(selected_form_order) > 0 and time.time() < expired_time:
        s.click_and_wait(l['next_btn'], 0.5)
        current_form = selected_form_order[0]
        _wait_the_form_stable(s, current_form)
        # get cfg of current form
        cfg[current_form] = get_form_cfg(fm, current_form, is_nav = False)
        # remove the form configured out of form_order
        del selected_form_order[0]

    if time.time() > expired_time:
        raise Exception(
            'Error: Cannot get configuration of zd template % after %s(s)' %
            (tmpl_name, timeout)
        )

    s.click_and_wait(l['cancel_btn'], 0.5)

    return cfg


def get_form_cfg(obj, form, is_nav = False):
    '''
    . to get form wlans, ap policies, system, hotspot, aaa server.
      It will support to get these forms from ZD template or ZD UI.
    . form: form to get cfg.
    . is_nav: False: to get cfg of ZD template from FM
              True: to get cfg from ZD UI.
    '''
    # get wlan
    fn_map = dict(
        # get functions for wlans form
        wlans = dict(
            wlan = zd_libs.wlan.get_wlan_cfg_list_2,
            wlan_group = zd_libs.wgs.get_all_wlan_group_cfgs,
            psk_expiration = zd_libs.wlan.get_psk_expiration,
        ),
        # get functions for ap polices form
        ap_policies = dict(
            limited_zd_discovery = zd_libs.ap.get_limited_zd_discovery_cfg,
        ),
        # get functions for hotspot service form
        hotspot_services = dict(
            service = zd_libs.wispr.get_all_profiles
        ),
        # get functions for aaa servers form
        aaa_servers = dict(
            server = zd_libs.aaa.get_auth_server_info_list,
        ),
        # get functions for System form
        system = dict(
            log = zd_libs.sys.get_syslog_info,
        )
    )
    cfg = {}
    for k, get_fn in fn_map[form].items():
        cfg[k] = get_fn(obj, is_nav = is_nav)

    return cfg
#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
def _cfg_zd_tmpl(fm,
                 tmpl_name,
                 cfg,
                 bk_cfg_name,
                 action = 'create',
                 timeout = 300
    ):
    '''
    . Currently support items: wlans, hotspot_services and aaa_servers only
    . cfg = dict(
        wlans = dict(
            refer to _cfg_wlans_form for its sub cfg detail
        ),
        ap_policies = dict(
            refer to _cfg_ap_policies_form func for its cfg detail
        ),
        hotspot_services = dict(
            refer to _cfg_hotspot_server_forms function for its cfg detail
        ),
        aaa_servers = dict(
            refer to _cfg_aaa_servers_form func for its cfg detail
        ),
        log_settings = dict(
            refer to _cfg_system_form func for its cfg detail
        ),
    )
    . bk_cfg_name: Let it empty for the case edit a zd template
    '''
    # configure the initial form of zd template
    _cfg_initial_tmpl_form(fm, action, tmpl_name, bk_cfg_name, cfg.keys())
    # configure other forms
    _fill_in_cfg(fm, cfg, timeout)


def _cfg_initial_tmpl_form(fm, action, tmpl_name, bk_cfg_name, cfg_ks):
    '''
    . to do configure the initial form of configuring ZD template
    '''
    # build configuration items to do configure the inital template form
    # get check boxes items.
    _cfg_ks = dict.fromkeys(cfg_ks, True)
    _cfg_ks.update(dict(
        tmpl_name = tmpl_name,
    ))

    if action == 'create':
        _cfg_ks.update(dict(
            create_tmpl = '',
            bk_cfg_name = bk_cfg_name,
        ))

    _set(fm, _cfg_ks, initial_form_co)


def _fill_in_cfg(fm, cfg, timeout = 300):
    '''
    . to fill input cfg into its form accordingly
    '''
    s, l, expired_time = fm.s, locators, timeout + time.time()

    # get forms need to be configured
    present_form_order = _get_present_form_order(cfg.keys())

    # configure other forms
    while len(present_form_order) > 0 and time.time() < expired_time:
        s.click_and_wait(l['next_btn'], 0.5)
        # get current form
        current_form = present_form_order[0]
        _wait_the_form_stable(s, current_form)
        # config the current form
        _cfg_tmpl_form(fm, current_form, cfg[current_form])
        # remove the form configured out of form_order
        del present_form_order[0]

    if time.time() > expired_time:
        raise Exception(
            'Error: Cannot complete configuring zd template after %s(s)' %
            timeout
        )

    s.click_and_wait(l['save_btn'], 0.5)
    if not _get_result_status(fm):
        logging.info('Saved the ZD template successfully.')


def _unselect_all_cfg_options(se):
    # Click twice to un-select all config check box
    se.click_if_not_checked(locators['select_all'])
    se.click_if_checked(locators['select_all'])


def _get_selected_items(fm):
    '''
    . return a list of following keys ['wlans', 'ap_policies',
    'hotspot_services', 'aaa_servers', 'system'] if it is
    selected in the template.

    '''
    items = [
        'wlans', 'ap_policies', 'hotspot_services', 'aaa_servers', 'system'
    ]
    return [k for k in items if _get(fm, [k])[k]]


def _cfg_tmpl_form(fm, form, cfg):
    '''
    to do configure for following forms wlans, 'ap_policies', 'hotspot_services',
    'aaa_servers', 'system'.

    . form: name of form for each page: wlans, 'ap_policies', 'hotspot_services',
            'aaa_servers', 'system'.
    .
    '''
    cfg_fn_map = dict(
        # set functions for wlans form
        wlans = dict(
            wlan = zd_libs.wlan.create_wlan,
            wlan_group = zd_libs.wgs.create_wlan_group_2,
            psk_expiration = zd_libs.wlan.set_psk_expiration,
        ),
        # set functions for ap polices form
        ap_policies = dict(
            limited_zd_discovery = zd_libs.ap.cfg_limited_zd_discovery,
        ),
        # set functions for hotspot service form
        hotspot_services = dict(
            service = zd_libs.wispr.create_profile_2
        ),
        # set functions for aaa servers form
        aaa_servers = dict(
            server = zd_libs.aaa.create_server_2,
        ),
        # set functions for System form
        system = dict(
            log = zd_libs.sys.set_syslog_info,
        )
    )

    for k, sub_cfg in cfg.items():
        logging.info(
            'Configure %s, (key, cfg): (%s, %s)' % (form, k, pformat(sub_cfg))
        )
        cfg_fn_map[form][k](fm, sub_cfg, is_nav = False)


result_parent_div = "//div[@dojoattachpoint='dataAreaFirstLayerContainer']"
report_list_parent_div = "//div[@dojoattachpoint='savedReportsContainer']"

locators = dict(
    create_tmpl = Ctrl("//div[@id='newZdTemplateAction']//span[contains(., 'Create a template')]", 'button'),
    tmpl_name = Ctrl("//input[@id='templateName']", 'text'),
    bk_cfg_name = Ctrl("//select[@id='backupConfigOption']", 'select'),

    select_all = "//input[@id='selectAllCheckBox']",
    wlans            = Ctrl("//input[@id='wlanCheckBox']", 'check'),
    ap_policies      = Ctrl("//input[@id='apPoliciesCheckBox']", 'check'),
    hotspot_services = Ctrl("//input[@id='hotspotCheckBox']", 'check'),
    aaa_servers      = Ctrl("//input[@id='aaaCheckBox']", 'check'),
    # Log Settings
    system     = Ctrl("//input[@id='logSettingsCheckBox']", 'check'),

    next_btn = "//input[@id='nextWizard']", # don't use AC lib for this control
    save_btn = "//input[@value='Save']", # don't use AC lib for this control
    cancel_btn = "//input[@value='Cancel']",
    loading_indicator = "//img[@id='imgLoading']",
    result_msg = "//a[@id='statusMessageLink']",

    tmpl_tbl = Ctrl(
        dict(
             tbl = "//table[@class='tableArea']",
             nav = "//table[@class='pageSelector']",
        ),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            links = dict(
                edit = "//span[.='Edit']",
                delete = "//span[.='Delete']",
            ),
        ),
    )
)

SUCCESS_MSG = 'success'
ctrl_order = '''
'''
form_order = [
    'wlans', 'ap_policies', 'hotspot_services',
    'aaa_servers', 'system'
]
initial_form_co = '''
[None create_tmpl tmpl_name bk_cfg_name wlans ap_policies hotspot_services
aaa_servers system]
'''

def nav_to(fm, force = True):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_ZD_CONFIG_TMPLS, force = force)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = None, # don't use now
)


def _set(fm, cfg, order = 'default'):
    return fns.set(m, fm, cfg, is_nav = False, order = order)


def _get(fm, cfg, order = 'default'):
    return fns.get(m, fm, cfg, is_nav = False, order = order)


def _get_tbl(fm, tbl, cfg={}, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav = False, order = order)


def _get_result_status(fm):
    '''
    . return
        None if success
        raise exception if other.
    '''
    s, l = fm.selenium, locators
    msg = s.get_text(l['result_msg'])

    if re.search(SUCCESS_MSG, msg, re.I):
        return None

    raise Exception('Cannot save the template. Error: %s' % msg)
#-------------------------------------------------------------------------------
#  PRIVATE METHODS
#-------------------------------------------------------------------------------
def _wait_the_form_stable(se, form, timeout = 180):
    ''''''
    ld_ind = locators['loading_indicator']
    expired_time = timeout + time.time()
    while se.is_element_displayed(ld_ind) and time.time() < expired_time:
        time.sleep(0.5)

    if time.time() > expired_time:
        raise Exception(
            'The form %s is still in loading after %s(s)' % (form, timeout)
        )

    time.sleep(1.5)

def _get_present_form_order(form_list):
    '''
    . to get forms with order from the form_list
    '''
    # filter form is not in form_list
    present_form_order = []
    for form in form_order:
        if form in form_list: present_form_order.append(form)

    return present_form_order

#---------------------------------------------------------------------------------
if __name__ == '__main__':
    #from ratenv import *
    from pprint import pprint
    from RuckusAutoTest.common.SeleniumControl import SeleniumManager
    from RuckusAutoTest.components.FlexMaster import FlexMaster

    sm = SeleniumManager()
    print "type of sm: ", type(sm)
    config = {
        'username': 'admin@ruckus.com',
        'password': 'admin'
    }

    fm = FlexMaster(sm, 'firefox', '192.168.0.124', config)
    fm.start()
    fm.login()

    fm.stop()
    cfg = dict(
        wlans = dict(
            wlan = {
                'ssid': 'test', 'description': 'test',
                'auth': 'open', # 'open' | 'shared' | 'eap' | 'mac'
                'wpa_ver': '',
                'encryption': 'none', ## 'none' | 'wpa' | 'wpa2' | 'wpa_mixed' | 'wep64' | 'wep128'
                #'type': 'standard', 'hotspot_profile': '',
                #'key_string': '', 'key_index': '', 'auth_svr': '',
                #'do_webauth': None, 'do_isolation': None, 'do_zero_it': None,
                #'do_dynamic_psk': None, 'acl_name': '', 'l3_l4_acl_name': '',
                #'uplink_rate_limit': '', 'downlink_rate_limit': '',
                #'dvlan': False, 'vlan_id': None, 'do_hide_ssid': None,
                #'do_tunnel': None, 'acct_svr': '', 'interim_update': None
            },
            wlan_group = dict(
                name = 'test group',
                description = 'test group',
                member_wlans = ['test'],
                enable_vlan_override = True, #True | False,
            ),
            psk_expiration = 'Unlimited', #'Unlimited' | 'One day' | 'One week' | 'Two weeks'...
        ),
        ap_policies = dict(
            limited_zd_discovery = dict(
                enabled = True, # False
                primary_zd_ip = '192.168.0.189',
                secondary_zd_ip = '',
            ),
        ),
        hotspot_services = {
            'name': 'test hotspot',
            'login_page': 'test.htm',
            'start_page': None,
            'session_timeout': 60,
            'idle_timeout': 10,
            'auth_svr': '', #'192.168.30.252',
            'acct_svr': '', #'192.168.30.252',
            #'interim_update_interval': None,
            #'radius_location_id': '',
            #'radius_location_name': '',
            #'walled_garden_list': [],
            #'restricted_subnet_list': [],
            #'enable_mac_auth': None,
        },
        aaa_servers = {
            'server_name': 'radius_srv',
            'server_addr': '192.168.30.252',
            'server_port': '1812',
            #'win_domain_name': '', 'ldap_search_base': '',
            #'ldap_admin_dn': '', 'ldap_admin_pwd': '',
            'radius_auth_secret': '123456',
            #'radius_acct_secret': ''
        },
        log_settings = dict(
            log_level = 'show_more', #'warning_and_critical' | 'critical_events_only'
            enable_remote_syslog = True, # False
            remote_syslog_ip = '192.168.30.252',
        ),
    )
