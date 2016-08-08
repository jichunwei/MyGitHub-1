# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)
    
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components.RuckusAP import RuckusAP


class CB_ZD_Verify_AP_Versions(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        self._verify_ap_version()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('zd_support_ap_versions'):
            self.zd_support_ap_versions = self.carrierbag['zd_support_ap_versions']
    
    def _update_carrier_bag(self):
        pass

    def _verify_ap_version(self):
        '''
        Get expected versions for ap.
        '''
        try:
            ap_cli = None
            logging.info('Get AP config from ZD')
            default_ap_cli_cfg = {'ip_addr' : '192.168.0.1',
                                  'username': 'admin',
                                  'password': 'admin',
                                  'port'    : 23,
                                  'telnet'  : True,
                                  'timeout' : 360, # sec
                                  }
            
            aps_list = self.zd.get_all_ap_info()

            if self.conf.has_key('expect_aps_version'):
                expect_aps_version = self.conf['expect_aps_version']
            else:
                expect_aps_version = self.zd_support_ap_versions
            
            err_d= {}
            
            for ap_cfg in aps_list:
                ip_addr = ap_cfg['ip_addr']
                mac_addr = ap_cfg['mac']
                model = ap_cfg['model']
                
                ap_cli_cfg = {}
                ap_cli_cfg.update(default_ap_cli_cfg)
                ap_cli_cfg['ip_addr'] = ip_addr
                #ap_cli_cfg['model'] = model
                
                logging.info('Verify AP firmware version for %s[%s]' % (model, ip_addr))
                ap_cli = tconfig.get_testbed_active_ap(self.testbed, mac_addr)
                #ap_cli = RuckusAP(ap_cli_cfg)
                
                if expect_aps_version.has_key(model):
                    expect_fw_version = expect_aps_version[model]
                else:
                    raise Exception("AP model is not supported by ZD: %s" % (model,))
                
                res_ap = self._verify_ap_fw_version(ap_cli, ap_cli_cfg, expect_fw_version)
                
                if res_ap:
                    key = '%s[IP:%s]' % (model, ip_addr)
                    err_d[key] = res_ap
            
            if err_d:
                self.errmsg = err_d
                
            self.passmsg = 'All AP versions are correct.'
        except Exception, ex:
            self.errmsg = ex.message
        
        finally:
            pass
            '''
            if ap_cli:
                ap_cli.close()
                del(ap_cli)
            '''
            
    def _verify_ap_fw_version(self, ap_cli, ap_cli_cfg, expect_fw_version):
        '''
        This version is to make sure AP fw version is the expected one after
        upgrading/restoring
        '''
        err_msg = ''
        cur_version = ap_cli.get_version().strip()
        expected_version = expect_fw_version
        logging.info('Current version: %s; Expected version: %s' % (cur_version, expected_version))
        
        if expected_version == cur_version:
            pass_msg = 'The AP was upgraded to version %s successfully.' % (expected_version)
            logging.info(pass_msg)        
        else:
            err_msg = 'The AP was not upgraded to version %s successfully. Expected Version = %s, Actual Version = %s'\
                        % (expected_version, expected_version, cur_version)        
            logging.warning(err_msg)
            
        return err_msg