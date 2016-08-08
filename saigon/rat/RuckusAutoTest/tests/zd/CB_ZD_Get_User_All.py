'''
Created on 2010-11-5
@author: serena.tan@ruckuswireless.com

Description: This script is used to get a list of all users from ZD GUI.

'''

import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import user
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Get_User_All(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getUserAll()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getUserAll(self):
        logging.info('Get the information of all users from ZD GUI.')
        try:
            self.all_user = user.get_all_users(self.zd)
            
        except Exception, ex:
            self.errmsg = ex.message
        
        self.passmsg = 'Get the information of all users from ZD GUI successfully'
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_all_users_list'] = self.all_user
                