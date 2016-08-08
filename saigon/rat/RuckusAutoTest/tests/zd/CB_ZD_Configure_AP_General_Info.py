'''
Description:

This function is used to set general Info for AP


Created on 2012-12-18
@author: zoe.huang@ruckuswireless.com
'''
import copy
import types
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Configure_AP_General_Info(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._set_ap_general_info()
        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': '',
                     'general_info': {
                                      'device_name': 'RuckusAP',
                                      'description': '',
                                      'device_location': 'Lab',
                                      'gps_latitude': '',
                                      'gps_longitude': '',
                                      'ap_group': 'System Default',
                                      }
                    }
        self.conf.update(conf)        
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag = self.conf['ap_tag']
        self.ap_generalinfo = self.conf['general_info']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        self.ap_macaddr = self.active_ap.base_mac_addr
        self.errmsg = ''
        self.passmsg = ''

    def _set_ap_general_info(self):
        try:
            logging.info('Begin to set ap general info %s for AP %s' %(self.ap_generalinfo, self.ap_macaddr))
            lib.zd.ap.set_ap_general_by_mac_addr(self.zd, self.ap_macaddr,self.ap_generalinfo['device_name'],
            self.ap_generalinfo['description'],self.ap_generalinfo['device_location'],self.ap_generalinfo['gps_latitude'],
            self.ap_generalinfo['gps_longitude'],self.ap_generalinfo['ap_group'])
            
            logging.info('Begin to verify the info set')
            real_ap_info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.ap_macaddr)
            res = self._verify_two_dicts(real_ap_info, self.ap_generalinfo)
            
            if res:
                self.errmsg = res
            else:
                self.passmsg = 'Set ap general info %s for AP %s successfully.' %(self.ap_generalinfo, self.ap_macaddr)
                       
        except Exception, e:
            self.errmsg = '[Apply failed]: %s' % e.message
            
    def _verify_two_dicts(self, dict1, dict2):
        dict1_keys = dict1.keys()
        dict2_keys = dict2.keys()
        
        dict1_keys.sort()
        dict2_keys.sort()
        
        res_d = {}
        if not dict1_keys == dict2_keys:
            message = 'The keys of dicts are different. Dict1 keys: %s, Dict2 keys: %s' % (dict1_keys, dict2_keys)
            res_d.update ({'ALL': message})
        
        for (key, value) in dict1.iteritems():
            if dict2.has_key(key):
                if type(value) is types.DictionaryType: 
                    if type(dict2[key]) is types.DictionaryType:                   
                        res_sub = self._verify_two_dicts(value, dict2[key])
                        res_d.update(res_sub.items())
                    else:
                        res_d.update({key: 'the value type of the key is not the same'})                    
                else:
                    if type(value) == type(dict2[key]):
                        if value != dict2[key]:
                            res_d.update({key: 'The value of this key in two dicts are different. value in Dict1: %s, value in Dict2: %s' % (value, dict2[key])})
                    else: 
                        if str(value) != str(dict2[key]):
                            res_d.update({key: 'The value of this key in two dicts are different. value in Dict1: %s, value in Dict2: %s' % (value, dict2[key])})                                                 
            else:
                res_d.update({key: 'No key in dict2 or the type of value is not the same'})

                
        return res_d   