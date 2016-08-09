'''
Description: This script is used to verify the ZD and GW detection by AP.
@author: an.nguyen@ruckuswireless.com
@since: Feb 2012
'''

import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_ZD_GW_Detection(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verify_zd_detection()        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_gw_detection()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        """
        """
        self.conf = conf
        self.passmsg = ''
        self.errmsg = ''
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
    
    def _verify_zd_detection(self):
        """
        """
        zd_info = lib.apcli.sysgrp.get_director(self.active_ap)['ap_is_under_management_of_zonedirector']
        ipv4_rex = '[0-9]+\.'
        ipv6_rex = '[0-9a-fA-F]+::'
        expect_cmd = ''
        expect_zd_ip = ''
        for i in zd_info:
            if re.search(ipv4_rex, i) and i!= '0.0.0.0':
                expect_cmd = 'arping'
                expect_zd_ip = i
                break
        if not expect_cmd:
            for i in zd_info:
                if re.search(ipv6_rex, i):
                    expect_cmd = 'ndisc6'
                    expect_zd_ip = i
                    break      
        if not expect_cmd:
            self.errmsg = 'Could not detect the ZD information on AP[%s]' % self.active_ap.get_ip_addr()
            return
        
        lib.apcli.shell.set_meshd_option(self.active_ap, 'm', '0xFFFFFFFC')
        aplog = lib.apcli.shell.read_mlog(self.active_ap, expect_cmd)
        logging.debug(aplog)
        
        if not aplog or expect_zd_ip not in aplog:
            self.errmsg = 'There is no "%s" to ZD IP[%s] as expectation on AP[%s]' % (expect_cmd, expect_zd_ip, 
                                                                                      self.active_ap.get_ip_addr()) 
            return
        
        self.passmsg = 'AP[%s] do "%s" to ZD IP[%s] as expected' % (self.active_ap.get_ip_addr(),
                                                                    expect_cmd, expect_zd_ip)
        
        
    def _verify_gw_detection(self):
        """
        """
        ap_ip_info = lib.apcli.sysgrp.get_ip_settings(self.active_ap, 'wan')
        expect_cmd = ''
        expect_gw = ''
        if ap_ip_info.get('ipv4'):
            if ap_ip_info['ipv4']['gateway']:
                expect_cmd = 'arping'
                expect_gw = ap_ip_info['ipv4']['gateway']
        
        if ap_ip_info.get('ipv6') and not expect_cmd:
            if ap_ip_info['ipv6']['default_gateway']:
                expect_cmd = 'ndisc6'
                expect_gw = ap_ip_info['ipv6']['default_gateway']
        
        if not expect_cmd:
            self.errmsg = 'Could not detect the Gateway information on AP[%s]' % self.active_ap.get_ip_addr()
            return
        
        lib.apcli.shell.set_meshd_option(self.active_ap, 'm', '0xFFFFFFFC')
        aplog = lib.apcli.shell.read_mlog(self.active_ap, expect_cmd)
        
        if not aplog or expect_gw not in aplog:
            self.errmsg = 'There is no "%s" to gate way "%s" as expectation on AP[%s]' % (expect_cmd, expect_gw, 
                                                                                          self.active_ap.get_ip_addr()) 
            return
        
        self.passmsg += '; AP[%s] do "%s" to gateway [%s] as expected' % (self.active_ap.get_ip_addr(),
                                                                          expect_cmd, expect_gw)