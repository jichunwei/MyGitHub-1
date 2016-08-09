'''
Created on Sep 30, 2014

@author: chen tao
'''

import logging
import random
import copy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap
class CB_ZD_CLI_Set_All_AP_LLDP(Test):
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):

        for ap in self.testbed.components['AP']:
            self.set_lldp(ap)
        
        if self.errmsg: 
            if self.negative:
                return self.returnResult('PASS', self.errmsg)
            else:
                return self.returnResult('FAIL', self.errmsg)
        else:
            if self.negative:
                return self.returnResult('FAIL', self.passmsg)
            else:
                return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'ap_tag': '',
                     'lldp_cfg':{},
                     'negative':False,
                     'robust_test':False
                     }
        self.conf.update(conf)
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.negative = self.conf['negative']
        self.ap_cfg = {}

    def set_lldp(self,ap):
        logging.info('Set AP[%s][%s] lldp in ZD CLI'%(ap.ip_addr,ap.base_mac_addr))
        try:
            ap_cfg = copy.deepcopy(self.ap_cfg)
            ap_cfg['mac_addr'] = ap.base_mac_addr
            ap_cfg['lldp'] = self.conf['lldp_cfg']
            if self.conf['lldp_cfg'].get('enable_ports') == 'active_port':
                ap_cfg['lldp']['enable_ports'] = [self.get_ap_active_port(ap)[0]]
            if self.conf['lldp_cfg'].get('enable_ports') == 'all':
                ap_cfg['lldp']['enable_ports'] = self.get_ap_all_port(ap)
            if self.conf['lldp_cfg'].get('disable_ports') == 'active_port':
                ap_cfg['lldp']['disable_ports'] = [self.get_ap_active_port(ap)[0]]
            if self.conf['lldp_cfg'].get('disable_ports') == 'all':
                ap_cfg['lldp']['disable_ports'] = self.get_ap_all_port(ap)

            res, msg = configure_ap.configure_ap(self.zdcli, ap_cfg)
            if res:
                self.passmsg += msg
            
            else:
                self.errmsg += msg
            
        except Exception, ex:
            self.errmsg += ex.message
            
    def get_ap_active_port(self,ap):
        ap_port_dict = ap.get_ap_eth_port_num_dict()
        active_port_list = ap_port_dict['up']
        if not active_port_list: raise Exception("Can not get AP's up eth port!")
        return active_port_list

    def get_ap_inactive_port(self,ap):
        ap_port_dict = ap.get_ap_eth_port_num_dict()
        inactive_port_list = ap_port_dict['down']
        if not inactive_port_list: raise Exception("Can not get AP's down eth port!")
        return inactive_port_list
    
    def get_ap_all_port(self,ap):
        ap_port_dict = ap.get_ap_eth_port_num_dict()
        all_port_list = ap_port_dict['all']
        if not all_port_list: raise Exception("Can not get AP's eth port!")
        return all_port_list