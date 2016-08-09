"""
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Client_Reconnect(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        self._test_client_reconnect()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'Client reconnection successfully'
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {'sta_tag': '',
                     'ssid': '',
                     'check_status_timeout': 120,
                     }
        self.conf.update(conf)
        self.sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        self.errmsg = ''
        self.passmsg = ''


    def _test_client_reconnect(self):
        '''
        '''
        self.sta.disconnect_from_wlan()

        self.sta.connect_to_wlan(self.conf['ssid'])

        res, var1, var2 = tmethod.renew_wifi_ip_address(
                              self.sta,
                              self.conf['check_status_timeout'],
                          )
        if not res:
            self.errmsg = var2

