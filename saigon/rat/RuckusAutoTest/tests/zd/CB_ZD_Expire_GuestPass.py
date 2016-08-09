'''
Description:
    Make the guest passes expired by changing the ZD system time.

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

Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import datetime
import time
import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


UNIT_TO_HOURS = {"Days": 24,
                 "Hours": 1,
                 "Weeks": 7 * 24,
                }


class CB_ZD_Expire_GuestPass(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if self.conf['is_first_use_expired'] and not self.conf['has_been_used']:
                #'valid_day' is the days before first use 
                #configured in ZD WebUI -> configure -> Guest Access -> Guest Pass Generation
                duration_hours = self.conf['valid_day'] * 24
            
            else:
                #'duration' is the duration configured in the Guest Pass Generation URL
                duration_hours = self.conf['duration'] * UNIT_TO_HOURS[self.conf['duration_unit']]
            
            logging.info("Change the system time of ZD to make the guest pass expired")
            tmptime = datetime.datetime.now() + datetime.timedelta(hours = duration_hours + 24)
            
            os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
            time.sleep(5)
            self.zd.get_current_time(True)
            
            logging.info("Make sure the entry disappears from the guest pass table")
            ga.get_guestpass_by_name(self.zd, self.conf['guest_name'])
            self.errmsg = "The entry[%s] still exists in the guest pass table" % self.conf['guest_name']
            
        except Exception, e:
            if 'No matched row found' in e.message:
                self.passmsg = "Expire the guest pass of '%s' successfully" % self.conf['guest_name']

            else:
                errmsg = "Expire the guest pass of '%s' failed: %s"
                self.errmsg = errmsg % (self.conf['guest_name'], e.message)
            
        finally:
            logging.debug("Restore the previous system time of ZD")
            tmptime = datetime.datetime.now() - datetime.timedelta(hours = duration_hours + 24)
            os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
            time.sleep(5)
            self.zd.get_current_time(True)
        
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
                     'duration': 2,
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
