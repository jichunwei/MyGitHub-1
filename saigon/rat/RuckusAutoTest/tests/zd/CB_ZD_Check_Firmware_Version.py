'''
Created on 2010-7-3

@author: cherry.cheng@ruckuswireless.com
'''
#import os
import re
#import time
import logging

from RuckusAutoTest.models import Test
from contrib.download import image_resolver as imgres

class CB_ZD_Check_Firmware_Version(Test):
    '''
    Check the ZD's version, if zd's version is the same as expected, return PASS
    
    else return FAIL
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._check_version()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)    
    
    def cleanup(self):
        pass     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.conf = {}
                
        self.conf.update(conf)     
        
        self.zd = self.testbed.components['ZoneDirector']
        
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
        
    def _update_carrier_bag(self):
        pass
        
    def _check_version(self):
        try:
            self.passmsg = ''
            if self.conf.has_key('expect_version'):
                self.expect_version = self.conf['expect_version']
            elif self.conf.has_key('image_file_path'):
                self.expect_version = self._get_version_from_image_file(self.conf['image_file_path'])
            
            logging.info('Login ZD and verify firmware version')
            self.zd.refresh()
            self.zd.login()
            self.zd.navigate_to(self.zd.ADMIN,self.zd.ADMIN_UPGRADE)
            version = self.zd._get_version()
            current_version = version['version']
            if current_version == self.expect_version:
                self.passmsg = 'The current version and the expect version are same: %s' % current_version
            else:
                self.errmsg = 'The current version %s was not the expect version %s' % (current_version, self.expect_version)
                
            self.passmsg = 'The current version and the expect version are same: %s' % current_version
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _get_version_from_image_file(self, image_file_path):
        '''
        Get firmware version from image file. 
        Input: .tar.gz
        (zd1k_9.2.0.99.651.ap_9.2.0.99.698.img)
        Output: 9.2.0.0.99.651
        '''
        ptn = 'zd.+_(?P<version>.+)\.ap_.+\.img'
        fw_img_full_path = imgres.get_image(image_file_path, filetype = ptn)
        
        fw_img_file = fw_img_full_path.split('/')[-1]
        matcher = re.compile(ptn,re.I).match(fw_img_file)
        if matcher:
            fw_version = matcher.groupdict()['version']
            return fw_version
        else:
            raise Exception("Can't get version from image file path [%s]" % image_file_path)
        