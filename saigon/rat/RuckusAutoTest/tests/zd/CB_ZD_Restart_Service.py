"""
Description: rename the file in linux PC
by west
"""

from RuckusAutoTest.models import Test
import logging


class CB_ZD_Restart_Service(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.info("restart service [%s]" %self.conf['service'])
        if not self.pc.restart_service(self.conf['service']):
            return self.returnResult("FAIL", self.errmsg) 
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'service':'radiusd'}
        self.conf.update(conf)
        self.pc = self.testbed.components['LinuxServer']

        self.pc.re_init()
        logging.info('Telnet to the server at IP address %s successfully' % \
                     self.pc.ip_addr)
        self.passmsg = "restart service [%s] successfully" %self.conf['service']
        self.errmsg = "restart service [%s] failed" %self.conf['service']
