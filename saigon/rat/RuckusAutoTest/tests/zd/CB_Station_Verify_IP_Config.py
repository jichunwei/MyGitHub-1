# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.
'''
Description:
   This script is support to verify the wifi ipconfig which is the expected in the station.
   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: Dec 2012
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

class CB_Station_Verify_IP_Config(Test):
    required_components = ['RemoteStationWinPC']
    parameters_description = {}
                                                         
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carrierbag()    
    
    def test(self):
        self._get_sta_wifi_ipconfig()
        
        if self.conf.get('expected_dhcp_svr'):
            self._verify_sta_dhcp_svr_info()
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        if self.conf.get('expected_subnet'):
            self._verify_sta_subnet()        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass


    def _init_params(self, conf):
        self.conf = {'expected_dhcp_svr': '',
                     'expected_subnet': ''
                     }
        self.conf.update(conf)
        
        if self.conf['expected_subnet']:
            l = self.conf['expected_subnet'].split("/")
            self.expected_subnet_ip_addr = l[0]
            if len(l) == 2:
                self.expected_subnet_mask = l[1]
            else:
                self.expected_subnet_mask = ""              
                
        self.passmsg = ''
        self.errmsg = ''
    
    def _retrieve_carrierbag(self):
        if self.carrierbag.has_key('Station'):
            self.station = self.carrierbag['Station'][self.conf['sta_tag']]['sta_ins']
        else:
            self.station = self.carrierbag[self.conf['sta_tag']]['sta_ins']

    def _get_sta_wifi_ipconfig(self):
        self.wifi_ip_config = self.station.get_ip_config()
        logging.info('The station wifi ip config info: %s' % self.wifi_ip_config)
    
    def _verify_sta_dhcp_svr_info(self):
        if type(self.conf['expected_dhcp_svr']) is not list:
            self.conf['expected_dhcp_svr'] = [self.conf['expected_dhcp_svr']]
        if self.wifi_ip_config['dhcp_server'] not in self.conf['expected_dhcp_svr']:
            self.errmsg = 'The DHCP server ip is %s not belong to expected list %s' % (self.wifi_ip_config['dhcp_server'], self.conf['expected_dhcp_svr'])
        else:
            self.passmsg = 'The DHCP server ip is %s as expectation' % self.wifi_ip_config['dhcp_server']
    
    def _verify_sta_subnet(self):
        '''
        Verify station wifi ipv4 address in expected subnet.
        '''
        logging.info("Verify station WIFI IPV4 address in expected subnet")
        expected_subnet = utils.get_network_address(self.expected_subnet_ip_addr, self.expected_subnet_mask)        
        sta_wifi_ip_subnet = utils.get_network_address(self.wifi_ip_config['ip_addr'], self.wifi_ip_config['subnet_mask'])
        if expected_subnet != sta_wifi_ip_subnet:
            errmsg = "The leased IPV4 address was '%s', which is not in the expected subnet '%s'" % \
                        (self.wifi_ip_config, expected_subnet)
            self.errmsg = errmsg
        else:
            self.passmsg = "The IPV4 address is %s in expected subnet %s." % (self.wifi_ip_config, expected_subnet)     