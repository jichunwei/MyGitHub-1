# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for verifying if the OS information of station obtained by ZD is correct.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Aug 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director
   2. The MAC address and IP of Station have been obtained.
   
   Required components: 'ZoneDirector', 'Station' 
   Test parameters:
        - check_status_timeout: timeout for checking status
        - sta_tag: station tag, and will get station instance and information from carrier bag based on sta_tag
        
   Test procedure:
    1. Config:
        - Initilize test parameters, and get ZD component.         
    2. Test:
        - Verify station OS type information on ZD is same as expect.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If station OS type information is same as expect
            FAIL: If the information is different as expect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_Verify_Station_OS_Type_Info(Test):
    required_components = ['ZoneDirector', 'Station']
    parameter_description = {'check_status_timeout':'Timeout for checking status',
                             'sta_tag':'Station tag, and will get station instance and information from carrier bag based on sta_tag',
                             }

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_station_os_type_info()
        if self.conf['expect_get_sta_os']:
            if self.msg:
                return self.returnResult('FAIL', self.msg)
            else:
                self._update_carrier_bag()
                self.passmsg = 'Verify station OS type information [%s] on ZD successfully' % self.station_info_on_zd
            return self.returnResult('PASS', self.passmsg)
        else:
            if not self.msg:
                errmsg = 'ZD can display station OS type information even if Fingerprinting off'
                return self.returnResult('FAIL', errmsg)
            elif not self.current_client_info:
                errmsg = 'There is not any target station information on ZD'
                return self.returnResult('FAIL', errmsg)
            elif self.station_info_on_zd:
                return self.returnResult('FAIL', self.msg)
            else:
                self._update_carrier_bag()
                self.passmsg = 'Verify station OS type information [%s] on ZD successfully' % self.station_info_on_zd
                return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'check_status_timeout':60,
                     'sta_tag':'sta_1',
                     }

        self.conf.update(conf)
        self.zd = self.testbed.components["ZoneDirector"]
        self._retrieve_carribag()
        self.msg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']

    def _verify_station_os_type_info(self):
        logging.info("Verify target station OS type information shown on the Zone Director")
        exp_sta_os_type = self._get_sta_os_type()
        self.msg, self.station_info_on_zd, self.current_client_info = tmethod.verify_station_os_type_info(
                                                                      self.zd,
                                                                      self.sta_wifi_mac_addr,
                                                                      exp_sta_os_type,
                                                                      self.conf['check_status_timeout']
                                                                      )
        
        logging.info('Target station OS type information on ZD is %s' % (self.station_info_on_zd))

    def _get_sta_os_type(self):
        station_list = self.testbed.components["Station"]
        target_station = tconfig.get_target_station(self.conf['sta_ip_addr'], station_list, remove_all_wlan = False)
        sta_platform_info = target_station.get_os_platform().split(',')
        return [sta_platform_info[0], sta_platform_info[1]]

    def _update_carrier_bag(self):
        self.carrierbag['station_os_type_info_on_zd'] = self.station_info_on_zd
