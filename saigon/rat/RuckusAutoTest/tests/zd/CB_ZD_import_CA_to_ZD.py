
'''
import CA to ZD
Created on Nov 12, 2014
@author: Yu.yanan@odc-ruckuswireless.com
'''

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import config_certificate as cc



class CB_ZD_import_CA_to_ZD(Test):
    def config(self,conf):
        self._initTestParameters(conf)
        
    def test(self):
        self.errmsg = ''
        self._import_ca_from_zd_gui()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'Import CA from ZDCLI success.'+self.passmsg
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
    
    def _import_ca_from_zd_gui(self):
        
        if not self.conf.get('file_name'):
            self.passmsg =  'no ca needs to import'
            return
        try:
            cc._import_ca(self.zd,self.conf['file_name'])
        except:
            self.errmsg = 'import CA from zd GUI failed!'
    
    def _initTestParameters(self, conf):
        self.conf = {
                     'target_zd':'',                     
                     'file_name':''#eg: d:/my-ca.crt
                     }
        self.conf.update(conf)
        if self.conf.get('target_zd') and self.carrierbag.get('active_zd') and self.carrierbag.get('standby_zd'):
            self.zd = self.carrierbag[self.conf['target_zd']]
        else:
            self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''