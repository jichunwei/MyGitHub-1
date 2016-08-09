
def enable_mgmt_inf(zd,ip_addr,net_mask,vlan=None):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    _enable_management_interface(zd,ip_addr,net_mask,vlan)

def disable_mgmt_inf(zd):
    zd.navigate_to(zd.CONFIGURE,zd.CONFIGURE_SYSTEM)
    _disable_management_interface(zd)

def get_mgmt_inf(zd):
    zd.navigate_to(zd.CONFIGURE,zd.CONFIGURE_SYSTEM)
    return _get_management_interface(zd)


#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
locs = dict(
    management_interface_enable_ckeckbox = "//input[@id='enable-addif']",
    management_ip_address_text = "//input[@id='addif-ip']",
    management_interface_netmask = "//input[@id='addif-netmask']",
    management_interface_vlan = "//input[@id='addif-vlan']",
    management_interface_apply_button = "//input[@id='apply-addif']",
    mgmt_inf_click_here_text = "//p[@id='show-config-addif']/a"
)


def _enable_management_interface(zd,ip_addr,net_mask,vlan=None,pause = 5):
    if locs['mgmt_inf_click_here_text'] and zd.s.is_element_present(locs['mgmt_inf_click_here_text']):
        zd.s.click_and_wait(locs['mgmt_inf_click_here_text'])
    zd.s.click_if_not_checked(locs['management_interface_enable_ckeckbox'])
    zd.s.type_text(locs['management_ip_address_text'],ip_addr,timeout=0.5)
    zd.s.type_text(locs['management_interface_netmask'],net_mask,timeout=0.5)
    zd.s.type_text(locs['management_interface_vlan'],vlan,timeout=0.5)
    zd.s.click_and_wait(locs['management_interface_apply_button'],pause)

def _disable_management_interface(zd, pause = 3):
    zd.s.click_if_checked(locs['management_interface_enable_ckeckbox'])
    zd.s.click_and_wait(locs['management_interface_apply_button'],pause)

def _get_management_interface(zd):
    if zd.s.get_value(locs['management_interface_enable_ckeckbox']) == 'on':
        status = 'Enabled'
    else:
        status = 'Disabled'

    ip_addr = zd.s.get_value(locs['management_ip_address_text'])
    net_mask = zd.s.get_value(locs['management_interface_netmask'])
    vlan = zd.s.get_value(locs['management_interface_vlan'])

    return {'Status':status,'IP Address':ip_addr,'Netmask':net_mask,'VLAN':vlan}

