'''
Description:
Created on 2010-8-6
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging
import time
import os

from RuckusAutoTest.models import Test
from contrib.download import image_resolver as imgres
from RuckusAutoTest.components.lib import FeatureUpdater
from RuckusAutoTest.common.DialogHandler import (
    BaseDialog,
    DialogManager
    )


class CB_Scaling_Downgrade_ZD_Under_SM(Test):
    '''
    Downgrade ZoneDirector from High Version[9.x] to low version[8.2FCS] under smart redundancy.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._downgrade_from_active_zd(default = self.conf['default'], )
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        passmsg.append(self.passmsg)
        
        self._downgrade_from_standby_zd(default = self.conf['default'])
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        passmsg.append(self.passmsg)
         
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        if self.carrierbag.has_key('image_file_path'):
            self.image_file_path = self.carrierbag['image_file_path']
    
    
    def _update_carrier_bag(self):
        self.carrierbag['zd1'] = self.active_zd
        self.carrierbag['zd2'] = self.standby_zd
        
        
    def _init_test_params(self, conf):
        self.conf = dict(image_file_path = '',
                         force_upgrade = True,
                         zd_build_stream = None,
                         default = False,
                         new_conf = {'wireless1_enabled':True,
                                     'dhcp_enabled':True}                          
                         )
        self.conf.update(conf)
        self.image_file_path = self.conf['image_file_path']
        self.new_conf = self.conf['new_conf']
        self.errmsg = ''
        self.passmsg = ''
    
    def _update_feature(self, zd):
        if self.conf['zd_build_stream']:
            FeatureUpdater.FeatureUpdater.notify(zd, self.conf['zd_build_stream'])
    
    
    def _downgrade_from_active_zd(self, default = False, wait_for_time = 180):
        fname = self.image_file_path
        filetype='^zd3k_(\d+\.){5}ap_(\d+\.){5}img$'
        img_filename = imgres.get_image(fname, filetype = filetype)
        img_path_file = os.path.realpath(img_filename)
                
        try:                
            self._start_dialog_manger()
            self.active_zd._upgrade_zd(img_path_file, default = default)
            time.sleep(wait_for_time)
            self._shut_down_dlg_manager()
            self._update_feature(self.active_zd)
            self.active_zd._check_upgrade_sucess(default = default, new_conf = self.new_conf)                
            self.active_zd.refresh()                
            self.active_zd.login()
            self.passmsg = 'The active zd upgrade process worked successfully'
            logging.info(self.passmsg)
            
        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message
    
    
    def _downgrade_from_standby_zd(self, default = False):
        try:
            self._update_feature(self.standby_zd)        
            if default:
                self.standby_zd._setup_wizard_cfg({}, new_conf = self.new_conf)
                self.standby_zd.logout()            
            
            self.standby_zd.refresh()
            self.standby_zd.login()
            self.passmsg = 'The standby zd upgrade process worked successfully'
            logging.info(self.passmsg)
        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message
                
                
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
                    