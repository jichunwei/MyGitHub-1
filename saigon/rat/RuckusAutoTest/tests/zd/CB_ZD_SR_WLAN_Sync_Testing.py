'''
Description:
Created on 2010-7-2
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.common.Ratutils import make_random_string
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8


class CB_ZD_SR_WLAN_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_wlan_setting_sync()
        if self.errmsg:
            return ("FAIL", self.errmsg)
        self.passmsg = "Add/Edit/Del WLAN service/setting can work correctly."
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(check_wlan_timeout=10)
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _test_wlan_setting_sync(self):
        open_wlan_cfg = {'ssid': 'rat-open-none',
                         'description': 'EnjoyPythonscripting_Open',
                         'auth': 'open',
                         'wpa_ver': '',
                         'encryption': 'none',
                         'sta_auth': 'open',
                         'sta_encryption': 'none',
                         'sta_wpa_ver': '',
                         'key_index': '',
                         'key_string': '',          
                         }
        if self.conf.has_key('wlan_cfg'):
            open_wlan_cfg.update(self.conf['wlan_cfg'])

        self._cfg_create_wlan_on_zd(open_wlan_cfg)
        if self.errmsg:            
            return False
        
        edit_wlan_cfg = {'ssid': open_wlan_cfg['ssid'], #'rat-open-none',
                                'description': 'EnjoyPythonscripting_OpWep64',
                                'auth': 'open',
                                'encryption': 'WEP-64',
                                'wpa_ver': '',
                                #'key_index': '1', 'key_string': 'f12a982cb1dec862b6795b1ac3',
                                'key_index': "1", 
                                'key_string': make_random_string(10, "hex"),
                                'sta_auth': 'open',
                                'sta_encryption': 'WEP-64',
                                'sta_wpa_ver': '',
                               }
        self._cfg_edit_wlan_on_zd(edit_wlan_cfg)
        
        if self.errmsg:            
            return False
        
        self._delete_all_wlan_on_zd()
        
    
    def _cfg_create_wlan_on_zd(self, wlan_cfg):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.active_zd, wlan_cfg)
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")
        if self.errmsg:
            return False
        
        if not self._verify_wlan_name():
            return False
        
        logging.info('Create WLAN [%s] has been synchronized to standby successfully' % wlan_cfg['ssid'])
        return True
        
        
    def _cfg_edit_wlan_on_zd(self, wlan_cfg):
        logging.info("Edit WLAN [%s] with new setting on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.edit_wlan(self.active_zd, wlan_cfg['ssid'], wlan_cfg)
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")
        if self.errmsg:
            return False
        self._verify_wlan_cfg()
    
    def _delete_all_wlan_on_zd(self):
        self.active_zd.remove_all_wlan()
        self._verify_wlan_name()
        if self.errmsg:
            return False
        
        self.passmsg = "WLAN information has synchronized to standby zd after remove all wlan"
        logging.info(self.passmsg)
    
    
    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
            
    
    def _verify_wlan_name(self):
        active_wlan_list = lib.zd.wlan.get_wlan_list(self.active_zd)
        self._refresh_standby_zd()
        standby_wlan_list = lib.zd.wlan.get_wlan_list(self.standby_zd)
        for wlan_name in active_wlan_list:
            if not standby_wlan_list.__contains__(wlan_name):
                self.errmsg = 'WLAN [%s] has not been synchronized to standby zd' % wlan_name
                logging.warning(self.errmsg)
                return False
        
        return True
    
    
    def _verify_wlan_cfg(self):
        active_wlan_cfg_list = lib.zd.wlan.get_wlan_cfg_list(self.active_zd)
        self._refresh_standby_zd()
        standby_wlan_cfg_list = lib.zd.wlan.get_wlan_cfg_list(self.standby_zd)
        for active_wlan in active_wlan_cfg_list:
            standby_wlan = self._find_wlan_cfg(active_wlan['name'], standby_wlan_cfg_list)
            if standby_wlan:
                for key, value in standby_wlan.items():
                    if active_wlan[key] != value:
                        self.errmsg = 'WLAN [%s] configurations are different between active and standby, key=%s'  % \
                        (active_wlan['names_essids'], key)
                        logging.warning(self.errmsg)
                        return False
                    
        self.passmsg = 'WLAN configurations have synchronized successfully'
        logging.info(self.passmsg)
        return True
    
        
    def _find_wlan_cfg(self, ssid_name, wlan_list):
        for wlan in wlan_list:
            if ssid_name == wlan['name']:
                return wlan
        return None