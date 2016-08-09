'''
All about Access Point Policy:
 .Approval
 .Management VLAN
 .Load Balancing
 .Max Clients
 .LWAPP message MTU
'''

#-----------------------------------------------------------------------------
# PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def set_access_point_policy(zd,
        auto_approval = None,
        zd_discovery = None,
        mgmt_vlan = None,
        load_balancing = None,
        max_clients = None,
        message_mtu = None
    ):
    '''
    auto_approval = True,
    zd_discovery = {
        'enabled': False,
        'pri_ip': '',
        'sec_ip': '',
    },
    mgmt_vlan = {
        'mode': 'disable' #[keep, disable, enable]
        'vlan_id': '',
    },
    load_balancing = False,
    max_clients = {
        'bg': 100,
        'n': 100,
    },
    message_mtu = 1450,
    '''
    pass


def set_ap_mgmt_vlan(zd, mode, vlan_id = ''):
    '''
    mgmt_vlan = {
        'mode': 'disable' #[keep, disable, enable]
        'vlan_id': '',
    },
    '''
    _nav_to(zd)
    
    import time
    
    time.sleep(10)
    _set_ap_mgmt_vlan(zd, mode, vlan_id)
    
    time.sleep(10)
    
    _apply_ap_policy(zd)


def get_ap_mgmt_vlan(zd):
    '''
    mgmt_vlan = {
        'mode': 'disable' #[keep, disable, enable]
        'vlan_id': '',
    },
    '''
    _nav_to(zd)

    info = _get_ap_mgmt_vlan(zd)

    return info


#-----------------------------------------------------------------------------
#  PRIVATE SECTION
#-----------------------------------------------------------------------------

locs = dict(
    # Approval
    allow_all_checkbox = r"//input[@id='allow-all']",

    # Limited ZD Discovery
    zd_ip_enable_checkbox = r"//input[@id='enable-zd-ip']",
    zd_prim_ip_textbox = r"//input[@id='zd-prim-ip']",
    zd_sec_ip_textbox = r"//input[@id='zd-sec-ip']",

    # Management VLAN
    mgmt_vlan_keep_checkbox = r"//input[@id='keep-mgmt-vlan']",
    mgmt_vlan_disable_checkbox = r"//input[@id='disable-mgmt-vlan']",
    mgmt_vlan_enable_checkbox = r"//input[@id='enable-mgmt-vlan']",
    mgmt_vlan_textbox = r"//input[@id='mgmt-vlan-ap']",

    #####@zj 20140611 zf-8370
    mgmt_vlan_reconfirm_dialog = r"//div[@class='reconfirm-dialog']",
    mgmt_vlan_reconfirm_dialog_mgmtvlan_checkbox = r"//label//input[@type='checkbox']",
    mgmt_vlan_reconfirm_dialog_ok_button = r"//button[text()='OK']",
    mgmt_vlan_reconfirm_dialog_cancel_button = r"//button[text()='Cancel']",
    #####@zj 20140611 zf-8370
        
    # Load Balancing
    balance_disable_checkbox = r"//input[@id='balance-disable']",
    balance_enable_checkbox = r"//input[@id='balance-enable']",

    # Max Clients
    max_clients_textbox = r"//input[@id='max-clients']",
    max_clients11n_textbox = r"//input[@id='max-clients-11n']",

    # LWAPP message MTU
    message_mtu_textbox = r"//input[@id='msg-mtu']",

    # ALL
    apply_button = r"//input[@id='apply-appolicy']",
)


def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_POINT)


def _apply_ap_policy(zd):
    '''
    '''
    zd.s.click_and_wait(locs['apply_button'])

    #####@zj 20140611 zf-8370
    if zd.s.is_element_present(locs['mgmt_vlan_reconfirm_dialog']):
        zd.s.click_and_wait(locs['mgmt_vlan_reconfirm_dialog_mgmtvlan_checkbox'])
        zd.s.click_and_wait(locs['mgmt_vlan_reconfirm_dialog_ok_button'])
    #####@zj 20140611 zf-8370  
    
    if zd.s.is_alert_present(1.5):
        _alert = zd.s.get_alert()
        raise Exception(_alert)    
		 
def _set_ap_mgmt_vlan(zd, mode, vlan_id = ''):
    '''
    mgmt_vlan = {
        'mode': 'disable' #[keep, disable, enable]
        'vlan_id': '',
    },
    '''
    xpath_by_mode = {
        'keep': locs['mgmt_vlan_keep_checkbox'],
        'disable': locs['mgmt_vlan_disable_checkbox'],
        'enable': locs['mgmt_vlan_enable_checkbox'],
    }
    #@author: Jessie.Zhang @since: 2013-09 fix bug is_element_present
    if mode == 'disable' and not zd.s.is_element_present(xpath_by_mode[mode]):
        zd.s.click_and_wait(xpath_by_mode['enable'])
        zd.s.type_text(locs['mgmt_vlan_textbox'], '1')
        return
    
    zd.s.click_and_wait(xpath_by_mode[mode])

    if mode == 'enable':
        zd.s.type_text(locs['mgmt_vlan_textbox'], vlan_id)


def _get_ap_mgmt_vlan(zd):
    '''
    mgmt_vlan = {
        'mode': 'disable' #[keep, disable, enable]
        'vlan_id': '',
    },
    '''
    xpath_by_mode = {
        'keep': locs['mgmt_vlan_keep_checkbox'],
        'disable': locs['mgmt_vlan_disable_checkbox'],
        'enable': locs['mgmt_vlan_enable_checkbox'],
    }

    mgmt_vlan = {}
    for (item, loc) in xpath_by_mode.iteritems():
        if zd.s.is_element_present(loc) and zd.s.is_checked(loc):
            mgmt_vlan.update({'mode': item})
            break

    if mgmt_vlan.get('mode') == 'enable':
        vlan_id = zd.s.get_value(locs['mgmt_vlan_textbox'])
        mgmt_vlan.update({'vlan_id': vlan_id})
        if vlan_id == '1':
            mgmt_vlan.update({'mode': 'disable'})

    return mgmt_vlan

feature_update = {
}

