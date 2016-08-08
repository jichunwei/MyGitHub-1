'''
Created on Jan 24, 2014

@author: jacky luh
'''
import time
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging_lib
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_Guest_Wlan_and_Wlangroup(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'wlan_cfg': '',
                       'wg_cfg': '',
                       'ap_cfg': ''
                       }
    
    def config(self, conf):
        self._init_test_parameters(conf)
        self._retrieve_carrier_bag()


    def test(self):
        #create the local user
        self._create_wlan()
        time.sleep(2)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self._create_wlan_group()
        time.sleep(2)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self._assign_wg_to_active_ap()
        time.sleep(2)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = "The guest wlan, wlangroup, and the active ap was configured successfully"
        return self.returnResult('PASS', self.passmsg)

        
    def cleanup(self):
        pass


    def _init_test_parameters(self, conf):
        self.wlan_conf = {}
        self.wg_conf = {}
        self.active_ap = ''

        if conf.has_key('wlan_cfg'):
            self.wlan_conf = conf['wlan_cfg']
        if conf.has_key('wg_cfg'):
            self.wg_conf = conf['wg_cfg']
        if conf.has_key('ap_cfg'):
            self.ap_cfg = conf['ap_cfg']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
    
    def _create_wlan(self):
        logging.info('Create the guest wlan')
        lib.zdcli.set_wlan.create_wlan(self.zdcli, self.wlan_conf)
        
        
    def _create_wlan_group(self):
        logging.info('Remove all wlan members from the default wlan group')
        lib.zdcli.wgs.remove_all_wlan_members_from_wlan_group(self.zdcli, 'Default')
        logging.info('Create the guest wlan group')
        lib.zdcli.wgs._configure_wlan_group(self.zdcli, self.wg_conf)
        
        
    def _assign_wg_to_active_ap(self):
        self.ap_cfg.update({'mac_addr': self.a_ap_obj.base_mac_addr})
        logging.info('Assign the wlan group to the active ap')
        lib.zdcli.configure_ap.configure_ap(self.zdcli, self.ap_cfg)
        
        
    def _retrieve_carrier_bag(self):
        self.a_ap_obj = self.carrierbag.get('ap')
    
