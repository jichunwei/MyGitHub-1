'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to get service information from ZD GUI.

'''


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import service_zd


class CB_ZD_Get_Service_Info(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getServiceInfomation()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'back_up': False}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getServiceInfomation(self):
        logging.info('Get the service information from ZD GUI.')
        try:
            self.service_info = service_zd.get_service_info(self.zd)
            logging.info("The service information in ZD GUI is: %s" % pformat(self.service_info, 4, 120))
            self.passmsg = 'Get the service information from ZD GUI successfully'
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        if self.conf['back_up']:
            self.carrierbag['bak_service_info'] = self.service_info
        
        else:
            self.carrierbag['zdgui_service_info'] = self.service_info

                