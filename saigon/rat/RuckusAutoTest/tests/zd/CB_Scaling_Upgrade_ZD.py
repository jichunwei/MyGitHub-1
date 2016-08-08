'''
Created on 2010-6-21

@author: louis.lou@ruckuswireless.com
'''
import os
import logging
from RuckusAutoTest.models import Test
from contrib.download import image_resolver as imgres
from RuckusAutoTest.components.lib import FeatureUpdater
from RuckusAutoTest.common.sshclient import sshclient
import re
#from RuckusAutoTest.components import (    
#    create_zd_cli_by_ip_addr,
#    )

class CB_Scaling_Upgrade_ZD(Test):
    '''
    Upgrade ZD when scaling enable
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self._upgrade_zd(self.zd,self.default)  
        self._check_upgrade_succ(self.default)      
        
        #reconnect zdcli
        if self.carrierbag.has_key('active_zd_cli'):
            try:
                self.zdcli2.do_shell_cmd('')
            except:
                self.zdcli2.zdcli = sshclient(self.zdcli2.ip_addr, self.zdcli2.port,'admin','admin')
                self.zdcli2.login()
                
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login() 
            
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
               
        return self.returnResult('PASS', self.msg)
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = {'image_file_path': '',
                     'force_upgrade': False,
                     'zd_build_stream':None,                  
                     'default':False,              
                    }
        self.conf.update(conf)
        self.msg = ''
        self.errmsg = '' 
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
            
        if self.conf.has_key('build') and self.conf['build']=='base':
            self.conf['image_file_path'] = self.carrierbag['base_build_file']
            self.conf['zd_build_stream'] = self.carrierbag['base_build_stream'].split('_')[1]
        else:
            self.conf['image_file_path'] = self.carrierbag['target_build_file']
            self.conf['zd_build_stream'] = self.carrierbag['target_build_stream'].split('_')[1]
            
        
        logging.info('upgrade img is :%s' % self.conf['image_file_path'])
            
        if self.conf.has_key('default') and self.conf['default']==True:
            self.default=True
        else:
            self.default=False
            
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.testbed.components.has_key('ZoneDirectorCLI'):
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
            
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        if self.carrierbag.has_key('active_zd_cli'):
            self.zdcli = self.carrierbag['active_zd_cli']
            self.zdcli2=self.carrierbag['standby_zd_cli']

            
        if self.conf.has_key('zd'):
            self.zd = self.carrierbag[self.conf['zd']]
        if self.conf.has_key('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
    def _upgrade_zd(self, zd,default = False):
        fname = self.conf['image_file_path']
        file=fname.split('\\')[-1]
#        filetype='^zd3k_(\d+\.){5}ap_(\d+\.){5}img$'
#        match_obj_img = re.search(filetype, file)
#        if match_obj_img:#img file
        if '.img' in file:#img file
            img_filename=file
        else:#tar.gz file
            img_filename = imgres.get_image(fname)
        img_path_file = os.path.realpath(img_filename)    
        logging.info('zd will upgrade by img %s'%img_path_file)            
        try:
            zd._upgrade_zd(img_path_file,default)
            logging.info('zd is upgrading')
            if self.conf['zd_build_stream']:
                FeatureUpdater.FeatureUpdater.notify(zd, self.conf['zd_build_stream'])            

        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message
            
    def _check_upgrade_succ(self,default = False):               
        try:
            self.zd._check_upgrade_sucess(default = default)
            logging.info('check zd upgrade succ end')
            try:
                self.zd.refresh()
            except:
                pass
            self.zd.login()
            self.msg = 'The upgrade process worked successfully,'
            logging.info(self.msg )

        except Exception, e:
            self.errmsg = '[Upgrade error]: %s' % e.message
