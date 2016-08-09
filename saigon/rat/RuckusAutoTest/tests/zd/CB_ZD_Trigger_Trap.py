'''
Description:

Trigger Traps by:
1. Create an opennone wlan: openwlan
2. Change the ssid of wlan (ruckusZDEventAPSSIDChangedTrap)
3. Client associates with wlan (ruckusZDEventClientJoin)
4. Client disconnects from wlan (ruckusZDEventClientDisconnect)
5. Delete An AP (ruckusZDEventAPJoinTrap, ruckusZDEventAPSystemWarmStartTrap, ruckusZDEventAPAvailableStatusTrap)
6. Reboot another AP (ruckusZDEventAPLostHeartbeatTrap)

        
Create on 2012-8-30
@author: zoe.huang@ruckuswireless.com
'''

import logging
import copy
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig 
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Trigger_Trap(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'station': 'station ip addr and tag',
                              'wlan_cfg': 'wlan to be created',
                              'new_ssid': 'the new ssid to be changed for wlan_cfg'}
    
    def _init_params(self, conf):
        self.conf = dict(check_status_timeout = 90,
                         check_wlan_timeout = 3,
                         pause = 2.0,
                         break_time = 10,
                         restart_cnt = 6
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        station_info = self.conf['station']
        self.sta_tag = station_info['sta_tag']
        self.sta_ip_addr = station_info['sta_ip_addr']
        self.wlan_info = self.conf['wlan_cfg']
        self.new_wlan = copy.deepcopy(self.wlan_info)
        self.new_wlan['ssid'] = self.conf['new_ssid']
        self.errmsg = ''
        self.deleted_ap = ''
        self.reboot_ap = ''
        self.client_mac_addr = ''
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        self.carrierbag['deleted_ap_mac_addr'] = self.deleted_ap
        self.carrierbag['reboot_ap_mac_addr'] = self.reboot_ap
        self.carrierbag['client_mac_addr'] = self.client_mac_addr
        self.carrierbag['modified_wlan_ssid'] = self.new_wlan['ssid']
     
    def config(self, conf):
        self._init_params(conf)
        self._cfgGetTargetStation()
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._retrieve_carribag()
        
    
    def test(self):
        try:
            self._cfgCreateWlanOnZD(self.wlan_info)
            time.sleep(self.conf['break_time'])            
            self._cfgEditWlanOnZD(self.wlan_info['ssid'],self.new_wlan) 
            self._test_assoc_station_with_ssid()           
            self._test_station_info()
            time.sleep(self.conf['break_time'])                   
            self._testRemoveWlanFromStation()
            self._delete_client_by_mac_addr()
                       
            ap_mac_list = self.testbed.get_aps_sym_dict_as_mac_addr_list()
            ap_mac_addr = ap_mac_list[0]
            
            logging.info('Delete AP[%s] from ZD' % ap_mac_addr)
            self.zd.remove_approval_ap(ap_mac_addr)
            self.deleted_ap = ap_mac_addr
            
            ap_mac_addr = ap_mac_list[1]
            logging.info('Reboot AP[%s]' % ap_mac_addr)
            ap = tconfig.get_active_ap(ap_mac_addr, self.testbed.components['AP']) 
            ap.reboot()
            self.reboot_ap = ap_mac_addr
                  
        except Exception, ex:
            self.errmsg += ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:  
            return self.returnResult('PASS', 'All trigger trap steps have been done successfully.')  
    
    def cleanup(self):
        self._update_carribag()
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._testRemoveWlanFromStation()
    
    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.sta_ip_addr
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.sta_ip_addr)
        
    def _cfgRemoveZDWlanGroupsAndWlan(self):       
#        logging.info("Remove all Wlan Groups on the Zone Director.")
#        lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        logging.info("Remove all WLAN on the Zone Director.")
        lib.zd.wlan.delete_all_wlans(self.zd)
        
    def _cfgEditWlanOnZD(self, ssid, wlan_cfg):
        logging.info("Edit WLAN [%s] with new setting on the Zone Director" % ssid)
        lib.zd.wlan.edit_wlan(self.zd, ssid, wlan_cfg)
        tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _cfgCreateWlanOnZD(self, wlan_cfg):
        logging.info("Create WLAN [%s] on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, wlan_cfg)
        tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")
        
    def _test_assoc_station_with_ssid(self):
        
        logging.info("Client associates with WLAN[%s]" % self.new_wlan['ssid'])
        res = tmethod.assoc_station_with_ssid(self.target_station, self.new_wlan, self.conf['check_status_timeout'],self.conf['break_time'], self.conf['restart_cnt'],)
        if  res:
            self.errmsg += tmethod.verify_wlan_in_the_air(self.target_station, self.new_wlan['ssid'])
            
    def _test_station_info(self):
        
        logging.info("Get wifi addr and wifi mac addr of station")
        res, var1, var2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if res:
            self.client_mac_addr = var2.lower()
        else:           
            self.errmsg += var2

    def _testRemoveWlanFromStation(self):
        try:
            logging.info("Remove all wlans from the stations")
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout=self.conf['check_status_timeout'])
        except Exception, e:
            self.errmsg += '[Removing wlan from target station failed] %s' % e.message
    
    def _delete_client_by_mac_addr(self):        
        logging.info("Delete client[%s] on ZD" % self.client_mac_addr)
        try:
            self.zd.delete_clients(self.client_mac_addr)
        except Exception, e:
            self.errmsg += e.message