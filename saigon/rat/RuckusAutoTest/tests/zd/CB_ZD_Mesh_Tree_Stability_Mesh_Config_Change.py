# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Dec 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree are match with expected 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the mesh tree is not changed
            FAIL: If the mesh tree is changed

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Mesh_Tree_Stability_Mesh_Config_Change(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        self._test_change_mesh_configuration()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_on_zd_webui()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_under_zd_cli()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        self._verify_aps_info()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_under_aps_cli()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
        
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'time_out': 180}
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_cli = self.testbed.components['ZoneDirectorCLI']
        self.ap_cli_list = self.testbed.components['AP']
        
        if self.carrierbag.get('expected_aps_info'):
            self.expected_aps_info = self.carrierbag['expected_aps_info']
        else:
            self.expected_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        
        self.carrierbag['default_mesh_conf'] = lib.zdcli.mesh.get_mesh_info(self.zd_cli)
        self.mesh_conf = {'mesh_name': '',
                          'mesh_passphrase': ''}
        if self.conf.get('mesh_conf'):
            self.mesh_conf.update(self.conf['mesh_conf'])
            
        if self.conf.get('cleanup') and self.carrierbag.has_key('default_mesh_conf'):
            self.mesh_conf = self.carrierbag['default_mesh_conf']
            if self.mesh_conf.has_key('mesh_name(essid)'):
                self.mesh_conf['mesh_name'] = self.mesh_conf['mesh_name(essid)']
                self.mesh_conf.pop('mesh_name(essid)')
    
    def _verify_aps_info(self):
        logging.debug('The expected APs info:\n %s' % pformat(self.expected_aps_info))
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        logging.debug('The current APs info: \n %s' % pformat(current_aps_info))
        
        lost_aps = []
        error_aps = []
        for mac_addr in self. expected_aps_info.keys():
            if mac_addr not in current_aps_info.keys():
                lost_aps.append(mac_addr)
                continue
            if current_aps_info[mac_addr]['status'] != self.expected_aps_info[mac_addr]['status']:
                error_aps.append(mac_addr)
                continue
        
        if lost_aps:
            self.errmsg = 'There are APs %s lost.' % lost_aps 
        if error_aps:
            self.errmsg += 'The APs %s have the information is not match with expected' % error_aps 
        
        if self.errmsg:
            return
        
        self.passmsg += '; the current APs info %s \n is match with the expected' % pformat(current_aps_info.keys())
    
    def _test_change_mesh_configuration(self):
        logging.info('Change the mesh configuration to %s' % self.mesh_conf)
        try:
            self.zd.enable_mesh(self.mesh_conf['mesh_name'], self.mesh_conf['mesh_passphrase'])
            self.passmsg = 'Change mesh setting successfully.'
            logging.info('sleep 60')
            time.sleep(60) # wait until the setting is apply to all APs
        except Exception, e:
            self.errmsg = 'Failed to change the mesh setting - %s' % e.message
        
    def _verify_setting_under_zd_cli(self):        
        mesh_cfg_under_zd_cli = lib.zdcli.mesh.get_mesh_info(self.zd_cli)
        logging.info('Verifying Mesh info under ZD CLI %s' % mesh_cfg_under_zd_cli)
        
        mesh_cfg_under_zd_cli['mesh_name'] = mesh_cfg_under_zd_cli['mesh_name(essid)']
        for key in self.mesh_conf.keys():
            if not self.mesh_conf[key]: continue
            if not mesh_cfg_under_zd_cli.has_key(key): continue
            if mesh_cfg_under_zd_cli[key] != self.mesh_conf[key]:
                msg = 'The value of %s is %s instead of %s as expected'
                self.errmsg = msg % (key, mesh_cfg_under_zd_cli[key], self.mesh_conf[key])
                return
        
        self.passmsg = self.passmsg + '; the mesh setting on zd cli is shown correctly'
    
    def _verify_setting_on_zd_webui(self):            
        mesh_cfg_on_zd_webui = lib.zd.mesh.get_mesh_configuration(self.zd)
        logging.info('Verifying Mesh info on ZD WebUI %s' % mesh_cfg_on_zd_webui)
        
        for key in self.mesh_conf.keys():
            if not self.mesh_conf[key]: continue
            if not mesh_cfg_on_zd_webui.has_key(key): continue
            if mesh_cfg_on_zd_webui[key] != self.mesh_conf[key]:
                msg = 'The value of %s is %s instead of %s as expected'
                self.errmsg = msg % (key, mesh_cfg_on_zd_webui[key], self.mesh_conf[key])
                return
        
        self.passmsg = self.passmsg + '; the mesh setting on zd webui is shown correctly'
    
    def _verify_setting_under_aps_cli(self):        
        if 'mesh_name' not in self.mesh_conf.keys() and 'mesh_passphrase' not in self.mesh_conf.keys():
            return # Do not verify any info except 'mesh_name' and 'mesh_passphrase'
        logging.info('Verifying Mesh info under APs CLI')
        
        start_time = time.time()
        while True:
            run_time = time.time() - start_time 
            if run_time > self.conf['time_out']: return
            self.errmsg = ''
            for ap in self.ap_cli_list:
                meshu_info = {}
                meshd_info = {}
                meshu_info['mesh_name'] = lib.apcli.radiogrp.get_ssid(ap, 'meshu')['ssid'][0]
                meshu_info['mesh_passphrase'] = lib.apcli.radiogrp.get_passphrase(ap, 'meshu')['passphrase'][0]
                meshd_info['mesh_name'] = lib.apcli.radiogrp.get_ssid(ap, 'meshd')['ssid'][0]
                meshd_info['mesh_passphrase'] = lib.apcli.radiogrp.get_passphrase(ap, 'meshd')['passphrase'][0]

                for key in self.mesh_conf.keys():
                    if key not in ['mesh_name', 'mesh_passphrase']:
                        continue
                    if not self.mesh_conf[key]: continue
                    if meshd_info[key] != self.mesh_conf[key] or meshu_info[key] != self.mesh_conf[key]:
                        msg = 'After %s seconds, AP[%s] the value of [meshd, meshu] "%s" is %s instead of %s as expected'
                        self.errmsg = self.errmsg + ';' + msg % (run_time, ap.ip_addr, key, [meshd_info[key], meshu_info[key]], self.mesh_conf[key])
                        
            if not self.errmsg:
                break
            else:
                time.sleep(30)

        self.passmsg = self.passmsg + '; the mesh setting is applied and shown correctly on all APs'   
