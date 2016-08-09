# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Nov 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       - check_status_timeout: timeout for check status,
       - expected_subnet: Station expected subnet for ipv4. E.g. 192.168.0.0/255.255.255.0
       - expected_subnet_ipv6: Station expected subnet for ipv6.E.g. 2020:db8:1::251/64
       - ip_version: ZD IP version, the values are dualstack, ipv6, ipv4.
       - need_get_sta_wifi_addr: is need to get station wifi address. If True, get station wifi address, if False, get station wifi from carrier bag.
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Get station wifi ipv4 and ipv6 address
        - Verify ipv4 and ipv6 address are in expected subnet.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get station wifi address successfully and they are in expected subnet. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_Station_Get_Wifi_Addr_Verify_Expect_Subnet_IPV6(Test):
    required_components = ['Station']
    parameters_description = {'check_status_timeout': 'timeout for check status',
                              'expected_subnet': 'Station expected subnet for ipv4. E.g. 192.168.0.0/255.255.255.0',
                              'expected_subnet_ipv6': 'Station expected subnet for ipv6.E.g. 2020:db8:1::251/64',
                              'ip_version': 'ZD IP version, the values are dualstack, ipv6, ipv4',
                              'need_get_sta_wifi_addr': 'is need to get station wifi address.',
                              }
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carrier_bag()
    
    def test(self):
        try:
            if self.conf['need_get_sta_wifi_addr']:
                logging.info('Get Station Wifi Addresses [IPV4, IPV6]')
                self._get_station_wifi_address(self.ip_version)
                self.passmsg = 'Get station wifi address and they are in expected subnet.'
            else:
                self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
                self.sta_wifi_ipv6_addr_list = self.carrierbag[self.conf['sta_tag']]['wifi_ipv6_addr_list']
                self.passmsg = 'Station wifi addresses are in expected subnet.'
            
            if not self.errmsg:
                if self.ip_version in [const.IPV4, const.DUAL_STACK]:                
                    self._verify_sta_subnet_ipv4()
                if self.ip_version in [const.IPV6, const.DUAL_STACK]:                
                    self._verify_sta_subnet_ipv6()
            
        except Exception, ex:
            self.errmsg = ex.message
            
        if self.errmsg:
            logging.warning(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()            
            logging.info(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _cfg_init_test_params(self, conf):
        self.conf = dict(check_status_timeout = 120,
                         wait_time = 10,
                         expected_subnet = "",  #192.168.0.0/255.255.255.0
                         expected_subnet_ipv6 = "",  #2020:db8:1::251/64
                         ip_version = const.DUAL_STACK,
                         need_get_sta_wifi_addr = True)
        self.conf.update(conf)
        
        if self.conf.has_key('expected_subnet'):
            l = self.conf['expected_subnet'].split("/")
            self.expected_subnet_ip_addr = l[0]
            if len(l) == 2:
                self.expected_subnet_mask = l[1]
            else:
                self.expected_subnet_mask = ""
        else:
            self.expected_subnet_ip_addr = ""
            self.expected_subnet_mask = ""
            
        if self.conf.has_key('expected_subnet_ipv6'):
            l = self.conf['expected_subnet_ipv6'].split("/")
            self.expected_subnet_ipv6_addr = l[0]
            if len(l) == 2:
                self.expected_prefix_len = l[1]
            else:
                self.expected_prefix_len = ""
        else:
            self.expected_subnet_ipv6 = ""
            self.expected_prefix_len = ""
        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        
        self.ip_version = self.conf['ip_version'].lower()
        
        if not self.ip_version in [const.IPV4, const.IPV6, const.DUAL_STACK]:
            raise Exception("IP version [%s] is incorrect." % self.ip_version)
        
        self.passmsg = ''
        self.errmsg = ''
    
    def _get_station_wifi_address(self, ip_version):
        '''
        Get station wifi ipv4, ipv6 and mac address. If fail, will return message.
        '''
        res, self.sta_wifi_ip_addr, self.sta_wifi_ipv6_addr_list, self.wifi_mac_addr, err_msg = \
            tmethod.renew_wifi_ip_address_ipv6(self.target_station, ip_version, self.conf['check_status_timeout'], wait_time = self.conf['wait_time'])
        
        if not res:            
            self.errmsg = "Did not get IP addresses successfully for station %s: %s" % (self.wifi_mac_addr, err_msg)
    
    def _retrieve_carrier_bag(self):
        pass        
    
    def _update_carrier_bag(self):
        self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.sta_wifi_ip_addr
        self.carrierbag[self.conf['sta_tag']]['wifi_ipv6_addr_list'] = self.sta_wifi_ipv6_addr_list
        self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.wifi_mac_addr.lower()
    
    def _verify_sta_subnet_ipv4(self):
        '''
        Verify station wifi ipv4 address in expected subnet.
        '''
        logging.info("Verify station WIFI IPV4 address in expected subnet")
        self.expected_subnet = utils.get_network_address(self.expected_subnet_ip_addr, self.expected_subnet_mask)        
        sta_wifi_ip_subnet = utils.get_network_address(self.sta_wifi_ip_addr, self.expected_subnet_mask)
        if self.expected_subnet != sta_wifi_ip_subnet:
            self.errmsg = "The leased IPV4 address was '%s', which is not in the expected subnet '%s'" % \
                          (self.sta_wifi_ip_addr, self.expected_subnet)        
                          
    def _verify_sta_subnet_ipv6(self):
        '''
        Verify station wifi ipv6 address in expected subnet.
        '''
        logging.info("Verify station WIFI IPV6 address in expected subnet")
        invalid_ipv6_list = []
        self.expected_subnet_ipv6 = utils.get_network_address_ipv6(self.expected_subnet_ipv6_addr, self.expected_prefix_len)
        
        for ipv6_addr in self.sta_wifi_ipv6_addr_list:
            sta_wifi_ipv6_subnet = utils.get_network_address_ipv6(ipv6_addr, self.expected_prefix_len)
            if self.expected_subnet_ipv6 != sta_wifi_ipv6_subnet:
                invalid_ipv6_list.append(ipv6_addr)
        
        if invalid_ipv6_list:
            self.errmsg = "The leased IPV6 address was %s, %s are not in the expected subnet '%s'" % \
                                      (self.sta_wifi_ipv6_addr_list, invalid_ipv6_list, self.expected_subnet_ipv6)