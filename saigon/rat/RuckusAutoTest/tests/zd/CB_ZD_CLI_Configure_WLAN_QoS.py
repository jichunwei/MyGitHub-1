# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
            - Prepare a testbed with ZD and APs under ZD control.
   2. Test:
            - Go to ZD CLI - Under config-wlan mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the WLAN QoS information if changed under AP CLI.

   3. Cleanup:
            - If test case is cleanup, return the default setting for WLAN QoS.

   How it is tested?
"""
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from rat.RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG,\
    INVALID_CMD_MSG

class CB_ZD_CLI_Configure_WLAN_QoS(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'qos_conf': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        if self.test_conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        
        self._verify_command_execution()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_under_aps_cli()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.qos_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180}
        
        if conf.has_key('qos_conf'):
            self.qos_conf = conf['qos_conf']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_cli = self.testbed.components['ZoneDirectorCLI']
        self.ap_cli_list = self.testbed.components['AP']

        self.errmsg = ''
        self.passmsg = ''
        
        if self.test_conf['init_env']:
            if self.ap_cli_list:
                ap = self.ap_cli_list[0]
                if self.qos_conf.get('wlan'):
                    try:
                        wlan_if = ap.ssid_to_wlan_if(self.qos_conf['wlan'])
                        if not wlan_if:
                            wlan_if = None
                    except:
                        self.zd.remove_all_wlan_group()
                        self.zd.remove_all_wlan()
                        lib.zdcli.set_wlan.create_wlan(self.zd_cli, {'name': self.qos_conf['wlan'],
                                                                     'ssid': self.qos_conf['wlan']})
                        wlan_if = ap.ssid_to_wlan_if(self.qos_conf['wlan'])
                else:
                    wlan_if = None
                self.carrierbag['default_wlan_qos_conf'] = ap.get_qos_cfg_option(wlan_if)
                self.carrierbag['default_wlan_qos_conf'].update({'wlan': self.qos_conf['wlan']})
            
            self.qos_conf = {}
        
        if self.test_conf['cleanup'] and self.carrierbag.has_key('default_wlan_qos_conf'):
            self.qos_conf = self.carrierbag['default_wlan_qos_conf']
    
    def _verify_command_execution(self):
        logging.log_info('Configure WLAN QoS', 'Execute commands', 'QoS setting: %s' % self.qos_conf)
        try:
            lib.zdcli.qos.config_wlan_qos(self.zd_cli, **self.qos_conf)
            time.sleep(5) #waiting for the setting is applied
            self.passmsg = 'The configure set %s is configured successfully' % self.qos_conf
        except Exception, e:
            self._verify_exception_msg(e)
    
    def _verify_exception_msg(self, e):
        if INVALID_CMD_MSG in e.message:
            msg = '[INVALID COMMAND] %s' % e.message
            if self.test_conf['pass_expected']:
                self.errmsg = msg
            else:
                self.passmsg = '[CORRECT BEHAVIOR]%s' % msg
            return
           
        if INCOMPLETE_CMD_MSG in e.message:
            msg = '[INCOMPLETE COMMAND] %s' % e.message
            if self.test_conf['pass_expected']:
                self.errmsg = msg
            else:
                self.passmsg = '[CORRECT BEHAVIOR]%s' % msg
            return
        
        raise Exception, e
    
    def _verify_setting_under_aps_cli(self):
        time.sleep(60) # wait until the seeting is apply to all APs
        if not self.test_conf['pass_expected']:
            return # Do not verify in navigate test
        logging.log_info('Configure WLAN QoS', 'Verifying', 'WLAN[%s] QoS info under APs CLI' % self.qos_conf.get('wlan'))
       
        start_time = time.time()
        while True:
            run_time = time.time() - start_time 
            if run_time > self.test_conf['time_out']: return
            self.errmsg = ''
            errmsg = ''
            for ap in self.ap_cli_list:
                ap_qos_conf = ap.get_qos_cfg_option(ap.ssid_to_wlan_if(self.qos_conf.get('wlan')))
                for key in self.qos_conf.keys():
                    if not ap_qos_conf.has_key(key):
                        continue
                    if ap_qos_conf[key].lower() != self.qos_conf[key].lower():
                        errmsg += 'The value "%s" is "%s" instead of "%s". ' % (key, ap_qos_conf[key], self.qos_conf[key]) 
                if errmsg: self.errmsg += 'AP[%s] - WLAN[%s]: %s' % (ap.ip_addr, self.qos_conf.get('wlan'), errmsg)
            if not self.errmsg:
                break
            else:
                time.sleep(30)

        self.passmsg = self.passmsg + '; the qos setting for WLAN %s is applied and shown correctly on all APs' % self.qos_conf.get('wlan')         