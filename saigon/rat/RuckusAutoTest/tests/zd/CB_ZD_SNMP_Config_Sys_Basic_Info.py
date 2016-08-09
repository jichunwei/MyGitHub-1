'''
Created on Mar 27, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to configure system info via zd snmp.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_info

class CB_ZD_SNMP_Config_Sys_Basic_Info(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._config_system_info()   
        self._update_carrier_bag()     
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            
            self.passmsg = 'The read-write nodes are updated successfully.'
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'test_cfg_sys_info': {}}
        self.conf.update(conf)
        
        if self.conf['test_cfg_sys_info']:
            self.test_cfg_sys_info = self.conf['test_cfg_sys_info']
        else:
            self.test_cfg_sys_info = sys_info.gen_test_data_sys_info()
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['test_cfg_sys_info'] = self.test_cfg_sys_info

    def _config_system_info(self):
        logging.info('Configure system information via ZD SNMP')
        try:
            update_cfg = self.test_cfg_sys_info 
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               

            snmp = helper.create_snmp(snmp_cfg)
            res_d = sys_info.update_sys_info(snmp, update_cfg)
            
            #Only filter some kind of errors.
            err_d = {}
            for key, value in res_d.items():
                if type(value) == dict and value.has_key('error'):
                    err_d.update({key: value})
                                        
            if err_d:
                self.errmsg = err_d
            else:
                self.passmsg = 'Update system basic information successfully.'
                                    
        except Exception, ex:
            self.errmsg = ex.message