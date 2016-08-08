'''
    Testbed for ATA/Veriwave and ZD testing.
        +ATA is an interface to control Veriwave
            -create clients/create clients group with different encryption types and aaa servers.
            -create servers to test traffic downlink and uplink testing.
            -create flow/start flow/stop flow etc
            -destroy clients/destroy clients group
            -purge ports etc.
        +stations is kind of real one, ATA will create virtual clients.
    
    This testbed is similar with testbed ZD_Stations.py, but we consider ATA/Veriwave will become components for multiple clients testing, 
    so extend from ZD_ATA_Stations.py
              
Created on Oct 16, 2013
@author: cwang@ruckuswireless.com
'''
import logging

from ZD_Stations import ZD_Stations
from RuckusAutoTest.components import AtaWrapper
from RuckusAutoTest.common import lib_Constant
from RuckusAutoTest.components.lib.zdcli import configure_ap as APSetter

class ZD_ATA_Stations(ZD_Stations):
    def __init__(self, testbedinfo, config):               
        ZD_Stations.__init__(self, testbedinfo, config)
        # Initialize the ATA server component
        if config.has_key('ATA') and config['ATA'] is not None:            
            self.components['ATA'] = AtaWrapper.AtaWrapper(
                ip_addr = config['ATA']['ata_IP'],
                username = config['ATA'].get('user','qaauto'))
            
            self.ata_IP = config['ATA']['ata_IP']
            self.veriwave_IP = config['ATA']['veriwave_IP']
            self.wifi_01  = config['ATA']['wifi_01']
            self.wifi_blade_01 = config['ATA']['wifi_blade_01']
            self.wifi_port_01 = config['ATA']['wifi_port_01']
            self.enet_01 = config['ATA']['enet_01']
            self.enet_blade_01 = config['ATA']['enet_blade_01']
            self.enet_port_01 = config['ATA']['enet_port_01']
            self.fiveg_channel = config['ATA']['fiveg_channel']
            self.twog_channel = config['ATA']['twog_channel']
            self.components['ATA'].remove_ports()
            logging.info('Bind VM Ethernet Port.')
            self.components['ATA'].bind_vw_port(port_name = self.enet_01, 
                                                ip_addr = self.veriwave_IP, 
                                                slot = AtaWrapper.enet_blade_01, 
                                                port = AtaWrapper.enet_port_01)
            self.update_ap_channel()
        else:
            self.components['ATA'] = None
            logging.warning('No about ATA configuration.')
            raise Exception("No about ATA configuration.")
        
    
    def update_ap_channel(self):
        logging.info('Update ap channel so that Veriwave can detect.')
        apdict = self.get_aps_sym_dict()
        cfgs = []
        for aptag, dd in apdict.items():
            model = dd['model']
            mac = dd['mac']
            cfg = {'mac_addr': '%s' % mac}
            if lib_Constant.is_ap_support_11n(model):
                cfg.update({'radio_na': {'channel': '36',                                
                                         'wlangroups': 'Default'}})
            
            if lib_Constant.is_ap_support_11g(model):
                cfg.update({'radio_bg': {'channel': '11',                                
                                         'wlangroups': 'Default'}})
            
            cfgs.append(cfg)
        
        APSetter.configure_aps(self.zd_cli, cfgs)
        logging.info('Update ap Channel DONE.')
        

