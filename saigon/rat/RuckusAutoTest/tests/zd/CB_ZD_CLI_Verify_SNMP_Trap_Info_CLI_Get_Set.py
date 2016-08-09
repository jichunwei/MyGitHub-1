'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description:
    This script is to verify snmp agent v2 information between CLI get and set.
'''
import copy
import types

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd.sys_snmp_info import server_ip

class CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'snmp_trap_cfg': 'snmp trap config of set'}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):      
        self._verify_snmp_trap_cli_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)    
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):        
        self.cli_d = self.carrierbag['zdcli_sys_snmp_trap_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)    
                
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_snmp_trap_cli_get_set(self,trap_id = '0'):
        try:
            cli_snmp_trap_info = copy.deepcopy(self.cli_d)
            set_snmp_trap_info = copy.deepcopy(self.conf['snmp_trap_cfg'])
            keys_mapping = {'Status':'enabled',
                            server_ip:'server_ip', 
                            'Format': 'version',
                            'Authentication Pass Phrase': 'auth_passphrase',
                            'Authentication Type': 'auth_protocol',
                            'Privacy Type': 'priv_protocol',
                            'Privacy Phrase':'priv_passphrase',
                            'User': 'sec_name'
                            }
            if set_snmp_trap_info.has_key('version'):
                set_snmp_trap_info['version'] = 'Version%s' % set_snmp_trap_info['version']
                
            enabled = set_snmp_trap_info['enabled']
            if enabled:
                set_snmp_trap_info['enabled'] = 'Enabled'
            else:
                set_snmp_trap_info['enabled'] = 'Disabled'
                #Remove the item except enabled.
                for key in cli_snmp_trap_info.keys():
                    if key != 'Status':
                        cli_snmp_trap_info.pop(key)
                for key in set_snmp_trap_info.keys():
                    if key != 'enabled':
                        set_snmp_trap_info.pop(key)
            
            new_cli_snmp_trap_info = {}
            for key,value in cli_snmp_trap_info.items(): 
                is_server = False;
                for i in range(1,5):
                    if key == str(i):
                        is_server= True
                        break
                tmpvalue = value
                tmpkey = key
                if is_server and type(value) is types.DictionaryType:
                    new_cli_snmp_trap_info[tmpkey]= {}
                    for key,value in tmpvalue.items():
                        if keys_mapping.has_key(key):
                            new_key = keys_mapping[key]
                            new_cli_snmp_trap_info[tmpkey][new_key] = value
                else: 
                    if keys_mapping.has_key(key):
                        new_key = keys_mapping[key]                    
                        new_cli_snmp_trap_info[new_key] = value 
            #updated by jluh@2012-12-14
            if new_cli_snmp_trap_info.get(trap_id):
                trap_setting = new_cli_snmp_trap_info.pop(trap_id)
                new_cli_snmp_trap_info.update(trap_setting)
                del(trap_setting)                
            #If trap is enable, version is 3 and priv_protocl is none, add priv_passphare item.
            if enabled and new_cli_snmp_trap_info['version'].lower() == 'version3' \
                 and new_cli_snmp_trap_info.has_key('priv_protocol') and new_cli_snmp_trap_info['priv_protocol'].lower() == 'none':
                new_cli_snmp_trap_info['priv_passphrase']= ''
            
            res = self._verify_two_dicts(new_cli_snmp_trap_info, set_snmp_trap_info)
            
            if res:
                self.errmsg = res
            else:
                self.passmsg = 'SNMP trap info is the same between CLI get and set.'
            
        except Exception, ex:
            self.errmsg = ex.message
            
                
    def _verify_two_dicts(self, dict1, dict2):
        dict1_keys = dict1.keys()
        dict2_keys = dict2.keys()
        
        dict1_keys.sort()
        dict2_keys.sort()
        
        res_d = {}
        #chen.tao 2014-01-16 to fix ZF-6551
        #if not dict1_keys == dict2_keys:
        #    message = 'The keys of dicts are different. Dict1 keys: %s, Dict2 keys: %s' % (dict1_keys, dict2_keys)
        #    res_d.update ({'ALL': message})
        for d1_key in dict1_keys:
            if not dict2.has_key(d1_key):
                message = 'The keys of dicts are different. Dict1 keys: %s, Dict2 keys: %s' % (dict1_keys, dict2_keys)
                res_d.update ({'ALL': message})
        #chen.tao 2014-01-16 to fix ZF-6551
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