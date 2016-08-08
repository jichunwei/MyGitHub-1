'''
Created on Oct 18, 2013

@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test

from contrib.wlandemo import defaultWlanConfigParams as WlanParam
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups as WgSetter
from RuckusAutoTest.components.lib.zdcli import set_wlan as WlanSetter
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as WlanGetter
from RuckusAutoTest.components.lib.zdcli import configure_ap as APSetter
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as Server

class CB_ATA_Test_Sta_Encryption_Types(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlan_group_cfg_list = [])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.zdcli = self.testbed.components['ZoneDirector']
        self.wlans = WlanParam.get_cfg_list()
        self.mac_addr_list = self.testbed.get_aps_mac_list()
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self.clean_wlans()
    
    def test(self):
        pass
    
    def cleanup(self):
        self._update_carribag()     
      
    
    def create_clients(self, ssid):
        self.ata.
    
    def create_wlans(self):        
        WlanSetter.create_multi_wlans(self.zdcli, self.wlans)
        logging.info('Create WLANs DONE.')
    
    def clean_wlans(self):        
        APSetter.default_ap_group_by_mac_addr(self.zdcli, self.mac_addr_list)
        WgSetter.remove_all_wlan_groups(self.zdcli)
        WlanSetter.remove_all_wlans(self.zdcli)
        Server.delete_all_servers(self.zdcli)
        logging.info('Clean WLAN DONE.')
        