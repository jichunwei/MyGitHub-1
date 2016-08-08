'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the alarm information in ZD CLI with ZD GUI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_alarm


class CB_ZD_CLI_Verify_Alarm_Cfg_In_GUI(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAlarmCfgInGUI()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.cli_cfg_dict = conf['alarm_cfg']
        self.gui_info_dict = self.carrierbag['zdgui_alarm_info']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAlarmCfgInGUI(self):
        logging.info('Verify the alarm information in ZD GUI')
        try:
            res, msg = configure_alarm.verify_cli_alarm_cfg_in_gui(self.cli_cfg_dict, self.gui_info_dict)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
