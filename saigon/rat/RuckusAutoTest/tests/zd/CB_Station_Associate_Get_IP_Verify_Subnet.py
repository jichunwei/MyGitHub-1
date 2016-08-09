# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Dec 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
      'sta_tag': 'Station tag',
      'wlan_cfg': 'Wlan configuration',
      'expected_subnet': 'Expected subnet of ipv4, 192.168.0.252/255.255.255.0',
      'expected_subnet_ipv6': 'Expected subnet of ipv6, 2020:db8:1::251/64',
      'ip_version': 'IP version information, it can be ipv4, ipv6 and dual stack',
      'restart_cnt': 'Restart network count',
      'is_negative': 'Is verify station can not associate the wlan',
      'check_status_timeout': 'Time out to check the station associated',
      'break_time': 'Break time during each retry',
      'browser_name': "Browser name, default is firefox",
      'start_browser_tries': 'Retries to start a browser',
      'start_browser_timeout': 'Timeout to start a browser',
      'remove_all_wlans': 'Will remove all wlan from the station before associate',
      'start_browser': 'Will start a browser',
      'get_sta_wifi_ip': 'Will get station wifi ip address',      
      'verify_ip_subnet': 'Will verify ip address in expected subnet',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - [Optional] Remove all wlans from station, default is True
        - Associate the station to wlan via wlan profile/zero-it
        - Get station wifi ip address [ipv4 and ipv6]
        - [Optional] Start browser, default is True
        - [Optional] Verify wifi ip address is in expected subnet, default is True
        
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If all steps works correctly: remove all wlans from station, associate to the wlan, 
                   get station wifi ip addresses, start browser and verify IP subnet. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
from copy import deepcopy 
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig


class CB_Station_Associate_Get_IP_Verify_Subnet(Test):
    required_components = ['Station']
    parameters_description = {'sta_tag': 'Station tag',
                              'browser_tag': 'Browser tag',
                              'wlan_cfg': 'Wlan configuration',
                              'expected_subnet': 'Expected subnet of ipv4, 192.168.0.252/255.255.255.0',
                              'expected_subnet_ipv6': 'Expected subnet of ipv6, 2020:db8:1::251/64',
                              'ip_version': 'IP version information, it can be ipv4, ipv6 and dual stack',
                              'restart_cnt': 'Restart network count',
                              'is_negative': 'Is verify station can not associate the wlan',
                              'check_status_timeout': 'Timeout to check the station associated',
                              'break_time': 'Break time during each retry',
                              'browser_name': "Browser name, default is firefox",
                              'start_browser_tries': 'Retries to start a browser',
                              'start_browser_timeout': 'Timeout to start a browser',
                              'remove_all_wlans': 'Will remove all wlan from the station before associate',
                              'start_browser': 'Will start a browser',
                              'get_sta_wifi_ip': 'Will get station wifi ip address',                              
                              'verify_ip_subnet': 'Will verify ip address in expected subnet',
                              'is_restart_adapter': 'Is restart wifi adapter',
                              }    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            if self.conf['is_restart_adapter']:
                tmethod.restart_station_adapter(self.target_station)
                
            if self.conf['remove_all_wlans']:
                self._remove_all_wlans_from_station()
                
            self._associate_station_to_wlan()            
            #For negative, only need to do associate the wlan, don't need to do the other vatlidation.
            if not self.conf['is_negative'] and not self.errmsg:
                if self.conf['start_browser'] and not self.errmsg:
                    self._start_browser()
                if self.conf['get_sta_wifi_ip'] and not self.errmsg:
                    self._get_sta_wifi_addr()
                    if self.conf['verify_ip_subnet'] and not self.errmsg:
                        self._verify_ip_address_subnet()
                    
        except Exception, ex:
            self.errmsg = "Exception: %s" % ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carribag()
            self.passmsg = "The steps %s works correctly." % self.steps
            return  self.returnResult('PASS', self.passmsg)                     
    
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf  = {'sta_tag': 'sta_1',
                      'browser_tag': 'browser',
                      'wlan_cfg': {},
                      'expected_subnet': "", #"192.168.0.252/255.255.255.0",
                      'expected_subnet_ipv6': "", #"2020:db8:1::251/64",
                      'ip_version': const.IPV4,
                      'restart_cnt': 6,
                      'is_negative': False,
                      'check_status_timeout': 240,
                      'break_time': 10,        
                      'browser_name': "firefox",
                      'start_browser_tries': 3,
                      'start_browser_timeout': 15,
                      'remove_all_wlans': True,              
                      'start_browser': True,
                      'get_sta_wifi_ip': True,
                      'verify_ip_subnet': True,
                      'is_restart_adapter': True,
                      'tshark_params':''
                      }
        
        self.conf.update(conf)
        
        if not self.conf['get_sta_wifi_ip']:
            self.conf[''] = False
                
        if not self.conf['ip_version'] in [const.IPV4, const.IPV6, const.DUAL_STACK]:
            raise Exception("IP version [%s] is incorrect." % self.conf['ip_version'])
        
        #Get station wifi expected subnet information.
        if self.conf['verify_ip_subnet']:
            l = self.conf['expected_subnet'].split("/")
            self.expected_subnet_ip_addr = l[0]
            if len(l) == 2:
                self.expected_subnet_mask = l[1]
            else:
                self.expected_subnet_mask = ""
                
            l = self.conf['expected_subnet_ipv6'].split("/")
            self.expected_subnet_ipv6_addr = l[0]
            if len(l) == 2:
                self.expected_prefix_len = l[1]
            else:
                self.expected_prefix_len = ""
        else:
            self.expected_subnet_ip_addr = ""
            self.expected_subnet_mask = ""
            self.expected_subnet_ipv6_addr = ""
            self.expected_prefix_len = ""
        
        self.errmsg = ''
        self.passmsg = ''
        self.steps = []
        
        self.sta_wifi_ip_addr = None
        self.sta_wifi_ipv6_addr_list = None   
        self.sta_wifi_mac_addr = None     
    
    def _retrieve_carribag(self):
        sta_dict = self.carrierbag.get(self.conf['sta_tag'])
        if sta_dict:
            self.target_station = sta_dict['sta_ins']
        else:
            raise Exception("No station provided.")
        
        #Get zero it tool path from carrier bag.
        if self.carrierbag.has_key('zeroit_tool_path'):            
            self.zeroit_toolpath = self.carrierbag['zeroit_tool_path']
        else:
            self.zeroit_toolpath = None
                
    def _update_carribag(self):
        if self.conf['get_sta_wifi_ip']:
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.sta_wifi_ip_addr
            self.carrierbag[self.conf['sta_tag']]['wifi_ipv6_addr_list'] = self.sta_wifi_ipv6_addr_list
            self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.sta_wifi_mac_addr
        
        if self.conf['start_browser']:
            browser_dict = {}
            browser_dict['browser_id'] = self.browser_id
            browser_dict['browser_name'] = self.conf['browser_name']
            self.carrierbag[self.conf['browser_tag']] = browser_dict
    
    #-----------------Main validation steps method -------------------
    def _remove_all_wlans_from_station(self):
        '''
        Remove all wlans from station/disassociate the wlan.
        '''
        logging.info("Remove all wlans from station")
        tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])
        
    def _associate_station_to_wlan(self):
        '''
        Associate the station to wlan via setting wlan profile or zero-it.
        '''
        errmsg = None
        passmsg = None
        
        if self.conf['wlan_cfg'].get('do_zero_it') == True:
            step_name = "Associate the wlan via Zero-IT"
            errmsg, passmsg = self._associate_station_to_wlan_via_zero_it()
        else:
            step_name = "Associate the wlan"
            errmsg, passmsg = self._associate_station_to_wlan_via_profile()
            
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)
                
    def _get_sta_wifi_addr(self):
        '''
        Get station wifi addresses: IPV4 and IPV6.
        '''
        errmsg = None
        passmsg = None
        
        try:
            logging.info('Get Station Wifi IP Addresses')
            
            if self.conf['ip_version'] == const.IPV4:
                res, self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = tmethod.renew_wifi_ip_address(self.target_station, 
                                                                                  self.conf['check_status_timeout'],
                                                                                  self.conf['break_time'])
                
                if not res:
                    errmsg = self.sta_wifi_mac_addr
            else:
                res, self.sta_wifi_ip_addr, self.sta_wifi_ipv6_addr_list, self.sta_wifi_mac_addr, errmsg = \
                            tmethod.renew_wifi_ip_address_ipv6(self.target_station, 
                                                               self.conf['ip_version'], 
                                                               self.conf['check_status_timeout'], 
                                                               wait_time = self.conf['break_time'])
                            
            if not res:            
                errmsg = "Fail to get IP addresses for station: %s" % (errmsg)
            else:
                self.sta_wifi_mac_addr = self.sta_wifi_mac_addr.lower()
                passmsg = 'Get station wifi IP addresses successfully: %s,%s' % (self.sta_wifi_ip_addr, self.sta_wifi_ipv6_addr_list)
                        
        except Exception, ex:
            errmsg = ex.message
        
        step_name = "Get station wifi IP addresses"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)
            
    def _start_browser(self):
        '''
        Start browser in station.
        '''
        errmsg = None
        
        try:
            logging.info("Trying to start the %s browser on the station %s" \
                        % (self.conf['browser_name'], self.conf['sta_tag']))
            self.browser_id = self.target_station.init_and_start_browser(self.conf['browser_name'],
                                                              self.conf['start_browser_tries'], 
                                                              self.conf['start_browser_timeout'])
            self.browser_id = int(self.browser_id)
            passmsg = "The %s browser on the station %s was started successfully with ID %s" \
                              % (self.conf['browser_name'], self.conf['sta_tag'], self.browser_id)            

        except Exception, ex:
            errmsg = ex.message
            
        step_name = "Start browser"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)
    
    def _verify_ip_address_subnet(self):
        '''
        Verify if station wifi ip addresses in expected subnet. Include ipv4 and ipv6.
        '''
        errmsg = None
        passmsg = None
        
        try:
            errmsg = ""
            if self.conf['ip_version'] in [const.IPV4, const.DUAL_STACK]:                
                errmsg_ipv4 = self._verify_sta_subnet_ipv4()
                if errmsg_ipv4:
                    errmsg = errmsg + "IPV4: %s" % errmsg_ipv4                 
            if self.conf['ip_version'] in [const.IPV6, const.DUAL_STACK]:                
                errmsg_ipv6 = self._verify_sta_subnet_ipv6()
                if errmsg_ipv6:
                    errmsg = errmsg + "IPV6: %s" % errmsg_ipv6
                
            if self.conf['ip_version'] == const.DUAL_STACK:
                passmsg = "Station wifi ipv4 and ipv6 address is in expected subnet."
            elif self.conf['ip_version'] == const.IPV4:
                passmsg = "Station wifi ipv4 address is in expected subnet."
            else:
                passmsg = "Station wifi ipv6 address is in expected subnet."
                
        except Exception,ex:
            errmsg = "Fail to verify station ip subnet: %s" % ex.message
            
        step_name = "Verify IP address in subnet"
        if errmsg:
            self.errmsg = "%s failed:%s" % (step_name, errmsg)
            logging.warning(self.errmsg)
        else:
            self.steps.append(step_name)
            logging.info(passmsg)
    
    #------------------------ Sub Methods calling by main step method. ------------------------
    def _associate_station_to_wlan_via_profile(self):
        '''
        Associate the station to wlan.
        '''
        errmsg = None
        passmsg = None
        
        try: 
            wlan_cfg = deepcopy(self.conf['wlan_cfg'])
            if wlan_cfg.has_key("wpa_ver") and wlan_cfg.get("wpa_ver").lower() == "wpa_mixed":
                wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
            if wlan_cfg.has_key("encryption") and wlan_cfg.get("encryption").lower() == "auto":
                wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
    
            errmsg = tmethod.assoc_station_with_ssid(self.target_station,
                                                     wlan_cfg,
                                                     self.conf['check_status_timeout'],
                                                     self.conf['break_time'],
                                                     self.conf['restart_cnt'],
                                                     self.conf['tshark_params'],
                                                     )
            
            if self.conf['is_negative']:
                if errmsg:
                    #Pass
                    if "couldn't associate" in self.errmsg:
                        passmsg = "The station was not allowed to associate due to ACL."
                    else:
                        passmsg = "The station can't associate the wlan."
                else:
                    errmsg = "The stations was associated although it was not allowed to."
            else:
                #If can't associate and is_negative is False, verify the wlan in the air.
                if not errmsg:
                    passmsg = "The station associate the wlan successfully."
                else:
                    logging.info('Verify if the wlan is in the air.')
                    errmsg = tmethod.verify_wlan_in_the_air(self.target_station, 
                                                            wlan_cfg['ssid'])
        except Exception, ex:
            errmsg = ex.message
            
        return errmsg, passmsg
    
    def _associate_station_to_wlan_via_zero_it(self):
        '''
        Execute zero-it file and wait the station to associate the wlan.
        '''
        errmsg = None
        passmsg = None
        
        try:    
            #Get use_raidus value via auth_svr value.
            if self.conf['wlan_cfg'].has_key('auth_svr') and not (self.conf['wlan_cfg']['auth_svr'].lower() == 'local database'):
                use_radius = True
            else:
                use_radius = False
                
            logging.info('Executing zero it to associate station to wlan %s' % self.conf['wlan_cfg']['ssid'])
            self.target_station.execute_zero_it(self.zeroit_toolpath, self.conf['wlan_cfg']['ssid'], self.conf['wlan_cfg']['auth'], use_radius)
            
            logging.info("Verify the status of the wireless adapter on the target station")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "connected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.conf['check_status_timeout']:
                    errmsg = "Timed out. The station didn't associate to the WLAN after %s" % \
                                 self.conf['check_status_timeout']
                    logging.info(errmsg)
                    break
        
            if self.conf['is_negative']:
                if errmsg:
                    #Pass
                    if "couldn't associate" in self.errmsg:
                        passmsg = "The station was not allowed to associate due to ACL."
                    else:
                        passmsg = "The station can't associate the wlan."
                else:
                    errmsg = "The stations was associated although it was not allowed to."
            else:
                #If can't associate and is_negative is False, verify the wlan in the air.
                if not errmsg:
                    passmsg = "The station associate the wlan via zero-it successfully."
                else:
                    logging.info('Verify if the wlan is in the air.')
                    errmsg = tmethod.verify_wlan_in_the_air(self.target_station, 
                                                            self.conf['wlan_cfg']['ssid'])
        except Exception, ex:
            errmsg = ex.message
            
        return errmsg, passmsg
    
    def _verify_sta_subnet_ipv4(self):
        '''
        Verify station wifi ipv4 address in expected subnet.
        '''
        errmsg = None
        
        logging.info("Verify station WIFI IPV4 address in expected subnet")
        expected_subnet = utils.get_network_address(self.expected_subnet_ip_addr, self.expected_subnet_mask)        
        sta_wifi_ip_subnet = utils.get_network_address(self.sta_wifi_ip_addr, self.expected_subnet_mask)
        if expected_subnet != sta_wifi_ip_subnet:
            errmsg = "The leased IPV4 address was '%s', which is not in the expected subnet '%s'" % \
                        (self.sta_wifi_ip_addr, expected_subnet)
        else:
            logging.info("The IPV4 address is %s in expected subnet %s." % (self.sta_wifi_ip_addr, expected_subnet))        
                        
        return errmsg
                          
    def _verify_sta_subnet_ipv6(self):
        '''
        Verify station wifi ipv6 address in expected subnet.
        '''
        errmsg = None
        
        logging.info("Verify station WIFI IPV6 address in expected subnet")
        
        invalid_ipv6_list = []
        expected_subnet_ipv6 = utils.get_network_address_ipv6(self.expected_subnet_ipv6_addr, self.expected_prefix_len)
        
        for ipv6_addr in self.sta_wifi_ipv6_addr_list:
            sta_wifi_ipv6_subnet = utils.get_network_address_ipv6(ipv6_addr, self.expected_prefix_len)
            if expected_subnet_ipv6 != sta_wifi_ipv6_subnet:
                invalid_ipv6_list.append(ipv6_addr)
        
        if invalid_ipv6_list:
            errmsg = "The leased IPV6 address was %s, %s are not in the expected subnet '%s'" % \
                        (self.sta_wifi_ipv6_addr_list, invalid_ipv6_list, expected_subnet_ipv6)
        else:
            logging.info("The IPV6 addresses are %s in expected subnet %s." % (self.sta_wifi_ipv6_addr_list, expected_subnet_ipv6))
                        
        return errmsg