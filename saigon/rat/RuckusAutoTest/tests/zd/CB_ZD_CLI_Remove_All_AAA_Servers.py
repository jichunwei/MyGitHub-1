'''
Created on Nov 20, 2013
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


class CB_ZD_CLI_Remove_All_AAA_Servers(Test):
    def config(self, conf):
        self._init_params(conf)

    def test(self):
        self._del_aaa_servers()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'Delete All Servers')

    def cleanup(self):
        pass

    def _init_params(self, conf):        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _del_aaa_servers(self):
        logging.info('Delete all aaa servers from ZD CLI')
        try:
            cas.delete_all_servers(self.zdcli)            
        except Exception, ex:
            self.errmsg = ex.message
