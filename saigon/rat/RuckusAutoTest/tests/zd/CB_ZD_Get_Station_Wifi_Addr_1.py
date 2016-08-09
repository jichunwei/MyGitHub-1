"""
Description: This script is support to get wifi address on remote station
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Get_Station_Wifi_Addr_1(Test):

    def config(self, conf):
        self._init_test_parameters(conf)


    def test(self):
        '''
        '''
        self._test_verify_station_info_on_zd()

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self._update_carrier_bag()

        self.passmsg = \
            'Get station [%s] wifi ip address [%s] and wifi mac address [%s] successfully' % \
            (self.conf['sta_tag'], self.var1, self.var2.lower())

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _init_test_parameters(self, conf):
        '''
        '''
        self.errmsg = ''
        self.passmsg = ''

        self.conf = {
            'check_status_timeout': 120,
            'breaktime': 10,
        }
        self.conf.update(conf)

        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']


    def _test_verify_station_info_on_zd(self):
        '''
        '''
        res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(
            self.target_station, self.conf['check_status_timeout']
        )
        if not res:
            self.errmsg = self.var2


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.var1
        self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] = self.var2.lower()

