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

class CB_ZD_CLI_Debug_Restart_AP(Test):
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        self._verify_debug_restart_ap()
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

    def _do_debug_restart(self, ap_mac):
        logging.log_info('Debug', 'Execute command', 'restart-ap')
        try:
            var, res = lib.zdcli.debug.restart_ap(self.zdcli, ap_mac)
            logging.log_info('Debug', 'Return Output', '%s' % res)
            if var:
                self.passmsg = '[DEBUG MODE] command "restart" works correctly'
            else:
                self.errmsg = 'The command "restart-ap" could not execute'
        except Exception, e:
            self.errmsg = '[DEBUG MODE][PS] %s' % e.message
    
    def _get_connected_ap_list(self):
        ap_list = lib.zd.ap.get_all_ap_info(self.zd).keys()
        logging.log_info('WebUI', 'Monitor', 'Connectted APs: %s' % ap_list)
        return ap_list
    
    def _verify_debug_restart_ap(self):
        ap_list = self._get_connected_ap_list()
        if not ap_list:
            self.errmsg = 'There is no connected AP. Could not complete the test.'
            return
                
        ap_mac = ap_list[0]
        self._do_debug_restart(ap_mac)