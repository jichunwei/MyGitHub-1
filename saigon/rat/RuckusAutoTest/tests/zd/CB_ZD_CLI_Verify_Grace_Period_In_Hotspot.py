'''
Description:
    

Input:
    
    
Create on 2011-12-14
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_hotspot as cfhs

class CB_ZD_CLI_Verify_Grace_Period_In_Hotspot(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            hotspot_name = self.gui_hotspot_cfg['name']
            cli_hotspot_info = cfhs.show_config_hotspot(self.zdcli, hotspot_name)
            cli_hotspot_info = cli_hotspot_info['hotspot']['id'].values()
            cli_gp_info = cli_hotspot_info[0]['grace_period']
            
            msg = "Grace Period information in ZDCLI is: %s " % cli_gp_info
            msg += "while the cfg in ZDGUI is: %s" % self.gui_hotspot_cfg
            if self.gui_hotspot_cfg['idle_timeout'] == None:
                if cli_gp_info['status'] != 'Disabled':
                    raise Exception(msg)
            
            else:
                if cli_gp_info['status'] != 'Enabled':
                    raise Exception(msg)
                
                if cli_gp_info['period'] != '%s Minutes' % self.gui_hotspot_cfg['idle_timeout']:
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
        self.conf = {'gui_hotspot_cfg': {},
                     }
        self.conf.update(conf)
        
        self.gui_hotspot_cfg = self.conf['gui_hotspot_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        pass
            
    def _update_carribag(self):
        pass
  
