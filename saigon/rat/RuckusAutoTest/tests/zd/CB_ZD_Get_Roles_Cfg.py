'''
Created on 2011-3-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to get the roles' configuration from ZD GUI.

'''


import logging
from pprint import pformat

from RuckusAutoTest.models import Test


class CB_ZD_Get_Roles_Cfg(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getRoles()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.role_name_list = conf['role_name_list']        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getRoles(self):
        logging.info('Get the configuration of roles %s from ZD GUI.' % self.role_name_list)
        self.role_cfg_list = []
        try:
            for role_name in self.role_name_list:
                role_cfg = self.zd.get_role_cfg_by_name(role_name)
                if role_cfg:
                    logging.info("The configuration of role [%s] in ZD GUI is: %s" % (role_name, pformat(role_cfg, 4, 120)))
                    self.role_cfg_list.append(role_cfg)
            
            self.passmsg = 'Get the configuration of roles [%s] from ZD GUI successfully' % self.role_name_list
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_role_info_list'] = self.role_cfg_list
     
                