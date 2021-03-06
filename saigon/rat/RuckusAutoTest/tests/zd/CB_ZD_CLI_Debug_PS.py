"""
Description:
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:  

   How it is tested?
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Debug_PS(Test):
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        self._do_debug_ps()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.debug_info = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180}
        
        if conf.has_key('debug_info'):
            self.debug_info = conf['debug_info']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''

    def _do_debug_ps(self):
        logging.log_info('Debug', 'Execute command', 'PS')
        try:
            res = lib.zdcli.debug.ps(self.zdcli)
            logging.log_info('Debug PS', 'Return Output', '%s' % res['ps'])
            self.passmsg = '[DEBUG MODE] command "ps" works correctly'
        except Exception, e:
            self.errmsg = '[DEBUG MODE][PS] %s' % e.message
            