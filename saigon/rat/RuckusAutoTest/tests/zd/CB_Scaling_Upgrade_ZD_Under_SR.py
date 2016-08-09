'''
Description:
Created on 2010-8-5
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import os
import time

from RuckusAutoTest.models import Test
from contrib.download import image_resolver as imgres
from RuckusAutoTest.components.lib import FeatureUpdater
from RuckusAutoTest.common.DialogHandler import (
    BaseDialog,
    DialogManager
    )

class CB_Scaling_Upgrade_ZD_Under_SR(Test):
    
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self._upgrade_zd_under_smart_redundancy(self.zd, self.conf['default'])        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
               
        return self.returnResult('PASS', self.msg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = {'image_file_path': '',
                     'force_upgrade': False,
                     'zd_build_stream':None,  
                     'default':False,
                     'upgrade_from':'active',              
                    }
        self.conf.update(conf)
        self.msg = ''
        self.errmsg = '' 
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
            
        self.zd = self.testbed.components['ZoneDirector']        
        
    
    def _update_feature(self, zd):
        if self.conf['zd_build_stream']:
            FeatureUpdater.FeatureUpdater.notify(zd, self.conf['zd_build_stream'])          
                    
    def _upgrade_zd_under_smart_redundancy(self, default):
        fname = self.conf['image_file_path']
        filetype='^zd3k_(\d+\.){5}ap_(\d+\.){5}img$'
        img_filename = imgres.get_image(fname, filetype = filetype)
        img_path_file = os.path.realpath(img_filename)
        
        if self.upgrade_from == 'active':
            try:                
                self._start_dialog_manger()
                self.active_zd._upgrade_zd(img_path_file, default = default)
                time.sleep(180)
                self._shut_down_dlg_manager()
                self._update_feature(self.active_zd)
                self.active_zd._check_upgrade_sucess(default = default)                
                self.active_zd.refresh()                
                self.active_zd.login()
                self.msg = 'The upgrade process worked successfully'
            except Exception, e:
                self.errmsg = '[Upgrade error]: %s' % e.message
        else:
            try:
                self.standby_zd._upgrade_zd(img_path_file, default = default)
                self._update_feature(self.standby_zd)                            
                self.errmsg = 'ZD can be upgraded from Standby ZD--Incorrect behaver'
            except Exception, e:
                self.msg = 'ZD can NOT be upgraded from Standby ZD--Correct behaver'
                
    def _start_dialog_manger(self):
        self.dlg_manager = DialogManager()

        dlg1 = None
        dlg2 = None

        # Handle IE browser
        if (self.active_zd.conf['browser_type'] == 'ie'):
            dlg1 = BaseDialog("Security Alert", "You are about to view pages over a secure", "OK")
            dlg2 = BaseDialog("Security Alert", "The security certificate was issued by a company", "&Yes")

        # Handle Firefox browser
        elif (self.active_zd.conf['browser_type'] == 'firefox'):
            dlg1 = BaseDialog("Website Certified by an Unknown Authority", "", "", "{ENTER}")
            dlg2 = BaseDialog("Security Error: Domain Name Mismatch", "", "", "{TAB}{TAB}{ENTER}")

        self.dlg_manager.add_dialog(dlg1)
        self.dlg_manager.add_dialog(dlg2)

        # Start dialog manager to manage the two dialogs that we have added
        self.dlg_manager.start()
    
    def _shut_down_dlg_manager(self):
        
        self.dlg_manager.shutdown()             

    
