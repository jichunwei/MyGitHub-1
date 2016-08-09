'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description:
    This script is to verify snmp agent v2 information between CLI get and set.
'''
from RuckusAutoTest.models import Test

class CB_ZD_Verify_SNMPV3_Info_Get_Set(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):      
        self._verify_snmpv3_agent_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)    
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):        
        self.gui_d = self.carrierbag['existed_snmp_agent_v3_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)    
                
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_snmpv3_agent_get_set(self):
        try:
            gui_snmpv3_agent_info = self.gui_d
            set_snmpv3_agent_info = self.conf['snmp_agent_cfg']
            
            if set_snmpv3_agent_info.has_key('version'):
                set_snmpv3_agent_info.pop('version')
           
            res = self._verify_two_dicts(gui_snmpv3_agent_info, set_snmpv3_agent_info)
            
            if res:
                self.errmsg = res
            else:
                self.passmsg = 'SNMPV3 agent info is the same between GUI Get and Set.'
            
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
        
        if key == 'ro_priv_passphrase' and value_d['ro_priv_protocol'].upper() == 'NONE':
            is_pass = True
        elif key == 'rw_priv_passphrase' and value_d['rw_priv_protocol'].upper() == 'NONE':
            is_pass = True
            
        return is_pass
        