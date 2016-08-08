'''
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_zd_by_ip_addr

class CB_ZD_WebUI_Launch(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        self._test_launch_webui()
        self._update_carrier_bag()

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'ip_addr': '192.168.0.2'
        }
        self.conf.update(conf)

        self.ip_addr = self.conf['ip_addr']

        self.errmsg = ""
        self.passmsg = ""


    def _update_carrier_bag(self):
        '''
        '''


    def _test_launch_webui(self):
        '''
        '''
        try:
            zd = create_zd_by_ip_addr(self.ip_addr)
            zd.destroy()

        except:
            self.errmsg = "Unable to launch ZD web UI"

        self.passmsg = "Able to launch ZD WebUI at management interface [%s]." % self.ip_addr

