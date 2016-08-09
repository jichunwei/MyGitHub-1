"""
"""
from RuckusAutoTest.models import Test

class CB_StationLinuxPC_Close_Station(Test):

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)
        self._retrive_carrier_bag()


    def test(self):
        '''
        '''
        self._test_close_station()

        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)

        self.passmsg = "Close station %s successfully" % (self.sta_tag)

        self._update_carrier_bag()

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_tag': "",
            'sta_ins': "",
        }
        self.conf.update(conf)

        self.sta_tag = self.conf['sta_tag']

        self.errmsg = ""
        self.passmsg = ""


    def _test_close_station(self):
        '''
        '''
        self.sta.__del__()

        try:
            self.sta.do_cmd("quit")

        except Exception, ex:
            self.passmsg = "The station [%s]'s connection was closed." % self.sta_tag
            return

        self.errmsg = "Error in closing the connection to the station [%s]" % self.sta_tag


    def _retrive_carrier_bag(self):
        '''
        '''
        self.sta = self.conf.get('sta_ins')
        if not self.sta and self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get('sta_ins')

        if not self.sta:
            raise Exception("No station provided.")


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag[self.sta_tag]['sta_ins'] = self.sta

