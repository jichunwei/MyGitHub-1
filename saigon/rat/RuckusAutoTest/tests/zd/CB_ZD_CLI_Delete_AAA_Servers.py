'''
Created on Jan 8, 2011
@author: serena.tan@ruckuswireless.com

Description: This script is used to delete aaa servers from ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas
from RuckusAutoTest.components.lib.zdcli import aaa_servers


class CB_ZD_CLI_Delete_AAA_Servers(Test):
    def config(self, conf):        
        self._initTestParameters(conf)

    def test(self):
        self._deleteAAAServers()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if conf.get('server_name_list'):
            self.server_name_list = conf['server_name_list']
        else:
            self.server_name_list = aaa_servers.get_all_aaa_server_name_list(self.zdcli)
                    
        self.errmsg = ''
        self.passmsg = ''

    def _deleteAAAServers(self):
        logging.info('Delete aaa servers %s from ZD CLI' % self.server_name_list)
        try:
            res, msg = cas.delete_aaa_servers(self.zdcli, self.server_name_list)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message