'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
       1) Send request to Northbound Interface.
       2) Northbound Interface will response to WebPortal
       3) Check XML file, validate code/message if match requirements.

   Required components: 
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-5-29
@author: cwang@ruckuswireless.com
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_WebPortal_Talk_With_Northbound_Interface(Test):
    required_components = []
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(cmd = Helpers.zd.nb.CHECK_USER_STATUS,
                         kwargs = {},
                         expected_code = '202',
                         sta_tag = 'sta_1',
                         data = None,#support raw data-check.
                         retries = 0#chen.tao 2014-01-06 to fix ZF-6821  #zj 2014-0210 fix script error
                         )
        self.conf.update(conf)
        self.cmd = self.conf['cmd']
        self.kwargs = self.conf['kwargs']
        self.expected_code = self.conf['expected_code']
        self.sta_tag = self.conf['sta_tag']
        self.retries = self.conf['retries']#chen.tao 2014-01-06 to fix ZF-6821
        self.error_msg = '' #zj 2014-0210 fix ZF-7392
        self.zd = self.testbed.components['ZoneDirector']
        self.kwargs['zd_ip_addr'] = self.zd.ip_addr#chen.tao 2015-03-18, using flexible zd ip address

    def _retrieve_carribag(self):
        self.ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        if 'macaddr' in self.conf:#Special Testing.
            self.mac_addr = self.conf['macaddr']
        else:
            self.mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self.kwargs['ipaddr'] = self.ip_addr
        self.kwargs['macaddr'] = self.mac_addr
    
    def test(self):
        logging.info('Communicate to Northbound Interface.')
        _fnc = {Helpers.zd.nb.CHECK_USER_STATUS: self._check_user_status,
                Helpers.zd.nb.USER_AUTHENTICATE: self._do_user_authenticate,
                Helpers.zd.nb.DEL_USER: self._del_user,
                Helpers.zd.nb.GENERATE_DPSK: self._gen_dpsk,
                Helpers.zd.nb.GET_DPSK: self._get_dpsk,
                Helpers.zd.nb.UNRESTRICTED: self._unrestrict_user
                }
        actual_code = []
        if not self.conf['data']:
            if type(self.cmd) == str:
                code, msg = _fnc[self.cmd]()
        #zj 2014-0210 fix ZF-7392
        #edit code param:  config = {'cmd': ['user-authenticate','check-user-status']}  'expected_code': ['202','201']
            elif type(self.cmd) == list and type(self.expected_code) == list :
                num = 0
                for cmd in self.cmd:
                    logging.info('Cmd is %s' % cmd)
                    code, msg = _fnc[cmd]()
                    if code.startswith(self.expected_code[num]):#pass like 200, 201, 202, 203 etc. actual code.
                        logging.info('Code %s, Message %s' % (code, msg))
                        actual_code.append(code)
                    else :
                        self.error_msg = 'Expected code %s, Actual code %s' % (self.expected_code[num], code)
                        actual_code.append(code)
                        break
#                    actual_code.append(code)
                    num = num+1                 
        #zj 2014-0210 fix ZF-7392  
          
        else:
            node = Helpers.zd.nb.request(data = self.conf['data'],**self.kwargs)#chen.tao 2015-03-18, using flexible zd ip address
            code = Helpers.zd.nb.get_response_code(node)
            msg = Helpers.zd.nb.get_response_msg(node)
        
        #chen.tao 2014-01-06 to fix ZF-6821
        if code != self.expected_code and self.retries:
            for i in range(self.retries):
                time.sleep(1)
                logging.info('Retry for %s time'%str(int(i)+1))
                if not self.conf['data']:
                    code, msg = _fnc[self.cmd]()
                else:
                    node = Helpers.zd.nb.request(data = self.conf['data'],**self.kwargs)#chen.tao 2015-03-18, using flexible zd ip address
                    code = Helpers.zd.nb.get_response_code(node)
                    msg = Helpers.zd.nb.get_response_msg(node)
                if code == self.expected_code:
                    break
        #chen.tao 2014-01-06 to fix ZF-6821
        if not actual_code: actual_code = code
        logging.info('Code %s, Message %s' % (actual_code, msg))  
        #zj 2014-0210 fix ZF-7392
        if type(self.cmd) == list:
            if self.error_msg:
                return self.returnResult('FAIL', 
                                     'Expected code %s, actual code %s' % \
                                     (self.expected_code, actual_code))
            else:
                return self.returnResult('PASS', msg)
        else:
#        #zj 2014-0210 fix ZF-7392        
#            if code.startswith(self.expected_code[:-1]):#pass like 200, 201, 202, 203 etc. actual code.  and not self.error_msg 
#                return self.returnResult('PASS', msg)
            
        #####@zj 20140610
            if code in self.expected_code:
                return self.returnResult('PASS', msg)
        #####@zj 20140610           
            else:
                return self.returnResult('FAIL', 
                                         'Expected code %s, actual code %s' % \
                                         (self.expected_code, actual_code))
        
    
    def cleanup(self):
        self._update_carribag()
    
    def _do_user_authenticate(self):
        #Updated by cwang@20130722, combine 3 steps together.
        _dd = {'ipaddr':self.kwargs.get('ipaddr'),
               'macaddr':self.kwargs.get('macaddr'),
               'zd_ip_addr':self.kwargs.get('zd_ip_addr')#chen.tao 2015-03-18, using flexible zd ip address
              }
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.CHECK_USER_STATUS, **_dd)
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.USER_AUTHENTICATE, **self.kwargs)
        res_check = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.CHECK_USER_STATUS, **_dd)
        if res:
            code = Helpers.zd.nb.get_response_code(res)
            message = Helpers.zd.nb.get_response_msg(res)
            return code, message
        
        return (None, None)
        
    
    def _check_user_status(self):
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.CHECK_USER_STATUS, **self.kwargs)
        if res:
            code = Helpers.zd.nb.get_response_code(res)
            message = Helpers.zd.nb.get_response_msg(res)
            return code, message
        return (None, None)
    
    def _del_user(self):        
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.DEL_USER, **self.kwargs)
        if res:
            code = Helpers.zd.nb.get_response_code(res)
            message = Helpers.zd.nb.get_response_msg(res)
            return code, message
        return (None, None)
    
    def _unrestrict_user(self):
        if 'ipaddr' in self.kwargs:
            self.kwargs.pop('ipaddr')
                    
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.UNRESTRICTED, **self.kwargs)
        if res:
            code = Helpers.zd.nb.get_response_code(res)
            message = Helpers.zd.nb.get_response_msg(res)
            return code, message
        return (None, None)
    
    def _gen_dpsk(self):
        if 'ipaddr' in self.kwargs:
            self.kwargs.pop('ipaddr')
            
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.GENERATE_DPSK, **self.kwargs)
        if res:
            code = Helpers.zd.nb.get_response_code(res)
            message = Helpers.zd.nb.get_response_msg(res)
            return code, message
        return (None, None)
    
    def _get_dpsk(self):
        res = Helpers.zd.nb.notify(cmd = Helpers.zd.nb.GET_DPSK, **self.kwargs)
        if res:
            code = Helpers.zd.nb.get_response_code(res)
            message = Helpers.zd.nb.get_response_msg(res)
            return code, message
        return (None, None)
