import logging
from RuckusAutoTest.common.Ratutils import ping

locs = dict(
    ip_manual_selection = r"//input[@id='manual']",
    ip_dhcp_selection = r"//input[@id='dhcp']",
    
    ip_addr_textbox = r"//input[@id='ip']",
    netmask_textbox = r"//input[@id='netmask']",
    gateway_textbox = r"//input[@id='gateway']",
    pri_dns_textbox = r"//input[@id='dns1']",
    sec_dns_textbox = r"//input[@id='dns2']",
    
    access_vlan_textbox = r"//input[@id='mgmt-vlan']",
    
    apply_ip_setting = r"//input[@id='apply-mgmt-ip']",
)


def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    

def set_zd_ip_setting(zd,ipconfig):
    '''
    ipconfig = {
                    'type':'manual'/'dhcp',
                    'ip_addr':'',
                    'net_mask':'',
                    'gateway':'',
                    'pri_dns':'',
                    'sec_dns':'',
                    'access_vlan':''
                }
    '''
    s=zd.s
    nav_to(zd)
#    import pdb
#    pdb.set_trace()
    if ipconfig['type']=='dhcp':
        s.click(locs['ip_dhcp_selection'])
    else:
        s.click(locs['ip_manual_selection'])
        ip = ipconfig.get('ip_addr')
        if ip:
            s.type_text(locs['ip_addr_textbox'],ip)
            
        net_mask = ipconfig.get('net_mask')
        if net_mask:
            s.type_text(locs['netmask_textbox'],net_mask)
            
        gateway = ipconfig.get('gateway')
        if gateway:
            s.type_text(locs['gateway_textbox'],gateway)
            
        pri_dns = ipconfig.get('pri_dns')
        if pri_dns:
            s.type_text(locs['pri_dns_textbox'],pri_dns)
            
        sec_dns = ipconfig.get('sec_dns')
        if sec_dns:
            s.type_text(locs['sec_dns_textbox'],sec_dns)
    
    access_vlan = ipconfig.get('access_vlan')
    if access_vlan:
        s.type_text(locs['access_vlan_textbox'],access_vlan)
    
    s.click_and_wait(locs['apply_ip_setting'])
    
    if zd.s.is_confirmation_present():
        cfm = zd.s.get_confirmation()
        if cfm:
            logging.info ('confirmation get %s'%cfm)
        
    if zd.s.is_alert_present():
        alert = zd.s.get_alert()
        if alert:
            logging.info ('alert get %s'%alert)
         
    