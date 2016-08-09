'''
Description:
    Verify the self service guest passes information on ZD WebUI.
       
Create on 2015-4-15
@author: yanan.yu
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_SelfService_GuestPass_Info_On_WebUI(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        
        self._verify_self_guestpass_on_webui()
            
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
        pass
  
    def _update_carribag(self):
        pass
    
    def _verify_self_guestpass_on_webui(self):
        
        try:
            all_guestpass_info_dict = ga.get_all_selfguestpasses(self.zd)
            all_guestpass_info_on_zd = {}

            for guest_full_name in all_guestpass_info_dict.iterkeys():
                all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info_dict[guest_full_name]['email'],
                                                             all_guestpass_info_dict[guest_full_name]['wlan']
                                                             ]
                
            if not all_guestpass_info_dict and not self.expected_webui_info:
                logging.debug(' guest pass on ZD WebUI are :%s'%all_guestpass_info_dict)
                self.passmsg = "No guest pass on zd webUI"
                return
               
            logging.debug('All guest pass information on ZD WebUI are: %s' % all_guestpass_info_on_zd)
            logging.debug('The expected guest pass information are: %s' % self.expected_webui_info)
            
            errguest = []
            for guestname in self.expected_webui_info.keys():
                if all_guestpass_info_on_zd[guestname] != self.expected_webui_info[guestname]:
                    errguest.append(guestname)
            
            if errguest:
                self.errmsg = 'The information of guest users: %s on ZD WebUI are not correct' % errguest
            
            else:
                passmsg = 'The information of guest users: %s on ZD WebUI are correct'
                self.passmsg = passmsg % self.expected_webui_info.keys()
                
        except Exception, e:
            self.errmsg = 'Verify guest pass information on WebUI failed: %s' % e.message