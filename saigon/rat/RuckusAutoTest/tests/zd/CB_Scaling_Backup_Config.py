'''
Description:
Created on 2010-9-28
@author: cwang@ruckuswireless.com 
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import admin_backup_restore_zd as bk
from RuckusAutoTest.common import lib_Constant as constant

#from RuckusAutoTest.components.lib.zd import control_zd 

class CB_Scaling_Backup_Config(Test):
    '''
    Backup ZD's configuration.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        self.bak_file_path = None
        try:
            self.bak_file_path = self._backup(self.zd, self.filename)
        except Exception, e:
            logging.debug(e.message)
            return self.returnResult('FAIL', e.message)
            
        self._update_carrier_bag()        
        return self.returnResult('PASS', 'Backup [%s] successfully' % self.bak_file_path)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        #add by west.li,after download ,should update the carriebag 
        self.carrierbag['bak_files']={}
        self.carrierbag['bak_files']['unspecific']=self.bak_file_path
        self.carrierbag['restore_file_path']=self.bak_file_path
        pass
        
    def _init_test_params(self, conf):
        self.conf = dict(filename = 'full_config.bak')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.get('zd'):
            self.zd = self.carrierbag[self.conf['zd']]
        self.filename = self.conf['filename']        
        self.errmsg = ''
        self.passmsg = ''
    


    def _backup(self, zd, filename = ''):
        """
        """
        import os
        save_to = constant.save_to
        # Go to the Administer --> Backup
        file_path = bk.backup(zd, save_to = save_to)
        if filename:
            
            file = os.path.join(save_to, filename)            
            if os.path.isfile(file):
                os.remove(file)  
            os.rename(file_path, file)
            
            return file
            
        return file_path
