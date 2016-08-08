'''
Description:
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
import copy
import types

from RuckusAutoTest.common.utils import compare_dict_key_value
from RuckusAutoTest.models import Test

class CB_ZD_Verify_SNMP_Trap_Info_Get_Set(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._verify_snmp_trap_gui_set_get()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_d = self.carrierbag['existed_snmp_trap_info']    
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_snmp_trap_gui_set_get(self): 
        try:       
            gui_snmp_trap_info = copy.deepcopy(self.gui_d)
            set_snmp_trap_info = copy.deepcopy(self.conf['snmp_trap_cfg'])
                
            if not gui_snmp_trap_info['enabled']:
                #Remove the item except enabled.
                for key in gui_snmp_trap_info.keys():
                    if key != 'enabled':
                        gui_snmp_trap_info.pop(key)
                for key in set_snmp_trap_info.keys():
                    if key != 'enabled':
                        set_snmp_trap_info.pop(key)
            
            res = self._verify_two_dicts(gui_snmp_trap_info, set_snmp_trap_info)
            
            if res:
                self.errmsg = res
            else:
                self.passmsg = 'SNMP trap info is the same between GUI get and set.'
            
        except Exception, ex:
            self.errmsg = ex.message  
            
             
    def _verify_two_dicts(self, dict1, dict2):
        dict1_keys = dict1.keys()
        dict2_keys = dict2.keys()
        
        dict1_keys.sort()
        dict2_keys.sort()
        
        res_d = {}
        if not dict1_keys == dict2_keys:
            message = 'The keys of dicts are different. Dict1 keys: %s, Dict2 keys: %s' % (dict1_keys, dict2_keys)
            res_d.update ({'ALL': message})
        
        for key, value in dict1.items():
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
'''    
    def _verify_two_dicts(self, dict1, dict2):
        dict1_keys = dict1.keys()
        dict2_keys = dict2.keys()
        
        dict1_keys.sort()
        dict2_keys.sort()
        
        res_d = {}
        if not dict1_keys == dict2_keys:
            message = 'The keys of dicts are different. Dict1 keys: %s, Dict2 keys: %s' % (dict1_keys, dict2_keys)
            res_d.update ({'ALL': message})
        
        for key, value in dict1.items():
            value = str(value)
            if dict2.has_key(key):
                is_pass = self._is_item_pass(dict1, key)
                value2 = str(dict2[key])
                
                if is_pass:
                    result = True
                else:               
                    if value.upper() == value2.upper():
                        result = True
                    else:
                        result = False
                        
                if not result:
                    message = 'The values are different. Dict1: %s, Dict2: %s' % (value, value2)
                    res_d.update({key: message})
            else:
                res_d.update({key: 'No key in dict2.'})
                
        return res_d
    
    def _is_item_pass(self, value_d, key):
        is_pass = False
        
        if key != 'enabled':
            enabled = value_d['enabled']
            if type(enabled) == str:
                if enabled.lower() == 'disabled':
                    is_pass = True
            else:
                if not enabled:
                    is_pass = True
                    
            if not is_pass:
                version = value_d['version']
                if version.lower() == 'version2' and key != 'server_ip':
                    is_pass = True
                else:
                    if key == 'server_ip':
                        is_pass = True
                    elif key == 'priv_passphrase' and value_d['priv_protocol'].lower() == 'none':
                        is_pass = True
                        
        return is_pass 
'''       