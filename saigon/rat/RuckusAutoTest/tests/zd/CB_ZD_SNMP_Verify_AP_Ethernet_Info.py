'''
Description:
    Checking AP Ethernet information by SNMP V2 and V3.
    
Created on 2013-1-20
@author: kevin.tan@ruckuswireless.com
'''
import logging
import re

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_aps_info
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli


class CB_ZD_SNMP_Verify_AP_Ethernet_Info(Test):
    '''
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        if self.conf.has_key('snmp_agent_cfg_v2'):
            #SNMP v2
            snmp_agent_cfg = self.conf['snmp_agent_cfg_v2']
            logging.info("Set SNMP agent V2 with config: %s" % snmp_agent_cfg)
            result, res_dict = config_snmp_agent(self.zdcli, snmp_agent_cfg)
            if not result:
                self.errmsg = 'Config SNMP agent V2 fail. Config: %s, Error: %s' % (snmp_agent_cfg, res_dict)
                return self.returnResult('FAIL', self.errmsg)

            snmp_cfg = self.conf['snmp_cfg_v2']
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))                           
            snmp_v2 = helper.create_snmp(snmp_cfg)
    
            self._verify_ap_ethernet_info(self.active_ap.base_mac_addr, snmp_v2)
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
    
            self._verify_ap_ethernet_info(self.active_ap.base_mac_addr, snmp_v3)
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'Verify ZD Ethernet info by SNMP Agent  V2 and V3 successfully')
        
    def _verify_ap_ethernet_info(self, ap_mac, snmp):
        try:
            logging.info('Get ZD Ethernet information via ZD SNMP.')
                     
            info = cli.show_ap_info_by_mac(self.zdcli, ap_mac)
            port_num = 1
            for index in info['AP']['ID']:
                port_num = len(info['AP']['ID'][index]['LAN Port'])
                break

            for idx in range(0, port_num):
                if idx == 0:
                    if self.conf['port_status'] == 'enable':
                        expect_status = 'up'
                    else:
                        expect_status = 'down'
                else:
                    expect_status = 'down'

                info = wlan_aps_info.get_zd_ap_eth_info_by_mac_and_index(snmp, ap_mac, idx)
                logging.info('SNMP AP port[%s] Ethernet information: %s' % (idx, info))

                if self.conf['interface'] == 'enable':
                    if info['port_id'] != ('%s' % idx):
                        self.errmsg += 'port_id[%s] retrieved from SNMP is invalid, should be %s'  %  (info['port_id'], idx)         
                    if info['if_name'].lower() != ('eth%s' % idx):
                        self.errmsg += 'if_name[%s] retrieved from SNMP is invalid, should be %s'  %  (info['if_name'], ('eth%s' % idx))         
                    if info['mac_addr'] != ap_mac.lower():
                        self.errmsg += 'mac_addr[%s] retrieved from SNMP is invalid, should be %s'  %  (info['mac_addr'], ap_mac)         
                    if expect_status not in info['logical_status'].lower():
                        self.errmsg += 'logical_status[%s] retrieved from SNMP is invalid, should be %s'  %  (info['logical_status'], expect_status)         
                    if expect_status not in info['physical_status'].lower():
                        self.errmsg += 'physical_status[%s] retrieved from SNMP is invalid, should be %s'  %  (info['physical_status'], expect_status)         
                else:
                    if 'No Such Instance currently exists at this OID' not in info['port_id']:
                        self.errmsg += 'port_id[%s] retrieved from SNMP is invalid, should be no such instance'  %  (info['port_id'])         
                    if 'No Such Instance currently exists at this OID' not in info['if_name']:
                        self.errmsg += 'if_name[%s] retrieved from SNMP is invalid, should be no such instance'  %  (info['if_name'])         
                    if 'No Such Instance currently exists at this OID' not in info['mac_addr']:
                        self.errmsg += 'mac_addr[%s] retrieved from SNMP is invalid, should be no such instance'  %  (info['mac_addr'])         
                    if 'No Such Instance currently exists at this OID' not in info['logical_status']:
                        self.errmsg += 'logical_status[%s] retrieved from SNMP is invalid, should be no such instance'  %  (info['logical_status'])         
                    if 'No Such Instance currently exists at this OID' not in info['physical_status']:
                        self.errmsg += 'physical_status[%s] retrieved from SNMP is invalid, should be no such instance'  %  (info['physical_status'])         

            self.passmsg = 'Get system basic information via ZD SNMP successfully.'
            
        except Exception, ex:
            self.errmsg = ex.message

    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.conf = {'port_status': 'enable', 'interface': 'enable'}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        
        self.passmsg = ""
        self.errmsg = ""
        