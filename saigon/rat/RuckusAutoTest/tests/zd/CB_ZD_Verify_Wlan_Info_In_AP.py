'''
@author: serena.tan@ruckuswireless.com

Created on 2011-5-10
Modified by Sean Chen on 2013/01/06
Modified by Jacky Luh on 2012/12/25
Description: This script is used to verify the WLANs' status in the active AP.

'''

import re
import copy
import logging
import time

from RuckusAutoTest.models import Test


INTERNAL_WLAN = {
    'name': ['meshd', 'meshu', 'recovery-ssid', 'wlan100', 'wlan101'],
    'type': ['MON', '???']
}
ENCRYPTION_PARA_LIST = ['ssid', 'auth', 'encryption', 'wpa_ver', 'key_index', 'key_string']


class CB_ZD_Verify_Wlan_Info_In_AP(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyWlanInfoInAP()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrierbag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        '''
        conf: 
        {'ap_tag': '',
         'expect_wlan_info': {'24g': {'wlan_tag1': {'status': 'up'/'down',
                                                    'encryption_cfg': {'ssid': '',
                                                                       'auth': '',
                                                                       'encryption': '',
                                                                       'wpa_ver': '',
                                                                       'key_index': '',
                                                                       'key_string': ''
                                                                       }
                                                    },
                                      ...
                                      },
                              '5g': {'wlan_tag1': {'status': 'up'/'down',
                                                   'encryption_cfg': {'ssid': '',
                                                                      'auth': '',
                                                                      'encryption': '',
                                                                      'wpa_ver': '',
                                                                      'key_index': '',
                                                                      'key_string': ''
                                                                      }
                                                   },
                                      ...
                                     }
                              }
        }
        WARNING: If value of 'expect_wlan_info' is None, means expect that there isn't any up wlan in the active AP.
        '''
        self.expect_wlan_info = conf['expect_wlan_info']
        self.ap_tag = conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        #chentao 2013-4-19
        self.expect_wlans_24g_up = 0
        self.expect_wlans_5g_up = 0
        #chentao 2013-4-19    
        # compatible with the test config-params before
        if (self.expect_wlan_info is not None) and (not self.expect_wlan_info.has_key('24g')) and (not self.expect_wlan_info.has_key('5g')):
            tag_24g = 0
            tag_5g = 0
            for wlan_id in self.expect_wlan_info.keys():
                #updated by jluh 2013-10-30, because 'wlan10' < 'wlan8' is True.
                if int(re.match(r'wlan(\d+)',wlan_id, re.I).group(1)) < 8:
                    tag_24g += 1
                    #chentao 2013-4-19          
                    if self.expect_wlan_info[wlan_id]['status'] == 'up':
                        self.expect_wlans_24g_up += 1
                        logging.info('Expected up 2.4G wlan number is: %s' %self.expect_wlans_24g_up)
                    #chentao 2013-4-19
                    wlan_tag = 'wlan_tag' + str(tag_24g)
                    wlan_info_24g = self.expect_wlan_info.pop(wlan_id)
                    if not self.expect_wlan_info.has_key('24g'):
                        self.expect_wlan_info.update({'24g': {wlan_tag: wlan_info_24g}})
                    else:
                        self.expect_wlan_info['24g'].update({wlan_tag: wlan_info_24g})
                else:
                    tag_5g += 1
                    #chentao 2013-4-19
                    if self.expect_wlan_info[wlan_id]['status'] == 'up':
                        self.expect_wlans_5g_up += 1
                        logging.info('Expected up 5G wlan number is: %s' %self.expect_wlans_5g_up)
                    #chentao 2013-4-19
                    wlan_tag = 'wlan_tag' + str(tag_5g)
                    wlan_info_5g = self.expect_wlan_info.pop(wlan_id)
                    if not self.expect_wlan_info.has_key('5g'):
                        self.expect_wlan_info.update({'5g': {wlan_tag: wlan_info_5g}})
                    else:
                        self.expect_wlan_info['5g'].update({wlan_tag: wlan_info_5g})
        
        self.wlan_name_list = []
        if self.carrierbag.has_key('wlan_name_list'):
            self.wlan_name_list = self.carrierbag['wlan_name_list']
        
        self.errmsg = ''
        self.passmsg = ''

    def _verifyWlanInfoInAP(self):
        logging.info('Verify wlan info in the active AP[%s]' % self.active_ap.get_base_mac())
        try:
            logging.info('The expect external wlan info in AP is: %s' % self.expect_wlan_info)
            time.sleep(5)
            wlan_info = self.active_ap.get_wlan_info_dict()
            logging.info('All wlan info in AP is: %s' % wlan_info)
            
            # don't check internal wlans
            external_wlans = {}
            for (wlan_id, wlan) in wlan_info.iteritems():
                if wlan['name'] not in INTERNAL_WLAN['name'] and wlan['type'] not in INTERNAL_WLAN['type']:
                    external_wlans[wlan['name']] = wlan
             
            if self.expect_wlan_info == None:
                if len(external_wlans) == 0:
                    self.passmsg = "There is no external wlan in AP"
                else:
                    for wlan_name in external_wlans:
                        if external_wlans[wlan_name]['status'] == 'up':
                            self.errmsg = "There are up wlans in AP when expect no wlan exists"
                            return
                    self.passmsg = "There are no up wlans in AP"
                return
            
            wlans_24g_up = {}
            wlans_5g_up = {}
            for wlan_name in external_wlans:
                if external_wlans[wlan_name]['status'] == 'up':
                    if external_wlans[wlan_name]['radioID'] == '0':
                        wlans_24g_up.update({wlan_name: external_wlans[wlan_name]})
                    else:
                        wlans_5g_up.update({wlan_name: external_wlans[wlan_name]})                   
            for radio_mode in self.expect_wlan_info:
                wlans_up = {}
                if radio_mode == '24g':
                    #chentao 2013-4-19
                    if len(wlans_24g_up) == 0:
                        if self.expect_wlans_24g_up == 0:
                            self.passmsg = "Expect_2.4g_wlans_up is 0, actual_2.4g_wlans_up is 0"
                            return
                        else:
                            self.errmsg = "There are no up wlans on 2.4g in AP"
                            return
                    #chentao 2013-4-19            
                    else:
                        wlans_up.update(wlans_24g_up)
                else:
                      #chentao 2013-4-19
                    if len(wlans_5g_up) == 0:
                        if self.expect_wlans_5g_up == 0:
                            self.passmsg = "Expect_5g_wlans_up is 0, actual_5g_wlans_up is 0"
                            return
                        else:
                            self.errmsg = "There are no up wlans on 5g in AP"
                            return
                    #chentao 2013-4-19 
                    else:
                        wlans_up.update(wlans_5g_up)
                match_wlan_count = 0
                for wlan_tag in self.expect_wlan_info[radio_mode]:
                    expect_encryption_cfg = self.expect_wlan_info[radio_mode][wlan_tag].get('encryption_cfg', {})
                    for wlan_name in wlans_up:
                        real_encryption_cfg = self.active_ap.get_encryption(wlan_name, use_id = False)
                        match_param_count = 0
                        #updated by jluh 2013-11-05 
                        #fixed the ssid value is not the same issue.
                        for param in expect_encryption_cfg:
                            if param == 'name':
                                continue
                            if param == 'ssid' and expect_encryption_cfg.has_key('name') and expect_encryption_cfg['name']:
                                expect_encryption_cfg[param] = copy.copy(expect_encryption_cfg['name'])
                        #del the 'name' value, let the lenth of dict is the same in the expected and the real.
                        if expect_encryption_cfg.has_key('name') and expect_encryption_cfg['name']:
                            del(expect_encryption_cfg['name'])
                                
                        for param in expect_encryption_cfg:
                            if expect_encryption_cfg[param] == real_encryption_cfg[param]:
                                match_param_count += 1
                        if match_param_count == len(expect_encryption_cfg):
                            match_wlan_count += 1
                            self.wlan_name_list.append(wlan_name)
                            break
                if match_wlan_count != len(self.expect_wlan_info[radio_mode]):
                    self.errmsg = "Wlans deployed on AP %s mode are not the same with expected" % radio_mode
                    return
                                
            self.passmsg = "The wlans info are correct in the active AP"           
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _update_carrierbag(self):
        self.wlan_name_list = set(self.wlan_name_list)
        self.wlan_name_list = list(self.wlan_name_list)
        self.carrierbag['wlan_name_list'] = self.wlan_name_list
        

