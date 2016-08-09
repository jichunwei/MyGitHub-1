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

class CB_ZD_CLI_Negative_Password_Test(Test):
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        {'all': self._test_negative_for_all,         
         'user': self._test_negative_name_setting_for_user,
         }[self.test_conf['test'].lower()]()
        
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
                          'time_out': 180,
                          'test': 'all'}
        
        if conf.has_key('debug_info'):
            self.debug_info = conf['debug_info']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''

    def _test_negative_name_setting_for_user(self):
        cmd_block = ""
        invalid_name_list = []
        for invalid_name in invalid_name_list:
            res = zdcli.do_cfg(cmd_block % invalid_name)
            if '' in res['']:
                self.errmsg = '[INCORRECT]Invalid value "" till could set for User name.' % invalid_name
        self.passmsg = 'All invalid values %s could not set for User name'
    
    def _test_negative_for_all(self):
        self._test_negative_name_setting_for_wlan()
        self.errmsg += self.errmsg
        self.passmsg += self.passmsg
        
        self._test_negative_name_setting_for_user()
        self.errmsg += self.errmsg
        self.passmsg += self.passmsg
        
        self._test_negative_name_setting_for_aaa_server()
        self.errmsg += self.errmsg
        self.passmsg += self.passmsg
            