'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to get system basic information via ZD CLI, include basic sys info, alarm, management info.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.sys_basic_info import get_sys_info, get_cfg_sys_info
from RuckusAutoTest.components.lib.zdcli.alarm_info import get_alarm_info
from RuckusAutoTest.components.lib.zdcli.email_server_info import get_email_server_info


class CB_ZD_CLI_Get_Sys_Basic_Info(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_sys_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _get_sys_info(self):
        logging.info('Get system information via zd cli.')
        try:        
            basic_info = get_sys_info(self.zdcli)['System Overview']
            cfg_info = get_cfg_sys_info(self.zdcli)
            alarm_info = get_alarm_info(self.zdcli)
            email_server_info = get_email_server_info(self.zdcli)
        
            all_sys_info = {}
            all_sys_info.update(basic_info)
            all_sys_info.update(cfg_info)
            all_sys_info.update(alarm_info)
            all_sys_info.update(email_server_info)
            
            self.zdcli_sys_info_dict = all_sys_info
            
            self.passmsg = 'Get system basic information via ZD CLI successfully: %s' % self.zdcli_sys_info_dict
            logging.info('System basic information: %s' % self.zdcli_sys_info_dict)
            
        except Exception, ex:
            self.errmsg = ex.message     
        
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['zdcli_sys_info'] = self.zdcli_sys_info_dict  