'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description:
    This script is to verify snmp agent v2 information between CLI get and set.
'''
from RuckusAutoTest.models import Test

class CB_ZD_CLI_Verify_SNMPV2_Info_CLI_Get_Set(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'snmp_agent_cfg': 'snmp agent settings'}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):      
        self._verify_snmpv2_agent_cli_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)    
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):        
        self.cli_d = self.carrierbag['existed_zdcli_sys_snmpv2_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)    
                
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_snmpv2_agent_cli_get_set(self):
        try:
            cli_snmpv2_agent_info = self.cli_d
            set_snmpv2_agent_info = self.conf['snmp_agent_cfg']
            
            cli_key_mapping = {'Status': 'enabled',
                               'RO Community': 'ro_community',
                               'RW Community': 'rw_community',
                               'Contact': 'contact',
                               'Location': 'location',
                               }    
            
            new_cli_agent_info = {}
            
            if set_snmpv2_agent_info.has_key('version'):
                set_snmpv2_agent_info.pop('version')
            
            for key,value in cli_snmpv2_agent_info.items():
                new_key = cli_key_mapping[key]
                if key == 'Status':
                    if value == 'Enabled':
                        value = True
                    else:
                        value = False
                new_cli_agent_info[new_key] = value
                
            res = self._verify_two_dicts(new_cli_agent_info, set_snmpv2_agent_info)
            
            if res:
                self.errmsg = res
            else:
                self.passmsg = 'SNMPV2 agent info is the same between GUI and CLI.'
            
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
                value2 = str(dict2[key])
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