'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to get alarm information from ZD GUI.

'''


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import alarm_setting_zd


class CB_ZD_Get_Alarm_Info(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getAlarmInfomation()
        
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

    def _getAlarmInfomation(self):
        logging.info('Get the alarm information from ZD GUI.')
        try:
            self.alarm_info = alarm_setting_zd.get_alarm_setting(self.zd)
            logging.info("The alarm information in ZD GUI is: %s" % pformat(self.alarm_info, 4, 120))
            self.passmsg = 'Get the alarm information from ZD GUI successfully'
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_alarm_info'] = self.alarm_info
        
        