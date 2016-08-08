'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       Prepare for configuration for AP Group which will create. 
   2. Test:
       Create AP Group and Verify it.
   3. Cleanup:
       - 
    How it was tested:
    
Created on OCT 2, 2011
@author: cwang@ruckuswireless.com
description:
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group


class CB_ZD_Create_AP_Group(Test):
    '''   
    conf = {'name':'',
            'description':'',
            'gn':{'channelization':None,
                   'channel':None,
                   'tx_power':None,
                   'mode': None,
                   'wlan_group':None,           
                   },
            'an':{'channelization':None,
                   'channel':None,
                   'tx_power':None,
                   'mode': None,
                   'wlan_group':None,           
                 },
            
            'move_to_member_list':['ac:ff:33:33:44:11',]
        } 
    '''
    def config(self,conf):
        self.conf = {'name':'ap_group_1',
                     'description':'ap_group_1',
                     'an': {'channel': '36',
                           'channelization': '20',
                           'mode': 'Auto',
                           'tx_power': 'Full',
                           'wlan_group': 'rat_wlangroup_999'},
                     'gn': {'channel': '11',
                            'channelization': '40',
                            'mode': 'N/AC-only',
                            'tx_power': '-1dB',
                            'wlan_group': 'rat_wlangroup_0'},                                 
                     }
        replace = conf.get('replace', False)
        if replace:                           
            self.conf = conf
        else:
            self.conf.update(**conf)            
            
        self.name = self.conf.pop('name')
        self._init_test_params(self.conf)
        
    
    def test(self):
        try:
            apgroups = ap_group.get_all_ap_group_brief_info(self.zd)
            fnd = False
            for gname in apgroups:
                if self.name == gname:
                    fnd = True
                    break
            
            if fnd:
                logging.info("AP Group %s existed, will be deleted" % self.name)
                ap_group.delete_ap_group_by_name(self.zd, self.name)
                        
            ap_group.create_ap_group(self.zd, self.name, **self.conf)
                            
            self.ap_group_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, self.name)
            res = self._verify_ap_cfg()
            if not res:
                self._update_carrier_bag()
                return self.returnResult('PASS', 'AP Group %s created' % self.name)
            else:
                return self.returnResult('FAIL', res)
        except Exception, e:
            return self.returnResult('ERROR', e.message)
    
    
    def cleanup(self):
        pass

    
    def _verify_ap_cfg(self):
        unmatchs = []
        general_info = self.ap_group_cfg['general_info']
        description = self.conf.get('description', '')
        if description != general_info.get('description', ''):
            unmatchs.append("expect [description=%s], actual [description=%s]" % \
                                    (description, general_info.get('description', '')))
        if self.ap_group_cfg.get('radio_gn', None):    
            bgn_info = self.ap_group_cfg['radio_gn']
        
        if self.conf.get('gn', None):
            bgn = self.conf['gn']
            unmatchs.extend(self._check_key_value(bgn, bgn_info))
        if self.ap_group_cfg.get('radio_an', None):
            an_info = self.ap_group_cfg['radio_an']
            
        an = self.conf.get('an', None)
        if an:
            unmatchs.extend(self._check_key_value(an, an_info))
        if 'move_to_member_list' in self.conf:
            move_to_member_list = self.conf['move_to_member_list']            
            members_info = self.ap_group_cfg['members_info']            
            for mac in move_to_member_list:
                fnd = False
                for member in members_info:
                    if member['mac'] == mac:
                        fnd = True
                        break
                if not fnd:
                    unmatchs.append("AP %s haven't move to members list" % mac)
        return unmatchs
#        aps_info = self.ap_group_cfg['aps_info']
    
    def _check_key_value(self, src_dict, target_dict):
        unmatchs = []
        for s_k, s_v in src_dict.items():
            if s_k in target_dict.keys():
                if s_k == "ac":
                    if s_v + "%" not in target_dict[s_k]:
                        unmatchs.append("expect [%s=%s], actual [%s=%s]" % \
                                    (s_k, s_v, s_k, target_dict[s_k]))
                elif target_dict[s_k] != s_v:
                    unmatchs.append("expect [%s=%s], actual [%s=%s]" % \
                                    (s_k, s_v, s_k, target_dict[s_k]))
        
        return unmatchs
    
    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        self.carrierbag['existed_ap_group'] = {self.name:self.ap_group_cfg} 
