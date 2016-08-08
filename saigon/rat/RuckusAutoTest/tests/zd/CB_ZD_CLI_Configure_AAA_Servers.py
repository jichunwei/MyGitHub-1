'''
Created on Jan 8, 2011
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure aaa servers in ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


class CB_ZD_CLI_Configure_AAA_Servers(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._configureAAAServers()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.server_cfg_list = conf['server_cfg_list']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _configureAAAServers(self):
        logging.info('Configure aaa servers in ZD CLI')
        try:
            res, msg = cas.configure_aaa_servers(self.zdcli, self.server_cfg_list)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
            