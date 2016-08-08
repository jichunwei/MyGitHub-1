"""
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Client_Ping_Dest(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        self._test_client_ping_dest()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = ''
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {'sta_tag': '',
                     'condition': 'allowed', #['allowed', 'disallowed']
                     'ping_timeout_ms': 15 * 1000,
                     'target': '172.16.10.252',
                     'clean_arp_before_ping': False}
        self.conf.update(conf)
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        try:
            target = self.carrierbag[self.conf['target']]['sta_ins']
            if isinstance(target, RemoteStationWinPC):
                self.target_ip = target.get_wifi_addresses()[0]

        except:
            self.target_ip = self.conf['target']

        self.errmsg = ''
        self.passmsg = ''

    def _test_client_ping_dest(self):
        if self.conf['clean_arp_before_ping']:
            try:
                self.target_station.clean_arp()
                
            except Exception, ex:
                self.errmsg = ex.message
                return
        
        if 'allowed' == self.conf['condition']:
            self.errmsg = tmethod.client_ping_dest_is_allowed(
                              self.target_station,
                              self.target_ip,
                              ping_timeout_ms = self.conf['ping_timeout_ms'],
                          )

        elif 'disallowed' == self.conf['condition']:
            self.errmsg = tmethod.client_ping_dest_not_allowed(
                              self.target_station,
                              self.target_ip,
                              ping_timeout_ms = self.conf['ping_timeout_ms'],
                          )

