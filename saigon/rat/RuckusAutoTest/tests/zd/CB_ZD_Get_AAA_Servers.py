'''
Created on Jan 8, 2011
@author: serena.tan@ruckuswireless.com

Description: This script is used to get aaa servers' information from ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import aaa_servers_zd


class CB_ZD_Get_AAA_Servers(Test):
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
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getAAAServers(self):
        logging.info('Get the cfg of aaa servers %s from ZD GUI.' % self.server_name_list)
        try:
            self.server_cfg_list = aaa_servers_zd.get_server_cfg_list_by_names(self.zd, self.server_name_list)
            self.passmsg = 'Get the cfg of aaa servers [%s] from ZD GUI successfully' % self.server_name_list
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_server_info_list'] = self.server_cfg_list
            
                