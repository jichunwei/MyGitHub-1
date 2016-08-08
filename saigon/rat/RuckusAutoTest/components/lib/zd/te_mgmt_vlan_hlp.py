"""
I can deal with components NetgeareSwitchRouter and ZoneDirector at the same time.

Take notice:

    When tag/untag ZD MgmtVlan,
    the SwitchRouter's ZD port's native VLAN need to be tag/untag.

"""
import time
import re

from RuckusAutoTest.components.lib.zd import mgmt_vlan_zd as MVLAN 
from RuckusAutoTest.components.lib.zd import nsr_hlp as NSRHLP

def get_zd_switch_port(zd, nsr):
    nsr.perform('clear mac-addr-table all')
    zd_mac_addr = zd.get_mac_address()
    zd_swp = {'mac_addr': zd_mac_addr}
    ptn = r"^%s\s+([0-9/]+)\s+(\d+)\s+(\d+)\s+" % zd_mac_addr
    mac_addr_table_info = nsr.perform('show mac-addr-table')
    
    m = re.search(ptn, mac_addr_table_info, re.M | re.I)
    if m:
        zd_swp.update({'interface':m.group(1), 'ifindex':m.group(2), 'vlan_id':m.group(3)})
        
    return zd_swp


def tag_zd_mgmt_vlan(zd, nsr, sw_interface, vlan_id = 301):
    zdinfo = dict(enabled = True, vlan_id = str(vlan_id))
    MVLAN.set_zd_mgmt_vlan_info(zd, zdinfo)
    NSRHLP.tag_switch_vlan_interface(nsr, vlan_id, sw_interface)
    time.sleep(2)
    zd_mgmt_vlan = MVLAN.get_zd_mgmt_vlan_info(zd)
    
    return zd_mgmt_vlan


def untag_zd_mgmt_vlan(zd, nsr, sw_interface, vlan_id = 301):
    zdinfo = dict(enabled = False)
    MVLAN.set_zd_mgmt_vlan_info(zd, zdinfo)
    NSRHLP.untag_switch_vlan_interface(nsr, vlan_id, sw_interface)
    time.sleep(2)
    zd_mgmt_vlan = MVLAN.get_zd_mgmt_vlan_info(zd)
    
    return zd_mgmt_vlan


def is_switch_interface_tag_vlan(nsr, interface, vlan_id):
    data = nsr.perform('show running interface %s' % interface)
    if re.search(r"^\s*vlan\s+tagging\s+%s" % str(vlan_id), data, re.M | re.I):
        return True
    
    return False


def untag_ap_mgmt_vlan(zd):
    appolicy = { 'mgmt_vlan': { 'enabled': False,
                                'disabled': True,
                                'keep': False } }
    MVLAN.set_ap_mgmt_vlan_info(zd, appolicy)
    time.sleep(2)
    ap_mgmt_vlan = MVLAN.get_ap_mgmt_vlan_info(zd)
    
    return ap_mgmt_vlan


# caller should call zd.get_all_ap_info() to validate all APs are joined with the new vlan subnet
def tag_ap_mgmt_vlan(zd, vlan_id = 302, prim_ip = None, sec_ip = None):
    appolicy = { 'zd_discovery': {},
                 'mgmt_vlan': { 'enabled': True,
                                'disabled': False,
                                'keep': False,
                                'vlan_id': vlan_id} }
    if prim_ip:
        appolicy['zd_discovery']['enabled'] = True
        appolicy['zd_discovery']['prim_ip'] = prim_ip
        if sec_ip:
            appolicy['zd_discovery']['sec_ip'] = sec_ip
    
    MVLAN.set_ap_mgmt_vlan_info(zd, appolicy)
    time.sleep(2)
    ap_mgmt_vlan = MVLAN.get_ap_mgmt_vlan_info(zd)
    
    return ap_mgmt_vlan


