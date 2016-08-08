# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)
    
"""
import logging
import time
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from contrib.wlandemo import defaultWlanConfigParams as wlancfg
from u.zd.scaling.lib import scaling_zd_lib as lib

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP

class CB_Scaling_Verify_WLANs(Test):
    
    required_components = ["ZoneDirector"]
    parameter_description = {'target_station':'the ipaddr of station',
                             'wlans':'The wlans configuration',
                             }

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_username = self.zd.username
        self.ap_password = self.zd.password
        
        self.conf = conf
        self.wlan_group_prefix = "scaling-sanity-check"
        self.check_status_timeout = 100
        self.target_station = conf['target_station']
        self.ruckus_aps = self.carrierbag['ruckus_aps']
        
        wlans = conf['wlans']        
        self.wlan_conf_list = []
        for wlan in wlans :
            self.wlan_conf_list.append(wlancfg.get_cfg(wlan))
            
        self.passmsg = ""      
        self.errmsg = ""  
    
    def test(self):
        logging.info('Begin to retrieve APs from webui')        
        self.aps = lib.retrieve_aps(self.zd)
                
        self._sanity_check_wlans(self.wlan_group_prefix)
        if self.errmsg:
            return ("FAIL", self.errmsg)
        
        self.passmsg = 'WLANs[%s]' % self.conf['wlans']
        
        return ("PASS", self.passmsg.strip())        
    
    def cleanup(self):
        pass
        
    def _create_wlan_and_wgs(self, wlan_conf, wlan_group):
        zhlp.wlan.create_wlan(self.zd, wlan_conf)        
        zhlp.wgs.create_wlan_group(self.zd, wlan_group, wlan_conf['ssid'])        
        zhlp.wgs.uncheck_default_wlan_member(self.zd, wlan_conf['ssid'])
        
    def _bind_wlan_groups_to_ap(self, ap_mac):
        zhlp.ap.assign_all_ap_to_default_wlan_group(self.zd)
        radios = zhlp.ap.get_supported_radio(self.zd, ap_mac)
        for radio in radios:
            zhlp.ap.assign_to_wlan_groups_by_radio(self.zd, ap_mac, self.wlan_group_prefix, radio, self.wlan_group_prefix)
    
    def _assign_client_to_wlan(self, wlan_conf):
        self.target_station.remove_all_wlan()
        time.sleep(10)
        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, self.check_status_timeout)        
        if errmsg:
            self.errmsg = '[Connect failed]: %s' % errmsg
            logging.info(self.errmsg)            
            return
        
    def _go_through_aps_wlan(self, wlan_conf):
        for index in range(len(self.aps)):
            active_ap = RuckusAP(dict(ip_addr=self.aps[index]['ip_addr'], username=self.ap_username, password=self.ap_password, ))            
            msg = tmethod.verify_wlan_on_aps(active_ap, wlan_conf['ssid'])
            if not msg and msg != '':
                self.errmsg = msg
                return
            
        self.passmsg = 'all of aps can perform wlan[%s]' % wlan_conf['ssid']
        logging.info(self.passmsg)

    def _go_through_ruckus_aps_wlan(self, wlan_conf):
        for index in range(len(self.ruckus_aps)):
            ap_mac = self.ruckus_aps[index]['mac']            
            self._bind_wlan_groups_to_ap(ap_mac)
            self._verify_wlan_aps_beyond_bind_ap(ap_mac, wlan_conf)
            if self.errmsg:
                zhlp.ap.default_wlan_groups_by_mac_addr(self.zd, ap_mac)
                return self.errmsg
            
            self._assign_client_to_wlan(wlan_conf)
                
            if self.errmsg:
                zhlp.ap.default_wlan_groups_by_mac_addr(self.zd, ap_mac)
                return self.errmsg
            
            zhlp.ap.default_wlan_groups_by_mac_addr(self.zd, ap_mac)     
                    
            

    
    def _verify_wlan_aps_beyond_bind_ap(self, ap_mac, wlan_conf):
        for index in range(len(self.aps)):
            active_ap = RuckusAP(dict(ip_addr=self.aps[index]['ip_addr'], username=self.ap_username, password=self.ap_password))
            msg = tmethod.verify_wlan_on_aps(active_ap, wlan_conf['ssid'])
            if ap_mac == self.aps[index]['mac'] and msg and msg != '':
                self.errmsg = msg
                return
            
            elif ap_mac != self.aps[index]['mac'] and not msg:
                wlan_info = active_ap.get_wlan_info_dict()
                cnt = 0
                #Just [meshu, meshd] interface                              
                for (wlan_id, wlan) in wlan_info.iteritems():
                    # don't check mesh wlan
                    if wlan['name'] in ['meshu', 'meshd']:
                        continue
                    else:
                        cnt = cnt + 1
                if cnt == 0:
                    return
                                    
                self.errmsg = 'AP[%s] should not been contained' % ap_mac
                return 
                                
        self.passmsg = 'All the wlans can perform successfully'      
    
    def _sanity_check_wlans(self, wlan_group):
        self._select_client_and_check()
        
        for wlan_conf in self.wlan_conf_list:
            logging.info('[WLANsCheck]try to create WLAN[%s], WLANGroup[%s]' % (wlan_conf, wlan_group))
            self._create_wlan_and_wgs(wlan_conf, wlan_group)
            logging.info('[WLANsCheck]WLAN[%s], WLANGroup[%s] are created successfully' % (wlan_conf, wlan_group))
            logging.info('[WLANsCheck]try to verify status of WLAN[%s] against APs' % wlan_conf)                                    
            self._go_through_aps_wlan(wlan_conf)
            logging.info('[WLANsCheck]try to verify status of WLAN[%s] against RuckusAPs and WirelessClient' % wlan_conf)
            self._go_through_ruckus_aps_wlan(wlan_conf) 
            if self.errmsg:
                return self.errmsg   
                  
            zhlp.wgs.remove_wlan_groups(self.zd)
            zhlp.wlan.delete_all_wlans(self.zd)
                
    def _select_client_and_check(self):
            # Find the target station object and remove all Wlan profiles
            for station in self.testbed.components['Station']:
                if station.get_ip_addr() == self.conf['target_station']:
                    # Found the target station
                    self.target_station = station
    
                    logging.info("Remove all WLAN profiles on the target station %s" % self.target_station.get_ip_addr())
                    self.target_station.remove_all_wlan()
    
                    logging.info("Make sure the target station %s disconnects from wireless network" % 
                                 self.target_station.get_ip_addr())
                    start_time = time.time()
                    while True:
                        if self.target_station.get_current_status() == "disconnected":
                            break
                        
                        time.sleep(1)
                        if time.time() - start_time > self.check_status_timeout:
                            raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                            self.check_status_timeout)
                    break
                
            if not self.target_station:
                raise Exception("Target station % s not found" % self.conf['target_station'])  