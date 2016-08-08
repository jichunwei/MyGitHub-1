'''
Description:
Created on 2011-03-05
@author: cherry.cheng@ruckuswireless.com
Verify snmp agent setting: set as the value outside the boundary, verify error message should be displayed.
'''
import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd.sys_snmp_info import set_sys_snmp_info

class CB_ZD_SNMP_Config_SNMP_Trap_Outside_Boundary(Test):
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
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_set_trap_outside_boundary(self):
        '''
        Verify set snmp agent settings with the outside boundary values, 
        and expect is error message is displayed.
        '''
        logging.info('Verify setting snmp agent settings with the outside boundary values')
        
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            invalid_user_name_list = ['',self._gen_random_string(33)]
            invalid_passphrase_list = ['',self._gen_random_string(7),self._gen_random_string(33)]            
            invalid_server_ip_list = ['', '1', self._gen_random_string(41)]
            
            err_dict = {}
            pass_dict = {}
            
            key_word = 'v2_trap_server'        
            err_msg, pass_msg = self._verify_err_msg(snmp, key_word, invalid_server_ip_list, set_sys_snmp_info)
            if err_msg:
                err_dict[key_word] = err_msg
            else:
                pass_dict[key_word] = pass_msg
            
            key_word = 'v3_trap_user'
            err_msg, pass_msg = self._verify_err_msg(snmp, key_word, invalid_user_name_list, set_sys_snmp_info)
            if err_msg:
                err_dict[key_word] = err_msg
            else:
                pass_dict[key_word] = pass_msg
            
            key_word = 'v3_trap_auth_key'        
            err_msg, pass_msg = self._verify_err_msg(snmp, key_word, invalid_passphrase_list, set_sys_snmp_info)
            if err_msg:
                err_dict[key_word] = err_msg
            else:
                pass_dict[key_word] = pass_msg
            
            key_word = 'v3_trap_priv_key'        
            err_msg, pass_msg = self._verify_err_msg(snmp, key_word, invalid_passphrase_list, set_sys_snmp_info)
            if err_msg:
                err_dict[key_word] = err_msg
            else:
                pass_dict[key_word] = pass_msg
                
            key_word = 'v3_trap_server'        
            err_msg, pass_msg = self._verify_err_msg(snmp, key_word, invalid_server_ip_list, set_sys_snmp_info)
            if err_msg:
                err_dict[key_word] = err_msg
            else:
                pass_dict[key_word] = pass_msg
                
            if err_dict:                
                self.errmsg = err_dict
                logging.warning('Error:%s' % (err_dict,))
            if pass_dict:
                self.passmsg = 'Error message is correct when input invalid values.'
                logging.info('Pass:%s' % (pass_dict,))
            
        except Exception, ex:
            self.errmsg = ex.message
        
    def _verify_err_msg(self, snmp, key_word, invalid_value_list, config_func):
        key_err_mapping = {'v2_trap_server': 'Reason: wrongValue \(The set value is illegal or unsupported in some way\)', #(Value does not match DISPLAY-HINT :: {(2..40)})',
                           'v3_trap_user':  '\(Value does not match DISPLAY-HINT :: {\(1\.\.32\)}\)',
                           'v3_trap_auth_key': '\(Value does not match DISPLAY-HINT :: {\(8\.\.32\)}\)',
                           'v3_trap_priv_key': '\(Value does not match DISPLAY-HINT :: {\(8\.\.32\)}\)',
                           'v3_trap_server': 'Reason: wrongValue \(The set value is illegal or unsupported in some way\)',
                           }
        
        logging.info('Verify outside boundary values for %s' % (key_word))
        err_msg_list = []
        pass_msg_list = []
        
        for invalid_value in invalid_value_list:
            if key_word in ['v3_trap_server','v2_trap_server'] and (len(invalid_value)>40 or len(invalid_value)<2):
                expected_err_msg = '\(Bad string length :: {\(2\.\.40\)}\)'
            else:
                expected_err_msg = key_err_mapping[key_word]
                
            snmp_set_cfg = {}
            snmp_set_cfg[key_word] = invalid_value
            res_dict = config_func(snmp, snmp_set_cfg, [], False)
            
            actual_err = "".join(res_dict.values())
            
            if re.compile(expected_err_msg).search(actual_err):
                #actual_err.upper() == expected_err_msg.upper():
                pass_msg = 'Invalid value: "%s", Error: "%s"'
                if len(invalid_value)>10:                                
                    pass_msg_list.append(pass_msg % (invalid_value[:10]+'...', actual_err))
                else:
                    pass_msg_list.append(pass_msg % (invalid_value, actual_err))
                    
                logging.info(pass_msg % (invalid_value, actual_err))
            else:
                err_msg = 'Error message is incorrect: Invalid value="%s",Expected="%s",Actual="%s"' % (invalid_value, expected_err_msg, actual_err)
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