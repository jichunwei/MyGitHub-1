'''
Description:
    Customize the guest pass printout sample.
       
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import time
import logging

from RuckusAutoTest.models import Test


class CB_ZD_Customize_GuestPass_Printout_Sample(Test):
    required_components = []
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        logging.info("Customize the downloaded Guest Pass Printout sample")
        try:
            tf = open(self.conf['html_file'], "rb")
            data = tf.read()
            tf.close()
            
            data = data.replace(self.conf['gprint1_old'], self.conf['gprint1_new'] % self.conf['gprint1_needed'])
            data = data.replace(self.conf['gprint2_old'], self.conf['gprint2_new'] % self.conf['gprint2_needed'])

            tf = open(self.conf['html_file'], "wb")
            tf.write(data)
            tf.close()
            
            self.passmsg = "Customize the downloaded Guest Pass Printout sample successfully"

        except Exception, e:
            self.errmsg = "Unable to read/write the file [%s]: %s" % (self.conf['html_file'], e.message)
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
            
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'name': 'CustomizedGPPrintout-%s' % time.strftime("%H%M%S"),
                     'description': 'Customized Guest Pass Printout',
                     'html_file': '',
                     'template_fname': 'guestpass_print.html',
                     'gprint1_old': '</style>',
                     'gprint1_new': '%s\n</style>',
                     'gprint1_needed': '.gptest {font-family: Tahoma; font-size: x-small; font-style: normal; color: #FF0000;}',
                     'gprint2_old': '<strong>{GP_GUEST_KEY}',
                     'gprint2_new': '<strong %s>{GP_GUEST_KEY}',
                     'gprint2_needed': 'class="gptest"',
                     }
        self.conf.update(conf)
        
        self.passmsg = ''
        self.errmsg = ''
        
    def _retrieve_carribag(self):
        if not self.conf['html_file']:
            self.conf['html_file'] = self.carrierbag['gprint_cfg']['html_file']
        
    def _update_carribag(self):
        self.carrierbag['gprint_cfg'].update(self.conf)
            