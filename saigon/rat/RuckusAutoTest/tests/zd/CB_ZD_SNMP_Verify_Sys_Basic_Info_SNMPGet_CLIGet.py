'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify system basic information between SNMP get and CLI set.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import sys_info
from RuckusAutoTest.components.lib.snmp import snmphelper as helper


class CB_ZD_SNMP_Verify_Sys_Basic_Info_SNMPGet_CLIGet(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_sys_info_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        if self.conf['recovery'] == True:
            self._recover_system_info()
    
    def _retrive_carrier_bag(self):
        self.zdcli_sys_info_dict = self.carrierbag['zdcli_sys_info']
        self.snmp_sys_info_dict = self.carrierbag['snmp_sys_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf={'recovery': False}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''

    def _verify_sys_info_snmp_cli_get(self):
        logging.info('Verify system basic information SNMP get and cli get')
        try:
            res_d = sys_info.verify_sys_info_snmp_cli(self.snmp_sys_info_dict, self.zdcli_sys_info_dict)
            
            self.errmsg = res_d
            self.passmsg = 'System basic information are same between SNMP get and CLI get'
            
        except Exception, ex:
            self.errmsg = ex.message
    
    def _recover_system_info(self):
        logging.info('Configure system information via ZD SNMP')
        try:
            update_cfg = {'system_name': 'Ruckus', 'country_code': 'US', 'ntp_enable': 2, 'syslog_enable': 2, 'fm_enable': 2, 'email_enable': 2} 
            
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
                self.passmsg = 'Recover system basic information successfully.'
                                    
        except Exception, ex:
            self.errmsg = ex.message
