'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to create wlans via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aps_info


class CB_ZD_SNMP_Negative_Input_AP(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_negative_input_ap()        
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
            
    def _update_carrier_bag(self):
        pass

    def _verify_negative_input_ap(self):
        logging.info('Verify negative input for ap config')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            ap_id_mac_mapping = aps_info.get_zd_ap_index_value_mapping(snmp)
            
            if len(ap_id_mac_mapping) > 0:
                ap_mac = ap_id_mac_mapping.values()[0]
            else:
                res_ap_d = {'Error': 'No ap joined ZD.'}
                    
            index = helper.get_dict_key_by_value(ap_id_mac_mapping, ap_mac)
            
            if not index:
                res_ap_d = {'Error': 'No ap for mac addr %s' % ap_mac}
            else:
                res_ap_d = aps_info.update_ap_cfg_one_by_one(snmp, index, aps_info.gen_ap_cfg_negative())
            
            pass_d, fail_d = helper.verify_error_for_negative(res_ap_d)
            
            if pass_d:
                logging.info('Pass information: %s' % pass_d)
            if fail_d:
                logging.warning('Error:' % fail_d)
                self.errmsg = fail_d
            else:                
                self.passmsg = 'Error message is correct for negative input.'
                                    
        except Exception, ex:
            self.errmsg = ex.message