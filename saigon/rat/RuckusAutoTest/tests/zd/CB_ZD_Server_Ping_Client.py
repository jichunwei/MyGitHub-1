"""
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RemoteStationWinPC import RemoteStationWinPC

class CB_ZD_Server_Ping_Client(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)


    def test(self):
        self._test_server_ping_client()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = ''
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        self.conf = {'server_ins': '',
                     'condition': 'allowed', #['allowed', 'disallowed']
                     'ping_timeout_ms': 150 * 1000,
                     'target': '172.16.10.252',
                     }
        self.conf.update(conf)

        if self.conf['server_ins']:
            self.server = self.conf['server_ins']

        else:
            self.server = self.testbed.components['LinuxServer']

        try:
            target = self.carrierbag[self.conf['target']]['sta_ins']
            if isinstance(target, RemoteStationWinPC):
                self.target_ip = target.get_wifi_addresses()[0]

        except:
            self.target_ip = self.conf['target']

        self.errmsg = ''
        self.passmsg = ''


    def _test_server_ping_client(self):
        '''
        '''
        ping_result = self.server.ping(self.target_ip,
                                       self.conf['ping_timeout_ms'])

        if 'allowed' == self.conf['condition']:
            if ping_result.find("Timeout") != -1:
                self.errmsg = 'Ping FAILED. Incorrect behavior'

            else:
                self.passmsg = 'Ping OK. Correct behavior'

        elif 'disallowed' == self.conf['condition']:
            if ping_result.find("Timeout") != -1:
                self.passmsg = 'Ping FAILED. Correct behavior'

            else:
                self.errmsg = 'Ping OK. Incorrect behavior'

