'''
Description:
    

Input:
    
    
Create on 2011-12-14
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi

class CB_ZD_CLI_Verify_Grace_Period_In_WLAN(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            ssid = self.gui_wlan_cfg['ssid']
            cli_wlan_info = gwi.get_wlan_by_ssid(self.zdcli, ssid)
            if cli_wlan_info == None:
                raise Exception("WLAN[%s] does not exist in ZDCLI!" % ssid)
            
            cli_gp_info = cli_wlan_info['Grace Period']
            
            msg = "Grace Period information in ZDCLI is: %s " % cli_gp_info
            msg += "while the cfg in ZDGUI is: %s" % self.gui_wlan_cfg
            if self.gui_wlan_cfg['do_grace_period'] == False:
                if cli_gp_info['Status'] != 'Disabled':
                    raise Exception(msg)
            
            else:
                if cli_gp_info['Status'] != 'Enabled':
                    raise Exception(msg)
                
                if cli_gp_info['Period'] != '%s Minutes' % self.gui_wlan_cfg['grace_period']:
                    raise Exception(msg)
            
            self.passmsg = msg
                
        except Exception, e:
            self.errmsg = e.message
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'gui_wlan_cfg': {},
                     }
        self.conf.update(conf)
        
        self.gui_wlan_cfg = self.conf['gui_wlan_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        pass
            
    def _update_carribag(self):
        pass
  
