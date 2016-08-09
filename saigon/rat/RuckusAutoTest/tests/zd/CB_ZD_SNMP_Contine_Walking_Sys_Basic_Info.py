'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify continue walking to get system basic information.
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_info


class CB_ZD_SNMP_Contine_Walking_Sys_Basic_Info(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_continue_walking_sys_basic_info()
        self._update_carrier_bag() 
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:          
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass        
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_sys_info'] = self.snmp_sys_info
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''

    def _verify_continue_walking_sys_basic_info(self):
        logging.info('Verify continue walking to get system basic info')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
                           
            snmp = helper.create_snmp(snmp_cfg)
            
            times = int(self.conf['times'])
            self.snmp_sys_info = {}
            if times < 1:
                raise Exception('Times must be greater than 1, please change the value.')
            else:
                sys_info_d_list, result_walking = self._walking_get_sys_basic_info(snmp, times)
                
                if sys_info_d_list and len(sys_info_d_list)>1:
                    self.snmp_sys_info = sys_info_d_list[0]
                    
                if result_walking:
                    self.errmsg = 'Continue walking is failed. Message: %s' % result_walking
                else:
                    logging.info('Verify the result for each walking are same.')
                    self.errmsg = self._verify_list_dict_items(sys_info_d_list)
                    
                self.passmsg = 'Continue working works well.'
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _walking_get_sys_basic_info(self, snmp, times):
        '''
        Continue walking to get system basic information.
        '''
        result_walking = ''
        sys_info_d_list = []
        
        logging.info('Continue walking %s times.' % (times,))
        for i in range(1,times+1):
            sys_info_d = sys_info.get_sys_info_by_walking(snmp)
            
            if not sys_info_d:
                result_walking = 'Response is incorrect when do walking in %s time.' % i
                break
            else:
                sys_info_d_list.append(sys_info_d)
            
        return sys_info_d_list, result_walking
    
    def _verify_list_dict_items(self, sys_info_d_list):
        '''
        Verify the item in the list are same.
        '''
        index = 0
        basic_sys_info_d = sys_info_d_list[index]
        
        index += 1
        res_d = {}
        for i in range(index, len(sys_info_d_list)):
            sys_info_d = sys_info_d_list[i]                
            result_dict = sys_info.verify_sys_info(sys_info_d, basic_sys_info_d, 10)
            
            error_list = []
            for value in result_dict.values():
                if value.find('PASS')< 0:                    
                    error_list.append(value)
            
            if error_list:
                res_d.update({i+1: 'FAIL:%s' % (error_list,)})
                
        return res_d