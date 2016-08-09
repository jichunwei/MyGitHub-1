from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns

locators = dict(
    add_mgmt_interface = Ctrl("//p[@id='show-config-addif']/a[.='click here']", "button"),
    en_mgmt_interface = Ctrl("//input[@id='enable-addif']", "check"),
    add_if_ip = Ctrl("//input[@id='addif-ip']", "text"),
    if_mask = Ctrl("//input[@id='addif-netmask']", "text"),
    if_vlan = Ctrl("//input[@id='addif-vlan-id']", "text"),
    if_apply = Ctrl("//input[@id='apply-addif']", "button"),
)

ctrl_order = '''
[add_mgmt_interface en_mgmt_interface
  add_if_ip if_mask if_vlan
if_apply]
'''

get_info_order = '''
[None
  en_mgmt_interface add_if_ip if_mask if_vlan
None]
'''

#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------

def enable_mgmt_interface(zd, cfg):
    '''
    enable mgmt interface
    cfg:  = dict(en_mgmt_interface=True, add_if_ip='192.168.2.1', if_mask='255.255.255.0', if_vlan='')
    .  en_mgmt_interface: enable mgmt if
    .  add_if_ip:  ip interface,
    .  if_mask:    subnet mask,
    .  if_vlan:    vlan id,
    '''
    return _set(zd, cfg, is_nav = True, order = ctrl_order)

def get_mgmt_interface(zd):
    '''

    '''
    cfg = dict(  en_mgmt_interface=True,
                 add_if_ip='',
                 if_mask='', if_vlan='')

    return _get(zd, cfg, is_nav = True, order = get_info_order)

#--------------------------------------------------------
#  PROTECTED METHODS
#--------------------------------------------------------

def nav_to(zd, force = False):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM, force=True)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)

def _set(zd, cfg, is_nav = True, order = 'default'):
    return fns.set(m, zd, cfg, is_nav, order)






