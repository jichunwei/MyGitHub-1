'''
Description:
Created on 2010-10-27
@author: cwang@ruckuswireless.com
'''
import copy

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import output_as_dict as dd

class CB_ZD_CLI_Get_Check_Load_Balancing(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self._update_carrier_bag()
        res = self._get_load_balaning_setting()
        if type(res) is tuple:
            r24g_res = res[0]
            r5g_res = res[1]
            
            if r24g_res == "Enabled" and self.r24g_expected_enable and r5g_res == "Enabled" and self.r5g_expected_enable:
                return self.returnResult('PASS', 'load-balancing show correctly, expected [Radio2.4G: %s, Radio5G: %s], \
                actual [Radio2.4G: %s, Radio5G: %s]' % (self.r24g_expected_enable, self.r5g_expected_enable,  r24g_res, r5g_res))
            elif r24g_res == "Disabled" and not self.r24g_expected_enable and r5g_res == "Disabled" and not self.r5g_expected_enable:
                return self.returnResult('PASS', 'load-balancing show correctly, expected [Radio2.4G: %s, Radio5G: %s], \
                actual [Radio2.4G: %s, Radio5G: %s]' % (self.r24g_expected_enable, self.r5g_expected_enable,  r24g_res, r5g_res))
            else:
                return self.returnResult('FAIL', 'load-balancing show incorrectly, expected [Radio2.4G: %s, Radio5G: %s], \
                actual [Radio2.4G: %s, Radio5G: %s]' % (self.r24g_expected_enable, self.r5g_expected_enable,  r24g_res, r5g_res))
            
        else:
            if res == "Enabled" and self.expected_enable:
                return self.returnResult('PASS', 'load-balancing show correctly, expected [%s], actual [%s]' % (self.expected_enable, res))
            elif res == "Disabled" and not self.expected_enable:
                return self.returnResult('PASS', 'load-balancing show correctly, expected [%s], actual [%s]' % (self.expected_enable, res))
            else:
                return self.returnResult('FAIL', 'load-balancing show incorrectly, expected [%s], actual [%s]' % (self.expected_enable, res))
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(enable = True)
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.expected_enable = self.conf['enable']
        self.errmsg = ''
        self.passmsg = ''
        self.r24g_expected_enable = True
        self.r5g_expected_enable = True
        
        if self.conf.has_key('r24g_expected_enable'):
            self.r24g_expected_enable = self.conf['r24g_expected_enable']
        #Modified by Liang Aihua on 2014-10-20 for incorrect radio status
        else:
            self.r24g_expected_enable = self.expected_enable
        if self.conf.has_key('r5g_expected_enable'):
            self.r5g_expected_enable = self.conf['r5g_expected_enable']
        #Modified by Liang Aihua on 2014-10-20 for incorrect radio status
        else:
            self.r5g_expected_enable = self.expected_enable 
            
    
    def _get_load_balaning_setting(self):
        '''
        '''
        res = ''
        res = self.zdcli.do_show('load-balancing', go_to_cfg = True)
        if type(res) is list:
            res = res[0]

        rr = dd.parse(res)
        clb_dict = rr['Load Balancing']
        if clb_dict.has_key('Radio 0') or clb_dict.has_key('Radio 1'):
            #jluh updated by 2013-09-26
            #tunnple unit 0 is 2.4g load balancing status
            #tunnple unit 1 is 5g load balancing status
            s = (clb_dict['Radio 0']['Status'], clb_dict['Radio 1']['Status'])
        else:
            s = rr['Load Balancing']['Status']
        return s
        
        
