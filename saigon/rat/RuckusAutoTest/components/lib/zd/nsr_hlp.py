from string import Template

TMPL_TAG_RAT_INTF_t = """
interface $interface
    vlan participation include $vlan_id
    vlan tagging $vlan_id
exit
"""
def tag_switch_vlan_interface(nsr, vlan_id, interface):
    cfg_block = Template(TMPL_TAG_RAT_INTF_t).substitute({'interface':str(interface), 'vlan_id':str(vlan_id)})
    nsr.do_cfg(cfg_block)
    return nsr.perform('show running interface %s' % interface)

TMPL_NOTAG_RAT_INTF_t = """
interface $interface
    no vlan tagging $vlan_id
    vlan participation include $vlan_id
exit
"""
def untag_switch_vlan_interface(nsr, vlan_id, interface):
    cfg_block = Template(TMPL_NOTAG_RAT_INTF_t).substitute({'interface':str(interface), 'vlan_id':str(vlan_id)})
    nsr.do_cfg(cfg_block)
    return nsr.perform('show running interface %s' % interface)

