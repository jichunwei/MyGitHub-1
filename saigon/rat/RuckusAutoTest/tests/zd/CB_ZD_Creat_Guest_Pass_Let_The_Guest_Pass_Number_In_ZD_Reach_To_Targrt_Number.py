'''
west.li  2011.12.20
generate guest pass,
let the guest pass number in ZD reach a target number
'''

import time
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Creat_Guest_Pass_Let_The_Guest_Pass_Number_In_ZD_Reach_To_Targrt_Number(Test):
    '''
    repeat create guest pass.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):     
        passmsg='guest pass number reach to %s' % self.conf['total_nums']
        errmsg = ''
        timeout = self.conf['timeout']
        time_start=time.time()
        time_now = time.time()
        timeout_flag=True
        while timeout>time_now-time_start:
            self._get_guest_passes_number_need_to_gen()
            logging.info("there are %d guest pass need to be generated" % self.number_to_gen)
            if self.number_to_gen==0:
                timeout_flag=False
                break;
            repeat_cnt = self.number_to_gen/100
            logging.info("let us create %d*100 guest pass first" % repeat_cnt)
            while repeat_cnt:
                self._generate_multiple_guestpass(**self.gp_cfg)
                repeat_cnt = repeat_cnt - 1
            if 0!=self.number_to_gen%100:
                cfg=self.gp_cfg
                cfg['number_profile']=self.number_to_gen%100
                logging.info("let us create %d guest pass" % cfg['number_profile'])
                self._generate_multiple_guestpass(**cfg)
            if not self.zd.is_logged_in():
                self.zd.login(force = True)
            time_now = time.time()
        if timeout_flag:
            errmsg = 'guset pass did not be created in %d seconds' % self.conf['timeout']   

        self._update_carrier_bag()
        if errmsg:
            return "FAIL",errmsg
        return "PASS", passmsg

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existed_username'):
            self.conf['username'] = self.carrierbag['existed_username']

        if self.carrierbag.has_key('existed_password'):
            self.conf['password'] = self.carrierbag['existed_password']

        if self.carrierbag.has_key('wlan-guestpass'):
            self.wlan_cfg = self.carrierbag['wlan-guestpass']
            self.gp_cfg['wlan'] = self.wlan_cfg['ssid']    

    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'type':'multiple',
                     'guest_fullname':'',
                     'duration': '100',
                     'duration_unit': 'Days',
                     'wlan': 'wlan-guestpass',
                     'remarks': '',
                     'key': '',
                     'number_profile': '100',
                     'repeat_cnt': 10,
                     'max_gp_allowable': 10000,
#                     'profile_file': '',
                     'username': 'rat_guest_pass',
                     'password': 'rat_guest_pass',
                     'timeout':3600*2,
                     "total_nums":9999
                     }

        self.conf.update(conf)
        
        if self.carrierbag.has_key('existed_gp_cfg'):
            self.conf.update(self.carrierbag['existed_gp_cfg'])
            
        self.zd = self.testbed.components['ZoneDirector']        
        self.gp_cfg = self._get_default_gp_cfg()
        self.gp_cfg.update(self.conf)
        dlg_cfg = self._get_default_glg_cfg()
        self.gp_cfg.update(dlg_cfg)   
        self.errmsg = ''
        self.passmsg = ''


    def _get_default_gp_cfg(self):
        gp_cfg = {'username': 'rat_guest_pass',
                  'password': 'rat_guest_pass',
                  'wlan': 'wlan_guestpass',
                  'duration': '100',
                  'duration_unit': 'Days',
                  'type': 'multiple',
                  }
        return gp_cfg

    def _get_default_glg_cfg(self):
        zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)
        dlg_cfg = {'dlg_title': "The page at %s says:" % zd_url,
                   'dlg_text_maxgp': "The total number of guest and user accounts reaches maximum allowable size %d" %
                   (self.conf['max_gp_allowable']),
                   'dlg_text_dupgp': 'The key %s already exists. Please enter a different key.',
                   }
        return dlg_cfg

    def _generate_multiple_guestpass(self, **kwarg):

        gen_msg = "Try to generate %s guest passes automatically." % kwarg['number_profile']
        pass_msg = 'Create %s guest passes automatically successfully. '
        pass_msg = pass_msg % (kwarg['number_profile'])
#        err_msg = 'Create %s guest passes failed' % self.conf['number_profile']

        logging.info(gen_msg)

        lib.zd.ga.generate_guestpass(self.zd, **kwarg)
#        self.passmsg = self.passmsg + pass_msg
        logging.info(pass_msg)
    
    def _get_guest_passes_number_need_to_gen(self): 
        cnt = 10
        while cnt:
            try:
                total = int(lib.zd.ga.get_all_guestpasses_total_numbers(self.zd))
                break
            except Exception, e:
                logging.debug(e.message)
                cnt = cnt - 1        
                if not cnt:
                    raise e
                
                time.sleep(10)
                
        if self.conf['total_nums']:
            expect_cnt = int(self.conf['total_nums'])
        else:
            expect_cnt = 9999
            
        self.number_to_gen=expect_cnt-total
        

