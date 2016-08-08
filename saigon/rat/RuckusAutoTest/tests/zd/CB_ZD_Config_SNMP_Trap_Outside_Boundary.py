'''
Description:
Created on 2011-03-05
@author: cherry.cheng@ruckuswireless.com
Verify snmp agent setting: set as the value outside the boundary, verify error message should be displayed.
'''
import logging
import copy,re

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zd.system_zd import set_snmp_trap_info

class CB_ZD_Config_SNMP_Trap_Outside_Boundary(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        self._verify_set_trap_outside_boundary()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()   
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_set_trap_outside_boundary(self):
        '''
        Verify set snmp agent settings with the outside boundary values, 
        and expect is error message is displayed.
        '''        
        logging.info('Verify setting snmp trap settings with the outside boundary values')
        
        try:
            default_v3_trap_cfg = {'version': 3,
                                   'enabled': True,
                                   'sec_name': 'ruckus-read',
                                   'server_ip': '192.168.0.2',
                                   'auth_protocol': 'MD5',
                                   'auth_passphrase': '12345678',
                                   'priv_protocol': 'DES',
                                   'priv_passphrase': '12345678',
                                   }
            
            default_v2_trap_cfg = {'version': 2,
                                   'enabled': True,
                                   'server_ip': '192.168.0.2',
                                   }
            
            err_dict = {}
            pass_dict = {}
            
            #For snmp agent v3: user name [1,31], passphrase is [8,32].        
            invalid_user_name_list = ['',self._gen_random_string(33)]
            invalid_passphrase_list = ['',self._gen_random_string(7),self._gen_random_string(33)]
            invalid_server_ip_list = ['1', self._gen_random_string(15), self._gen_random_string(41), '255.255.255.255', '0.0.0.0', '::1']        
            
            v2_trap_err_dict = {}
            v2_trap_pass_dict = {}
            
            snmp_trap_cfg = copy.deepcopy(default_v2_trap_cfg)
            key_word = 'server_ip'
            err_msg, pass_msg = self._verify_err_msg(snmp_trap_cfg, key_word, invalid_server_ip_list, set_snmp_trap_info)
                
            if err_msg:
                v2_trap_err_dict[key_word] = err_msg
            else:
                v2_trap_pass_dict[key_word] = pass_msg
                
            v3_trap_err_dict = {}
            v3_trap_pass_dict = {}
            
            snmp_trap_cfg = copy.deepcopy(default_v3_trap_cfg)
            key_word = 'sec_name'
            err_msg, pass_msg = self._verify_err_msg(snmp_trap_cfg, key_word, invalid_user_name_list, set_snmp_trap_info)
            if err_msg:
                v3_trap_err_dict[key_word] = err_msg
            else:
                v3_trap_pass_dict[key_word] = pass_msg
                
            snmp_trap_cfg = copy.deepcopy(default_v3_trap_cfg)
            key_word = 'auth_passphrase'
            err_msg, pass_msg = self._verify_err_msg(snmp_trap_cfg, key_word, invalid_passphrase_list, set_snmp_trap_info)
            if err_msg:
                v3_trap_err_dict[key_word] = err_msg
            else:
                v3_trap_pass_dict[key_word] = pass_msg
            
            snmp_trap_cfg = copy.deepcopy(default_v3_trap_cfg)
            key_word = 'priv_passphrase'
            err_msg, pass_msg = self._verify_err_msg(snmp_trap_cfg, key_word, invalid_passphrase_list, set_snmp_trap_info)
                
            if err_msg:
                v3_trap_err_dict[key_word] = err_msg
            else:
                v3_trap_pass_dict[key_word] = pass_msg  
                
            snmp_trap_cfg = copy.deepcopy(default_v3_trap_cfg)
            key_word = 'server_ip'
            invalid_server_ip_list.append('')
            err_msg, pass_msg = self._verify_err_msg(snmp_trap_cfg, key_word, invalid_server_ip_list, set_snmp_trap_info)
                
            if err_msg:
                v3_trap_err_dict[key_word] = err_msg
            else:
                v3_trap_pass_dict[key_word] = pass_msg 
                
            if v2_trap_err_dict:
                err_dict['v2_trap'] = v2_trap_err_dict            
            if v2_trap_pass_dict:
                pass_dict['v2_trap'] = v2_trap_pass_dict            
            if v3_trap_err_dict:
                err_dict['v3_trap'] = v3_trap_err_dict            
            if v3_trap_pass_dict:
                pass_dict['v3_trap'] = v3_trap_pass_dict
                
            if err_dict:                
                self.errmsg = err_dict
                logging.warning('Error:%s' % (err_dict,))
            if pass_dict:
                self.passmsg = 'Error message is correct when input invalid values.'
                logging.info('Pass:%s' % (pass_dict,))                
                
        except Exception, ex:
            self.errmsg = ex.message
        
    def _verify_err_msg(self, snmp_set_cfg, key_word, invalid_value_list, config_func):
        '''                
        '''
        key_cmd_err_mapping = {'sec_name': 'User has to be no less than 1 and no greater than 32 characters\.',
                               'auth_passphrase': 'Auth Pass Phrase can only contain between 8 and 32 characters, including characters from ! \(char 33\) to ~ \(char 126\), or 32 HEX characters\.',
                               'priv_passphrase': 'Privacy Phrase can only contain between 8 and 32 characters, including characters from ! \(char 33\) to ~ \(char 126\), or 32 HEX characters\.',
                               'server_ip': 'Trap Server IP, .*, is not a valid IP address\.'
                               }
        
        logging.info('Verify outside boundary values for %s' % (key_word))
        
        err_msg_list = []
        pass_msg_list = []
        
        for invalid_value in invalid_value_list:
            if not snmp_set_cfg.has_key(key_word):
                err_msg = 'Key word is not included in config. Keyword:%s, Config:%s' % (key_word, snmp_set_cfg)
                err_msg_list.append(err_msg)
                logging.warning(err_msg)
            else:
                expect_err_msg = key_cmd_err_mapping[key_word]
                if invalid_value == '' and key_word.lower() == 'server_ip':
                    expect_err_msg = 'Trap Server IP cannot be empty'
                        
                snmp_set_cfg[key_word] = invalid_value
                res = config_func(self.zd, snmp_set_cfg)
                if not res:
                    err_msg = 'No error message when set %s as invalid value "%s"'  % (key_word, invalid_value)
                    err_msg_list.append(err_msg)
                    logging.warning(err_msg)
                else:
                    if re.compile(expect_err_msg).search(res):
                        pass_msg = 'Invalid value: "%s", Error: "%s"'
                        if len(invalid_value)>10:                                
                            pass_msg_list.append(pass_msg % (invalid_value[:10]+'...', res))
                        else:
                            pass_msg_list.append(pass_msg % (invalid_value, res))
                            
                        logging.info(pass_msg % (invalid_value, expect_err_msg))
                        
                    else:
                        err_msg = 'Error message is incorrect: Invalid value="%s",Expected="%s",Actual="%s"' % (invalid_value, expect_err_msg, res)
                        err_msg_list.append(err_msg)
                        logging.warning(err_msg)
                        
        return err_msg_list, pass_msg_list             
            
    def _gen_random_string(self, min_len, max_len = '', type = 'alnum'):
        '''
        Generate a random string between min_len and max_len. 
        Type can be 'ascii'[char 32 -126], 'alpha'[letters], 'hex'[0-9 a-f], 'alnum'[letters,digits].     
        ''' 
        ran_str = utils.get_random_string(type, min_len, max_len)
            
        if type.lower() == 'ascii':
            #In webui, can't input the string include <, / and > in order.
            if ran_str.find('<')>-1 and ran_str.find('>')>-1 and ran_str.find('/')>-1:
                ran_str = ran_str.replace('/','a')
            
            #Remove ' and ".
            if ran_str.find("'")>-1:
                ran_str = ran_str.replace("'",'a')                
            if ran_str.find('"')>-1:
                ran_str = ran_str.replace('"','a')
            #Remove ; because parsing issue in zd cli.            
            if ran_str.find(';')>-1:
                ran_str = ran_str.replace(';','a')
                        
        return ran_str