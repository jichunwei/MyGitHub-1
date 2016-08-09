"""
   Description: 
   @author: Yin.wenling
   @since: November 2013

"""

import logging
import re

from RuckusAutoTest.models import Test

class CB_Station_AP_Exec_Command(Test):
    required_components = ['Station']
    parameters_description = {'ap_cfg' : {},
                              'sta_tag' : 'sta_1'
                               }
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carrier_bag()
    
    def test(self): 
        logging.info('Station Login ap and Send Command')     
        try:
            self._login_ap_and_send_command()
        except Exception, ex:
            self.errmsg = 'Station Login ap and Send Command Failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Station Login ap and Send Command success'
            return self.returnResult('PASS', pass_msg)        
        
        
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'ap_cfg' : {'ip_addr':'169.254.1.1', 
                                 'port' : 22, 
                                 'username' : 'super', 
                                 'password' : 'sp-admin',
                                 'cmd_text' : ''},
                    'sta_tag' : 'sta_1'}
        self.conf.update(conf)
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
           
        self.ap_cfg = self.conf['ap_cfg']       
        self.errmsg = ''     
    
    def _retrieve_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _login_ap_and_send_command(self):
        if self.ap_cfg:
            self.target_station.login_ap_cli_and_exec_command(self.ap_cfg['cmd_text'],self.ap_cfg['username'],
                                                              self.ap_cfg['password'],self.ap_cfg['port'],
                                                              self.ap_cfg['ip_addr'])
        else:
            self.errmsg = "ap_cfg must be offered."   
            