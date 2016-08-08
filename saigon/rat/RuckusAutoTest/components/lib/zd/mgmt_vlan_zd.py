import time
import logging

LOCATOR_CFG_MGMTVLAN = dict(
    # ZD Management VLAN
    zd_mgmt_vlan_enable_checkbox = r"//form[@id='form-mgmt-vlan']//input[@id='enable-mgmt-vlan']",
    zd_mgmt_vlan_textbox = r"//form[@id='form-mgmt-vlan']//input[@id='mgmt-vlan']",
    zd_mgmt_vlan_apply_button = r"//form[@id='form-mgmt-vlan']//input[@id='apply-mgmt-vlan']",
    # AP Policy - Limited zd Discovery
    appolicy_allow_all_checkbox = r"//input[@id='allow-all']",
    appolicy_zd_ip_enable_checkbox = r"//form[@id='form-appolicy']//input[@id='enable-zd-ip']",
    appolicy_zd_prim_ip_textbox = r"//form[@id='form-appolicy']//input[@id='zd-prim-ip']",
    appolicy_zd_sec_ip_textbox = r"//form[@id='form-appolicy']//input[@id='zd-sec-ip']",
    appolicy_apply_button = r"//input[@id='apply-appolicy']",
    appolicy_max_clients_textbox = r"//input[@id='max-clients']",
    # AP Policy - AP Management VLAN
    appolicy_mgmt_vlan_disable_checkbox = r"//form[@id='form-appolicy']//input[@id='disable-mgmt-vlan']",
    appolicy_mgmt_vlan_enable_checkbox = r"//form[@id='form-appolicy']//input[@id='enable-mgmt-vlan']",
    appolicy_mgmt_vlan_textbox = r"//form[@id='form-appolicy']//input[@id='mgmt-vlan-ap']",
    appolicy_mgmt_vlan_keep_checkbox = r"//form[@id='form-appolicy']//input[@id='keep-mgmt-vlan']",
)

# zd_mgmt_vlan = get_zd_mgmt_vlan_info(zd)
def get_zd_mgmt_vlan_info(zd, debug = False, timeout = 120):
    endtime = time.time() + timeout
    while time.time() < endtime:
        try:
            return _get_zd_mgmt_vlan_info(zd)

        except:
            time.sleep(1)

    raise Exception('Can not get ZoneDirector zd mgmt_vlan')


def _get_zd_mgmt_vlan_info(zd, debug = False):
    xloc = LOCATOR_CFG_MGMTVLAN
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)

    zd_mgmt_vlan = {}
    zd_mgmt_vlan['vlan_id'] = zd.s.get_value(xloc['zd_mgmt_vlan_textbox'])
    zd_mgmt_vlan['enabled'] = zd.s.is_checked(xloc['zd_mgmt_vlan_enable_checkbox'])

    return zd_mgmt_vlan


# ap_policy = get_ap_mgmt_vlan_info(zd)
def get_ap_mgmt_vlan_info(zd, debug = False, timeout = 120):
    endtime = time.time() + timeout
    while time.time() < endtime:
        try:
            return _get_ap_mgmt_vlan_info(zd)

        except:
            time.sleep(1)

    raise Exception('Can not get ZoneDirector AP mgmt_vlan')


def _get_ap_mgmt_vlan_info(zd, debug = False):
    xloc = LOCATOR_CFG_MGMTVLAN
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_POINT)
    
    ap_policy = {}
    ap_policy['auto_approval'] = zd.s.is_checked(xloc['appolicy_allow_all_checkbox'])
    ap_policy['max_clients'] = zd.s.get_value(xloc['appolicy_max_clients_textbox'])
    ap_policy['mgmt_vlan'] = {}    
    ap_policy['mgmt_vlan']['vlan_id'] = zd.s.get_value(xloc['appolicy_mgmt_vlan_textbox'])
    ap_policy['mgmt_vlan']['enabled'] = zd.s.is_checked(xloc['appolicy_mgmt_vlan_enable_checkbox'])
    ap_policy['mgmt_vlan']['disabled'] = zd.s.is_checked(xloc['appolicy_mgmt_vlan_disable_checkbox'])
    ap_policy['mgmt_vlan']['keep'] = zd.s.is_checked(xloc['appolicy_mgmt_vlan_keep_checkbox'])
    ap_policy['zd_discovery'] = {}
    ap_policy['zd_discovery']['enabled'] = zd.s.is_checked(xloc['appolicy_zd_ip_enable_checkbox'])
    ap_policy['zd_discovery']['prim_ip'] = zd.s.get_value(xloc['appolicy_zd_prim_ip_textbox'])
    ap_policy['zd_discovery']['sec_ip'] = zd.s.get_value(xloc['appolicy_zd_sec_ip_textbox'])

    return ap_policy


def set_zd_mgmt_vlan_info(zd, zd_mgmt_vlan, debug = False):
    logging.info('set zd MgmtVlan with args: %s' % str(zd_mgmt_vlan))
    xloc = LOCATOR_CFG_MGMTVLAN
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)

    mgmt_vlan_enabled = zd.s.is_checked(xloc['zd_mgmt_vlan_enable_checkbox'])

    if zd_mgmt_vlan.has_key('enabled'):
        is_enabled = click_checkbox_if_not_eq(zd, xloc['zd_mgmt_vlan_enable_checkbox'],
                                              zd_mgmt_vlan['enabled'])

        if is_enabled:
            if zd_mgmt_vlan.has_key('vlan_id'):
                zd.s.type_text(xloc['zd_mgmt_vlan_textbox'],
                               unicode(zd_mgmt_vlan['vlan_id']))

            else:
                logging.info("Field 'vlan_id' is required when zd mgmt_vlan is enabled.")

    zd.s.click_and_wait(xloc['zd_mgmt_vlan_apply_button'])
    # no # zd.logout() because we might lost connection between TE and zd
    # no call to get_zd_mgmt_vlan_info() neither; because we might lost connection to zd already
    return {}


def set_ap_mgmt_vlan_info(zd, ap_policy, debug = False):
    logging.info('set AP MgmtVlan with args: %s' % str(ap_policy))
    xloc = LOCATOR_CFG_MGMTVLAN
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_POINT)

    if ap_policy.has_key('auto_approval'):
        click_checkbox_if_not_eq(zd, xloc['appolicy_allow_all_checkbox'],
                                 ap_policy['auto_approval'])

    if ap_policy.has_key('max_clients'):
        zd.s.type_text(xloc['appolicy_max_clients_textbox'],
                       unicode(ap_policy['max_clients']))

    if ap_policy.has_key('zd_discovery') and ap_policy['zd_discovery'].has_key('enabled'):
        zd_discovery = ap_policy['zd_discovery']
        is_enabled = click_checkbox_if_not_eq(zd, xloc['appolicy_zd_ip_enable_checkbox'],
                                              zd_discovery['enabled'])

        if is_enabled:
            if zd_discovery.has_key('prim_ip'):
                zd.s.type_text(xloc['appolicy_zd_prim_ip_textbox'],
                               unicode(zd_discovery['prim_ip']))

            if zd_discovery.has_key('sec_ip'):
                zd.s.type_text(xloc['appolicy_zd_sec_ip_textbox'],
                               unicode(zd_discovery['sec_ip']))

    if ap_policy.has_key('mgmt_vlan'):
        mgmt_vlan = ap_policy['mgmt_vlan']
        if mgmt_vlan.has_key('disabled') and mgmt_vlan['disabled']:
            if zd.s.is_element_present(xloc['appolicy_mgmt_vlan_disable_checkbox']):
                click_checkbox_if_not_eq(zd, xloc['appolicy_mgmt_vlan_disable_checkbox'],
                                         mgmt_vlan['disabled'])
            else:
                click_checkbox_if_not_eq(zd, xloc['appolicy_mgmt_vlan_enable_checkbox'],
                                         mgmt_vlan['enabled'])
    
                zd.s.type_text(xloc['appolicy_mgmt_vlan_textbox'], '1')

        elif mgmt_vlan.has_key('keep') and mgmt_vlan['keep']:
            click_checkbox_if_not_eq(zd, xloc['appolicy_mgmt_vlan_keep_checkbox'],
                                     mgmt_vlan['keep'])

        elif mgmt_vlan.has_key('enabled') and mgmt_vlan['enabled']:
            if not mgmt_vlan.has_key('vlan_id'):
                logging.info("Field 'vlan_id' is required when AP mgmt_vlan is enabled.")

            click_checkbox_if_not_eq(zd, xloc['appolicy_mgmt_vlan_enable_checkbox'],
                                     mgmt_vlan['enabled'])

            zd.s.type_text(xloc['appolicy_mgmt_vlan_textbox'],
                           unicode(mgmt_vlan['vlan_id']))

    zd.s.click_and_wait(xloc['appolicy_apply_button'])

    ap_info = get_ap_mgmt_vlan_info(zd)
    # no logout required; because get_ap_mgmt_vlan_info() will login and logout

    return ap_info


def click_checkbox_if_not_eq(zd, checkbox_loc, target_value):
    is_enabled = zd.s.is_checked(checkbox_loc)
    if is_enabled is target_value:
        # checkbox is set to what I want; no action
        return is_enabled

    zd.s.click(checkbox_loc)

    return zd.s.is_checked(checkbox_loc)


def get_node_mgmt_vlan_info(zd):
    mgmt_vlan = {}
    mgmt_vlan['zd'] = get_zd_mgmt_vlan_info(zd)
    mgmt_vlan['ap'] = get_ap_mgmt_vlan_info(zd)

    return mgmt_vlan

