"""
Description: This combo test is used to configure alarm settings on Zone Director  
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Zone Director
Input: provide dictionary 'alarm_setting' input config with below keys: 
    - email_addr      : (*)  the email address to which ZoneDirector will send alarm messages 
    - server_name     : (*)  full name of mail server or server ipaddress  
    - server_port     : (**) the SMTP port number of mail server  
    - username        : (**) username of mail server if server require authentication 
    - password        : (**) password associate with username
    - tls_option      : (**) TLS encryption option (True/False)
    - starttls_option : (**) STARTTLS encryption option (True/False)
      
    Notes: (*) is required keys 
           (**) is optional keys if no input will use default values
Output:
    - carrierbag['alarm_setting']: a dictionary of current alarm settings on Zone Director 
    - PASS: If alarm setting can apply successful.
    - FAIL: If any error/ can not apply configure message return by Zone Director 
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from copy import deepcopy
from pprint import pformat
import logging



class CB_ZD_Config_Alarm_Setting(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        try: 
            logging.info("Configure Alarm Setting with configuration: \r\n%s" % pformat(self.conf['alarm_setting']))
            lib.zd.asz.set_alarm_email(self.zd,self.conf['alarm_setting']['email_addr'], self.conf['alarm_setting']['server_name'], 
                                             self.conf['alarm_setting']['server_port'], self.conf['alarm_setting']['username'], self.conf['alarm_setting']['password'], 
                                             self.conf['alarm_setting']['tls_option'], self.conf['alarm_setting']['starttls_option'])
        except Exception, e: 
            self.errmsg = e.message
            return self.returnResult('FAIL', self.errmsg)
        
        self.carrierbag['alarm_setting'] = deepcopy(self.conf['alarm_setting'])
        self.passmsg = 'Alarm Settings configured successful on Zone Director.' 
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':120,}
        self.conf['alarm_setting'] = dict(
            email_addr = 'lab@example.net', 
            server_name = '192.168.0.252', 
            server_port = '25', 
            username = 'lab', #chen.tao 2014-2-18, to fix ZF-7119
            password = 'lab4man1',#chen.tao 2014-2-18, to fix ZF-7119
            tls_option = False, 
            starttls_option = False
        )
        self.zd = self.testbed.components['ZoneDirector']
        self.conf['alarm_setting'].update(conf['alarm_setting'])
