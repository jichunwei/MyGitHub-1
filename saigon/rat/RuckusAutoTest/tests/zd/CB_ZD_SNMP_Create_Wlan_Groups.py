'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to create wlan groups via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup

class CB_ZD_SNMP_Create_Wlan_Groups(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._create_wlan_groups()       
        
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
        if self.carrierbag.has_key('wlan_group_cfg_list'):
            self.wlan_group_cfg_list = self.carrierbag['wlan_group_cfg_list']
            
    def _update_carrier_bag(self):
        self.carrierbag['snmp_set_wg_cfg_dict'] = self.create_wlan_groups_cfg_dict

    def _create_wlan_groups(self):
        logging.info('Create wlan groups via ZD SNMP')
        try:
            #Wlan config can be passed by parameter or carrierbag.
            if self.conf.has_key('wlan_group_cfg_list'):
                new_wg_cfg_list = self.conf['wlan_group_cfg_list']
            else:
                new_wg_cfg_list = self.wlan_group_cfg_list
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            logging.info('Wlan group config: %s' % new_wg_cfg_list)
            
            wg_cfg_dict = wlangroup.create_wlan_groups(snmp, new_wg_cfg_list)
            self.create_wlan_groups_cfg_dict = wg_cfg_dict
            
            #Parsing wlan names are not created successfully.            
            new_wg_names_list = []
            for wg_cfg in new_wg_cfg_list:
                new_wg_names_list.append(wg_cfg['name'])
            
            created_wg_names_list = []
            for wg_cfg in wg_cfg_dict.values():
                created_wg_names_list.append(wg_cfg['name'])
                
            err_wg_names_list = []
            for wg_name in new_wg_names_list:
                if wg_name not in created_wg_names_list:
                    err_wg_names_list.append(wg_name)
            
            if err_wg_names_list:
                self.errmsg = "Some wlan groups are not created successfully: %s" % err_wg_names_list
            else:
                self.passmsg = 'The wlan groups are created: %s' % new_wg_names_list
                                    
        except Exception, ex:
            self.errmsg = ex.message