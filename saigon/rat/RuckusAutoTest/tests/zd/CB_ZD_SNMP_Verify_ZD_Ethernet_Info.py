'''
Description:
    Checking ZD Ethernet information by SNMP V2 and V3.
    
Created on 2013-1-20
@author: kevin.tan@ruckuswireless.com
'''
import logging
import re

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.snmp.zd import sys_info


class CB_ZD_SNMP_Verify_ZD_Ethernet_Info(Test):
    '''
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        self.zd_mac = self.zd.mac_addr

        if self.conf.has_key('snmp_agent_cfg_v2'):
            #SNMP v2
            snmp_agent_cfg = self.conf['snmp_agent_cfg_v2']
            logging.info("Set SNMP agent V2 with config: %s" % snmp_agent_cfg)
            result, res_dict = config_snmp_agent(self.zdcli, snmp_agent_cfg)
            
            if not result:
                self.errmsg = 'Config snmp agent V2 fail. Config: %s, Error: %s' % (snmp_agent_cfg, res_dict)
                return self.returnResult('FAIL', self.errmsg)

            snmp_cfg = self.conf['snmp_cfg_v2']
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))                           
            snmp_v2 = helper.create_snmp(snmp_cfg)
    
            self._verify_zd_ethernet_info(snmp_v2)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)

        if self.conf.has_key('snmp_agent_cfg_v3'):
            #SNMP v3
            snmp_agent_cfg = self.conf['snmp_agent_cfg_v3']
            logging.info("Set SNMP agent V3 with config: %s" % snmp_agent_cfg)
            result, res_dict = config_snmp_agent(self.zdcli, snmp_agent_cfg)
            
            if not result:
                self.errmsg = 'Config SNMP agent V3 fail. Config: %s, Error: %s' % (snmp_agent_cfg, res_dict)
                return self.returnResult('FAIL', self.errmsg)

            snmp_cfg = self.conf['snmp_cfg_v3']
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))                           
            snmp_v3 = helper.create_snmp(snmp_cfg)
    
            self._verify_zd_ethernet_info(snmp_v3)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', 'Verify ZD Ethernet info by SNMP Agent  V2 and V3 successfully')

    def _verify_zd_ethernet_info(self, snmp):
        try:
            logging.info('Get ZD Ethernet information via ZD SNMP.')
                     
            #index 1
            info = sys_info.get_ethernet_info(snmp, 1)
            logging.info('SNMP V2 ZD Ethernet port 1 information: %s' % info)
            if info['eth_idx'] != '1':
                self.errmsg += 'eth_idx[%s] retrieved from SNMP is invalid, should be 1'  %  info['eth_idx']         
            if info['eth_name'].lower() != 'eth0':
                self.errmsg += 'eth_name[%s] retrieved from SNMP is invalid, should be eth0'  %  info['eth_name']         
            if 'up' not in info['eth_status'].lower():
                self.errmsg += 'eth_status[%s] retrieved from SNMP is invalid, should be up'  %  info['eth_status']         
            if info['mac_addr'] != self.zd_mac.lower():
                self.errmsg += 'mac_addr[%s] retrieved from SNMP is invalid, should be %s'  %  (info['mac_addr'], self.zd_mac)         
            if info['eth_rx_pkts'] == '0':
                self.errmsg += 'eth_rx_pkts[%s] retrieved from SNMP is invalid'  %  info['eth_rx_pkts']         
            if info['eth_tx_pkts'] == '0':
                self.errmsg += 'eth_tx_pkts[%s] retrieved from SNMP is invalid'  %  info['eth_tx_pkts']         
            if info['eth_rx_bytes'] == '0':
                self.errmsg += 'eth_rx_bytes[%s] retrieved from SNMP is invalid'  %  info['eth_rx_bytes']         
            if info['eth_tx_bytes'] == '0':
                self.errmsg += 'eth_rx_bytes[%s] retrieved from SNMP is invalid'  %  info['eth_rx_bytes']         
            
            #index 2
            info = sys_info.get_ethernet_info(snmp, 2)
            logging.info('SNMP V3 ZD Ethernet port 2 information: %s' % info)
            if info['eth_idx'] != '2':
                self.errmsg += 'eth_idx[%s] retrieved from SNMP is invalid, should be 1'  %  info['eth_idx']         
            if info['eth_name'].lower() != 'eth1':
                self.errmsg += 'eth_name[%s] retrieved from SNMP is invalid, should be eth1'  %  info['eth_name']         
            if 'up' in info['eth_status'].lower():
                self.errmsg += 'eth_status[%s] retrieved from SNMP is invalid, should be down'  %  info['eth_status']         
            if info['eth_rx_pkts'] != '0':
                self.errmsg += 'eth_rx_pkts[%s] retrieved from SNMP is invalid, should be 0'  %  info['eth_rx_pkts']         
            if info['eth_tx_pkts'] != '0':
                self.errmsg += 'eth_tx_pkts[%s] retrieved from SNMP is invalid, should be 0'  %  info['eth_tx_pkts']         
            if info['eth_rx_bytes'] != '0':
                self.errmsg += 'eth_rx_bytes[%s] retrieved from SNMP is invalid, should be 0'  %  info['eth_rx_bytes']         
            if info['eth_tx_bytes'] != '0':
                self.errmsg += 'eth_rx_bytes[%s] retrieved from SNMP is invalid, should be 0'  %  info['eth_rx_bytes']         

            logging.info('Get ZD Ethernet all ports information successfully by SNMP V2 and V3')

        except Exception, ex:
            self.errmsg = ex.message
            
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'port_status': 'enable'}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.passmsg = ""
        self.errmsg = ""
        