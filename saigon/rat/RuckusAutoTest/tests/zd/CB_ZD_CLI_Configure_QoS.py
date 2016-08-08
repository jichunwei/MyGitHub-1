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
            - Go to ZD CLI - Under config-sys-qos mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the Global QoS information if changed under AP CLI.

   3. Cleanup:
            - If test case is cleanup, return the default setting for global QoS.

   How it is tested?
"""
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from rat.RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG,\
    INVALID_CMD_MSG

class CB_ZD_CLI_Configure_QoS(Test):
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
                self.carrierbag['default_qos_conf'] = lib.apcli.qosgrp.get_qos(self.ap_cli_list[0])
            
            self.qos_conf = {}
        
        if self.test_conf['cleanup'] and self.carrierbag.has_key('default_qos_conf'):
            self.qos_conf = self.carrierbag['default_qos_conf']
            for key in self.qos_conf.keys():
                #@author: chen.tao since 2014-10-21, to fix ZF-10172
                if type(self.qos_conf[key]) is list: self.qos_conf[key] = ','.join([x for x in self.qos_conf[key]])
    
    def _verify_command_execution(self):
        logging.log_info('Configure Global QoS', 'Execute commands', 'QoS setting: %s' % self.qos_conf)
        try:
            lib.zdcli.qos.config_sys_qos(self.zd_cli, **self.qos_conf)
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
        time.sleep(60) # wait until the setting is apply to all APs
        if not self.test_conf['pass_expected']:
            return # Do not verify in navigate test
        logging.log_info('Configure Global QoS', 'Verifying', 'QoS info under APs CLI')
        
        start_time = time.time()
        while True:
            run_time = time.time() - start_time 
            if run_time > self.test_conf['time_out']: return
            self.errmsg = ''
            for ap in self.ap_cli_list:
                errmsg = ''
                ap_qos_conf = lib.apcli.qosgrp.get_qos(ap)
                for key in self.qos_conf.keys():
                    if not ap_qos_conf.has_key(key):
                        continue
                    #@author: chen.tao since 2014-10-21, to fix ZF-10172
                    if type(ap_qos_conf[key]) is list: ap_qos_conf[key] = ','.join([x for x in ap_qos_conf[key]])
                    if self.qos_conf[key] not in ap_qos_conf[key]:
                        errmsg += 'The value "%s" is "%s" instead of "%s". ' % (key, ap_qos_conf[key], self.qos_conf[key]) 
                if errmsg: self.errmsg += 'AP[%s]: %s' % (ap.ip_addr, errmsg)
            if not self.errmsg:
                break
            else:
                time.sleep(30)

        self.passmsg = self.passmsg + '; the Global QoS setting is applied and shown correctly on all APs'            