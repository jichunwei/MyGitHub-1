# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Mar 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector', 'ZoneDirectorCLI', 'RuckusAP'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Getting the syslog setting
        - Verify if the expected info
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_Syslog_Setting(Test):
    required_components = ['ZoneDirector', 'ZoneDirectorCLI', 'RuckusAP']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._verify_expected_syslog_info()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_zd_webui_syslog_info()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_zd_cli_syslog_info()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_ap_syslog_info()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'ap_tag': '',
                     'expected_syslog_cfg': {},
                    }        
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        if self.conf['ap_tag']:
            self.ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']            
        else:
            self.ap = None
        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_expected_syslog_info(self):
        if self.conf['expected_syslog_cfg']:
            logging.info('Expected Syslog configuration: %s' % self.conf['expected_syslog_cfg'])
        else:
            self.errmsg = 'There is not any expected syslog info to verify. Please check!'
    
    def _verify_zd_webui_syslog_info(self): 
        logging.info('Verify the syslog setting on ZD WebUI')
        syslog_info = lib.zd.sys.get_syslog_info(self.zd) 
        logging.info('syslog setting info on WebUI: %s' % syslog_info)
        
        errmsg = ''
        for key in self.conf['expected_syslog_cfg'].keys():
            if syslog_info[key] != self.conf['expected_syslog_cfg'][key] \
            and self.conf['expected_syslog_cfg'][key] is not None:
                msg = ' %s is not "%s" as expected but "%s".'
                errmsg += msg % (key, self.conf['expected_syslog_cfg'][key], syslog_info[key])
        
        if errmsg:
            self.errmsg = '[ZD WebUI][Syslog]' + errmsg
            logging.debug(self.errmsg)
            return
        
        passmsg = ' [ZD WebUI][Syslog] All the info are correct as expected!'
        logging.debug(passmsg)
        
        self.passmsg += passmsg        
    
    def _verify_zd_cli_syslog_info(self):
        logging.info('Verify the syslog setting on ZD CLI')
        syslog_info = lib.zdcli.syslog.get_syslog_config(self.zdcli) 
        logging.info('syslog setting info under CLI: %s' % syslog_info)
        
        errmsg = ''
        for key in self.conf['expected_syslog_cfg'].keys():
            if syslog_info[key] != self.conf['expected_syslog_cfg'][key] \
            and self.conf['expected_syslog_cfg'][key] is not None:
                msg = ' %s is not "%s" as expected but "%s".'
                errmsg += msg % (key, self.conf['expected_syslog_cfg'][key], syslog_info[key])
        
        if errmsg:
            logging.debug(self.errmsg)
            self.errmsg = '[ZD CLI][Syslog]' + errmsg
            return
        
        passmsg = ' [ZD CLI][Syslog] All the info are correct as expected!'
        logging.debug(passmsg)
        
        self.passmsg += passmsg
    
    def _verify_ap_syslog_info(self):
        if not self.ap:
            return
        
        logging.info('Verify the syslog configuration under AP %s' %
                     self.ap.ip_addr)
        ap_syslog_info = self.ap.get_syslog_info()
        logging.info('syslog setting info in ap side: %s' % ap_syslog_info)
        
        if not self.conf['expected_syslog_cfg'].get('enable_remote_syslog'):
            self.conf['expected_syslog_cfg']['remote_syslog_ip'] = ''
            
        if self.conf['expected_syslog_cfg'].get('remote_syslog_ip'):
            if ap_syslog_info['server_ip'] != self.conf['expected_syslog_cfg']['remote_syslog_ip']:
                errmsg = ' The AP syslog server ip is not "%s" as expected but "%s".' 
                self.errmsg += errmsg % (self.conf['expected_syslog_cfg']['remote_syslog_ip'],
                                         ap_syslog_info['server_ip'])
                logging.debug(self.errmsg)
                return
            else:
                self.passmsg += ' The AP syslog server ip is "%s" as expected.' % ap_syslog_info['server_ip']
                
        if self.conf['expected_syslog_cfg'].get('ap_priority_level'):
            if self.conf['expected_syslog_cfg']['ap_priority_level'] is None:
                return
            expected_level = {'emerg': '0', 'alert': '1', 'crit': '2',
                              'err': '3', 'warning': '4', 'notice': '5',
                              'info': '6', 'debug': '7'}[self.conf['expected_syslog_cfg']['ap_priority_level']]
            if ap_syslog_info['level_network'] != expected_level:
                errmsg = ' The AP syslog network level is not "%s" as expected but "%s".' 
                self.errmsg += errmsg % (expected_level,
                                         ap_syslog_info['level_network'])
                logging.debug(self.errmsg)
                return
            else:
                self.passmsg += ' The AP syslog network level is "%s" as expected.' % ap_syslog_info['level_network']


