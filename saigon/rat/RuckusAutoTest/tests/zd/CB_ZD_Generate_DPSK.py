# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
Description: This script is used to generate a dynamic PSK by manual or .csv file importing.
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
@since: April 2012
"""

import time
import logging
import os

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import Test_Methods as test


class CB_ZD_Generate_DPSK(Test):
    
    def config(self, conf):
        self._init_test_parameters(conf)        
        
    def test(self):
        self._generate_dpsk()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        if self.conf['negative']:
            return self.returnResult('PASS', self.passmsg)
        
        self._verify_the_generated_dpsk_in_file()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        if self.conf['check_webui']:
            self._verify_the_generated_dpsk_on_zd_webui()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
        if self.conf['check_cli']:
            self._verify_the_generated_dpsk_under_zd_cli()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass
        
    def _init_test_parameters(self, conf):
        self.conf = {'dpsk_conf': {'file_name':None},#@author:yuyanan @2014-7-24
                     'check_webui': True,
                     'check_cli': True,
                     'negative': False}
        
        self.conf.update(conf)     
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
        #@author:yuyanan @since:2014-7-24  optimize: get profile according file name
        if self.conf.get('dpsk_conf') and self.conf.get('dpsk_conf').get('file_name'):
            profile = self._define_psk_batch_file_paths(self.conf.get('dpsk_conf').get('file_name'))
            conf['dpsk_conf']['profile_file'] = profile
            
        
        
    def _define_psk_batch_file_paths(self,file_name):
        working_path = os.getcwd().split('\\rat')[0]
        batches_dir = '\\rat\\RuckusAutoTest\\common\\dpsk_batches\\'
        profile = working_path + batches_dir + file_name
    
        if not os.path.isfile(profile):
            raise Exception('Please check "%s" is not a file' % profile)
        return profile

    def _update_carrier_bag(self):
        if self.carrierbag.get('generated_dpsk_files'):
            self.carrierbag['generated_dpsk_files'].append(self.record_file_path)
        else:
            self.carrierbag['generated_dpsk_files'] = [self.record_file_path]
        
        self.carrierbag['last_generated_dpsks'] = self.dpsk_in_file        
    
    def _generate_dpsk(self):
        try:
            test.dpsk.generate_multiple_dpsk(self.zd, self.conf['dpsk_conf'])
            time.sleep(30)
            self.passmsg = 'Generate the DPSK[%s] successfully. ' % self.conf['dpsk_conf']
            logging.info(self.passmsg)
        except Exception, e:
            msg = 'Fail to generate DPSK: %s' % e.message
            if self.conf['negative']:
                self.passmsg = '[CORRECT BEHAVIOR] %s' % msg
            else:
                self.errmsg = msg
    
    def _verify_the_generated_dpsk_in_file(self):
        res, msg = test.dpsk.verify_dpsk_info_in_record_file(self.zd, self.conf['dpsk_conf'])
        if res == 'PASS':
            self.passmsg += msg
            self.record_file_path = lib.zd.wlan.download_generated_dpsk_record(
                                                self.zd, filename_re = "batch_dpsk_\d{6}_\d{2}_\d{2}.csv",
                                                pause = 3)    
            self.dpsk_in_file = test.dpsk.parse_csv_file(self.record_file_path)            
        else:
            self.errmsg = msg
    
    def _verify_the_generated_dpsk_on_zd_webui(self):
        mapped_key = {'user': 'User Name',
                      'wlans': 'WLAN',
                      'vlan': 'Vlan ID',
                      'mac': 'Mac Address'}
        res, msg = test.dpsk.verify_dpsk_info_on_webui(self.zd, self.dpsk_in_file, mapped_key = mapped_key)
        if res == 'PASS':
            self.passmsg += msg
        else:
            self.errmsg = msg
    
    def _verify_the_generated_dpsk_under_zd_cli(self):
        mapped_key = {'user': 'User Name',
                      #'wlansvc-name': 'WLAN', #Chico, 2015-8-3, ZF-14011, wlansvc-name is removed from XML file
                      'dvlan-id': 'Vlan ID',
                      'mac': 'Mac Address'}
        res, msg = test.dpsk.verify_dpsk_info_under_shell(self.zdcli, self.dpsk_in_file, mapped_key = mapped_key)
        if res == 'PASS':
            self.passmsg += msg
        else:
            self.errmsg = msg