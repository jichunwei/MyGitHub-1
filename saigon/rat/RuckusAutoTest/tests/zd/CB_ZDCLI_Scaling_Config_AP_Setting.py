'''
Case will substitute ZDGUI so that speed up testing and reduce breaking.

Created on Feb 10, 2011
@author: cwang@ruckuswireless.com
'''
import random
import logging

from RuckusAutoTest.models import Test
from string import Template

class CB_ZDCLI_Scaling_Config_AP_Setting(Test):
    '''
    Set each AP devname, description, device location gps coordinates to maximum.
    '''
       
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        #skip location setting, bug#17492
        self.SETTING_COMMAND = '''ap $mac
        devname $device_name
        description $description
        gps $x,$y       
        '''
        self.COMMAND_INSTANCE = Template(self.SETTING_COMMAND)
         
    def test(self):
        passmsg = []        
        if not self.aps_list:
            self.aps_list = self.testbed.get_aps_sym_dict()
            
        self.aps_list = self.aps_list.values()  
        self.aps_cfg_list = []             
        for ap in self.aps_list:
            ap_cfg = {}                        
            ap_cfg['mac'] = ap['mac']                        
            ap_cfg['description'] = self._generate_string(64)
            device_name = self._generate_string(64)
            ap_cfg['device_name'] = device_name
            ap_cfg['x'] = self.conf['latitude']
            ap_cfg['y'] = self.conf['longitude']
            logging.info('configure ap %s as %s' % (ap_cfg['mac'], ap_cfg))            
            self.zdcli.do_cfg(self.COMMAND_INSTANCE.substitute(ap_cfg))
            self.aps_cfg_list.append(ap_cfg)
            
        passmsg.append('AP configuration setting finished')           
        self._update_carrier_bag()
        
        return ["PASS", passmsg]        
        
    
    def cleanup(self):
        pass 
    
    def _generate_string(self, size = 64):
        char_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''        
        random.seed()
        while size>0:
            lgt = len(char_string)
            index = random.randrange(0, lgt)
            result += char_string[index]
            size = size - 1
        return result
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existing_aps_list'):
            self.aps_list = self.carrierbag['existing_aps_list']
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_aps_cfg_list'] = self.aps_cfg_list 
    
    def _init_test_params(self, conf):
        self.conf = dict(description = self._generate_string(64), 
                         device_name = self._generate_string(64),
                         #device_location = self._geneate_string(64),
                         latitude = '37.38813989',
                         longitude = '-122.02586330',
                         )
        
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.aps_list = None
        self.errmsg = ''
        self.passmsg = ''

            