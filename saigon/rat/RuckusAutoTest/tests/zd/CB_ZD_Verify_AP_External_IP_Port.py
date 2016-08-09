# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
Description: This test verifies the external ip port information of active ap
@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: May 2012    
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_External_IP_Port(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        self._get_ap_connection_mode()
        self._verify_ap_external_ip_port()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'expected_ext_ip': '',
                     'expected_ext_port': '12223'}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_ap_external_ip_port(self):
        '''
        verify the external ap ip and port
        '''
        monitor_ap_info = lib.zd.ap.get_ap_info_by_mac(self.zd, self.active_ap.base_mac_addr)
        monitor_ap_ip_port = monitor_ap_info['extipport']
        detail_ap_info = lib.zd.aps.get_ap_detail_general_by_mac_addr2(self.zd, self.active_ap.base_mac_addr)
        detail_ap_ip_port = detail_ap_info['external_ip_port']        
        
        errmsg = ''
        logging.info('Verifying the Monitor AP external IP Port %s' % monitor_ap_ip_port)
        if monitor_ap_ip_port != self.expected_ext_ip_port:
            errmsg = 'The external info on Monitor page of AP[%s] is %s instead of %s. '
            errmsg = errmsg % (self.active_ap.ip_addr, monitor_ap_ip_port, self.expected_ext_ip_port)
        
        logging.info('Verifying the Detail AP external IP Port %s' % monitor_ap_ip_port)
        if detail_ap_ip_port != self.expected_ext_ip_port:
            errmsg += 'The external info on detail page of AP[%s] is %s instead of %s.'
            errmsg = errmsg % (self.active_ap.ip_addr, detail_ap_ip_port, self.expected_ext_ip_port)
        if errmsg:
            self.errmsg = errmsg
            logging.info('[FAIL]: %s' % self.errmsg)
            return
        
        msg = 'The external ip port info of AP[%s] is same as expected %s'
        self.passmsg = msg % (self.active_ap.ip_addr, self.expected_ext_ip_port)
        logging.info(self.passmsg)        
            
    def _get_ap_connection_mode(self):
        '''
        Get the AP connection mode and define the expected information to verify
        '''
        ap_status_info = lib.zd.aps.get_ap_detail_info_by_mac_addr(self.zd, self.active_ap.base_mac_addr)
        logging.info(ap_status_info['tunnel_mode'])
        if 'l2' in ap_status_info['tunnel_mode'].lower():
            self.expected_ext_ip_port = ''
        elif 'l3' in ap_status_info['tunnel_mode'].lower():
            if self.conf['expected_ext_ip']:
                self.expected_ext_ip_port = '%s:%s' % (self.conf['expected_ext_ip'], self.conf['expected_ext_port'])
            else:
                self.expected_ext_ip_port = '%s:%s' % (self.active_ap.ip_addr, self.conf['expected_ext_port'])
        msg = 'AP[%s] connected to ZD under %s mode - the expected external ap_ip port is %s'
        msg = msg % (self.active_ap.base_mac_addr, ap_status_info['tunnel_mode'], self.expected_ext_ip_port)
        logging.info(msg)
            