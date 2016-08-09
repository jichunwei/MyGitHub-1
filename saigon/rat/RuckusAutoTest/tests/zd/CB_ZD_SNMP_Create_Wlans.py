'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to create wlans via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan


class CB_ZD_SNMP_Create_Wlans(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._create_wlans()        
        
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
        if self.carrierbag.has_key('create_wlan_cfg_list'):
            self.create_wlans_cfg_list = self.carrierbag['create_wlan_cfg_list']
        else:
            self.create_wlans_cfg_list = self.conf['create_wlan_cfg_list']
            
    def _update_carrier_bag(self):
        self.carrierbag['create_wlan_cfg_dict'] = self.create_wlans_cfg_dict         

    def _create_wlans(self):
        logging.info('Create Wlans via ZD SNMP')
        try:
            new_wlans_cfg_list = self.create_wlans_cfg_list
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            logging.info('Wlan config: %s' % new_wlans_cfg_list)
            wlan_cfg_dict = wlan.create_wlans(snmp, new_wlans_cfg_list)
            self.create_wlans_cfg_dict = wlan_cfg_dict
            
            #Parsing wlan names are not created successfully.            
            new_wlan_names_list = []
            for wlan_cfg in new_wlans_cfg_list:
                new_wlan_names_list.append(wlan_cfg['name'])
            
            created_wlan_names_list = []
            for wlan_cfg in wlan_cfg_dict.values():
                created_wlan_names_list.append(wlan_cfg['name'])
                
            err_wlan_names_list = []
            for wlan_name in new_wlan_names_list:
                if wlan_name not in created_wlan_names_list:
                    err_wlan_names_list.append(wlan_name)
            
            if err_wlan_names_list:
                self.errmsg = "Some wlans are not created successfully: %s" % err_wlan_names_list
            else:
                self.passmsg = 'The wlans are created: %s' % new_wlan_names_list
                                    
        except Exception, ex:
            self.errmsg = ex.message