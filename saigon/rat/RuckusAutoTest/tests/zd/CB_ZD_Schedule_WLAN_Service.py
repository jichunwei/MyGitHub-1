'''
Create a WLAN with service schedule.
Created on 2011-4-20
@author: cwang@ruckuswireless.com
'''
from datetime import datetime
import random
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD


class CB_ZD_Schedule_WLAN_Service(Test):
    required_components = ['ZoneDirector', 'Station']
    test_parameter = {}
    
    def _init_test_parameter(self):
        self.zd = self.testbed.components['ZoneDirector']
        self.schedule = {'on':False,
                         'off':False,
                         'specific':False,                                                                           
                         }
        self.schedule = self._get_service_schedule(self.conf)
            
    
    def _retrive_parameter_from_carribag(self):        
        self.wlan_conf = self.carrierbag[self.conf['ssid']]
        
    def _update_parameter_to_carribag(self):
        self.carrierbag[self.conf['ssid']] = self.wlan_conf
    
    def _get_service_schedule(self, cfg):
        #schedule 15 Mins for current WLAN
        _schedule = {}
        if cfg['on']:
                _schedule['on'] = True
                _schedule['off'] = False
                _schedule['specific'] = None
        elif cfg['off']:        
            _schedule['on'] = False
            _schedule['off'] = True
            _schedule['specific'] = None
        elif cfg['specific']:        
            _schedule['on'] = False
            _schedule['off'] = False
            #sync-up pc time
            self.zd.get_current_time(True)
            #schedule 15 Mins for current WLAN
            dt = datetime.today()        
            wd = dt.weekday() + 1
            h = dt.hour
            m = dt.minute
            init_pos = h * 4 + m/15 + 1
            _basetime = None
            if init_pos + 1 >= 97:
                if wd < 6:                        
                    _basetime = {'%s' % wd : [init_pos],
                                 '%s' % (wd+1) : [1], 
                                 }
                else:
                    _basetime = {'%s' % wd : [init_pos],
                                 '%s' % (wd-7) : [1],
                                 }
            else:
                _basetime = {'%s' % wd : [init_pos, init_pos + 1],}
            
            _schedule['specific'] = _basetime
            
        return _schedule
        
#    def _get_wlan_cfg(self):
#        wlan_cfg = dict(ssid = "rat-wlan-service-schedule-%d" % random.randint(10000, 20000), 
#                        auth = "open", wpa_ver = "", encryption = "none",
#                        key_index = "" , key_string = "",
#                        username = "", password = "", 
#                        auth_svr = "", do_service_schedule=None,)
#                    
#        return wlan_cfg
    
    def config(self, conf):        
        self.conf = {'ssid':None,
                     'wlan_cfg':None}
        self.conf.update(conf)
        self._init_test_parameter()
        if self.conf['wlan_cfg']:
            self.wlan_conf = self.conf['wlan_cfg']
        else:            
            self._retrive_parameter_from_carribag()
    
    def test(self):        
        try:                
            self.wlan_conf['do_service_schedule'] = self.schedule   
#            import pdb
#            pdb.set_trace()                     
            Helper_ZD.wlan.edit_wlan(self.zd, self.wlan_conf['ssid'], self.wlan_conf)
            pass_msg = 'WLAN %s with schedule %s edited successfully' % (self.wlan_conf['ssid'], self.schedule)            
            logging.info(pass_msg)
            self._update_parameter_to_carribag()
            return self.returnResult('PASS', pass_msg)        
        except Exception:
            import sys
            return self.returnResult('FAIL', sys.exc_info())
    
    def cleanup(self):
        pass        