"""
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_linux_station_by_ip_addr

class CB_StationLinuxPC_Create_Station(Test):

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        self._create_target_station()

        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)

        self.carrierbag[self.sta_tag]['sta_ins'] = self.sta
        self.passmsg = "Create station %s [%s] successfully" % (self.sta_tag, self.sta_ip_addr)

        self._update_carrier_bag()

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_tag': "",
            'sta_ip_addr': "192.168.1.101",
        }
        self.conf.update(conf)

        self.sta_tag = self.conf['sta_tag']
        self.sta_ip_addr = self.conf['sta_ip_addr']
        self.carrierbag[self.sta_tag] = {}

        self.errmsg = ""
        self.passmsg = ""


    def _create_target_station(self):
        '''
        '''
        self.sta = create_linux_station_by_ip_addr(self.sta_ip_addr)

        if not self.sta:
            self.errmsg = "Target station [%s %s] not found" % (self.sta_tag, self.sta_ip_addr)


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag[self.sta_tag]['sta_ins'] = self.sta

