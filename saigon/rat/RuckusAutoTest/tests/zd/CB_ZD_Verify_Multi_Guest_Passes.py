'''
Description:
    config:
        
    test:
    
    cleanup:
    
Created on 2010-6-10
@author: cwang@ruckuswireless.com
'''
import logging
import traceback
import time

from RuckusAutoTest.models import Test

from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_Multi_Guest_Passes(Test):
    '''
    Verify guest passes from webui.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
#        import pdb
#        pdb.set_trace()
        passmsg = []
        #Check numbers first.
        self._chk_guest_passes_total_numbers()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
            
        if self.chk_detail and not self.conf['total_nums']:
            self._verify_guest_pass_info_on_webui()
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):  
#        self.carrierbag['wlan-guestpass'] = {'auth': 'open', 'encryption': 'none', 'ssid': 'wlan-guestpass', 'type': 'guest'}        
        if self.carrierbag.has_key('wlan-guestpass'):
            self.wlan_cfg = self.carrierbag['wlan-guestpass']            
#        self.carrierbag['existed_gp_cfg'] = {'duration': '1',
#                                             'duration_unit': 'Days',
#                                             'guest_fullname': '',
#                                             'key': '',
#                                             'max_gp_allowable': 1250,
#                                             'number_profile': '100',
#                                             'password': 'rat_guest_pass',
#                                             'remarks': '',
#                                             'repeat_cnt': 10,
#                                             'type': 'multiple',
#                                             'username': 'rat_guest_pass',
#                                             'wlan': 'wlan-guestpass'}
                         
        if self.carrierbag.has_key('existed_gp_cfg'):
            gp_cfg = self.carrierbag['existed_gp_cfg']            
            self.conf['username'] = gp_cfg['username']
            self.conf['password'] = gp_cfg['password']
            self.conf['number_profile'] = gp_cfg['number_profile']
            self.conf['repeat_cnt'] = gp_cfg['repeat_cnt']
        
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(username='admin',
                         number_profile = '100',
                         repeat_cnt = 10,
                         chk_detail = False,
                         total_nums = None,
                         )
        
        self.conf.update(conf)
        if self.conf.has_key('wlan_cfg'):
            self.wlan_cfg = self.conf['wlan_cfg']
        self.chk_detail = self.conf['chk_detail']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
       
    
    def _chk_guest_passes_total_numbers(self): 
        #cwang@2010-10-23, add retry mechanism.
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
            expect_cnt = self.conf['repeat_cnt'] * int(self.conf['number_profile'])
            
        if total == expect_cnt:
            self.passmsg = 'There are %d Guest Passes shown correctly' % total
        else:
            self.errmsg = 'There are %d Guest Passes shown, expected [%d]' % (total, expect_cnt)
            
        
    def _verify_guest_pass_info_on_webui(self, expected_info = None):    
        if expected_info is None:
            expected_info = [self.conf['username'], self.wlan_cfg['ssid']]
        
        logging.info("Get all guest passes on WebUI")
        all_guestpass_info = lib.zd.ga.get_all_guestpasses(self.zd)

        all_guestpass_info_on_zd = {}
        for guest_full_name in all_guestpass_info.iterkeys():
            all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info[guest_full_name]['created_by'],
                                                         all_guestpass_info[guest_full_name]['wlan']
                                                         ]

        logging.debug('All guest pass information on Zone Director WebUI are: %s' % all_guestpass_info_on_zd)

        if isinstance(expected_info, dict):
            logging.info('Verify the number of user names and guest passes generated')
            if len(all_guestpass_info) != self.conf['number_profile'] * self.conf['repeat_cnt']:
                errmsg = 'We expect there are %s guest passes created but %s on file. '
                errmsg = errmsg % (self.conf['number_profile'], len(all_guestpass_info))
                self.errmsg = self.errmsg + errmsg
                return

        logging.info('Verify the guest pass information shown on WebUI')
        if not self._verify_info(all_guestpass_info_on_zd, expected_info):
            errmsg = 'The creator and wlan information of guest users %s are not %s as expected. '
            errmsg = errmsg % (self.errkey, expected_info)
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            return

        passmsg = 'WebUI was updated correctly %s guest pass(es) created. ' % len(all_guestpass_info_on_zd)
        self.passmsg = self.passmsg + passmsg
        logging.info(passmsg)

    def _verify_info(self, sourceInfo, expectedInfo, keyOnly = True):
        #
        if not isinstance(sourceInfo, dict) or expectedInfo is None:
            logging.debug("Either expectedInfo is None or sourceInfo is not a dict")
            return False

        if isinstance(expectedInfo, dict):
            if sourceInfo == expectedInfo:
                return True

        self.errkey = []
        try:
            if isinstance(expectedInfo, dict):
                for key in expectedInfo.keys():
                    # either the key does not exist, or its value is not identical to the expected one
                    if key in sourceInfo.keys():
                        if not keyOnly and expectedInfo[key] != sourceInfo[key]:
                            self.errkey.append(key)
                    else:
                        self.errkey.append(key)

            else:
                for key in sourceInfo.keys():
                    if sourceInfo[key] != expectedInfo:
                        self.errkey.append(key)

        except Exception:
            traceback.print_exc()
            return False

        if self.errkey:
            return False

        return True        
        
