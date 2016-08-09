'''
Description:
    Generate a big template File to /tmp against RuckusAP shell till AP reboot.
        In order to watchdog timeout
Create on 2013-8-7
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.common import Ratutils
from RuckusAutoTest.models import Test

class CB_AP_Generate_Big_Tmp_File(Test):
    required_components = ['RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ap_tag = 'AP_01',
                         tftpserver='192.168.0.10',
                         filename='testfile.img'
                         )
        self.conf.update(conf)
            
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']   
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        
    
    def test(self):
        filename = self.conf.get('filename')
        logging.info('Touch a file %s' % filename)
        self.active_ap.do_shell("touch /tmp/%s" % filename)
#        msg = lambda x, n: x.join([x for i in range(n)])
        logging.info('tftp get file %s' % filename)
        ip_addr = self.active_ap.ip_addr
        try:                       
            self.active_ap.tn.write("set rpmkey cli_esc2shell_ok t\n") 
            time.sleep(1)
            self.active_ap.tn.write("!v54!\n")
            time.sleep(1)            
            self.active_ap.tn.write("cd /tmp\n")                                 
            self.active_ap.tn.write("tftp -g -r '%s' %s\n"  % (filename, self.conf.get('tftpserver')))
            st = time.time()
            while time.time() - st < 360:
                res = Ratutils.ping(ip_addr)
                if res.find("Timeout") != -1:
                    logging.info('Wait for 60 second, make sure statistic number can report to ZD.')
                    time.sleep(60)                
                    return self.returnResult('PASS',
                                            "Correct Behavior-AP rebooting while watchdog timeout." )            
            return self.returnResult("FAIL", "InCorrect Behavior, AP doesn't reboot.")
                                                
        except Exception, e:                
            import traceback
            logging.error(traceback.format_exc())            
            return self.returnResult('FAIL', e.message)
        
    def cleanup(self):
        self._update_carribag()