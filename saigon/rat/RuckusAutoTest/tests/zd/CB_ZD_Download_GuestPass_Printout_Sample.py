'''
Description:
    Download the guest pass printout sample from ZD WebUI -> Configure -> Guest Access ->
    Guest Pass Printout Customization table.
       
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Download_GuestPass_Printout_Sample(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        logging.info("Try to download the sample Guest Pass Printout")
        try:
            self.sample_fpath = ga.download_guestpass_printout_sample(self.zd, self.conf['sample_filename'])
            if not os.path.isfile(self.sample_fpath):
                raise
            
            else:
                self.passmsg = "Download the sample Guest Pass Printout successfully"
            
        except Exception, e:
            self.errmsg = "Unable to download the sample Guest Pass Printout: %s" % e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
            
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'sample_filename': 'guestpass_print.html'}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''
        
    def _retrieve_carribag(self):
        pass
        
    def _update_carribag(self):
        if self.carrierbag.has_key('gprint_cfg'):
            self.carrierbag['gprint_cfg']['html_file'] = self.sample_fpath
        
        else:
            self.carrierbag['gprint_cfg'] = {'html_file': self.sample_fpath}
            
