'''
Description:

This function is used to config radio info in AP group

Created on 2012-12-10
@author: zoe.huang@ruckuswireless.com

'''
import copy
import types
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as hlper

# Note that the name of the Test class must match the name of this file for ease of runtime-reference
CallAdmissionConrl={0:'OFF',
                    10:'10% airtime usage limit',
                    20:'20% airtime usage limit',
                    30:'30% airtime usage limit',
                    40:'40% airtime usage limit',
                    50:'50% airtime usage limit',
                    60:'60% airtime usage limit',
                    70:'70% airtime usage limit',
                    }
class CB_ZD_Configure_AP_Group_Radio_Info(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._set_ap_group_info_by_name()
        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'apgroup_name' : 'System Default',
                     'bgn': {'channelization':None,
                             'channel':None,
                             'power':None,
                             'mode': None,
                             'wlangroups':'Default',
                             'ac':0,        
                             },
                     'na': {'channelization':None,
                             'channel':None,
                             'power':None,
                             'mode': None,
                             'wlangroups':'Default', 
                             'ac':0,       
                             },
                    }
        self.conf.update(conf)        
        self.zd = self.testbed.components['ZoneDirector']
        self.apgroup_name = self.conf['apgroup_name']
        self.bgn_cfg = self.conf['bgn']
        if 'channelization' not in self.bgn_cfg.keys():
            self.bgn_cfg['channelization'] = 'Auto'
        if 'channel' not in self.bgn_cfg.keys():
            self.bgn_cfg['channel'] = 'Auto'
        if 'power' not in self.bgn_cfg.keys():
            self.bgn_cfg['power'] = 'Auto'
        if 'mode' not in self.bgn_cfg.keys():
            self.bgn_cfg['mode'] = 'Auto'
        if 'wlangroups' not in self.bgn_cfg.keys():
            self.bgn_cfg['wlangroups'] = 'Default'
        if 'ac' not in self.bgn_cfg.keys():
            self.bgn_cfg['ac'] = 0
                
        self.na_cfg = self.conf['na']
        
        if 'channelization' not in self.na_cfg.keys():
            self.na_cfg['channelization'] = 'Auto'
        if 'channel' not in self.na_cfg.keys():
            self.na_cfg['channel'] = 'Auto'
        if 'power' not in self.na_cfg.keys():
            self.na_cfg['power'] = 'Auto'
        if 'mode' not in self.na_cfg.keys():
            self.na_cfg['mode'] = 'Auto'
        if 'wlangroups' not in self.na_cfg.keys():
            self.na_cfg['wlangroups'] = 'Default'
        if 'ac' not in self.na_cfg.keys():
            self.na_cfg['ac'] = 0
                
        self.errmsg = ''
        self.passmsg = ''

    def _set_ap_group_info_by_name(self):
        try:
            logging.info('Begin to set radio info for AP Group %s' % self.apgroup_name)
            hlper.zd.apg.set_ap_group_radio_by_name(self.zd, self.apgroup_name, self.bgn_cfg, self.na_cfg)
            logging.info('Begin to verify the info set')
            apgrp_info = hlper.zd.apg.get_ap_group_cfg_by_name(self.zd, self.apgroup_name)
            logging.info('Check the 2.4 info in AP group %s' % self.apgroup_name)
            bgn_cfg_verify = self.bgn_cfg.copy()
            bgn_cfg_verify['ac'] = CallAdmissionConrl[bgn_cfg_verify['ac']]
            res1 = self._verify_two_dicts(apgrp_info['radio_gn'], bgn_cfg_verify)           
            logging.info('Check the 5g info in AP group %s' % self.apgroup_name)
            na_cfg_verify = self.na_cfg.copy()
            na_cfg_verify['ac'] = CallAdmissionConrl[na_cfg_verify['ac']]
            res2 = self._verify_two_dicts(apgrp_info['radio_an'], na_cfg_verify)
            res2.update(res1)         
            if res2:
                self.errmsg = res2
            else:
                self.passmsg = 'Set ap group radio info successfully.'
                       
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