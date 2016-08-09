'''
Created on 2010-6-21

@author: louis.lou@ruckuswireless.com
'''
import os
import re
#import time
import logging
import time #Chico, 2014-8-14, ZF-9675 sync upgrade codes from P4 
from RuckusAutoTest.models import Test
from contrib.download import image_resolver as imgres

class CB_ZD_SR_Single_Upgrade(Test):
    '''
    Upgrade when Smart Redundancy was enabled
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.upgrade_single_zd(self.zd1)
        self.upgrade_single_zd(self.zd2)
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
       
        return ('PASS', self.msg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = {'image_file_path': '',
                     'force_upgrade': False,
                    }
        
        self.conf.update(conf)
        self.msg = ''
        self.errmsg = ''
#        self.upgrade_from = self.conf['upgrade_from']
        
#        self.active_zd = self.carrierbag['active_zd']
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
        self.filetype='^zd3k_(\d+\.){5}ap_(\d+\.){5}img$'
        
        if self.conf.has_key('build') and self.conf['build']=='base':
            self.conf['image_file_path'] = self.carrierbag['base_build_file']
        else:
            self.conf['image_file_path'] = self.carrierbag['target_build_file']
        
    def upgrade_single_zd(self,zd):
        fname = self.conf['image_file_path']
        
        # see the image is the 'img' file or the 'gz' file
        file=fname.split('\\')[-1]
        img_typy_re = "img$"
        match_obj_img = re.search(img_typy_re, file)
        if match_obj_img:
            img_filename = file
        else:    
            img_filename = imgres.get_image(fname, filetype=self.filetype)
        #Chico, make sure self.conf['image_file_path'] is absolute path
        #img_path_file = os.path.realpath(img_filename)
        img_path_file = fname
        #Chico, make sure self.conf['image_file_path'] is absolute path
        
        try:
            #zd._upgrade_zd(img_path_file)
            #zd._check_upgrade_sucess()
            zd.upgrade_sw(img_path_file)
            zd.login()
            self.msg = 'The upgrade process worked successfully'
            #Chico, 2014-8-14, ZF-9675 sync upgrade codes from P4 
            time.sleep(120)
            #Chico, 2014-8-14, ZF-9675 sync upgrade codes from P4 
        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message
   
