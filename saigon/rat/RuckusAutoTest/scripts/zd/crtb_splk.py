import time
from pprint import pprint, pformat
import logging

#from RuckusAutoTest.components.lib.zd import mgmt_vlan_te as TE
from RuckusAutoTest.components.lib.zd import system_zd as SYS
from RuckusAutoTest.components import NetgearSwitchRouter as NSR
from RuckusAutoTest.common.SeleniumControl import SeleniumManager
import RuckusAutoTest.common.lib_Debug as bugme
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import RuckusAP
from RuckusAutoTest.tests.zd.libZD_TestMethods_v8 import pause_test_for

INTF_AP = ['1/0/%d' %p for p in range(1,7)]
INTF_ZD = ['1/0/25']
INTF_AP_ZD = INTF_AP + INTF_ZD
VOICE_VID = '55'
MGMT_VID = '301'
DATA_VID = '66'
ZD_IP1 = '192.168.0.2'
IP1_GW = '192.168.0.253'
ZD_IP2 = '192.168.31.2'
IP2_GW =  '192.168.31.253'

def create_zonedirector(**zdcfg):
    cfg = {'browser_type':'firefox', 'ip_addr':'192.168.0.2', 'username':'admin', 'password':'admin'}
    cfg.update(zdcfg)
    zd = ZoneDirector.ZoneDirector(cfg)
    zd.start()
    return zd

def create_netgear_switch_router(**swcfg):
    cfg = {'enable_password': '',
           'ip_addr': '192.168.0.253',
           'password': '',
           'username': 'admin'}
    cfg.update(swcfg)
    ngsw = NSR.NetgearSwitchRouter(cfg)
    return ngsw

def get_ap_status(zd):
    apstatus = {}
    for apinfo in zd.getAllAPsInfo():
        mac = apinfo.pop('mac')
        apstatus[mac] = apinfo
    logging.info("ZD Currently Managed APs Status:\n%s" % (pformat(apstatus, indent=4)))
    return apstatus

def waitfor_ap_associated(zd, apstatus_0, **kwargs):
    cfg = dict(timeout=600, pause=15)
    end_time = time.time() + int(cfg['timeout'])
    pause = int(cfg['pause'])
    while time.time() < end_time:
        aps1 = get_ap_status(zd)
        cnd = len(apstatus_0)
        for mac in apstatus_0.keys():
            if aps1.has_key(mac):
                apstatus_1 = aps1[mac]
                if apstatus_1['status'].startswith('Connected'):
                    cnd -= 1
        if cnd < 1:
            return True
        time.sleep(pause)
    return False

def recover_testbed(**kwargs):
    mycfg = dict(debug=False, wait4assoc=True, timeout=600)
    zdcfg = dict(ip_addr='192.168.0.2', x_loadtime=0, username='admin', password='admin')
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        elif zdcfg.has_key(k):
            zdcfg[k] = v
    #if mycfg['debug']: bugme.pdb.set_trace()
    zd = create_zonedirector(**zdcfg)
    ng2 = create_netgear_switch_router(**dict(ip_addr='192.168.0.253'))
    mycfg['ap.status.0'] = get_ap_status(zd)
    # all APs set factory 
    ap_info_list = mycfg['ap.status.0'].values()
    for ap_info in ap_info_list:
        ap = RuckusAP.RuckusAP(dict(ip_addr=ap_info['ip_addr'],
                                    username='admin',
                                    password='admin'))
        ap_intf=ng2.mac_to_interface(ap.get_base_mac())
        ap.set_factory(login=False)
        ng2.disable_interface(ap_intf)
        #ap.reboot(login=False)
    # disable switch ports which connect to APs    
    #for intf in INTF_AP:
    #    ng2.disable_interface(intf)        
    if zdcfg['ip_addr'] != ZD_IP1:
        SYS.change_zd_ipaddr(zd, dict(ip_addr=ZD_IP1, gateway=IP1_GW))
    for intf in INTF_AP_ZD:
        ng2.remove_interface_vlan(intf)
        ng2.change_interface_pvid(intf, VOICE_VID)
    # enable switch ports which connect to APs    
    for intf in INTF_AP:
        ng2.add_interface_tag_vlan(intf, DATA_VID)
        ng2.enable_interface(intf)
    ng2.clear_mac_table()
    if zdcfg['ip_addr'] != ZD_IP1:
        del(zd)
        time.sleep(15)
        zd = create_zonedirector(**dict(ip_addr=ZD_IP1,gateway=IP1_GW))
        zd.restart_aps()
    if mycfg['wait4assoc'] and mycfg.has_key('ap.status.0'):
        tm_0 = time.time()
        time.sleep(10)
        if not waitfor_ap_associated(zd, mycfg['ap.status.0'], timeout=mycfg['timeout']):
            raise Exception('AP disconnected after change topology')
    if zd:
        zd.selenium_mgr.shutdown()
    tm_x = int(time.time() - tm_0)
    return mycfg

def create_L2_without_vlan(**kwargs):
    mycfg = dict(debug=False, wait4assoc=True, timeout=600)
    zdcfg = dict(ip_addr='192.168.0.2', x_loadtime=0, username='admin', password='admin')
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        elif zdcfg.has_key(k):
            zdcfg[k] = v
    #if mycfg['debug']: bugme.pdb.set_trace()
    zd = create_zonedirector(**dict(ip_addr=zdcfg['ip_addr']))
    ng2 = create_netgear_switch_router(**dict(ip_addr='192.168.0.253'))
    mycfg['ap.status.0'] = get_ap_status(zd)
    ap_info_list = mycfg['ap.status.0'].values()
    for ap_info in ap_info_list:
        ap = RuckusAP.RuckusAP(dict(ip_addr=ap_info['ip_addr'],
                                    username='admin',
                                    password='admin'))
        ap_intf=ng2.mac_to_interface(ap.get_base_mac())
        ap.set_factory(login=False)
        ng2.disable_interface(ap_intf)
        #ap.reboot(login=False)
    # disable switch ports which connect to APs    
    #for intf in INTF_AP:
    #    ng2.disable_interface(intf)      
    if zdcfg['ip_addr'] != ZD_IP1:
        SYS.change_zd_ipaddr(zd, dict(ip_addr=ZD_IP1, gateway=IP1_GW))
        del(zd)
    for intf in INTF_AP_ZD:
        ng2.remove_interface_vlan(intf)
        ng2.change_interface_pvid(intf, VOICE_VID)
    # enable switch ports which connect to APs    
    for intf in INTF_AP:
        ng2.add_interface_tag_vlan(intf, DATA_VID)
        ng2.enable_interface(intf)
    if zdcfg['ip_addr'] != ZD_IP1:
        time.sleep(15)
        zd = create_zonedirector(**dict(ip_addr=ZD_IP1))
    else:
        # waitfor ZD update ap infomation on WebUI
        pause_test_for(30, "waitfor ZD update ap infomation on WebUI")

    if mycfg['wait4assoc'] and mycfg.has_key('ap.status.0'):
        tm_0 = time.time()
        time.sleep(10)
        if not waitfor_ap_associated(zd, mycfg['ap.status.0'], timeout=mycfg['timeout']):
            raise Exception('AP disconnected after change topology')
    if zd:
        zd.selenium_mgr.shutdown()
    tm_x = int(time.time() - tm_0)
    return mycfg

# ZD and AP move to 31 subnet    
def create_L2_with_vlan(**kwargs):
    mycfg = dict(debug=False, wait4assoc=True, timeout=600)
    zdcfg = dict(ip_addr='192.168.0.2', x_loadtime=0, username='admin', password='admin')
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        elif zdcfg.has_key(k):
            zdcfg[k] = v
    #if mycfg['debug']: bugme.pdb.set_trace()
    
    zd = create_zonedirector(**dict(ip_addr=zdcfg['ip_addr']))
    ng2 = create_netgear_switch_router(**dict(ip_addr='192.168.0.253'))
    
    mycfg['ap.status.0'] = get_ap_status(zd)        
    ap_info_list = mycfg['ap.status.0'].values()
    for ap_info in ap_info_list:
        ap = RuckusAP.RuckusAP(dict(ip_addr=ap_info['ip_addr'],
                                    username='admin',
                                    password='admin'))
        ap_intf=ng2.mac_to_interface(ap.get_base_mac())
        ap.set_factory(login=False)
        ng2.disable_interface(ap_intf)
        #ap.reboot(login=False)
    # disable switch ports which connect to APs    
    #for intf in INTF_AP:
    #    ng2.disable_interface(intf)
        
    if zdcfg['ip_addr'] != ZD_IP2:
        SYS.change_zd_ipaddr(zd, dict(ip_addr=ZD_IP2, gateway=IP2_GW))
        del(zd)
        
    for intf in INTF_AP_ZD:
        ng2.remove_interface_vlan(intf)
        ng2.change_interface_pvid(intf, MGMT_VID)
        ng2.add_interface_tag_vlan(intf, VOICE_VID)
    # enable switch ports which connect to APs    
    for intf in INTF_AP:
        ng2.add_interface_tag_vlan(intf, DATA_VID)
        ng2.enable_interface(intf)
    ng2.clear_mac_table()        
    if zdcfg['ip_addr'] != ZD_IP2:
        time.sleep(15)
        zd = create_zonedirector(**dict(ip_addr=ZD_IP2))
    else:
        # waitfor ZD update ap infomation on WebUI
        pause_test_for(30, "waitfor ZD update ap infomation on WebUI")
        
    if mycfg['wait4assoc'] and mycfg.has_key('ap.status.0'):
        tm_0 = time.time()
        time.sleep(10)
        if not waitfor_ap_associated(zd, mycfg['ap.status.0'], timeout=mycfg['timeout']):
            raise Exception('AP disconnected after change topology')
    if zd:
        zd.selenium_mgr.shutdown()
    tm_x = int(time.time() - tm_0)
    return mycfg
# AP move to 31 subnet   
def create_L3_tunnel_without_vlan(**kwargs):
    mycfg = dict(debug=False, wait4assoc=True, timeout=600)
    zdcfg = dict(ip_addr='192.168.0.2', x_loadtime=0, username='admin', password='admin')
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        elif zdcfg.has_key(k):
            zdcfg[k] = v
    #if mycfg['debug']: bugme.pdb.set_trace()
    
    zd = create_zonedirector(**dict(ip_addr=zdcfg['ip_addr']))
    ng2 = create_netgear_switch_router(**dict(ip_addr='192.168.0.253'))
    
    mycfg['ap.status.0'] = get_ap_status(zd)
    ap_info_list = mycfg['ap.status.0'].values()
    for ap_info in ap_info_list:
        ap = RuckusAP.RuckusAP(dict(ip_addr=ap_info['ip_addr'],
                                    username='admin',
                                    password='admin'))
        #ap.set_factory(login=False)
        ap_intf=ng2.mac_to_interface(ap.get_base_mac())
        ap.set_director_info(ip1=ZD_IP1)
        ap.reboot(login=False)
        ng2.disable_interface(ap_intf)
    # disable switch ports which connect to APs    
    #for intf in INTF_AP:
        #ng2.disable_interface(intf)
        
    if zdcfg['ip_addr'] != ZD_IP1:
        SYS.change_zd_ipaddr(zd, dict(ip_addr=ZD_IP1, gateway=IP1_GW))  
        
    for intf in INTF_AP_ZD:
        ng2.remove_interface_vlan(intf)
        ng2.change_interface_pvid(intf, VOICE_VID)
    for intf in INTF_AP:
        ng2.change_interface_pvid(intf, MGMT_VID)
        
    # enable switch ports which connect to APs    
    for intf in INTF_AP:
        ng2.add_interface_tag_vlan(intf, DATA_VID)
        ng2.enable_interface(intf)
    ng2.clear_mac_table()
    if zdcfg['ip_addr'] != ZD_IP1: 
        time.sleep(15)
        zd = create_zonedirector(**dict(ip_addr=ZD_IP1))
    else:
        # waitfor ZD update ap infomation on WebUI
        pause_test_for(30, "waitfor ZD update ap infomation on WebUI")      
    if mycfg['wait4assoc'] and mycfg.has_key('ap.status.0'):
        tm_0 = time.time()
        time.sleep(10)
        if not waitfor_ap_associated(zd, mycfg['ap.status.0'], timeout=mycfg['timeout']):
            raise Exception('AP disconnected after change topology')
    if zd:
        zd.selenium_mgr.shutdown()
    tm_x = int(time.time() - tm_0)
    return mycfg

# ZD move 31 subnet
def create_L3_tunnel_with_vlan(**kwargs):
    mycfg = dict(debug=False, wait4assoc=True, timeout=600)
    zdcfg = dict(ip_addr='192.168.0.2', x_loadtime=0, username='admin', password='admin')
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
        elif zdcfg.has_key(k):
            zdcfg[k] = v
    #if mycfg['debug']: bugme.pdb.set_trace()
    zd = create_zonedirector(**dict(ip_addr=zdcfg['ip_addr']))
    ng2 = create_netgear_switch_router(**dict(ip_addr='192.168.0.253'))
    
    mycfg['ap.status.0'] = get_ap_status(zd)
    ap_info_list = mycfg['ap.status.0'].values()
    for ap_info in ap_info_list:
        ap = RuckusAP.RuckusAP(dict(ip_addr=ap_info['ip_addr'],
                                    username='admin',
                                    password='admin'))
        ap_intf=ng2.mac_to_interface(ap.get_base_mac())
        ap.set_director_info(ip1=ZD_IP2)
        ap.reboot(login=False)
        ng2.disable_interface(ap_intf)
    # disable switch ports which connect to APs    
    #for intf in INTF_AP:
    #    ng2.disable_interface(intf)
        
    if zdcfg['ip_addr'] != ZD_IP2:
        SYS.change_zd_ipaddr(zd, dict(ip_addr=ZD_IP2, gateway=IP2_GW))
        del(zd)
    for intf in INTF_AP_ZD:
        ng2.remove_interface_vlan(intf)
        ng2.change_interface_pvid(intf, VOICE_VID)
    for intf in INTF_ZD:
        ng2.change_interface_pvid(intf, MGMT_VID)
        ng2.add_interface_tag_vlan(intf, VOICE_VID)
    # enable switch ports which connect to APs    
    for intf in INTF_AP:
        ng2.add_interface_tag_vlan(intf, DATA_VID)
        ng2.enable_interface(intf)
    ng2.clear_mac_table()
    if zdcfg['ip_addr'] != ZD_IP2: 
        time.sleep(15)
        zd = create_zonedirector(**dict(ip_addr=ZD_IP2))
    else:
        # waitfor ZD update ap infomation on WebUI
        pause_test_for(30, "waitfor ZD update ap infomation on WebUI")
    if mycfg['wait4assoc'] and mycfg.has_key('ap.status.0'):
        tm_0 = time.time()
        time.sleep(10)
        if not waitfor_ap_associated(zd, mycfg['ap.status.0'], timeout=mycfg['timeout']):
            raise Exception('AP disconnected after change topology')
    if zd:
        zd.selenium_mgr.shutdown()
    tm_x = int(time.time() - tm_0)
    return mycfg

def create_splk_tb_usage():
    print """
    Change Topology on Spectralink Test Bed.
    tea.py voice.crtb_splk type=<topology naem> ip_addr=<ZD ip address> debug=<True,False>

    Where <args> are keyword=[value] pair:
       Keyword    What is represent
       -------    --------------------------------------
       type       L2WithoutVlan
                  L2WithVlan
                  L2TunnelWithoutVlan
                  L2TunnelWithVlan
                  L3TunnelWithoutVlan
                  L3TunnelWithVlan
       ip_addr    ip address of Zone Director in test bed currently
       debug      True, go to debug mode

     Examples:
     tea.py voice.crtb_splk type=L2WithoutVlan debug=Ture
     tea.py voice.crtb_splk type=L3TunnelWithVlan
     tea.py voice.crtb_splk type=recover_testbed ip_addr=192.168.31.2
     """
        
def main(**kwargs):
    if len(kwargs) < 1:
        create_splk_tb_usage()
        exit(1)
    if kwargs.has_key('zd_ip_addr'):
        kwargs['ip_addr'] = kwargs['zd_ip_addr']
        kwargs.pop('zd_ip_addr')
    tb_cfg = dict(type='L2WithoutVlan', debug=False)
    tb_cfg.update(kwargs)
    if tb_cfg['debug']: bugme.pdb.set_trace()
    if tb_cfg['type'] in ['L2WithVlan', 'L2TunnelWithVlan']:
        create_L2_with_vlan(**tb_cfg)
    if tb_cfg['type'] in ['L2WithoutVlan', 'L2TunnelWithoutVlan']:
        create_L2_without_vlan(**tb_cfg)
    if tb_cfg['type'] == 'L3TunnelWithVlan':
        create_L3_tunnel_with_vlan(**tb_cfg)
    if tb_cfg['type'] == 'L3TunnelWithoutVlan':
        create_L3_tunnel_without_vlan(**tb_cfg)
    if tb_cfg['type'] == 'recoverTestbed':
        recover_testbed(**tb_cfg)

