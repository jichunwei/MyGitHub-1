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

from RuckusAutoTest.models import Test

class CB_ZD_Verify_Multi_DPSK(Test):
    '''
    Verify DPSK information against ZD Web UI.
    '''
    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
        
    
    def test(self):
        self._chk_dpsk_total_numbers()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        if self.chk_detail:
            self._verify_dpsk_on_web_ui()
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult("PASS", self.passmsg)
    
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.wlan_cfg = None
        if self.carrierbag.has_key('wlan-dpsk'):            
            self.wlan_cfg = self.carrierbag['wlan-dpsk']
            
        self.dpsk_cfg = None        
        if self.carrierbag.has_key('existed_dpsk_cfg'):            
            self.dpsk_cfg = self.carrierbag['existed_dpsk_cfg']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(chk_detail = False,
                         wlan_cfg = {'auth': 'PSK',
                                     'auth_svr': '',
                                     'do_dynamic_psk': True,
                                     'do_zero_it': True,
                                     'encryption': 'AES',
                                     'key_index': '',
                                     'key_string': '1234567890',
                                     'ssid': 'wlan-dpsk',
                                     'type': 'standard',
                                     'wpa_ver': 'WPA'},
                          dpsk_cfg = {'expected_response_time': 30,
                                      'number_of_dpsk': 100,
                                      'psk_expiration': 'Unlimited',
                                      'repeat_cnt': 50,
                                      'wlan': 'wlan-dpsk'}                         
                         )        
        self.conf.update(conf)
        if not self.dpsk_cfg:
            self.dpsk_cfg = self.conf['dpsk_cfg']
        
        if not self.wlan_cfg:
            self.wlan_cfg = self.conf['wlan_cfg']
            
        self.chk_detail = self.conf['chk_detail']
        self.zd = self.testbed.components['ZoneDirector']
        self.total_dpsk = self.dpsk_cfg['number_of_dpsk'] * self.dpsk_cfg['repeat_cnt']
        self.errmsg = ''
        self.passmsg = ''
            
    
    def _chk_dpsk_total_numbers(self):
        try:            
            total = self.zd.get_all_generated_psks_total_numbers()
        except Exception, e:
            #check again
            logging.info(e)
            import time
            time.sleep(10)
            total = self.zd.get_all_generated_psks_total_numbers()
            
        if self.total_dpsk == int(total):
            self.passmsg = 'There are %d DPSKs have shown' %  self.total_dpsk
            return
        else:
            self.errmsg = 'There are %s DPSKs have shown, expected %d' % (total, self.total_dpsk)
            return        
    
    
    def _verify_dpsk_on_web_ui(self, expected_info = None):        
        if expected_info is None:
            expected_info = [self.wlan_cfg['ssid']]

        logging.info("Get all generated PSKs on WebUI")
        all_dpsk_info = self.zd.get_all_generated_psks_info()

        all_dpsk_info_on_zd = {}
        for dpsk_info in all_dpsk_info:
            all_dpsk_info_on_zd[dpsk_info['user']] = [dpsk_info['wlans']]
        logging.debug('All PSKs information on ZD WebUI are: %s' % all_dpsk_info_on_zd)

        if isinstance(expected_info, dict):
            logging.info('Verify the number of generated PSKs')
            if len(all_dpsk_info) != self.total_dpsk:
                errmsg = 'We expect there are %s PSKs created but %s on file. '
                errmsg = errmsg % (self.total_dpsk, len(all_dpsk_info))
                self.errmsg = self.errmsg + errmsg
                return

        logging.info('Verify the PSKs information shown on WebUI')
        if not self._verify_info(all_dpsk_info_on_zd, expected_info):
            errmsg = 'The wlan information of PSKs %s are not %s as expected. '
            errmsg = errmsg % (self.errkey, expected_info)
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            return

        passmsg = 'WebUI was updated correctly %s PSKs created. ' % len(all_dpsk_info_on_zd)
        self.passmsg = self.passmsg + passmsg
        logging.info(passmsg)    

    def _verify_info(self, sourceInfo, expectedInfo, keyOnly = True):
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
