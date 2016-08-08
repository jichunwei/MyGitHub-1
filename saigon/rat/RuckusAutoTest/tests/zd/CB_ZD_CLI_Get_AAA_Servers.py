'''
Created on Jan 8, 2011
@author: serena.tan@ruckuswireless.com

Description: This script is used to get aaa servers' information from ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


class CB_ZD_CLI_Get_AAA_Servers(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getAAAServers()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.server_name_list = conf['server_name_list']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _getAAAServers(self):
        logging.info('Get the information of aaa servers %s from ZD CLI.' % self.server_name_list)
        try:
            self.server_info_list = cas.get_server_info_by_names(self.zdcli, self.server_name_list)
            self.passmsg = 'Get the information of aaa servers [%s] from ZD CLI successfully' % self.server_name_list
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_server_info_list'] = self.server_info_list
        