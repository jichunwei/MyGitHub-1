'''
Description:
    Verify the guest passes information in ZD WebUI.
       
Create on 2011-8-23
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_GuestPass_Info_On_WebUI(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            all_guestpass_info = ga.get_all_guestpasses(self.zd)
            all_guestpass_info_on_zd = {}

            for guest_full_name in all_guestpass_info.iterkeys():
                all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info[guest_full_name]['created_by'],
                                                             all_guestpass_info[guest_full_name]['wlan']
                                                             ]
    
            logging.debug('All guest pass information on ZD WebUI are: %s' % all_guestpass_info_on_zd)
            logging.debug('The expected guest pass information are: %s' % self.expected_webui_info)
            
            errguest = []
            for guestname in self.expected_webui_info.keys():
                if all_guestpass_info_on_zd[guestname] != self.expected_webui_info[guestname]:
                    errguest.append(guestname)
            
            if errguest:
                self.errmsg = 'The information of guest users: %s on ZD WebUI are not correct' % errguest
            
            else:
                self.passmsg = 'The information of guest users: %s on ZD WebUI are correct'
                self.passmsg = self.passmsg % self.expected_webui_info.keys()
                
        except Exception, e:
            self.errmsg = 'Verify guest pass information on WebUI failed: %s' % e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'expected_webui_info': {}}
        self.conf.update(conf)
        
        self.expected_webui_info = self.conf['expected_webui_info']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        if not self.expected_webui_info:
            self.expected_webui_info = self.carrierbag['gp_cfg']['expected_webui_info']
  
    def _update_carribag(self):
        pass
