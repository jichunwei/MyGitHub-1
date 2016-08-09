'''
Created on Sep 30, 2014

@author: chen tao
'''

import logging
import random
import copy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap
class CB_ZD_CLI_Set_AP_LLDP(Test):

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        if self.conf['robust_test']: 
            self.continuous_reset_lldp(self.active_ap)
        else:
            self.set_lldp(self.active_ap)

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
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
        self.ap_cfg = {}
        self.negative = self.conf['negative']

    def continuous_reset_lldp(self,ap):
        logging.info('Set AP[%s][%s] lldp in ZD CLI'%(ap.ip_addr,ap.base_mac_addr))
        reset_times = random.randint(30,50)

        enable_lldp_cfg = copy.deepcopy(self.ap_cfg)
        enable_lldp_cfg['mac_addr'] = ap.base_mac_addr
        enable_lldp_cfg['lldp'] = {}
        enable_lldp_cfg['lldp']['state'] = 'enable'
        disable_lldp_cfg = copy.deepcopy(enable_lldp_cfg)
        disable_lldp_cfg['lldp']['state'] = 'disable'

        for i in range(0,reset_times):
            logging.info('=====Reset lldp %s times, %s times remains.====='%(reset_times,reset_times-i-1))
            res, msg = configure_ap.configure_ap(self.zdcli, enable_lldp_cfg)
            if not res:
                self.errmsg = msg
                break
            res, msg = configure_ap.configure_ap(self.zdcli, disable_lldp_cfg)
            if not res:
                self.errmsg = msg
                break

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
            logging.info('The config is :\n%s'%ap_cfg)
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