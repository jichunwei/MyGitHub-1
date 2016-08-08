'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswirelesss.com
'''
import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import application_visibility_zd as vap_zd

class CB_ZD_Verify_Application_Visibility_Info(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to verify application visibility info!')
            logging.info('It may take several minutes, please wait!')
            st = time.time()
            fnd_app = False
            while time.time() - st < self.conf['check_timeout']:
                res = self.verify_application_visibility_info(self.conf['application_description'])
                if res: 
                    fnd_app = True
                    break
        except: 
            self.errmsg = 'Error occurred while verifying application visibility info.'                                  
            return self.returnResult('FAIL', self.errmsg)
        if fnd_app:
            self.passmsg = 'Application is shown zd webui.'
            return self.returnResult('PASS', self.passmsg)
        else:
            self.errmsg = 'Application is not shown on zd webui.'
            return self.returnResult('FAIL', self.errmsg)
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {
                     'application_description':'',
                     'check_timeout':600
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.get('zd_tag'):
            self.zd=self.carrierbag[self.conf['zd_tag']]
            
    def verify_application_visibility_info(self, app_desc):
        application_info = vap_zd.get_application_visibility_info_by_description(self.zd)
        if application_info.get(app_desc):
            logging.info('Get application info successfully: %s'%application_info[app_desc])
            return True
        return False
