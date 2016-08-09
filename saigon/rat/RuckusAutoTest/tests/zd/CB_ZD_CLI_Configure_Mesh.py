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
            - Go to ZD CLI - Under config-mesh mode, execute the setting commands.
            - Make sure the command is existed and be used without any issue.
            - Verify the setting is save on ZD, by check mesh info by using command "show mesh info"
            - Verify the new setting is show correctly on the ZD WebUI
            - Verify the mesh ssid/passphrase if changed under AP CLI.

   3. Cleanup:
            - If test case is cleanup, return the default setting for mesh.

   How it is tested?
"""
import time
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib
from rat.RuckusAutoTest.components.lib.apcli.cli_regex import INCOMPLETE_CMD_MSG,\
    INVALID_CMD_MSG

class CB_ZD_CLI_Configure_Mesh(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'mesh_conf': ''}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        if self.test_conf['init_env']:
            return self.returnResult('PASS', 'Testbed is ready for the test.')
        
        self._verify_command_execution()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_on_zd_webui()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_under_zd_cli()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._verify_setting_under_aps_cli()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.mesh_conf = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180}
        
        if conf.has_key('mesh_conf'):
            self.mesh_conf = conf['mesh_conf']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_cli = self.testbed.components['ZoneDirectorCLI']
        self.ap_cli_list = self.testbed.components['AP']

        self.errmsg = ''
        self.passmsg = ''
        
        if self.test_conf['init_env']:
            self.carrierbag['default_mesh_conf'] = lib.zdcli.mesh.get_mesh_info(self.zd_cli)
            self.mesh_conf = {}
        
        if self.test_conf['cleanup'] and self.carrierbag.has_key('default_mesh_conf'):
            self.mesh_conf = self.carrierbag['default_mesh_conf']
            if self.mesh_conf.has_key('mesh_name(essid)'):
                self.mesh_conf['mesh_name'] = self.mesh_conf['mesh_name(essid)']
                self.mesh_conf.pop('mesh_name(essid)')

    def _verify_command_execution(self):
        if self.mesh_conf.has_key('mesh_hop_detection') and type(self.mesh_conf['mesh_hop_detection']) is dict:
            self.mesh_conf['mesh_hop_detection'] = copy.copy(self.mesh_conf['mesh_hop_detection']['Status'])
        if self.mesh_conf.has_key('mesh_downlinks_detection') and type(self.mesh_conf['mesh_downlinks_detection']) is dict:
            self.mesh_conf['mesh_downlinks_detection'] = copy.copy(self.mesh_conf['mesh_downlinks_detection']['Status'])
        logging.log_info('Configure Mesh', 'Execute commands', 'Mesh setting: %s' % self.mesh_conf)
        try:
            lib.zdcli.mesh.config_mesh(self.zd_cli, **self.mesh_conf)
            
            time.sleep(5) #waiting for the setting is applied
            self.passmsg = 'The setting "%s" is executed successfully' % self.mesh_conf
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

    def _verify_setting_under_zd_cli(self):        
        if not self.test_conf['pass_expected']:
            return # Do not verify in navigate test       
        
        mesh_cfg_under_zd_cli = lib.zdcli.mesh.get_mesh_info(self.zd_cli)
        logging.log_info('Configure Mesh', 'Verifying', 'Mesh info under ZD CLI %s' % mesh_cfg_under_zd_cli)
        
        mesh_cfg_under_zd_cli['mesh_name'] = mesh_cfg_under_zd_cli['mesh_name(essid)']
        for key in self.mesh_conf.keys():
            if not mesh_cfg_under_zd_cli.has_key(key): continue
            if key == "mesh_status" : continue
            if mesh_cfg_under_zd_cli[key] != self.mesh_conf[key]:
                msg = 'The value of %s is %s instead of %s as expected'
                self.errmsg = msg % (key, mesh_cfg_under_zd_cli[key], self.mesh_conf[key])
                return
        
        self.passmsg = self.passmsg + '; the mesh setting on zd cli is shown correctly'

    
    def _verify_setting_on_zd_webui(self):        
        if not self.test_conf['pass_expected']:
            return # Do not verify in navigate test
                
        mesh_cfg_on_zd_webui = lib.zd.mesh.get_mesh_configuration(self.zd)
        logging.log_info('Configure Mesh', 'Verifying', 'Mesh info on ZD WebUI %s' % mesh_cfg_on_zd_webui)
        
        mesh_conf_u_dict = copy.deepcopy(self.mesh_conf)
        if mesh_conf_u_dict.has_key('mesh_hop_detection') and type(mesh_conf_u_dict['mesh_hop_detection']) is dict:
            mesh_conf_u_dict['mesh_hop_detection'] = copy.copy(mesh_conf_u_dict['mesh_hop_detection']['Status'])
        if mesh_conf_u_dict.has_key('mesh_downlinks_detection') and type(mesh_conf_u_dict['mesh_downlinks_detection']) is dict:
            mesh_conf_u_dict['mesh_downlinks_detection'] = copy.copy(mesh_conf_u_dict['mesh_downlinks_detection']['Status'])
        
        for key in mesh_conf_u_dict.keys():
            if not mesh_cfg_on_zd_webui.has_key(key): continue
            if key == "mesh_status" : continue
            if mesh_cfg_on_zd_webui[key] != mesh_conf_u_dict[key]:
                msg = 'The value of %s is %s instead of %s as expected'
                self.errmsg = msg % (key, mesh_cfg_on_zd_webui[key], mesh_conf_u_dict[key])
                return
        
        self.passmsg = self.passmsg + '; the mesh setting on zd webui is shown correctly'
    
    def _verify_setting_under_aps_cli(self):
        time.sleep(60) # wait until the seeting is apply to all APs
        if not self.test_conf['pass_expected']:
            return # Do not verify in navigate test
        if 'mesh_name' not in self.mesh_conf.keys() and 'mesh_passphrase' not in self.mesh_conf.keys():
            return # Do not verify any info except 'mesh_name' and 'mesh_passphrase'
        logging.log_info('Configure Mesh', 'Verifying', 'Mesh info under APs CLI')
        
        start_time = time.time()
        while True:
            run_time = time.time() - start_time 
            if run_time > self.test_conf['time_out']: return
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
                    if meshd_info[key] != self.mesh_conf[key] or meshu_info[key] != self.mesh_conf[key]:
                        msg = 'After %s seconds, AP[%s] the value of [meshd, meshu] "%s" is %s instead of %s as expected'
                        self.errmsg = self.errmsg + ';' + msg % (run_time, ap.ip_addr, key, [meshd_info[key], meshu_info[key]], self.mesh_conf[key])
                        
            if not self.errmsg:
                break
            else:
                time.sleep(30)

        self.passmsg = self.passmsg + '; the mesh setting is applied and shown correctly on all APs'            