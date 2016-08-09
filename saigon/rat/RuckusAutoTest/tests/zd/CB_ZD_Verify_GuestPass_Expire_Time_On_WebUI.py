'''
Description: 
    Verify the guest pass expire time on ZD WebUI.
    The expected guest pass expire time on ZD WebUI is:
    1. The guest pass is effective from creation:
       The expire time is created time plus the duration configured in the Guest Pass Generation URL;
    2. The guest pass is effective from first use:
       a. Before first use, the expire time is created time plus the valid days configured in 
          ZD WebUI -> configure -> Guest Access -> Guest Pass Generation;
       b. After first use, the expire time is first use time plus the duration configured in 
          the Guest Pass Generation URL;

Input:
    'is_first_use_expired': The guest pass is effective from first use or creation.
                            True: from first use
                            False: from creation
    'has_been_used': The guest pass has been used or not.
    'valid_day': The valid days configured in 
                 ZD WebUI -> configure -> Guest Access -> Guest Pass Generation.
    'duration': The duration configured in the Guest Pass Generation URL.
    'duration_unit': The duration unit configured in the Guest Pass Generation URL.
    'guest_name': Name of the guest.
    
Limitation:
    This script works when duration_unit is 'Days', and only verify the day of the expire time.

Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_GuestPass_Expire_Time_On_WebUI(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            logging.info("Try to verify the guest pass expire time on ZD WebUI.")
            if self.conf['is_first_use_expired'] and not self.conf['has_been_used']:
                #'valid_day' is the days before first use 
                #configured in ZD WebUI -> configure -> Guest Access -> Guest Pass Generation
                duration = self.conf['valid_day']
            
            else:
                #'duration' is the duration configured in the Guest Pass Generation URL
                duration = self.conf['duration']
            
            zd_current_time = self.zd.get_current_time()
            zd_current_time = time.strptime(zd_current_time, "%A, %B %d, %Y %H:%M:%S %p")
            zd_current_time = time.strftime("%Y/%m/%d %H:%M:%S", zd_current_time)
            zd_current_time = time.mktime(time.strptime(zd_current_time.split()[0], "%Y/%m/%d"))
            max_expired_time = zd_current_time + duration * 24 * 3600
            
            guestpass_info = ga.get_guestpass_by_name(self.zd, self.conf['guest_name'])
            guestpass_time = guestpass_info['expire_time']
            guestpass_time = time.mktime(time.strptime(guestpass_time.split()[0], "%Y/%m/%d"))

            msg = "The guest pass expired time for guest[%s] on ZD WebUI is: %s,"
            msg = msg % (self.conf['guest_name'], guestpass_time)
            msg += "The expected expired time is: %s" % max_expired_time
            
            if guestpass_time != max_expired_time:
                self.errmsg = "Verify guest pass expired time on ZD WebUI failed: %s" % msg
            
            else:
                self.passmsg = "Verify guest pass expired time on ZD WebUI successfully: %s" % msg
            
        except Exception, e:
            self.errmsg = 'Verify guest pass expired time on ZD WebUI failed: %s' % e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'is_first_use_expired': True,
                     'has_been_used': True,
                     'valid_day': 1,
                     'duration': 1,
                     'duration_unit': 'Days',
                     'guest_name': ''
                     }
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        pass
            
    def _update_carribag(self):
        pass
